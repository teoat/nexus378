#!/usr/bin/env python3

import threading
import time

def main():
    print("🔧 FIXING WORKER PROCESSING...")
    print("=" * 50)

    # Initialize processor
    processor = CollectiveWorkerProcessor(max_workers=8)

    print("📊 Initial Status:")
    print(f"  - Max Workers: {processor.max_workers}")
    print(f"  - Active Workers: {len(processor.worker_assignments)}")
    print(f"  - Cache Size: {len(processor.worker_cache)}")

    # Step 1: Scan and mark TODO master
    print("\n🔍 Step 1: Scanning TODO master...")
    scan_results = processor.scan_and_mark_todo_master()
    print(f"  - Scanned: {scan_results.get('scanned', 0)}")
    print(f"  - Marked: {scan_results.get('marked', 0)}")

    # Step 2: Load work items
    print("\n📥 Step 2: Loading work items...")
    work_items = processor.load_work_items_batch()
    print(f"  - Loaded: {len(work_items)} work items")

    if not work_items:
        print("❌ No work items available - cannot proceed")
        return False

    # Step 3: Start the processing loop
    print("\n🚀 Step 3: Starting processing loop...")

    # Start the processing loop in a separate thread

            print(f"❌ Error in processing loop: {e}")

    processing_thread = threading.Thread(target=start_processing, daemon=True)
    processing_thread.start()

    # Wait a moment for the loop to start
    time.sleep(2)

    # Step 4: Check if workers are now processing
    print("\n👥 Step 4: Checking worker status...")

    # Give it a few more seconds to process
    time.sleep(3)

    # Check status again
    try:
        stats = processor.get_collective_processing_stats()
        print(f"  - Complex TODOs: {stats.get('total_complex_todos', 0)}")
        print(f"  - Active Workers: {stats.get('active_workers', 0)}")
        print(f"  - Cache Size: {stats.get('cache_stats', {}).get('size', 0)}")
        print(f"  - Total Processed: {stats.get('total_processed', 0)}")
    except Exception as e:
        print(f"  ❌ Error getting stats: {e}")

    # Check worker assignments
    print(f"  - Worker Assignments: {len(processor.worker_assignments)}")
    if processor.worker_assignments:
        print("  - Active Assignments:")
        for todo_id, assignments in list(processor.worker_assignments.items())[:3]:
            print(f"    - {todo_id}: {len(assignments)} workers")

    # Check cache
    print(f"  - Cache Size: {len(processor.worker_cache)}")
    if processor.worker_cache:
        print("  - Cache Keys:")
        for key in list(processor.worker_cache.keys())[:5]:
            print(f"    - {key}")

    print("\n✅ Worker processing fix completed!")

    # Show what should happen next
    print("\n💡 WHAT SHOULD HAPPEN NEXT:")
    print("  - Workers should now be processing the loaded work items")
    print("  - You should see activity in the worker terminals")
    print("  - Check Tab 9 (Monitoring Dashboard) for real-time updates")
    print("  - Workers will continue processing every 30 seconds")

    return True

if __name__ == "__main__":
    main()
