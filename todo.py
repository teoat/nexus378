import datetime

# In-memory store for to-do items
todos = []
# Log of activities
activity_log = []

def log_activity(action):
    """Logs an activity with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity_log.append(f"[{timestamp}] {action}")

def add_todo():
    """Adds a new to-do item."""
    item = input("Enter a new to-do item: ")
    todos.append({"task": item, "completed": False})
    log_activity(f"Added to-do: '{item}'")
    print(f"Added: '{item}'")

def view_todos():
    """Displays all to-do items."""
    print("\n--- To-Do List ---")
    if not todos:
        print("No to-do items yet.")
    else:
        for i, todo in enumerate(todos):
            status = "✓" if todo["completed"] else "✗"
            print(f"{i + 1}. [{status}] {todo['task']}")
    print("------------------\n")

def update_todo():
    """Marks a to-do item as complete."""
    view_todos()
    try:
        item_num = int(input("Enter the number of the item to mark as complete: "))
        if 1 <= item_num <= len(todos):
            todos[item_num - 1]["completed"] = True
            task = todos[item_num - 1]['task']
            log_activity(f"Completed to-do: '{task}'")
            print(f"Marked '{task}' as complete.")
        else:
            print("Invalid item number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def view_log():
    """Displays the activity log."""
    print("\n--- Activity Log ---")
    if not activity_log:
        print("No activities logged yet.")
    else:
        for log_entry in activity_log:
            print(log_entry)
    print("--------------------\n")

def main():
    """Main application loop."""
    log_activity("Application started.")
    while True:
        print("\nWhat would you like to do?")
        print("1. Add a to-do item")
        print("2. View to-do list")
        print("3. Mark a to-do item as complete")
        print("4. View activity log")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            add_todo()
        elif choice == '2':
            view_todos()
        elif choice == '3':
            update_todo()
        elif choice == '4':
            view_log()
        elif choice == '5':
            log_activity("Application exited.")
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
