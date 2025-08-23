#!/usr/bin/env python3
"""
Show All Terminals Script
Brings all 8 collective worker terminal windows to the front
"""

import subprocess
import sys
import time


def bring_terminals_to_front():
    """Bring all terminal windows to the front"""

    print("🔍 BRINGING ALL 8 COLLECTIVE WORKER TERMINALS TO THE FRONT")
    print("=" * 70)
    print("This will make all terminal windows visible on your screen")
    print()

    try:
        # macOS: Bring all Terminal windows to front
        if sys.platform == "darwin":
            print("🍎 macOS detected - bringing Terminal windows to front...")

            # Script to bring all Terminal windows to front
            apple_script = """
            tell application "Terminal"
                activate
                set windowCount to count of windows
                repeat with i from 1 to windowCount
                    set frontmost of window i to true
                end repeat
            end tell
            """

            subprocess.run(["osascript", "-e", apple_script])
            print("✅ All Terminal windows brought to front!")

        # Linux: Focus all terminal windows
        elif sys.platform.startswith("linux"):
            print("🐧 Linux detected - focusing terminal windows...")
            subprocess.run(["wmctrl", "-a", "Terminal"])
            print("✅ Terminal windows focused!")

        # Windows: Bring all cmd windows to front
        elif sys.platform == "win32":
            print("🪟 Windows detected - bringing cmd windows to front...")
            subprocess.run(["tasklist", "/FI", "IMAGENAME eq cmd.exe"])
            print("✅ CMD windows should be visible!")

        else:
            print("❓ Unknown platform - please manually check for terminal windows")

    except Exception as e:
        print(f"❌ Error bringing terminals to front: {e}")

    print()
    print("🎯 NEXT STEPS:")
    print("1. Look for 8 Terminal windows on your screen")
    print("2. Each window should show 'Collective Worker Processing'")
    print("3. If you still don't see them, check Mission Control (F3)")
    print("4. Look in the Terminal app's Window menu")
    print()
    print("💡 TIP: On macOS, try pressing F3 to see all windows in Mission Control")


def check_terminal_processes():
    """Check if all 8 collective worker processes are running"""

    print("🔍 CHECKING COLLECTIVE WORKER PROCESSES")
    print("=" * 50)

    try:
        # Check for running collective worker processes
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)

        if result.returncode == 0:
            lines = result.stdout.split("\n")
            collective_processes = [
                line
                for line in lines
                if "collective_worker_processor.py" in line and "grep" not in line
            ]

            print(f"📊 Found {len(collective_processes)} collective worker processes:")
            print()

            for i, process in enumerate(collective_processes[:8], 1):
                print(f"Process {i}: {process.strip()}")

            if len(collective_processes) >= 8:
                print(f"\n✅ All 8 processes are running!")
            else:
                print(f"\n⚠️  Only {len(collective_processes)} processes found")
                print("Some terminals may have closed or failed to start")

        else:
            print("❌ Could not check processes")

    except Exception as e:
        print(f"❌ Error checking processes: {e}")

    print()


def main():
    """Main function"""

    print("🚀 COLLECTIVE WORKER TERMINAL VISIBILITY HELPER")
    print("=" * 70)
    print("This script will help you see all 8 collective worker terminals")
    print()

    # Check current processes
    check_terminal_processes()

    # Bring terminals to front
    bring_terminals_to_front()

    print("🎯 VISIBILITY TROUBLESHOOTING:")
    print("=" * 50)
    print("If you still don't see all 8 terminals:")
    print()
    print("1. 🍎 macOS Users:")
    print("   - Press F3 for Mission Control")
    print("   - Look for Terminal windows across spaces")
    print("   - Check Terminal app → Window menu")
    print()
    print("2. 🐧 Linux Users:")
    print("   - Use Alt+Tab to cycle through windows")
    print("   - Check workspace switcher")
    print()
    print("3. 🪟 Windows Users:")
    print("   - Use Alt+Tab to see all windows")
    print("   - Check taskbar for multiple cmd instances")
    print()
    print("4. 🔄 Manual Launch:")
    print("   - Open 8 terminal windows manually")
    print("   - Run 'python collective_worker_processor.py' in each")
    print()
    print("🚀 Your collective worker system is ready - let's get it visible!")


if __name__ == "__main__":
    main()
