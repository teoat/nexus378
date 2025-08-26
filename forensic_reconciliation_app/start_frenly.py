#!/usr/bin/env python3
"""
Startup script for Frenly integration testing.

This script starts the Frenly service and tests basic functionality.
"""

import uvicorn
import asyncio
import sys
import os
from pathlib import Path

# Add the ai_service directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_service'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_service', 'agents'))

def test_basic_imports():
    """Test basic imports to ensure everything is working."""
    print("🧪 Testing basic imports...")
    
    try:
        from ai_service.frenly_user_integration import FrenlyUserIntegration
        print("  ✅ User integration service: Import successful")
        
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent
        print("  ✅ Frenly meta agent: Import successful")
        
        from ai_service.frenly_api import frenly_router
        print("  ✅ Frenly API: Import successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_frenly_agent():
    """Test Frenly agent initialization."""
    print("\n🤖 Testing Frenly agent initialization...")
    
    try:
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent
        
        # Initialize Frenly
        frenly = FrenlyMetaAgent()
        print("  ✅ Frenly agent: Successfully initialized")
        
        # Check user integration
        if hasattr(frenly, 'user_integration') and frenly.user_integration is not None:
            print("  ✅ User integration: Available")
        else:
            print("  ⚠️  User integration: Not available (expected without main platform)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Frenly agent test failed: {e}")
        return False

def start_frenly_service():
    """Start the Frenly service."""
    print("\n🚀 Starting Frenly service...")
    
    try:
        # Import the main app
        from ai_service.main import app
        
        # Start the service
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,  # Use different port to avoid conflicts
            log_level="info"
        )
        
    except Exception as e:
        print(f"  ❌ Failed to start Frenly service: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Frenly Integration Startup Test")
    print("=" * 50)
    
    # Test 1: Basic imports
    imports_ok = test_basic_imports()
    
    # Test 2: Frenly agent
    agent_ok = test_frenly_agent()
    
    if not imports_ok or not agent_ok:
        print("\n❌ Basic tests failed. Cannot start service.")
        print("Please fix the import issues first.")
        return
    
    print("\n✅ All basic tests passed!")
    print("\n🎯 Starting Frenly service on port 8001...")
    print("You can test the integration at: http://localhost:8001")
    
    # Start the service
    start_frenly_service()

if __name__ == "__main__":
    main()
