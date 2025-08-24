#!/usr/bin/env python3
11-Tab System Launcher
8 Worker Tabs + 3 Processing Tabs (TODOs/Tasks/Microtasks)

import subprocess
import sys
import time

def launch_11_tab_system():
    print("🚀 Launching 11-Tab Collective Worker System...")
    print("=" * 70)

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

    print("\n🚀 Starting 12-tab system...")
    print("📱 Tab 1-8: Core Worker Processes")
    print("🔧 Tab 9: TODO Processing Engine")
    print("⚡ Tab 10: Task Breakdown Engine")
    print("🎯 Tab 11: Dynamic Worker Coordinator")
    print("📊 Tab 12: System Monitor & Analytics")
    print("\n⏱️  Starting in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    # Launch core workers (tabs 1-8)
    worker_processes = []
    print("\n🔧 Launching 8 core worker processes...")

    for i in range(8):
        worker_id = i + 1
        print(f"   Starting Core Worker {worker_id}...")

        try:
            # Launch worker process with optimized settings
            process = subprocess.Popen(
                [
                    sys.executable,
                    "collective_worker_processor.py",
                    "--worker-id",
                    str(worker_id),
                    "--max-workers",
                    "8",
                ],
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            worker_processes.append(
                {
                    "id": f"core_worker_{worker_id}",
                    "process": process,
                    "type": "core_worker",
                }
            )

            print(f"   ✅ Core Worker {worker_id} started (PID: {process.pid})")

        except Exception as e:
            print(f"   ❌ Failed to start Core Worker {worker_id}: {e}")

    # Launch TODO Processing Engine (tab 9)
    print("\n🔧 Launching TODO Processing Engine...")
    try:
        todo_engine = subprocess.Popen(
            [sys.executable, "todo_processing_engine.py"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        worker_processes.append(
            {"id": "todo_engine", "process": todo_engine, "type": "todo_engine"}
        )

        print(f"   ✅ TODO Processing Engine started (PID: {todo_engine.pid})")

    except Exception as e:
        print(f"   ❌ Failed to start TODO Processing Engine: {e}")

    # Launch Task Breakdown Engine (tab 10)
    print("\n⚡ Launching Task Breakdown Engine...")
    try:
        breakdown_engine = subprocess.Popen(
            [sys.executable, "task_breakdown_engine.py"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        worker_processes.append(
            {
                "id": "breakdown_engine",
                "process": breakdown_engine,
                "type": "breakdown_engine",
            }
        )

        print(f"   ✅ Task Breakdown Engine started (PID: {breakdown_engine.pid})")

    except Exception as e:
        print(f"   ❌ Failed to start Task Breakdown Engine: {e}")

    # Launch Dynamic Worker Coordinator (tab 11)
    print("\n🎯 Launching Dynamic Worker Coordinator...")
    try:
        coordinator = subprocess.Popen(
            [sys.executable, "dynamic_worker_coordinator.py"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        worker_processes.append(
            {"id": "coordinator", "process": coordinator, "type": "coordinator"}
        )

        print(f"   ✅ Dynamic Worker Coordinator started (PID: {coordinator.pid})")

    except Exception as e:
        print(f"   ❌ Failed to start Dynamic Worker Coordinator: {e}")

    # Launch System Monitor (tab 12)
    print("\n📊 Launching System Monitor...")
    try:
        monitor = subprocess.Popen(
            [sys.executable, "monitor_collective_system.py"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        worker_processes.append(
            {"id": "monitor", "process": monitor, "type": "monitor"}
        )

        print(f"   ✅ System Monitor started (PID: {monitor.pid})")

    except Exception as e:
        print(f"   ❌ Failed to start System Monitor: {e}")

    print(f"\n🎉 System launched successfully!")
    print(f"📊 Active processes: {len(worker_processes)}")
    print(
        f"🔧 Core Workers: {len([p for p in worker_processes if p['type'] == 'core_worker'])}"
    )
    print(
        f"🔧 Processing Engines: {len([p for p in worker_processes if p['type'] in ['todo_engine', 'breakdown_engine']])}"
    )
    print(
        f"🎯 Coordinators: {len([p for p in worker_processes if p['type'] == 'coordinator'])}"
    )
    print(
        f"📊 Monitors: {len([p for p in worker_processes if p['type'] == 'monitor'])}"
    )

    print("\n📋 Process Information:")
    for proc_info in worker_processes:
        proc_type = proc_info["type"].replace("_", " ").title()
        proc_id = proc_info["id"]
        proc_pid = proc_info["process"].pid
        print(f"   {proc_type} {proc_id}: PID {proc_pid}")

    print("\n💡 System Features:")
    print("   - 8 Core Workers: Process TODOs with 15-second intervals")
    print("   - TODO Processing Engine: Manages TODO lifecycle and updates")
    print("   - Task Breakdown Engine: Converts complex TODOs to microtasks")
    print("   - Dynamic Worker Coordinator: Enables collaborative task processing")
    print("   - System Monitor: Real-time health and performance tracking")
    print("   - Automatic TODO_MASTER.md updates after completion")
    print("   - Dynamic worker scaling based on available resources")
    print("   - Collaborative task processing with multiple workers")

    print("\n⚠️  To stop the system, press Ctrl+C")

    try:
        # Keep the main process running
        while True:
            time.sleep(10)

            # Check if any processes have died
            active_processes = []
            for proc_info in worker_processes:
                if proc_info["process"].poll() is None:
                    active_processes.append(proc_info)
                else:
                    print(
                        f"⚠️  {proc_info['type'].replace('_', ' ').title()} {proc_info['id']} has stopped"
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
                print(
                    f"   Stopped {proc_info['type'].replace('_', ' ').title()} {proc_info['id']}"
                )
            except Exception:
                logger.error(f"Error: {e}")
                pass

        print("✅ System stopped")

    return True

if __name__ == "__main__":
    launch_11_tab_system()
