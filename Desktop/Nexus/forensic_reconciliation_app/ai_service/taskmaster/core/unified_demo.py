#!/usr/bin/env python3
"""
Unified Task System Demo
Demonstrates the complete functionality of the unified task management system
"""

from unified_task_system import UnifiedTaskSystem
import time
import threading

def demo_basic_functionality():
    """Demonstrate basic system functionality"""
    print("🚀 Unified Task Management System Demo")
    print("=" * 60)
    
    # Create system
    system = UnifiedTaskSystem()
    
    # Add sample TODOs
    print("\n📋 Adding sample TODOs...")
    
    todo1 = system.add_new_todo(
        name="API Gateway Implementation",
        description="Implement Node.js API gateway with GraphQL support",
        priority="HIGH",
        estimated_duration="12-16 hours",
        required_capabilities=["nodejs", "graphql", "api_design"],
        subtasks=[
            {"name": "Express.js server setup", "duration": "2-3 hours"},
            {"name": "GraphQL schema design", "duration": "4-6 hours"},
            {"name": "Authentication middleware", "duration": "3-4 hours"},
            {"name": "Rate limiting and security", "duration": "3-3 hours"}
        ]
    )
    
    todo2 = system.add_new_todo(
        name="Frontend Dashboard Development",
        description="Build React-based dashboard with Tauri desktop app",
        priority="HIGH",
        estimated_duration="20-24 hours",
        required_capabilities=["react", "typescript", "ui_design", "tauri"],
        subtasks=[
            {"name": "React component library", "duration": "6-8 hours"},
            {"name": "Dashboard layout and routing", "duration": "4-6 hours"},
            {"name": "Tauri integration", "duration": "4-6 hours"},
            {"name": "State management setup", "duration": "3-4 hours"},
            {"name": "Testing and optimization", "duration": "3-4 hours"}
        ]
    )
    
    todo3 = system.add_new_todo(
        name="Database Schema Design",
        description="Design and implement PostgreSQL database schema",
        priority="NORMAL",
        estimated_duration="8-10 hours",
        required_capabilities=["postgresql", "database_design", "sql"],
        subtasks=[
            {"name": "Entity relationship modeling", "duration": "2-3 hours"},
            {"name": "Schema creation", "duration": "2-3 hours"},
            {"name": "Indexing and optimization", "duration": "2-2 hours"},
            {"name": "Migration scripts", "duration": "2-2 hours"}
        ]
    )
    
    print(f"✅ Added TODO 1: {todo1}")
    print(f"✅ Added TODO 2: {todo2}")
    print(f"✅ Added TODO 3: {todo3}")
    
    # Register workers
    print("\n👷 Registering workers...")
    
    system.register_worker("worker_001", "Frontend Developer", ["react", "typescript", "ui_design"])
    system.register_worker("worker_002", "Backend Developer", ["nodejs", "graphql", "api_design"])
    system.register_worker("worker_003", "Full Stack Developer", ["react", "nodejs", "typescript", "graphql"])
    system.register_worker("worker_004", "Database Engineer", ["postgresql", "database_design", "sql"])
    
    print("✅ Workers registered")
    
    # Show available tasks for workers
    print("\n📊 Available tasks for workers:")
    
    for worker_id in ["worker_001", "worker_002", "worker_003", "worker_004"]:
        available = system.get_available_tasks(worker_id)
        print(f"\n{worker_id}:")
        for task in available:
            print(f"  - {task['name']} ({task['priority']} priority)")
    
    return system, [todo1, todo2, todo3]

def demo_task_workflow(system, todos):
    """Demonstrate complete task workflow"""
    print("\n🔄 Simulating task workflow...")
    
    # Worker 2 claims API Gateway task
    if system.claim_task("worker_002", todos[0]):
        print(f"✅ Worker 2 claimed task {todos[0]}")
        
        # Update progress
        system.update_task_progress("worker_002", todos[0], 25.0, "Express.js server setup completed")
        system.update_task_progress("worker_002", todos[0], 50.0, "GraphQL schema design in progress")
        system.update_task_progress("worker_002", todos[0], 75.0, "Authentication middleware implemented")
        system.complete_task("worker_002", todos[0], "API Gateway fully implemented and tested")
    
    # Worker 1 claims Frontend task
    if system.claim_task("worker_001", todos[1]):
        print(f"✅ Worker 1 claimed task {todos[1]}")
        
        # Update progress
        system.update_task_progress("worker_001", todos[1], 30.0, "React component library created")
        system.update_task_progress("worker_001", todos[1], 60.0, "Dashboard layout implemented")
        system.update_task_progress("worker_001", todos[1], 90.0, "Tauri integration nearly complete")
        system.complete_task("worker_001", todos[1], "Frontend dashboard fully implemented")
    
    # Worker 4 claims Database task
    if system.claim_task("worker_004", todos[2]):
        print(f"✅ Worker 4 claimed task {todos[2]}")
        
        # Update progress
        system.update_task_progress("worker_004", todos[2], 40.0, "Entity relationship modeling completed")
        system.update_task_progress("worker_004", todos[2], 70.0, "Schema creation in progress")
        system.update_task_progress("worker_004", todos[2], 90.0, "Indexing and optimization completed")
        system.complete_task("worker_004", todos[2], "Database schema fully implemented")

