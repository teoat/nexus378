#!/usr/bin/env python3
"""
🔧 ENHANCED WORKER POOL - NEXUS AUTOMATION PLATFORM 🔧
Advanced worker pool management with adaptive scaling and performance optimization
"""

import asyncio
import json
import logging
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import PriorityQueue, Queue
import multiprocessing

logger = logging.getLogger(__name__)

class AdaptiveWorkerPool:
    """Enhanced worker pool with adaptive scaling and performance optimization"""
    
    def __init__(self, min_workers=120, max_workers=200):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = min_workers
        self.adaptive_scaling = True
        self.performance_thresholds = {
            "cpu_usage": 0.8,
            "memory_usage": 0.85,
            "queue_depth": 100,
            "worker_efficiency": 0.9
        }
        
        # Performance monitoring
        self.performance_metrics = {
            "cpu_history": [],
            "memory_history": [],
            "queue_depth_history": [],
            "worker_efficiency_history": [],
            "scaling_events": []
        }
        
        # Worker pool management
        self.worker_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.active_workers = 0
        self.idle_workers = 0
        self.worker_stats = {}
        
        # Task queue management
        self.task_queue = PriorityQueue()
        self.processing_queue = Queue()
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        # Performance monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._performance_monitor, daemon=True)
        self.monitor_thread.start()
        
        print("🔧 Enhanced Worker Pool Initialized")
        print(f"✅ Min Workers: {self.min_workers}")
        print(f"✅ Max Workers: {self.max_workers}")
        print(f"✅ Adaptive Scaling: {self.adaptive_scaling}")
        print(f"✅ Performance Monitoring: ACTIVE")
    
    def _performance_monitor(self):
        """Continuous performance monitoring and auto-scaling"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent / 100
                queue_depth = self.task_queue.qsize()
                
                # Calculate worker efficiency
                if self.active_workers > 0:
                    worker_efficiency = self.completed_tasks / max(self.active_workers, 1)
                else:
                    worker_efficiency = 0
                
                # Store metrics
                self.performance_metrics["cpu_history"].append(cpu_percent)
                self.performance_metrics["memory_history"].append(memory_percent)
                self.performance_metrics["queue_depth_history"].append(queue_depth)
                self.performance_metrics["worker_efficiency_history"].append(worker_efficiency)
                
                # Keep only last 100 metrics
                for key in self.performance_metrics:
                    if len(self.performance_metrics[key]) > 100:
                        self.performance_metrics[key] = self.performance_metrics[key][-100:]
                
                # Auto-scaling logic
                if self.adaptive_scaling:
                    self._auto_scale_workers(cpu_percent, memory_percent, queue_depth, worker_efficiency)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(10)
    
    def _auto_scale_workers(self, cpu_percent, memory_percent, queue_depth, worker_efficiency):
        """Automatically scale workers based on performance metrics"""
        scaling_needed = False
        scaling_action = None
        
        # Scale up conditions
        if (cpu_percent < self.performance_thresholds["cpu_usage"] and
            memory_percent < self.performance_thresholds["memory_usage"] and
            queue_depth > self.performance_thresholds["queue_depth"] and
            self.current_workers < self.max_workers):
            
            new_workers = min(self.current_workers + 20, self.max_workers)
            if new_workers > self.current_workers:
                scaling_needed = True
                scaling_action = "scale_up"
                self.current_workers = new_workers
        
        # Scale down conditions
        elif (cpu_percent > 0.9 or memory_percent > 0.9 or
              queue_depth < 10 or worker_efficiency < 0.5):
            
            if self.current_workers > self.min_workers:
                scaling_needed = True
                scaling_action = "scale_down"
                self.current_workers = max(self.current_workers - 10, self.min_workers)
        
        # Apply scaling
        if scaling_needed:
            self._apply_worker_scaling(scaling_action)
            
            # Log scaling event
            scaling_event = {
                "timestamp": datetime.now().isoformat(),
                "action": scaling_action,
                "new_worker_count": self.current_workers,
                "metrics": {
                    "cpu": cpu_percent,
                    "memory": memory_percent,
                    "queue_depth": queue_depth,
                    "worker_efficiency": worker_efficiency
                }
            }
            self.performance_metrics["scaling_events"].append(scaling_event)
            
            print(f"🔄 Auto-scaling: {scaling_action} to {self.current_workers} workers")
    
    def _apply_worker_scaling(self, action):
        """Apply worker scaling by updating the thread pool"""
        try:
            # Create new thread pool with updated worker count
            old_pool = self.worker_pool
            self.worker_pool = ThreadPoolExecutor(max_workers=self.current_workers)
            
            # Gracefully shutdown old pool
            old_pool.shutdown(wait=False)
            
            print(f"✅ Worker scaling applied: {self.current_workers} workers active")
            
        except Exception as e:
            logger.error(f"Worker scaling error: {e}")
    
    def submit_task(self, task, priority=1):
        """Submit a task to the worker pool with priority"""
        self.task_queue.put((priority, time.time(), task))
        return True
    
    async def process_tasks(self, max_tasks=None):
        """Process tasks with enhanced worker management"""
        if max_tasks is None:
            max_tasks = self.current_workers * 2  # Process 2x worker capacity
        
        print(f"🚀 Processing {max_tasks} tasks with {self.current_workers} workers...")
        
        # Submit tasks to workers
        futures = []
        tasks_submitted = 0
        
        while not self.task_queue.empty() and tasks_submitted < max_tasks:
            try:
                priority, timestamp, task = self.task_queue.get_nowait()
                
                # Submit to worker pool
                future = self.worker_pool.submit(self._execute_task, task)
                futures.append(future)
                tasks_submitted += 1
                self.active_workers += 1
                
            except Exception as e:
                logger.error(f"Task submission error: {e}")
                break
        
        print(f"✅ Submitted {tasks_submitted} tasks to {self.current_workers} workers")
        
        # Wait for completion
        completed = 0
        for future in as_completed(futures):
            try:
                result = future.result()
                if result.get("success"):
                    completed += 1
                    self.completed_tasks += 1
                else:
                    self.failed_tasks += 1
                
                self.active_workers -= 1
                
            except Exception as e:
                logger.error(f"Task execution error: {e}")
                self.failed_tasks += 1
                self.active_workers -= 1
        
        # Update performance metrics
        success_rate = (self.completed_tasks / (self.completed_tasks + self.failed_tasks)) * 100 if (self.completed_tasks + self.failed_tasks) > 0 else 0
        
        print(f"✅ Batch completed: {completed}/{tasks_submitted} tasks")
        print(f"📊 Overall success rate: {success_rate:.1f}%")
        print(f"🔧 Active workers: {self.active_workers}/{self.current_workers}")
        
        return completed
    
    def _execute_task(self, task):
        """Execute a single task with enhanced error handling"""
        try:
            # Simulate task processing with variable complexity
            import random
            complexity = random.uniform(0.1, 0.5)
            time.sleep(complexity)
            
            # Random success/failure for demonstration
            success = random.random() > 0.05  # 95% success rate (improved from 90%)
            
            return {
                "success": success,
                "task_id": task.get("id", "unknown"),
                "result": f"Task {task.get('id', 'unknown')} {'completed' if success else 'failed'}",
                "execution_time": complexity,
                "worker_id": threading.current_thread().ident
            }
            
        except Exception as e:
            return {
                "success": False,
                "task_id": task.get("id", "unknown"),
                "error": str(e),
                "worker_id": threading.current_thread().ident
            }
    
    def get_performance_report(self):
        """Get comprehensive performance report"""
        if self.performance_metrics["cpu_history"]:
            avg_cpu = sum(self.performance_metrics["cpu_history"]) / len(self.performance_metrics["cpu_history"])
            avg_memory = sum(self.performance_metrics["memory_history"]) / len(self.performance_metrics["memory_history"])
            avg_queue_depth = sum(self.performance_metrics["queue_depth_history"]) / len(self.performance_metrics["queue_depth_history"])
        else:
            avg_cpu = avg_memory = avg_queue_depth = 0
        
        report = {
            "enhanced_worker_pool_report": {
                "timestamp": datetime.now().isoformat(),
                "current_workers": self.current_workers,
                "min_workers": self.min_workers,
                "max_workers": self.max_workers,
                "active_workers": self.active_workers,
                "idle_workers": self.idle_workers,
                "adaptive_scaling": self.adaptive_scaling,
                "performance_metrics": {
                    "average_cpu_usage": avg_cpu,
                    "average_memory_usage": avg_memory,
                    "average_queue_depth": avg_queue_depth,
                    "scaling_events_count": len(self.performance_metrics["scaling_events"])
                },
                "task_metrics": {
                    "completed_tasks": self.completed_tasks,
                    "failed_tasks": self.failed_tasks,
                    "success_rate": (self.completed_tasks / (self.completed_tasks + self.failed_tasks)) * 100 if (self.completed_tasks + self.failed_tasks) > 0 else 0
                }
            }
        }
        
        return report
    
    def shutdown(self):
        """Gracefully shutdown the enhanced worker pool"""
        print("🔄 Shutting down enhanced worker pool...")
        self.monitoring_active = False
        self.worker_pool.shutdown(wait=True)
        print("✅ Enhanced worker pool shutdown complete")

# Example usage and testing
async def test_enhanced_worker_pool():
    """Test the enhanced worker pool"""
    print("🧪 Testing Enhanced Worker Pool...")
    
    # Create enhanced worker pool
    pool = AdaptiveWorkerPool(min_workers=120, max_workers=200)
    
    # Submit test tasks
    for i in range(100):
        task = {"id": f"test_task_{i}", "priority": 1}
        pool.submit_task(task)
    
    # Process tasks
    await pool.process_tasks(max_tasks=50)
    
    # Get performance report
    report = pool.get_performance_report()
    print("\n📊 Enhanced Worker Pool Performance Report:")
    print(json.dumps(report, indent=2))
    
    # Shutdown
    pool.shutdown()

if __name__ == "__main__":
    asyncio.run(test_enhanced_worker_pool())
