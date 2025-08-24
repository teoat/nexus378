#!/usr/bin/env python3


    """Test the enhanced TODO features
    print("🔍 Testing Enhanced Multi-Source TODO Features")
    print("=" * 50)
    
    try:
        from todo_master_reader import TodoMasterReader
        
        # Initialize the reader
        reader = TodoMasterReader()
        print("✅ TodoMasterReader initialized")
        
        # Test multi-source TODO reading
        print("\n📋 Testing Multi-Source TODO Reading:")
        all_todos = reader.get_all_todos()
        print(f"   Total TODOs: {len(all_todos)}")
        
        # Test source status
        source_status = reader.get_source_status()
        print("   Source Status:")
        for source, available in source_status.items():
            status_icon = "✅" if available else "❌"
            print(f"     {status_icon} {source}")
        
        # Test enhanced statistics
        print("\n📊 Testing Enhanced Statistics:")
        stats = reader.get_todo_statistics()
        print(f"   Total: {stats['total_todos']}")
        print(f"   Pending: {stats['pending_todos']}")
        print(f"   Completed: {stats['completed_todos']}")
        
        # Test extension distribution
        if stats['extensions']:
            print("   Extensions:")
            for ext, count in stats['extensions'].items():
                if count > 0:
                    print(f"     {ext}: {count}")
        
        # Test type distribution
        if stats['types']:
            print("   Types:")
            for todo_type, count in stats['types'].items():
                if count > 0:
                    print(f"     {todo_type}: {count}")
        
        # Test enhanced recommendations
        print("\n💡 Testing Enhanced Recommendations:")
        recommendations = reader.get_todo_recommendations()
        print(f"   Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"     {i}. {rec}")
        
        print("\n🎉 Enhanced Features Testing Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_features()
    sys.exit(0 if success else 1)
