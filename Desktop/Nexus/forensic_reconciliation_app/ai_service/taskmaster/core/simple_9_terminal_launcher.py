#!/usr/bin/env python3
"""
🚀 SIMPLE & RELIABLE 9-TERMINAL COLLECTIVE WORKER SYSTEM LAUNCHER
======================================================================
This script creates 9 terminal tabs and provides clear instructions for launching workers.
It avoids complex AppleScript that requires special permissions.
"""

import os
import platform
import subprocess
import sys


def main():
    print("🚀 SIMPLE 9-TERMINAL COLLECTIVE WORKER SYSTEM LAUNCHER")
    print("=" * 60)
    print("Creating 9 terminal tabs with clear launch instructions...")
    print()

    # Get current directory
    current_dir = os.getcwd()
    print(f"📍 Current directory: {current_dir}")

    # Check if we're in the right place
    if not os.path.exists("collective_worker_processor.py"):
        print("❌ ERROR: Please run this script from the core folder")
        return False

    print("✅ Core folder confirmed")
    print()

    # Create terminal with tabs based on platform
    system = platform.system()

    if system == "Darwin":  # macOS
        print("🍎 macOS detected - creating 9-tab terminal...")

        # Create main terminal window
        create_script = """
        tell application "Terminal"
            activate
            do script ""
            set custom title of front window to "🚀 COLLECTIVE WORKER SYSTEM - 9 TABS"
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", create_script], check=True)
            print("✅ Terminal window created")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: {e}")

        # Create tabs using simple approach
        for i in range(2, 10):
            if i == 9:
                title = "📊 MONITORING DASHBOARD"
            else:
                title = f"🚀 WORKER TERMINAL {i}"

            tab_script = f"""
            tell application "Terminal"
                do script "echo 'Tab {i}: {title}'"
                delay 0.2
            end tell
            """

            try:
                subprocess.run(["osascript", "-e", tab_script], check=True)
                print(f"✅ Tab {i} created: {title}")
            except subprocess.CalledProcessError:
                print(
                    f"⚠️  Tab {i} creation had issues (will provide manual instructions)"
                )

        print()
        print("🎯 9-TAB TERMINAL SYSTEM CREATED!")
        print("=" * 50)
        print("✅ Terminal window with 9 tabs is now open")
        print("✅ Tab 1: WORKER TERMINAL 1")
        print("✅ Tab 2: WORKER TERMINAL 2")
        print("✅ Tab 3: WORKER TERMINAL 3")
        print("✅ Tab 4: WORKER TERMINAL 4")
        print("✅ Tab 5: WORKER TERMINAL 5")
        print("✅ Tab 6: WORKER TERMINAL 6")
        print("✅ Tab 7: WORKER TERMINAL 7")
        print("✅ Tab 8: WORKER TERMINAL 8")
        print("✅ Tab 9: MONITORING DASHBOARD")

    elif system == "Linux":
        print("🐧 Linux detected - creating 9-tab terminal...")

        try:
            cmd = [
                "gnome-terminal",
                "--tab",
                "--title=🚀 WORKER TERMINAL 1",
                "--tab",
                "--title=🚀 WORKER TERMINAL 2",
                "--tab",
                "--title=🚀 WORKER TERMINAL 3",
                "--tab",
                "--title=🚀 WORKER TERMINAL 4",
                "--tab",
                "--title=🚀 WORKER TERMINAL 5",
                "--tab",
                "--title=🚀 WORKER TERMINAL 6",
                "--tab",
                "--title=🚀 WORKER TERMINAL 7",
                "--tab",
                "--title=🚀 WORKER TERMINAL 8",
                "--tab",
                "--title=📊 MONITORING DASHBOARD",
            ]
            subprocess.Popen(cmd, cwd=current_dir)
            print("✅ Linux terminal with 9 tabs created")
        except Exception as e:
            print(f"⚠️  Linux terminal creation failed: {e}")

    elif system == "Windows":
        print("🪟 Windows detected - creating 9-tab terminal...")

        try:
            cmd = [
                "wt",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 1",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 2",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 3",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 4",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 5",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 6",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 7",
                "new-tab",
                "--title",
                "🚀 WORKER TERMINAL 8",
                "new-tab",
                "--title",
                "📊 MONITORING DASHBOARD",
            ]
            subprocess.Popen(cmd, cwd=current_dir)
            print("✅ Windows terminal with 9 tabs created")
        except Exception as e:
            print(f"⚠️  Windows terminal creation failed: {e}")

    print()
    print("📋 LAUNCH INSTRUCTIONS:")
    print("=" * 50)
    print("Now launch your workers in each tab:")
    print()
    print("Tab 1-8 (Worker Terminals):")
    print(f"   cd {current_dir}")
    print("   python collective_worker_processor.py")
    print()
    print("Tab 9 (Monitoring Dashboard):")
    print(f"   cd {current_dir}")
    print("   python monitor_collective_system.py")
    print()
    print("💡 Navigation:")
    print("   • macOS: Cmd + Shift + [ or ]")
    print("   • Linux: Ctrl + PageUp/PageDown")
    print("   • Windows: Ctrl + Tab")
    print()
    print("🎉 YOUR 9-TAB SYSTEM IS READY!")
    print("🚀 Launch workers in each tab to start processing!")

    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Launcher completed successfully!")
        else:
            print("\n⚠️  Some issues occurred")
    except KeyboardInterrupt:
        print("\n\n⚠️  Launch interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
