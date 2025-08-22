#!/usr/bin/env python3
"""
Demo Script: 15-Minute Task Breakdown System
Shows how to break down complex TODOs into manageable 15-minute tasks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_breakdown_15min import (
    create_15min_breakdown_for_todo,
    get_available_15min_tasks,
    update_15min_task_status,
    export_15min_breakdown,
    get_15min_breakdown_summary
)


def demo_15min_breakdown():
    """Demonstrate the 15-minute task breakdown system"""
    
    print("🚀 15-Minute Task Breakdown System Demo")
    print("=" * 50)
    
    # Sample TODO data (representing the next priority items)
    sample_todos = [
        {
            "id": "AI_002",
            "name": "Complete JobScheduler Implementation",
            "description": "Implement comprehensive job scheduling system for AI agents",
            "estimated_duration": "12-16 hours",
            "required_capabilities": ["python_development", "scheduling", "algorithm_implementation"],
            "task_type": "complex_task"
        },
        {
            "id": "AI_003", 
            "name": "Implement TaskRouter for Intelligent Routing",
            "description": "Build intelligent task routing system for optimal agent assignment",
            "estimated_duration": "12-16 hours",
            "required_capabilities": ["python_development", "routing", "machine_learning"],
            "task_type": "complex_task"
        },
        {
            "id": "AI_004",
            "name": "Build WorkflowOrchestrator for Complex Workflows",
            "description": "Create workflow orchestration system for complex multi-agent processes",
            "estimated_duration": "16-20 hours",
            "required_capabilities": ["python_development", "workflow", "orchestration"],
            "task_type": "complex_task"
        },
        {
            "id": "AI_005",
            "name": "Implement Reconciliation Agent Core Algorithms",
            "description": "Develop core reconciliation algorithms for transaction matching",
            "estimated_duration": "20-24 hours",
            "required_capabilities": ["python_development", "machine_learning", "algorithm_implementation"],
            "task_type": "complex_task"
        },
        {
            "id": "AI_006",
            "name": "Implement Fraud Agent Pattern Detection",
            "description": "Build advanced fraud pattern detection using AI and graph algorithms",
            "estimated_duration": "24-32 hours",
            "required_capabilities": ["python_development", "graph_algorithms", "fraud_detection"],
            "task_type": "complex_task"
        }
    ]
    
    print(f"📋 Creating 15-minute breakdowns for {len(sample_todos)} complex TODOs...")
    print()
    
    # Create breakdowns for each TODO
    for todo in sample_todos:
        print(f"🔧 Breaking down: {todo['name']}")
        print(f"   Duration: {todo['estimated_duration']}")
        print(f"   Capabilities: {', '.join(todo['required_capabilities'])}")
        
        # Create 15-minute breakdown
        breakdown = create_15min_breakdown_for_todo(todo)
        
        print(f"   ✅ Created {breakdown.total_micro_tasks} micro-tasks")
        print(f"   ⏱️  Total estimated time: {breakdown.total_estimated_minutes} minutes")
        print(f"   📊 Status: {breakdown.status}")
        print()
        
        # Show micro-tasks
        print("   📝 Micro-tasks:")
        for i, task in enumerate(breakdown.micro_tasks, 1):
            status_emoji = "⏳" if task.status == "pending" else "🔄" if task.status == "in_progress" else "✅"
            print(f"      {i:2d}. {status_emoji} {task.title}")
            print(f"          Priority: {task.priority}, Dependencies: {len(task.dependencies)}")
        
        print()
    
    # Show overall summary
    print("📊 Overall Breakdown Summary")
    print("=" * 50)
    
    summary = get_15min_breakdown_summary()
    print(f"Total Breakdowns: {summary['total_breakdowns']}")
    print(f"Total Micro-tasks: {summary['total_micro_tasks']}")
    print(f"Completed: {summary['completed_micro_tasks']}")
    print(f"In Progress: {summary['in_progress_micro_tasks']}")
    print(f"Pending: {summary['pending_micro_tasks']}")
    print()
    
    # Show detailed breakdown
    for breakdown_summary in summary['breakdowns']:
        print(f"🔍 {breakdown_summary['todo_name']}")
        print(f"   Progress: {breakdown_summary['completed']}/{breakdown_summary['total_micro_tasks']} ({breakdown_summary['progress_percentage']:.1f}%)")
        print(f"   Status: {breakdown_summary['pending']} pending, {breakdown_summary['in_progress']} in progress")
        print()
    
    # Demonstrate task assignment
    print("🤖 Agent Task Assignment Demo")
    print("=" * 50)
    
    # Simulate agent capabilities
    agent_capabilities = [
        "python_development",
        "machine_learning", 
        "algorithm_implementation",
        "class_design",
        "testing",
        "documentation"
    ]
    
    print(f"Agent Capabilities: {', '.join(agent_capabilities)}")
    print()
    
    # Get available tasks for this agent
    available_tasks = get_available_15min_tasks(agent_capabilities)
    
    print(f"Available 15-minute tasks: {len(available_tasks)}")
    print()
    
    if available_tasks:
        print("📋 Available Tasks (Priority Order):")
        for i, task in enumerate(available_tasks[:5], 1):  # Show first 5
            print(f"   {i}. {task.title}")
            print(f"      Priority: {task.priority}, Required: {', '.join(task.required_capabilities[:2])}")
            print(f"      Dependencies: {len(task.dependencies)}")
            print()
        
        # Simulate task assignment
        if available_tasks:
            first_task = available_tasks[0]
            print(f"🎯 Assigning task: {first_task.title}")
            
            # Update task status
            success = update_15min_task_status(
                first_task.task_id, 
                "in_progress", 
                agent="demo_agent",
                notes="Demo assignment - task started"
            )
            
            if success:
                print(f"✅ Task {first_task.task_id} assigned and started")
            else:
                print(f"❌ Failed to update task status")
    
    # Export example breakdown
    print("\n💾 Export Example")
    print("=" * 50)
    
    if sample_todos:
        first_todo_id = sample_todos[0]['id']
        json_export = export_15min_breakdown(first_todo_id)
        
        if json_export:
            print(f"📄 Exported breakdown for {first_todo_id} to JSON")
            print(f"   Length: {len(json_export)} characters")
            print(f"   Preview: {json_export[:100]}...")
        else:
            print(f"❌ Failed to export breakdown for {first_todo_id}")
    
    print("\n🎉 Demo completed! The 15-minute task breakdown system is ready to use.")
    print("\n💡 Next steps:")
    print("   1. Use create_15min_breakdown_for_todo() to break down your TODOs")
    print("   2. Use get_available_15min_tasks() to find tasks for agents")
    print("   3. Use update_15min_task_status() to track progress")
    print("   4. Use export_15min_breakdown() to export to JSON")
    print("   5. Use get_15min_breakdown_summary() to get overview")


if __name__ == "__main__":
    demo_15min_breakdown()
