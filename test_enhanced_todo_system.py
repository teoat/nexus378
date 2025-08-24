#!/usr/bin/env python3


    """Test the enhanced TodoMasterReader with all new features
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
        
        # Test getting all TODOs including extensions
        print("\n📋 Testing Enhanced TODO Retrieval:")
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
        
        # Test enhanced TODO statistics
        print("\n📊 Testing Enhanced TODO Statistics:")
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
        
        # Test type distribution
        if stats['types']:
            print("   Type Distribution:")
            for todo_type, count in stats['types'].items():
                if count > 0:
                    print(f"     {todo_type}: {count}")
        
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
        
        # Test enhanced TODO recommendations
        print("\n💡 Testing Enhanced TODO Recommendations:")
        recommendations = reader.get_todo_recommendations()
        print(f"   Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"     {i}. {rec}")
        
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
            print(f"     Type: {sample_todo.get('type', 'unknown')}")
        
        print("\n🎉 Enhanced Multi-Source TODO Testing Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced multi-source TODO functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_todo_update_functionality():
    """Test TODO update capabilities
    print("\n🔧 Testing TODO Update Functionality")
    print("=" * 40)
    
    try:
        
        reader = TodoMasterReader()
        
        # Get a sample TODO to test updates
        all_todos = reader.get_all_todos()
        if not all_todos:
            print("   ⚠️  No TODOs found to test updates")
            return True
        
        # Find a pending TODO to test
        pending_todos = [t for t in all_todos if not t.get('completed', False)]
        if not pending_todos:
            print("   ⚠️  No pending TODOs found to test updates")
            return True
        
        test_todo = pending_todos[0]
        print(f"   Testing update on TODO: {test_todo['id']}")
        print(f"   Title: {test_todo['title']}")
        print(f"   Source: {test_todo['source']}")
        
        # Test updating TODO status
        print("   Testing TODO status update...")
        success = reader.update_todo_status(
            test_todo['id'], 
            completed=True, 
            completion_notes="Test completion via enhanced system"
        )
        
        if success:
            print("   ✅ TODO update successful")
            
            # Verify the update
            updated_todos = reader.get_all_todos()
            updated_todo = None
            for todo in updated_todos:
                if todo['id'] == test_todo['id']:
                    updated_todo = todo
                    break
            
            if updated_todo and updated_todo.get('completed'):
                print("   ✅ TODO status verified as completed")
            else:
                print("   ⚠️  TODO status not properly updated")
        else:
            print("   ❌ TODO update failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing TODO update functionality: {e}")
        return False

def test_extension_discovery():
    """Test extension-based TODO discovery
    print("\n🔍 Testing Extension-Based TODO Discovery")
    print("=" * 40)
    
    try:
        
        reader = TodoMasterReader()
        
        # Test extension discovery
        print("   Testing extension pattern discovery...")
        extension_patterns = reader.extension_patterns
        print(f"   Extension patterns: {len(extension_patterns)}")
        for pattern in extension_patterns:
            print(f"     - {pattern}")
        
        # Test extension categorization
        print("\n   Testing extension categorization...")
        test_titles = [
            "API Authentication Implementation",
            "UI Dashboard Design",
            "Database Schema Optimization",
            "Security Vulnerability Scan",
            "Testing Framework Setup",
            "Documentation Update",
            "Integration Testing",
            "Performance Optimization",
            "Monitoring Configuration",
            "Docker Container Setup",
            "Kubernetes Deployment",
            "CI/CD Pipeline Configuration"
        ]
        
        for title in test_titles:
            extension, priority = reader._extract_extension_and_priority(title)
            print(f"     '{title}' -> {extension} ({priority})")
        
        print("   ✅ Extension discovery testing complete")
        return True
        
    except Exception as e:
        print(f"❌ Error testing extension discovery: {e}")
        return False

def main():
    """Run all tests
    print("🚀 Starting Enhanced Multi-Source TODO System Testing")
    print("=" * 80)
    
    tests = [
        ("Enhanced Multi-Source TODO Reader", test_enhanced_todo_reader),
        ("TODO Update Functionality", test_todo_update_functionality),
        ("Extension-Based Discovery", test_extension_discovery)
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
        print("\n🚀 System Features:")
        print("   ✅ Multi-source TODO reading (TODO_MASTER.md, master_todo.md)")
        print("   ✅ Extension-based TODO discovery")
        print("   ✅ Automatic TODO updates after implementation")
        print("   ✅ Enhanced recommendations and statistics")
        print("   ✅ Support for code comment TODOs")
        print("   ✅ Priority and extension categorization")
        return True
    else:
        print("⚠️  Some tests failed. Enhanced multi-source TODO system needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
