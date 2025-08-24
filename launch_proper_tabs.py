#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path

def main():
    """Launch ONE Terminal window with proper tabs using AppleScript"""
    # Get current directory and project root
    current_dir = Path.cwd()
    project_root = current_dir  # Use current directory as project root
    venv_path = project_root / ".venv"
    
    print("🚀 Proper Tab-Based Terminal Launcher")
    print("=" * 60)
    print(" Opening ONE Terminal.app window with 36 tabs")
    print("   - Tab 1-32: Collective Workers")
    print("   - Tab 33: TODO Processing Engine")
    print("   - Tab 34: Task Breakdown Engine")
    print("   - Tab 35: Dynamic Worker Coordinator")
    print("   - Tab 36: System Monitor")
    print()
    
    print(f"📍 Project Root: {project_root}")
    print(f"🔧 Core Directory: {current_dir}")
    print(f"🐍 Virtual Environment: {venv_path}")
    print()
    
    # Check if virtual environment exists
    if not venv_path.exists():
        print(f"❌ Virtual environment not found at: {venv_path}")
        return False
    
    print(f"✅ Virtual environment found at: {venv_path}")
    print()
    
    # Check if required engines exist
    print("🔍 Checking engines...")
    engines = [
        "collective_worker_processor.py",
        "todo_processing_engine.py", 
        "task_breakdown_engine.py",
        "dynamic_worker_coordinator.py",
        "monitor_collective_system.py"
    ]
    
    for engine in engines:
        engine_path = current_dir / engine
        if engine_path.exists():
            print(f"   ✅ {engine}")
        else:
            print(f"   ❌ {engine} - MISSING!")
            return False
    
    print("\n🚀 Launching Proper Tab System...")
    print("⏱️  Starting in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    try:
        print("🔧 Opening Terminal.app with first tab...")
        
        # Create the main AppleScript to open Terminal with multiple tabs
        applescript = f'''
tell application "Terminal"
    -- Create new window with first tab
    set newWindow to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Worker 1 - Tab 1' && python3 collective_worker_processor.py --worker-id 1 --max-workers 32"
    
    -- Wait for window to be ready
    delay 2
    
    -- Create additional tabs within the same window
    repeat with i from 2 to 32
        tell newWindow
            set newTab to do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🚀 Worker ' & i & ' - Tab ' & i && python3 collective_worker_processor.py --worker-id ' & i & ' --max-workers 32"
        end tell
        delay 0.5
    end repeat
    
    -- Create Tab 33: TODO Processing Engine
    tell newWindow
        do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🔧 TODO Processing Engine - Tab 33' && python3 todo_processing_engine.py"
    end tell
    delay 0.5
    
    -- Create Tab 34: Task Breakdown Engine
    tell newWindow
        do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '⚡ Task Breakdown Engine - Tab 34' && python3 task_breakdown_engine.py"
    end tell
    delay 0.5
    
    -- Create Tab 35: Dynamic Worker Coordinator
    tell newWindow
        do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '🎯 Dynamic Worker Coordinator - Tab 35' && python3 dynamic_worker_coordinator.py"
    end tell
    delay 0.5
    
    -- Create Tab 36: System Monitor
    tell newWindow
        do script "cd '{current_dir}' && source '{venv_path}/bin/activate' && echo '📊 System Monitor - Tab 36' && python3 monitor_collective_system.py"
    end tell
    
    -- Set window title
    set name of newWindow to "32-Worker Collective System"
    
    -- Activate the window
    activate
end tell
'''
        
        # Write AppleScript to temporary file and execute
        script_file = current_dir / "temp_launcher.scpt"
        with open(script_file, 'w') as f:
            f.write(applescript)
        
        # Execute the AppleScript
        os.system(f'osascript "{script_file}"')
        
        # Clean up temporary file
        os.remove(script_file)
        
        print("\n✅ Proper Tab-Based Terminal System launched successfully!")
        print()
        print("📱 Terminal.app window opened with 36 tabs:")
        print("   Tab 1-32: Collective Workers (Processing TODOs)")
        print("   Tab 33: TODO Processing Engine (Collective Intelligence)")
        print("   Tab 34: Task Breakdown Engine (Collaborative Microtasks)")
        print("   Tab 35: Dynamic Worker Coordinator (Capacity Management)")
        print("   Tab 36: System Monitor (Real-time Analytics)")
        print()
        print("🎯 System Features:")
        print("   - ONE Terminal window with 36 tabs")
        print("   - 32 Collective Workers ready to process TODOs")
        print("   - Enhanced engines for coordination and processing")
        print("   - Virtual environment active in all tabs")
        print("   - 10-second processing intervals (optimized)")
        print()
        print("💡 What you should see:")
        print("   - ONE Terminal.app window")
        print("   - 36 tabs within that window")
        print("   - Each tab running the appropriate engine")
        print("   - All using your project .venv")
        print()
        print("🚀 The collective system is now running!")
        print("   Check the Terminal window for all 36 tabs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching Terminal system: {e}")
        return False


if __name__ == "__main__":
    main()
