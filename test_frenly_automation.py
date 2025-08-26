#!/usr/bin/env python3
"""
Test script for Frenly Enhancement Automation System
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from frenly_enhancement_automation import FrenlyEnhancementAutomation
        print("✅ FrenlyEnhancementAutomation imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import FrenlyEnhancementAutomation: {e}")
        return False

def test_config_import():
    """Test if configuration can be imported"""
    print("🔍 Testing configuration import...")
    
    try:
        import frenly_automation_config
        print("✅ Configuration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False

def test_launcher_import():
    """Test if launcher can be imported"""
    print("🔍 Testing launcher import...")
    
    try:
        import launch_frenly_automation
        print("✅ Launcher imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import launcher: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("🔍 Testing file structure...")
    
    required_files = [
        "frenly_enhancement_automation.py",
        "frenly_automation_config.py",
        "launch_frenly_automation.py",
        "FRENLY_AUTOMATION_SYSTEM.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def test_frenly_todos():
    """Test if Frenly enhancement todos exist"""
    print("🔍 Testing Frenly enhancement todos...")
    
    todo_file = Path("forensic_reconciliation_app/FRENLY_ENHANCEMENT_TODO.md")
    if not todo_file.exists():
        print("❌ Frenly enhancement todo file not found")
        return False
    
    try:
        with open(todo_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count todo items
        todo_count = content.count('- [ ]')
        completed_count = content.count('- [x]')
        
        print(f"✅ Found {todo_count} pending todos and {completed_count} completed todos")
        return True
        
    except Exception as e:
        print(f"❌ Error reading todo file: {e}")
        return False

async def test_automation_system():
    """Test the automation system"""
    print("🔍 Testing automation system...")
    
    try:
        from frenly_enhancement_automation import FrenlyEnhancementAutomation
        
        # Create automation instance
        automation = FrenlyEnhancementAutomation()
        
        # Check if todos were loaded
        if not automation.tasks:
            print("❌ No tasks loaded from todo file")
            return False
        
        print(f"✅ Loaded {len(automation.tasks)} tasks")
        
        # Check if workers were initialized
        if not automation.workers:
            print("❌ No workers initialized")
            return False
        
        print(f"✅ Initialized {len(automation.workers)} workers")
        
        # Check worker types
        worker_types = list(automation.workers.keys())
        expected_types = ['workflow', 'machine-learning', 'frontend', 'backend', 'monitoring']
        
        for expected_type in expected_types:
            if expected_type not in worker_types:
                print(f"❌ Missing worker type: {expected_type}")
                return False
        
        print("✅ All expected worker types present")
        
        return True
        
    except Exception as e:
        print(f"❌ Automation system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Testing Frenly Enhancement Automation System")
    print("=" * 80)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Frenly Todos", test_frenly_todos),
        ("Module Imports", test_imports),
        ("Configuration Import", test_config_import),
        ("Launcher Import", test_launcher_import),
        ("Automation System", test_automation_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the automation system:")
        print("   python launch_frenly_automation.py")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
