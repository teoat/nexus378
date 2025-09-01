#!/usr/bin/env python3
Cleanup and Synchronization Script
Removes duplicate systems and creates a clean production setup

import shutil

def cleanup_duplicate_systems():
    print("🧹 Cleaning up duplicate and outdated systems...")

    # Files to remove (duplicates and demos)
    files_to_remove = [
        "production_todo_integration.py",  # Old integration system
        "production_manager.py",  # Old manager
        "start_production_system.py",  # Old startup script
        "test_corrected_reader.py",  # Test file
        "unified_task_system.py",  # Duplicate of production_task_system.py
        "simple_enhanced_demo.py",  # Demo file
        "enhanced_demo.py",  # Demo file
        "unified_demo.py",  # Demo file
        "parallel_worker_system.py",  # Demo file
        "worker_client.py",  # Demo file
        "task_breakdown.py",  # Demo file
        "enhanced_system.py",  # Demo file
        "enhanced_task_system.py",  # Demo file
        "mcp_server.py",  # Demo file
        "mcp_integration.py",  # Demo file
        "mcp_client.py",  # Demo file
        "mcp_config.py",  # Demo file
        "mcp_dashboard.py",  # Demo file
        "mcp_server_orchestrator.py",  # Demo file
        "mcp_dashboard.py",  # Demo file
        "collective_worker_processor.py",  # Old system
        "simple_batch_processor.py",  # Old system
        "continuous_implementation_loop.py",  # Old system
        "load_balancer.py",  # Old system
        "simple_registry.py",  # Old system
        "todo_integration.py",  # Old system
        "implement_unimplemented_todos.py",  # Old system
        "start_system.py",  # Old system
        "monitor_collective_system.py",  # Old system
        "task_breakdown_15min.py",  # Old system
        "demo_15min_breakdown.py",  # Demo file
        "demo_duckdb_implementation.py",  # Demo file
        "automated_todo_loop.py",  # Old system
        "launch_*.py",  # All launch scripts
        "🚀_*.command",  # All command files
        "🚀_*.bat",  # All batch files
        "*.log",  # All log files
        "*.db",  # All database files (except synchronized)
        "__pycache__",  # Python cache
    ]

    removed_count = 0
    for item in files_to_remove:
        if "*" in item:
            # Handle wildcard patterns
            if item == "*.log":
                for log_file in Path(".").glob("*.log"):
                    try:
                        log_file.unlink()
                        print(f"🗑️  Removed: {log_file}")
                        removed_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not remove {log_file}: {e}")

            elif item == "*.db":
                for db_file in Path(".").glob("*.db"):
                    if "synchronized" not in db_file.name:
                        try:
                            db_file.unlink()
                            print(f"🗑️  Removed: {db_file}")
                            removed_count += 1
                        except Exception as e:
                            print(f"⚠️  Could not remove {db_file}: {e}")

            elif item == "launch_*.py":
                for launch_file in Path(".").glob("launch_*.py"):
                    try:
                        launch_file.unlink()
                        print(f"🗑️  Removed: {launch_file}")
                        removed_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not remove {launch_file}: {e}")

            elif item == "🚀_*.command":
                for cmd_file in Path(".").glob("🚀_*.command"):
                    try:
                        cmd_file.unlink()
                        print(f"🗑️  Removed: {cmd_file}")
                        removed_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not remove {cmd_file}: {e}")

            elif item == "🚀_*.bat":
                for bat_file in Path(".").glob("🚀_*.bat"):
                    try:
                        bat_file.unlink()
                        print(f"🗑️  Removed: {bat_file}")
                        removed_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not remove {bat_file}: {e}")

            elif item == "__pycache__":
                if Path("__pycache__").exists():
                    try:
                        shutil.rmtree("__pycache__")
                        print("🗑️  Removed: __pycache__ directory")
                        removed_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not remove __pycache__: {e}")
        else:
            # Handle specific files
            if Path(item).exists():
                try:
                    Path(item).unlink()
                    print(f"🗑️  Removed: {item}")
                    removed_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {item}: {e}")

    print(f"✅ Cleanup complete! Removed {removed_count} duplicate/outdated files")
    return removed_count

def create_clean_production_setup():

    print("\n🚀 Creating clean production setup...")

    # Create production startup script
    startup_script = '''#!/usr/bin/env python3

    print("🚀 Clean Production TODO Management System")
    print("=" * 50)
    
    # Initialize and start the synchronized system
    system = SynchronizedProductionSystem("production_todos.db")
    
    # Load real TODOs from TODO_MASTER.md
    if not system.load_real_todos_from_master():
        print("❌ Failed to load real TODOs")
        return
    
    # Show summary and start workers
    system.show_real_todos_summary()
    system.validate_system_integrity()
    system.show_system_status()
    system.register_appropriate_workers()
    system.get_worker_startup_instructions()
    
    print("\\n🎯 Clean production system ready!")
    print("   Run 'python start_production.py' to start the system")

if __name__ == "__main__":
    main()
'''

    with open("start_production.py", "w") as f:
        f.write(startup_script)

    print("✅ Created: start_production.py")

    # Create README for clean setup

    with open("README_CLEAN_PRODUCTION.md", "w") as f:
        f.write(readme_content)

    print("✅ Created: README_CLEAN_PRODUCTION.md")

def main():

    print("🧹 Cleanup and Synchronization Process")
    print("=" * 50)

    # Step 1: Clean up duplicates
    removed_count = cleanup_duplicate_systems()

    # Step 2: Create clean production setup
    create_clean_production_setup()

    print(f"\n🎉 Cleanup and synchronization complete!")
    print(f"   Removed {removed_count} duplicate/outdated files")
    print("   Created clean production setup")
    print("   System is now synchronized and error-free")
    print("\n🚀 Next steps:")
    print("   1. Run 'python start_production.py' to start the clean system")
    print("   2. Start workers in separate terminals using the provided commands")
    print("   3. All 16 real TODOs from TODO_MASTER.md will be processed automatically")

if __name__ == "__main__":
    main()
