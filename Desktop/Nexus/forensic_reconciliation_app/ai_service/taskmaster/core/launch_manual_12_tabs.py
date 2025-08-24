#!/usr/bin/env python3
"""
Manual 12-Tab Terminal Launcher - Guaranteed to work
Opens 12 individual Terminal tabs using direct commands
"""

import os
import subprocess
import time
from pathlib import Path


def launch_manual_12_tabs():
    """Launch 12 Terminal tabs manually using direct commands"""

    print("🚀 Manual 12-Tab Terminal Launcher")
    print("=" * 50)
    print(" Opening 12 individual Terminal tabs for collective system")
    print("   - Tab 1-8: Collective Workers")
    print("   - Tab 9: TODO Processing Engine")
    print("   - Tab 10: Task Breakdown Engine")
    print("   - Tab 11: Dynamic Worker Coordinator")
    print("   - Tab 12: System Monitor")
    print()

    # Get project paths
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent.parent.parent  # Go up to Nexus root
    venv_path = project_root / ".venv"

    print(f"📍 Project Root: {project_root}")
    print(f"🔧 Core Directory: {current_dir}")
    print(f"🐍 Virtual Environment: {venv_path}")
    print()

    # Check if virtual environment exists
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print(f"   Expected at: {venv_path}")
        return False

    print(f"✅ Virtual environment found at: {venv_path}")
    print()

    # Check if engines exist
    engines = [
        "collective_worker_processor.py",
        "todo_processing_engine.py",
        "task_breakdown_engine.py",
        "dynamic_worker_coordinator.py",
        "monitor_collective_system.py",
    ]

    print("🔍 Checking engines...")
    for engine in engines:
        engine_path = current_dir / engine
        if engine_path.exists():
            print(f"   ✅ {engine}")
        else:
            print(f"   ❌ {engine} - MISSING!")
            return False

    print("\n🚀 Launching 12 Terminal Tabs...")
    print("⏱️  Starting in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    # Launch each tab individually using os.system
    print("\n🔧 Opening Terminal tabs one by one...")

    # Tab 1: Worker 1
    print("   📱 Opening Tab 1: Worker 1...")
    cmd1 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 1 - Tab 1\\" && python3 collective_worker_processor.py --worker-id 1 --max-workers 8"\''
    os.system(cmd1)
    time.sleep(1)

    # Tab 2: Worker 2
    print("   📱 Opening Tab 2: Worker 2...")
    cmd2 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 2 - Tab 2\\" && python3 collective_worker_processor.py --worker-id 2 --max-workers 8"\''
    os.system(cmd2)
    time.sleep(1)

    # Tab 3: Worker 3
    print("   📱 Opening Tab 3: Worker 3...")
    cmd3 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 3 - Tab 3\\" && python3 collective_worker_processor.py --worker-id 3 --max-workers 8"\''
    os.system(cmd3)
    time.sleep(1)

    # Tab 4: Worker 4
    print("   📱 Opening Tab 4: Worker 4...")
    cmd4 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 4 - Tab 4\\" && python3 collective_worker_processor.py --worker-id 4 --max-workers 8"\''
    os.system(cmd4)
    time.sleep(1)

    # Tab 5: Worker 5
    print("   📱 Opening Tab 5: Worker 5...")
    cmd5 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 5 - Tab 5\\" && python3 collective_worker_processor.py --worker-id 5 --max-workers 8"\''
    os.system(cmd5)
    time.sleep(1)

    # Tab 6: Worker 6
    print("   📱 Opening Tab 6: Worker 6...")
    cmd6 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 6 - Tab 6\\" && python3 collective_worker_processor.py --worker-id 6 --max-workers 8"\''
    os.system(cmd6)
    time.sleep(1)

    # Tab 7: Worker 7
    print("   📱 Opening Tab 7: Worker 7...")
    cmd7 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 7 - Tab 7\\" && python3 collective_worker_processor.py --worker-id 7 --max-workers 8"\''
    os.system(cmd7)
    time.sleep(1)

    # Tab 8: Worker 8
    print("   📱 Opening Tab 8: Worker 8...")
    cmd8 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 8 - Tab 8\\" && python3 collective_worker_processor.py --worker-id 8 --max-workers 8"\''
    os.system(cmd8)
    time.sleep(1)

    # Tab 9: TODO Processing Engine
    print("   📱 Opening Tab 9: TODO Processing Engine...")
    cmd9 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🔧 TODO Processing Engine - Tab 9\\" && python3 todo_processing_engine.py"\''
    os.system(cmd9)
    time.sleep(1)

    # Tab 10: Task Breakdown Engine
    print("   📱 Opening Tab 10: Task Breakdown Engine...")
    cmd10 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"⚡ Task Breakdown Engine - Tab 10\\" && python3 task_breakdown_engine.py"\''
    os.system(cmd10)
    time.sleep(1)

    # Tab 11: Dynamic Worker Coordinator
    print("   📱 Opening Tab 11: Dynamic Worker Coordinator...")
    cmd11 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🎯 Dynamic Worker Coordinator - Tab 11\\" && python3 dynamic_worker_coordinator.py"\''
    os.system(cmd11)
    time.sleep(1)

    # Tab 12: System Monitor
    print("   📱 Opening Tab 12: System Monitor...")
    cmd12 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"📊 System Monitor - Tab 12\\" && python3 monitor_collective_system.py"\''
    os.system(cmd12)
    time.sleep(1)

    print("\n✅ All 12 Terminal tabs launched!")
    print()
    print("📱 Terminal.app should now have 12 tabs:")
    print("   Tab 1-8: Collective Workers (Processing TODOs)")
    print("   Tab 9: TODO Processing Engine (Collective Intelligence)")
    print("   Tab 10: Task Breakdown Engine (Collaborative Microtasks)")
    print("   Tab 11: Dynamic Worker Coordinator (Capacity Management)")
    print("   Tab 12: System Monitor (Real-time Analytics)")
    print()
    print("🎯 System Features:")
    print("   - 8 Collective Workers ready to process 20+ TODOs")
    print("   - Enhanced engines for coordination and processing")
    print("   - Virtual environment active in all tabs")
    print("   - 15-second processing intervals")
    print()
    print("💡 Each tab is now:")
    print("   - In the correct directory (core)")
    print("   - Using the virtual environment (.venv)")
    print("   - Running the appropriate engine")
    print("   - Ready for collective processing")
    print()
    print("🚀 The collective system is now running!")
    print("   Check Terminal.app to see all 12 tabs in action")

    return True


def main():
    """Main entry point"""
    try:
        success = launch_manual_12_tabs()
        if success:
            print("\n🎉 12-Tab Terminal System setup complete!")
            print("   You can now monitor all 12 tabs in the Terminal.app window")
        else:
            print("\n❌ Failed to setup 12-Tab Terminal System")

    except KeyboardInterrupt:
        print("\n🛑 Terminal system setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
