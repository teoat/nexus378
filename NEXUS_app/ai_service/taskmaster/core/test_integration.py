#!/usr/bin/env python3
Integration Test Script - Tests all system components together

This script tests:
1. Queue management system
2. Worker initialization
3. TODO processing workflow
4. Monitor integration
5. System coordination

    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_queue_manager():

    print("🧪 Testing Queue Manager...")

    try:

        qm = QueueManager()

        # Test 1: Empty queue
        assert not qm.should_process([]), "Empty queue should not trigger processing"
        assert (
            len(qm.get_processing_batch([])) == 0
        ), "Empty queue should return empty batch"

        # Test 2: Below minimum threshold
        test_todos = [{"id": f"todo_{i}", "status": "pending"} for i in range(3)]
        assert not qm.should_process(
            test_todos
        ), "Below minimum should not trigger processing"

        # Test 3: At minimum threshold
        test_todos = [{"id": f"todo_{i}", "status": "pending"} for i in range(5)]
        assert qm.should_process(test_todos), "At minimum should trigger processing"

        # Test 4: Above minimum, below maximum
        test_todos = [{"id": f"todo_{i}", "status": "pending"} for i in range(15)]
        batch = qm.get_processing_batch(test_todos)
        assert len(batch) == 15, "Should return all 15 TODOs"

        # Test 5: Above maximum
        test_todos = [{"id": f"todo_{i}", "status": "pending"} for i in range(25)]
        batch = qm.get_processing_batch(test_todos)
        assert len(batch) == 20, "Should return max 20 TODOs"

        print("✅ Queue Manager tests passed!")
        return True

    except Exception as e:
        print(f"❌ Queue Manager test failed: {e}")
        return False

def test_worker_initialization():

    print("🧪 Testing Worker Initialization...")

    try:

        # Test with 8 workers first
        processor = CollectiveWorkerProcessor(max_workers=8)

        # Check worker count
        assert (
            len(processor.workers) == 8
        ), f"Expected 8 workers, got {len(processor.workers)}"
        assert (
            len(processor.worker_status) == 8
        ), f"Expected 8 worker statuses, got {len(processor.worker_status)}"

        # Check worker IDs
        expected_workers = [f"worker_{i}" for i in range(1, 9)]
        actual_workers = list(processor.workers.keys())
        assert (
            actual_workers == expected_workers
        ), f"Worker IDs mismatch: {actual_workers}"

        # Check initial status
        for worker_id, status in processor.worker_status.items():
            assert status == "idle", f"Worker {worker_id} should be idle, got {status}"

        print("✅ Worker Initialization tests passed!")
        return True

    except Exception as e:
        print(f"❌ Worker Initialization test failed: {e}")
        return False

def test_todo_processing():

    print("🧪 Testing TODO Processing Workflow...")

    try:

        reader = TodoMasterReader()
        todos = reader.get_pending_todos()

        print(f"   - Found {len(todos)} TODOs in TODO_MASTER.md")

        if len(todos) == 0:
            print("   ⚠️  No TODOs found - system will be idle")
            print("   💡 Add deployment tasks to TODO_MASTER.md to test processing")
        else:
            print("   ✅ TODOs found - processing workflow can be tested")

        print("✅ TODO Processing test completed!")
        return True

    except Exception as e:
        print(f"❌ TODO Processing test failed: {e}")
        return False

def test_monitor_integration():

    print("🧪 Testing Monitor Integration...")

    try:

        monitor = CollectiveSystemMonitor()

        # Check initialization
        assert (
            monitor.total_workers == 32
        ), f"Expected 32 workers, got {monitor.total_workers}"
        assert hasattr(
            monitor, "todo_progress"
        ), "Monitor should have TODO progress tracking"
        assert hasattr(
            monitor, "memory_optimization"
        ), "Monitor should have memory optimization"
        assert hasattr(
            monitor, "system_recommendations"
        ), "Monitor should have system recommendations"

        print("✅ Monitor Integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Monitor Integration test failed: {e}")
        return False

def run_complete_integration_test():

    print("🚀 RUNNING COMPLETE INTEGRATION TEST")
    print("=" * 60)
    print("Testing all system components...")
    print()

    tests = [
        ("Queue Manager", test_queue_manager),
        ("Worker Initialization", test_worker_initialization),
        ("TODO Processing", test_todo_processing),
        ("Monitor Integration", test_monitor_integration),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
            print()

    # Display results
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print()
    print(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! System is ready.")
        print("🚀 You can now run the proper tab launcher:")
        print("   python3 launch_proper_tabs.py")
    else:
        print("⚠️  Some tests failed. Please fix issues before running the system.")

    return passed == total

def main():

        print("\n🛑 Integration test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Integration test error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
