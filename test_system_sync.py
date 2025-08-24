#!/usr/bin/env python3


    """Test all critical imports
    print("🔍 Testing imports...")
    
    try:
        import psutil
        print("✅ psutil imported successfully")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    try:
        from queue_manager import QueueManager
        print("✅ QueueManager imported successfully")
    except ImportError as e:
        print(f"❌ QueueManager import failed: {e}")
        return False
    
    try:
        from todo_master_reader import TodoMasterReader
        print("✅ TodoMasterReader imported successfully")
    except ImportError as e:
        print(f"❌ TodoMasterReader import failed: {e}")
        return False
    
    try:
        from collective_worker_processor import CollectiveWorkerProcessor
        print("✅ CollectiveWorkerProcessor imported successfully")
    except ImportError as e:
        print(f"❌ CollectiveWorkerProcessor import failed: {e}")
        return False
    
    try:
        from task_breakdown_engine import TaskBreakdownEngine
        print("✅ TaskBreakdownEngine imported successfully")
    except ImportError as e:
        print(f"❌ TaskBreakdownEngine import failed: {e}")
        return False
    
    try:
        from todo_processing_engine import TodoProcessingEngine
        print("✅ TodoProcessingEngine imported successfully")
    except ImportError as e:
        print(f"❌ TodoProcessingEngine import failed: {e}")
        return False
    
    try:
        from dynamic_worker_coordinator import DynamicWorkerCoordinator
        print("✅ DynamicWorkerCoordinator imported successfully")
    except ImportError as e:
        print(f"❌ DynamicWorkerCoordinator import failed: {e}")
        return False
    
    try:
        from monitor_collective_system import CollectiveSystemMonitor
        print("✅ CollectiveSystemMonitor imported successfully")
    except ImportError as e:
        print(f"❌ CollectiveSystemMonitor import failed: {e}")
        return False
    
    print("✅ All imports successful")
    return True

def test_queue_manager():
    """Test QueueManager functionality
    print("\n🔍 Testing QueueManager...")
    
    try:
        
        # Initialize queue manager
        queue_manager = QueueManager()
        
        # Test queue limits
        assert queue_manager.min_todos == 5, f"Expected min_todos=5, got {queue_manager.min_todos}"
        assert queue_manager.max_todos == 20, f"Expected max_todos=20, got {queue_manager.max_todos}"
        
        print("✅ Queue limits configured correctly")
        
        # Test should_process logic
        should_process = queue_manager.should_process(3)  # Below minimum
        assert not should_process, f"Expected should_process=False for 3 TODOs, got {should_process}"
        
        should_process = queue_manager.should_process(10)  # Above minimum, below maximum
        assert should_process, f"Expected should_process=True for 10 TODOs, got {should_process}"
        
        should_process = queue_manager.should_process(25)  # Above maximum
        assert not should_process, f"Expected should_process=False for 25 TODOs, got {should_process}"
        
        print("✅ Queue processing logic working correctly")
        
        # Test batch processing
        test_todos = [f"test_todo_{i}" for i in range(15)]
        batch = queue_manager.get_processing_batch(test_todos)
        assert len(batch) <= 20, f"Expected batch size <= 20, got {len(batch)}"
        
        print("✅ Batch processing working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ QueueManager test failed: {e}")
        return False

def test_todo_master_reader():
    """Test TodoMasterReader functionality
    print("\n🔍 Testing TodoMasterReader...")
    
    try:
        
        # Initialize reader
        reader = TodoMasterReader()
        
        # Check if TODO_MASTER.md exists
        if not reader.todo_master_path.exists():
            print("⚠️  TODO_MASTER.md not found, creating test file")
            test_content = 
        assert len(todos) > 0, f"Expected some TODOs, got {len(todos)}"
        
        print(f"✅ Found {len(todos)} TODOs in TODO_MASTER.md")
        
        # Test pending TODOs
        pending = reader.get_pending_todos()
        assert len(pending) > 0, f"Expected pending TODOs, got {len(pending)}"
        
        print(f"✅ Found {len(pending)} pending TODOs")
        
        return True
        
    except Exception as e:
        print(f"❌ TodoMasterReader test failed: {e}")
        return False

def test_worker_processor():
    """Test CollectiveWorkerProcessor functionality
    print("\n🔍 Testing CollectiveWorkerProcessor...")
    
    try:
        
        # Initialize processor with reduced workers for testing
        processor = CollectiveWorkerProcessor(max_workers=4)  # Use 4 for testing
        
        # Check worker initialization
        assert len(processor.workers) == 4, f"Expected 4 workers, got {len(processor.workers)}"
        
        print("✅ Worker initialization successful")
        
        # Check processing interval
        assert processor.processing_interval == 10, f"Expected processing_interval=10, got {processor.processing_interval}"
        
        print("✅ Processing interval configured correctly")
        
        # Check queue manager integration
        assert hasattr(processor, 'queue_manager'), "QueueManager not integrated"
        
        print("✅ QueueManager integration verified")
        
        return True
        
    except Exception as e:
        print(f"❌ CollectiveWorkerProcessor test failed: {e}")
        return False

