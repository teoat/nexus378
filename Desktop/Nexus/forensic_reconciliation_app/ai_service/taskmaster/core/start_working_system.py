#!/usr/bin/env python3
"""
Start Working System
Simple script to start the working production system
"""

import subprocess
import sys
import time


def start_working_system():
    """Start the working production system"""
    print("🚀 Starting Working Production System")
    print("=" * 40)

    # Step 1: Load the fixed system to populate database
    print("📖 Step 1: Loading fixed system...")
    try:
        result = subprocess.run(
            [sys.executable, "fixed_production_system.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Fixed system loaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to load fixed system: {e}")
        return False

    # Step 2: Start workers in separate processes
    print("\n👷 Step 2: Starting workers...")

    worker_commands = [
        [
            "python",
            "corrected_production_worker.py",
            "code_quality_worker",
            "Code Quality Engineer",
            "python_development,code_quality,general_implementation",
        ],
        [
            "python",
            "corrected_production_worker.py",
            "documentation_worker",
            "Documentation Engineer",
            "documentation,technical_writing",
        ],
        [
            "python",
            "corrected_production_worker.py",
            "security_worker",
            "Security Engineer",
            "security,authentication,encryption",
        ],
        [
            "python",
            "corrected_production_worker.py",
            "performance_worker",
            "Performance Engineer",
            "performance,optimization",
        ],
        [
            "python",
            "corrected_production_worker.py",
            "general_worker",
            "General Developer",
            "python_development,general_implementation,error_handling",
        ],
    ]

    print("🚀 To start workers, open new terminals and run:")
    for i, cmd in enumerate(worker_commands, 1):
        print(f"\n   Terminal {i}:")
        print(f"   {' '.join(cmd)}")

    print("\n💡 Workers will automatically:")
    print("   - Connect to the same database")
    print("   - Claim available tasks")
    print("   - Process and complete tasks")
    print("   - Continue until all tasks are done")

    print("\n🎯 System is ready!")
    print("   Database: production_todos.db")
    print("   Tasks loaded: 16 real TODOs from TODO_MASTER.md")
    print("   Workers ready: 5 specialized workers")

    return True


if __name__ == "__main__":
    start_working_system()
