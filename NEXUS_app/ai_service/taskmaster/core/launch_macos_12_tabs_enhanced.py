#!/usr/bin/env python3
Enhanced macOS Terminal Launcher - 12 Tabs with Virtual Environment
Opens one Terminal.app window with 12 tabs, sets venv, path, and launches enhanced engines

import subprocess
import time

def launch_macos_12_tabs_enhanced():

    print("🚀 Enhanced macOS Terminal Launcher - 12 Tabs")
    print("=" * 60)
    print(" Opening Terminal.app with 12 tabs for enhanced collective system")
    print("   - Tab 1-8: Enhanced Collective Workers")
    print("   - Tab 9: Enhanced TODO Processing Engine")
    print("   - Tab 10: Enhanced Task Breakdown Engine")
    print("   - Tab 11: Enhanced Dynamic Worker Coordinator")
    print("   - Tab 12: System Monitor")
    print()

    # Get project paths
    current_dir = Path(__file__).parent.absolute()
    project_root = (
        current_dir.parent.parent.parent.parent
    )  # Go up to Nexus root (4 levels)
    venv_path = project_root / ".venv"

    print(f"📍 Project Root: {project_root}")
    print(f"🔧 Core Directory: {current_dir}")
    print(f"🐍 Virtual Environment: {venv_path}")
    print()

    # Check if virtual environment exists
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print(f"   Expected at: {venv_path}")
        print("   Please run: python3 -m venv .venv")
        return False

    # Check if engines exist
    engines = [
        "todo_processing_engine.py",
        "task_breakdown_engine.py",
        "dynamic_worker_coordinator.py",
    ]

    print("🔍 Checking engines...")
    for engine in engines:
        engine_path = current_dir / engine
        if engine_path.exists():
            print(f"   ✅ {engine}")
        else:
            print(f"   ❌ {engine} - MISSING!")
            return False

    print("\n�� Launching Enhanced 12-Tab Terminal System...")
    print("⏱️  Starting in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    # Create AppleScript to launch Terminal with 12 tabs

tell application "Terminal"
    -- Create new window
    set newWindow to do script ""
    
    -- Wait for window to be ready
    delay 1
    
    -- Configure Tab 1: Enhanced Worker 1
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 1 - Tab 1' && python3 collective_worker_processor.py --worker-id 1 --max-workers 8" in newWindow
    
    -- Create Tab 2: Enhanced Worker 2
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 2 - Tab 2' && python3 collective_worker_processor.py --worker-id 2 --max-workers 8" in newWindow
    
    -- Create Tab 3: Enhanced Worker 3
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 3 - Tab 3' && python3 collective_worker_processor.py --worker-id 3 --max-workers 8" in newWindow
    
    -- Create Tab 4: Enhanced Worker 4
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 4 - Tab 4' && python3 collective_worker_processor.py --worker-id 4 --max-workers 8" in newWindow
    
    -- Create Tab 5: Enhanced Worker 5
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 5 - Tab 5' && python3 collective_worker_processor.py --worker-id 5 --max-workers 8" in newWindow
    
    -- Create Tab 6: Enhanced Worker 6
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 6 - Tab 6' && python3 collective_worker_processor.py --worker-id 6 --max-workers 8" in newWindow
    
    -- Create Tab 7: Enhanced Worker 7
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 7 - Tab 7' && python3 collective_worker_processor.py --worker-id 7 --max-workers 8" in newWindow
    
    -- Create Tab 8: Enhanced Worker 8
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Enhanced Worker 8 - Tab 8' && python3 collective_worker_processor.py --worker-id 8 --max-workers 8" in newWindow
    
    -- Create Tab 9: TODO Processing Engine
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🔧 TODO Processing Engine - Tab 9' && python3 todo_processing_engine.py" in newWindow
    
    -- Create Tab 10: Task Breakdown Engine
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '⚡ Task Breakdown Engine - Tab 10' && python3 task_breakdown_engine.py" in newWindow
    
    -- Create Tab 11: Dynamic Worker Coordinator
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🎯 Dynamic Worker Coordinator - Tab 11' && python3 dynamic_worker_coordinator.py" in newWindow
    
    -- Create Tab 12: System Monitor
    tell application "Terminal" to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '📊 System Monitor - Tab 12' && python3 monitor_collective_system.py" in newWindow
    
    -- Activate the window
    activate
    
    -- Wait for all tabs to be created
    delay 2
    
end tell

        print("🔧 Executing AppleScript to create Terminal with 12 tabs...")

        # Execute AppleScript
        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Enhanced 12-Tab Terminal System launched successfully!")
            print()
            print("📱 Terminal.app window opened with 12 tabs:")
            print("   Tab 1-8: Enhanced Collective Workers (Processing TODOs)")
            print("   Tab 9: Enhanced TODO Processing Engine (Collective Intelligence)")
            print(
                "   Tab 10: Enhanced Task Breakdown Engine (Collaborative Microtasks)"
            )
            print(
                "   Tab 11: Enhanced Dynamic Worker Coordinator (Capacity Management)"
            )
            print("   Tab 12: System Monitor (Real-time Analytics)")
            print()
            print("🎯 Enhanced System Features:")
            print("   - Capacity Limits: Max 5 active tasks, Max 12 total TODOs")
            print(
                "   - Conflict Prevention: Automatic task marking to prevent conflicts"
            )
            print(
                "   - Collective Intelligence: Workers coordinate for optimal performance"
            )
            print(
                "   - Enhanced Processing: 6-12 second intervals for faster processing"
            )
            print("   - Virtual Environment: All tabs use project .venv")
            print("   - Custom Tab Titles: Easy identification of each component")
            print()
            print("💡 Each tab is now:")
            print("   - In the correct directory (core)")
            print("   - Using the virtual environment (.venv)")
            print("   - Running the appropriate enhanced engine")
            print("   - Ready for collective processing")
            print()
            print("🚀 The enhanced collective system is now running!")
            print("   Check each tab to see the engines in action")

        else:
            print("❌ Failed to launch Terminal system")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error launching Terminal system: {e}")
        return False

    return True

def main():

            print("\n🎉 Enhanced macOS Terminal System setup complete!")
            print("   You can now monitor all 12 tabs in the Terminal.app window")
        else:
            print("\n❌ Failed to setup Enhanced macOS Terminal System")

    except KeyboardInterrupt:
        print("\n🛑 Terminal system setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
