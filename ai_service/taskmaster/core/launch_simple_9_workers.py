#!/usr/bin/env python3
Simple 9-Worker System Launcher
Launches 8 worker processes and 1 monitor process

import subprocess
import sys
import time

def launch_simple_9_worker_system():
    print("🚀 Launching Simple 9-Worker System...")
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

    print("\n🚀 Starting 9-worker system...")
    print("📱 This will launch 8 worker processes and 1 monitor process")
    print("🔧 Workers: Processing TODOs from TODO_MASTER.md")
    print("📊 Monitor: System health and performance dashboard")
    print("\n⏱️  Starting in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    # Launch workers
    worker_processes = []
    print("\n🔧 Launching 8 worker processes...")

    for i in range(8):
        worker_id = i + 1
        print(f"   Starting Worker {worker_id}...")

        try:
            # Launch worker process
            process = subprocess.Popen(
                [sys.executable, "collective_worker_processor.py"],
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            worker_processes.append(
                {"id": worker_id, "process": process, "type": "worker"}
            )

            print(f"   ✅ Worker {worker_id} started (PID: {process.pid})")

        except Exception as e:
            print(f"   ❌ Failed to start Worker {worker_id}: {e}")

    # Launch monitor
    print("\n📊 Launching system monitor...")
    try:
        monitor_process = subprocess.Popen(
            [sys.executable, "monitor_collective_system.py"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        worker_processes.append(
            {"id": "monitor", "process": monitor_process, "type": "monitor"}
        )

        print(f"   ✅ Monitor started (PID: {monitor_process.pid})")

    except Exception as e:
        print(f"   ❌ Failed to start monitor: {e}")

    print(f"\n🎉 System launched successfully!")
    print(f"📊 Active processes: {len(worker_processes)}")
    print(f"🔧 Workers: {len([p for p in worker_processes if p['type'] == 'worker'])}")
    print(
        f"📊 Monitors: {len([p for p in worker_processes if p['type'] == 'monitor'])}"
    )

    print("\n📋 Process Information:")
    for proc_info in worker_processes:
        proc_type = proc_info["type"].title()
        proc_id = proc_info["id"]
        proc_pid = proc_info["process"].pid
        print(f"   {proc_type} {proc_id}: PID {proc_pid}")

    print("\n💡 System is now running!")
    print("   - Workers are processing TODOs from TODO_MASTER.md")
    print("   - Monitor is tracking system health")
    print("   - Check individual process outputs for detailed logs")

    print("\n⚠️  To stop the system, press Ctrl+C")

    try:
        # Keep the main process running
        while True:
            time.sleep(5)

            # Check if any processes have died
            active_processes = []
            for proc_info in worker_processes:
                if proc_info["process"].poll() is None:
                    active_processes.append(proc_info)
                else:
                    print(
                        f"⚠️  {proc_info['type'].title()} {proc_info['id']} has stopped"
                    )

            worker_processes = active_processes

            if not worker_processes:
                print("❌ All processes have stopped")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")

        # Terminate all processes
        for proc_info in worker_processes:
            try:
                proc_info["process"].terminate()
                print(f"   Stopped {proc_info['type'].title()} {proc_info['id']}")
            except Exception:
                logger.error(f"Error: {e}")
                pass

        print("✅ System stopped")

    return True

if __name__ == "__main__":
    launch_simple_9_worker_system()
