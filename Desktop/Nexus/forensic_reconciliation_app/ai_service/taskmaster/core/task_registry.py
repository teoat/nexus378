"""
Task Registry - Prevents overlapping implementations and manages task dependencies
"""

import hashlib
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class TaskSignature:
    """Unique signature for a task to prevent duplicates"""
    name: str
    description: str
    input_parameters: Dict[str, Any]
    output_schema: Dict[str, Any]
    hash: str
    
    def __post_init__(self):
        if not self.hash:
            self.hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate unique hash for task signature"""
        content = f"{self.name}:{self.description}:{json.dumps(self.input_parameters, sort_keys=True)}:{json.dumps(self.output_schema, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class TaskImplementation:
    """Implementation details for a task"""
    task_id: str
    agent_id: str
    implementation_hash: str
    created_at: datetime
    status: str
    metadata: Dict[str, Any]


class TaskRegistry:
    """Central registry to prevent overlapping task implementations"""
    
    def __init__(self):
        self.task_signatures: Dict[str, TaskSignature] = {}
        self.implementations: Dict[str, TaskImplementation] = {}
        self.task_dependencies: Dict[str, Set[str]] = {}
        self.implementation_locks: Dict[str, str] = {}  # task_id -> agent_id
    
    def register_task_signature(self, name: str, description: str, 
                              input_parameters: Dict[str, Any] = None,
                              output_schema: Dict[str, Any] = None) -> str:
        """Register a new task signature"""
        signature = TaskSignature(
            name=name,
            description=description,
            input_parameters=input_parameters or {},
            output_schema=output_schema or {}
        )
        
        self.task_signatures[signature.hash] = signature
        logger.info(f"Task signature registered: {name} (hash: {signature.hash[:8]})")
        return signature.hash
    
    def check_duplicate_implementation(self, name: str, description: str,
                                    input_parameters: Dict[str, Any] = None,
                                    output_schema: Dict[str, Any] = None) -> Optional[str]:
        """Check if a task implementation already exists"""
        # Generate hash for the proposed implementation
        proposed_signature = TaskSignature(
            name=name,
            description=description,
            input_parameters=input_parameters or {},
            output_schema=output_schema or {}
        )
        
        # Check if signature already exists
        if proposed_signature.hash in self.task_signatures:
            existing = self.task_signatures[proposed_signature.hash]
            logger.warning(f"Duplicate task implementation detected: {name}")
            return existing.hash
        
        return None
    
    def lock_task_implementation(self, task_id: str, agent_id: str) -> bool:
        """Lock a task for implementation by a specific agent"""
        if task_id in self.implementation_locks:
            if self.implementation_locks[task_id] != agent_id:
                logger.warning(f"Task {task_id} already locked by another agent")
                return False
        
        self.implementation_locks[task_id] = agent_id
        logger.info(f"Task {task_id} locked by agent {agent_id}")
        return True
    
    def unlock_task_implementation(self, task_id: str, agent_id: str) -> bool:
        """Unlock a task implementation"""
        if task_id in self.implementation_locks:
            if self.implementation_locks[task_id] == agent_id:
                del self.implementation_locks[task_id]
                logger.info(f"Task {task_id} unlocked by agent {agent_id}")
                return True
        
        return False
    
    def register_implementation(self, task_id: str, agent_id: str, 
                              implementation_hash: str, metadata: Dict[str, Any] = None) -> bool:
        """Register a completed task implementation"""
        if task_id not in self.implementation_locks:
            logger.error(f"Task {task_id} not locked for implementation")
            return False
        
        if self.implementation_locks[task_id] != agent_id:
            logger.error(f"Task {task_id} locked by different agent")
            return False
        
        implementation = TaskImplementation(
            task_id=task_id,
            agent_id=agent_id,
            implementation_hash=implementation_hash,
            created_at=datetime.now(),
            status="completed",
            metadata=metadata or {}
        )
        
        self.implementations[task_id] = implementation
        self.unlock_task_implementation(task_id, agent_id)
        
        logger.info(f"Task implementation registered: {task_id} by {agent_id}")
        return True
    
    def add_task_dependency(self, task_id: str, dependency_id: str):
        """Add a dependency between tasks"""
        if task_id not in self.task_dependencies:
            self.task_dependencies[task_id] = set()
        
        self.task_dependencies[task_id].add(dependency_id)
        logger.info(f"Dependency added: {task_id} -> {dependency_id}")
    
    def get_task_dependencies(self, task_id: str) -> Set[str]:
        """Get all dependencies for a task"""
        return self.task_dependencies.get(task_id, set())
    
    def check_dependencies_met(self, task_id: str) -> bool:
        """Check if all dependencies for a task are completed"""
        dependencies = self.get_task_dependencies(task_id)
        
        for dep_id in dependencies:
            if dep_id not in self.implementations:
                return False
            if self.implementations[dep_id].status != "completed":
                return False
        
        return True
    
    def get_available_tasks(self, agent_capabilities: List[str]) -> List[str]:
        """Get tasks available for an agent based on capabilities"""
        available_tasks = []
        
        for task_id in self.implementation_locks:
            # Check if task is locked
            if task_id in self.implementation_locks:
                continue
            
            # Check if dependencies are met
            if not self.check_dependencies_met(task_id):
                continue
            
            # Check if agent has required capabilities
            if self._agent_can_handle_task(task_id, agent_capabilities):
                available_tasks.append(task_id)
        
        return available_tasks
    
    def _agent_can_handle_task(self, task_id: str, agent_capabilities: List[str]) -> bool:
        """Check if an agent can handle a specific task"""
        # This is a simplified check - in practice, you'd want more sophisticated
        # capability matching based on task requirements
        return True
    
    def get_implementation_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get implementation status for a task"""
        if task_id in self.implementations:
            impl = self.implementations[task_id]
            return {
                "task_id": impl.task_id,
                "agent_id": impl.agent_id,
                "status": impl.status,
                "created_at": impl.created_at.isoformat(),
                "metadata": impl.metadata
            }
        return None
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of the task registry"""
        return {
            "total_signatures": len(self.task_signatures),
            "total_implementations": len(self.implementations),
            "locked_tasks": len(self.implementation_locks),
            "total_dependencies": sum(len(deps) for deps in self.task_dependencies.values())
        }


class TaskValidator:
    """Validates task implementations against signatures"""
    
    def __init__(self, registry: TaskRegistry):
        self.registry = registry
    
    def validate_implementation(self, task_id: str, implementation_data: Dict[str, Any]) -> bool:
        """Validate a task implementation against its signature"""
        # Get the task signature
        signature = None
        for sig in self.registry.task_signatures.values():
            if sig.name == task_id or sig.hash == task_id:
                signature = sig
                break
        
        if not signature:
            logger.error(f"No signature found for task: {task_id}")
            return False
        
        # Validate input parameters
        if not self._validate_input_parameters(implementation_data.get('input', {}), signature.input_parameters):
            logger.error(f"Input parameter validation failed for task: {task_id}")
            return False
        
        # Validate output schema
        if not self._validate_output_schema(implementation_data.get('output', {}), signature.output_schema):
            logger.error(f"Output schema validation failed for task: {task_id}")
            return False
        
        logger.info(f"Task implementation validation passed: {task_id}")
        return True
    
    def _validate_input_parameters(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Validate input parameters against expected schema"""
        # Simplified validation - in practice, you'd want more sophisticated validation
        for key, expected_type in expected.items():
            if key not in actual:
                logger.warning(f"Missing required input parameter: {key}")
                return False
        
        return True
    
    def _validate_output_schema(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Validate output against expected schema"""
        # Simplified validation - in practice, you'd want more sophisticated validation
        for key, expected_type in expected.items():
            if key not in actual:
                logger.warning(f"Missing required output field: {key}")
                return False
        
        return True


# Global registry instance
task_registry = TaskRegistry()
task_validator = TaskValidator(task_registry)
