#!/usr/bin/env python3
"""
Check for other agents working on tasks to prevent overlapping implementations
"""

from simple_registry import SimpleTaskRegistry

def main():
    """Check for other agents working on tasks"""
    print("🔍 CHECKING FOR OTHER AGENTS WORKING ON TASKS")
    print("=" * 60)
    
    # Initialize registry
    registry = SimpleTaskRegistry()
    
    # Check each task for agent assignments
    for todo in registry.priority_todos:
        print(f"Task: {todo['name']}")
        print(f"  Agent: {todo['assigned_agent']}")
        print(f"  Status: {todo['status']}")
        print(f"  MCP Status: {todo['mcp_status']}")
        print(f"  Progress: {todo['progress']}%")
        print("-" * 40)
    
    # Check for any conflicts
    assigned_tasks = [todo for todo in registry.priority_todos if todo['assigned_agent'] is not None]
    unassigned_tasks = [todo for todo in registry.priority_todos if todo['assigned_agent'] is None]
    
    print(f"\n📊 SUMMARY:")
    print(f"Total Tasks: {len(registry.priority_todos)}")
    print(f"Assigned Tasks: {len(assigned_tasks)}")
    print(f"Unassigned Tasks: {len(unassigned_tasks)}")
    
    if assigned_tasks:
        print(f"\n⚠️  WARNING: {len(assigned_tasks)} tasks are already assigned to agents!")
        print("These tasks should not be implemented by other agents to prevent overlaps.")
        for task in assigned_tasks:
            print(f"  - {task['name']} (Agent: {task['assigned_agent']})")
    
    if unassigned_tasks:
        print(f"\n✅ {len(unassigned_tasks)} tasks are available for implementation:")
        for task in unassigned_tasks:
            print(f"  - {task['name']} ({task['priority']} priority)")

if __name__ == "__main__":
    main()
