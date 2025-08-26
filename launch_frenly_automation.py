#!/usr/bin/env python3
"""
🚀 Frenly Enhancement Automation Launcher
Launches the unified automation system for Frenly enhancement todos
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path.cwd()))

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 FRENLY ENHANCEMENT AUTOMATION SYSTEM")
    print("=" * 80)
    print("Unified automation system combining best features from all systems")
    print("Specifically designed for Frenly enhancement todos")
    print("=" * 80)
    print()

def print_config():
    """Print current configuration"""
    print("📋 System Configuration:")
    print("   • Max Concurrent Tasks: 3")
    print("   • Task Timeout: 30 minutes")
    print("   • Retry Attempts: 3")
    print("   • Loop Interval: 30 seconds")
    print("   • Max Tasks per Cycle: 5")
    print("   • Auto Recovery: Enabled")
    print("   • Performance Optimization: Enabled")
    print("   • Collaboration: Enabled")
    print()

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking system dependencies...")
    
    required_files = [
        "frenly_enhancement_automation.py",
        "frenly_automation_config.py",
        "forensic_reconciliation_app/FRENLY_ENHANCEMENT_TODO.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return False
    
    print("✅ All dependencies available")
    return True

def check_frenly_todos():
    """Check Frenly enhancement todos"""
    print("📋 Checking Frenly enhancement todos...")
    
    todo_file = Path("forensic_reconciliation_app/FRENLY_ENHANCEMENT_TODO.md")
    if not todo_file.exists():
        print("❌ Frenly enhancement todo file not found")
        return False
    
    try:
        with open(todo_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count todo items
        todo_count = content.count('- [ ]')
        completed_count = content.count('- [x]')
        
        print(f"✅ Found {todo_count} pending todos and {completed_count} completed todos")
        return True
        
    except Exception as e:
        print(f"❌ Error reading todo file: {e}")
        return False

async def main():
    """Main launcher function"""
    print_banner()
    print_config()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ System dependencies not met. Please check the missing files.")
        sys.exit(1)
    
    # Check Frenly todos
    if not check_frenly_todos():
        print("❌ Frenly enhancement todos not found. Please check the todo file.")
        sys.exit(1)
    
    print("🚀 Starting Frenly Enhancement Automation in 5 seconds...")
    print("Press Ctrl+C to cancel")
    print()
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        await asyncio.sleep(1)
    
    print("🚀 Starting now!")
    print()
    
    try:
        # Import and start the automation system
        from frenly_enhancement_automation import FrenlyEnhancementAutomation
        
        # Create automation instance
        automation = FrenlyEnhancementAutomation()
        
        # Start the automation loop
        await automation.start_automation_loop()
        
    except ImportError as e:
        print(f"❌ Failed to import automation system: {e}")
        print("Please ensure frenly_enhancement_automation.py is properly created")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Automation system failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Automation launcher interrupted by user")
        print("🎯 Automation system stopped")
    except Exception as e:
        print(f"\n💥 Launcher failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
