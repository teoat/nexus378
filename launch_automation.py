#!/usr/bin/env python3
"""
🚀 LAUNCHER - CONSOLIDATED AUTOMATION SYSTEM 🚀

This script launches the consolidated automation system.
It provides a simple interface to start, stop, and monitor the automation engine.

Version: 1.0.0
Status: Production Ready
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path

# Add the automation directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "automation"))

# Import the automation engine
from core.automation_engine import AutomationEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AutomationLauncher:
    """Launcher for the consolidated automation system"""
    
    def __init__(self):
        self.engine = None
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_event.set()
    
    async def start(self):
        """Start the automation system"""
        try:
            logger.info("🚀 Starting Consolidated Automation System...")
            
            # Create and initialize the automation engine
            self.engine = AutomationEngine()
            
            # Start the engine
            await self.engine.run()
            
        except Exception as e:
            logger.error(f"❌ Failed to start automation system: {e}")
            raise
    
    async def stop(self):
        """Stop the automation system"""
        try:
            if self.engine:
                logger.info("🔄 Shutting down automation system...")
                await self.engine.shutdown()
                logger.info("✅ Automation system shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    async def run(self):
        """Main run loop"""
        try:
            # Start the system
            start_task = asyncio.create_task(self.start())
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            # Cancel start task if it's still running
            if not start_task.done():
                start_task.cancel()
                try:
                    await start_task
                except asyncio.CancelledError:
                    pass
            
            # Stop the system
            await self.stop()
            
        except Exception as e:
            logger.error(f"❌ Error in main run loop: {e}")
            raise

async def main():
    """Main entry point"""
    launcher = AutomationLauncher()
    
    try:
        await launcher.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
