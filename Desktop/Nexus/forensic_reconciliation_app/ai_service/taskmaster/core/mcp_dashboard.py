#!/usr/bin/env python3
"""
MCP Server Dashboard for Forensic Reconciliation App
Comprehensive status monitoring and progress tracking
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server_orchestrator import MCPServerOrchestrator

logger = logging.getLogger(__name__)


class MCPDashboard:
    """Comprehensive MCP server dashboard"""
    
    def __init__(self):
        self.orchestrator = MCPServerOrchestrator()
        self.dashboard_status = "initializing"
        self.refresh_interval = 5  # seconds
        
    async def start_dashboard(self):
        """Start the MCP dashboard"""
        try:
            logger.info("Starting MCP Dashboard...")
            
            # Initialize orchestrator
            await self.orchestrator.start_all_servers()
            
            self.dashboard_status = "running"
            logger.info("MCP Dashboard started successfully")
            
            # Start monitoring
            await self._run_dashboard()
            
        except Exception as e:
            logger.error(f"Failed to start MCP Dashboard: {e}")
            self.dashboard_status = "failed"
    
    async def _run_dashboard(self):
        """Run the main dashboard loop"""
        try:
            while self.dashboard_status == "running":
                # Clear screen (platform independent)
                self._clear_screen()
                
                # Display dashboard
                self._display_dashboard_header()
                self._display_system_overview()
                self._display_server_status_table()
                self._display_progress_summary()
                self._display_health_summary()
                self._display_next_actions()
                self._display_footer()
                
                # Wait for next refresh
                await asyncio.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            logger.info("Dashboard interrupted by user")
        except Exception as e:
            logger.error(f"Error in dashboard loop: {e}")
    
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _display_dashboard_header(self):
        """Display dashboard header"""
        print("=" * 100)
        print("🚀 MCP SERVER DASHBOARD - FORENSIC RECONCILIATION APP")
        print("=" * 100)
        print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔄 Refresh Interval: {self.refresh_interval} seconds")
        print(f"🎯 Dashboard Status: {self.dashboard_status.upper()}")
        print("=" * 100)
    
    def _display_system_overview(self):
        """Display system overview"""
        try:
            status = self.orchestrator.get_orchestrator_status()
            
            print("\n📊 SYSTEM OVERVIEW")
            print("-" * 50)
            print(f"🏗️  Orchestrator Status: {status['orchestrator_status'].upper()}")
            print(f"⏱️  Uptime: {status['uptime']}")
            print(f"🖥️  Total Servers: {status['total_servers']}")
            print(f"🟢 Running: {status['running_servers']}")
            print(f"🔴 Stopped: {status['stopped_servers']}")
            print(f"❌ Failed: {status['failed_servers']}")
            print(f"📈 Overall Progress: {status['overall_progress']:.1f}%")
            
        except Exception as e:
            print(f"❌ Error getting system overview: {e}")
    
    def _display_server_status_table(self):
        """Display server status table"""
        try:
            server_status = self.orchestrator.get_server_status()
            
            print("\n🖥️  SERVER STATUS TABLE")
            print("-" * 100)
            print(f"{'Server ID':<25} {'Status':<12} {'Priority':<10} {'Progress':<10} {'Health':<10} {'Uptime':<15}")
            print("-" * 100)
            
            for server_id, status in server_status.items():
                if isinstance(status, dict):
                    server_id_display = server_id[:24]
                    status_display = status.get('status', 'unknown')[:11]
                    priority_display = status.get('priority', 'unknown')[:9]
                    progress_display = f"{status.get('progress', 0):.1f}%"[:9]
                    health_display = status.get('health_status', 'unknown')[:9]
                    uptime_display = status.get('uptime', '0s')[:14]
                    
                    # Color coding for status
                    status_color = self._get_status_color(status_display)
                    health_color = self._get_health_color(health_display)
                    
                    print(f"{server_id_display:<25} {status_color}{status_display:<12}{'🔴'} {priority_display:<10} "
                          f"{progress_display:<10} {health_color}{health_display:<10}{'🔴'} {uptime_display:<15}")
            
        except Exception as e:
            print(f"❌ Error getting server status: {e}")
    
    def _display_progress_summary(self):
        """Display progress summary"""
        try:
            summary = self.orchestrator.get_mcp_system_summary()
            
            print("\n📈 PROGRESS SUMMARY")
            print("-" * 50)
            
            if 'progress_summary' in summary:
                progress = summary['progress_summary']
                print(f"🎯 Overall Progress: {progress.get('overall_progress', 0):.1f}%")
                print(f"🔴 Critical Priority: {progress.get('critical_progress', 0):.1f}%")
                print(f"🟡 High Priority: {progress.get('high_priority_progress', 0):.1f}%")
                print(f"🟢 Normal Priority: {progress.get('normal_priority_progress', 0):.1f}%")
            
            if 'implementation_status' in summary:
                impl = summary['implementation_status']
                print(f"✅ Completed: {impl.get('completed', 0)}")
                print(f"🔄 In Progress: {impl.get('in_progress', 0)}")
                print(f"📋 Total: {impl.get('total', 0)}")
            
        except Exception as e:
            print(f"❌ Error getting progress summary: {e}")
    
    def _display_health_summary(self):
        """Display health summary"""
        try:
            summary = self.orchestrator.get_mcp_system_summary()
            
            print("\n🏥 HEALTH SUMMARY")
            print("-" * 50)
            
            if 'health_summary' in summary:
                health = summary['health_summary']
                print(f"🟢 Healthy: {health.get('healthy', 0)}")
                print(f"🟡 Optimal: {health.get('optimal', 0)}")
                print(f"🔵 Excellent: {health.get('excellent', 0)}")
                print(f"🔴 Unhealthy: {health.get('unhealthy', 0)}")
            
        except Exception as e:
            print(f"❌ Error getting health summary: {e}")
    
    def _display_next_actions(self):
        """Display next actions"""
        try:
            print("\n🎯 NEXT ACTIONS")
            print("-" * 50)
            
            # Get servers that need attention
            server_status = self.orchestrator.get_server_status()
            critical_servers = []
            high_priority_servers = []
            
            for server_id, status in server_status.items():
                if isinstance(status, dict):
                    if status.get('priority') == 'CRITICAL' and status.get('progress', 0) < 100:
                        critical_servers.append(server_id)
                    elif status.get('priority') == 'HIGH' and status.get('progress', 0) < 100:
                        high_priority_servers.append(server_id)
            
            if critical_servers:
                print("🔴 CRITICAL PRIORITY - Immediate attention required:")
                for server in critical_servers[:3]:  # Show first 3
                    print(f"   • {server}")
            
            if high_priority_servers:
                print("🟡 HIGH PRIORITY - Plan implementation:")
                for server in high_priority_servers[:3]:  # Show first 3
                    print(f"   • {server}")
            
            if not critical_servers and not high_priority_servers:
                print("✅ All priority servers are running smoothly!")
            
        except Exception as e:
            print(f"❌ Error getting next actions: {e}")
    
    def _display_footer(self):
        """Display dashboard footer"""
        print("\n" + "=" * 100)
        print("💡 Commands: Ctrl+C to exit | Auto-refresh every 5 seconds")
        print("🔗 MCP System: All servers coordinated and monitored")
        print("🎯 Goal: Complete all priority TODO items with zero overlapping implementations")
        print("=" * 100)
    
    def _get_status_color(self, status: str) -> str:
        """Get color code for status"""
        status_lower = status.lower()
        if 'running' in status_lower:
            return "🟢"
        elif 'starting' in status_lower:
            return "🟡"
        elif 'stopping' in status_lower:
            return "🟠"
        elif 'stopped' in status_lower:
            return "🔴"
        elif 'failed' in status_lower:
            return "❌"
        else:
            return "⚪"
    
    def _get_health_color(self, health: str) -> str:
        """Get color code for health"""
        health_lower = health.lower()
        if 'excellent' in health_lower:
            return "🔵"
        elif 'optimal' in health_lower:
            return "🟢"
        elif 'healthy' in health_lower:
            return "🟡"
        elif 'unhealthy' in health_lower:
            return "🔴"
        else:
            return "⚪"
    
    async def stop_dashboard(self):
        """Stop the MCP dashboard"""
        try:
            logger.info("Stopping MCP Dashboard...")
            
            self.dashboard_status = "stopping"
            
            # Stop orchestrator
            await self.orchestrator.stop_all_servers()
            
            self.dashboard_status = "stopped"
            logger.info("MCP Dashboard stopped")
            
        except Exception as e:
            logger.error(f"Error stopping dashboard: {e}")


async def main():
    """Main function to run MCP Dashboard"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize dashboard
    dashboard = MCPDashboard()
    
    try:
        # Start dashboard
        await dashboard.start_dashboard()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping MCP Dashboard...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await dashboard.stop_dashboard()
        print("👋 MCP Dashboard shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
