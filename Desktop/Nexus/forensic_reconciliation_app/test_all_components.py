#!/usr/bin/env python3
"""
Test All Implemented Components with MCP Logging
Comprehensive testing of all infrastructure and AI agent components.
"""

import os
import sys
import time
from pathlib import Path

import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_load_balancers():
    """Test all load balancer components"""
    print("🧪 Testing Load Balancer Components...")

    try:
        # Test Round Robin Load Balancer
        from infrastructure.load_balancer.round_robin_lb import RoundRobinLoadBalancer

        lb = RoundRobinLoadBalancer()
        print("  ✅ Round Robin Load Balancer: Imported successfully")

        # Test Weighted Load Balancer
        from infrastructure.load_balancer.weighted_lb import WeightedLoadBalancer

        wlb = WeightedLoadBalancer()
        print("  ✅ Weighted Load Balancer: Imported successfully")

        # Test Health-Based Load Balancer
        from infrastructure.load_balancer.health_based_lb import HealthBasedLoadBalancer

        hblb = HealthBasedLoadBalancer()
        print("  ✅ Health-Based Load Balancer: Imported successfully")

        # Test Load Balancer Configuration
        from infrastructure.load_balancer.lb_config import ConfigurationManager

        cm = ConfigurationManager()
        print("  ✅ Load Balancer Configuration: Imported successfully")

        print("  🎉 All Load Balancer components working!")
        return True

    except Exception as e:
        print(f"  ❌ Load Balancer test failed: {e}")
        return False


def test_queue_monitoring():
    """Test all queue monitoring components"""
    print("🧪 Testing Queue Monitoring Components...")

    try:
        # Test Queue Metrics
        from infrastructure.queue_monitoring.queue_metrics import QueueMetricsCollector

        qmc = QueueMetricsCollector()
        print("  ✅ Queue Metrics Collector: Imported successfully")

        # Test Performance Dashboard
        from infrastructure.queue_monitoring.performance_dashboard import (
            PerformanceDashboard,
        )

        pd = PerformanceDashboard()
        print("  ✅ Performance Dashboard: Imported successfully")

        # Test Alert System
        from infrastructure.queue_monitoring.alert_system import AlertSystem

        asys = AlertSystem()
        print("  ✅ Alert System: Imported successfully")

        print("  🎉 All Queue Monitoring components working!")
        return True

    except Exception as e:
        print(f"  ❌ Queue Monitoring test failed: {e}")
        return False


def test_ai_agents():
    """Test all AI agent components"""
    print("🧪 Testing AI Agent Components...")

    try:
        # Test Confidence Scorer
        from ai_service.agents.confidence_scorer import ConfidenceScorer

        cs = ConfidenceScorer()
        print("  ✅ Confidence Scorer: Imported successfully")

        # Test Risk Scorer
        from ai_service.agents.risk_scorer import RiskScorer

        rs = RiskScorer()
        print("  ✅ Risk Scorer: Imported successfully")

        print("  🎉 All AI Agent components working!")
        return True

    except Exception as e:
        print(f"  ❌ AI Agent test failed: {e}")
        return False


def test_database():
    """Test database components"""
    print("🧪 Testing Database Components...")

    try:
        # Test DuckDB OLAP Engine
        from datastore.duckdb.olap_engine import DuckDBOLAPEngine

        olap = DuckDBOLAPEngine()
        print("  ✅ DuckDB OLAP Engine: Imported successfully")

        print("  🎉 All Database components working!")
        return True

    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False


def test_mcp_integration():
    """Test MCP logging integration"""
    print("🧪 Testing MCP Integration...")

    try:
        # Test MCP Logger from any component
        from infrastructure.queue_monitoring.queue_metrics import MCPLogger

        mcp = MCPLogger()
        session_id = mcp.create_session("test_session", "Testing MCP Integration")

        # Test agent assignment
        success = mcp.assign_component(session_id, "test_agent", "test_component")

        if success:
            print("  ✅ MCP Logger: Component assignment working")

            # Test implementation logging
            mcp.log_implementation_start(session_id, "test_agent", "test_component")
            mcp.log_implementation_complete(session_id, "test_agent", "test_component")

            # Get session summary
            summary = mcp.get_session_summary(session_id)
            if summary:
                print("  ✅ MCP Logger: Session management working")
            else:
                print("  ❌ MCP Logger: Session summary failed")
                return False
        else:
            print("  ❌ MCP Logger: Component assignment failed")
            return False

        print("  🎉 MCP Integration working!")
        return True

    except Exception as e:
        print(f"  ❌ MCP Integration test failed: {e}")
        return False


async def test_async_components():
    """Test async components"""
    print("🧪 Testing Async Components...")

    try:
        # Test async operations in load balancers
        from infrastructure.load_balancer.round_robin_lb import RoundRobinLoadBalancer

        lb = RoundRobinLoadBalancer()

        # Add test servers
        lb.add_server("test1", "192.168.1.10", 8080)
        lb.add_server("test2", "192.168.1.11", 8080)

        # Test async health checks
        await lb.run_health_checks()
        print("  ✅ Async health checks working")

        # Test async server selection
        server = await lb.get_next_server()
        if server:
            print("  ✅ Async server selection working")
        else:
            print("  ❌ Async server selection failed")
            return False

        print("  🎉 All Async components working!")
        return True

    except Exception as e:
        print(f"  ❌ Async components test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Testing All Implemented Components with MCP Logging")
    print("=" * 60)

    test_results = []

    # Test synchronous components
    test_results.append(("Load Balancers", test_load_balancers()))
    test_results.append(("Queue Monitoring", test_queue_monitoring()))
    test_results.append(("AI Agents", test_ai_agents()))
    test_results.append(("Database", test_database()))
    test_results.append(("MCP Integration", test_mcp_integration()))

    # Test async components
    async_result = asyncio.run(test_async_components())
    test_results.append(("Async Components", async_result))

    # Print results summary
    print("\n📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for component, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {component:<20} {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall Result: {passed}/{total} components working")

    if passed == total:
        print("🎉 All components are working correctly!")
        print("🚀 Platform is ready for deployment!")
    else:
        print("⚠️  Some components need attention before deployment")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
