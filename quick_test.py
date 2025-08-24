#!/usr/bin/env python3


    """Test basic imports for all core components
    print("🔍 Testing basic imports...")
    
    try:
        import psutil
        print("✅ psutil imported successfully")
    except ImportError:
        print("❌ psutil import failed")
        return False
    
    try:
        from queue_manager import QueueManager
        print("✅ QueueManager imported successfully")
    except ImportError:
        print("❌ QueueManager import failed")
        return False
    
    try:
        from todo_master_reader import TodoMasterReader
        print("✅ TodoMasterReader imported successfully")
    except ImportError:
        print("❌ TodoMasterReader import failed")
        return False
    
    try:
        from collective_worker_processor import CollectiveWorkerProcessor
        print("✅ CollectiveWorkerProcessor imported successfully")
    except ImportError:
        print("❌ CollectiveWorkerProcessor import failed")
        return False
    
    try:
        from task_breakdown_engine import TaskBreakdownEngine
        print("✅ TaskBreakdownEngine imported successfully")
    except ImportError:
        print("❌ TaskBreakdownEngine import failed")
        return False
    
    try:
        from dynamic_worker_coordinator import DynamicWorkerCoordinator
        print("✅ DynamicWorkerCoordinator imported successfully")
    except ImportError:
        print("❌ DynamicWorkerCoordinator import failed")
        return False
    
    try:
        from monitor_collective_system import CollectiveSystemMonitor
        print("✅ CollectiveSystemMonitor imported successfully")
    except ImportError:
        print("❌ CollectiveSystemMonitor import failed")
        return False
    
    print("✅ All basic imports successful")
    return True

def test_component_initialization():
    """Test component initialization
    print("🔍 Testing component initialization...")
    
    try:
        queue_manager = QueueManager()
        print("✅ QueueManager initialized")
    except Exception as e:
        print(f"❌ QueueManager initialization failed: {e}")
        return False
    
    try:
        todo_reader = TodoMasterReader()
        print("✅ TodoMasterReader initialized")
    except Exception as e:
        print(f"❌ TodoMasterReader initialization failed: {e}")
        return False
    
    try:
        worker_processor = CollectiveWorkerProcessor(max_workers=4)  # Test with 4 workers
        print("✅ CollectiveWorkerProcessor initialized")
    except Exception as e:
        print(f"❌ CollectiveWorkerProcessor initialization failed: {e}")
        return False
    
    try:
        task_engine = TaskBreakdownEngine()
        print("✅ TaskBreakdownEngine initialized")
    except Exception as e:
        print(f"❌ TaskBreakdownEngine initialization failed: {e}")
        return False
    
    try:
        coordinator = DynamicWorkerCoordinator()
        print("✅ DynamicWorkerCoordinator initialized")
    except Exception as e:
        print(f"❌ DynamicWorkerCoordinator initialization failed: {e}")
        return False
    
    try:
        monitor = CollectiveSystemMonitor()
        print("✅ CollectiveSystemMonitor initialized")
    except Exception as e:
        print(f"❌ CollectiveSystemMonitor initialization failed: {e}")
        return False
    
    print("✅ All components initialized successfully")
    return True

def test_todo_reading():
    """Test TODO reading functionality
    print("🔍 Testing TODO reading...")
    
    try:
        reader = TodoMasterReader()
        
        # Test getting all TODOs
        all_todos = reader.get_all_todos()
        print(f"✅ Found {len(all_todos)} TODOs")
        
        # Test getting pending TODOs
        pending_todos = reader.get_pending_todos()
        print(f"✅ Found {len(pending_todos)} pending TODOs")
        
        return True
        
    except Exception as e:
        print(f"❌ TODO reading test failed: {e}")
        return False

def main():
    """Run all tests
    print("🚀 Starting Quick System Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Component Initialization", test_component_initialization),
        ("TODO Reading", test_todo_reading)
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        return True
    else:
        print("⚠️  Some tests failed. System needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
