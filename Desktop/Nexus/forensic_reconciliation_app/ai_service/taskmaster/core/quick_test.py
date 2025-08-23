#!/usr/bin/env python3
"""
Quick System Test
Tests core functionality before exiting demo mode
"""

from collective_worker_processor import CollectiveWorkerProcessor


def quick_test():
    """Run quick system test"""

    print("🧪 TESTING SYSTEM FUNCTIONALITY...")
    print("=" * 50)

    # Initialize processor
    processor = CollectiveWorkerProcessor(max_workers=8)

    # Test core functions
    print("1️⃣ Testing scanning...")
    scan = processor.scan_and_mark_todo_master()
    print(f"   Scan: {scan}")

    print("2️⃣ Testing auto-generation...")
    auto_gen = processor.auto_generate_work_items()
    print(f"   Auto-gen: {auto_gen}")

    print("3️⃣ Testing ML classification...")
    ml = processor.ml_classify_work_item("Implement user authentication")
    print(f'   ML: {ml.get("complexity", "unknown")}')

    print("4️⃣ Testing performance tracking...")
    perf = processor.track_performance_metrics()
    print(f"   Performance: {len(perf)} metrics")

    print("5️⃣ Testing collaboration...")
    collab = processor.get_collaboration_status()
    print(f"   Collaboration: {len(collab)} components")

    print("\n🎯 TEST RESULTS:")
    if all([scan, auto_gen, ml, perf, collab]):
        print("✅ ALL TESTS PASSED - System is operational!")
        print("🚀 Ready to exit demo mode and get real TODOs!")
        return True
    else:
        print("❌ Some tests failed - System needs attention")
        return False


if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 SYSTEM READY FOR PRODUCTION USE!")
    else:
        print("\n⚠️  SYSTEM NEEDS ATTENTION")
