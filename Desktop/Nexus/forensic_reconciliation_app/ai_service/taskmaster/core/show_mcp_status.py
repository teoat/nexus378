#!/usr/bin/env python3
"""
Show MCP System Status after DuckDB Task Completion
"""

from simple_registry import SimpleTaskRegistry


def main():
    """Show current MCP system status"""
    print("🔍 MCP SYSTEM STATUS - DUCKDB TASK COMPLETED")
    print("=" * 60)
    
    # Initialize registry
    registry = SimpleTaskRegistry()
    
    # Show overall statistics
    total_todos = len(registry.priority_todos)
    completed_todos = sum(
    1 for todo in registry.priority_todos if todo["status"] == "completed",
)
    pending_todos = sum(
    1 for todo in registry.priority_todos if todo["status"] == "pending",
)
    overall_progress = sum(
    todo["progress"] for todo in registry.priority_todos,
)
    
    print(f"Total Priority TODOs: {total_todos}")
    print(f"Completed: {completed_todos}")
    print(f"Pending: {pending_todos}")
    print(f"Overall Progress: {overall_progress:.1f}%")
    
    # Show completed tasks
    print("\n✅ COMPLETED TASKS:")
    for todo in registry.priority_todos:
        if todo["status"] == "completed":
            print(f"  - {todo['name']} ({todo['mcp_status']})")
            print(
    f"    Progress: {todo['progress']}% | Agent: {todo['assigned_agent']}",
)
            if 'completion_notes' in todo:
                print(f"    Notes: {todo['completion_notes']}")
    
    # Show pending tasks
    print("\n🔄 PENDING TASKS:")
    for todo in registry.priority_todos:
        if todo["status"] == "pending":
            print(f"  - {todo['name']} ({todo['priority']})")
            print(f"    Progress: {todo['progress']}% | Status: {todo['mcp_status']}")
    
    # Show next priority tasks
    print("\n🎯 NEXT PRIORITY TASKS:")
    critical_tasks = (
    [todo for todo in registry.priority_todos if todo["priority"] == "CRITICAL" and todo["status"] == "pending"]
)
    high_tasks = (
    [todo for todo in registry.priority_todos if todo["priority"] == "HIGH" and todo["status"] == "pending"]
)
    
    if critical_tasks:
        print("  🔴 CRITICAL Priority:")
        for todo in critical_tasks[:2]:  # Show first 2 critical tasks
            print(f"    - {todo['name']} ({todo['estimated_duration']})")
    
    if high_tasks:
        print("  🟡 HIGH Priority:")
        for todo in high_tasks[:2]:  # Show first 2 high priority tasks
            print(f"    - {todo['name']} ({todo['estimated_duration']})")
    
    print("\n" + "=" * 60)
    print("🎉 DUCKDB Implementation: COMPLETED ✅")
    print("🚀 MCP System: Ready for next priority tasks")
    print("=" * 60)

if __name__ == "__main__":
    main()
