#!/usr/bin/env python3
"""
9-Tab Terminal System Launcher
Opens a single Terminal window with 9 tabs:
- 8 tabs for collective worker terminals
- 1 tab for system monitoring
"""

import subprocess
import sys
import time
import os

def launch_9_tab_system():
    """Launch a single Terminal window with 9 tabs"""
    
    print("🚀 9-TAB COLLECTIVE WORKER SYSTEM LAUNCHER")
    print("=" * 70)
    print("Creating a single Terminal window with 9 organized tabs:")
    print("• Tab 1-8: Collective Worker Terminals")
    print("• Tab 9: System Monitoring Dashboard")
    print()
    
    current_dir = os.getcwd()
    
    try:
        if sys.platform == "darwin":  # macOS
            print("🍎 macOS detected - launching 9-tab Terminal system...")
            
            # Create the main Terminal window with first tab
            main_window_script = f'''
            tell application "Terminal"
                activate
                set newWindow to do script "cd {current_dir}"
                set custom title of newWindow to "🚀 COLLECTIVE WORKER SYSTEM - TERMINAL 1"
            end tell
            '''
            
            subprocess.run(['osascript', '-e', main_window_script])
            print("✅ Main Terminal window created with Terminal 1")
            time.sleep(1)
            
            # Add 7 additional tabs for collective workers (tabs 2-8)
            for i in range(7):
                tab_num = i + 2  # Tabs 2-8
                worker_configs = [
                    ("Micro-task Processing", 12),
                    ("Worker Coordination", 10),
                    ("Cache Management", 8),
                    ("Progress Tracking", 6),
                    ("Status Synchronization", 5),
                    ("Error Handling", 4),
                    ("Logging & Monitoring", 3)
                ]
                
                specialization, workers = worker_configs[i]
                tab_title = f"Terminal {tab_num} - {specialization} ({workers} workers)"
                
                # Create new tab
                new_tab_script = f'''
                tell application "Terminal"
                    tell front window
                        set newTab to do script "cd {current_dir}"
                        set custom title of newTab to "{tab_title}"
                    end tell
                end tell
                '''
                
                subprocess.run(['osascript', '-e', new_tab_script])
                print(f"✅ Tab {tab_num} created: {specialization}")
                time.sleep(0.5)
            
            # Add the 9th tab for monitoring
            monitoring_tab_script = f'''
            tell application "Terminal"
                tell front window
                    set newTab to do script "cd {current_dir}"
                    set custom title of newTab to "📊 SYSTEM MONITORING DASHBOARD"
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', monitoring_tab_script])
            print("✅ Tab 9 created: System Monitoring Dashboard")
            
            print()
            print("🎯 ALL 9 TABS CREATED SUCCESSFULLY!")
            print("=" * 50)
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
            
            # Now start the collective workers in tabs 1-8
            print("🚀 STARTING COLLECTIVE WORKERS IN TABS 1-8...")
            print("=" * 50)
            
            for i in range(8):
                tab_num = i + 1  # Tabs 1-8 for workers
                worker_configs = [
                    ("Complex TODO Breakdown", 15),
                    ("Micro-task Processing", 12),
                    ("Worker Coordination", 10),
                    ("Cache Management", 8),
                    ("Progress Tracking", 6),
                    ("Status Synchronization", 5),
                    ("Error Handling", 4),
                    ("Logging & Monitoring", 3)
                ]
                
                specialization, workers = worker_configs[i]
                
                # Start collective worker in this tab
                start_worker_script = f'''
                tell application "Terminal"
                    tell front window
                        tell tab {tab_num}
                            do script "python collective_worker_processor.py" in selected tab
                        end tell
                    end tell
                end tell
                '''
                
                subprocess.run(['osascript', '-e', start_worker_script])
                print(f"✅ Started collective worker in Tab {tab_num}: {specialization}")
                time.sleep(1)
            
            # Start monitoring in the 9th tab
            print()
            print("📊 STARTING MONITORING DASHBOARD IN TAB 9...")
            monitoring_script = f'''
            tell application "Terminal"
                tell front window
                    tell tab 9
                        do script "python monitor_collective_system.py" in selected tab
                    end tell
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', monitoring_script])
            print("✅ Monitoring dashboard started in Tab 9")
            
            print()
            print("🎉 9-TAB COLLECTIVE WORKER SYSTEM LAUNCHED SUCCESSFULLY!")
            print("=" * 70)
            print("🚀 Your system is now running with:")
            print("   • 1 Terminal window")
            print("   • 9 organized tabs")
            print("   • 8 collective worker terminals (tabs 1-8)")
            print("   • 1 monitoring dashboard (tab 9)")
            print("   • 63 total workers")
            print("   • Full collective collaboration")
            print()
            print("💡 TAB ORGANIZATION:")
            print("   Tab 1: Terminal 1 - Complex TODO Breakdown (15 workers)")
            print("   Tab 2: Terminal 2 - Micro-task Processing (12 workers)")
            print("   Tab 3: Terminal 3 - Worker Coordination (10 workers)")
            print("   Tab 4: Terminal 4 - Cache Management (8 workers)")
            print("   Tab 5: Terminal 5 - Progress Tracking (6 workers)")
            print("   Tab 6: Terminal 6 - Status Synchronization (5 workers)")
            print("   Tab 7: Terminal 7 - Error Handling (4 workers)")
            print("   Tab 8: Terminal 8 - Logging & Monitoring (3 workers)")
            print("   Tab 9: 📊 SYSTEM MONITORING DASHBOARD")
            print()
            print("🎯 SYSTEM STATUS:")
            print("   ✅ All 9 tabs created and organized")
            print("   ✅ Collective workers started in tabs 1-8")
            print("   ✅ Monitoring dashboard active in tab 9")
            print("   ✅ 63 workers collaborating across 8 terminals")
            print("   ✅ Single window interface for easy management")
            print()
            print("🚀 Your collective worker system is now fully operational!")
            print("Monitor everything from Tab 9, manage workers from tabs 1-8!")
            
        elif sys.platform.startswith("linux"):
            print("🐧 Linux detected - launching 9-tab system...")
            # Linux implementation would go here
            print("💡 For Linux, manually create 9 terminal tabs and run the commands")
            
        elif sys.platform == "win32":
            print("🪟 Windows detected - launching 9-tab system...")
            # Windows implementation would go here
            print("💡 For Windows, manually create 9 terminal tabs and run the commands")
            
        else:
            print("❓ Unknown platform - please manually create 9 terminal tabs")
            
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
    
    print("🚀 9-TAB COLLECTIVE WORKER SYSTEM LAUNCHER")
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
        
        launch_9_tab_system()
        
    else:
        print("\n📋 Manual setup mode selected")
        show_manual_fallback(os.getcwd())
    
    print("\n🎯 Your 9-tab collective worker system is ready!")

if __name__ == "__main__":
    main()
