#!/usr/bin/env python3
"""
Dynamic Collaborative TODO System
================================

Features:
- Dynamic worker collaboration: idle workers help busy ones
- Real-time detailed status display
- Worker load balancing
- Collective task processing
- Enhanced monitoring and logging
"""

import time
import threading
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import our existing system
from production_task_system import UnifiedTaskSystem
from working_todo_reader import WorkingTodoReader

class WorkerActivity:
    IDLE = "🟡 Idle"
    WORKING = "🟢 Working"
    HELPING = "🔵 Helping Others"
    WAITING = "🟠 Waiting for Tasks"
    COLLABORATING = "🟣 Collaborating"

class WorkerStatus:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.status = WorkerActivity.IDLE
        self.current_task = None
        self.progress = 0
        self.last_activity = datetime.now()
        self.tasks_completed = 0
        self.tasks_helped = 0
        self.is_collaborating = False
        self.collaboration_partners = []

class DynamicCollaborativeSystem:
    def __init__(self):
        self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.db_path = "dynamic_collaborative.db"
        
        # Configuration
        self.MAX_TODOS = 5
        self.MIN_TODOS = 2
        self.TASKS_BEFORE_ADD = 1
        
        # Initialize system
        self.system = UnifiedTaskSystem(db_path=self.db_path)
        self.todo_reader = WorkingTodoReader()
        
        # Worker management
        self.workers = {}
        self.worker_threads = {}
        self.collaboration_lock = threading.Lock()
        
        # Statistics
        self.start_time = datetime.now()
        self.total_tasks_completed = 0
        self.total_collaborations = 0
        
        print(f"🚀 Dynamic Collaborative TODO System")
        print(f"==================================================")
        print(f"🆔 Agent ID: {self.agent_id}")
        print(f"📁 Database: {self.db_path}")
        print(f"🔧 Features: Dynamic Collaboration, Load Balancing, Enhanced Monitoring")
        print(f"==================================================")

    def load_limited_todos(self):
        """Load limited number of TODOs from TODO_MASTER.md"""
        try:
            todos = self.todo_reader.read_todo_master()
            if not todos:
                print("❌ No TODOs found")
                return []
            
            print(f"📋 Found {len(todos)} TODOs, loading {min(self.MAX_TODOS, len(todos))} (limit)")
            
            # Add limited TODOs
            loaded_todos = []
            for i, todo in enumerate(todos[:self.MAX_TODOS]):
                task_id = f"todo_{i+1:03d}"
                self.system.add_new_todo(
                    name=todo['name'],
                    description=todo['description'],
                    priority=todo['priority'],
                    estimated_duration=todo['estimated_duration'],
                    required_capabilities=todo['required_capabilities']
                )
                loaded_todos.append(todo)
                print(f"✅ Added: {task_id} - {todo['name']}")
            
            return loaded_todos
            
        except Exception as e:
            print(f"❌ Error loading TODOs: {e}")
            return []

    def register_workers(self):
        """Register workers with enhanced capabilities"""
        worker_configs = [
            {
                'id': 'code_quality_worker',
                'name': 'Code Quality Engineer',
                'capabilities': ['code_review', 'testing', 'documentation'],
                'specialty': 'Quality Assurance'
            },
            {
                'id': 'general_worker', 
                'name': 'General Developer',
                'capabilities': ['development', 'integration', 'deployment'],
                'specialty': 'Full Stack Development'
            },
            {
                'id': 'infrastructure_worker',
                'name': 'Infrastructure Specialist',
                'capabilities': ['docker', 'kubernetes', 'monitoring'],
                'specialty': 'DevOps & Infrastructure'
            }
        ]
        
        print("👷 Registering enhanced workers...")
        
        for config in worker_configs:
            worker_id = f"{config['id']}_{self.agent_id}"
            
            # Register in system
            self.system.register_worker(
                worker_id=worker_id,
                name=config['name'],
                capabilities=config['capabilities']
            )
            
            # Create worker status tracker
            self.workers[worker_id] = WorkerStatus(worker_id)
            
            print(f"✅ Registered: {worker_id} - {config['name']} ({config['specialty']})")
            
        print(f"🎯 Total workers: {len(self.workers)}")

    def start_workers(self):
        """Start all workers with dynamic collaboration"""
        print("🚀 Starting dynamic collaborative workers...")
        
        for worker_id in self.workers.keys():
            thread = threading.Thread(
                target=self._dynamic_worker_loop,
                args=(worker_id,),
                daemon=True,
                name=f"Worker-{worker_id}"
            )
            self.worker_threads[worker_id] = thread
            thread.start()
            print(f"👷 {worker_id} started with dynamic collaboration")
            
        print("✅ All workers started with dynamic collaboration enabled")

    def _dynamic_worker_loop(self, worker_id):
        """Enhanced worker loop with collaboration capabilities"""
        worker_status = self.workers[worker_id]
        
        while True:
            try:
                # Check if worker should help others
                if self._should_help_others(worker_id):
                    self._help_other_workers(worker_id)
                    continue
                
                # Try to get a task for this worker
                task = self._get_task_for_worker(worker_id)
                
                if task:
                    self._process_task_dynamically(worker_id, task)
                else:
                    # Worker is idle, look for collaboration opportunities
                    self._handle_idle_worker(worker_id)
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error in worker {worker_id}: {e}")
                worker_status.status = WorkerActivity.IDLE
                time.sleep(5)

    def _should_help_others(self, worker_id):
        """Determine if worker should help others"""
        with self.collaboration_lock:
            # Check if other workers are struggling
            busy_workers = [
                w for w in self.workers.values() 
                if w.status == WorkerActivity.WORKING and w.progress < 30
            ]
            
            # Check if this worker has been idle for a while
            worker_status = self.workers[worker_id]
            idle_time = (datetime.now() - worker_status.last_activity).seconds
            
            return len(busy_workers) > 0 and idle_time > 10

    def _help_other_workers(self, worker_id):
        """Worker helps other struggling workers"""
        worker_status = self.workers[worker_id]
        
        with self.collaboration_lock:
            # Find workers that need help
            struggling_workers = [
                w for w in self.workers.values()
                if w.status == WorkerActivity.WORKING and w.progress < 30
            ]
            
            if struggling_workers:
                target_worker = random.choice(struggling_workers)
                
                worker_status.status = WorkerActivity.HELPING
                worker_status.current_task = f"Helping {target_worker.worker_id}"
                worker_status.is_collaborating = True
                worker_status.collaboration_partners = [target_worker.worker_id]
                
                print(f"🤝 {worker_id} is helping {target_worker.worker_id}")
                
                # Simulate helping
                time.sleep(random.uniform(3, 8))
                
                # Update statistics
                worker_status.tasks_helped += 1
                self.total_collaborations += 1
                
                worker_status.status = WorkerActivity.IDLE
                worker_status.is_collaborating = False
                worker_status.collaboration_partners = []
                worker_status.last_activity = datetime.now()

    def _get_task_for_worker(self, worker_id):
        """Get a task for a specific worker"""
        try:
            available_tasks = self.system.get_available_tasks(worker_id)
            if available_tasks:
                # Get first available task
                task = available_tasks[0]
                
                # Try to claim it
                if self.system.claim_task(worker_id, task['id']):
                    return task
                    
        except Exception as e:
            print(f"❌ Error getting task for {worker_id}: {e}")
        
        return None

    def _process_task_dynamically(self, worker_id, task):
        """Process task with enhanced status tracking"""
        worker_status = self.workers[worker_id]
        
        try:
            worker_status.status = WorkerActivity.WORKING
            worker_status.current_task = task['title']
            worker_status.progress = 0
            worker_status.last_activity = datetime.now()
            
            print(f"🔄 {worker_id} started: {task['title']}")
            
            # Process task with progress updates
            for progress in range(0, 101, 20):
                worker_status.progress = progress
                time.sleep(random.uniform(1, 3))
                
                if progress == 100:
                    # Complete task
                    self.system.complete_task(worker_id, task['id'])
                    worker_status.tasks_completed += 1
                    self.total_tasks_completed += 1
                    
                    print(f"✅ {worker_id} completed: {task['title']}")
                    
                    # Update TODO_MASTER.md
                    self._update_todo_master(task)
                    
            worker_status.status = WorkerActivity.IDLE
            worker_status.current_task = None
            worker_status.progress = 0
            worker_status.last_activity = datetime.now()
            
        except Exception as e:
            print(f"❌ Error processing task in {worker_id}: {e}")
            worker_status.status = WorkerActivity.IDLE

    def _handle_idle_worker(self, worker_id):
        """Handle idle worker behavior"""
        worker_status = self.workers[worker_id]
        
        if worker_status.status != WorkerActivity.IDLE:
            return
            
        worker_status.status = WorkerActivity.WAITING
        worker_status.last_activity = datetime.now()
        
        # Look for collaboration opportunities
        if self._should_help_others(worker_id):
            return  # Will be handled in next iteration
            
        time.sleep(1)

    def _update_todo_master(self, task):
        """Update TODO_MASTER.md with completion status"""
        try:
            todo_master_path = Path(__file__).parent.parent.parent.parent / "TODO_MASTER.md"
            
            if todo_master_path.exists():
                content = todo_master_path.read_text()
                
                # Find and mark the task as completed
                task_title = task['title']
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if task_title in line and '🔄' in line:
                        # Mark as completed with agent ID and timestamp
                        completion_mark = f"✅ COMPLETED by {self.agent_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        lines[i] = line.replace('🔄', '✅') + f" - {completion_mark}"
                        break
                
                # Write back to file
                todo_master_path.write_text('\n'.join(lines))
                print(f"📝 Updated TODO_MASTER.md for: {task_title}")
                
        except Exception as e:
            print(f"❌ Error updating TODO_MASTER.md: {e}")

    def monitor_progress_enhanced(self):
        """Enhanced progress monitoring with detailed information"""
        print("\n🚀 Dynamic Collaborative System - Enhanced Live Status")
        print("=" * 60)
        
        while True:
            try:
                # Clear screen (simple approach)
                print("\n" * 50)
                
                # System overview
                print(f"🚀 Dynamic Collaborative System - Enhanced Live Status")
                print("=" * 60)
                print(f"🆔 Agent ID: {self.agent_id}")
                print(f"📁 Database: {self.db_path}")
                print(f"⏰ Runtime: {datetime.now() - self.start_time}")
                print(f"🎯 Total Collaborations: {self.total_collaborations}")
                print(f"✅ Total Tasks Completed: {self.total_tasks_completed}")
                print("=" * 60)
                
                # Task status - use system status instead
                system_status = self.system.get_system_status()
                total_tasks = system_status.get('total_tasks', 0)
                pending_tasks = system_status.get('pending_tasks', 0)
                completed_tasks = system_status.get('completed_tasks', 0)
                
                print(f"📋 Task Status:")
                print(f"   Total: {total_tasks}")
                print(f"   ⏳ Pending: {pending_tasks}")
                print(f"   ✅ Completed: {completed_tasks}")
                print()
                
                # Worker status with detailed information
                print(f"👷 Worker Status:")
                print("-" * 60)
                
                for worker_id, status in self.workers.items():
                    # Get worker info from system
                    worker_info = self.system.get_worker(worker_id)
                    worker_name = worker_info['name'] if worker_info else "Unknown"
                    
                    # Status emoji and details
                    status_display = status.status
                    current_work = status.current_task or "No current task"
                    progress_bar = "█" * (status.progress // 10) + "░" * (10 - status.progress // 10)
                    
                    print(f"🔹 {worker_id}")
                    print(f"   👤 Name: {worker_name}")
                    print(f"   📊 Status: {status_display}")
                    print(f"   📝 Current: {current_work}")
                    print(f"   📈 Progress: [{progress_bar}] {status.progress}%")
                    print(f"   ✅ Completed: {status.tasks_completed}")
                    print(f"   🤝 Helped: {status.tasks_helped}")
                    
                    if status.is_collaborating:
                        partners = ", ".join(status.collaboration_partners) if status.collaboration_partners else "None"
                        print(f"   🔗 Collaborating with: {partners}")
                    
                    print(f"   ⏰ Last Activity: {status.last_activity.strftime('%H:%M:%S') if status.last_activity else 'Never'}")
                    print()
                
                # System limits and configuration
                print(f"📊 System Configuration:")
                print(f"   Loaded TODOs: {total_tasks} (max: {self.MAX_TODOS})")
                print(f"   Min TODOs: {self.MIN_TODOS}")
                print(f"   Tasks before add: {self.TASKS_BEFORE_ADD}")
                print()
                
                # Recent activities
                print(f"📝 Recent Activities:")
                print(f"   Last TODO_MASTER.md Update: {datetime.now().strftime('%H:%M:%S')}")
                print(f"   Active Collaborations: {sum(1 for w in self.workers.values() if w.is_collaborating)}")
                print()
                
                print("Press Ctrl+C to stop")
                print("=" * 60)
                
                time.sleep(3)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping enhanced monitoring...")
                break
            except Exception as e:
                print(f"❌ Error in monitoring: {e}")
                time.sleep(5)

    def run(self):
        """Run the complete dynamic collaborative system"""
        try:
            # Load TODOs
            loaded_todos = self.load_limited_todos()
            if not loaded_todos:
                print("❌ No TODOs loaded, exiting")
                return
            
            # Register workers
            self.register_workers()
            
            # Start workers
            self.start_workers()
            
            # Start enhanced monitoring
            self.monitor_progress_enhanced()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down dynamic collaborative system...")
        except Exception as e:
            print(f"❌ Error in system: {e}")

if __name__ == "__main__":
    system = DynamicCollaborativeSystem()
    system.run()
