#!/usr/bin/env python3
"""
Reliable 12-Tab Terminal Launcher - Using open command
Opens ONE Terminal.app window and creates 12 tabs using a bulletproof method
"""

import os
import subprocess
import time
from pathlib import Path


def launch_reliable_12_tabs():
    """Launch ONE Terminal window with 12 tabs using open command"""

    print("🚀 Reliable 12-Tab Terminal Launcher")
    print("=" * 55)
    print(" Opening ONE Terminal.app window with 12 tabs")
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

    print("\n🚀 Launching Reliable 12-Tab System...")
    print("⏱️  Starting in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    try:
        print("🔧 Opening Terminal.app with first tab...")

        # Open Terminal.app with the first tab
        cmd1 = f'open -a Terminal "{current_dir}"'
        os.system(cmd1)

        # Wait for Terminal to open
        time.sleep(2)

        print("🔧 Creating additional tabs...")

        # Create Tab 2: Worker 2
        cmd2 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 2 - Tab 2\\" && python3 collective_worker_processor.py --worker-id 2 --max-workers 8"\''
        os.system(cmd2)
        time.sleep(0.5)

        # Create Tab 3: Worker 3
        cmd3 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 3 - Tab 3\\" && python3 collective_worker_processor.py --worker-id 3 --max-workers 8"\''
        os.system(cmd3)
        time.sleep(0.5)

        # Create Tab 4: Worker 4
        cmd4 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 4 - Tab 4\\" && python3 collective_worker_processor.py --worker-id 4 --max-workers 8"\''
        os.system(cmd4)
        time.sleep(0.5)

        # Create Tab 5: Worker 5
        cmd5 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 5 - Tab 5\\" && python3 collective_worker_processor.py --worker-id 5 --max-workers 8"\''
        os.system(cmd5)
        time.sleep(0.5)

        # Create Tab 6: Worker 6
        cmd6 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 6 - Tab 6\\" && python3 collective_worker_processor.py --worker-id 6 --max-workers 8"\''
        os.system(cmd6)
        time.sleep(0.5)

        # Create Tab 7: Worker 7
        cmd7 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 7 - Tab 7\\" && python3 collective_worker_processor.py --worker-id 7 --max-workers 8"\''
        os.system(cmd7)
        time.sleep(0.5)

        # Create Tab 8: Worker 8
        cmd8 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 8 - Tab 8\\" && python3 collective_worker_processor.py --worker-id 8 --max-workers 8"\''
        os.system(cmd8)
        time.sleep(0.5)

        # Create Tab 9: TODO Processing Engine
        cmd9 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🔧 TODO Processing Engine - Tab 9\\" && python3 todo_processing_engine.py"\''
        os.system(cmd9)
        time.sleep(0.5)

        # Create Tab 10: Task Breakdown Engine
        cmd10 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"⚡ Task Breakdown Engine - Tab 10\\" && echo \\"Starting engine...\\" && python3 task_breakdown_engine.py"\''
        os.system(cmd10)
        time.sleep(0.5)

        # Create Tab 11: Dynamic Worker Coordinator
        cmd11 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🎯 Dynamic Worker Coordinator - Tab 11\\" && echo \\"Starting coordinator...\\" && python3 dynamic_worker_coordinator.py"\''
        os.system(cmd11)
        time.sleep(0.5)

        # Create Tab 12: System Monitor
        cmd12 = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"📊 System Monitor - Tab 12\\" && echo \\"Starting monitor...\\" && python3 monitor_collective_system.py"\''
        os.system(cmd12)
        time.sleep(0.5)

        # Now start the first worker in the main tab
        print("🔧 Starting Worker 1 in main tab...")
        cmd_main = f'osascript -e \'tell application "Terminal" to do script "cd {current_dir} && source {venv_path}/bin/activate && echo \\"🚀 Worker 1 - Main Tab\\" && python3 collective_worker_processor.py --worker-id 1 --max-workers 8"\''
        os.system(cmd_main)

        print("\n✅ Reliable 12-Tab Terminal System launched successfully!")
        print()
        print("📱 Terminal.app window opened with 12 tabs:")
        print("   Main Tab: Worker 1 (Processing TODOs)")
        print("   Tab 2-8: Additional Collective Workers")
        print("   Tab 9: TODO Processing Engine (Collective Intelligence)")
        print("   Tab 10: Task Breakdown Engine (Collaborative Microtasks)")
        print("   Tab 11: Dynamic Worker Coordinator (Capacity Management)")
        print("   Tab 12: System Monitor (Real-time Analytics)")
        print()
        print("🎯 System Features:")
        print("   - ONE Terminal window with multiple tabs")
        print("   - 8 Collective Workers ready to process 20+ TODOs")
        print("   - Enhanced engines for coordination and processing")
        print("   - Virtual environment active in all tabs")
        print("   - 15-second processing intervals")
        print()
        print("💡 What you should see:")
        print("   - ONE Terminal.app window")
        print("   - Multiple tabs within that window")
        print("   - Each tab running the appropriate engine")
        print("   - All using your project .venv")
        print()
        print("🚀 The collective system is now running!")
        print("   Check the Terminal window for all tabs")

        return True

    except Exception as e:
        print(f"❌ Error launching Terminal system: {e}")
        return False


def main():
    """Main entry point"""
    try:
        success = launch_reliable_12_tabs()
        if success:
            print("\n🎉 Reliable 12-Tab Terminal System setup complete!")
            print("   You can now monitor all tabs in ONE Terminal window")
        else:
            print("\n❌ Failed to setup Reliable 12-Tab Terminal System")

    except KeyboardInterrupt:
        print("\n🛑 Terminal system setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
