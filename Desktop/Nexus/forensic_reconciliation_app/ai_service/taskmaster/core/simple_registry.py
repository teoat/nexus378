"""
Simple Task Registry - Prevents overlapping implementations
"""

import hashlib
import logging
from typing import Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class SimpleTaskRegistry:
    """Simple registry to prevent duplicate task implementations"""
    
    def __init__(self):
        self.registered_tasks: Dict[str, str] = {}  # task_hash -> agent_id
        self.task_dependencies: Dict[str, Set[str]] = {}
    
    def register_task(self, name: str, description: str, agent_id: str) -> bool:
        """Register a task implementation"""
        task_hash = self._generate_hash(name, description)
        
        if task_hash in self.registered_tasks:
            existing_agent = self.registered_tasks[task_hash]
            logger.warning(f"Task already implemented by agent {existing_agent}: {name}")
            return False
        
        self.registered_tasks[task_hash] = agent_id
        logger.info(f"Task registered: {name} by agent {agent_id}")
        return True
    
    def is_task_implemented(self, name: str, description: str) -> bool:
        """Check if a task is already implemented"""
        task_hash = self._generate_hash(name, description)
        return task_hash in self.registered_tasks
    
    def get_implementing_agent(self, name: str, description: str) -> str:
        """Get the agent that implemented a task"""
        task_hash = self._generate_hash(name, description)
        return self.registered_tasks.get(task_hash)
    
    def _generate_hash(self, name: str, description: str) -> str:
        """Generate hash for task identification"""
        content = f"{name}:{description}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_dependency(self, task_id: str, dependency_id: str):
        """Add task dependency"""
        if task_id not in self.task_dependencies:
            self.task_dependencies[task_id] = set()
        self.task_dependencies[task_id].add(dependency_id)
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """Get task dependencies"""
        return self.task_dependencies.get(task_id, set())


# Global registry instance
task_registry = SimpleTaskRegistry()
