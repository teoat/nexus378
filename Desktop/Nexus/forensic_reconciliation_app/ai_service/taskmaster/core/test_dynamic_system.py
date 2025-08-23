#!/usr/bin/env python3
"""
Test Dynamic Worker System - Verify the dynamic, collaborative worker system
"""

import sys
import time
from pathlib import Path

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_dynamic_worker_system():
    """Test the dynamic worker system components"""
    print("🧪 TESTING DYNAMIC WORKER SYSTEM")
    print("=" * 60)

    tests = [
        ("Dynamic Worker Coordinator", test_dynamic_coordinator),
        ("TODO Processing Engine", test_todo_engine),
        ("Task Breakdown Engine", test_breakdown_engine),
        ("Collective Worker Processor", test_collective_worker),
        ("System Integration", test_system_integration),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)

        try:
            success = test_func()
            results.append((test_name, success))

            if success:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")

        except Exception as e:
            print(f"💥 {test_name} test ERROR: {e}")
            results.append((test_name, False))

        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Dynamic system is ready to run.")
        print("\n🚀 To launch the 12-tab system:")
        print("   python3 launch_11_tab_system.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

    return passed == total


def test_dynamic_coordinator():
    """Test the dynamic worker coordinator"""
    try:
        from dynamic_worker_coordinator import DynamicWorkerCoordinator

        coordinator = DynamicWorkerCoordinator()

        # Test basic functionality
        status = coordinator.get_coordinator_status()
        if not isinstance(status, dict):
            return False

        # Test worker discovery (should work even with no workers)
        coordinator._discover_workers()

        # Test task analysis
        coordinator._analyze_available_tasks()

        print(f"   ✅ Coordinator initialized successfully")
        print(f"   ✅ Status retrieved: {len(status)} fields")
        print(f"   ✅ Worker discovery working")
        print(f"   ✅ Task analysis working")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_todo_engine():
    """Test the TODO processing engine"""
    try:
        from todo_processing_engine import TodoProcessingEngine

        engine = TodoProcessingEngine()

        # Test basic functionality
        status = engine.get_engine_status()
        if not isinstance(status, dict):
            return False

        print(f"   ✅ Engine initialized successfully")
        print(f"   ✅ Status retrieved: {len(status)} fields")
        print(f"   ✅ TODO Master path: {status.get('todo_master_path', 'Unknown')}")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_breakdown_engine():
    """Test the task breakdown engine"""
    try:
        from task_breakdown_engine import TaskBreakdownEngine

        engine = TaskBreakdownEngine()

        # Test basic functionality
        status = engine.get_engine_status()
        if not isinstance(status, dict):
            return False

        print(f"   ✅ Engine initialized successfully")
        print(f"   ✅ Status retrieved: {len(status)} fields")
        print(
            f"   ✅ Microtasks directory: {status.get('microtasks_directory', 'Unknown')}"
        )

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_collective_worker():
    """Test the collective worker processor"""
    try:
        from collective_worker_processor import CollectiveWorkerProcessor

        processor = CollectiveWorkerProcessor(max_workers=2)

        # Test basic functionality
        status = processor.get_system_status()
        performance = processor.get_worker_performance()

        if not isinstance(status, dict) or not isinstance(performance, dict):
            return False

        print(f"   ✅ Processor initialized successfully")
        print(f"   ✅ System status: {len(status)} fields")
        print(f"   ✅ Worker performance: {len(performance)} workers")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_system_integration():
    """Test system integration"""
    try:
        # Test if all components can work together
        from collective_worker_processor import CollectiveWorkerProcessor
        from todo_master_reader import TodoMasterReader

        # Test TODO reading
        reader = TodoMasterReader()
        todos = reader.get_pending_todos()

        if not isinstance(todos, list):
            return False

        print(f"   ✅ TODO reading working: {len(todos)} pending TODOs")

        # Test worker processor with TODO registry
        processor = CollectiveWorkerProcessor(max_workers=1)
        pending = processor.todo_registry.get_pending_todos()

        if not isinstance(pending, list):
            return False

        print(
            f"   ✅ Worker processor integration working: {len(pending)} pending TODOs"
        )

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_dynamic_worker_system()
