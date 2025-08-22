"""
LangGraph Multi-Agent Integration - Advanced Agent Communication and Coordination

This module implements the LangGraphIntegration class that provides
advanced multi-agent orchestration capabilities using LangGraph technology
for the forensic platform.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import networkx as nx
from pathlib import Path
import pandas as pd

from ...taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class WorkflowState(Enum):
    """States of a LangGraph workflow."""
    INITIALIZED = "initialized"                             # Workflow initialized
    RUNNING = "running"                                     # Workflow running
    PAUSED = "paused"                                       # Workflow paused
    COMPLETED = "completed"                                 # Workflow completed
    FAILED = "failed"                                        # Workflow failed
    CANCELLED = "cancelled"                                 # Workflow cancelled


class NodeType(Enum):
    """Types of workflow nodes."""
    AGENT_NODE = "agent_node"                               # Agent execution node
    CONDITIONAL_NODE = "conditional_node"                    # Conditional logic node
    PARALLEL_NODE = "parallel_node"                          # Parallel execution node
    MERGE_NODE = "merge_node"                                # Result merge node
    VALIDATION_NODE = "validation_node"                      # Data validation node
    TRANSFORMATION_NODE = "transformation_node"               # Data transformation node


class EdgeType(Enum):
    """Types of workflow edges."""
    SEQUENTIAL = "sequential"                                # Sequential execution
    CONDITIONAL = "conditional"                              # Conditional execution
    PARALLEL = "parallel"                                    # Parallel execution
    ERROR_HANDLING = "error_handling"                        # Error handling path
    LOOPBACK = "loopback"                                    # Loop back to previous node


@dataclass
class WorkflowNode:
    """A node in the LangGraph workflow."""
    
    node_id: str
    node_type: NodeType
    node_name: str
    node_config: Dict[str, Any]
    agent_id: Optional[str]
    execution_order: int
    dependencies: List[str]
    timeout: int  # seconds
    retry_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """An edge in the LangGraph workflow."""
    
    edge_id: str
    source_node: str
    target_node: str
    edge_type: EdgeType
    condition: Optional[str]
    weight: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """A workflow execution instance."""
    
    execution_id: str
    workflow_id: str
    state: WorkflowState
    start_time: datetime
    end_time: Optional[datetime]
    current_node: Optional[str]
    completed_nodes: List[str]
    failed_nodes: List[str]
    execution_log: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """A message between agents in the workflow."""
    
    message_id: str
    source_agent: str
    target_agent: str
    message_type: str
    message_data: Dict[str, Any]
    timestamp: datetime
    priority: str
    correlation_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    
    result_id: str
    execution_id: str
    success: bool
    output_data: Dict[str, Any]
    execution_time: float
    node_results: Dict[str, Any]
    error_messages: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LangGraphIntegration:
    """
    Advanced multi-agent orchestration using LangGraph technology.
    
    The LangGraphIntegration is responsible for:
    - Creating and managing complex workflow graphs
    - Coordinating agent communication and execution
    - Managing workflow state and transitions
    - Supporting parallel and conditional execution
    - Providing advanced orchestration capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LangGraphIntegration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_workflow_nodes = config.get('max_workflow_nodes', 100)
        self.max_parallel_executions = config.get('max_parallel_executions', 10)
        self.default_timeout = config.get('default_timeout', 300)  # 5 minutes
        self.max_retries = config.get('max_retries', 3)
        
        # Workflow management
        self.workflows: Dict[str, nx.DiGraph] = {}
        self.workflow_configs: Dict[str, Dict[str, Any]] = {}
        self.workflow_executions: Dict[str, WorkflowExecution] = {}
        
        # Agent coordination
        self.agent_messages: Dict[str, AgentMessage] = {}
        self.message_queues: Dict[str, deque] = defaultdict(deque)
        self.agent_states: Dict[str, str] = {}
        
        # Performance tracking
        self.total_workflows_created = 0
        self.total_executions = 0
        self.successful_executions = 0
        self.average_execution_time = 0.0
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("LangGraphIntegration initialized successfully")
    
    async def start(self):
        """Start the LangGraphIntegration."""
        self.logger.info("Starting LangGraphIntegration...")
        
        # Initialize LangGraph components
        await self._initialize_langgraph_components()
        
        # Start background tasks
        asyncio.create_task(self._monitor_workflow_executions())
        asyncio.create_task(self._process_agent_messages())
        asyncio.create_task(self._cleanup_completed_executions())
        
        self.logger.info("LangGraphIntegration started successfully")
    
    async def stop(self):
        """Stop the LangGraphIntegration."""
        self.logger.info("Stopping LangGraphIntegration...")
        self.logger.info("LangGraphIntegration stopped")
    
    async def create_workflow(self, workflow_name: str, workflow_description: str,
                             nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> str:
        """Create a new LangGraph workflow."""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Create workflow graph
            workflow_graph = nx.DiGraph()
            
            # Add nodes
            for node_data in nodes:
                node = WorkflowNode(
                    node_id=node_data.get('node_id', str(uuid.uuid4())),
                    node_type=NodeType(node_data.get('node_type', 'agent_node')),
                    node_name=node_data['node_name'],
                    node_config=node_data.get('config', {}),
                    agent_id=node_data.get('agent_id'),
                    execution_order=node_data.get('execution_order', 0),
                    dependencies=node_data.get('dependencies', []),
                    timeout=node_data.get('timeout', self.default_timeout),
                    retry_count=node_data.get('retry_count', self.max_retries)
                )
                
                workflow_graph.add_node(
                    node.node_id,
                    node_data=node,
                    node_type=node.node_type.value,
                    agent_id=node.agent_id,
                    execution_order=node.execution_order
                )
            
            # Add edges
            for edge_data in edges:
                edge = WorkflowEdge(
                    edge_id=edge_data.get('edge_id', str(uuid.uuid4())),
                    source_node=edge_data['source_node'],
                    target_node=edge_data['target_node'],
                    edge_type=EdgeType(edge_data.get('edge_type', 'sequential')),
                    condition=edge_data.get('condition'),
                    weight=edge_data.get('weight', 1.0)
                )
                
                workflow_graph.add_edge(
                    edge.source_node,
                    edge.target_node,
                    edge_id=edge.edge_id,
                    edge_type=edge.edge_type.value,
                    condition=edge.condition,
                    weight=edge.weight
                )
            
            # Validate workflow
            if not nx.is_directed_acyclic_graph(workflow_graph):
                raise ValueError("Workflow contains cycles")
            
            # Store workflow
            self.workflows[workflow_id] = workflow_graph
            self.workflow_configs[workflow_id] = {
                'name': workflow_name,
                'description': workflow_description,
                'node_count': len(nodes),
                'edge_count': len(edges),
                'created_date': datetime.utcnow().isoformat()
            }
            
            # Update statistics
            self.total_workflows_created += 1
            
            self.logger.info(f"Created workflow: {workflow_id} - {workflow_name}")
            
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> str:
        """Execute a LangGraph workflow."""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow_graph = self.workflows[workflow_id]
            
            # Create execution instance
            execution = WorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                state=WorkflowState.INITIALIZED,
                start_time=datetime.utcnow(),
                end_time=None,
                current_node=None,
                completed_nodes=[],
                failed_nodes=[],
                execution_log=[]
            )
            
            # Store execution
            self.workflow_executions[execution.execution_id] = execution
            
            # Start execution
            asyncio.create_task(self._execute_workflow_graph(execution, input_data or {}))
            
            # Update statistics
            self.total_executions += 1
            
            self.logger.info(f"Started workflow execution: {execution.execution_id}")
            
            return execution.execution_id
            
        except Exception as e:
            self.logger.error(f"Error executing workflow: {e}")
            raise
    
    async def _execute_workflow_graph(self, execution: WorkflowExecution, input_data: Dict[str, Any]):
        """Execute the workflow graph."""
        try:
            workflow_graph = self.workflows[execution.workflow_id]
            
            # Update state
            execution.state = WorkflowState.RUNNING
            execution.execution_log.append(f"Workflow execution started at {execution.start_time}")
            
            # Find starting nodes (nodes with no incoming edges)
            starting_nodes = [node for node in workflow_graph.nodes() 
                            if workflow_graph.in_degree(node) == 0]
            
            if not starting_nodes:
                raise ValueError("No starting nodes found in workflow")
            
            # Execute starting nodes
            await self._execute_nodes(execution, starting_nodes, input_data)
            
            # Continue execution until completion
            while execution.state == WorkflowState.RUNNING:
                # Find next executable nodes
                next_nodes = self._find_next_executable_nodes(execution, workflow_graph)
                
                if not next_nodes:
                    # No more nodes to execute
                    execution.state = WorkflowState.COMPLETED
                    execution.end_time = datetime.utcnow()
                    execution.execution_log.append("Workflow execution completed successfully")
                    break
                
                # Execute next nodes
                await self._execute_nodes(execution, next_nodes, input_data)
                
                # Check for completion
                if len(execution.completed_nodes) == len(workflow_graph.nodes()):
                    execution.state = WorkflowState.COMPLETED
                    execution.end_time = datetime.utcnow()
                    execution.execution_log.append("All nodes completed successfully")
                    break
            
            # Update statistics
            if execution.state == WorkflowState.COMPLETED:
                self.successful_executions += 1
                execution_time = (execution.end_time - execution.start_time).total_seconds()
                self.average_execution_time = (self.average_execution_time + execution_time) / 2
            
            self.logger.info(f"Workflow execution {execution.execution_id} completed with state: {execution.state.value}")
            
        except Exception as e:
            execution.state = WorkflowState.FAILED
            execution.end_time = datetime.utcnow()
            execution.execution_log.append(f"Workflow execution failed: {e}")
            self.logger.error(f"Error executing workflow graph: {e}")
    
    async def _execute_nodes(self, execution: WorkflowExecution, node_ids: List[str], input_data: Dict[str, Any]):
        """Execute a set of nodes."""
        try:
            workflow_graph = self.workflows[execution.workflow_id]
            
            # Execute nodes in parallel if possible
            if len(node_ids) == 1:
                await self._execute_single_node(execution, node_ids[0], input_data)
            else:
                # Execute nodes in parallel
                tasks = [
                    self._execute_single_node(execution, node_id, input_data)
                    for node_id in node_ids
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Error executing nodes: {e}")
    
    async def _execute_single_node(self, execution: WorkflowExecution, node_id: str, input_data: Dict[str, Any]):
        """Execute a single node."""
        try:
            workflow_graph = self.workflows[execution.workflow_id]
            node_data = workflow_graph.nodes[node_id]['node_data']
            
            execution.current_node = node_id
            execution.execution_log.append(f"Executing node: {node_data.node_name}")
            
            # Execute based on node type
            if node_data.node_type == NodeType.AGENT_NODE:
                result = await self._execute_agent_node(node_data, input_data)
            elif node_data.node_type == NodeType.CONDITIONAL_NODE:
                result = await self._execute_conditional_node(node_data, input_data)
            elif node_data.node_type == NodeType.PARALLEL_NODE:
                result = await self._execute_parallel_node(node_data, input_data)
            elif node_data.node_type == NodeType.MERGE_NODE:
                result = await self._execute_merge_node(node_data, input_data)
            elif node_data.node_type == NodeType.VALIDATION_NODE:
                result = await self._execute_validation_node(node_data, input_data)
            elif node_data.node_type == NodeType.TRANSFORMATION_NODE:
                result = await self._execute_transformation_node(node_data, input_data)
            else:
                result = {'success': False, 'error': f'Unknown node type: {node_data.node_type.value}'}
            
            # Handle execution result
            if result.get('success', False):
                execution.completed_nodes.append(node_id)
                execution.execution_log.append(f"Node {node_data.node_name} completed successfully")
            else:
                execution.failed_nodes.append(node_id)
                execution.execution_log.append(f"Node {node_data.node_name} failed: {result.get('error', 'Unknown error')}")
                
                # Check retry logic
                if node_data.retry_count > 0:
                    node_data.retry_count -= 1
                    execution.execution_log.append(f"Retrying node {node_data.node_name}, {node_data.retry_count} retries remaining")
                    await asyncio.sleep(1)  # Brief delay before retry
                    await self._execute_single_node(execution, node_id, input_data)
                else:
                    execution.state = WorkflowState.FAILED
                    execution.end_time = datetime.utcnow()
                    execution.execution_log.append(f"Node {node_data.node_name} failed after all retries")
            
        except Exception as e:
            execution.failed_nodes.append(node_id)
            execution.execution_log.append(f"Error executing node {node_id}: {e}")
            self.logger.error(f"Error executing single node: {e}")
    
    async def _execute_agent_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent node."""
        try:
            if not node.agent_id:
                return {'success': False, 'error': 'No agent ID specified'}
            
            # Simulate agent execution
            # In production, this would call the actual agent
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Generate mock result
            result = {
                'success': True,
                'output': f"Agent {node.agent_id} processed data",
                'timestamp': datetime.utcnow().isoformat(),
                'node_id': node.node_id
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_conditional_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a conditional node."""
        try:
            # Simple conditional logic
            condition = node.node_config.get('condition', 'true')
            
            # Evaluate condition (simplified)
            if condition == 'true' or input_data.get('condition', True):
                result = {
                    'success': True,
                    'output': 'Condition met',
                    'branch': 'true'
                }
            else:
                result = {
                    'success': True,
                    'output': 'Condition not met',
                    'branch': 'false'
                }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_parallel_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parallel node."""
        try:
            # Parallel execution logic
            parallel_tasks = node.node_config.get('parallel_tasks', [])
            
            if not parallel_tasks:
                return {'success': True, 'output': 'No parallel tasks defined'}
            
            # Simulate parallel execution
            results = []
            for task in parallel_tasks:
                await asyncio.sleep(0.05)  # Simulate task execution
                results.append(f"Task {task} completed")
            
            result = {
                'success': True,
                'output': f"Executed {len(parallel_tasks)} parallel tasks",
                'results': results
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_merge_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a merge node."""
        try:
            # Merge logic for combining results
            merge_strategy = node.node_config.get('merge_strategy', 'concatenate')
            
            if merge_strategy == 'concatenate':
                merged_output = "Merged results: " + str(input_data.get('results', []))
            elif merge_strategy == 'aggregate':
                merged_output = f"Aggregated {len(input_data.get('results', []))} results"
            else:
                merged_output = "Default merge completed"
            
            result = {
                'success': True,
                'output': merged_output,
                'merge_strategy': merge_strategy
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_validation_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a validation node."""
        try:
            # Data validation logic
            validation_rules = node.node_config.get('validation_rules', [])
            
            if not validation_rules:
                return {'success': True, 'output': 'No validation rules defined'}
            
            # Simple validation
            validation_results = []
            for rule in validation_rules:
                if rule in input_data:
                    validation_results.append(f"Rule {rule}: PASSED")
                else:
                    validation_results.append(f"Rule {rule}: FAILED")
            
            all_passed = all('PASSED' in result for result in validation_results)
            
            result = {
                'success': all_passed,
                'output': f"Validation {'passed' if all_passed else 'failed'}",
                'validation_results': validation_results
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_transformation_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a transformation node."""
        try:
            # Data transformation logic
            transformation_type = node.node_config.get('transformation_type', 'format')
            
            if transformation_type == 'format':
                transformed_data = f"Formatted: {str(input_data)}"
            elif transformation_type == 'filter':
                transformed_data = {k: v for k, v in input_data.items() if v is not None}
            elif transformation_type == 'enrich':
                transformed_data = {**input_data, 'enriched': True, 'timestamp': datetime.utcnow().isoformat()}
            else:
                transformed_data = input_data
            
            result = {
                'success': True,
                'output': 'Data transformation completed',
                'transformed_data': transformed_data
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _find_next_executable_nodes(self, execution: WorkflowExecution, workflow_graph: nx.DiGraph) -> List[str]:
        """Find the next nodes that can be executed."""
        try:
            executable_nodes = []
            
            for node_id in workflow_graph.nodes():
                if node_id in execution.completed_nodes or node_id in execution.failed_nodes:
                    continue
                
                # Check if all dependencies are completed
                dependencies = list(workflow_graph.predecessors(node_id))
                if all(dep in execution.completed_nodes for dep in dependencies):
                    executable_nodes.append(node_id)
            
            return executable_nodes
            
        except Exception as e:
            self.logger.error(f"Error finding next executable nodes: {e}")
            return []
    
    async def send_agent_message(self, source_agent: str, target_agent: str, message_type: str,
                                message_data: Dict[str, Any], priority: str = 'normal',
                                correlation_id: str = None) -> str:
        """Send a message between agents."""
        try:
            message = AgentMessage(
                message_id=str(uuid.uuid4()),
                source_agent=source_agent,
                target_agent=target_agent,
                message_type=message_type,
                message_data=message_data,
                timestamp=datetime.utcnow(),
                priority=priority,
                correlation_id=correlation_id or str(uuid.uuid4())
            )
            
            # Store message
            self.agent_messages[message.message_id] = message
            
            # Add to target agent's queue
            self.message_queues[target_agent].append(message.message_id)
            
            self.logger.info(f"Sent message: {message.message_id} from {source_agent} to {target_agent}")
            
            return message.message_id
            
        except Exception as e:
            self.logger.error(f"Error sending agent message: {e}")
            raise
    
    async def get_agent_messages(self, agent_id: str, message_type: str = None) -> List[AgentMessage]:
        """Get messages for a specific agent."""
        try:
            messages = []
            
            for message_id in self.message_queues[agent_id]:
                if message_id in self.agent_messages:
                    message = self.agent_messages[message_id]
                    
                    if message_type is None or message.message_type == message_type:
                        messages.append(message)
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error getting agent messages: {e}")
            return []
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution."""
        try:
            if execution_id not in self.workflow_executions:
                raise ValueError(f"Execution {execution_id} not found")
            
            execution = self.workflow_executions[execution_id]
            
            status = {
                'execution_id': execution.execution_id,
                'workflow_id': execution.workflow_id,
                'state': execution.state.value,
                'start_time': execution.start_time.isoformat(),
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'current_node': execution.current_node,
                'completed_nodes': execution.completed_nodes,
                'failed_nodes': execution.failed_nodes,
                'progress': len(execution.completed_nodes) / (len(execution.completed_nodes) + len(execution.failed_nodes) + 1),
                'execution_log': execution.execution_log[-10:]  # Last 10 log entries
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {e}")
            return {}
    
    async def _monitor_workflow_executions(self):
        """Monitor workflow executions."""
        while True:
            try:
                # Check for stuck executions
                current_time = datetime.utcnow()
                stuck_executions = []
                
                for execution in self.workflow_executions.values():
                    if execution.state == WorkflowState.RUNNING:
                        # Check if execution has been running too long
                        if execution.start_time and (current_time - execution.start_time).total_seconds() > 3600:  # 1 hour
                            stuck_executions.append(execution.execution_id)
                
                if stuck_executions:
                    self.logger.warning(f"Found {len(stuck_executions)} stuck executions")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring workflow executions: {e}")
                await asyncio.sleep(60)
    
    async def _process_agent_messages(self):
        """Process agent messages."""
        while True:
            try:
                # Process message queues
                for agent_id, message_queue in self.message_queues.items():
                    if message_queue:
                        # Process high priority messages first
                        high_priority = [msg_id for msg_id in message_queue 
                                       if self.agent_messages.get(msg_id, {}).get('priority') == 'high']
                        
                        if high_priority:
                            # Process high priority messages
                            for msg_id in high_priority[:5]:  # Process up to 5 at a time
                                message_queue.remove(msg_id)
                        else:
                            # Process normal priority messages
                            for msg_id in list(message_queue)[:3]:  # Process up to 3 at a time
                                message_queue.remove(msg_id)
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                self.logger.error(f"Error processing agent messages: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_completed_executions(self):
        """Clean up completed workflow executions."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=24)  # Keep 24 hours of data
                
                # Clean up old executions
                old_executions = [
                    exec_id for exec_id, execution in self.workflow_executions.items()
                    if execution.end_time and execution.end_time < cutoff_time
                ]
                
                for exec_id in old_executions:
                    del self.workflow_executions[exec_id]
                
                if old_executions:
                    self.logger.info(f"Cleaned up {len(old_executions)} old executions")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up executions: {e}")
                await asyncio.sleep(3600)
    
    async def _initialize_langgraph_components(self):
        """Initialize LangGraph components."""
        try:
            # Initialize default components
            await self._initialize_default_components()
            
            self.logger.info("LangGraph components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing LangGraph components: {e}")
    
    async def _initialize_default_components(self):
        """Initialize default LangGraph components."""
        try:
            # This would initialize default components
            # For now, just log initialization
            self.logger.info("Default LangGraph components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing default components: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_workflows_created': self.total_workflows_created,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'average_execution_time': self.average_execution_time,
            'active_executions': len([e for e in self.workflow_executions.values() 
                                   if e.state == WorkflowState.RUNNING]),
            'workflow_states_supported': [s.value for s in WorkflowState],
            'node_types_supported': [t.value for t in NodeType],
            'edge_types_supported': [t.value for t in EdgeType],
            'total_agent_messages': len(self.agent_messages)
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'max_workflow_nodes': 100,
        'max_parallel_executions': 10,
        'default_timeout': 300,
        'max_retries': 3
    }
    
    # Initialize LangGraph integration
    integration = LangGraphIntegration(config)
    
    print("LangGraphIntegration system initialized successfully!")
