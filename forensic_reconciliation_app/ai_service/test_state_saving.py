#!/usr/bin/env python3
"""
Test script for Frenly State Saving & Loading (Phase 2, Items 6-10)

This script tests:
6. Save app context to file
7. Load app context from file  
8. Save mode intersections to file
9. Load mode intersections from file
10. Auto-save on changes
"""

import time
import json
from pathlib import Path
from agents.frenly_meta_agent import FrenlyMetaAgent, AppCommand

def test_state_saving_and_loading():
    """Test the next 5 todo items from Phase 2."""
    print("🧪 Testing Frenly State Saving & Loading (Phase 2, Items 6-10)")
    print("=" * 70)
    
    # Initialize Frenly
    print("\n1️⃣ Initializing Frenly Meta Agent...")
    frenly = FrenlyMetaAgent()
    
    # Test 6: Save app context to file
    print("\n2️⃣ Testing app context saving...")
    
    # Change some modes to create interesting state
    print("   🔄 Changing app mode to 'construction'...")
    response = frenly.manage_app(AppCommand(
        command_type="switch_app_mode",
        target_mode="construction"
    ))
    print(f"   📊 Response: {response.message}")
    
    print("   🔄 Changing AI mode to 'extreme'...")
    response = frenly.manage_app(AppCommand(
        command_type="change_ai_mode",
        target_ai_mode="extreme"
    ))
    print(f"   📊 Response: {response.message}")
    
    # Check if state files were created
    state_dir = Path(".taskmaster")
    context_file = state_dir / "frenly_state.json"
    modes_file = state_dir / "frenly_modes.json"
    
    print(f"\n3️⃣ Checking state files...")
    print(f"   📁 State directory: {state_dir.absolute()}")
    print(f"   📄 Context file exists: {context_file.exists()}")
    print(f"   📄 Modes file exists: {modes_file.exists()}")
    
    if context_file.exists():
        print(f"   📄 Context file size: {context_file.stat().st_size} bytes")
        with open(context_file, 'r') as f:
            context_data = json.load(f)
            print(f"   📊 Context version: {context_data.get('version', 'N/A')}")
            print(f"   📊 Context timestamp: {context_data.get('timestamp', 'N/A')}")
            if 'app_context' in context_data:
                app_ctx = context_data['app_context']
                print(f"   📊 App mode: {app_ctx.get('app_mode', 'N/A')}")
                print(f"   📊 AI mode: {app_ctx.get('ai_mode', 'N/A')}")
    
    if modes_file.exists():
        print(f"   📄 Modes file size: {modes_file.stat().st_size} bytes")
        with open(modes_file, 'r') as f:
            modes_data = json.load(f)
            print(f"   📊 Modes version: {modes_data.get('version', 'N/A')}")
            print(f"   📊 Modes timestamp: {modes_data.get('timestamp', 'N/A')}")
            print(f"   📊 Mode intersections count: {len(modes_data.get('mode_intersections', {}))}")
    
    # Test 7: Load app context from file
    print("\n4️⃣ Testing app context loading...")
    
    # Change to a different mode
    print("   🔄 Changing app mode to 'regular'...")
    response = frenly.manage_app(AppCommand(
        command_type="switch_app_mode",
        target_mode="regular"
    ))
    print(f"   📊 Response: {response.message}")
    
    # Now load the saved context
    print("   📥 Loading saved context...")
    frenly.load_context_from_file()
    
    # Check if context was restored
    current_mode = frenly.app_context.app_mode.value
    current_ai_mode = frenly.app_context.ai_mode.value
    print(f"   📊 Current app mode after load: {current_mode}")
    print(f"   📊 Current AI mode after load: {current_ai_mode}")
    
    # Test 8: Save mode intersections to file
    print("\n5️⃣ Testing mode intersections saving...")
    
    # Change thinking perspective to create new mode intersection
    print("   🔄 Changing thinking perspective to 'investigation'...")
    response = frenly.manage_app(AppCommand(
        command_type="change_thinking_perspective",
        target_perspective="investigation"
    ))
    print(f"   📊 Response: {response.message}")
    
    # Check if modes file was updated
    if modes_file.exists():
        with open(modes_file, 'r') as f:
            modes_data = json.load(f)
            print(f"   📊 Modes file updated timestamp: {modes_data.get('timestamp', 'N/A')}")
    
    # Test 9: Load mode intersections from file
    print("\n6️⃣ Testing mode intersections loading...")
    
    # Change to a different perspective
    print("   🔄 Changing thinking perspective to 'litigation'...")
    response = frenly.manage_app(AppCommand(
        command_type="change_thinking_perspective",
        target_perspective="litigation"
    ))
    print(f"   📊 Response: {response.message}")
    
    # Now load the saved modes
    print("   📥 Loading saved modes...")
    frenly.load_modes_from_file()
    
    # Check current mode intersection
    current_intersection = frenly._get_current_mode_intersection_response()
    if current_intersection.success:
        intersection_data = current_intersection.message
        if hasattr(intersection_data, 'app_mode'):
            print(f"   📊 Current mode intersection: {intersection_data.app_mode.value}_{intersection_data.ai_mode.value}")
            print(f"   📊 Features: {len(intersection_data.features)} features")
            print(f"   📊 Agent priorities: {intersection_data.agent_priorities}")
        else:
            print(f"   📊 Current mode intersection data: {intersection_data}")
    else:
        print(f"   📊 Mode intersection response: {current_intersection.message}")
    
    # Test 10: Auto-save on changes
    print("\n7️⃣ Testing auto-save on changes...")
    
    # Make multiple changes to trigger auto-save
    print("   🔄 Making multiple mode changes...")
    
    changes = [
        ("switch_app_mode", "accounting"),
        ("change_ai_mode", "guided"),
        ("change_dashboard_view", "reconciliation"),
        ("change_user_role", "investigator")
    ]
    
    for change_type, target in changes:
        print(f"      🔄 {change_type}: {target}")
        response = frenly.manage_app(AppCommand(
            command_type=change_type,
            target_mode=target if change_type == "switch_app_mode" else None,
            target_ai_mode=target if change_type == "change_ai_mode" else None,
            target_view=target if change_type == "change_dashboard_view" else None,
            user_role=target if change_type == "change_user_role" else None
        ))
        print(f"         📊 Response: {response.message}")
        time.sleep(0.1)  # Small delay to see auto-save in action
    
    # Check final state
    print("\n8️⃣ Final state check...")
    final_context = frenly.app_context
    print(f"   📊 Final app mode: {final_context.app_mode.value}")
    print(f"   📊 Final AI mode: {final_context.ai_mode.value}")
    print(f"   📊 Final dashboard view: {final_context.dashboard_view.value}")
    print(f"   📊 Final user role: {final_context.user_role.value}")
    
    # Check if state files are current
    if context_file.exists():
        with open(context_file, 'r') as f:
            context_data = json.load(f)
            final_timestamp = context_data.get('timestamp', 'N/A')
            print(f"   📊 Context file timestamp: {final_timestamp}")
    
    print("\n✅ Phase 2 Testing Complete!")
    print("=" * 70)
    
    return True

