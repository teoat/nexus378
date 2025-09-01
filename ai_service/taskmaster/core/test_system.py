#!/usr/bin/env python3
Test System - Verify all core components are working

This script tests the main components of the collective worker system:
1. TodoMasterReader
2. CollectiveWorkerProcessor
3. SystemIntegrationAPI
4. Monitor

    print("🔍 Testing TODO Master Reader...")

    try:

        reader = TodoMasterReader()

        # Test reading
        content = reader.read_todo_master()
        if content:
            print(f"✅ Successfully read TODO_MASTER.md ({len(content)} characters)")
        else:
            print("⚠️  No content found in TODO_MASTER.md")

        # Test parsing
        todos = reader.parse_markdown_content(content)
        print(f"✅ Parsed {len(todos)} TODO items")

        # Test getting pending TODOs
        pending = reader.get_pending_todos()
        print(f"✅ Found {len(pending)} pending TODOs")

        return True

    except Exception as e:
        print(f"❌ TODO Master Reader test failed: {e}")
        return False

def test_collective_worker_processor():

    print("🔧 Testing Collective Worker Processor...")

    try:

        # Initialize processor
        processor = CollectiveWorkerProcessor(max_workers=4)

        # Test system status
        status = processor.get_system_status()
        print(f"✅ System status retrieved: {len(status)} fields")

        # Test worker performance
        performance = processor.get_worker_performance()
        print(f"✅ Worker performance retrieved: {len(performance)} workers")

        return True

    except Exception as e:
        print(f"❌ Collective Worker Processor test failed: {e}")
        return False

def test_system_integration_api():

    print("🔌 Testing System Integration API...")

    try:

        # Create a mock processor
        class MockProcessor:

                return {"status": "mock", "workers": 4}

            def get_worker_performance(self):
                return {"worker_1": {"status": "idle"}}

        mock_processor = MockProcessor()

        # Initialize API
        api = SystemIntegrationAPI(mock_processor)

        # Test system status
        status = api.get_system_status()
        print(f"✅ API system status retrieved: {len(status)} fields")

        # Test integration status
        integration_status = api.get_integration_status()
        print(
            f"✅ Integration status retrieved: {len(integration_status)} integrations"
        )

        return True

    except Exception as e:
        print(f"❌ System Integration API test failed: {e}")
        return False

def test_monitor():

    print("📊 Testing Monitor component...")

    try:

        # Initialize monitor
        monitor = CollectiveSystemMonitor()

        # Test system status
        status = monitor.system_status
        print(f"✅ Monitor system status: {len(status)} fields")

        # Test worker status
        worker_status = monitor.worker_status
        print(f"✅ Monitor worker status: {len(worker_status)} workers")

        return True

    except Exception as e:
        print(f"❌ Monitor test failed: {e}")
        return False

def main():

    print("🚀 COLLECTIVE WORKER SYSTEM - COMPONENT TEST")
    print("=" * 60)

    tests = [
        ("TODO Master Reader", test_todo_master_reader),
        ("Collective Worker Processor", test_collective_worker_processor),
        ("System Integration API", test_system_integration_api),
        ("Monitor", test_monitor),
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

        time.sleep(1)  # Brief pause between tests

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
        print("🎉 All tests passed! System is ready to run.")
        print("\n🚀 To launch the system:")
        print("   python3 launch_macos_9_tabs.py")
        print("   or")
        print("   ./🚀_LAUNCH_9_TABS.command")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("🔧 Fix the issues before running the system.")

if __name__ == "__main__":
    main()
