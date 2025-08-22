#!/usr/bin/env python3
"""
Multi-Terminal Infinite Processing Launcher
Shows commands to run multiple instances manually
"""

import os
import sys

def show_multi_terminal_commands(num_instances=3):
    """Show commands to run multiple terminal instances"""
    
    print("🚀 MULTI-TERMINAL INFINITE PROCESSING COMMANDS")
    print("=" * 70)
    print(f"To run {num_instances} instances of the infinite processing system:")
    print("Each instance will run independently in its own terminal")
    print()
    
    # Configuration for different instances - optimized for 8 terminals
    base_configs = [
        {'max_workers': 15, 'min_batch_size': 8, 'max_batch_size': 120},   # Instance 1: High capacity
        {'max_workers': 12, 'min_batch_size': 6, 'max_batch_size': 100},   # Instance 2: High capacity
        {'max_workers': 10, 'min_batch_size': 5, 'max_batch_size': 80},    # Instance 3: Medium-high
        {'max_workers': 8, 'min_batch_size': 4, 'max_batch_size': 60},     # Instance 4: Medium
        {'max_workers': 6, 'min_batch_size': 3, 'max_batch_size': 40},     # Instance 5: Medium
        {'max_workers': 5, 'min_batch_size': 2, 'max_batch_size': 30},     # Instance 6: Light
        {'max_workers': 4, 'min_batch_size': 2, 'max_batch_size': 25},     # Instance 7: Light
        {'max_workers': 3, 'min_batch_size': 1, 'max_batch_size': 20},     # Instance 8: Ultra-light
    ]
    
    # Use only the configurations we need
    instance_configs = base_configs[:num_instances]
    
    print("🎯 INSTANCE CONFIGURATIONS:")
    print("=" * 50)
    
    for i, config in enumerate(instance_configs):
        instance_id = i + 1
        print(f"Instance #{instance_id}:")
        print(f"  - Workers: {config['max_workers']}")
        print(f"  - Batch Size: {config['min_batch_size']}-{config['max_batch_size']}")
        print()
    
    total_workers = sum(config['max_workers'] for config in instance_configs)
    print(f"🚀 Total processing power: {total_workers} workers")
    print()
    
    print("📋 MANUAL TERMINAL COMMANDS:")
    print("=" * 50)
    print(f"Open {num_instances} terminal windows/tabs and run these commands:")
    print()
    
    current_dir = os.getcwd()
    
    for i in range(num_instances):
        instance_id = i + 1
        config = instance_configs[i]
        
        print(f"Terminal {instance_id}:")
        print(f"  cd {current_dir}")
        print(f"  python start_system.py")
        print()
    
    print("💡 EACH INSTANCE WILL:")
    print("  🔄 Process TODOs continuously")
    print("  📥 Auto-load next TODOs automatically")
    print("  ♾️  Run FOREVER until manually stopped")
    print("  📊 Show real-time progress and statistics")
    print("  🔗 Update shared TODO master registry")
    print()
    
    print("🎯 BENEFITS OF 8-TERMINAL SETUP:")
    print("  🚀 Massive parallel processing ({total_workers} total workers)")
    print("  📊 Independent monitoring per instance")
    print("  🔧 Different configurations for different workloads")
    print("  🔄 True infinite processing across all instances")
    print("  🔗 Shared TODO master integration")
    print("  ⚡ No resource conflicts between instances")
    print()
    
    print("🛑 TO STOP ANY INSTANCE:")
    print("  Press Ctrl+C in that terminal window")
    print("  Other instances will continue running independently")
    print("  TODO master registry stays synchronized")
    print()
    
    print("🚀 READY TO LAUNCH 8 TERMINALS!")
    print("Open your terminal windows and run the commands above")
    print("Each instance will start processing TODOs infinitely!")
    print("All instances will update the shared TODO master registry!")

if __name__ == "__main__":
    # Default to 3 instances, but can be customized
    num_instances = 3
    
    if len(sys.argv) > 1:
        try:
            num_instances = int(sys.argv[1])
            if num_instances < 1 or num_instances > 10:
                print("⚠️  Number of instances should be between 1-10. Using default: 3")
                num_instances = 3
        except ValueError:
            print("⚠️  Invalid number of instances. Using default: 3")
            num_instances = 3
    
    show_multi_terminal_commands(num_instances)
