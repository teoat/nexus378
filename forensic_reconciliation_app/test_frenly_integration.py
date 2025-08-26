#!/usr/bin/env python3
"""
Test script for Frenly integration with main Nexus platform.

This script tests the user integration service and API endpoints
to ensure proper connectivity and functionality.
"""

import asyncio
import requests
import json
from datetime import datetime
import sys
import os

# Add the ai_service directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_service'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_service', 'agents'))

def test_user_integration_service():
    """Test the user integration service directly."""
    print("🧪 Testing Frenly User Integration Service...")
    
    try:
        # Try to import the service
        try:
            from ai_service.frenly_user_integration import FrenlyUserIntegration
        except ImportError:
            print("  ❌ User integration service: Import failed")
            return False
        
        # Mock Frenly agent for testing
        class MockFrenlyAgent:
            def __init__(self):
                self.app_context = type('obj', (object,), {
                    'app_mode': type('obj', (object,), {'value': 'regular'}),
                    'ai_mode': type('obj', (object,), {'value': 'guided'}),
                    'dashboard_view': type('obj', (object,), {'value': 'reconciliation'})
                })()
            
            def manage_app(self, command):
                print(f"  Mock command execution: {command.command_type}")
                return type('obj', (object,), {'success': True})()
        
        frenly = MockFrenlyAgent()
        
        # Initialize user integration
        integration = FrenlyUserIntegration(frenly)
        
        # Test configuration
        integration.set_main_platform_config("http://localhost:8000")
        
        # Test integration status
        status = integration.get_integration_status()
        print(f"  ✅ Integration status: {status['main_platform_status']}")
        
        # Test user profile methods (will fail without main platform, but should handle gracefully)
        profile = integration.get_user_profile("test_user_123")
        if profile is None:
            print("  ✅ User profile handling: Graceful failure (expected without main platform)")
        
        # Test session creation (will fail without main platform, but should handle gracefully)
        session = integration.create_user_session("test_user_123", "test_token")
        if session is None:
            print("  ✅ Session creation handling: Graceful failure (expected without main platform)")
        
        print("  ✅ User integration service tests completed")
        return True
        
    except Exception as e:
        print(f"  ❌ User integration service test failed: {e}")
        return False

def test_frenly_api_endpoints():
    """Test the Frenly API endpoints."""
    print("\n🌐 Testing Frenly API Endpoints...")
    
    base_url = "http://localhost:8000/api/frenly"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health endpoint: Working")
        else:
            print(f"  ❌ Health endpoint: Failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Health endpoint: Connection failed - {e}")
    
    # Test user integration endpoints (will fail without main platform, but should handle gracefully)
    try:
        response = requests.get(f"{base_url}/users/integration/status", timeout=5)
        if response.status_code == 503:
            print("  ✅ User integration status: Service unavailable (expected without main platform)")
        else:
            print(f"  ⚠️  User integration status: Unexpected response {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ User integration status: Connection failed - {e}")
    
    # Test WebSocket status
    try:
        response = requests.get(f"{base_url}/websocket/status", timeout=5)
        if response.status_code == 200:
            print("  ✅ WebSocket status: Working")
        else:
            print(f"  ❌ WebSocket status: Failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ WebSocket status: Connection failed - {e}")

def test_frenly_meta_agent():
    """Test the Frenly meta agent with user integration."""
    print("\n🤖 Testing Frenly Meta Agent with User Integration...")
    
    try:
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent
        
        # Initialize Frenly (this will attempt to import user integration)
        frenly = FrenlyMetaAgent()
        
        # Check if user integration was initialized
        if hasattr(frenly, 'user_integration') and frenly.user_integration is not None:
            print("  ✅ User integration service: Successfully initialized")
        else:
            print("  ⚠️  User integration service: Not available (expected without main platform)")
        
        # Test basic functionality
        print("  ✅ Frenly meta agent: Successfully initialized")
        return True
        
    except Exception as e:
        print(f"  ❌ Frenly meta agent test failed: {e}")
        return False

def test_main_platform_connection():
    """Test connection to main Nexus platform."""
    print("\n🔗 Testing Main Platform Connection...")
    
    main_platform_url = "http://localhost:8000"
    
    try:
        # Test basic connectivity
        response = requests.get(f"{main_platform_url}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Main platform: Connected and healthy")
            return True
        else:
            print(f"  ⚠️  Main platform: Responding but unhealthy (status {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Main platform: Connection failed - {e}")
        print("  ℹ️  This is expected if the main platform is not running")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Frenly Integration Test Suite")
    print("=" * 50)
    
    # Check dependencies first
    print("📦 Checking dependencies...")
    try:
        import requests
        print("  ✅ requests: Available")
    except ImportError:
        print("  ❌ requests: Not available - install with: pip install requests")
        return
    
    try:
        import fastapi
        print("  ✅ fastapi: Available")
    except ImportError:
        print("  ❌ fastapi: Not available - install with: pip install fastapi")
        return
    
    print("  ✅ All required dependencies available")
    
    # Test 1: User integration service
    service_test = test_user_integration_service()
    
    # Test 2: Frenly API endpoints
    test_frenly_api_endpoints()
    
    # Test 3: Frenly meta agent
    agent_test = test_frenly_meta_agent()
    
    # Test 4: Main platform connection
    platform_test = test_main_platform_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if service_test and agent_test:
        print("✅ Core Integration Tests: PASSED")
        print("  - User integration service working")
        print("  - Frenly meta agent working")
    else:
        print("❌ Core Integration Tests: FAILED")
        print("  - Some core components have issues")
    
    if platform_test:
        print("✅ Main Platform: CONNECTED")
        print("  - Full integration available")
    else:
        print("⚠️  Main Platform: NOT CONNECTED")
        print("  - Integration tests will fail")
        print("  - Start main platform to test full integration")
    
    print("\n🎯 Next Steps:")
    if platform_test:
        print("  1. Test user profile synchronization")
        print("  2. Test session management")
        print("  3. Test cross-platform analytics")
    else:
        print("  1. Start the main Nexus platform")
        print("  2. Run this test again")
        print("  3. Verify full integration functionality")
    
    print("\n✨ Frenly Integration Test Suite Complete!")

if __name__ == "__main__":
    main()
