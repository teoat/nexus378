#!/usr/bin/env python3
"""
Simple launcher for Frenly Enhancement Automation System
This script will start the automation system and keep it running
"""

import sys
import time
import signal
import asyncio
import threading
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path.cwd()))

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutdown signal received. Stopping automation system...")
    sys.exit(0)

async def main():
    """Main launcher function"""
    print("🚀 Starting Frenly Enhancement Automation System...")
    print("=" * 60)
    print("📊 System Configuration:")
    print("   • Workers: 9 specialized workers")
    print("   • Max Concurrent Tasks: 6")
    print("   • Max Tasks per Cycle: 8")
    print("   • Task Timeout: 30 minutes")
    print("   • Loop Interval: 30 seconds")
    print("=" * 60)
    
    try:
        # Import and initialize the automation system
        from frenly_enhancement_automation import FrenlyEnhancementAutomation
        
        print("✅ Successfully imported automation system")
        
        # Create automation instance
        automation = FrenlyEnhancementAutomation()
        print("✅ Automation system initialized")
        
        # Start the automation system
        print("🚀 Starting automation system...")
        await automation.start_automation_loop()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure frenly_enhancement_automation.py is in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting automation system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🔄 Frenly Automation Launcher")
    print("Press Ctrl+C to stop the system")
    print()
    
    # Start the automation system
    asyncio.run(main())
