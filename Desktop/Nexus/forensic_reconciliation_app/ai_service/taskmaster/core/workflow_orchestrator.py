"""
Workflow Orchestrator - Complex Workflow Management Engine

This module implements the WorkflowOrchestrator class that handles complex
investigation workflows, step dependencies, and process automation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid

from ..models.job import Job, JobStatus, JobPriority, JobType
from ..models.workflow import Workflow, WorkflowStatus, WorkflowStep
from ..models.agent import Agent, AgentStatus, AgentType


class WorkflowTrigger(Enum):
    """Workflow trigger types."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    CONDITION_BASED = "condition_based"
    API_CALL = "api_call"


class WorkflowExecutionMode(Enum):
    """Workflow execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    FORK_JOIN = "fork_join"


class StepStatus(Enum):
    """Workflow step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class DependencyType(Enum):
    """Step dependency types."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    EXCLUSIVE = "exclusive"
    INCLUSIVE = "inclusive"


@dataclass
class WorkflowStep:
    """Workflow step definition."""
    
    id: str
    name: str
    description: str
    step_type: str
    agent_type: Optional[AgentType] = None
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    timeout: timedelta = timedelta(hours=1)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.SEQUENTIAL
    conditions: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class WorkflowExecution:
    """Workflow execution instance."""
    
    id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    completed_steps: Set[str] = field(default_factory=set)
    failed_steps: Set[str] = field(default_factory=set)
    step_results: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics."""
    
    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    step_success_rate: float = 0.0
    parallel_execution_efficiency: float = 0.0
    
    def update_average_execution_time(self, new_time: float):
        """Update average execution time."""
        self.average_execution_time = (
            (self.average_execution_time * self.total_workflows + new_time) /
            (self.total_workflows + 1)
        )
    
    def update_success_rate(self):
        """Update success rate."""
        if self.total_workflows > 0:
            self.success_rate = self.completed_workflows / self.total_workflows