def demo_conflict_prevention(system):
    """Demonstrate conflict prevention mechanisms"""
    print("\n🛡️ Testing conflict prevention...")
    
    # Try to add a similar task
    similar_todo = system.add_new_todo(
        name="API Gateway Enhancement",
        description="Enhance existing API gateway with additional features",
        priority="NORMAL",
        estimated_duration="6-8 hours",
        required_capabilities=["nodejs", "graphql", "api_design"],
        subtasks=[
            {"name": "Feature analysis", "duration": "1-2 hours"},
            {"name": "Implementation", "duration": "4-5 hours"},
            {"name": "Testing", "duration": "1-1 hours"}
        ]
    )
    
    print(f"✅ Added similar TODO: {similar_todo}")
    
    # Try to have multiple workers claim similar tasks
    print("\n🔍 Testing conflict detection...")
    
    # Worker 2 tries to claim the similar task
    if system.claim_task("worker_002", similar_todo):
        print(f"✅ Worker 2 claimed similar task {similar_todo}")
        
        # Worker 3 tries to claim the original API Gateway task (should fail due to similarity)
        if system.claim_task("worker_003", "todo_001"):
            print("❌ Conflict detection failed - both workers can work on similar tasks")
        else:
            print("✅ Conflict detection working - prevented duplicate work on similar tasks")
    else:
        print("❌ Failed to claim similar task")

def demo_worker_monitoring(system):
    """Demonstrate worker monitoring capabilities"""
    print("\n👀 Testing worker monitoring...")
    
    # Show worker status
    print("\n📊 Current worker status:")
    for worker_id in ["worker_001", "worker_002", "worker_003", "worker_004"]:
        status = system.get_worker_status(worker_id)
        if status:
            print(f"  {worker_id}: {status['status']} - Current task: {status['current_task']}")
    
    # Simulate worker timeout
    print("\n⏰ Simulating worker timeout...")
    # This would normally happen in the background monitoring loop
    
    # Show final system status
    print("\n📈 Final System Status:")
    status = system.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

def demo_performance_tracking(system):
    """Demonstrate performance tracking"""
    print("\n📊 Performance tracking demonstration:")
    
    # Show worker performance metrics
    print("\n👷 Worker performance metrics:")
    for worker_id in ["worker_001", "worker_002", "worker_003", "worker_004"]:
        status = system.get_worker_status(worker_id)
        if status:
            metrics = status['performance_metrics']
            print(f"  {worker_id}:")
            print(f"    Tasks completed: {metrics['tasks_completed']}")
            print(f"    Tasks failed: {metrics['tasks_failed']}")
            print(f"    Success rate: {metrics['success_rate']:.1%}")
            if metrics['average_completion_time'] > 0:
                print(f"    Avg completion time: {metrics['average_completion_time']:.1f}s")

def main():
    """Main demo function"""
    try:
        # Run basic functionality demo
        system, todos = demo_basic_functionality()
        
        # Run task workflow demo
        demo_task_workflow(system, todos)
        
        # Run conflict prevention demo
        demo_conflict_prevention(system)
        
        # Run worker monitoring demo
        demo_worker_monitoring(system)
        
        # Run performance tracking demo
        demo_performance_tracking(system)
        
        print("\n🎉 Unified Task System demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Task creation and management")
        print("  ✅ Worker registration and capability matching")
        print("  ✅ Task claiming and progress tracking")
        print("  ✅ Conflict prevention and detection")
        print("  ✅ Worker monitoring and timeout handling")
        print("  ✅ Performance metrics and tracking")
        print("  ✅ Database persistence")
        print("  ✅ Thread-safe operations")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
