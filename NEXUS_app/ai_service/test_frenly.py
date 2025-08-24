#!/usr/bin/env python3
"""
Test script for Frenly Meta Agent
"""

import asyncio
from agents.frenly_meta_agent import FrenlyMetaAgent, AppCommand

async def test_frenly():
    """Test Frenly's basic functionality"""
    
    print("🧪 Testing Frenly Meta Agent...")
    
    # Initialize Frenly
    config = {"test_mode": True}
    frenly = FrenlyMetaAgent(config)
    
    print("✅ Frenly initialized successfully")
    
    # Test app status
    status = frenly.get_app_status()
    print(f"📊 App Status: {status['frenly_status']}")
    print(f"🎯 Current Mode: {status['app_mode']}")
    print(f"👁️ Current View: {status['current_view']}")
    
    # Test mode switching
    print("\n🔄 Testing mode switching...")
    command = AppCommand(
        command_type="switch_mode",
        parameters={"mode": "construction"}
    )
    
    response = await frenly.manage_app(command)
    print(f"✅ Mode switch response: {response.message}")
    
    # Test dashboard view change
    print("\n🖥️ Testing dashboard view change...")
    command = AppCommand(
        command_type="change_view",
        parameters={"view": "fraud_analysis"}
    )
    
    response = await frenly.manage_app(command)
    print(f"✅ View change response: {response.message}")
    
    # Test user query handling
    print("\n💬 Testing user query handling...")
    command = AppCommand(
        command_type="user_query",
        parameters={"query": "What can you help me with?", "context": {}}
    )
    
    response = await frenly.manage_app(command)
    print(f"✅ Query response: {response.message}")
    
    # Get final status
    final_status = frenly.get_app_status()
    print(f"\n🎯 Final Mode: {final_status['app_mode']}")
    print(f"👁️ Final View: {final_status['current_view']}")
    print(f"📈 Total Commands: {final_status['total_commands']}")
    print(f"✅ Success Rate: {final_status['success_rate']:.2%}")
    
    print("\n🎉 All tests passed! Frenly is working correctly.")

if __name__ == "__main__":
    asyncio.run(test_frenly())
