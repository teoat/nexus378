#!/usr/bin/env python3
Corrected Production Worker - Uses the same database as the fixed system

import sys
import time

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def run_worker(
    worker_id: str, name: str, capabilities: str, db_path: str = "production_todos.db"
):

    print(f"🚀 Starting Corrected Production Worker")
    print(f"📁 Database: {db_path}")
    print(f"👷 Worker: {worker_id} ({name})")
    print(f"🛠️  Capabilities: {capabilities}")
    print("=" * 60)

    # Initialize system with the SAME database path
    system = UnifiedTaskSystem(db_path)

    # Check if worker is already registered
    if worker_id not in system.workers:
        print(f"❌ Worker {worker_id} not found in system")
        print(f"💡 Make sure to run the fixed production system first:")
        print(f"   python fixed_production_system.py")
        return

    print(f"✅ Worker {worker_id} found in system")

    # Check available tasks
    available_tasks = system.get_available_tasks(worker_id)
    print(f"📋 Available tasks: {len(available_tasks)}")

    if not available_tasks:
        print("❌ No available tasks for this worker")
        print("💡 This could mean:")
        print("   1. All tasks are already claimed")
        print("   2. Worker capabilities don't match any tasks")
        print("   3. Database path mismatch")
        return

    print(f"🚀 Starting continuous work loop...")
    print("   Press Ctrl+C to stop\n")

    iteration = 1
    while True:
        try:
            print(f"🔄 Iteration {iteration}")

            # Get available tasks
            available = system.get_available_tasks(worker_id)
            if not available:
                print("   ⏳ No available tasks, waiting...")
                time.sleep(5)
                iteration += 1
                continue

            # Take the first available task
            task = available[0]

            # Handle both object and dictionary formats
            if hasattr(task, "name"):
                task_name = task.name
                task_id = task.id
            else:
                task_name = task.get("name", "Unknown")
                task_id = task.get("id", "unknown")

            print(f"   📋 Claiming: {task_name}")

            # Claim the task
            if system.claim_task(worker_id, task_id):
                print(f"   ✅ Claimed: {task_name}")

                # Simulate work progress
                for progress in [25, 50, 75, 100]:
                    time.sleep(1)  # Simulate work time
                    notes = f"Progress: {progress}% - Working on {task_name}"

                    if system.update_task_progress(worker_id, task_id, progress, notes):
                        print(f"   📈 Progress: {progress}%")
                    else:
                        print(f"   ❌ Failed to update progress")
                        break

                # Complete the task
                completion_notes = (
                    f"Task '{task_name}' completed successfully by {worker_id}"
                )
                if system.complete_task(worker_id, task_id, completion_notes):
                    print(f"   🎉 Completed: {task_name}")
                else:
                    print(f"   ❌ Failed to complete task")

            else:
                print(f"   ❌ Failed to claim: {task_name}")

            iteration += 1

        except KeyboardInterrupt:
            print("\n\n🛑 Worker stopped by user")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
            time.sleep(5)
            iteration += 1

def main():

            "Usage: python corrected_production_worker.py <worker_id> <name> <capabilities>"
        )
        print(
            "Example: python corrected_production_worker.py code_quality_worker 'Code Quality Engineer' 'python_development,code_quality,general_implementation'"
        )
        print("\n💡 IMPORTANT: Make sure to run the fixed production system first:")
        print("   python fixed_production_system.py")
        sys.exit(1)

    worker_id = sys.argv[1]
    name = sys.argv[2]
    capabilities = sys.argv[3]

    # Use the same database path as the fixed system
    db_path = "production_todos.db"

    run_worker(worker_id, name, capabilities, db_path)

if __name__ == "__main__":
    main()
