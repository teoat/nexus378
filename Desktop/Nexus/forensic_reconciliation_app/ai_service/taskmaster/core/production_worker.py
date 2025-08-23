#!/usr/bin/env python3
"""
Production Worker - Run in separate terminals
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from production_task_system import UnifiedTaskSystem


def run_worker(worker_id: str, name: str, capabilities: str):
    """Run a production worker"""
    system = UnifiedTaskSystem("production.db")

    # Register worker
    if not system.register_worker(worker_id, name, capabilities.split(",")):
        print(f"❌ Failed to register worker {worker_id}")
        return

    print(f"✅ Worker {worker_id} ({name}) registered")
    print(f"   Capabilities: {capabilities}")
    print(f"\n🚀 Starting continuous work loop...")
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

            # Claim and work on a task
            task = available[0]
            print(f"   📋 Claiming: {task['name']}")

            if system.claim_task(worker_id, task["id"]):
                print(f"   ✅ Claimed: {task['name']}")

                # Simulate work
                for progress in [25, 50, 75, 100]:
                    time.sleep(1)
                    system.update_task_progress(
                        worker_id, task["id"], progress, f"Progress: {progress}%"
                    )
                    print(f"   📈 Progress: {progress}%")

                print(f"   🎉 Completed: {task['name']}")
            else:
                print(f"   ❌ Failed to claim: {task['name']}")

            iteration += 1

        except KeyboardInterrupt:
            print("\n\n🛑 Worker stopped")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
            time.sleep(5)
            iteration += 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python production_worker.py <worker_id> <name> <capabilities>")
        print(
            "Example: python production_worker.py worker_001 'Frontend Dev' 'react,typescript,ui_design'"
        )
        sys.exit(1)

    worker_id = sys.argv[1]
    name = sys.argv[2]
    capabilities = sys.argv[3]

    run_worker(worker_id, name, capabilities)
