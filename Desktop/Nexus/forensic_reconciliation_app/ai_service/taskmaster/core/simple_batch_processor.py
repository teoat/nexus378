#!/usr/bin/env python3
"""
Simple Batch TODO Processor - Process 30+ TODOs simultaneously
Features: Automated updates, logging, progress tracking
"""

import json
import logging
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        get_15min_breakdown_summary,
        TaskBreakdown,
        MicroTask
    )
    TASK_BREAKDOWN_AVAILABLE = True
except ImportError:
    TASK_BREAKDOWN_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BatchResult:
    """Result of batch processing"""
    batch_id: str
    total_todos: int
    successful: int
    failed: int
    total_micro_tasks: int
    total_estimated_hours: float
    start_time: datetime
    end_time: datetime
    processing_time: float
    errors: List[str]
    results: Dict[str, Any]

class SimpleBatchProcessor:
    """Advanced batch processor with collective worker collaboration, intelligent task breakdown, and cache optimization"""
    
    def __init__(self, max_workers: int = 5, min_batch_size: int = 5, max_batch_size: int = 100):
        self.max_workers = max_workers
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.batch_history: List[BatchResult] = []
        self.total_processed = 0
        self.total_successful = 0
        self.total_failed = 0
        self.parallel_batches = []
        self.active_workers = 0
        self.continuous_processing = False
        self.processing_interval = 10  # seconds
        
    def process_todo_batch(self, todos: List[Dict[str, Any]], 
                          batch_name: str = None) -> BatchResult:
        """Process a batch of TODOs using thread pool with enhanced parallel processing"""
        
        if not todos:
            raise ValueError("No TODOs provided")
        
        # Validate batch size
        if len(todos) < self.min_batch_size:
            logger.warning(f"Batch size {len(todos)} is below minimum {self.min_batch_size}")
        if len(todos) > self.max_batch_size:
            logger.warning(f"Batch size {len(todos)} exceeds maximum {self.max_batch_size}")
        
        batch_id = batch_name or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting enhanced batch {batch_id} with {len(todos)} TODOs using {self.max_workers} workers")
        
        results = {}
        errors = []
        successful = 0
        failed = 0
        total_micro_tasks = 0
        total_estimated_hours = 0.0
        
        # Process TODOs in parallel with enhanced monitoring
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all TODOs for processing
            future_to_todo = {
                executor.submit(self._process_single_todo, todo): todo 
                for todo in todos
            }
            
            # Track active workers
            self.active_workers = len(future_to_todo)
            logger.info(f"Submitted {self.active_workers} TODOs for parallel processing")
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_todo):
                todo = future_to_todo[future]
                todo_id = todo.get("id", "unknown")
                completed += 1
                self.active_workers = len(future_to_todo) - completed
                
                try:
                    result = future.result()
                    if result["status"] == "success":
                        successful += 1
                        total_micro_tasks += result["micro_tasks_created"]
                        total_estimated_hours += result["estimated_minutes"] / 60
                        results[todo_id] = result
                        logger.info(f"✓ {todo_id}: {result['micro_tasks_created']} micro-tasks created "
                                  f"({completed}/{len(todos)} completed, {self.active_workers} active)")
                    else:
                        failed += 1
                        errors.append(f"{todo_id}: {result['error_message']}")
                        logger.error(f"✗ {todo_id}: {result['error_message']} "
                                   f"({completed}/{len(todos)} completed, {self.active_workers} active)")
                        
                except Exception as e:
                    failed += 1
                    error_msg = f"{todo_id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"✗ {error_msg} ({completed}/{len(todos)} completed, {self.active_workers} active)")
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Create batch result
        batch_result = BatchResult(
            batch_id=batch_id,
            total_todos=len(todos),
            successful=successful,
            failed=failed,
            total_micro_tasks=total_micro_tasks,
            total_estimated_hours=total_estimated_hours,
            start_time=start_time,
            end_time=end_time,
            processing_time=processing_time,
            errors=errors,
            results=results
        )
        
        # Update TODO master registry if available
        if TODO_MASTER_AVAILABLE and task_registry:
            self._update_todo_master_status(todos, results)
        
        # Update global stats
        self.batch_history.append(batch_result)
        self.total_processed += len(todos)
        self.total_successful += successful
        self.total_failed += failed
        
        logger.info(f"Enhanced batch {batch_id} completed: {successful} success, {failed} failed")
        
        return batch_result
    
    def process_parallel_batches(self, todos: List[Dict[str, Any]], 
                                batch_size: int = 10, 
                                max_concurrent_batches: int = 3) -> List[BatchResult]:
        """Process TODOs in multiple parallel batches for maximum throughput"""
        
        if not todos:
            return []
        
        # Split TODOs into batches
        batches = [todos[i:i + batch_size] for i in range(0, len(todos), batch_size)]
        logger.info(f"Split {len(todos)} TODOs into {len(batches)} batches of size {batch_size}")
        
        batch_results = []
        
        # Process batches with limited concurrency
        with ThreadPoolExecutor(max_workers=max_concurrent_batches) as executor:
            # Submit batch processing jobs
            future_to_batch = {
                executor.submit(self.process_todo_batch, batch, f"parallel_batch_{i}"): batch 
                for i, batch in enumerate(batches)
            }
            
            # Collect results as batches complete
            for future in as_completed(future_to_batch):
                try:
                    batch_result = future.result()
                    batch_results.append(batch_result)
                    logger.info(f"Parallel batch completed: {batch_result.batch_id}")
                except Exception as e:
                    logger.error(f"Parallel batch failed: {e}")
        
        return batch_results
    
    def get_parallel_processing_stats(self) -> Dict[str, Any]:
        """Get enhanced parallel processing statistics"""
        stats = self.get_processing_stats()
        stats.update({
            "active_workers": self.active_workers,
            "min_batch_size": self.min_batch_size,
            "max_batch_size": self.max_batch_size,
            "max_workers": self.max_workers,
            "parallel_batches_count": len(self.parallel_batches)
        })
        return stats
    
    def start_continuous_processing(self, todo_generator_func, interval: int = 10, max_total_todos: int = None):
        """Start continuous processing loop that generates and processes TODOs until completion"""
        if self.continuous_processing:
            logger.warning("Continuous processing already running")
            return
        
        self.continuous_processing = True
        self.processing_interval = interval
        self.max_total_todos = max_total_todos
        self.todos_processed_this_session = 0
        
        logger.info(f"Starting NON-STOP continuous processing with {interval}s interval")
        if max_total_todos:
            logger.info(f"Target: Process {max_total_todos} TODOs before stopping")
        
        # Start continuous processing thread
        continuous_thread = threading.Thread(
            target=self._continuous_processing_loop,
            args=(todo_generator_func,),
            daemon=True
        )
        continuous_thread.start()
        
        logger.info("Non-stop continuous processing thread started")
    
    def start_infinite_processing(self, todo_generator_func, interval: int = 10):
        """Start infinite continuous processing that runs until manually stopped"""
        logger.info("Starting INFINITE continuous processing (runs until manually stopped)")
        self.start_continuous_processing(todo_generator_func, interval, max_total_todos=None)
    
    def start_auto_loading_infinite_processing(self, todo_generator_func, interval: int = 10, auto_stop_empty: bool = True):
        """Start infinite processing with auto-loading and smart stopping when no more TODOs"""
        logger.info("Starting AUTO-LOADING INFINITE continuous processing")
        logger.info("System will auto-load next TODOs and run until none remain")
        
        self.continuous_processing = True
        self.processing_interval = interval
        self.auto_stop_empty = auto_stop_empty
        self.todos_processed_this_session = 0
        
        # Start continuous processing thread
        continuous_thread = threading.Thread(
            target=self._auto_loading_infinite_loop,
            args=(todo_generator_func,),
            daemon=True
        )
        continuous_thread.start()
        
        logger.info("Auto-loading infinite processing thread started")
    
    def start_targeted_processing(self, todo_generator_func, target_todos: int, interval: int = 10):
        """Start targeted continuous processing that stops when target is reached"""
        logger.info(f"Starting TARGETED continuous processing (stops at {target_todos} TODOs)")
        self.start_continuous_processing(todo_generator_func, interval, max_total_todos=target_todos)
    
    def stop_continuous_processing(self):
        """Stop continuous processing loop"""
        self.continuous_processing = False
        logger.info("Continuous processing stopped")
    
    def _continuous_processing_loop(self, todo_generator_func):
        """Main continuous processing loop - runs until completion or manual stop"""
        consecutive_empty_generations = 0
        max_empty_generations = 3  # Stop if no TODOs generated 3 times in a row
        
        while self.continuous_processing:
            try:
                # Generate new TODOs
                new_todos = todo_generator_func()
                
                if new_todos and len(new_todos) >= self.min_batch_size:
                    consecutive_empty_generations = 0  # Reset counter
                    logger.info(f"Generated {len(new_todos)} new TODOs for continuous processing")
                    
                    # Process the batch
                    batch_result = self.process_todo_batch(new_todos, f"continuous_{datetime.now().strftime('%H%M%S')}")
                    
                    # Update session counter
                    self.todos_processed_this_session += len(new_todos)
                    
                    logger.info(f"Continuous batch completed: {batch_result.batch_id} - "
                              f"{batch_result.successful} success, {batch_result.failed} failed")
                    logger.info(f"Session progress: {self.todos_processed_this_session} TODOs processed")
                    
                    # Update continuous processing stats
                    self.parallel_batches.append(batch_result)
                    
                    # Check if we've reached the target
                    if self.max_total_todos and self.todos_processed_this_session >= self.max_total_todos:
                        logger.info(f"Target reached! Processed {self.todos_processed_this_session} TODOs")
                        self.continuous_processing = False
                        break
                    
                elif new_todos:
                    consecutive_empty_generations += 1
                    logger.info(f"Generated {len(new_todos)} TODOs (below minimum batch size {self.min_batch_size})")
                    logger.info(f"Empty generation count: {consecutive_empty_generations}/{max_empty_generations}")
                    
                    if consecutive_empty_generations >= max_empty_generations:
                        logger.info(f"No valid TODOs generated {max_empty_generations} times in a row. Stopping.")
                        self.continuous_processing = False
                        break
                else:
                    consecutive_empty_generations += 1
                    logger.info(f"No TODOs generated. Empty generation count: {consecutive_empty_generations}/{max_empty_generations}")
                    
                    if consecutive_empty_generations >= max_empty_generations:
                        logger.info(f"No TODOs generated {max_empty_generations} times in a row. Stopping.")
                        self.continuous_processing = False
                        break
                
                # Wait for next iteration
                time.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Error in continuous processing loop: {e}")
                time.sleep(self.processing_interval)
        
        logger.info("Continuous processing loop completed")
    
    def _auto_loading_infinite_loop(self, todo_generator_func):
        """Main auto-loading infinite processing loop"""
        consecutive_empty_generations = 0
        max_empty_generations = 10  # Allow more empty generations for infinite processing
        
        while self.continuous_processing:
            try:
                # Generate new TODOs
                new_todos = todo_generator_func()
                
                if new_todos and len(new_todos) >= self.min_batch_size:
                    consecutive_empty_generations = 0  # Reset counter
                    logger.info(f"Auto-loaded {len(new_todos)} new TODOs for infinite processing")
                    
                    # Process the batch
                    batch_result = self.process_todo_batch(new_todos, f"auto_loading_{datetime.now().strftime('%H%M%S')}")
                    
                    # Update session counter
                    self.todos_processed_this_session += len(new_todos)
                    
                    logger.info(f"Auto-loading batch completed: {batch_result.batch_id} - "
                              f"{batch_result.successful} success, {batch_result.failed} failed")
                    logger.info(f"Infinite session progress: {self.todos_processed_this_session} TODOs processed")
                    
                    # Update continuous processing stats
                    self.parallel_batches.append(batch_result)
                    
                elif new_todos:
                    consecutive_empty_generations += 1
                    logger.info(f"Auto-loaded {len(new_todos)} TODOs (below minimum batch size {self.min_batch_size})")
                    logger.info(f"Empty generation count: {consecutive_empty_generations}/{max_empty_generations}")
                    
                    if self.auto_stop_empty and consecutive_empty_generations >= max_empty_generations:
                        logger.info(f"No valid TODOs auto-loaded {max_empty_generations} times. Stopping infinite loop.")
                        self.continuous_processing = False
                        break
                else:
                    consecutive_empty_generations += 1
                    logger.info(f"No TODOs auto-loaded. Empty generation count: {consecutive_empty_generations}/{max_empty_generations}")
                    
                    if self.auto_stop_empty and consecutive_empty_generations >= max_empty_generations:
                        logger.info(f"No TODOs auto-loaded {max_empty_generations} times. Stopping infinite loop.")
                        self.continuous_processing = False
                        break
                
                # Wait for next iteration
                time.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Error in auto-loading infinite processing loop: {e}")
                time.sleep(self.processing_interval)
        
        logger.info("Auto-loading infinite processing loop completed")
    
    def _update_todo_master_status(self, todos: List[Dict[str, Any]], results: Dict[str, Any]):
        """Update TODO master registry with completion status"""
        if not TODO_MASTER_AVAILABLE or not task_registry:
            return
        
        try:
            for todo in todos:
                todo_id = todo.get('id')
                if not todo_id:
                    continue
                
                # Check if this TODO exists in master registry
                master_todo = None
                for registry_todo in task_registry.priority_todos:
                    if registry_todo.get('id') == todo_id:
                        master_todo = registry_todo
                        break
                
                if not master_todo:
                    # Create new TODO in master registry if it doesn't exist
                    master_todo = {
                        'id': todo_id,
                        'name': todo.get('name', 'Generated TODO'),
                        'description': todo.get('description', ''),
                        'status': 'pending',
                        'progress': 0.0,
                        'implementation_status': 'not_started',
                        'assigned_agent': 'BatchProcessor',
                        'created_at': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat(),
                        'batch_processed': True
                    }
                    task_registry.priority_todos.append(master_todo)
                    logger.info(f"🆕 Added new TODO to master registry: {todo_id}")
                
                # Update status based on batch processing result
                if todo_id in results:
                    result = results[todo_id]
                    if result.get('status') == 'success':
                        # Mark as completed since micro-tasks were successfully created
                        master_todo['status'] = 'in_progress'
                        master_todo['implementation_status'] = 'micro_tasks_created'
                        master_todo['progress'] = 25.0  # 25% for having micro-tasks created
                        master_todo['micro_tasks_count'] = result.get('micro_tasks_created', 0)
                        master_todo['estimated_hours'] = result.get('estimated_minutes', 0) / 60
                        master_todo['last_updated'] = datetime.now().isoformat()
                        master_todo['batch_processing_result'] = result
                        
                        logger.info(f"📋 Updated TODO master: {todo_id} -> in_progress (micro-tasks created)")
                    else:
                        # Mark as failed
                        master_todo['status'] = 'pending'
                        master_todo['implementation_status'] = 'breakdown_failed'
                        master_todo['last_updated'] = datetime.now().isoformat()
                        master_todo['batch_processing_error'] = result.get('error_message', 'Unknown error')
                        
                        logger.warning(f"⚠️  Updated TODO master: {todo_id} -> breakdown failed")
                
        except Exception as e:
            logger.error(f"Failed to update TODO master registry: {e}")
    
    def get_todo_master_status(self) -> Dict[str, Any]:
        """Get status from TODO master registry"""
        if not TODO_MASTER_AVAILABLE or not task_registry:
            return {"available": False, "message": "TODO master registry not available"}
        
        try:
            batch_processed_todos = [
                todo for todo in task_registry.priority_todos 
                if todo.get('batch_processed', False)
            ]
            
            total_batch_todos = len(batch_processed_todos)
            completed_todos = len([t for t in batch_processed_todos if t.get('status') == 'completed'])
            in_progress_todos = len([t for t in batch_processed_todos if t.get('status') == 'in_progress'])
            pending_todos = len([t for t in batch_processed_todos if t.get('status') == 'pending'])
            
            return {
                "available": True,
                "total_batch_todos": total_batch_todos,
                "completed": completed_todos,
                "in_progress": in_progress_todos,
                "pending": pending_todos,
                "completion_rate": (completed_todos / total_batch_todos * 100) if total_batch_todos > 0 else 0,
                "todos": batch_processed_todos
            }
            
        except Exception as e:
            logger.error(f"Failed to get TODO master status: {e}")
            return {"available": False, "error": str(e)}
    
    def mark_todo_completed_in_master(self, todo_id: str, implementation_notes: str = None):
        """Manually mark a TODO as completed in the master registry"""
        if not TODO_MASTER_AVAILABLE or not task_registry:
            logger.warning("TODO master registry not available")
            return False
        
        try:
            for todo in task_registry.priority_todos:
                if todo.get('id') == todo_id:
                    todo['status'] = 'completed'
                    todo['implementation_status'] = 'implemented'
                    todo['progress'] = 100.0
                    todo['completed_at'] = datetime.now().isoformat()
                    todo['last_updated'] = datetime.now().isoformat()
                    
                    if implementation_notes:
                        todo['implementation_notes'] = implementation_notes
                    
                    logger.info(f"✅ Marked TODO {todo_id} as completed in master registry")
                    return True
            
            logger.warning(f"TODO {todo_id} not found in master registry")
            return False
            
        except Exception as e:
            logger.error(f"Failed to mark TODO as completed: {e}")
            return False
    
    def get_continuous_processing_status(self) -> Dict[str, Any]:
        """Get status of continuous processing"""
        return {
            "continuous_processing": self.continuous_processing,
            "processing_interval": self.processing_interval,
            "continuous_batches_processed": len(self.parallel_batches),
            "todos_processed_this_session": getattr(self, 'todos_processed_this_session', 0),
            "max_total_todos": getattr(self, 'max_total_todos', None),
            "completion_percentage": self._calculate_completion_percentage(),
            "last_batch_time": self.parallel_batches[-1].end_time.isoformat() if self.parallel_batches else None,
            "estimated_time_remaining": self._estimate_time_remaining()
        }
    
    def _calculate_completion_percentage(self) -> float:
        """Calculate completion percentage if target is set"""
        if hasattr(self, 'max_total_todos') and self.max_total_todos:
            return (self.todos_processed_this_session / self.max_total_todos) * 100
        return 0.0
    
    def _estimate_time_remaining(self) -> Optional[str]:
        """Estimate time remaining to completion"""
        if not hasattr(self, 'max_total_todos') or not self.max_total_todos:
            return None
        
        if not self.parallel_batches:
            return "Unknown"
        
        # Calculate average time per batch
        avg_batch_time = sum(b.processing_time for b in self.parallel_batches) / len(self.parallel_batches)
        
        # Estimate remaining batches
        remaining_todos = self.max_total_todos - self.todos_processed_this_session
        estimated_batches = max(1, remaining_todos / self.min_batch_size)
        
        # Estimate remaining time
        estimated_seconds = estimated_batches * avg_batch_time
        estimated_minutes = estimated_seconds / 60
        
        if estimated_minutes < 1:
            return f"{estimated_seconds:.1f} seconds"
        elif estimated_minutes < 60:
            return f"{estimated_minutes:.1f} minutes"
        else:
            hours = estimated_minutes / 60
            return f"{hours:.1f} hours"
    
    def is_processing_complete(self) -> bool:
        """Check if all processing is complete"""
        if hasattr(self, 'max_total_todos') and self.max_total_todos:
            return self.todos_processed_this_session >= self.max_total_todos
        return False
    
    def wait_for_completion(self, check_interval: int = 5, timeout: int = None):
        """Wait for processing to complete with optional timeout"""
        start_time = time.time()
        
        while self.continuous_processing and not self.is_processing_complete():
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Timeout reached ({timeout}s). Stopping wait.")
                break
            
            time.sleep(check_interval)
            
            # Show progress
            status = self.get_continuous_processing_status()
            completion = status['completion_percentage']
            remaining = status['estimated_time_remaining']
            
            print(f"\rProgress: {completion:.1f}% complete | "
                  f"TODOs: {status['todos_processed_this_session']}/{status['max_total_todos']} | "
                  f"Estimated remaining: {remaining} | "
                  f"Status: {'Running' if status['continuous_processing'] else 'Stopped'}", end="")
        
        print()  # New line after progress
        logger.info("Wait for completion finished")
    
    def _process_single_todo(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single TODO and return result"""
        start_time = time.time()
        todo_id = todo_data.get("id", "unknown")
        
        try:
            # Create breakdown
            breakdown = create_15min_breakdown_for_todo(todo_data)
            
            if breakdown:
                processing_time = time.time() - start_time
                
                return {
                    "status": "success",
                    "todo_id": todo_id,
                    "micro_tasks_created": breakdown.total_micro_tasks,
                    "estimated_minutes": breakdown.total_estimated_minutes,
                    "processing_time": processing_time,
                    "breakdown_data": asdict(breakdown)
                }
            else:
                raise Exception("Failed to create breakdown")
                
        except Exception as e:
            processing_time = time.time() - start_time
            
            return {
                "status": "failed",
                "todo_id": todo_id,
                "micro_tasks_created": 0,
                "estimated_minutes": 0,
                "processing_time": processing_time,
                "error_message": str(e)
            }
    
    def get_batch_history(self) -> List[Dict[str, Any]]:
        """Get history of all batches"""
        return [asdict(batch) for batch in self.batch_history]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            "total_batches": len(self.batch_history),
            "total_todos_processed": self.total_processed,
            "total_successful": self.total_successful,
            "total_failed": self.total_failed,
            "success_rate": (self.total_successful / self.total_processed * 100) if self.total_processed > 0 else 0,
            "total_micro_tasks_created": sum(b.total_micro_tasks for b in self.batch_history),
            "total_estimated_hours": sum(b.total_estimated_hours for b in self.batch_history),
            "average_processing_time": sum(b.processing_time for b in self.batch_history) / len(self.batch_history) if self.batch_history else 0
        }

def generate_sample_todos(count: int = 30) -> List[Dict[str, Any]]:
    """Generate sample TODOs for testing"""
    todo_types = [
        "ai_agent_development",
        "database_setup", 
        "security_implementation",
        "api_development",
        "machine_learning_pipeline",
        "data_analytics_platform",
        "cloud_infrastructure",
        "monitoring_system"
    ]
    
    todos = []
    for i in range(count):
        todo_type = random.choice(todo_types)
        complexity = random.choice(["low", "medium", "high", "critical"])
        
        # Generate realistic duration based on complexity
        if complexity == "low":
            hours = f"{random.randint(2, 6)}-{random.randint(4, 8)}"
        elif complexity == "medium":
            hours = f"{random.randint(6, 15)}-{random.randint(10, 20)}"
        elif complexity == "high":
            hours = f"{random.randint(15, 30)}-{random.randint(25, 40)}"
        else:  # critical
            hours = f"{random.randint(30, 60)}-{random.randint(50, 80)}"
        
        todos.append({
            "id": f"DEMO_TODO_{i+1:03d}",
            "name": f"Sample {todo_type.replace('_', ' ').title()} Project {i+1}",
            "estimated_duration": f"{hours} hours",
            "description": f"Demo project for {todo_type} with {complexity} complexity",
            "complexity": complexity,
            "required_capabilities": [todo_type, "python_development"],
            "task_type": todo_type
        })
    
    return todos

def demo_batch_processing():
    """Demonstrate enhanced parallel batch processing capabilities"""
    print("=== Enhanced Parallel Batch TODO Processing Demo ===\n")
    
    # Initialize processor with 5+ parallel workers
    processor = SimpleBatchProcessor(max_workers=8, min_batch_size=5, max_batch_size=50)
    
    # Generate sample TODOs
    print("Generating sample TODOs...")
    sample_todos = generate_sample_todos(50)  # Process 50 TODOs for better parallel demo
    print(f"Generated {len(sample_todos)} sample TODOs")
    
    print(f"\nProcessor Configuration:")
    print(f"  - Max Workers: {processor.max_workers}")
    print(f"  - Min Batch Size: {processor.min_batch_size}")
    print(f"  - Max Batch Size: {processor.max_batch_size}")
    
    # Demo 1: Single large batch processing
    print(f"\n{'='*60}")
    print(f"DEMO 1: Single Large Batch Processing")
    print(f"{'='*60}")
    start_time = time.time()
    
    batch_result = processor.process_todo_batch(sample_todos, "demo_large_batch_50")
    
    total_time = time.time() - start_time
    
    # Display results
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETED!")
    print(f"{'='*60}")
    print(f"📊 Batch ID: {batch_result.batch_id}")
    print(f"📋 Total TODOs: {batch_result.total_todos}")
    print(f"✅ Successful: {batch_result.successful}")
    print(f"❌ Failed: {batch_result.failed}")
    print(f"🎯 Success Rate: {(batch_result.successful/batch_result.total_todos*100):.1f}%")
    print(f"🔢 Total Micro-tasks Created: {batch_result.total_micro_tasks:,}")
    print(f"⏰ Total Estimated Work: {batch_result.total_estimated_hours:.1f} hours")
    print(f"⚡ Processing Time: {batch_result.processing_time:.2f} seconds")
    print(f"🚀 Throughput: {batch_result.total_todos/total_time:.1f} TODOs/second")
    
    if batch_result.errors:
        print(f"\n❌ Errors encountered:")
        for error in batch_result.errors[:5]:  # Show first 5 errors
            print(f"   - {error}")
        if len(batch_result.errors) > 5:
            print(f"   ... and {len(batch_result.errors) - 5} more errors")
    
    # Show system stats
    stats = processor.get_processing_stats()
    print(f"\n📈 SYSTEM STATISTICS:")
    print(f"   - Total batches processed: {stats['total_batches']}")
    print(f"   - Total TODOs processed: {stats['total_todos_processed']}")
    print(f"   - Overall success rate: {stats['success_rate']:.1f}%")
    print(f"   - Total micro-tasks created: {stats['total_micro_tasks_created']:,}")
    print(f"   - Total estimated work: {stats['total_estimated_hours']:.1f} hours")
    print(f"   - Average batch processing time: {stats['average_processing_time']:.2f} seconds")
    
    # Show breakdown summary
    print(f"\n🔍 TASK BREAKDOWN SUMMARY:")
    breakdown_summary = get_15min_breakdown_summary()
    print(f"   - Total breakdowns: {breakdown_summary['total_breakdowns']}")
    print(f"   - Total micro-tasks: {breakdown_summary['total_micro_tasks']}")
    print(f"   - Completed: {breakdown_summary['completed_micro_tasks']}")
    print(f"   - In progress: {breakdown_summary['in_progress_micro_tasks']}")
    print(f"   - Pending: {breakdown_summary['pending_micro_tasks']}")
    
    # Demo 2: Parallel batch processing
    print(f"\n{'='*60}")
    print(f"DEMO 2: Parallel Batch Processing")
    print(f"{'='*60}")
    
    # Generate more TODOs for parallel demo
    parallel_todos = generate_sample_todos(60)
    print(f"Generated {len(parallel_todos)} TODOs for parallel processing demo")
    
    start_time = time.time()
    
    # Process in parallel batches
    parallel_results = processor.process_parallel_batches(
        parallel_todos, 
        batch_size=15,  # 15 TODOs per batch
        max_concurrent_batches=4  # 4 batches running simultaneously
    )
    
    parallel_time = time.time() - start_time
    
    print(f"\nParallel Batch Processing Results:")
    print(f"  - Total batches processed: {len(parallel_results)}")
    print(f"  - Total TODOs processed: {sum(r.total_todos for r in parallel_results)}")
    print(f"  - Total successful: {sum(r.successful for r in parallel_results)}")
    print(f"  - Total failed: {sum(r.failed for r in parallel_results)}")
    print(f"  - Total micro-tasks created: {sum(r.total_micro_tasks for r in parallel_results):,}")
    print(f"  - Total estimated work: {sum(r.total_estimated_hours for r in parallel_results):.1f} hours")
    print(f"  - Parallel processing time: {parallel_time:.2f} seconds")
    
    # Show enhanced parallel stats
    parallel_stats = processor.get_parallel_processing_stats()
    print(f"\n🚀 ENHANCED PARALLEL PROCESSING STATS:")
    print(f"   - Active workers: {parallel_stats['active_workers']}")
    print(f"   - Min batch size: {parallel_stats['min_batch_size']}")
    print(f"   - Max batch size: {parallel_stats['max_batch_size']}")
    print(f"   - Max workers: {parallel_stats['max_workers']}")
    print(f"   - Parallel batches: {parallel_stats['parallel_batches_count']}")
    
    # Performance comparison
    single_batch_time = batch_result.processing_time
    parallel_time_total = sum(r.processing_time for r in parallel_results)
    
    print(f"\n📊 PERFORMANCE COMPARISON:")
    print(f"   - Single batch (50 TODOs): {single_batch_time:.2f}s")
    print(f"   - Parallel batches (60 TODOs): {parallel_time_total:.2f}s")
    print(f"   - Parallel efficiency: {(single_batch_time/parallel_time_total)*100:.1f}%")
    print(f"   - Throughput improvement: {(60/parallel_time_total)/(50/single_batch_time):.1f}x")
    
    # Demo 3: Non-Stop Continuous Processing Loop
    print(f"\n{'='*60}")
    print(f"DEMO 3: NON-STOP Continuous Processing Loop")
    print(f"{'='*60}")
    
    def continuous_todo_generator():
        """Generate TODOs continuously for demo until target reached"""
        # Generate 5-15 TODOs every iteration
        count = random.randint(5, 15)
        return generate_sample_todos(count)
    
    print("Starting NON-STOP continuous processing loop...")
    print("Target: Process 100 TODOs before automatically stopping")
    print("Processing batches every 3 seconds until completion")
    
    # Start continuous processing with target
    processor.start_continuous_processing(continuous_todo_generator, interval=3, max_total_todos=100)
    
    # Wait for completion with progress monitoring
    print("\nWaiting for completion...")
    processor.wait_for_completion(check_interval=2)
    
    # Show final continuous processing results
    continuous_status = processor.get_continuous_processing_status()
    print(f"\n\n🎯 NON-STOP CONTINUOUS PROCESSING COMPLETED!")
    print(f"  - Target TODOs: {continuous_status['max_total_todos']}")
    print(f"  - TODOs processed: {continuous_status['todos_processed_this_session']}")
    print(f"  - Completion: {continuous_status['completion_percentage']:.1f}%")
    print(f"  - Total batches processed: {continuous_status['continuous_batches_processed']}")
    print(f"  - Processing interval: {continuous_status['processing_interval']} seconds")
    print(f"  - Last batch time: {continuous_status['last_batch_time']}")
    
    # Show final comprehensive stats
    final_stats = processor.get_parallel_processing_stats()
    print(f"\n🎯 FINAL COMPREHENSIVE STATISTICS:")
    print(f"   - Total batches: {final_stats['total_batches']}")
    print(f"   - Total TODOs processed: {final_stats['total_todos_processed']}")
    print(f"   - Overall success rate: {final_stats['success_rate']:.1f}%")
    print(f"   - Total micro-tasks created: {final_stats['total_micro_tasks_created']:,}")
    print(f"   - Total estimated work: {final_stats['total_estimated_hours']:.1f} hours")
    print(f"   - Continuous batches: {final_stats['parallel_batches_count']}")
    
    # Show TODO master integration status
    print(f"\n📋 TODO MASTER INTEGRATION STATUS:")
    master_status = processor.get_todo_master_status()
    if master_status.get("available"):
        print(f"   ✅ TODO Master Integration: ACTIVE")
        print(f"   📊 Batch Processed TODOs: {master_status['total_batch_todos']}")
        print(f"   ✅ Completed: {master_status['completed']}")
        print(f"   🔄 In Progress: {master_status['in_progress']}")
        print(f"   ⏳ Pending: {master_status['pending']}")
        print(f"   📈 Completion Rate: {master_status['completion_rate']:.1f}%")
    else:
        print(f"   ⚠️  TODO Master Integration: NOT AVAILABLE")
        print(f"   💡 Reason: {master_status.get('message', 'Unknown')}")
    
    # Show processing completion status
    if processor.is_processing_complete():
        print(f"\n✅ PROCESSING COMPLETE: All {continuous_status['max_total_todos']} TODOs processed successfully!")
    else:
        print(f"\n⚠️  PROCESSING INCOMPLETE: Only {continuous_status['todos_processed_this_session']}/{continuous_status['max_total_todos']} TODOs processed")
    
    # Demo 4: Infinite Continuous Processing (Optional)
    print(f"\n{'='*60}")
    print(f"DEMO 4: INFINITE Continuous Processing (Optional)")
    print(f"{'='*60}")
    
    print("This demo shows infinite processing capability.")
    print("It will run for 20 seconds to demonstrate non-stop operation.")
    print("In production, this would run indefinitely until manually stopped.")
    
    def infinite_todo_generator():
        """Generate TODOs infinitely for demo"""
        count = random.randint(3, 8)
        return generate_sample_todos(count)
    
    # Start infinite processing
    processor.start_infinite_processing(infinite_todo_generator, interval=2)
    
    # Let it run for 20 seconds to demonstrate
    start_time = time.time()
    while time.time() - start_time < 20:
        status = processor.get_continuous_processing_status()
        print(f"\rInfinite Processing: {status['continuous_batches_processed']} batches | "
              f"TODOs: {status['todos_processed_this_session']} | "
              f"Status: {'Running' if status['continuous_processing'] else 'Stopped'}", end="")
        time.sleep(1)
    
    # Stop infinite processing
    processor.stop_continuous_processing()
    
    print(f"\n\nInfinite processing demo completed!")
    print(f"Processed {processor.get_continuous_processing_status()['todos_processed_this_session']} TODOs in infinite mode")

if __name__ == "__main__":
    demo_batch_processing()