class WorkflowOrchestrator:
    """
    Workflow orchestration engine for the Taskmaster system.
    
    The WorkflowOrchestrator is responsible for:
    - Managing complex investigation workflows
    - Handling step dependencies and execution order
    - Supporting parallel and conditional execution
    - Managing workflow state and recovery
    - Monitoring workflow performance
    """
    
    def __init__(self, config: Dict[str, Any], taskmaster=None):
        """Initialize the WorkflowOrchestrator."""
        self.config = config
        self.taskmaster = taskmaster
        self.logger = logging.getLogger(__name__)
        
        # Workflow configuration
        self.max_concurrent_workflows = config.get('max_concurrent_workflows', 100)
        self.max_parallel_steps = config.get('max_parallel_steps', 20)
        self.workflow_timeout = timedelta(hours=config.get('workflow_timeout_hours', 24))
        self.step_timeout = timedelta(hours=config.get('step_timeout_hours', 4))
        self.enable_recovery = config.get('enable_recovery', True)
        self.enable_rollback = config.get('enable_rollback', True)
        
        # Internal state
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.step_executions: Dict[str, Dict[str, Any]] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        
        # Workflow metrics
        self.metrics = WorkflowMetrics()
        
        # Execution state
        self.execution_queue: deque = deque()
        self.running_steps: Dict[str, Set[str]] = defaultdict(set)
        self.step_dependencies: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("WorkflowOrchestrator initialized successfully")
    
    async def start(self):
        """Start the WorkflowOrchestrator."""
        self.logger.info("Starting WorkflowOrchestrator...")
        
        # Load workflow templates
        await self._load_workflow_templates()
        
        # Start background tasks
        asyncio.create_task(self._process_execution_queue())
        asyncio.create_task(self._monitor_workflow_timeouts())
        asyncio.create_task(self._cleanup_completed_executions())
        asyncio.create_task(self._update_workflow_metrics())
        
        self.logger.info("WorkflowOrchestrator started successfully")
    
    async def stop(self):
        """Stop the WorkflowOrchestrator."""
        self.logger.info("Stopping WorkflowOrchestrator...")
        
        # Cancel all running workflows
        for execution_id in list(self.active_executions.keys()):
            await self.cancel_workflow(execution_id)
        
        self.logger.info("WorkflowOrchestrator stopped")
    
    async def create_workflow(self, template_name: str, parameters: Dict[str, Any]) -> str:
        """Create a new workflow from template."""
        try:
            if template_name not in self.workflow_templates:
                raise ValueError(f"Workflow template '{template_name}' not found")
            
            template = self.workflow_templates[template_name]
            
            # Create workflow instance
            workflow = Workflow(
                id=str(uuid.uuid4()),
                name=template['name'],
                description=template['description'],
                steps=template['steps'].copy(),
                triggers=template.get('triggers', []),
                execution_mode=template.get('execution_mode', WorkflowExecutionMode.SEQUENTIAL),
                metadata=template.get('metadata', {})
            )
            
            # Apply parameters
            workflow = self._apply_workflow_parameters(workflow, parameters)
            
            # Store workflow
            self.workflows[workflow.id] = workflow
            
            self.logger.info(f"Created workflow {workflow.id} from template {template_name}")
            return workflow.id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            raise
    
    async def start_workflow(self, workflow_id: str, trigger: WorkflowTrigger = WorkflowTrigger.MANUAL) -> str:
        """Start a workflow execution."""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            
            # Check if we can start more workflows
            if len(self.active_executions) >= self.max_concurrent_workflows:
                raise RuntimeError("Maximum concurrent workflows reached")
            
            # Create execution instance
            execution = WorkflowExecution(
                id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                metadata={'trigger': trigger.value}
            )
            
            # Store execution
            self.executions[execution.id] = execution
            
            # Add to execution queue
            self.execution_queue.append(execution.id)
            
            self.logger.info(f"Started workflow execution {execution.id} for workflow {workflow_id}")
            return execution.id
            
        except Exception as e:
            self.logger.error(f"Error starting workflow {workflow_id}: {e}")
            raise
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            
            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                return False
            
            # Cancel all running steps
            if execution_id in self.running_steps:
                for step_id in self.running_steps[execution_id]:
                    await self._cancel_step(execution_id, step_id)
            
            # Update execution status
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            
            # Remove from active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            self.logger.info(f"Cancelled workflow execution {execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling workflow {execution_id}: {e}")
            return False
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowStatus]:
        """Get the status of a workflow execution."""
        if execution_id in self.executions:
            return self.executions[execution_id].status
        return None
    
    async def get_workflow_metrics(self) -> WorkflowMetrics:
        """Get current workflow performance metrics."""
        return self.metrics
    
    async def _process_execution_queue(self):
        """Process the workflow execution queue."""
        while True:
            try:
                if self.execution_queue and len(self.active_executions) < self.max_concurrent_workflows:
                    execution_id = self.execution_queue.popleft()
                    asyncio.create_task(self._execute_workflow(execution_id))
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing execution queue: {e}")
                await asyncio.sleep(1)
    
    async def _execute_workflow(self, execution_id: str):
        """Execute a workflow."""
        try:
            execution = self.executions[execution_id]
            workflow = self.workflows[execution.workflow_id]
            
            # Update status
            execution.status = WorkflowStatus.RUNNING
            self.active_executions[execution_id] = execution
            
            # Initialize step dependencies
            self._initialize_step_dependencies(workflow)
            
            # Execute based on mode
            if workflow.execution_mode == WorkflowExecutionMode.SEQUENTIAL:
                await self._execute_sequential(execution_id, workflow)
            elif workflow.execution_mode == WorkflowExecutionMode.PARALLEL:
                await self._execute_parallel(execution_id, workflow)
            elif workflow.execution_mode == WorkflowExecutionMode.CONDITIONAL:
                await self._execute_conditional(execution_id, workflow)
            elif workflow.execution_mode == WorkflowExecutionMode.LOOP:
                await self._execute_loop(execution_id, workflow)
            elif workflow.execution_mode == WorkflowExecutionMode.FORK_JOIN:
                await self._execute_fork_join(execution_id, workflow)
            else:
                await self._execute_sequential(execution_id, workflow)
            
            # Mark as completed
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.utcnow()
            
            # Update metrics
            self.metrics.completed_workflows += 1
            execution_time = (execution.end_time - execution.start_time).total_seconds()
            self.metrics.update_average_execution_time(execution_time)
            
            # Remove from active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            self.logger.info(f"Completed workflow execution {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {execution_id}: {e}")
            await self._handle_workflow_error(execution_id, str(e))
    
    async def _execute_sequential(self, execution_id: str, workflow: Workflow):
        """Execute workflow steps sequentially."""
        execution = self.executions[execution_id]
        
        for step in workflow.steps:
            if execution.status == WorkflowStatus.CANCELLED:
                break
            
            # Wait for dependencies
            await self._wait_for_dependencies(execution_id, step.id)
            
            # Execute step
            step_result = await self._execute_step(execution_id, step)
            
            if step_result['status'] == StepStatus.FAILED:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = step_result['error']
                break
            
            # Update execution state
            execution.completed_steps.add(step.id)
            execution.step_results[step.id] = step_result
    
    async def _execute_parallel(self, execution_id: str, workflow: Workflow):
        """Execute workflow steps in parallel."""
        execution = self.executions[execution_id]
        
        # Group steps by dependency level
        dependency_levels = self._calculate_dependency_levels(workflow)
        
        for level in dependency_levels:
            if execution.status == WorkflowStatus.CANCELLED:
                break
            
            # Execute all steps in this level in parallel
            step_tasks = []
            for step_id in level:
                step = next(s for s in workflow.steps if s.id == step_id)
                task = asyncio.create_task(self._execute_step(execution_id, step))
                step_tasks.append(task)
            
            # Wait for all steps in this level to complete
            step_results = await asyncio.gather(*step_tasks, return_exceptions=True)
            
            # Check for failures
            for i, result in enumerate(step_results):
                if isinstance(result, Exception):
                    step_id = level[i]
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = str(result)
                    break
                elif result['status'] == StepStatus.FAILED:
                    step_id = level[i]
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = result['error']
                    break
            
            if execution.status == WorkflowStatus.FAILED:
                break
            
            # Update execution state
            for step_id, result in zip(level, step_results):
                if not isinstance(result, Exception):
                    execution.completed_steps.add(step_id)
                    execution.step_results[step_id] = result
    
    async def _execute_conditional(self, execution_id: str, workflow: Workflow):
        """Execute workflow steps conditionally."""
        execution = self.executions[execution_id]
        
        for step in workflow.steps:
            if execution.status == WorkflowStatus.CANCELLED:
                break
            
            # Check conditions
            if not self._evaluate_step_conditions(step, execution):
                execution.step_results[step.id] = {
                    'status': StepStatus.SKIPPED,
                    'reason': 'Conditions not met'
                }
                continue
            
            # Wait for dependencies
            await self._wait_for_dependencies(execution_id, step.id)
            
            # Execute step
            step_result = await self._execute_step(execution_id, step)
            
            if step_result['status'] == StepStatus.FAILED:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = step_result['error']
                break
            
            # Update execution state
            execution.completed_steps.add(step.id)
            execution.step_results[step.id] = step_result
    
    async def _execute_loop(self, execution_id: str, workflow: Workflow):
        """Execute workflow steps in a loop."""
        execution = self.executions[execution_id]
        
        max_iterations = workflow.metadata.get('max_iterations', 100)
        iteration = 0
        
        while iteration < max_iterations and execution.status != WorkflowStatus.CANCELLED:
            iteration += 1
            
            # Execute all steps
            for step in workflow.steps:
                if execution.status == WorkflowStatus.CANCELLED:
                    break
                
                # Wait for dependencies
                await self._wait_for_dependencies(execution_id, step.id)
                
                # Execute step
                step_result = await self._execute_step(execution_id, step)
                
                if step_result['status'] == StepStatus.FAILED:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = step_result['error']
                    break
                
                # Update execution state
                execution.step_results[f"{step.id}_iter_{iteration}"] = step_result
            
            # Check loop condition
            if not self._evaluate_loop_condition(workflow, execution, iteration):
                break
    
    async def _execute_fork_join(self, execution_id: str, workflow: Workflow):
        """Execute workflow using fork-join pattern."""
        execution = self.executions[execution_id]
        
        # Find fork and join points
        fork_steps = [s for s in workflow.steps if s.step_type == 'fork']
        join_steps = [s for s in workflow.steps if s.step_type == 'join']
        
        for fork_step in fork_steps:
            # Execute parallel branches
            branch_tasks = []
            for branch in fork_step.metadata.get('branches', []):
                task = asyncio.create_task(self._execute_branch(execution_id, branch))
                branch_tasks.append(task)
            
            # Wait for all branches to complete
            branch_results = await asyncio.gather(*branch_tasks, return_exceptions=True)
            
            # Check for failures
            for result in branch_results:
                if isinstance(result, Exception):
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = str(result)
                    break
            
            if execution.status == WorkflowStatus.FAILED:
                break
    
    async def _execute_step(self, execution_id: str, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            step_id = step.id
            execution = self.executions[execution_id]
            
            # Update step status
            self.step_executions[execution_id][step_id] = {
                'status': StepStatus.RUNNING,
                'start_time': datetime.utcnow()
            }
            
            # Add to running steps
            self.running_steps[execution_id].add(step_id)
            
            # Create job for step execution
            job = await self._create_step_job(execution_id, step)
            
            # Wait for job completion
            job_result = await self._wait_for_job_completion(job.id, step.timeout)
            
            # Update step status
            if job_result['status'] == JobStatus.COMPLETED:
                step_status = StepStatus.COMPLETED
                step_result = {
                    'status': step_status,
                    'outputs': job_result.get('outputs', {}),
                    'execution_time': job_result.get('execution_time', 0)
                }
            else:
                if job.can_retry():
                    job.retry_count += 1
                    delay = job.get_retry_delay()
                    self.logger.info(f"Job {job.id} failed, retrying in {delay.total_seconds()} seconds...")
                    await asyncio.sleep(delay.total_seconds())
                    return await self._execute_step(execution_id, step)
                else:
                    step_status = StepStatus.FAILED
                    step_result = {
                        'status': step_status,
                        'error': job_result.get('error', 'Unknown error'),
                        'execution_time': job_result.get('execution_time', 0)
                    }
            
            # Update step execution state
            self.step_executions[execution_id][step_id].update({
                'status': step_status,
                'end_time': datetime.utcnow(),
                'result': step_result
            })
            
            # Remove from running steps
            self.running_steps[execution_id].discard(step_id)
            
            return step_result
            
        except Exception as e:
            self.logger.error(f"Error executing step {step.id}: {e}")
            return {
                'status': StepStatus.FAILED,
                'error': str(e)
            }
    
    async def _create_step_job(self, execution_id: str, step: WorkflowStep) -> Job:
        """Create a job for step execution."""
        job = Job(
            id=str(uuid.uuid4()),
            type=JobType(step.step_type),
            priority=JobPriority.MEDIUM,
            data={'workflow_execution_id': execution_id, 'step_id': step.id, 'inputs': step.inputs},
            resource_requirements=step.resource_requirements,
            metadata={
                'workflow_execution_id': execution_id,
                'workflow_step_id': step.id,
            }
        )
        
        if self.taskmaster:
            await self.taskmaster.submit_job(job)

        return job
    
    async def _wait_for_job_completion(self, job_id: str, timeout: timedelta) -> Dict[str, Any]:
        """Wait for job completion."""
        if not self.taskmaster:
            # Simulate job completion if no taskmaster is present
            await asyncio.sleep(1)
            return {
                'status': JobStatus.COMPLETED,
                'outputs': {'result': 'success'},
                'execution_time': 1.0
            }

        start_time = datetime.utcnow()
        while datetime.utcnow() - start_time < timeout:
            job_status = await self.taskmaster.get_job_status(job_id)
            if job_status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job = self.taskmaster.active_jobs.get(job_id)
                return {
                    'status': job_status,
                    'outputs': job.outputs if job else {},
                    'error': job.error_message if job else None,
                    'execution_time': (datetime.utcnow() - start_time).total_seconds()
                }
            await asyncio.sleep(1)
        
        return {'status': JobStatus.FAILED, 'error': 'Timeout'}
    
    def _initialize_step_dependencies(self, workflow: Workflow):
        """Initialize step dependencies for a workflow."""
        for step in workflow.steps:
            if step.dependencies:
                self.step_dependencies[workflow.id][step.id] = step.dependencies
    
    def _calculate_dependency_levels(self, workflow: Workflow) -> List[List[str]]:
        """Calculate dependency levels for parallel execution."""
        # This is a simplified implementation
        # In a real system, you'd use topological sorting
        levels = []
        remaining_steps = set(step.id for step in workflow.steps)
        
        while remaining_steps:
            current_level = []
            for step_id in remaining_steps:
                step = next(s for s in workflow.steps if s.id == step_id)
                if not step.dependencies or all(dep in [s for level in levels for s in level] for dep in step.dependencies):
                    current_level.append(step_id)
            
            if not current_level:
                # Circular dependency detected
                break
            
            levels.append(current_level)
            remaining_steps -= set(current_level)
        
        return levels
    
    def _evaluate_step_conditions(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Evaluate step execution conditions."""
        if not step.conditions:
            return True
        
        # Simple condition evaluation
        # In a real system, you'd use a more sophisticated expression evaluator
        for condition_key, condition_value in step.conditions.items():
            if condition_key == 'requires_output':
                required_output = condition_value
                if not any(required_output in result.get('outputs', {}) for result in execution.step_results.values()):
                    return False
        
        return True
    
    def _evaluate_loop_condition(self, workflow: Workflow, execution: WorkflowExecution, iteration: int) -> bool:
        """Evaluate loop continuation condition."""
        loop_condition = workflow.metadata.get('loop_condition', {})
        
        if 'max_iterations' in loop_condition:
            if iteration >= loop_condition['max_iterations']:
                return False
        
        if 'until_output' in loop_condition:
            expected_output = loop_condition['until_output']
            if any(expected_output in result.get('outputs', {}) for result in execution.step_results.values()):
                return False
        
        return True
    
    async def _wait_for_dependencies(self, execution_id: str, step_id: str):
        """Wait for step dependencies to complete."""
        execution = self.executions[execution_id]
        workflow = self.workflows[execution.workflow_id]
        
        if execution_id in self.step_dependencies and step_id in self.step_dependencies[execution_id]:
            dependencies = self.step_dependencies[execution_id][step_id]
            
            while not all(dep in execution.completed_steps for dep in dependencies):
                await asyncio.sleep(0.1)
    
    async def _cancel_step(self, execution_id: str, step_id: str):
        """Cancel a running step."""
        # This would integrate with your job management system
        # For now, just update the status
        if execution_id in self.step_executions and step_id in self.step_executions[execution_id]:
            self.step_executions[execution_id][step_id]['status'] = StepStatus.CANCELLED
    
    async def _handle_workflow_error(self, execution_id: str, error_message: str):
        """Handle workflow execution errors."""
        execution = self.executions[execution_id]
        execution.status = WorkflowStatus.FAILED
        execution.error_message = error_message
        execution.end_time = datetime.utcnow()
        
        # Update metrics
        self.metrics.failed_workflows += 1
        
        # Remove from active executions
        if execution_id in self.active_executions:
            del self.active_executions[execution_id]
        
        # Handle recovery if enabled
        if self.enable_recovery:
            await self._attempt_workflow_recovery(execution_id)
    
    async def _attempt_workflow_recovery(self, execution_id: str):
        """Attempt to recover from workflow failure."""
        self.logger.info(f"Attempting recovery for failed workflow {execution_id}")
        execution = self.executions.get(execution_id)
        if not execution:
            return

        # Simple recovery: restart the workflow from the failed step
        if execution.failed_steps:
            failed_step_id = list(execution.failed_steps)[0]
            self.logger.info(f"Restarting workflow from failed step: {failed_step_id}")

            # Reset the status of the failed step and re-queue the execution
            execution.status = WorkflowStatus.PENDING
            execution.failed_steps.clear()
            execution.error_message = None

            # We need to be careful not to create an infinite loop.
            # A real implementation would have a limit on the number of retries.
            # For now, we will just re-queue it once.
            if execution.metadata.get("retry_count", 0) < 1:
                execution.metadata["retry_count"] = 1
                self.execution_queue.append(execution_id)
    
    def _apply_workflow_parameters(self, workflow: Workflow, parameters: Dict[str, Any]) -> Workflow:
        """Apply parameters to workflow template."""
        # This would replace placeholders in the workflow with actual values
        # For now, just return the workflow as-is
        return workflow
    
    async def _load_workflow_templates(self):
        """Load workflow templates from storage."""
        # This would load templates from your storage system
        # For now, create some mock templates
        
        self.workflow_templates = {
            'forensic_investigation': {
                'name': 'Forensic Investigation',
                'description': 'Standard forensic investigation workflow',
                'execution_mode': WorkflowExecutionMode.SEQUENTIAL,
                'steps': [
                    {
                        'id': 'evidence_collection',
                        'name': 'Evidence Collection',
                        'step_type': 'evidence_collection',
                        'agent_type': AgentType.EVIDENCE_AGENT
                    },
                    {
                        'id': 'analysis',
                        'name': 'Evidence Analysis',
                        'step_type': 'analysis',
                        'agent_type': AgentType.ANALYSIS_AGENT,
                        'dependencies': ['evidence_collection']
                    },
                    {
                        'id': 'reporting',
                        'name': 'Report Generation',
                        'step_type': 'reporting',
                        'agent_type': AgentType.REPORTING_AGENT,
                        'dependencies': ['analysis']
                    }
                ]
            }
        }
    
    async def _monitor_workflow_timeouts(self):
        """Monitor and handle workflow timeouts."""
        while True:
            try:
                current_time = datetime.utcnow()
                
                for execution_id, execution in list(self.active_executions.items()):
                    if current_time - execution.start_time > self.workflow_timeout:
                        self.logger.warning(f"Workflow {execution_id} timed out")
                        await self.cancel_workflow(execution_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring workflow timeouts: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_completed_executions(self):
        """Clean up completed workflow executions."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=7)
                
                # Remove old completed executions
                expired_executions = [
                    exec_id for exec_id, execution in self.executions.items()
                    if execution.end_time and execution.end_time < cutoff_time
                ]
                
                for exec_id in expired_executions:
                    del self.executions[exec_id]
                
                if expired_executions:
                    self.logger.info(f"Cleaned up {len(expired_executions)} expired executions")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up executions: {e}")
                await asyncio.sleep(3600)
    
    async def _update_workflow_metrics(self):
        """Update workflow performance metrics."""
        while True:
            try:
                # Update success rate
                self.metrics.update_success_rate()
                
                # Calculate step success rate
                total_steps = sum(len(execution.completed_steps) + len(execution.failed_steps) 
                                for execution in self.executions.values())
                successful_steps = sum(len(execution.completed_steps) 
                                     for execution in self.executions.values())
                
                if total_steps > 0:
                    self.metrics.step_success_rate = successful_steps / total_steps
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating workflow metrics: {e}")
                await asyncio.sleep(300)


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'max_concurrent_workflows': 100,
        'max_parallel_steps': 20,
        'workflow_timeout_hours': 24,
        'step_timeout_hours': 4,
        'enable_recovery': True,
        'enable_rollback': True
    }
    
    # Initialize workflow orchestrator
    orchestrator = WorkflowOrchestrator(config)
    
    print("WorkflowOrchestrator system initialized successfully!")
