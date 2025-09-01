#!/usr/bin/env python3
Active Worker Launcher - Launches workers that actually process TODOs

import sys
import threading
import time

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def worker_function(worker_id, max_workers):

        print(f"🔧 Worker {worker_id} starting...")

        # Create worker processor
        processor = CollectiveWorkerProcessor(max_workers=max_workers)

        # Start the processing loop
        print(f"🚀 Worker {worker_id} starting processing loop...")
        processor.start_collective_processing_loop(interval=15)

    except Exception as e:
        print(f"❌ Worker {worker_id} error: {e}")

def launch_active_workers():

    print("🚀 LAUNCHING ACTIVE WORKER SYSTEM")
    print("=" * 60)

    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    print(f"📍 Working directory: {current_dir}")

    # Check if required files exist
    required_files = [
        "collective_worker_processor.py",
        "monitor_collective_system.py",
        "todo_master_reader.py",
    ]

    print("🔍 Checking required files...")
    for file in required_files:
        if not (current_dir / file).exists():
            print(f"❌ Missing required file: {file}")
            return False
        print(f"✅ Found: {file}")

    print("\n🚀 Starting 8 active workers...")
    print("📱 Each worker will actively process TODOs from TODO_MASTER.md")
    print("⏱️  Processing interval: 15 seconds per worker")
    print("\n⏱️  Starting in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    # Create worker threads
    worker_threads = []
    max_workers = 8

    print(f"\n🔧 Launching {max_workers} active workers...")

    for i in range(max_workers):
        worker_id = i + 1
        print(f"   Starting Worker {worker_id}...")

        # Create worker thread
        worker_thread = threading.Thread(
            target=worker_function,
            args=(worker_id, max_workers),
            name=f"Worker_{worker_id}",
            daemon=True,
        )

        worker_threads.append(worker_thread)
        worker_thread.start()

        print(f"   ✅ Worker {worker_id} started")
        time.sleep(0.5)  # Brief pause between workers

    print(f"\n🎉 All {max_workers} workers launched successfully!")
    print("📊 Workers are now actively processing TODOs")
    print("🔧 Each worker runs independently with 15-second intervals")

    print("\n💡 System Status:")
    print("   - Workers are reading from TODO_MASTER.md")
    print("   - Processing TODOs with intelligent breakdown")
    print("   - Updating TODO status in real-time")
    print("   - Clearing cache after completion")

    print("\n⚠️  To stop the system, press Ctrl+C")

    try:
        # Keep the main process running
        while True:
            time.sleep(10)

            # Check if any threads are still alive
            active_threads = [t for t in worker_threads if t.is_alive()]

            if not active_threads:
                print("❌ All worker threads have stopped")
                break
            else:
                print(f"📊 {len(active_threads)} workers still active...")

    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
        print("   Workers will stop after completing current processing cycle")
        print("✅ System shutdown initiated")

    return True

if __name__ == "__main__":
    launch_active_workers()
