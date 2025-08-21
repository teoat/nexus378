"""
Dependency Manager - Job Dependency and Execution Order Management

This module implements the DependencyManager class that handles job dependencies,
execution order, and dependency resolution for the Taskmaster system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import networkx as nx

from ..models.job import Job, JobStatus, JobDependency


class DependencyType(Enum):
    """Dependency types."""
    REQUIRED = "required"      # Job must complete before dependent can start
    OPTIONAL = "optional"      # Job completion is preferred but not required
    EXCLUSIVE = "exclusive"    # Jobs cannot run simultaneously
    CONDITIONAL = "conditional"  # Dependency based on condition
    TIMEOUT = "timeout"        # Dependency with timeout


class DependencyStatus(Enum):
    """Dependency status."""
    PENDING = "pending"        # Dependency not yet satisfied
    SATISFIED = "satisfied"    # Dependency is satisfied
    FAILED = "failed"          # Dependency failed
    TIMEOUT = "timeout"        # Dependency timed out
    SKIPPED = "skipped"        # Dependency was skipped


class DependencyResolution(Enum):
    """Dependency resolution strategies."""
    ALL = "all"                # Wait for all dependencies
    ANY = "any"                # Wait for any dependency
    MAJORITY = "majority"      # Wait for majority of dependencies
    CONDITIONAL = "conditional"  # Resolve based on conditions


@dataclass
class DependencyNode:
    """Dependency graph node."""
    
    job_id: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    status: JobStatus = JobStatus.PENDING
    dependency_status: Dict[str, DependencyStatus] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyGraph:
    """Dependency graph representation."""
    
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    
    def add_node(self, job_id: str, dependencies: List[str] = None, dependents: List[str] = None):
        """Add a node to the dependency graph."""
        if job_id not in self.nodes:
            self.nodes[job_id] = DependencyNode(job_id=job_id)
        
        node = self.nodes[job_id]
        if dependencies:
            node.dependencies.extend(dependencies)
        if dependents:
            node.dependents.extend(dependents)
        
        # Add to NetworkX graph
        self.graph.add_node(job_id)
    
    def add_edge(self, from_job: str, to_job: str):
        """Add an edge to the dependency graph."""
        if from_job not in self.nodes:
            self.add_node(from_job)
        if to_job not in self.nodes:
            self.add_node(to_job)
        
        # Add dependency relationship
        self.nodes[from_job].dependents.append(to_job)
        self.nodes[to_job].dependencies.append(from_job)
        
        # Add to NetworkX graph
        self.graph.add_edge(from_job, to_job)
        self.edges.append((from_job, to_job))
    
    def remove_node(self, job_id: str):
        """Remove a node from the dependency graph."""
        if job_id in self.nodes:
            # Remove all edges
            for dep in self.nodes[job_id].dependencies:
                if dep in self.nodes:
                    self.nodes[dep].dependents.remove(job_id)
            
            for dep in self.nodes[job_id].dependents:
                if dep in self.nodes:
                    self.nodes[dep].dependencies.remove(job_id)
            
            # Remove from NetworkX graph
            self.graph.remove_node(job_id)
            
            # Remove node
            del self.nodes[job_id]
    
    def has_cycles(self) -> bool:
        """Check if the dependency graph has cycles."""
        try:
            nx.find_cycle(self.graph)
            return True
        except nx.NetworkXNoCycle:
            return False
    
    def get_topological_order(self) -> List[str]:
        """Get topological ordering of jobs."""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            # Graph has cycles, return empty list
            return []
    
    def get_ready_jobs(self, completed_jobs: Set[str]) -> List[str]:
        """Get jobs that are ready to execute (all dependencies satisfied)."""
        ready_jobs = []
        
        for job_id, node in self.nodes.items():
            if job_id in completed_jobs:
                continue
            
            # Check if all dependencies are satisfied
            if all(dep in completed_jobs for dep in node.dependencies):
                ready_jobs.append(job_id)
        
        return ready_jobs
    
    def get_blocked_jobs(self, completed_jobs: Set[str]) -> List[str]:
        """Get jobs that are blocked by dependencies."""
        blocked_jobs = []
        
        for job_id, node in self.nodes.items():
            if job_id in completed_jobs:
                continue
            
            # Check if any dependencies are not satisfied
            if any(dep not in completed_jobs for dep in node.dependencies):
                blocked_jobs.append(job_id)
        
        return blocked_jobs


class DependencyManager:
    """
    Dependency management engine for the Taskmaster system.
    
    The DependencyManager is responsible for:
    - Managing job dependencies and relationships
    - Resolving dependency conflicts
    - Determining execution order
    - Handling dependency timeouts and failures
    - Optimizing dependency resolution
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the DependencyManager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.default_timeout = timedelta(hours=config.get('default_dependency_timeout_hours', 12))
        self.dependency_check_interval = timedelta(seconds=config.get('dependency_check_interval_seconds', 30))
        self.enable_parallel_dependencies = config.get('enable_parallel_dependencies', True)
        self.max_dependency_depth = config.get('max_dependency_depth', 10)
        
        # Internal state
        self.dependency_graph = DependencyGraph()
        self.job_dependencies: Dict[str, List[JobDependency]] = defaultdict(list)
        self.dependency_status: Dict[str, Dict[str, DependencyStatus]] = defaultdict(dict)
        self.completed_jobs: Set[str] = set()
        self.failed_jobs: Set[str] = set()
        self.blocked_jobs: Set[str] = set()
        
        # Dependency resolution cache
        self.resolution_cache: Dict[str, bool] = {}
        self.resolution_history: List[Dict[str, Any]] = []
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("DependencyManager initialized successfully")
    
    async def start(self):
        """Start the DependencyManager."""
        self.logger.info("Starting DependencyManager...")
        
        # Start background tasks
        asyncio.create_task(self._monitor_dependencies())
        asyncio.create_task(self._cleanup_resolution_cache())
        asyncio.create_task(self._detect_deadlocks())
        
        self.logger.info("DependencyManager started successfully")
    
    async def stop(self):
        """Stop the DependencyManager."""
        self.logger.info("Stopping DependencyManager...")
        self.logger.info("DependencyManager stopped")
    
    async def add_job_dependencies(self, job_id: str, dependencies: List[JobDependency]):
        """Add dependencies for a job."""
        try:
            self.job_dependencies[job_id] = dependencies
            
            # Add to dependency graph
            for dependency in dependencies:
                self.dependency_graph.add_edge(dependency.job_id, job_id)
                
                # Initialize dependency status
                self.dependency_status[job_id][dependency.job_id] = DependencyStatus.PENDING
            
            # Check for cycles
            if self.dependency_graph.has_cycles():
                self.logger.warning(f"Circular dependency detected for job {job_id}")
                # Remove the problematic dependencies
                self.job_dependencies[job_id] = []
                return False
            
            self.logger.info(f"Added {len(dependencies)} dependencies for job {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding dependencies for job {job_id}: {e}")
            return False
    
    async def remove_job_dependencies(self, job_id: str):
        """Remove all dependencies for a job."""
        try:
            if job_id in self.job_dependencies:
                del self.job_dependencies[job_id]
            
            if job_id in self.dependency_status:
                del self.dependency_status[job_id]
            
            # Remove from dependency graph
            self.dependency_graph.remove_node(job_id)
            
            self.logger.info(f"Removed dependencies for job {job_id}")
            
        except Exception as e:
            self.logger.error(f"Error removing dependencies for job {job_id}: {e}")
    
    async def update_job_status(self, job_id: str, status: JobStatus):
        """Update job status and resolve dependencies."""
        try:
            # Update dependency graph
            if job_id in self.dependency_graph.nodes:
                self.dependency_graph.nodes[job_id].status = status
            
            # Handle completed jobs
            if status == JobStatus.COMPLETED:
                self.completed_jobs.add(job_id)
                if job_id in self.blocked_jobs:
                    self.blocked_jobs.remove(job_id)
                
                # Update dependent jobs
                await self._update_dependent_jobs(job_id)
            
            # Handle failed jobs
            elif status == JobStatus.FAILED:
                self.failed_jobs.add(job_id)
                if job_id in self.blocked_jobs:
                    self.blocked_jobs.remove(job_id)
                
                # Handle failed dependencies
                await self._handle_failed_dependency(job_id)
            
            # Handle cancelled jobs
            elif status == JobStatus.CANCELLED:
                if job_id in self.blocked_jobs:
                    self.blocked_jobs.remove(job_id)
                
                # Handle cancelled dependencies
                await self._handle_cancelled_dependency(job_id)
            
            self.logger.info(f"Updated job {job_id} status to {status.value}")
            
        except Exception as e:
            self.logger.error(f"Error updating job status for {job_id}: {e}")
    
    async def can_job_start(self, job_id: str) -> bool:
        """Check if a job can start (all dependencies satisfied)."""
        try:
            if job_id not in self.job_dependencies:
                return True
            
            # Check cache first
            cache_key = f"{job_id}_can_start"
            if cache_key in self.resolution_cache:
                return self.resolution_cache[cache_key]
            
            # Check each dependency
            can_start = True
            for dependency in self.job_dependencies[job_id]:
                if not await self._is_dependency_satisfied(job_id, dependency):
                    can_start = False
                    break
            
            # Cache result
            self.resolution_cache[cache_key] = can_start
            
            return can_start
            
        except Exception as e:
            self.logger.error(f"Error checking if job {job_id} can start: {e}")
            return False
    
    async def get_ready_jobs(self) -> List[str]:
        """Get list of jobs that are ready to execute."""
        try:
            return self.dependency_graph.get_ready_jobs(self.completed_jobs)
        except Exception as e:
            self.logger.error(f"Error getting ready jobs: {e}")
            return []
    
    async def get_blocked_jobs(self) -> List[str]:
        """Get list of jobs that are blocked by dependencies."""
        try:
            return self.dependency_graph.get_blocked_jobs(self.completed_jobs)
        except Exception as e:
            self.logger.error(f"Error getting blocked jobs: {e}")
            return []
    
    async def get_job_dependencies(self, job_id: str) -> List[JobDependency]:
        """Get dependencies for a specific job."""
        return self.job_dependencies.get(job_id, [])
    
    async def get_job_dependents(self, job_id: str) -> List[str]:
        """Get jobs that depend on a specific job."""
        if job_id in self.dependency_graph.nodes:
            return self.dependency_graph.nodes[job_id].dependents
        return []
    
    async def get_execution_order(self) -> List[str]:
        """Get the recommended execution order for jobs."""
        try:
            return self.dependency_graph.get_topological_order()
        except Exception as e:
            self.logger.error(f"Error getting execution order: {e}")
            return []
    
    async def get_dependency_status(self, job_id: str) -> Dict[str, DependencyStatus]:
        """Get dependency status for a specific job."""
        return self.dependency_status.get(job_id, {})
    
    async def force_dependency_resolution(self, job_id: str, dependency_id: str, 
                                       status: DependencyStatus):
        """Force resolve a dependency status."""
        try:
            if job_id in self.dependency_status and dependency_id in self.dependency_status[job_id]:
                self.dependency_status[job_id][dependency_id] = status
                
                # Clear cache
                cache_key = f"{job_id}_can_start"
                if cache_key in self.resolution_cache:
                    del self.resolution_cache[cache_key]
                
                self.logger.info(f"Force resolved dependency {dependency_id} for job {job_id} to {status.value}")
                
        except Exception as e:
            self.logger.error(f"Error force resolving dependency: {e}")
    
    async def _is_dependency_satisfied(self, job_id: str, dependency: JobDependency) -> bool:
        """Check if a specific dependency is satisfied."""
        try:
            # Check if dependency job exists
            if dependency.job_id not in self.dependency_graph.nodes:
                return False
            
            # Check dependency job status
            dep_node = self.dependency_graph.nodes[dependency.job_id]
            
            if dependency.dependency_type == "required":
                return dep_node.status == JobStatus.COMPLETED
            
            elif dependency.dependency_type == "optional":
                return dep_node.status in [JobStatus.COMPLETED, JobStatus.SKIPPED]
            
            elif dependency.dependency_type == "exclusive":
                # Check if any exclusive jobs are running
                for node in self.dependency_graph.nodes.values():
                    if (node.job_id != dependency.job_id and 
                        node.status == JobStatus.RUNNING):
                        return False
                return True
            
            elif dependency.dependency_type == "conditional":
                # Evaluate condition
                if dependency.condition:
                    return await self._evaluate_condition(dependency.condition, job_id)
                return True
            
            elif dependency.dependency_type == "timeout":
                # Check if dependency has timed out
                if dependency.timeout:
                    dep_created = dep_node.metadata.get('created_at', datetime.utcnow())
                    if datetime.utcnow() - dep_created > dependency.timeout:
                        return True
                return dep_node.status == JobStatus.COMPLETED
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking dependency satisfaction: {e}")
            return False
    
    async def _evaluate_condition(self, condition: str, job_id: str) -> bool:
        """Evaluate a dependency condition."""
        try:
            # Simple condition evaluation
            # In a real system, you'd use a more sophisticated expression evaluator
            
            if condition == "always":
                return True
            elif condition == "never":
                return False
            elif condition.startswith("case_status:"):
                case_status = condition.split(":")[1]
                # This would check the actual case status
                return True  # Placeholder
            elif condition.startswith("time_based:"):
                time_condition = condition.split(":")[1]
                # This would evaluate time-based conditions
                return True  # Placeholder
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    async def _update_dependent_jobs(self, completed_job_id: str):
        """Update jobs that depend on a completed job."""
        try:
            dependents = await self.get_job_dependents(completed_job_id)
            
            for dependent_id in dependents:
                # Update dependency status
                if dependent_id in self.dependency_status and completed_job_id in self.dependency_status[dependent_id]:
                    self.dependency_status[dependent_id][completed_job_id] = DependencyStatus.SATISFIED
                
                # Clear cache
                cache_key = f"{dependent_id}_can_start"
                if cache_key in self.resolution_cache:
                    del self.resolution_cache[cache_key]
                
                # Check if dependent can now start
                if await self.can_job_start(dependent_id):
                    if dependent_id in self.blocked_jobs:
                        self.blocked_jobs.remove(dependent_id)
                else:
                    if dependent_id not in self.blocked_jobs:
                        self.blocked_jobs.add(dependent_id)
            
        except Exception as e:
            self.logger.error(f"Error updating dependent jobs: {e}")
    
    async def _handle_failed_dependency(self, failed_job_id: str):
        """Handle a failed dependency."""
        try:
            dependents = await self.get_job_dependents(failed_job_id)
            
            for dependent_id in dependents:
                # Update dependency status
                if dependent_id in self.dependency_status and failed_job_id in self.dependency_status[dependent_id]:
                    self.dependency_status[dependent_id][failed_job_id] = DependencyStatus.FAILED
                
                # Check if dependent should fail or continue
                should_fail = await self._should_fail_on_dependency_failure(dependent_id, failed_job_id)
                
                if should_fail:
                    # Mark dependent as failed
                    if dependent_id in self.dependency_graph.nodes:
                        self.dependency_graph.nodes[dependent_id].status = JobStatus.FAILED
                    self.failed_jobs.add(dependent_id)
                    if dependent_id in self.blocked_jobs:
                        self.blocked_jobs.remove(dependent_id)
                
                # Clear cache
                cache_key = f"{dependent_id}_can_start"
                if cache_key in self.resolution_cache:
                    del self.resolution_cache[cache_key]
            
        except Exception as e:
            self.logger.error(f"Error handling failed dependency: {e}")
    
    async def _handle_cancelled_dependency(self, cancelled_job_id: str):
        """Handle a cancelled dependency."""
        try:
            dependents = await self.get_job_dependents(cancelled_job_id)
            
            for dependent_id in dependents:
                # Update dependency status
                if dependent_id in self.dependency_status and cancelled_job_id in self.dependency_status[dependent_id]:
                    self.dependency_status[dependent_id][cancelled_job_id] = DependencyStatus.SKIPPED
                
                # Clear cache
                cache_key = f"{dependent_id}_can_start"
                if cache_key in self.resolution_cache:
                    del self.resolution_cache[cache_key]
            
        except Exception as e:
            self.logger.error(f"Error handling cancelled dependency: {e}")
    
    async def _should_fail_on_dependency_failure(self, job_id: str, failed_dependency_id: str) -> bool:
        """Determine if a job should fail when a dependency fails."""
        try:
            if job_id not in self.job_dependencies:
                return False
            
            # Check if the failed dependency is required
            for dependency in self.job_dependencies[job_id]:
                if (dependency.job_id == failed_dependency_id and 
                    dependency.dependency_type == "required"):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if job should fail: {e}")
            return True
    
    async def _monitor_dependencies(self):
        """Monitor dependencies for timeouts and failures."""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Check for dependency timeouts
                for job_id, dependencies in self.job_dependencies.items():
                    for dependency in dependencies:
                        if dependency.timeout:
                            # Check if dependency has timed out
                            dep_node = self.dependency_graph.nodes.get(dependency.job_id)
                            if dep_node and dep_node.status == JobStatus.PENDING:
                                dep_created = dep_node.metadata.get('created_at', current_time)
                                if current_time - dep_created > dependency.timeout:
                                    # Mark dependency as timed out
                                    self.dependency_status[job_id][dependency.job_id] = DependencyStatus.TIMEOUT
                                    
                                    # Clear cache
                                    cache_key = f"{job_id}_can_start"
                                    if cache_key in self.resolution_cache:
                                        del self.resolution_cache[cache_key]
                
                await asyncio.sleep(self.dependency_check_interval.total_seconds())
                
            except Exception as e:
                self.logger.error(f"Error monitoring dependencies: {e}")
                await asyncio.sleep(self.dependency_check_interval.total_seconds())
    
    async def _cleanup_resolution_cache(self):
        """Clean up old resolution cache entries."""
        while True:
            try:
                # Clear cache periodically
                self.resolution_cache.clear()
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error cleaning up resolution cache: {e}")
                await asyncio.sleep(300)
    
    async def _detect_deadlocks(self):
        """Detect and handle deadlocks in dependency graph."""
        while True:
            try:
                # Check for cycles in dependency graph
                if self.dependency_graph.has_cycles():
                    self.logger.warning("Deadlock detected in dependency graph")
                    
                    # Try to resolve deadlock by removing problematic dependencies
                    await self._resolve_deadlock()
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error detecting deadlocks: {e}")
                await asyncio.sleep(600)
    
    async def _resolve_deadlock(self):
        """Attempt to resolve a deadlock."""
        try:
            # Find cycles in the graph
            cycles = list(nx.simple_cycles(self.dependency_graph.graph))
            
            if cycles:
                # Remove the shortest cycle to break deadlock
                shortest_cycle = min(cycles, key=len)
                
                for i in range(len(shortest_cycle)):
                    from_job = shortest_cycle[i]
                    to_job = shortest_cycle[(i + 1) % len(shortest_cycle)]
                    
                    # Remove the edge
                    if to_job in self.dependency_graph.nodes[from_job].dependents:
                        self.dependency_graph.nodes[from_job].dependents.remove(to_job)
                    if from_job in self.dependency_graph.nodes[to_job].dependencies:
                        self.dependency_graph.nodes[to_job].dependencies.remove(from_job)
                    
                    # Remove from NetworkX graph
                    if self.dependency_graph.graph.has_edge(from_job, to_job):
                        self.dependency_graph.graph.remove_edge(from_job, to_job)
                    
                    # Remove from edges list
                    if (from_job, to_job) in self.dependency_graph.edges:
                        self.dependency_graph.edges.remove((from_job, to_job))
                
                self.logger.info(f"Resolved deadlock by removing cycle: {shortest_cycle}")
                
        except Exception as e:
            self.logger.error(f"Error resolving deadlock: {e}")
    
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get a summary of dependency status."""
        summary = {
            'total_jobs': len(self.dependency_graph.nodes),
            'completed_jobs': len(self.completed_jobs),
            'failed_jobs': len(self.failed_jobs),
            'blocked_jobs': len(self.blocked_jobs),
            'ready_jobs': len(self.dependency_graph.get_ready_jobs(self.completed_jobs)),
            'total_dependencies': sum(len(deps) for deps in self.job_dependencies.values()),
            'has_cycles': self.dependency_graph.has_cycles(),
            'topological_order': self.dependency_graph.get_topological_order()
        }
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'default_dependency_timeout_hours': 12,
        'dependency_check_interval_seconds': 30,
        'enable_parallel_dependencies': True,
        'max_dependency_depth': 10
    }
    
    # Initialize dependency manager
    manager = DependencyManager(config)
    
    print("DependencyManager system initialized successfully!")
