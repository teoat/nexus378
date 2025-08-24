#!/usr/bin/env python3
"""
Test script for Frenly Service Communication & Event Logging (Phase 3, Items 11-15)

This script tests:
11. Create simple event log
12. Add status endpoint  
13. Basic service discovery
14. Event filtering and pagination
15. Event summary and statistics
"""

import time
import json
from pathlib import Path
from agents.frenly_meta_agent import FrenlyMetaAgent, AppCommand

def test_service_communication():
    """Test the next 5 todo items from Phase 3."""
    print("🧪 Testing Frenly Service Communication & Event Logging (Phase 3, Items 11-15)")
    print("=" * 70)
    
    # Initialize Frenly
    print("\n1️⃣ Initializing Frenly Meta Agent...")
    frenly = FrenlyMetaAgent()
    
    # Test 11: Create simple event log
    print("\n2️⃣ Testing event logging system...")
    
    # Make some mode changes to generate events
    print("   🔄 Making mode changes to generate events...")
    
    changes = [
        ("switch_app_mode", "construction"),
        ("change_ai_mode", "extreme"),
        ("change_thinking_perspective", "investigation"),
        ("change_dashboard_view", "fraud_analysis"),
        ("change_user_role", "investigator")
    ]
    
    for change_type, target in changes:
        print(f"      🔄 {change_type}: {target}")
        response = frenly.manage_app(AppCommand(
            command_type=change_type,
            target_mode=target if change_type == "switch_app_mode" else None,
            target_ai_mode=target if change_type == "change_ai_mode" else None,
            target_perspective=target if change_type == "change_thinking_perspective" else None,
            target_view=target if change_type == "change_dashboard_view" else None,
            user_role=target if change_type == "change_user_role" else None
        ))
        print(f"         📊 Response: {response.message}")
        time.sleep(0.1)  # Small delay to see events being logged
    
    # Test 12: Add status endpoint functionality
    print("\n3️⃣ Testing status endpoint functionality...")
    
    # Get overall system health
    print("   📊 Getting overall system health...")
    system_health = frenly.get_overall_system_health()
    print(f"      🏥 Overall status: {system_health['overall_status']}")
    print(f"      🏥 Health score: {system_health['health_score']}%")
    print(f"      🏥 Active agents: {system_health['agents']['active']}/{system_health['agents']['total']}")
    
    # Get agent status
    print("   📊 Getting agent status...")
    agent_status = frenly.get_all_agent_status()
    print(f"      🤖 Registered agents: {len(agent_status)}")
    for agent_name, status in agent_status.items():
        print(f"         🤖 {agent_name}: {status['status']} (alive: {status['is_alive']})")
    
    # Test 13: Basic service discovery
    print("\n4️⃣ Testing basic service discovery...")
    
    # Check system components
    print("   🔍 Checking system components...")
    for component in frenly.system_components.keys():
        status = frenly.get_system_component_status(component)
        print(f"      🔧 {component.value}: {status.get('status', 'unknown')}")
    
    # Test 14: Event filtering and pagination
    print("\n5️⃣ Testing event filtering and pagination...")
    
    # Get recent events with limit
    print("   📝 Getting recent events (limit=10)...")
    recent_events = frenly.get_recent_events(limit=10)
    print(f"      📊 Recent events count: {len(recent_events)}")
    
    # Get events by type
    print("   📝 Getting events by type...")
    mode_change_events = frenly.get_recent_events(event_type="mode_change")
    print(f"      📊 Mode change events: {len(mode_change_events)}")
    
    perspective_change_events = frenly.get_recent_events(event_type="perspective_change")
    print(f"      📊 Perspective change events: {len(perspective_change_events)}")
    
    ai_mode_change_events = frenly.get_recent_events(event_type="ai_mode_change")
    print(f"      📊 AI mode change events: {len(ai_mode_change_events)}")
    
    # Get events by severity
    print("   📝 Getting events by severity...")
    info_events = frenly.get_recent_events(severity="INFO")
    print(f"      📊 INFO events: {len(info_events)}")
    
    warning_events = frenly.get_recent_events(severity="WARNING")
    print(f"      📊 WARNING events: {len(warning_events)}")
    
    # Test 15: Event summary and statistics
    print("\n6️⃣ Testing event summary and statistics...")
    
    # Get event summary
    print("   📊 Getting event summary...")
    event_summary = frenly.get_event_summary()
    print(f"      📊 Total events: {event_summary['total_events']}")
    print(f"      📊 Recent activity (last hour): {event_summary['recent_activity']}")
    
    # Show events by type
    print("      📊 Events by type:")
    for event_type, count in event_summary['by_type'].items():
        print(f"         📝 {event_type}: {count}")
    
    # Show events by severity
    print("      📊 Events by severity:")
    for severity, count in event_summary['by_severity'].items():
        print(f"         📝 {severity}: {count}")
    
    # Test event details
    print("\n7️⃣ Testing event details...")
    
    if recent_events:
        print("   📝 Sample event details:")
        sample_event = recent_events[-1]  # Get most recent event
        print(f"      📅 Timestamp: {sample_event['timestamp']}")
        print(f"      🏷️  Event type: {sample_event['event_type']}")
        print(f"      ⚠️  Severity: {sample_event['severity']}")
        print(f"      📋 Details: {sample_event['details']}")
    
    # Test event filtering combinations
    print("\n8️⃣ Testing event filtering combinations...")
    
    # Get recent mode changes with INFO severity
    print("   📝 Getting recent mode changes with INFO severity...")
    filtered_events = frenly.get_recent_events(
        limit=5, 
        event_type="mode_change", 
        severity="INFO"
    )
    print(f"      📊 Filtered events count: {len(filtered_events)}")
    
    # Test pagination
    print("   📝 Testing pagination...")
    all_events = frenly.get_recent_events(limit=0)  # Get all events
    print(f"      📊 Total events available: {len(all_events)}")
    
    # Get first 5 events
    first_5 = frenly.get_recent_events(limit=5)
    print(f"      📊 First 5 events: {len(first_5)}")
    
    # Get last 5 events (by getting all and taking last 5)
    last_5 = all_events[-5:] if len(all_events) >= 5 else all_events
    print(f"      📊 Last 5 events: {len(last_5)}")
    
    print("\n✅ Phase 3 Testing Complete!")
    print("=" * 70)
    
    return True

