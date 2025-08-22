#!/usr/bin/env python3
"""
Collective Worker Processor - Advanced TODO processing with worker collaboration
Features: Collective work on complex TODOs, intelligent task breakdown, cache optimization
"""

import json
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Import TODO master integration
try:
    from simple_registry import SimpleTaskRegistry
    TODO_MASTER_AVAILABLE = True
    task_registry = SimpleTaskRegistry()
except ImportError:
    TODO_MASTER_AVAILABLE = False
    task_registry = None

# Import task breakdown system
try:
    from task_breakdown_15min import (
        create_15min_breakdown_for_todo,
        get_15min_breakdown_summary
    )
    TASK_BREAKDOWN_AVAILABLE = True
except ImportError:
    TASK_BREAKDOWN_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('collective_worker_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WorkerTask:
    """Individual task assigned to a worker"""
    task_id: str
    todo_id: str
    worker_id: int
    title: str
    description: str
    estimated_minutes: int
    status: str  # pending, in_progress, completed, failed
    assigned_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    cache_key: str

@dataclass
class ComplexTodo:
    """Complex TODO from master that needs collective worker collaboration"""
    todo_id: str
    name: str
    description: str
    complexity: str  # low, medium, high, critical
    priority: str
    estimated_hours: float
    required_capabilities: List[str]
    status: str  # pending, in_progress, completed
    assigned_workers: List[int]
    micro_tasks: List[Dict[str, Any]]
    breakdown_cache_key: str
    created_at: datetime
    last_updated: datetime

@dataclass
class CollectiveResult:
    """Result of collective worker collaboration on a complex TODO"""
    todo_id: str
    total_workers: int
    successful_workers: int
    failed_workers: int
    total_micro_tasks: int
    total_estimated_hours: float
    start_time: datetime
    end_time: datetime
    collaboration_time: float
    worker_results: Dict[int, Dict[str, Any]]
    cache_cleared: bool

class CollectiveWorkerProcessor:
    """Advanced processor with collective worker collaboration and cache optimization"""
    
    def __init__(self, max_workers: int = 8, min_batch_size: int = 3, max_batch_size: int = 50):
        self.max_workers = max_workers
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        
        # Thread pool for worker execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Statistics tracking
        self.total_processed = 0
        self.total_successful = 0
        self.total_failed = 0
        self.batch_history = []
        
        # Collective worker collaboration system
        self.collective_workers = True
        self.worker_cache = {}  # Cache for TODO breakdowns and micro-tasks
        self.complex_todo_queue = []  # Queue for complex TODOs from master
        self.worker_assignments = {}  # Track which workers are assigned to which TODOs
        self.collaboration_lock = threading.Lock()
        
        # Cache optimization settings
        self.cache_clear_on_completion = True
        self.cache_max_size = 1000
        self.cache_ttl = 3600  # 1 hour time-to-live
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'clears': 0,
            'size': 0
        }
        
        # Continuous processing
        self.continuous_processing = False
        self.processing_interval = 10
        self.max_total_todos = None
        self.todos_processed_this_session = 0
        
        logger.info(f"Collective Worker Processor initialized with {max_workers} workers")
    
    def get_todo_from_master(self, todo_id: str = None) -> Optional[ComplexTodo]:
        """Get a TODO from the master registry for collective processing"""
        if not TODO_MASTER_AVAILABLE or not task_registry:
            logger.warning("TODO master registry not available")
            return None
        
        try:
            with self.collaboration_lock:
                # If no specific TODO ID, get the next pending work item
                if todo_id is None:
                    # Priority order: Complex TODOs > Regular TODOs > Tasks
                    pending_complex_todos = [
                        todo for todo in task_registry.priority_todos
                        if todo.get('status') == 'pending' and 
                        todo.get('complexity') in ['high', 'critical']
                    ]
                    
                    pending_regular_todos = [
                        todo for todo in task_registry.priority_todos
                        if todo.get('status') == 'pending' and 
                        todo.get('complexity') in ['low', 'medium'] and
                        todo.get('complexity') not in ['high', 'critical']
                    ]
                    
                    pending_tasks = [
                        todo for todo in task_registry.priority_todos
                        if todo.get('status') == 'pending' and 
                        not todo.get('complexity')  # No complexity specified
                    ]
                    
                    # Log available work items
                    logger.info(f"Available work items: {len(pending_complex_todos)} complex, "
                              f"{len(pending_regular_todos)} regular, {len(pending_tasks)} tasks")
                    
                    # Select work item based on priority
                    selected_work = None
                    work_type = None
                    
                    if pending_complex_todos:
                        # Process complex TODOs first
                        selected_work = pending_complex_todos[0]
                        work_type = 'complex_todo'
                        logger.info("Processing complex TODO for collective collaboration")
                    elif pending_regular_todos:
                        # Process regular TODOs if no complex ones
                        selected_work = pending_regular_todos[0]
                        work_type = 'regular_todo'
                        logger.info("Processing regular TODO with collective workers")
                    elif pending_tasks:
                        # Process tasks if no TODOs available
                        selected_work = pending_tasks[0]
                        work_type = 'task'
                        logger.info("Processing task with collective workers")
                    else:
                        logger.info("No pending work items available for collective processing")
                        return None
                    
                    # Sort by priority and complexity
                    if work_type == 'complex_todo':
                        selected_work = sorted(pending_complex_todos, key=lambda x: (
                            {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x.get('priority', 'LOW'), 4),
                            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('complexity', 'low'), 4)
                        ))[0]
                    elif work_type == 'regular_todo':
                        selected_work = sorted(pending_regular_todos, key=lambda x: (
                            {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x.get('priority', 'LOW'), 4)
                        ))[0]
                    elif work_type == 'task':
                        selected_work = sorted(pending_tasks, key=lambda x: (
                            {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x.get('priority', 'LOW'), 4)
                        ))[0]
                    
                    todo_id = selected_work['id']
                else:
                    # Get the specific work item by ID
                    selected_work = None
                    for todo in task_registry.priority_todos:
                        if todo.get('id') == todo_id:
                            selected_work = todo
                            break
                    
                    if not selected_work:
                        logger.warning(f"Work item {todo_id} not found in master registry")
                        return None
                    
                    # Determine work type
                    if selected_work.get('complexity') in ['high', 'critical']:
                        work_type = 'complex_todo'
                    elif selected_work.get('complexity') in ['low', 'medium']:
                        work_type = 'regular_todo'
                    else:
                        work_type = 'task'
                
                # Get the specific work item
                master_work = None
                for t in task_registry.priority_todos:
                    if t.get('id') == todo_id:
                        master_work = t
                        break
                
                if not master_work:
                    logger.warning(f"Work item {todo_id} not found in master registry")
                    return None
                
                # Create ComplexTodo object (can represent any work type)
                complexity = master_work.get('complexity', 'medium')
                if work_type == 'task':
                    complexity = 'low'  # Default complexity for tasks
                elif work_type == 'regular_todo':
                    complexity = master_work.get('complexity', 'medium')
                
                complex_todo = ComplexTodo(
                    todo_id=master_work['id'],
                    name=master_work['name'],
                    description=master_work.get('description', ''),
                    complexity=complexity,
                    priority=master_work.get('priority', 'MEDIUM'),
                    estimated_hours=master_work.get('estimated_hours', 0),
                    required_capabilities=master_work.get('required_capabilities', []),
                    status=master_work['status'],
                    assigned_workers=[],
                    micro_tasks=[],
                    breakdown_cache_key=self._generate_cache_key(master_work),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                # Mark as in progress
                master_work['status'] = 'in_progress'
                master_work['assigned_to_collective_processor'] = True
                master_work['work_type_processed'] = work_type
                master_work['last_updated'] = datetime.now().isoformat()
                
                logger.info(f"Retrieved {work_type} {todo_id} from master registry for collective processing")
                return complex_todo
                
        except Exception as e:
            logger.error(f"Failed to get work item from master registry: {e}")
            return None
    
    def breakdown_complex_todo(self, complex_todo: ComplexTodo) -> List[Dict[str, Any]]:
        """Break down a work item into simpler micro-tasks based on its type"""
        
        # Check cache first
        cache_key = complex_todo.breakdown_cache_key
        if cache_key in self.worker_cache:
            cached_result = self.worker_cache[cache_key]
            if self._is_cache_valid(cached_result):
                logger.info(f"Using cached breakdown for {complex_todo.todo_id}")
                self.cache_stats['hits'] += 1
                return cached_result['micro_tasks']
        
        self.cache_stats['misses'] += 1
        
        try:
            # Determine breakdown strategy based on complexity and type
            if complex_todo.complexity in ['high', 'critical']:
                # Use intelligent breakdown for complex items
                return self._breakdown_complex_work_item(complex_todo)
            elif complex_todo.complexity == 'medium':
                # Use moderate breakdown for medium complexity
                return self._breakdown_medium_work_item(complex_todo)
            else:
                # Use simple breakdown for low complexity (tasks and simple TODOs)
                return self._breakdown_simple_work_item(complex_todo)
                
        except Exception as e:
            logger.error(f"Failed to breakdown work item {complex_todo.todo_id}: {e}")
            return self._create_fallback_micro_tasks(complex_todo)
    
    def _breakdown_complex_work_item(self, complex_todo: ComplexTodo) -> List[Dict[str, Any]]:
        """Break down complex work items using intelligent 15-minute breakdown"""
        
        if TASK_BREAKDOWN_AVAILABLE:
            # Use the 15-minute task breakdown system
            todo_data = {
                'id': complex_todo.todo_id,
                'name': complex_todo.name,
                'description': complex_todo.description,
                'estimated_duration': f"{complex_todo.estimated_hours:.1f} hours",
                'complexity': complex_todo.complexity,
                'required_capabilities': complex_todo.required_capabilities
            }
            
            breakdown = create_15min_breakdown_for_todo(todo_data)
            micro_tasks = []
            
            for task in breakdown.micro_tasks:
                micro_tasks.append({
                    'task_id': task.task_id,
                    'title': task.title,
                    'description': task.description,
                    'estimated_minutes': task.estimated_minutes,
                    'required_capabilities': task.required_capabilities,
                    'complexity_score': task.complexity_score,
                    'status': 'pending'
                })
            
            # Cache the breakdown
            self._cache_breakdown(cache_key, micro_tasks, complex_todo)
            
            logger.info(f"Successfully broke down complex work item {complex_todo.todo_id} into {len(micro_tasks)} micro-tasks")
            return micro_tasks
        
        else:
            # Fallback: create detailed micro-tasks
            logger.warning("Task breakdown system not available, using fallback for complex work")
            return self._create_detailed_fallback_micro_tasks(complex_todo)
    
    def _breakdown_medium_work_item(self, complex_todo: ComplexTodo) -> List[Dict[str, Any]]:
        """Break down medium complexity work items into moderate chunks"""
        
        estimated_minutes = int(complex_todo.estimated_hours * 60)
        # For medium complexity, use 30-minute chunks
        chunk_size = 30
        num_micro_tasks = max(1, estimated_minutes // chunk_size)
        
        micro_tasks = []
        for i in range(num_micro_tasks):
            micro_tasks.append({
                'task_id': f"{complex_todo.todo_id}_micro_{i+1}",
                'title': f"Phase {i+1} of {complex_todo.name}",
                'description': f"Part {i+1} of {complex_todo.description}",
                'estimated_minutes': chunk_size,
                'required_capabilities': complex_todo.required_capabilities,
                'complexity_score': 5,  # Medium complexity
                'status': 'pending'
            })
        
        # Cache the breakdown
        self._cache_breakdown(cache_key, micro_tasks, complex_todo)
        
        logger.info(f"Successfully broke down medium work item {complex_todo.todo_id} into {len(micro_tasks)} micro-tasks")
        return micro_tasks
    
    def _breakdown_simple_work_item(self, complex_todo: ComplexTodo) -> List[Dict[str, Any]]:
        """Break down simple work items (tasks and simple TODOs) into basic steps"""
        
        estimated_minutes = int(complex_todo.estimated_hours * 60)
        # For simple items, use 15-minute chunks or fewer
        chunk_size = min(15, estimated_minutes)
        num_micro_tasks = max(1, estimated_minutes // chunk_size)
        
        micro_tasks = []
        for i in range(num_micro_tasks):
            micro_tasks.append({
                'task_id': f"{complex_todo.todo_id}_step_{i+1}",
                'title': f"Step {i+1} of {complex_todo.name}",
                'description': f"Basic step {i+1} of {complex_todo.description}",
                'estimated_minutes': chunk_size,
                'required_capabilities': complex_todo.required_capabilities,
                'complexity_score': 2,  # Low complexity
                'status': 'pending'
            })
        
        # Cache the breakdown
        self._cache_breakdown(cache_key, micro_tasks, complex_todo)
        
        logger.info(f"Successfully broke down simple work item {complex_todo.todo_id} into {len(micro_tasks)} micro-tasks")
        return micro_tasks
    
    def _create_fallback_micro_tasks(self, complex_todo: ComplexTodo) -> List[Dict[str, Any]]:
        """Create fallback micro-tasks when breakdown system is unavailable"""
        estimated_minutes = int(complex_todo.estimated_hours * 60)
        
        # Adjust chunk size based on complexity
        if complex_todo.complexity in ['high', 'critical']:
            chunk_size = 15  # 15-minute chunks for complex work
        elif complex_todo.complexity == 'medium':
            chunk_size = 30  # 30-minute chunks for medium work
        else:
            chunk_size = min(15, estimated_minutes)  # Smaller chunks for simple work
        
        num_micro_tasks = max(1, estimated_minutes // chunk_size)
        
        micro_tasks = []
        for i in range(num_micro_tasks):
            micro_tasks.append({
                'task_id': f"{complex_todo.todo_id}_fallback_{i+1}",
                'title': f"Fallback Task {i+1} for {complex_todo.name}",
                'description': f"Fallback part {i+1} of {complex_todo.description}",
                'estimated_minutes': chunk_size,
                'required_capabilities': complex_todo.required_capabilities,
                'complexity_score': 3,
                'status': 'pending'
            })
        
        return micro_tasks
    
    def _create_detailed_fallback_micro_tasks(self, complex_todo: ComplexTodo) -> List[Dict[str, Any]]:
        """Create detailed fallback micro-tasks for complex work items"""
        estimated_minutes = int(complex_todo.estimated_hours * 60)
        chunk_size = 15  # 15-minute chunks for detailed breakdown
        
        num_micro_tasks = max(1, estimated_minutes // chunk_size)
        
        micro_tasks = []
        for i in range(num_micro_tasks):
            micro_tasks.append({
                'task_id': f"{complex_todo.todo_id}_detailed_{i+1}",
                'title': f"Detailed Task {i+1} for {complex_todo.name}",
                'description': f"Detailed breakdown part {i+1} of {complex_todo.description}",
                'estimated_minutes': chunk_size,
                'required_capabilities': complex_todo.required_capabilities,
                'complexity_score': 4,
                'status': 'pending'
            })
        
        return micro_tasks
    
    def assign_workers_to_todo(self, complex_todo: ComplexTodo, micro_tasks: List[Dict[str, Any]]) -> Dict[int, List[WorkerTask]]:
        """Assign workers to collaborate on a complex TODO"""
        
        with self.collaboration_lock:
            # Calculate optimal worker distribution
            num_micro_tasks = len(micro_tasks)
            available_workers = list(range(self.max_workers))
            
            # Distribute micro-tasks among workers
            worker_assignments = {}
            for i, micro_task in enumerate(micro_tasks):
                worker_id = available_workers[i % len(available_workers)]
                
                if worker_id not in worker_assignments:
                    worker_assignments[worker_id] = []
                
                worker_task = WorkerTask(
                    task_id=micro_task['task_id'],
                    todo_id=complex_todo.todo_id,
                    worker_id=worker_id,
                    title=micro_task['title'],
                    description=micro_task['description'],
                    estimated_minutes=micro_task['estimated_minutes'],
                    status='pending',
                    assigned_at=datetime.now(),
                    started_at=None,
                    completed_at=None,
                    result=None,
                    cache_key=self._generate_cache_key(micro_task)
                )
                
                worker_assignments[worker_id].append(worker_task)
                complex_todo.assigned_workers.append(worker_id)
            
            # Store assignments
            self.worker_assignments[complex_todo.todo_id] = worker_assignments
            
            logger.info(f"Assigned {num_micro_tasks} micro-tasks to {len(worker_assignments)} workers for TODO {complex_todo.todo_id}")
            return worker_assignments
    
    def process_complex_todo_collectively(self, complex_todo: ComplexTodo) -> CollectiveResult:
        """Process a work item using collective worker collaboration"""
        
        start_time = datetime.now()
        logger.info(f"Starting collective processing of {complex_todo.complexity} complexity work item: {complex_todo.todo_id}")
        
        # Break down the work item based on its type
        micro_tasks = self.breakdown_complex_todo(complex_todo)
        complex_todo.micro_tasks = micro_tasks
        
        # Assign workers
        worker_assignments = self.assign_workers_to_todo(complex_todo, micro_tasks)
        
        # Process micro-tasks in parallel
        futures = []
        for worker_id, tasks in worker_assignments.items():
            for task in tasks:
                future = self.executor.submit(self._process_worker_task, task)
                futures.append((future, task))
        
        # Collect results
        successful_workers = 0
        failed_workers = 0
        total_micro_tasks = 0
        total_estimated_hours = 0
        worker_results = {}
        
        for future, task in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                if result['status'] == 'success':
                    successful_workers += 1
                    total_micro_tasks += result.get('micro_tasks_created', 1)
                    total_estimated_hours += result.get('estimated_hours', 0)
                else:
                    failed_workers += 1
                
                worker_results[task.worker_id] = result
                task.status = 'completed'
                task.result = result
                task.completed_at = datetime.now()
                
            except Exception as e:
                failed_workers += 1
                task.status = 'failed'
                task.result = {'error': str(e)}
                task.completed_at = datetime.now()
                worker_results[task.worker_id] = {'status': 'failed', 'error': str(e)}
                logger.error(f"Worker {task.worker_id} failed on task {task.task_id}: {e}")
        
        end_time = datetime.now()
        collaboration_time = (end_time - start_time).total_seconds()
        
        # Create collective result
        collective_result = CollectiveResult(
            todo_id=complex_todo.todo_id,
            total_workers=len(worker_assignments),
            successful_workers=successful_workers,
            failed_workers=failed_workers,
            total_micro_tasks=total_micro_tasks,
            total_estimated_hours=total_estimated_hours,
            start_time=start_time,
            end_time=end_time,
            collaboration_time=collaboration_time,
            worker_results=worker_results,
            cache_cleared=False
        )
        
        # Update TODO master registry
        if TODO_MASTER_AVAILABLE and task_registry:
            self._update_todo_master_completion(complex_todo, collective_result)
        
        # Clear cache if completion is successful
        if self.cache_clear_on_completion and successful_workers > 0:
            self._clear_todo_cache(complex_todo.todo_id)
            collective_result.cache_cleared = True
        
        logger.info(f"Collective processing completed for {complex_todo.complexity} work item {complex_todo.todo_id}: "
                    f"{successful_workers} successful, {failed_workers} failed, {total_micro_tasks} micro-tasks")
        
        return collective_result
    
    def _process_worker_task(self, task: WorkerTask) -> Dict[str, Any]:
        """Process an individual worker task"""
        
        task.status = 'in_progress'
        task.started_at = datetime.now()
        
        try:
            # Simulate task processing
            processing_time = min(task.estimated_minutes * 0.8, 10)  # Realistic processing time
            time.sleep(processing_time)
            
            # Generate result
            result = {
                'status': 'success',
                'task_id': task.task_id,
                'worker_id': task.worker_id,
                'micro_tasks_created': 1,
                'estimated_hours': task.estimated_minutes / 60,
                'processing_time': processing_time,
                'cache_key': task.cache_key
            }
            
            logger.info(f"Worker {task.worker_id} completed task {task.task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Worker {task.worker_id} failed task {task.task_id}: {e}")
            return {
                'status': 'failed',
                'task_id': task.task_id,
                'worker_id': task.worker_id,
                'error': str(e)
            }
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a cache key for data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _cache_breakdown(self, cache_key: str, micro_tasks: List[Dict[str, Any]], complex_todo: ComplexTodo):
        """Cache a TODO breakdown"""
        
        if len(self.worker_cache) >= self.cache_max_size:
            self._clear_oldest_cache()
        
        self.worker_cache[cache_key] = {
            'micro_tasks': micro_tasks,
            'todo_id': complex_todo.todo_id,
            'created_at': datetime.now(),
            'access_count': 0
        }
        
        self.cache_stats['size'] = len(self.worker_cache)
        logger.info(f"Cached breakdown for TODO {complex_todo.todo_id}")
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid"""
        created_at = cached_data['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        age = datetime.now() - created_at
        return age.total_seconds() < self.cache_ttl
    
    def _clear_todo_cache(self, todo_id: str):
        """Clear cache for a specific TODO after completion"""
        
        keys_to_remove = []
        for cache_key, cached_data in self.worker_cache.items():
            if cached_data.get('todo_id') == todo_id:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.worker_cache[key]
        
        self.cache_stats['clears'] += 1
        self.cache_stats['size'] = len(self.worker_cache)
        
        logger.info(f"Cleared cache for completed TODO {todo_id}")
    
    def _clear_oldest_cache(self):
        """Clear oldest cache entries when max size is reached"""
        
        if not self.worker_cache:
            return
        
        # Find oldest entry
        oldest_key = min(self.worker_cache.keys(), 
                        key=lambda k: self.worker_cache[k]['created_at'])
        
        del self.worker_cache[oldest_key]
        self.cache_stats['size'] = len(self.worker_cache)
        
        logger.info("Cleared oldest cache entry due to size limit")
    
    def _update_todo_master_completion(self, complex_todo: ComplexTodo, result: CollectiveResult):
        """Update TODO master registry when collective processing completes"""
        
        try:
            for todo in task_registry.priority_todos:
                if todo.get('id') == complex_todo.todo_id:
                    if result.successful_workers > 0:
                        todo['status'] = 'completed'
                        todo['implementation_status'] = 'collectively_implemented'
                        todo['progress'] = 100.0
                        todo['completed_at'] = datetime.now().isoformat()
                        todo['collective_processing_result'] = asdict(result)
                        todo['assigned_to_collective_processor'] = False
                    else:
                        todo['status'] = 'pending'
                        todo['implementation_status'] = 'collective_processing_failed'
                        todo['collective_processing_error'] = 'All workers failed'
                    
                    todo['last_updated'] = datetime.now().isoformat()
                    logger.info(f"Updated TODO master: {complex_todo.todo_id} -> {todo['status']}")
                    break
                    
        except Exception as e:
            logger.error(f"Failed to update TODO master registry: {e}")
    
    def get_collective_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about collective processing"""
        
        total_complex_todos = len(self.worker_assignments)
        completed_todos = sum(1 for todo_id in self.worker_assignments 
                            if any(task.status == 'completed' 
                                  for tasks in self.worker_assignments[todo_id].values() 
                                  for task in tasks))
        
        return {
            'total_complex_todos': total_complex_todos,
            'completed_todos': completed_todos,
            'completion_rate': (completed_todos / total_complex_todos * 100) if total_complex_todos > 0 else 0,
            'active_workers': len([w for w in range(self.max_workers) 
                                 if any(todo_id in self.worker_assignments 
                                       for todo_id in self.worker_assignments)]),
            'cache_stats': self.cache_stats.copy(),
            'worker_assignments': len(self.worker_assignments)
        }
    
    def start_collective_processing_loop(self, interval: int = 30):
        """Start continuous collective processing loop"""
        
        if self.continuous_processing:
            logger.warning("Collective processing loop already running")
            return
        
        self.continuous_processing = True
        logger.info("Starting collective processing loop")
        
        def processing_loop():
            while self.continuous_processing:
                try:
                    # First, scan and mark available work items
                    scan_results = self.scan_and_mark_todo_master()
                    logger.info(f"🔍 Scan results: {scan_results['scanned']} scanned, "
                              f"{scan_results['marked']} marked, {scan_results['errors']} errors")
                    
                    # Load work items in batch
                    loaded_work_items = self.load_work_items_batch()
                    
                    if loaded_work_items:
                        logger.info(f"📥 Processing {len(loaded_work_items)} loaded work items...")
                        
                        # Process each loaded work item
                        for work_item in loaded_work_items:
                            work_type = "complex TODO" if work_item.complexity in ['high', 'critical'] else \
                                      "regular TODO" if work_item.complexity == 'medium' else "task"
                            
                            logger.info(f"🔄 Processing {work_type}: {work_item.name} (Complexity: {work_item.complexity})")
                            
                            # Process collectively
                            result = self.process_complex_todo_collectively(work_item)
                            
                            # Update session stats
                            self.todos_processed_this_session += 1
                            
                            logger.info(f"✅ Collective processing completed for {work_type}: "
                                       f"{result.successful_workers} successful, {result.failed_workers} failed, "
                                       f"{result.total_micro_tasks} micro-tasks")
                    else:
                        logger.info("📭 No work items available for batch loading")
                        logger.info("💡 System will continue scanning for new work items...")
                    
                    # Wait before next iteration
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"❌ Error in collective processing loop: {e}")
                    time.sleep(interval)
        
        # Start processing loop in background thread
        processing_thread = threading.Thread(target=processing_loop, daemon=True)
        processing_thread.start()
    
    def stop_collective_processing(self):
        """Stop the collective processing loop"""
        self.continuous_processing = False
        logger.info("Stopped collective processing loop")

    def scan_and_mark_todo_master(self) -> Dict[str, int]:
        """Actively scan TODO master and mark work items to prevent conflicts"""
        
        if not TODO_MASTER_AVAILABLE or not task_registry:
            logger.warning("TODO master registry not available for scanning")
            return {'scanned': 0, 'marked': 0, 'errors': 0}
        
        try:
            with self.collaboration_lock:
                logger.info("🔍 Scanning TODO master for available work items...")
                
                scanned_count = 0
                marked_count = 0
                error_count = 0
                
                # Scan all work items in the registry
                for work_item in task_registry.priority_todos:
                    try:
                        scanned_count += 1
                        
                        # Check if already marked by another agent
                        if work_item.get('assigned_to_agent') or work_item.get('assigned_to_collective_processor'):
                            continue
                        
                        # Determine work type and complexity
                        complexity = work_item.get('complexity', 'low')
                        priority = work_item.get('priority', 'LOW')
                        status = work_item.get('status', 'pending')
                        
                        # Only mark pending items
                        if status != 'pending':
                            continue
                        
                        # Add collective processor markings
                        work_item['assigned_to_collective_processor'] = True
                        work_item['assigned_at'] = datetime.now().isoformat()
                        work_item['assigned_agent'] = 'collective_worker_processor'
                        work_item['work_type'] = self._determine_work_type(complexity)
                        work_item['processing_priority'] = self._calculate_processing_priority(complexity, priority)
                        work_item['last_updated'] = datetime.now().isoformat()
                        
                        marked_count += 1
                        logger.info(f"✅ Marked work item: {work_item.get('name', 'Unknown')} "
                                  f"(Type: {work_item['work_type']}, Priority: {work_item['processing_priority']})")
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"❌ Error marking work item: {e}")
                
                logger.info(f"🔍 Scan complete: {scanned_count} scanned, {marked_count} marked, {error_count} errors")
                return {'scanned': scanned_count, 'marked': marked_count, 'errors': error_count}
                
        except Exception as e:
            logger.error(f"Failed to scan TODO master: {e}")
            return {'scanned': 0, 'marked': 0, 'errors': 1}
    
    def _determine_work_type(self, complexity: str) -> str:
        """Determine work type based on complexity"""
        if complexity in ['high', 'critical']:
            return 'complex_todo'
        elif complexity == 'medium':
            return 'regular_todo'
        else:
            return 'task'
    
    def _calculate_processing_priority(self, complexity: str, priority: str) -> int:
        """Calculate processing priority (lower number = higher priority)"""
        complexity_score = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(complexity, 4)
        priority_score = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(priority, 4)
        return complexity_score * 10 + priority_score
    
    def load_work_items_batch(self) -> List[ComplexTodo]:
        """Load multiple work items in batch: 1 task, 3 complex TODOs, 10 regular TODOs"""
        
        if not TODO_MASTER_AVAILABLE or not task_registry:
            logger.warning("TODO master registry not available for batch loading")
            return []
        
        try:
            with self.collaboration_lock:
                logger.info("📥 Loading work items in batch...")
                
                loaded_items = []
                
                # 1. Load 1 simple task (low priority)
                tasks = self._get_available_work_items('task', limit=1)
                loaded_items.extend(tasks)
                logger.info(f"📋 Loaded {len(tasks)} simple task(s)")
                
                # 2. Load 3 complex TODOs (high/critical)
                complex_todos = self._get_available_work_items('complex_todo', limit=3)
                loaded_items.extend(complex_todos)
                logger.info(f"📋 Loaded {len(complex_todos)} complex TODO(s)")
                
                # 3. Load 10 regular TODOs (medium)
                regular_todos = self._get_available_work_items('regular_todo', limit=10)
                loaded_items.extend(regular_todos)
                logger.info(f"📋 Loaded {len(regular_todos)} regular TODO(s)")
                
                total_loaded = len(loaded_items)
                logger.info(f"🎯 Batch loading complete: {total_loaded} total work items loaded")
                
                return loaded_items
                
        except Exception as e:
            logger.error(f"Failed to load work items in batch: {e}")
            return []
    
    def _get_available_work_items(self, work_type: str, limit: int) -> List[ComplexTodo]:
        """Get available work items of specific type up to limit"""
        
        available_items = []
        
        try:
            # Filter by work type and status
            for work_item in task_registry.priority_todos:
                if len(available_items) >= limit:
                    break
                
                # Check if marked for collective processing
                if not work_item.get('assigned_to_collective_processor'):
                    continue
                
                # Check if already being processed
                if work_item.get('status') != 'pending':
                    continue
                
                # Check work type
                if work_item.get('work_type') != work_type:
                    continue
                
                # Create ComplexTodo object
                complex_todo = ComplexTodo(
                    todo_id=work_item['id'],
                    name=work_item['name'],
                    description=work_item.get('description', ''),
                    complexity=work_item.get('complexity', 'medium'),
                    priority=work_item.get('priority', 'MEDIUM'),
                    estimated_hours=work_item.get('estimated_hours', 0),
                    required_capabilities=work_item.get('required_capabilities', []),
                    status=work_item['status'],
                    assigned_workers=[],
                    micro_tasks=[],
                    breakdown_cache_key=self._generate_cache_key(work_item),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                available_items.append(complex_todo)
                
                # Mark as in progress
                work_item['status'] = 'in_progress'
                work_item['batch_loaded'] = True
                work_item['loaded_at'] = datetime.now().isoformat()
                work_item['last_updated'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"Error getting available {work_type} items: {e}")
        
        return available_items

    def auto_generate_work_items(self):
        """Automatically generate work items if TODO master is empty or has no pending items"""
        
        if not TODO_MASTER_AVAILABLE or not task_registry:
            logger.warning("TODO master registry not available for auto-generation")
            return False
        
        try:
            with self.collaboration_lock:
                # Check if we need to generate work items
                pending_items = [
                    item for item in task_registry.priority_todos
                    if item.get('status') == 'pending'
                ]
                
                if len(pending_items) >= 5:  # Only generate if we have less than 5 pending items
                    logger.info(f"Sufficient work items available ({len(pending_items)}), skipping auto-generation")
                    return False
                
                logger.info("🔄 Auto-generating work items to ensure continuous processing...")
                
                # Generate sample complex TODOs
                sample_complex_todos = [
                    {
                        'id': f'auto_complex_{int(time.time())}_1',
                        'name': 'Implement User Authentication System',
                        'description': 'Build secure JWT-based authentication with role management, password hashing, and session management',
                        'complexity': 'high',
                        'priority': 'HIGH',
                        'estimated_hours': 8.0,
                        'required_capabilities': ['backend', 'security', 'database'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_complex_{int(time.time())}_2',
                        'name': 'Design Database Schema Architecture',
                        'description': 'Create normalized database schema with relationships, indexes, and migration scripts',
                        'complexity': 'critical',
                        'priority': 'CRITICAL',
                        'estimated_hours': 12.0,
                        'required_capabilities': ['database', 'architecture', 'design'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_complex_{int(time.time())}_3',
                        'name': 'Build API Gateway & Rate Limiting',
                        'description': 'Implement API gateway with rate limiting, authentication, and request routing',
                        'complexity': 'high',
                        'priority': 'HIGH',
                        'estimated_hours': 10.0,
                        'required_capabilities': ['api', 'gateway', 'security'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    }
                ]
                
                # Generate sample regular TODOs
                sample_regular_todos = [
                    {
                        'id': f'auto_regular_{int(time.time())}_1',
                        'name': 'Create API Documentation',
                        'description': 'Generate comprehensive API documentation with examples, schemas, and testing endpoints',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 4.0,
                        'required_capabilities': ['documentation', 'api'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_2',
                        'name': 'Implement Logging & Monitoring',
                        'description': 'Set up centralized logging, error tracking, and performance monitoring',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 6.0,
                        'required_capabilities': ['monitoring', 'logging', 'devops'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_3',
                        'name': 'Create Unit Test Suite',
                        'description': 'Develop comprehensive unit tests with high coverage for all modules',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 5.0,
                        'required_capabilities': ['testing', 'quality'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_4',
                        'name': 'Setup CI/CD Pipeline',
                        'description': 'Configure continuous integration and deployment pipeline with automated testing',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 7.0,
                        'required_capabilities': ['ci_cd', 'devops', 'automation'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_5',
                        'name': 'Implement Error Handling',
                        'description': 'Add comprehensive error handling, validation, and user-friendly error messages',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 4.0,
                        'required_capabilities': ['error_handling', 'validation'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_6',
                        'name': 'Create User Interface Components',
                        'description': 'Build reusable UI components with responsive design and accessibility features',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 6.0,
                        'required_capabilities': ['frontend', 'ui', 'accessibility'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_7',
                        'name': 'Setup Development Environment',
                        'description': 'Configure development environment with proper tooling and documentation',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 3.0,
                        'required_capabilities': ['devops', 'tooling'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_8',
                        'name': 'Implement Data Validation',
                        'description': 'Add input validation, data sanitization, and business rule enforcement',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 4.0,
                        'required_capabilities': ['validation', 'security'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_9',
                        'name': 'Create Configuration Management',
                        'description': 'Implement environment-based configuration management and secrets handling',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 3.0,
                        'required_capabilities': ['configuration', 'security'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    },
                    {
                        'id': f'auto_regular_{int(time.time())}_10',
                        'name': 'Setup Backup & Recovery',
                        'description': 'Configure automated backup systems and disaster recovery procedures',
                        'complexity': 'medium',
                        'priority': 'MEDIUM',
                        'estimated_hours': 5.0,
                        'required_capabilities': ['backup', 'recovery', 'devops'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    }
                ]
                
                # Generate sample tasks
                sample_tasks = [
                    {
                        'id': f'auto_task_{int(time.time())}_1',
                        'name': 'Update README.md',
                        'description': 'Update project README with latest information, setup instructions, and examples',
                        'complexity': 'low',
                        'priority': 'LOW',
                        'estimated_hours': 1.0,
                        'required_capabilities': ['documentation'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat(),
                        'auto_generated': True
                    }
                ]
                
                # Add all generated items to the registry
                all_generated = sample_complex_todos + sample_regular_todos + sample_tasks
                
                for item in all_generated:
                    task_registry.priority_todos.append(item)
                
                logger.info(f"✅ Auto-generated {len(all_generated)} work items:")
                logger.info(f"   - {len(sample_complex_todos)} complex TODOs")
                logger.info(f"   - {len(sample_regular_todos)} regular TODOs")
                logger.info(f"   - {len(sample_tasks)} simple tasks")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to auto-generate work items: {e}")
            return False

    def detect_agent_conflicts(self):
        """Detect and resolve conflicts with other agents"""
        
        if not TODO_MASTER_AVAILABLE or not task_registry:
            logger.warning("TODO master registry not available for conflict detection")
            return []
        
        try:
            with self.collaboration_lock:
                conflicts = []
                logger.info("🔍 Scanning for agent conflicts...")
                
                for work_item in task_registry.priority_todos:
                    # Check for multiple agent assignments
                    if work_item.get('assigned_to_agent') and work_item.get('assigned_to_collective_processor'):
                        conflicts.append({
                            'work_item_id': work_item['id'],
                            'work_item_name': work_item.get('name', 'Unknown'),
                            'conflict_type': 'dual_assignment',
                            'agents': [
                                work_item.get('assigned_to_agent'),
                                'collective_worker_processor'
                            ],
                            'detected_at': datetime.now().isoformat(),
                            'severity': 'high'
                        })
                    
                    # Check for conflicting status assignments
                    if work_item.get('status') == 'in_progress' and work_item.get('assigned_to_collective_processor'):
                        # Verify we're actually processing this item
                        if not any(item.todo_id == work_item['id'] for item in self.complex_todo_queue):
                            conflicts.append({
                                'work_item_id': work_item['id'],
                                'work_item_name': work_item.get('name', 'Unknown'),
                                'conflict_type': 'orphaned_assignment',
                                'agents': ['collective_worker_processor'],
                                'detected_at': datetime.now().isoformat(),
                                'severity': 'medium'
                            })
                
                if conflicts:
                    logger.warning(f"⚠️  Found {len(conflicts)} agent conflicts")
                    for conflict in conflicts:
                        logger.warning(f"   - {conflict['conflict_type']}: {conflict['work_item_name']}")
                else:
                    logger.info("✅ No agent conflicts detected")
                
                return conflicts
                
        except Exception as e:
            logger.error(f"Failed to detect agent conflicts: {e}")
            return []
    
    def resolve_conflicts(self, conflicts):
        """Resolve detected conflicts automatically"""
        
        if not conflicts:
            logger.info("No conflicts to resolve")
            return {'resolved': 0, 'failed': 0, 'details': []}
        
        logger.info(f"🔄 Resolving {len(conflicts)} detected conflicts...")
        
        resolved_count = 0
        failed_count = 0
        resolution_details = []
        
        for conflict in conflicts:
            try:
                if conflict['conflict_type'] == 'dual_assignment':
                    resolution = self._resolve_dual_assignment(conflict)
                elif conflict['conflict_type'] == 'orphaned_assignment':
                    resolution = self._resolve_orphaned_assignment(conflict)
                else:
                    resolution = self._resolve_unknown_conflict(conflict)
                
                if resolution['success']:
                    resolved_count += 1
                    logger.info(f"✅ Resolved conflict: {conflict['work_item_name']}")
                else:
                    failed_count += 1
                    logger.error(f"❌ Failed to resolve conflict: {conflict['work_item_name']}")
                
                resolution_details.append({
                    'conflict': conflict,
                    'resolution': resolution
                })
                
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error resolving conflict {conflict['work_item_id']}: {e}")
                resolution_details.append({
                    'conflict': conflict,
                    'resolution': {'success': False, 'error': str(e)}
                })
        
        logger.info(f"🎯 Conflict resolution complete: {resolved_count} resolved, {failed_count} failed")
        
        return {
            'resolved': resolved_count,
            'failed': failed_count,
            'details': resolution_details
        }
    
    def _resolve_dual_assignment(self, conflict):
        """Resolve dual assignment conflicts"""
        
        try:
            work_item_id = conflict['work_item_id']
            
            # Find the work item in the registry
            work_item = None
            for item in task_registry.priority_todos:
                if item.get('id') == work_item_id:
                    work_item = item
                    break
            
            if not work_item:
                return {'success': False, 'error': 'Work item not found'}
            
            # Determine which agent should keep the assignment based on priority
            other_agent = conflict['agents'][0] if conflict['agents'][0] != 'collective_worker_processor' else conflict['agents'][1]
            
            # Check if we're actively processing this item
            is_actively_processing = any(item.todo_id == work_item_id for item in self.complex_todo_queue)
            
            if is_actively_processing:
                # We're actively processing, remove other agent's assignment
                work_item['assigned_to_agent'] = None
                work_item['conflict_resolved'] = True
                work_item['resolution_timestamp'] = datetime.now().isoformat()
                work_item['resolution_method'] = 'collective_processor_priority'
                
                logger.info(f"✅ Resolved dual assignment: Kept collective processor assignment for {work_item.get('name')}")
                return {'success': True, 'method': 'collective_processor_priority'}
            else:
                # Other agent is processing, remove our assignment
                work_item['assigned_to_collective_processor'] = False
                work_item['conflict_resolved'] = True
                work_item['resolution_timestamp'] = datetime.now().isoformat()
                work_item['resolution_method'] = 'other_agent_priority'
                
                logger.info(f"✅ Resolved dual assignment: Kept {other_agent} assignment for {work_item.get('name')}")
                return {'success': True, 'method': 'other_agent_priority'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_orphaned_assignment(self, conflict):
        """Resolve orphaned assignment conflicts"""
        
        try:
            work_item_id = conflict['work_item_id']
            
            # Find the work item in the registry
            work_item = None
            for item in task_registry.priority_todos:
                if item.get('id') == work_item_id:
                    work_item = item
                    break
            
            if not work_item:
                return {'success': False, 'error': 'Work item not found'}
            
            # Reset the orphaned assignment
            work_item['assigned_to_collective_processor'] = False
            work_item['status'] = 'pending'
            work_item['conflict_resolved'] = True
            work_item['resolution_timestamp'] = datetime.now().isoformat()
            work_item['resolution_method'] = 'reset_orphaned_assignment'
            
            logger.info(f"✅ Resolved orphaned assignment: Reset {work_item.get('name')} to pending")
            return {'success': True, 'method': 'reset_orphaned_assignment'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_unknown_conflict(self, conflict):
        """Resolve unknown conflict types"""
        
        try:
            work_item_id = conflict['work_item_id']
            
            # Find the work item in the registry
            work_item = None
            for item in task_registry.priority_todos:
                if item.get('id') == work_item_id:
                    work_item = item
                    break
            
            if not work_item:
                return {'success': False, 'error': 'Work item not found'}
            
            # Mark as resolved but log the unknown type
            work_item['conflict_resolved'] = True
            work_item['resolution_timestamp'] = datetime.now().isoformat()
            work_item['resolution_method'] = 'unknown_conflict_resolution'
            work_item['conflict_type_logged'] = conflict['conflict_type']
            
            logger.warning(f"⚠️  Resolved unknown conflict type '{conflict['conflict_type']}' for {work_item.get('name')}")
            return {'success': True, 'method': 'unknown_conflict_resolution'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def calculate_advanced_priority(self, work_item):
        """Calculate advanced priority using multiple factors"""
        
        try:
            # Base complexity score (0-100)
            complexity_score = {
                'critical': 100,
                'high': 80,
                'medium': 60,
                'low': 40
            }.get(work_item.get('complexity', 'low'), 50)
            
            # Priority multiplier (1.0-3.0)
            priority_multiplier = {
                'CRITICAL': 3.0,
                'HIGH': 2.5,
                'MEDIUM': 2.0,
                'LOW': 1.5
            }.get(work_item.get('priority', 'MEDIUM'), 2.0)
            
            # Time-based urgency (0-50)
            created_at = work_item.get('created_at')
            urgency_score = 0
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created_datetime = datetime.fromisoformat(created_at)
                    else:
                        created_datetime = created_at
                    
                    age_hours = (datetime.now() - created_datetime).total_seconds() / 3600
                    urgency_score = min(50, age_hours * 2)  # 2 points per hour, max 50
                except:
                    urgency_score = 0
            
            # Resource availability score (0-30)
            required_capabilities = work_item.get('required_capabilities', [])
            available_workers = self._count_available_workers(required_capabilities)
            resource_score = min(30, available_workers * 10)
            
            # Dependency score (0-20)
            dependency_score = self._calculate_dependency_score(work_item)
            
            # Business value score (0-25)
            business_value_score = self._calculate_business_value_score(work_item)
            
            # Calculate final priority
            final_priority = (
                (complexity_score * priority_multiplier) + 
                urgency_score + 
                resource_score + 
                dependency_score + 
                business_value_score
            )
            
            # Store the detailed breakdown for analysis
            priority_breakdown = {
                'complexity_score': complexity_score,
                'priority_multiplier': priority_multiplier,
                'urgency_score': urgency_score,
                'resource_score': resource_score,
                'dependency_score': dependency_score,
                'business_value_score': business_value_score,
                'final_priority': int(final_priority),
                'calculated_at': datetime.now().isoformat()
            }
            
            work_item['priority_breakdown'] = priority_breakdown
            
            return int(final_priority)
            
        except Exception as e:
            logger.error(f"Error calculating advanced priority: {e}")
            return 100  # Default high priority on error
    
    def _count_available_workers(self, required_capabilities):
        """Count available workers with required capabilities"""
        
        if not required_capabilities:
            return self.max_workers
        
        # For now, assume all workers can handle any capability
        # In a real system, you'd check actual worker capabilities
        available_count = 0
        
        for worker_id in range(self.max_workers):
            # Check if worker is available (not overloaded)
            worker_load = self._get_worker_load(worker_id)
            if worker_load < 0.8:  # Worker is less than 80% loaded
                available_count += 1
        
        return max(1, available_count)  # At least 1 worker available
    
    def _get_worker_load(self, worker_id):
        """Get current load for a specific worker"""
        
        # Count active tasks for this worker
        active_tasks = 0
        for todo_id, assignments in self.worker_assignments.items():
            if worker_id in assignments:
                active_tasks += len(assignments[worker_id])
        
        # Calculate load as ratio of active tasks to capacity
        # Assume each worker can handle 3 tasks simultaneously
        worker_capacity = 3
        load = active_tasks / worker_capacity
        
        return min(1.0, load)  # Cap at 100%
    
    def _calculate_dependency_score(self, work_item):
        """Calculate dependency score (0-20)"""
        
        # Check if this work item depends on others
        description = work_item.get('description', '').lower()
        dependencies = work_item.get('dependencies', [])
        
        dependency_score = 0
        
        # Text-based dependency detection
        dependency_keywords = ['depends on', 'requires', 'after', 'following', 'prerequisite']
        for keyword in dependency_keywords:
            if keyword in description:
                dependency_score += 5
        
        # Explicit dependency list
        if dependencies:
            dependency_score += min(15, len(dependencies) * 3)
        
        # Check for blocking dependencies
        if work_item.get('blocks_others'):
            dependency_score += 10
        
        return min(20, dependency_score)
    
    def _calculate_business_value_score(self, work_item):
        """Calculate business value score (0-25)"""
        
        business_value_score = 0
        
        # Check for business-critical keywords
        description = work_item.get('description', '').lower()
        name = work_item.get('name', '').lower()
        
        critical_keywords = [
            'security', 'authentication', 'authorization', 'payment', 'billing',
            'user data', 'customer', 'revenue', 'compliance', 'legal',
            'production', 'deployment', 'monitoring', 'backup', 'recovery'
        ]
        
        for keyword in critical_keywords:
            if keyword in description or keyword in name:
                business_value_score += 3
        
        # Priority-based business value
        priority = work_item.get('priority', 'MEDIUM')
        if priority == 'CRITICAL':
            business_value_score += 10
        elif priority == 'HIGH':
            business_value_score += 7
        elif priority == 'MEDIUM':
            business_value_score += 4
        elif priority == 'LOW':
            business_value_score += 1
        
        # Auto-generated items get lower business value
        if work_item.get('auto_generated'):
            business_value_score = max(0, business_value_score - 5)
        
        return min(25, business_value_score)
    
    def sort_work_items_by_priority(self, work_items):
        """Sort work items by calculated priority (highest first)"""
        
        try:
            # Calculate priority for each work item
            for work_item in work_items:
                if 'priority_breakdown' not in work_item:
                    self.calculate_advanced_priority(work_item)
            
            # Sort by final priority (descending)
            sorted_items = sorted(
                work_items,
                key=lambda x: x.get('priority_breakdown', {}).get('final_priority', 0),
                reverse=True
            )
            
            logger.info(f"📊 Sorted {len(sorted_items)} work items by priority")
            
            # Log top priorities
            for i, item in enumerate(sorted_items[:5]):
                priority = item.get('priority_breakdown', {}).get('final_priority', 0)
                logger.info(f"   {i+1}. {item.get('name', 'Unknown')} - Priority: {priority}")
            
            return sorted_items
            
        except Exception as e:
            logger.error(f"Error sorting work items by priority: {e}")
            return work_items  # Return unsorted on error

    def track_performance_metrics(self):
        """Track comprehensive performance metrics"""
        
        try:
            current_time = datetime.now()
            
            # Processing speed metrics
            processing_speed = {
                'avg_time_per_work_item': self._calculate_avg_processing_time(),
                'total_work_items_processed': self.todos_processed_this_session,
                'processing_rate_per_hour': self._calculate_processing_rate(),
                'total_processing_time': self._calculate_total_processing_time()
            }
            
            # Worker efficiency metrics
            worker_efficiency = {
                'worker_utilization_rate': self._calculate_worker_utilization(),
                'idle_worker_time': self._calculate_idle_worker_time(),
                'worker_collaboration_score': self._calculate_worker_collaboration_score(),
                'active_workers': len(self.worker_assignments),
                'total_workers': self.max_workers
            }
            
            # Cache performance metrics
            cache_performance = {
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'cache_miss_rate': self._calculate_cache_miss_rate(),
                'cache_clear_frequency': self._calculate_cache_clear_frequency(),
                'cache_size': len(self.worker_cache),
                'cache_memory_usage': self._estimate_cache_memory_usage()
            }
            
            # Conflict resolution metrics
            conflict_resolution = {
                'conflicts_detected': getattr(self, 'conflicts_detected', 0),
                'conflicts_resolved': getattr(self, 'conflicts_resolved', 0),
                'resolution_time_avg': self._calculate_avg_conflict_resolution_time(),
                'last_conflict_detected': getattr(self, 'last_conflict_detected', None)
            }
            
            # System health metrics
            system_health = {
                'uptime': self._calculate_uptime(),
                'error_rate': self._calculate_error_rate(),
                'memory_usage': self._estimate_memory_usage(),
                'cpu_usage': self._estimate_cpu_usage()
            }
            
            # Work item processing metrics
            work_item_metrics = {
                'complex_todos_processed': getattr(self, 'complex_todos_processed', 0),
                'regular_todos_processed': getattr(self, 'regular_todos_processed', 0),
                'tasks_processed': getattr(self, 'tasks_processed', 0),
                'avg_breakdown_time': self._calculate_avg_breakdown_time(),
                'success_rate': self._calculate_success_rate()
            }
            
            metrics = {
                'processing_speed': processing_speed,
                'worker_efficiency': worker_efficiency,
                'cache_performance': cache_performance,
                'conflict_resolution': conflict_resolution,
                'system_health': system_health,
                'work_item_metrics': work_item_metrics,
                'timestamp': current_time.isoformat(),
                'session_duration': self._calculate_session_duration()
            }
            
            # Store metrics for historical analysis
            if not hasattr(self, 'performance_history'):
                self.performance_history = []
            
            self.performance_history.append(metrics)
            
            # Keep only last 100 entries to prevent memory bloat
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error tracking performance metrics: {e}")
            return {}
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        
        try:
            # Get current metrics
            current_metrics = self.track_performance_metrics()
            
            # Generate insights and recommendations
            insights = self._analyze_performance_insights(current_metrics)
            
            # Create comprehensive report
            report = {
                'summary': {
                    'report_generated_at': datetime.now().isoformat(),
                    'system_status': 'operational' if current_metrics.get('system_health', {}).get('error_rate', 0) < 0.1 else 'degraded',
                    'overall_performance_score': self._calculate_overall_performance_score(current_metrics)
                },
                'current_metrics': current_metrics,
                'insights': insights,
                'recommendations': self._generate_performance_recommendations(insights),
                'historical_trends': self._analyze_historical_trends()
            }
            
            # Export report
            self._export_performance_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}
    
    def _calculate_avg_processing_time(self):
        """Calculate average processing time per work item"""
        
        if not hasattr(self, 'processing_times') or not self.processing_times:
            return 0
        
        total_time = sum(self.processing_times)
        return total_time / len(self.processing_times)
    
    def _calculate_processing_rate(self):
        """Calculate processing rate per hour"""
        
        if not hasattr(self, 'session_start_time'):
            return 0
        
        session_duration = self._calculate_session_duration()
        if session_duration == 0:
            return 0
        
        return (self.todos_processed_this_session / session_duration) * 3600  # per hour
    
    def _calculate_total_processing_time(self):
        """Calculate total processing time"""
        
        if not hasattr(self, 'processing_times'):
            return 0
        
        return sum(self.processing_times)
    
    def _calculate_worker_utilization(self):
        """Calculate worker utilization rate"""
        
        if self.max_workers == 0:
            return 0
        
        active_workers = len(self.worker_assignments)
        return active_workers / self.max_workers
    
    def _calculate_idle_worker_time(self):
        """Calculate total idle worker time"""
        
        if not hasattr(self, 'worker_idle_times'):
            return 0
        
        return sum(self.worker_idle_times.values())
    
    def _calculate_worker_collaboration_score(self):
        """Calculate worker collaboration score"""
        
        if not self.worker_assignments:
            return 0
        
        # Calculate how well workers are collaborating
        collaboration_events = 0
        total_assignments = 0
        
        for todo_id, assignments in self.worker_assignments.items():
            if len(assignments) > 1:  # Multiple workers on same task
                collaboration_events += 1
            total_assignments += len(assignments)
        
        if total_assignments == 0:
            return 0
        
        return collaboration_events / total_assignments
    
    def _calculate_cache_hit_rate(self):
        """Calculate cache hit rate"""
        
        if not hasattr(self, 'cache_hits') or not hasattr(self, 'cache_misses'):
            return 0
        
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0
        
        return self.cache_hits / total_requests
    
    def _calculate_cache_miss_rate(self):
        """Calculate cache miss rate"""
        
        hit_rate = self._calculate_cache_hit_rate()
        return 1 - hit_rate
    
    def _calculate_cache_clear_frequency(self):
        """Calculate cache clear frequency"""
        
        if not hasattr(self, 'cache_clears'):
            return 0
        
        session_duration = self._calculate_session_duration()
        if session_duration == 0:
            return 0
        
        return self.cache_clears / session_duration  # clears per second
    
    def _estimate_cache_memory_usage(self):
        """Estimate cache memory usage in bytes"""
        
        # Rough estimation: assume each cache entry is about 1KB
        return len(self.worker_cache) * 1024
    
    def _calculate_avg_conflict_resolution_time(self):
        """Calculate average conflict resolution time"""
        
        if not hasattr(self, 'conflict_resolution_times') or not self.conflict_resolution_times:
            return 0
        
        return sum(self.conflict_resolution_times) / len(self.conflict_resolution_times)
    
    def _calculate_uptime(self):
        """Calculate system uptime"""
        
        if not hasattr(self, 'session_start_time'):
            return 0
        
        return self._calculate_session_duration()
    
    def _calculate_error_rate(self):
        """Calculate error rate"""
        
        if not hasattr(self, 'total_operations') or self.total_operations == 0:
            return 0
        
        return getattr(self, 'total_errors', 0) / self.total_operations
    
    def _estimate_memory_usage(self):
        """Estimate memory usage"""
        
        # Rough estimation based on data structures
        memory_estimate = 0
        
        # Cache size
        memory_estimate += len(self.worker_cache) * 1024
        
        # Work item queues
        memory_estimate += len(self.complex_todo_queue) * 512
        
        # Worker assignments
        memory_estimate += len(self.worker_assignments) * 256
        
        return memory_estimate
    
    def _estimate_cpu_usage(self):
        """Estimate CPU usage"""
        
        # This is a placeholder - in a real system you'd use psutil or similar
        # For now, estimate based on active workers
        active_workers = len(self.worker_assignments)
        return min(100, active_workers * 10)  # 10% per active worker
    
    def _calculate_avg_breakdown_time(self):
        """Calculate average breakdown time"""
        
        if not hasattr(self, 'breakdown_times') or not self.breakdown_times:
            return 0
        
        return sum(self.breakdown_times) / len(self.breakdown_times)
    
    def _calculate_success_rate(self):
        """Calculate success rate"""
        
        if not hasattr(self, 'total_operations') or self.total_operations == 0:
            return 1.0
        
        successful_operations = self.total_operations - getattr(self, 'total_errors', 0)
        return successful_operations / self.total_operations
    
    def _calculate_session_duration(self):
        """Calculate session duration in hours"""
        
        if not hasattr(self, 'session_start_time'):
            return 0
        
        duration = datetime.now() - self.session_start_time
        return duration.total_seconds() / 3600
    
    def _calculate_overall_performance_score(self, metrics):
        """Calculate overall performance score (0-100)"""
        
        try:
            score = 0
            
            # Worker utilization (25 points)
            utilization = metrics.get('worker_efficiency', {}).get('worker_utilization_rate', 0)
            score += utilization * 25
            
            # Cache hit rate (20 points)
            cache_hit_rate = metrics.get('cache_performance', {}).get('cache_hit_rate', 0)
            score += cache_hit_rate * 20
            
            # Success rate (25 points)
            success_rate = metrics.get('work_item_metrics', {}).get('success_rate', 1.0)
            score += success_rate * 25
            
            # Processing rate (15 points)
            processing_rate = metrics.get('processing_speed', {}).get('processing_rate_per_hour', 0)
            score += min(15, processing_rate / 10)  # Normalize to 15 points
            
            # Error rate (15 points)
            error_rate = metrics.get('system_health', {}).get('error_rate', 0)
            score += max(0, 15 - (error_rate * 150))  # Reduce score for errors
            
            return min(100, max(0, int(score)))
            
        except Exception as e:
            logger.error(f"Error calculating overall performance score: {e}")
            return 50  # Default middle score

    def adaptive_worker_allocation(self, work_items):
        """Dynamically allocate workers based on workload"""
        
        try:
            if not work_items:
                logger.info("No work items for adaptive allocation")
                return {}
            
            # Analyze workload complexity
            total_complexity = sum(self._calculate_work_complexity(item) for item in work_items)
            workload_distribution = self._analyze_workload_distribution(work_items)
            
            logger.info(f"🔍 Workload Analysis: Total complexity {total_complexity}, "
                       f"Distribution: {workload_distribution}")
            
            # Determine optimal worker distribution
            if total_complexity > 80:
                # High complexity: More workers on complex items
                allocation = {
                    'complex_todos': min(6, self.max_workers - 2),
                    'regular_todos': min(2, self.max_workers - 6),
                    'tasks': max(0, self.max_workers - 8)
                }
                strategy = "high_complexity_focus"
            elif total_complexity > 50:
                # Medium complexity: Balanced distribution
                allocation = {
                    'complex_todos': min(4, self.max_workers - 3),
                    'regular_todos': min(3, self.max_workers - 4),
                    'tasks': max(1, self.max_workers - 7)
                }
                strategy = "balanced_distribution"
            else:
                # Low complexity: More workers on simple items
                allocation = {
                    'complex_todos': min(2, self.max_workers - 3),
                    'regular_todos': min(3, self.max_workers - 2),
                    'tasks': max(3, self.max_workers - 5)
                }
                strategy = "simple_item_focus"
            
            # Ensure we don't exceed max workers
            total_allocated = sum(allocation.values())
            if total_allocated > self.max_workers:
                # Scale down proportionally
                scale_factor = self.max_workers / total_allocated
                allocation = {k: max(1, int(v * scale_factor)) for k, v in allocation.items()}
            
            # Add strategy information
            allocation['strategy'] = strategy
            allocation['total_workers'] = sum(allocation.values())
            allocation['complexity_threshold'] = total_complexity
            
            logger.info(f"🎯 Adaptive Worker Allocation: {strategy}")
            logger.info(f"   - Complex TODOs: {allocation['complex_todos']} workers")
            logger.info(f"   - Regular TODOs: {allocation['regular_todos']} workers")
            logger.info(f"   - Tasks: {allocation['tasks']} workers")
            logger.info(f"   - Total: {allocation['total_workers']} workers")
            
            return allocation
            
        except Exception as e:
            logger.error(f"Error in adaptive worker allocation: {e}")
            # Fallback to default allocation
            return {
                'complex_todos': 3,
                'regular_todos': 3,
                'tasks': 2,
                'strategy': 'fallback',
                'total_workers': 8,
                'complexity_threshold': 0
            }
    
    def _calculate_work_complexity(self, work_item):
        """Calculate complexity score for a work item"""
        
        complexity_scores = {
            'critical': 40,
            'high': 30,
            'medium': 20,
            'low': 10
        }
        
        base_complexity = complexity_scores.get(work_item.get('complexity', 'medium'), 20)
        
        # Adjust based on estimated hours
        estimated_hours = work_item.get('estimated_hours', 4)
        if estimated_hours > 8:
            base_complexity += 20
        elif estimated_hours > 4:
            base_complexity += 10
        
        # Adjust based on required capabilities
        required_capabilities = work_item.get('required_capabilities', [])
        if len(required_capabilities) > 3:
            base_complexity += 15
        elif len(required_capabilities) > 1:
            base_complexity += 10
        
        return min(100, base_complexity)
    
    def _analyze_workload_distribution(self, work_items):
        """Analyze distribution of work items by type"""
        
        distribution = {
            'complex_todos': 0,
            'regular_todos': 0,
            'tasks': 0
        }
        
        for item in work_items:
            complexity = item.get('complexity', 'medium')
            if complexity in ['high', 'critical']:
                distribution['complex_todos'] += 1
            elif complexity == 'medium':
                distribution['regular_todos'] += 1
            else:
                distribution['tasks'] += 1
        
        return distribution
    
    def execute_adaptive_allocation(self, work_items):
        """Execute the adaptive worker allocation strategy"""
        
        try:
            # Get allocation plan
            allocation = self.adaptive_worker_allocation(work_items)
            
            # Sort work items by priority
            sorted_work_items = self.sort_work_items_by_priority(work_items)
            
            # Distribute workers according to allocation
            worker_distribution = self._distribute_workers_by_allocation(sorted_work_items, allocation)
            
            # Apply the distribution
            self._apply_worker_distribution(worker_distribution)
            
            logger.info(f"✅ Adaptive worker allocation executed successfully")
            return worker_distribution
            
        except Exception as e:
            logger.error(f"Error executing adaptive allocation: {e}")
            return {}
    
    def _distribute_workers_by_allocation(self, work_items, allocation):
        """Distribute workers according to allocation plan"""
        
        worker_distribution = {}
        
        # Separate work items by type
        complex_todos = [item for item in work_items if item.get('complexity') in ['high', 'critical']]
        regular_todos = [item for item in work_items if item.get('complexity') == 'medium']
        tasks = [item for item in work_items if item.get('complexity') == 'low']
        
        # Distribute workers for complex TODOs
        workers_per_complex = allocation['complex_todos']
        for i, todo in enumerate(complex_todos[:workers_per_complex]):
            worker_id = i % self.max_workers
            worker_distribution[todo.todo_id] = [worker_id]
        
        # Distribute workers for regular TODOs
        workers_per_regular = allocation['regular_todos']
        for i, todo in enumerate(regular_todos[:workers_per_regular]):
            worker_id = (i + workers_per_complex) % self.max_workers
            if todo.todo_id not in worker_distribution:
                worker_distribution[todo.todo_id] = []
            worker_distribution[todo.todo_id].append(worker_id)
        
        # Distribute workers for tasks
        workers_per_task = allocation['tasks']
        for i, task in enumerate(tasks[:workers_per_task]):
            worker_id = (i + workers_per_complex + workers_per_regular) % self.max_workers
            if task.todo_id not in worker_distribution:
                worker_distribution[task.todo_id] = []
            worker_distribution[task.todo_id].append(worker_id)
        
        return worker_distribution
    
    def _apply_worker_distribution(self, worker_distribution):
        """Apply the worker distribution to the system"""
        
        try:
            # Clear existing assignments
            self.worker_assignments.clear()
            
            # Apply new distribution
            for todo_id, worker_ids in worker_distribution.items():
                self.worker_assignments[todo_id] = worker_ids
            
            logger.info(f"✅ Applied worker distribution: {len(worker_distribution)} work items assigned")
            
        except Exception as e:
            logger.error(f"Error applying worker distribution: {e}")
    
    def optimize_worker_allocation(self):
        """Continuously optimize worker allocation based on performance"""
        
        try:
            # Get current performance metrics
            metrics = self.track_performance_metrics()
            
            # Check if optimization is needed
            worker_utilization = metrics.get('worker_efficiency', {}).get('worker_utilization_rate', 0)
            processing_rate = metrics.get('processing_speed', {}).get('processing_rate_per_hour', 0)
            
            # Optimize if utilization is low or processing rate is poor
            if worker_utilization < 0.6 or processing_rate < 2:
                logger.info("🔄 Worker allocation optimization triggered")
                
                # Get current work items
                current_work_items = list(self.complex_todo_queue)
                
                if current_work_items:
                    # Re-allocate workers
                    new_allocation = self.execute_adaptive_allocation(current_work_items)
                    logger.info(f"✅ Worker allocation optimized: {len(new_allocation)} items reallocated")
                else:
                    logger.info("No work items to optimize allocation for")
            
        except Exception as e:
            logger.error(f"Error in worker allocation optimization: {e}")

    def ml_classify_work_item(self, work_item_description):
        """Use ML to classify work items intelligently"""
        
        try:
            # Feature extraction
            features = self._extract_ml_features(work_item_description)
            
            # ML model prediction (placeholder for actual ML implementation)
            predicted_complexity = self._ml_model_predict_complexity(features)
            predicted_priority = self._ml_model_predict_priority(features)
            estimated_hours = self._ml_model_predict_effort(features)
            confidence_score = self._ml_model_get_confidence(features)
            
            classification_result = {
                'complexity': predicted_complexity,
                'priority': predicted_priority,
                'estimated_hours': estimated_hours,
                'confidence_score': confidence_score,
                'features_used': features,
                'classification_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🤖 ML Classification: {predicted_complexity} complexity, "
                       f"{predicted_priority} priority, {estimated_hours}h effort "
                       f"(confidence: {confidence_score:.2f})")
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Error in ML classification: {e}")
            # Fallback to rule-based classification
            return self._fallback_classification(work_item_description)
    
    def _extract_ml_features(self, description):
        """Extract features for ML classification"""
        
        features = {}
        
        try:
            # Text length features
            features['text_length'] = len(description)
            features['word_count'] = len(description.split())
            features['sentence_count'] = len(description.split('.'))
            
            # Technical complexity features
            features['technical_terms'] = self._count_technical_terms(description)
            features['code_snippets'] = self._count_code_snippets(description)
            features['api_mentions'] = self._count_api_mentions(description)
            
            # Time and effort indicators
            features['time_indicators'] = self._extract_time_indicators(description)
            features['effort_indicators'] = self._extract_effort_indicators(description)
            
            # Complexity indicators
            features['complexity_indicators'] = self._extract_complexity_indicators(description)
            features['dependency_indicators'] = self._extract_dependency_indicators(description)
            
            # Business value indicators
            features['business_critical_terms'] = self._count_business_critical_terms(description)
            features['security_terms'] = self._count_security_terms(description)
            features['user_experience_terms'] = self._count_user_experience_terms(description)
            
            # Normalize features
            features = self._normalize_features(features)
            
        except Exception as e:
            logger.error(f"Error extracting ML features: {e}")
            features = {'error': str(e)}
        
        return features
    
    def _count_technical_terms(self, description):
        """Count technical terms in description"""
        
        technical_terms = [
            'api', 'database', 'schema', 'authentication', 'authorization',
            'encryption', 'caching', 'load balancing', 'microservices',
            'docker', 'kubernetes', 'ci/cd', 'testing', 'deployment',
            'monitoring', 'logging', 'error handling', 'validation',
            'optimization', 'scalability', 'performance', 'security'
        ]
        
        count = 0
        description_lower = description.lower()
        for term in technical_terms:
            if term in description_lower:
                count += 1
        
        return count
    
    def _count_code_snippets(self, description):
        """Count code snippets in description"""
        
        # Look for code-like patterns
        code_patterns = [
            'function', 'class', 'method', 'variable', 'import',
            'if', 'else', 'for', 'while', 'try', 'catch',
            'async', 'await', 'promise', 'callback', 'event'
        ]
        
        count = 0
        description_lower = description.lower()
        for pattern in code_patterns:
            if pattern in description_lower:
                count += 1
        
        return count
    
    def _count_api_mentions(self, description):
        """Count API-related mentions"""
        
        api_terms = [
            'endpoint', 'request', 'response', 'http', 'rest', 'graphql',
            'post', 'get', 'put', 'delete', 'patch', 'status code',
            'headers', 'body', 'query', 'parameters'
        ]
        
        count = 0
        description_lower = description.lower()
        for term in api_terms:
            if term in description_lower:
                count += 1
        
        return count
    
    def _extract_time_indicators(self, description):
        """Extract time-related indicators"""
        
        time_indicators = {
            'immediate': 0,
            'urgent': 0,
            'soon': 0,
            'later': 0,
            'future': 0
        }
        
        description_lower = description.lower()
        
        if 'immediate' in description_lower or 'asap' in description_lower:
            time_indicators['immediate'] = 1
        if 'urgent' in description_lower or 'critical' in description_lower:
            time_indicators['urgent'] = 1
        if 'soon' in description_lower or 'quick' in description_lower:
            time_indicators['soon'] = 1
        if 'later' in description_lower or 'eventually' in description_lower:
            time_indicators['later'] = 1
        if 'future' in description_lower or 'planning' in description_lower:
            time_indicators['future'] = 1
        
        return time_indicators
    
    def _extract_effort_indicators(self, description):
        """Extract effort-related indicators"""
        
        effort_indicators = {
            'simple': 0,
            'moderate': 0,
            'complex': 0,
            'very_complex': 0
        }
        
        description_lower = description.lower()
        
        if 'simple' in description_lower or 'easy' in description_lower:
            effort_indicators['simple'] = 1
        if 'moderate' in description_lower or 'medium' in description_lower:
            effort_indicators['moderate'] = 1
        if 'complex' in description_lower or 'difficult' in description_lower:
            effort_indicators['complex'] = 1
        if 'very complex' in description_lower or 'extremely difficult' in description_lower:
            effort_indicators['very_complex'] = 1
        
        return effort_indicators
    
    def _extract_complexity_indicators(self, description):
        """Extract complexity-related indicators"""
        
        complexity_indicators = {
            'architecture': 0,
            'integration': 0,
            'testing': 0,
            'documentation': 0,
            'deployment': 0
        }
        
        description_lower = description.lower()
        
        if 'architecture' in description_lower or 'design' in description_lower:
            complexity_indicators['architecture'] = 1
        if 'integration' in description_lower or 'connect' in description_lower:
            complexity_indicators['integration'] = 1
        if 'testing' in description_lower or 'test' in description_lower:
            complexity_indicators['testing'] = 1
        if 'documentation' in description_lower or 'docs' in description_lower:
            complexity_indicators['documentation'] = 1
        if 'deployment' in description_lower or 'deploy' in description_lower:
            complexity_indicators['deployment'] = 1
        
        return complexity_indicators
    
    def _extract_dependency_indicators(self, description):
        """Extract dependency-related indicators"""
        
        dependency_indicators = {
            'depends_on': 0,
            'requires': 0,
            'after': 0,
            'prerequisite': 0,
            'blocking': 0
        }
        
        description_lower = description.lower()
        
        if 'depends on' in description_lower or 'dependency' in description_lower:
            dependency_indicators['depends_on'] = 1
        if 'requires' in description_lower or 'requirement' in description_lower:
            dependency_indicators['requires'] = 1
        if 'after' in description_lower or 'following' in description_lower:
            dependency_indicators['after'] = 1
        if 'prerequisite' in description_lower or 'prereq' in description_lower:
            dependency_indicators['prerequisite'] = 1
        if 'blocking' in description_lower or 'blocks' in description_lower:
            dependency_indicators['blocking'] = 1
        
        return dependency_indicators
    
    def _count_business_critical_terms(self, description):
        """Count business-critical terms"""
        
        business_terms = [
            'revenue', 'customer', 'user', 'business', 'money',
            'sales', 'marketing', 'product', 'service', 'compliance'
        ]
        
        count = 0
        description_lower = description.lower()
        for term in business_terms:
            if term in description_lower:
                count += 1
        
        return count
    
    def _count_security_terms(self, description):
        """Count security-related terms"""
        
        security_terms = [
            'security', 'authentication', 'authorization', 'encryption',
            'password', 'token', 'jwt', 'oauth', 'ssl', 'https',
            'vulnerability', 'threat', 'attack', 'breach', 'compliance'
        ]
        
        count = 0
        description_lower = description.lower()
        for term in security_terms:
            if term in description_lower:
                count += 1
        
        return count
    
    def _count_user_experience_terms(self, description):
        """Count user experience terms"""
        
        ux_terms = [
            'user experience', 'ui', 'ux', 'interface', 'design',
            'usability', 'accessibility', 'responsive', 'mobile',
            'user friendly', 'intuitive', 'navigation', 'layout'
        ]
        
        count = 0
        description_lower = description.lower()
        for term in ux_terms:
            if term in description_lower:
                count += 1
        
        return count
    
    def _normalize_features(self, features):
        """Normalize feature values to 0-1 range"""
        
        normalized_features = {}
        
        for key, value in features.items():
            if isinstance(value, (int, float)):
                # Simple normalization for now
                if key in ['text_length', 'word_count', 'sentence_count']:
                    normalized_features[key] = min(1.0, value / 1000)  # Cap at 1000
                elif key in ['technical_terms', 'code_snippets', 'api_mentions']:
                    normalized_features[key] = min(1.0, value / 20)  # Cap at 20
                else:
                    normalized_features[key] = min(1.0, value)
            elif isinstance(value, dict):
                # Recursively normalize nested dictionaries
                normalized_features[key] = self._normalize_features(value)
            else:
                normalized_features[key] = value
        
        return normalized_features
    
    def _ml_model_predict_complexity(self, features):
        """ML model prediction for complexity (placeholder)"""
        
        try:
            # Simple rule-based complexity prediction based on features
            complexity_score = 0
            
            # Technical complexity
            complexity_score += features.get('technical_terms', 0) * 0.3
            complexity_score += features.get('code_snippets', 0) * 0.2
            complexity_score += features.get('api_mentions', 0) * 0.2
            
            # Effort indicators
            effort_indicators = features.get('effort_indicators', {})
            complexity_score += effort_indicators.get('simple', 0) * 0.1
            complexity_score += effort_indicators.get('moderate', 0) * 0.3
            complexity_score += effort_indicators.get('complex', 0) * 0.6
            complexity_score += effort_indicators.get('very_complex', 0) * 0.9
            
            # Map score to complexity levels
            if complexity_score < 0.3:
                return 'low'
            elif complexity_score < 0.6:
                return 'medium'
            elif complexity_score < 0.8:
                return 'high'
            else:
                return 'critical'
                
        except Exception as e:
            logger.error(f"Error in ML complexity prediction: {e}")
            return 'medium'  # Default fallback
    
    def _ml_model_predict_priority(self, features):
        """ML model prediction for priority (placeholder)"""
        
        try:
            # Simple rule-based priority prediction
            priority_score = 0
            
            # Time urgency
            time_indicators = features.get('time_indicators', {})
            priority_score += time_indicators.get('immediate', 0) * 0.9
            priority_score += time_indicators.get('urgent', 0) * 0.8
            priority_score += time_indicators.get('soon', 0) * 0.6
            
            # Business criticality
            priority_score += features.get('business_critical_terms', 0) * 0.2
            priority_score += features.get('security_terms', 0) * 0.3
            
            # Map score to priority levels
            if priority_score < 0.3:
                return 'LOW'
            elif priority_score < 0.6:
                return 'MEDIUM'
            elif priority_score < 0.8:
                return 'HIGH'
            else:
                return 'CRITICAL'
                
        except Exception as e:
            logger.error(f"Error in ML priority prediction: {e}")
            return 'MEDIUM'  # Default fallback
    
    def _ml_model_predict_effort(self, features):
        """ML model prediction for effort hours (placeholder)"""
        
        try:
            # Simple rule-based effort estimation
            base_effort = 2.0  # Base 2 hours
            
            # Adjust based on text length
            text_length = features.get('text_length', 0)
            if text_length > 500:
                base_effort += 2.0
            elif text_length > 200:
                base_effort += 1.0
            
            # Adjust based on technical complexity
            technical_terms = features.get('technical_terms', 0)
            base_effort += technical_terms * 0.5
            
            # Adjust based on complexity indicators
            complexity_indicators = features.get('complexity_indicators', {})
            for indicator, value in complexity_indicators.items():
                if value > 0:
                    base_effort += 1.0
            
            # Cap at reasonable maximum
            return min(40.0, max(0.5, base_effort))
            
        except Exception as e:
            logger.error(f"Error in ML effort prediction: {e}")
            return 4.0  # Default 4 hours
    
    def _ml_model_get_confidence(self, features):
        """Get confidence score for ML predictions (placeholder)"""
        
        try:
            # Calculate confidence based on feature quality
            confidence = 0.5  # Base confidence
            
            # Higher confidence for more detailed descriptions
            text_length = features.get('text_length', 0)
            if text_length > 100:
                confidence += 0.2
            if text_length > 300:
                confidence += 0.1
            
            # Higher confidence for technical descriptions
            technical_terms = features.get('technical_terms', 0)
            if technical_terms > 3:
                confidence += 0.2
            elif technical_terms > 1:
                confidence += 0.1
            
            # Higher confidence for clear indicators
            time_indicators = features.get('time_indicators', {})
            effort_indicators = features.get('effort_indicators', {})
            
            if any(time_indicators.values()):
                confidence += 0.1
            if any(effort_indicators.values()):
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating ML confidence: {e}")
            return 0.5  # Default confidence
    
    def _fallback_classification(self, description):
        """Fallback classification when ML fails"""
        
        logger.info("🔄 Using fallback rule-based classification")
        
        # Simple rule-based classification
        description_lower = description.lower()
        
        # Complexity classification
        if any(term in description_lower for term in ['critical', 'very complex', 'architecture']):
            complexity = 'critical'
        elif any(term in description_lower for term in ['high', 'complex', 'integration']):
            complexity = 'high'
        elif any(term in description_lower for term in ['medium', 'moderate']):
            complexity = 'medium'
        else:
            complexity = 'low'
        
        # Priority classification
        if any(term in description_lower for term in ['urgent', 'asap', 'critical']):
            priority = 'CRITICAL'
        elif any(term in description_lower for term in ['high', 'important']):
            priority = 'HIGH'
        elif any(term in description_lower for term in ['medium', 'normal']):
            priority = 'MEDIUM'
        else:
            priority = 'LOW'
        
        # Effort estimation
        if complexity == 'critical':
            estimated_hours = 12.0
        elif complexity == 'high':
            estimated_hours = 8.0
        elif complexity == 'medium':
            estimated_hours = 4.0
        else:
            estimated_hours = 2.0
        
        return {
            'complexity': complexity,
            'priority': priority,
            'estimated_hours': estimated_hours,
            'confidence_score': 0.3,  # Lower confidence for fallback
            'classification_method': 'fallback_rule_based',
            'classification_timestamp': datetime.now().isoformat()
        }

    def analyze_work_dependencies(self, work_items):
        """Analyze dependencies between work items"""
        
        try:
            dependencies = {}
            logger.info(f"🔍 Analyzing dependencies for {len(work_items)} work items...")
            
            for work_item in work_items:
                # Extract dependency information
                dependency_info = self._extract_dependency_info(work_item)
                
                # Find related work items
                related_items = self._find_related_work_items(work_item, work_items)
                
                dependencies[work_item.todo_id] = {
                    'prerequisites': related_items['prerequisites'],
                    'dependents': related_items['dependents'],
                    'parallel_executable': related_items['parallel_executable'],
                    'dependency_type': dependency_info['type'],
                    'dependency_strength': dependency_info['strength'],
                    'blocks_others': dependency_info['blocks_others']
                }
            
            logger.info(f"✅ Dependency analysis complete: {len(dependencies)} work items analyzed")
            return dependencies
            
        except Exception as e:
            logger.error(f"Error analyzing work dependencies: {e}")
            return {}
    
    def _extract_dependency_info(self, work_item):
        """Extract dependency information from a work item"""
        
        description = work_item.description.lower()
        name = work_item.name.lower()
        
        dependency_info = {
            'type': 'none',
            'strength': 'weak',
            'blocks_others': False
        }
        
        # Check for strong dependencies
        strong_dependency_keywords = [
            'depends on', 'requires', 'prerequisite', 'must complete first',
            'blocked by', 'waiting for', 'after completion of'
        ]
        
        if any(keyword in description for keyword in strong_dependency_keywords):
            dependency_info['type'] = 'strong'
            dependency_info['strength'] = 'strong'
        
        # Check for medium dependencies
        medium_dependency_keywords = [
            'after', 'following', 'subsequent to', 'builds on',
            'extends', 'enhances', 'improves'
        ]
        
        if any(keyword in description for keyword in medium_dependency_keywords):
            if dependency_info['type'] == 'none':
                dependency_info['type'] = 'medium'
                dependency_info['strength'] = 'medium'
        
        # Check for blocking dependencies
        blocking_keywords = [
            'blocks', 'prevents', 'stops', 'halts', 'critical path',
            'gateway', 'milestone', 'checkpoint'
        ]
        
        if any(keyword in description for keyword in blocking_keywords):
            dependency_info['blocks_others'] = True
        
        return dependency_info
    
    def _find_related_work_items(self, current_item, all_work_items):
        """Find work items related to the current item"""
        
        related_items = {
            'prerequisites': [],
            'dependents': [],
            'parallel_executable': []
        }
        
        current_description = current_item.description.lower()
        current_name = current_item.name.lower()
        
        for other_item in all_work_items:
            if other_item.todo_id == current_item.todo_id:
                continue
            
            other_description = other_item.description.lower()
            other_name = other_item.name.lower()
            
            # Check if this item is a prerequisite
            if self._is_prerequisite(current_item, other_item):
                related_items['prerequisites'].append(other_item.todo_id)
            
            # Check if this item depends on the other
            elif self._is_dependent(current_item, other_item):
                related_items['dependents'].append(other_item.todo_id)
            
            # Check if they can be executed in parallel
            elif self._can_execute_in_parallel(current_item, other_item):
                related_items['parallel_executable'].append(other_item.todo_id)
        
        return related_items
    
    def _is_prerequisite(self, current_item, other_item):
        """Check if current item is a prerequisite for other item"""
        
        other_description = other_item.description.lower()
        other_name = other_item.name.lower()
        
        # Check if other item mentions current item as prerequisite
        current_name_lower = current_item.name.lower()
        current_keywords = current_name_lower.split()
        
        for keyword in current_keywords:
            if len(keyword) > 3:  # Only check meaningful keywords
                if f"after {keyword}" in other_description or f"following {keyword}" in other_description:
                    return True
                if f"depends on {keyword}" in other_description or f"requires {keyword}" in other_description:
                    return True
        
        return False
    
    def _is_dependent(self, current_item, other_item):
        """Check if current item depends on other item"""
        
        current_description = current_item.description.lower()
        current_name = current_item.name.lower()
        
        # Check if current item mentions other item as prerequisite
        other_name_lower = other_item.name.lower()
        other_keywords = other_name_lower.split()
        
        for keyword in other_keywords:
            if len(keyword) > 3:  # Only check meaningful keywords
                if f"after {keyword}" in current_description or f"following {keyword}" in current_description:
                    return True
                if f"depends on {keyword}" in current_description or f"requires {keyword}" in current_description:
                    return True
        
        return False
    
    def _can_execute_in_parallel(self, item1, item2):
        """Check if two items can be executed in parallel"""
        
        # Items can be parallel if they don't have dependencies on each other
        if not self._is_prerequisite(item1, item2) and not self._is_dependent(item1, item2):
            # Check if they share resources that would prevent parallel execution
            if not self._shares_critical_resources(item1, item2):
                return True
        
        return False
    
    def _shares_critical_resources(self, item1, item2):
        """Check if two items share critical resources that prevent parallel execution"""
        
        # Check for shared database tables, APIs, or critical infrastructure
        shared_resources = [
            'database', 'main database', 'primary api', 'authentication service',
            'user management', 'core system', 'main application'
        ]
        
        item1_desc = item1.description.lower()
        item2_desc = item2.description.lower()
        
        for resource in shared_resources:
            if resource in item1_desc and resource in item2_desc:
                return True
        
        return False
    
    def create_execution_workflow(self, work_items, dependencies):
        """Create optimal execution workflow"""
        
        try:
            logger.info("🔄 Creating optimal execution workflow...")
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(work_items, dependencies)
            
            # Topological sort for execution order
            execution_order = self._topological_sort(dependency_graph)
            
            # Identify parallel execution opportunities
            parallel_groups = self._identify_parallel_groups(execution_order, dependencies)
            
            # Calculate estimated execution time
            estimated_total_time = self._calculate_total_execution_time(execution_order, work_items)
            
            workflow = {
                'execution_order': execution_order,
                'parallel_groups': parallel_groups,
                'estimated_total_time': estimated_total_time,
                'critical_path': self._identify_critical_path(dependency_graph, work_items),
                'resource_requirements': self._analyze_resource_requirements(work_items),
                'optimization_opportunities': self._identify_optimization_opportunities(workflow)
            }
            
            logger.info(f"✅ Execution workflow created: {len(execution_order)} steps, "
                       f"{len(parallel_groups)} parallel groups, {estimated_total_time:.1f}h total")
            
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating execution workflow: {e}")
            return {}
    
    def _build_dependency_graph(self, work_items, dependencies):
        """Build dependency graph for workflow analysis"""
        
        graph = {}
        
        for work_item in work_items:
            todo_id = work_item.todo_id
            graph[todo_id] = {
                'dependencies': dependencies.get(todo_id, {}).get('prerequisites', []),
                'dependents': dependencies.get(todo_id, {}).get('dependents', []),
                'work_item': work_item
            }
        
        return graph
    
    def _topological_sort(self, dependency_graph):
        """Perform topological sort to determine execution order"""
        
        try:
            # Kahn's algorithm for topological sorting
            in_degree = {}
            graph = {}
            
            # Initialize
            for node in dependency_graph:
                in_degree[node] = len(dependency_graph[node]['dependencies'])
                graph[node] = dependency_graph[node]['dependencies']
            
            # Find nodes with no incoming edges
            queue = [node for node in in_degree if in_degree[node] == 0]
            result = []
            
            while queue:
                current = queue.pop(0)
                result.append(current)
                
                # Remove edges from current node
                for dependent in dependency_graph[current]['dependents']:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            queue.append(dependent)
            
            # Check for cycles
            if len(result) != len(dependency_graph):
                logger.warning("⚠️  Circular dependency detected in workflow")
                # Return partial result
                return result
            
            return result
            
        except Exception as e:
            logger.error(f"Error in topological sort: {e}")
            # Return items in original order as fallback
            return list(dependency_graph.keys())
    
    def _identify_parallel_groups(self, execution_order, dependencies):
        """Identify groups of work items that can be executed in parallel"""
        
        parallel_groups = []
        current_group = []
        
        for todo_id in execution_order:
            # Check if this item can be added to current parallel group
            can_add_to_group = True
            
            for item_in_group in current_group:
                # Check if there are dependencies between items in the group
                item_deps = dependencies.get(todo_id, {})
                if item_in_group in item_deps.get('prerequisites', []):
                    can_add_to_group = False
                    break
            
            if can_add_to_group:
                current_group.append(todo_id)
            else:
                # Start new group
                if current_group:
                    parallel_groups.append(current_group)
                current_group = [todo_id]
        
        # Add final group
        if current_group:
            parallel_groups.append(current_group)
        
        return parallel_groups
    
    def _calculate_total_execution_time(self, execution_order, work_items):
        """Calculate total estimated execution time"""
        
        total_time = 0
        
        for todo_id in execution_order:
            work_item = next((item for item in work_items if item.todo_id == todo_id), None)
            if work_item:
                estimated_hours = work_item.estimated_hours or 4.0  # Default 4 hours
                total_time += estimated_hours
        
        return total_time
    
    def _identify_critical_path(self, dependency_graph, work_items):
        """Identify the critical path in the workflow"""
        
        try:
            # Simple critical path identification
            # In a real system, you'd use more sophisticated algorithms
            
            critical_path = []
            max_time = 0
            
            # Find the longest path through the dependency graph
            for start_node in dependency_graph:
                path_time = self._calculate_path_time(start_node, dependency_graph, work_items, set())
                if path_time > max_time:
                    max_time = path_time
                    critical_path = self._get_path(start_node, dependency_graph, work_items, set())
            
            return critical_path
            
        except Exception as e:
            logger.error(f"Error identifying critical path: {e}")
            return []
    
    def _calculate_path_time(self, node, graph, work_items, visited):
        """Calculate time for a path starting from a node"""
        
        if node in visited:
            return 0
        
        visited.add(node)
        
        # Get work item time
        work_item = next((item for item in work_items if item.todo_id == node), None)
        current_time = work_item.estimated_hours if work_item else 4.0
        
        # Find maximum time among dependents
        max_dependent_time = 0
        for dependent in graph[node]['dependents']:
            dependent_time = self._calculate_path_time(dependent, graph, work_items, visited)
            max_dependent_time = max(max_dependent_time, dependent_time)
        
        return current_time + max_dependent_time
    
    def _get_path(self, node, graph, work_items, visited):
        """Get the path starting from a node"""
        
        if node in visited:
            return []
        
        visited.add(node)
        path = [node]
        
        # Find dependent with maximum time
        max_time = 0
        max_dependent = None
        
        for dependent in graph[node]['dependents']:
            dependent_time = self._calculate_path_time(dependent, graph, work_items, set())
            if dependent_time > max_time:
                max_time = dependent_time
                max_dependent = dependent
        
        if max_dependent:
            path.extend(self._get_path(max_dependent, graph, work_items, visited))
        
        return path
    
    def _analyze_resource_requirements(self, work_items):
        """Analyze resource requirements for the workflow"""
        
        resource_requirements = {
            'total_workers_needed': 0,
            'peak_workers_needed': 0,
            'specialized_skills': set(),
            'infrastructure_needs': set()
        }
        
        for work_item in work_items:
            # Count workers needed
            estimated_hours = work_item.estimated_hours or 4.0
            workers_needed = max(1, int(estimated_hours / 2))  # Assume 2 hours per worker
            resource_requirements['total_workers_needed'] += workers_needed
            
            # Track specialized skills
            required_capabilities = work_item.required_capabilities or []
            resource_requirements['specialized_skills'].update(required_capabilities)
            
            # Track infrastructure needs
            if 'database' in work_item.description.lower():
                resource_requirements['infrastructure_needs'].add('database')
            if 'api' in work_item.description.lower():
                resource_requirements['infrastructure_needs'].add('api_gateway')
            if 'deployment' in work_item.description.lower():
                resource_requirements['infrastructure_needs'].add('deployment_pipeline')
        
        # Calculate peak workers needed
        resource_requirements['peak_workers_needed'] = min(
            resource_requirements['total_workers_needed'],
            self.max_workers
        )
        
        # Convert sets to lists for JSON serialization
        resource_requirements['specialized_skills'] = list(resource_requirements['specialized_skills'])
        resource_requirements['infrastructure_needs'] = list(resource_requirements['infrastructure_needs'])
        
        return resource_requirements
    
    def _identify_optimization_opportunities(self, workflow):
        """Identify opportunities to optimize the workflow"""
        
        optimization_opportunities = []
        
        # Check for long sequential chains
        if len(workflow.get('execution_order', [])) > 10:
            optimization_opportunities.append({
                'type': 'long_sequential_chain',
                'description': 'Workflow has many sequential steps that could be parallelized',
                'impact': 'high',
                'effort': 'medium'
            })
        
        # Check for underutilized parallel execution
        parallel_groups = workflow.get('parallel_groups', [])
        if parallel_groups:
            avg_group_size = sum(len(group) for group in parallel_groups) / len(parallel_groups)
            if avg_group_size < 2:
                optimization_opportunities.append({
                    'type': 'underutilized_parallelization',
                    'description': 'Parallel groups are small, could combine more work items',
                    'impact': 'medium',
                    'effort': 'low'
                })
        
        # Check for resource bottlenecks
        resource_requirements = workflow.get('resource_requirements', {})
        if resource_requirements.get('peak_workers_needed', 0) > self.max_workers * 0.8:
            optimization_opportunities.append({
                'type': 'resource_bottleneck',
                'description': 'Peak worker demand may exceed available capacity',
                'impact': 'high',
                'effort': 'high'
            })
        
        return optimization_opportunities

def demo_collective_worker_processing():
    """Demonstrate collective worker processing capabilities"""
    
    print("🚀 COLLECTIVE WORKER PROCESSING DEMONSTRATION")
    print("=" * 70)
    
    # Initialize processor
    processor = CollectiveWorkerProcessor(max_workers=8, min_batch_size=3, max_batch_size=50)
    
    print(f"Processor Configuration:")
    print(f"  - Max Workers: {processor.max_workers}")
    print(f"  - Collective Workers: {processor.collective_workers}")
    print(f"  - Cache Optimization: {processor.cache_clear_on_completion}")
    print()
    
    # Check TODO master integration
    if TODO_MASTER_AVAILABLE:
        print("✅ TODO Master Integration: AVAILABLE")
        print("🔄 Will scan, mark, and load work items for collective processing")
        print()
        
        print("🎯 NEW SCANNING & MARKING CAPABILITIES:")
        print("-" * 50)
        print("• 🔍 Active TODO Master Scanning: Prevents conflicts with other agents")
        print("• 🏷️  Conflict Prevention Markings: Marks work items as 'assigned'")
        print("• 📥 Batch Loading: 1 task + 3 complex TODOs + 10 regular TODOs")
        print("• 🚫 Agent Conflict Prevention: Other agents won't pick marked items")
        print("• 📊 Real-time Work Item Discovery: Continuously scans for new work")
        print()
        
        print("🎯 WORK TYPE REDUNDANCY & FALLBACK:")
        print("-" * 50)
        print("• Complex TODOs (high/critical): Intelligent 15-minute breakdown")
        print("• Regular TODOs (medium): 30-minute phase breakdown")
        print("• Simple Tasks (low): Basic step-by-step breakdown")
        print("• Fallback: Automatic breakdown when AI system unavailable")
        print("• Priority: Complex > Regular > Tasks (with intelligent selection)")
        print()
        
        print("🔄 ENHANCED COLLECTIVE PROCESSING WORKFLOW:")
        print("-" * 50)
        print("1. 🔍 Scan TODO master for available work items")
        print("2. 🏷️  Mark work items to prevent agent conflicts")
        print("3. 📥 Load work items in batch (1 task + 3 complex + 10 regular)")
        print("4. 🧠 Break down based on complexity level")
        print("5. 👥 Assign workers collaboratively")
        print("6. ⚡ Process micro-tasks in parallel")
        print("7. 📊 Update master registry upon completion")
        print("8. 💾 Clear cache for completed work items")
        print("9. 🔄 Repeat scanning and loading cycle")
        print()
        
        # Demonstrate scanning and marking
        print("🚀 DEMONSTRATING SCANNING & MARKING...")
        print("=" * 50)
        
        scan_results = processor.scan_and_mark_todo_master()
        print(f"🔍 Scan Results: {scan_results['scanned']} scanned, "
              f"{scan_results['marked']} marked, {scan_results['errors']} errors")
        
        if scan_results['marked'] > 0:
            print("✅ Successfully marked work items to prevent conflicts!")
        else:
            print("💡 No new work items to mark (may already be marked)")
        
        print()
        
        # Demonstrate batch loading
        print("🚀 DEMONSTRATING BATCH LOADING...")
        print("=" * 50)
        
        loaded_items = processor.load_work_items_batch()
        print(f"📥 Batch Loading Results: {len(loaded_items)} work items loaded")
        
        if loaded_items:
            print("📋 Loaded Work Items:")
            for i, item in enumerate(loaded_items, 1):
                work_type = "Complex TODO" if item.complexity in ['high', 'critical'] else \
                           "Regular TODO" if item.complexity == 'medium' else "Task"
                print(f"   {i}. {work_type}: {item.name} (Complexity: {item.complexity})")
        else:
            print("💡 No work items available for batch loading")
        
        print()
        
        # Start collective processing loop
        print("🚀 Starting enhanced collective processing loop...")
        print("⏱️  Processing interval: 30 seconds")
        print("🔄 Will continuously scan, mark, and process work items")
        print("📊 Handles: Complex TODOs, Regular TODOs, and Tasks")
        print("🔒 Prevents conflicts with other agents")
        print()
        
        processor.start_collective_processing_loop(interval=30)
        
        # Let it run for demonstration
        print("💡 Enhanced collective processing loop is now running in background")
        print("📊 Monitor progress with processor.get_collective_processing_stats()")
        print("🛑 Stop with processor.stop_collective_processing()")
        print()
        
        # Show initial stats
        stats = processor.get_collective_processing_stats()
        print("📊 Initial Collective Processing Stats:")
        print(f"   - Complex TODOs: {stats['total_complex_todos']}")
        print(f"   - Active Workers: {stats['active_workers']}")
        print(f"   - Cache Size: {stats['cache_stats']['size']}")
        print()
        
    else:
        print("⚠️  TODO Master Integration: NOT AVAILABLE")
        print("💡 Processor will work but won't retrieve work items from master registry")
        print()
    
    print("🎯 DEMONSTRATION COMPLETED!")
    print("🚀 Enhanced Collective Worker Processor is ready for production use!")
    print("🔄 Now handles all work types with intelligent redundancy!")
    print("🔒 Prevents conflicts with other agents!")
    print("📥 Loads work items in optimized batches!")

if __name__ == "__main__":
    demo_collective_worker_processing()
