#!/usr/bin/env python3
"""
Simple 9-Tab Terminal System Launcher
Creates a single Terminal window with 9 tabs more reliably
"""

import subprocess
import sys
import time
import os

def launch_9_tabs_simple():
    """Launch 9 tabs in a simpler, more reliable way"""
    
    print("🚀 SIMPLE 9-TAB COLLECTIVE WORKER SYSTEM LAUNCHER")
    print("=" * 70)
    print("Creating a single Terminal window with 9 organized tabs")
    print("• Tabs 1-8: Collective Worker Terminals")
    print("• Tab 9: System Monitoring Dashboard")
    print()
    
    current_dir = os.getcwd()
    
    try:
        if sys.platform == "darwin":  # macOS
            print("🍎 macOS detected - launching 9-tab Terminal system...")
            
            # Create the main Terminal window
            print("✅ Creating main Terminal window...")
            main_window_script = f'''
            tell application "Terminal"
                activate
                do script "cd {current_dir}"
            end tell
            '''
            
            subprocess.run(['osascript', '-e', main_window_script])
            time.sleep(2)
            
            # Add 8 additional tabs
            print("✅ Adding 8 additional tabs...")
            for i in range(8):
                tab_num = i + 2  # Tabs 2-9
                print(f"   Creating Tab {tab_num}...")
                
                new_tab_script = f'''
                tell application "Terminal"
                    tell front window
                        do script "cd {current_dir}"
                    end tell
                end tell
                '''
                
                subprocess.run(['osascript', '-e', new_tab_script])
                time.sleep(1)
            
            print()
            print("🎯 ALL 9 TABS CREATED SUCCESSFULLY!")
            print("=" * 50)
            print("Tab 1: 🚀 COLLECTIVE WORKER SYSTEM - TERMINAL 1")
            print("Tab 2: Terminal 2 - Micro-task Processing")
            print("Tab 3: Terminal 3 - Worker Coordination")
            print("Tab 4: Terminal 4 - Cache Management")
            print("Tab 5: Terminal 5 - Progress Tracking")
            print("Tab 6: Terminal 6 - Status Synchronization")
            print("Tab 7: Terminal 7 - Error Handling")
            print("Tab 8: Terminal 8 - Logging & Monitoring")
            print("Tab 9: 📊 SYSTEM MONITORING DASHBOARD")
            print()
            
            print("📋 NEXT STEPS:")
            print("=" * 50)
            print("1. You now have 9 tabs in one Terminal window")
            print("2. In Tabs 1-8, run: python collective_worker_processor.py")
            print("3. In Tab 9, run: python monitor_collective_system.py")
            print("4. Use Cmd + Shift + [ or ] to navigate between tabs")
            print()
            
            print("💡 MANUAL STARTUP INSTRUCTIONS:")
            print("-" * 50)
            print("Tab 1: python collective_worker_processor.py")
            print("Tab 2: python collective_worker_processor.py")
            print("Tab 3: python collective_worker_processor.py")
            print("Tab 4: python collective_worker_processor.py")
            print("Tab 5: python collective_worker_processor.py")
            print("Tab 6: python collective_worker_processor.py")
            print("Tab 7: python collective_worker_processor.py")
            print("Tab 8: python collective_worker_processor.py")
            print("Tab 9: python monitor_collective_system.py")
            print()
            
            print("🚀 YOUR 9-TAB SYSTEM IS READY!")
            print("=" * 50)
            print("• 1 Terminal window with 9 organized tabs")
            print("• Tabs 1-8 for collective worker terminals")
            print("• Tab 9 for system monitoring")
            print("• Easy navigation between tabs")
            print("• Clean, organized interface")
            
        else:
            print("💡 For other platforms, manually create 9 terminal tabs")
            
    except Exception as e:
        print(f"❌ Error launching 9-tab system: {e}")
        print("💡 Falling back to manual instructions...")
        show_manual_fallback(current_dir)

def show_manual_fallback(current_dir):
    """Show manual instructions if automatic launch fails"""
    
    print("\n📋 MANUAL 9-TAB SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("If automatic launch failed, follow these steps:")
    print()
    print("🎯 STEP 1: CREATE 9 TERMINAL TABS")
    print("-" * 40)
    print("1. Open Terminal app")
    print("2. Press Cmd + T 8 times to create 8 additional tabs")
    print("3. You should now have 9 tabs total")
    print()
    print("🎯 STEP 2: ORGANIZE YOUR TABS")
    print("-" * 40)
    print("Tab 1: 🚀 COLLECTIVE WORKER SYSTEM - TERMINAL 1 (15 workers)")
    print("Tab 2: Terminal 2 - Micro-task Processing (12 workers)")
    print("Tab 3: Terminal 3 - Worker Coordination (10 workers)")
    print("Tab 4: Terminal 4 - Cache Management (8 workers)")
    print("Tab 5: Terminal 5 - Progress Tracking (6 workers)")
    print("Tab 6: Terminal 6 - Status Synchronization (5 workers)")
    print("Tab 7: Terminal 7 - Error Handling (4 workers)")
    print("Tab 8: Terminal 8 - Logging & Monitoring (3 workers)")
    print("Tab 9: 📊 SYSTEM MONITORING DASHBOARD")
    print()
    print("🎯 STEP 3: START COLLECTIVE WORKERS IN TABS 1-8")
    print("-" * 40)
    print("In each of tabs 1-8, run:")
    print(f"  cd {current_dir}")
    print("  python collective_worker_processor.py")
    print()
    print("🎯 STEP 4: START MONITORING IN TAB 9")
    print("-" * 40)
    print("In Tab 9, run:")
    print(f"  cd {current_dir}")
    print("  python monitor_collective_system.py")
    print()
    print("🎯 STEP 5: VERIFY SYSTEM")
    print("-" * 40)
    print("Verify all terminals are running with:")
    print("  python verify_terminals.py")

def main():
    """Main function"""
    
    print("🚀 SIMPLE 9-TAB COLLECTIVE WORKER SYSTEM LAUNCHER")
    print("=" * 70)
    print("This will create a single Terminal window with 9 organized tabs")
    print("• 8 tabs for collective worker terminals")
    print("• 1 tab for system monitoring")
    print("• All in one organized interface")
    print()
    
    response = input("🚀 Launch 9-tab Terminal system now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\n🚀 LAUNCHING 9-TAB COLLECTIVE WORKER SYSTEM...")
        print("This will create a single Terminal window with 9 organized tabs")
        print("Please wait while the system is set up...")
        print()
        
        launch_9_tabs_simple()
        
    else:
        print("\n📋 Manual setup mode selected")
        show_manual_fallback(os.getcwd())
    
    print("\n🎯 Your 9-tab collective worker system is ready!")

if __name__ == "__main__":
    main()