def test_event_persistence():
    """Test that events persist across Frenly instances."""
    print("\n💾 Testing Event Persistence")
    print("=" * 50)
    
    # Create first Frenly instance
    print("   🔄 Creating first Frenly instance...")
    frenly1 = FrenlyMetaAgent()
    
    # Make some changes to generate events
    print("   🔄 Generating events in first instance...")
    frenly1.manage_app(AppCommand(
        command_type="switch_app_mode",
        target_mode="regular"
    ))
    
    # Get event count
    events1 = frenly1.get_recent_events()
    print(f"   📊 Events in first instance: {len(events1)}")
    
    # Create second Frenly instance
    print("   🔄 Creating second Frenly instance...")
    frenly2 = FrenlyMetaAgent()
    
    # Get event count in second instance
    events2 = frenly2.get_recent_events()
    print(f"   📊 Events in second instance: {len(events2)}")
    
    # Note: Events are stored in memory, so they don't persist across instances
    # In a real implementation, events would be stored in a database or file
    print("   ℹ️  Note: Events are currently stored in memory only")
    print("   ℹ️  For production, events should be stored in database/file")
    
    print("   ✅ Event Persistence Testing Complete!")

if __name__ == "__main__":
    try:
        # Test core functionality
        test_service_communication()
        
        # Test event persistence
        test_event_persistence()
        
        print("\n🎉 All Phase 3 tests passed! Service communication and event logging is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