def test_task_breakdown_engine():
    """Test TaskBreakdownEngine functionality
    print("\n🔍 Testing TaskBreakdownEngine...")
    
    try:
        
        # Initialize engine
        engine = TaskBreakdownEngine()
        
        # Check breakdown interval
        assert engine.breakdown_interval == 10, f"Expected breakdown_interval=10, got {engine.breakdown_interval}"
        
        print("✅ Breakdown interval configured correctly")
        
        # Check microtask settings
        assert hasattr(engine, 'microtask_settings'), "Microtask settings not found"
        assert engine.microtask_settings['max_microtasks_per_todo'] == 20, "Max microtasks not set correctly"
        
        print("✅ Microtask settings configured correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ TaskBreakdownEngine test failed: {e}")
        return False

def test_dynamic_coordinator():
    """Test DynamicWorkerCoordinator functionality
    print("\n🔍 Testing DynamicWorkerCoordinator...")
    
    try:
        
        # Initialize coordinator
        coordinator = DynamicWorkerCoordinator()
        
        # Check capacity limits
        assert coordinator.max_active_tasks == 5, f"Expected max_active_tasks=5, got {coordinator.max_active_tasks}"
        assert coordinator.max_total_todos == 12, f"Expected max_total_todos=12, got {coordinator.max_total_tasks}"
        
        print("✅ Capacity limits configured correctly")
        
        # Check coordination stats
        assert hasattr(coordinator, 'coordination_stats'), "Coordination stats not found"
        
        print("✅ Coordination stats initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ DynamicWorkerCoordinator test failed: {e}")
        return False

def test_monitor():
    """Test CollectiveSystemMonitor functionality
    print("\n🔍 Testing CollectiveSystemMonitor...")
    
    try:
        
        # Initialize monitor
        monitor = CollectiveSystemMonitor()
        
        # Check total workers
        assert monitor.total_workers == 32, f"Expected total_workers=32, got {monitor.total_workers}"
        
        print("✅ Total workers configured correctly")
        
        # Check monitoring capabilities
        assert hasattr(monitor, 'todo_progress'), "TODO progress tracking not found"
        assert hasattr(monitor, 'system_recommendations'), "System recommendations not found"
        
        print("✅ Enhanced monitoring capabilities verified")
        
        return True
        
    except Exception as e:
        print(f"❌ CollectiveSystemMonitor test failed: {e}")
        return False

def test_system_integration():
    """Test system integration
    print("\n🔍 Testing System Integration...")
    
    try:
        # Test that all components can work together
        
        # Initialize components
        queue_manager = QueueManager()
        reader = TodoMasterReader()
        processor = CollectiveWorkerProcessor(max_workers=4)
        
        # Test workflow
        todos = reader.get_pending_todos()
        if todos:
            # Test queue processing
            should_process = queue_manager.should_process(len(todos))
            print(f"✅ Queue processing decision: {should_process} for {len(todos)} TODOs")
        
        print("✅ System integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        return False

def main():
    """Run all tests
    print("🚀 Starting Comprehensive System Synchronization Test")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Queue Manager", test_queue_manager),
        ("TODO Master Reader", test_todo_master_reader),
        ("Worker Processor", test_worker_processor),
        ("Task Breakdown Engine", test_task_breakdown_engine),
        ("Dynamic Coordinator", test_dynamic_coordinator),
        ("System Monitor", test_monitor),
        ("System Integration", test_system_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is fully synchronized.")
        return True
    else:
        print("⚠️  Some tests failed. System needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
