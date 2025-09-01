#!/usr/bin/env python3

List all unimplemented TODO items

def main():
    print("📋 UNIMPLEMENTED TODO ITEMS")
    print("=" * 80)

    # Initialize registry
    registry = SimpleTaskRegistry()

    # Get all tasks
    all_tasks = registry.priority_todos

    # Separate completed and unimplemented
    completed_tasks = []
    unimplemented_tasks = []

    for todo in all_tasks:
        if todo["implementation_status"] == "implemented":
            completed_tasks.append(todo)
        else:
            unimplemented_tasks.append(todo)

    print(f"📊 TOTAL TASKS: {len(all_tasks)}")
    print(f"✅ COMPLETED: {len(completed_tasks)}")
    print(f"❌ UNIMPLEMENTED: {len(unimplemented_tasks)}")
    print("=" * 80)

    if completed_tasks:
        print("\n✅ COMPLETED TASKS:")
        for todo in completed_tasks:
            print(f"  • {todo['id']}: {todo['name']}")
            print(
                f"    Status: {todo['status']} | Progress: {todo['progress']}% | MCP: {todo['mcp_status']}",
            )
            print(f"    Agent: {todo['assigned_agent']}")
            print()

    if unimplemented_tasks:
        print("\n❌ UNIMPLEMENTED TASKS:")
        for todo in unimplemented_tasks:
            print(f"  • {todo['id']}: {todo['name']}")
            print(
                f"    Priority: {todo['priority']} | Duration: {todo['estimated_duration']}",
            )
            print(
                f"    Status: {todo['status']} | Progress: {todo['progress']}% | MCP: {todo['mcp_status']}",
            )
            print(f"    Agent: {todo['assigned_agent']}")
            print(f"    Implementation: {todo['implementation_status']}")

            if todo.get("implementation_notes"):
                print(f"    Notes: {todo['implementation_notes']}")

            if todo.get("subtasks"):
                print(f"    Subtasks: {len(todo['subtasks'])} subtasks")
                for subtask, progress in todo["subtask_progress"].items():
                    print(f"      - {subtask}: {progress}%")

            print()

    # Summary by priority
    print("\n📈 PRIORITY BREAKDOWN:")
    critical = [t for t in unimplemented_tasks if t["priority"] == "CRITICAL"]
    high = [t for t in unimplemented_tasks if t["priority"] == "HIGH"]
    normal = [t for t in unimplemented_tasks if t["priority"] == "NORMAL"]

    print(f"  🔴 CRITICAL: {len(critical)} tasks")
    print(f"  🟡 HIGH: {len(high)} tasks")
    print(f"  🟢 NORMAL: {len(normal)} tasks")

    # Overall progress
    total_progress = sum(todo["progress"] for todo in all_tasks)
    overall_progress = total_progress / len(all_tasks) if all_tasks else 0
    print(f"\n🎯 OVERALL PROGRESS: {overall_progress:.1f}%")

    # Next actions
    print("\n🎯 NEXT ACTIONS:")
    if critical:
        print("  🔴 CRITICAL PRIORITY - Immediate attention required:")
        for todo in critical[:3]:
            print(f"    • {todo['name']} ({todo['estimated_duration']})")

    if high:
        print("  🟡 HIGH PRIORITY - Plan implementation:")
        for todo in high[:3]:
            print(f"    • {todo['name']} ({todo['estimated_duration']})")

    if not critical and not high:
        print("  ✅ All priority tasks are in progress!")

if __name__ == "__main__":
    main()
