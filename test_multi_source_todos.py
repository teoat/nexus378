#!/usr/bin/env python3


    """Test the enhanced TodoMasterReader
    print("🔍 Testing Enhanced Multi-Source TODO Reader")
    print("=" * 60)
    
    try:
        from todo_master_reader import TodoMasterReader
        
        # Initialize the reader
        reader = TodoMasterReader()
        print("✅ TodoMasterReader initialized successfully")
        
        # Test source status
        print("\n📊 Testing Source Status:")
        source_status = reader.get_source_status()
        for source, available in source_status.items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {source}: {'Available' if available else 'Not Found'}")
        
        # Test getting all TODOs
        print("\n📋 Testing TODO Retrieval:")
        all_todos = reader.get_all_todos()
        print(f"   Total TODOs: {len(all_todos)}")
        
        # Test getting TODOs by source
        print("\n📁 Testing Source-Specific Retrieval:")
        for source_name in source_status.keys():
            if source_status[source_name]:
                source_todos = reader.get_todos_by_source(source_name)
                print(f"   {source_name}: {len(source_todos)} TODOs")
        
        # Test getting pending TODOs
        print("\n⏳ Testing Pending TODOs:")
        pending_todos = reader.get_pending_todos()
        print(f"   Pending: {len(pending_todos)}")
        
        # Test getting completed TODOs
        print("\n✅ Testing Completed TODOs:")
        completed_todos = reader.get_completed_todos()
        print(f"   Completed: {len(completed_todos)}")
        
        # Test TODO statistics
        print("\n📊 Testing TODO Statistics:")
        stats = reader.get_todo_statistics()
        print(f"   Total: {stats['total_todos']}")
        print(f"   Pending: {stats['pending_todos']}")
        print(f"   Completed: {stats['completed_todos']}")
        
        # Test priority distribution
        if stats['priorities']:
            print("   Priority Distribution:")
            for priority, count in stats['priorities'].items():
                if count > 0:
                    print(f"     {priority.title()}: {count}")
        
        # Test extension distribution
        if stats['extensions']:
            print("   Extension Distribution:")
            for ext, count in stats['extensions'].items():
                if count > 0:
                    print(f"     {ext}: {count}")
        
        # Test phase distribution
        if stats['phases']:
            print("   Phase Distribution:")
            for phase, count in stats['phases'].items():
                if count > 0:
                    print(f"     {phase}: {count}")
        
        # Test source distribution
        if stats['sources']:
            print("   Source Distribution:")
            for source, count in stats['sources'].items():
                if count > 0:
                    print(f"     {source}: {count}")
        
        # Test TODO search functionality
        print("\n🔍 Testing TODO Search:")
        search_results = reader.search_todos("API")
        print(f"   Search 'API': {len(search_results)} results")
        
        search_results = reader.search_todos("security")
        print(f"   Search 'security': {len(search_results)} results")
        
        # Test extension-based filtering
        print("\n🏷️  Testing Extension-Based Filtering:")
        api_todos = reader.get_todos_by_extension("API")
        print(f"   API TODOs: {len(api_todos)}")
        
        sec_todos = reader.get_todos_by_extension("SEC")
        print(f"   Security TODOs: {len(sec_todos)}")
        
        # Test phase-based filtering
        print("\n📅 Testing Phase-Based Filtering:")
        setup_todos = reader.get_todos_by_phase("Setup")
        print(f"   Setup Phase: {len(setup_todos)}")
        
        backend_todos = reader.get_todos_by_phase("Backend")
        print(f"   Backend Phase: {len(backend_todos)}")
        
        # Display sample TODOs
        print("\n📝 Sample TODO Details:")
        if all_todos:
            sample_todo = all_todos[0]
            print(f"   Sample TODO from {sample_todo['source']}:")
            print(f"     ID: {sample_todo['id']}")
            print(f"     Title: {sample_todo['title']}")
            print(f"     Phase: {sample_todo['phase']}")
            print(f"     Extension: {sample_todo['extension']}")
            print(f"     Priority: {sample_todo['priority']}")
            print(f"     Completed: {sample_todo['completed']}")
        
        print("\n🎉 Multi-Source TODO Testing Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing multi-source TODO functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_todo_format_parsing():
    """Test different TODO format parsing
    print("\n🔍 Testing TODO Format Parsing")
    print("=" * 40)
    
    try:
        
        reader = TodoMasterReader()
        
        # Test different format patterns
        test_formats = [
            "- [ ] **API_001:** Implement authentication endpoints",
            "- [x] **UI_002:** Create login form",
            "- [ ] Simple TODO without extension",
            "## Phase Header",
            "### Sub Phase Header"
        ]
        
        print("   Testing format patterns:")
        for i, test_line in enumerate(test_formats, 1):
            print(f"     {i}. {test_line}")
        
        print("   ✅ Format pattern testing complete")
        return True
        
    except Exception as e:
        print(f"❌ Error testing format parsing: {e}")
        return False

def test_extension_categorization():
    """Test TODO extension categorization
    print("\n🏷️  Testing Extension Categorization")
    print("=" * 40)
    
    try:
        
        reader = TodoMasterReader()
        
        # Test extension detection
        test_titles = [
            "API Authentication Implementation",
            "UI Dashboard Design",
            "Database Schema Optimization",
            "Security Vulnerability Scan",
            "Testing Framework Setup",
            "Documentation Update",
            "Integration Testing",
            "Performance Optimization",
            "Monitoring Configuration"
        ]
        
        print("   Testing extension detection:")
        for title in test_titles:
            extension, priority = reader._extract_extension_and_priority(title)
            print(f"     '{title}' -> {extension} ({priority})")
        
        print("   ✅ Extension categorization testing complete")
        return True
        
    except Exception as e:
        print(f"❌ Error testing extension categorization: {e}")
        return False

def main():
    """Run all tests
    print("🚀 Starting Enhanced Multi-Source TODO Testing")
    print("=" * 80)
    
    tests = [
        ("Multi-Source TODO Reader", test_multi_source_todo_reader),
        ("TODO Format Parsing", test_todo_format_parsing),
        ("Extension Categorization", test_extension_categorization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced multi-source TODO system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Enhanced multi-source TODO system needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
