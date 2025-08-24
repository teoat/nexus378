#!/usr/bin/env python3


    """Print startup banner
    print("=" * 80)
    print("🚀 AUTOMATED TODO IMPLEMENTATION LOOP")
    print("=" * 80)
    print("This system will continuously implement TODO items and run verification scripts")
    print("Press Ctrl+C to stop the loop")
    print("=" * 80)
    print()

def print_config():
    """Print current configuration
    print("📋 Current Configuration:")
    print(f"   Loop Interval: {LOOP_CONFIG['loop_interval']} seconds")
    print(f"   Max Implementations per Cycle: {LOOP_CONFIG['max_implementations_per_loop']}")
    print(f"   Implementation Timeout: {LOOP_CONFIG['implementation_timeout']} seconds")
    print(f"   Delay Between Implementations: {LOOP_CONFIG['delay_between_implementations']} seconds")
    print(f"   Implementations Directory: {LOOP_CONFIG['implementations_dir']}")
    print(f"   Log File: {LOOP_CONFIG['log_file']}")
    print()

async def main():
    """Main launcher function
        print("🚀 Starting Automated TODO Loop in 5 seconds...")
        print("Press Ctrl+C to cancel")
        
        for i in range(5, 0, -1):
            print(f"   Starting in {i}...")
            await asyncio.sleep(1)
        
        print("🚀 Starting now!")
        print()
        
        # Create and start automated loop
        automated_loop = AutomatedTODOLoop()
        
        # Override config with file settings
        automated_loop.loop_config.update({
            "loop_interval": LOOP_CONFIG["loop_interval"],
            "max_implementations_per_loop": LOOP_CONFIG["max_implementations_per_loop"],
            "implementation_timeout": LOOP_CONFIG["implementation_timeout"]
        })
        
        # Start the loop
        await automated_loop.start_continuous_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Automated loop interrupted by user")
        print("📊 Final summary will be displayed...")
        
        # Print summary if available
        if 'automated_loop' in locals():
            summary = automated_loop.get_implementation_summary()
            print(f"\n📊 Implementation Summary:")
            print(f"   Total Cycles: {summary['total_implementations']}")
            print(f"   Successful: {summary['successful_implementations']}")
            print(f"   Failed: {summary['failed_implementations']}")
            
            if summary['successful_implementations'] + summary['failed_implementations'] > 0:
                success_rate = (summary['successful_implementations'] / 
                              (summary['successful_implementations'] + summary['failed_implementations'])) * 100
                print(f"   Success Rate: {success_rate:.1f}%")
        
        print("\n🎯 Automated loop stopped")
        print("Check the 'implementations/' directory for generated files")
        print("Check the log file for detailed information")
        
    except Exception as e:
        print(f"\n💥 Automated loop failed: {e}")
        print("Check the logs for more details")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Launcher failed: {e}")
        sys.exit(1)
