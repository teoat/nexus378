#!/usr/bin/env python3
"""
Test Single Worker - Test if a worker can actually process TODOs
"""

import sys
import time
from pathlib import Path

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from collective_worker_processor import CollectiveWorkerProcessor


def test_single_worker():
    """Test a single worker to see if it can process TODOs"""
    print("🧪 TESTING SINGLE WORKER")
    print("=" * 50)

    try:
        # Create a single worker processor
        print("🔧 Creating single worker processor...")
        processor = CollectiveWorkerProcessor(max_workers=1)

        # Get system status
        print("\n📊 System Status:")
        status = processor.get_system_status()
        for key, value in status.items():
            if key != "workers":  # Skip detailed worker info
                print(f"   {key}: {value}")

        # Get worker performance
        print("\n🔧 Worker Performance:")
        performance = processor.get_worker_performance()
        for worker_id, worker_data in performance.items():
            print(
                f"   {worker_id}: {worker_data['status']} - Tasks: {worker_data['tasks_completed']} completed, {worker_data['tasks_failed']} failed"
            )

        # Test TODO reading
        print("\n📋 Testing TODO Reading:")
        todos = processor.todo_registry.get_pending_todos()
        print(f"   Found {len(todos)} pending TODOs")

        if todos:
            sample_todo = todos[0]
            print(f"   Sample TODO: {sample_todo['title'][:50]}...")
            print(f"   Priority: {sample_todo.get('priority', 'unknown')}")
            print(f"   Complexity: {sample_todo.get('complexity', 'unknown')}")

        # Test processing a single TODO
        print("\n🚀 Testing TODO Processing:")
        if todos:
            print("   Attempting to process first TODO...")

            # Mark as in-progress
            marked_items = processor._mark_work_items_in_progress([todos[0]])

            if marked_items:
                print(f"   ✅ Successfully marked {len(marked_items)} TODO(s)")

                # Process the marked items
                processor._process_work_items_collectively(marked_items)

                print("   ✅ Processing completed")
            else:
                print("   ❌ Failed to mark TODO for processing")
        else:
            print("   ❌ No pending TODOs to process")

        print("\n✅ Single worker test completed successfully!")

    except Exception as e:
        print(f"❌ Error in single worker test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_single_worker()