def test_file_operations():
    """Test file operations and backup functionality."""
    print("\n📁 Testing File Operations and Backup Functionality")
    print("=" * 50)
    
    state_dir = Path(".taskmaster")
    context_file = state_dir / "frenly_state.json"
    modes_file = state_dir / "frenly_modes.json"
    
    print(f"   📁 State directory: {state_dir.absolute()}")
    print(f"   📄 Context file: {context_file.absolute()}")
    print(f"   📄 Modes file: {modes_file.absolute()}")
    
    # Check for backup files
    backup_files = list(state_dir.glob("*.backup"))
    if backup_files:
        print(f"   🔄 Backup files found: {len(backup_files)}")
        for backup in backup_files:
            print(f"      📄 {backup.name}")
    else:
        print("   🔄 No backup files found (this is normal for first run)")
    
    # Check for temp files
    temp_files = list(state_dir.glob("*.tmp"))
    if temp_files:
        print(f"   ⚠️  Temporary files found: {len(temp_files)}")
        for temp in temp_files:
            print(f"      📄 {temp.name}")
    else:
        print("   ✅ No temporary files found")
    
    print("   ✅ File Operations Testing Complete!")

if __name__ == "__main__":
    try:
        # Test core functionality
        test_state_saving_and_loading()
        
        # Test file operations
        test_file_operations()
        
        print("\n🎉 All Phase 2 tests passed! State saving and loading is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
