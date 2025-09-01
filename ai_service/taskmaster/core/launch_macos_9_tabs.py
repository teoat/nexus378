#!/usr/bin/env python3
macOS 9-Tab System Launcher

This script opens one Terminal.app window with 9 tabs:
- Tab 1-8: Worker processes (collective_worker_processor.py)
- Tab 9: Monitor (monitor_collective_system.py)

Uses AppleScript to automate Terminal.app operations.

    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}")
        print(f"Error output: {e.stderr}")
        return None

def launch_9_tab_system():

    print("🚀 Launching macOS 9-Tab Collective Worker System...")
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

    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are present before launching.")
        return False

    print("✅ All required files found")

    # AppleScript to create Terminal window with 9 tabs

    tell application "Terminal"
        activate
        
        -- Create new window
        set newWindow to do script ""
        
        -- Wait for window to be ready
        delay 1
        
        -- Create 9 tabs
        repeat with i from 1 to 8
            tell application "System Events"
                keystroke "t" using command down
            end tell
            delay 0.5
        end repeat
        
        -- Set tab titles
        set tabNames to {"Worker 1", "Worker 2", "Worker 3", "Worker 4", "Worker 5", "Worker 6", "Worker 7", "Worker 8", "Monitor"}
        
        repeat with i from 1 to 9
            tell application "System Events"
                keystroke "i" using command down
                delay 0.2
                keystroke tabNames & item i
                keystroke return
                delay 0.2
            end tell
        end repeat
        
        -- Return window reference
        return id of newWindow
    end tell

    print("🔧 Creating Terminal window with 9 tabs...")
    window_id = run_applescript(terminal_script)

    if not window_id:
        print("❌ Failed to create Terminal window")
        return False

    print(f"✅ Terminal window created with ID: {window_id}")
    print("⏳ Waiting for tabs to be ready...")
    time.sleep(3)

    # Launch workers in tabs 1-8
    print("🚀 Launching worker processes in tabs 1-8...")

    tell application "Terminal"
        set targetWindow to window id {window_id}
        
        -- Launch workers in tabs 1-8
        repeat with i from 1 to 8
            set currentTab to tab i of targetWindow
            
            -- Navigate to correct directory
            do script "cd '{current_dir}'" in currentTab
            delay 0.5
            
            -- Launch worker process
            do script "python3 collective_worker_processor.py" in currentTab
            delay 1
        end repeat
        
        -- Launch monitor in tab 9
        set monitorTab to tab 9 of targetWindow
        do script "cd '{current_dir}'" in monitorTab
        delay 0.5
        do script "python3 monitor_collective_system.py" in monitorTab
    end tell

    print("🔧 Launching processes...")
    result = run_applescript(worker_launch_script)

    if result is not None:
        print("✅ All processes launched successfully!")
        print("=" * 60)
        print("🎯 SYSTEM STATUS:")
        print("📱 Terminal window opened with 9 tabs")
        print("🔧 Tabs 1-8: Worker processes running")
        print("📊 Tab 9: System monitor active")
        print("=" * 60)
        print("💡 TIPS:")
        print("- Monitor system health in Tab 9")
        print("- Workers automatically process TODOs from TODO_MASTER.md")
        print("- Processing interval: 15 seconds per worker")
        print("- Press Ctrl+C in any tab to stop that process")
        print("=" * 60)
        return True
    else:
        print("❌ Failed to launch some processes")
        return False

def main():

        if sys.platform != "darwin":
            print("❌ This script is designed for macOS only")
            print("Please use the appropriate launcher for your operating system")
            return

        # Check if Terminal.app is available
        if not os.path.exists("/Applications/Utilities/Terminal.app"):
            print("❌ Terminal.app not found")
            print("Please ensure Terminal.app is installed")
            return

        # Launch the system
        success = launch_9_tab_system()

        if success:
            print("🎉 Collective Worker System launched successfully!")
            print("🚀 Your 9-tab system is now running!")
        else:
            print("💥 Failed to launch Collective Worker System")
            print("Please check the error messages above and try again")

    except KeyboardInterrupt:
        print("\n⏹️  Launch cancelled by user")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback

        traceback.print_exc()

if __name__ == "__main__":
    main()
