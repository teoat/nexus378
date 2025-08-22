#!/usr/bin/env python3
"""
MCP Server Orchestrator for Forensic Reconciliation App
Manages all MCP servers and their coordination, including auto-scaling.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import signal
import sys

from .mcp_server import mcp_server
from .autoscaler import AutoScaler, ScalingDecision
from ...plugins.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    server_id: str
    server_name: str
    server_type: str
    priority: str
    status: str
    progress: float
    mcp_status: str
    last_updated: str
    health_status: str
    uptime: str


class MCPServerOrchestrator:
    """Orchestrates all MCP servers for the forensic reconciliation app"""
    
    def __init__(self):
        self.servers: Dict[str, Any] = {}
        self.server_status: Dict[str, MCPServerInfo] = {}
        self.orchestrator_status = "initializing"
        self.start_time = datetime.now()
        
        # Initialize server registry
        self._initialize_server_registry()
        
        # Initialize AutoScaler
        autoscaler_config = {
            "MIN_AGENTS": 2,
            "MAX_AGENTS": 10,
            "TASKS_PER_AGENT_THRESHOLD": 5,
            "IDLE_AGENT_PERCENT_THRESHOLD": 0.5,
            "COOLDOWN_PERIOD_S": 30,
        }
        self.autoscaler = AutoScaler(mcp_server, autoscaler_config)

        logger.info("MCP Server Orchestrator initialized")
    
    def _initialize_server_registry(self):
        """Initialize the registry of all MCP servers"""
        self.server_registry = {
            "mfa_server": {
                "name": "Multi-Factor Authentication MCP Server",
                "type": "security",
                "priority": "CRITICAL",
                "task_id": "todo_002",
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["security", "authentication", "mfa_implementation"],
                "subtasks": [
                    "TOTP Service Implementation (3-4 hours)",
                    "SMS Service Integration (2-3 hours)",
                    "Hardware Token Support (2-3 hours)",
                    "MFA Configuration Management (1-2 hours)"
                ]
            },
            "encryption_server": {
                "name": "End-to-End Encryption MCP Server",
                "type": "security",
                "priority": "CRITICAL",
                "task_id": "todo_003",
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["security", "encryption", "key_management"],
                "subtasks": [
                    "AES-256 Encryption Core (3-4 hours)",
                    "Key Management System (2-3 hours)",
                    "Encryption Pipeline Integration (1-2 hours)"
                ]
            },
            "load_balancing_server": {
                "name": "Load Balancing Strategies MCP Server",
                "type": "performance",
                "priority": "HIGH",
                "task_id": "todo_004",
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["python_development", "load_balancing", "algorithm_implementation"],
                "subtasks": []
            },
            "queue_monitoring_server": {
                "name": "Queue Monitoring and Metrics MCP Server",
                "type": "monitoring",
                "priority": "HIGH",
                "task_id": "todo_005",
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["python_development", "monitoring", "metrics"],
                "subtasks": []
            },
            "reconciliation_agent_server": {
                "name": "Reconciliation Agent AI Fuzzy Matching MCP Server",
                "type": "ai_agent",
                "priority": "HIGH",
                "task_id": "todo_006",
                "estimated_duration": "10-15 hours",
                "required_capabilities": ["ai_development", "fuzzy_matching", "algorithm_implementation"],
                "subtasks": []
            },
            "fraud_agent_server": {
                "name": "Fraud Agent Pattern Detection MCP Server",
                "type": "ai_agent",
                "priority": "HIGH",
                "task_id": "todo_007",
                "estimated_duration": "12-18 hours",
                "required_capabilities": ["ai_development", "pattern_detection", "fraud_analysis"],
                "subtasks": []
            },
            "entity_network_server": {
                "name": "Fraud Agent Entity Network Analysis MCP Server",
                "type": "ai_agent",
                "priority": "HIGH",
                "task_id": "todo_008",
                "estimated_duration": "15-20 hours",
                "required_capabilities": ["ai_development", "network_analysis", "graph_algorithms"],
                "subtasks": []
            },
            "risk_agent_server": {
                "name": "Risk Agent Compliance Engine MCP Server",
                "type": "ai_agent",
                "priority": "HIGH",
                "task_id": "todo_009",
                "estimated_duration": "10-15 hours",
                "required_capabilities": ["ai_development", "compliance", "risk_assessment"],
                "subtasks": []
            },
            "evidence_agent_server": {
                "name": "Evidence Agent Processing Pipeline MCP Server",
                "type": "ai_agent",
                "priority": "NORMAL",
                "task_id": "todo_010",
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["ai_development", "data_processing", "pipeline_management"],
                "subtasks": []
            }
        }
    
    async def start_all_servers(self) -> bool:
        """Start all MCP servers"""
        try:
            logger.info("Starting all MCP servers...")
            
            # Start servers in priority order
            critical_servers = []
            high_priority_servers = []
            normal_priority_servers = []
            
            for server_id, server_info in self.server_registry.items():
                if server_info["priority"] == "CRITICAL":
                    critical_servers.append(server_id)
                elif server_info["priority"] == "HIGH":
                    high_priority_servers.append(server_id)
                else:
                    normal_priority_servers.append(server_id)
            
            # Start critical servers first
            logger.info("Starting CRITICAL priority servers...")
            for server_id in critical_servers:
                await self._start_server(server_id)
                await asyncio.sleep(1)  # Small delay between starts
            
            # Start high priority servers
            logger.info("Starting HIGH priority servers...")
            for server_id in high_priority_servers:
                await self._start_server(server_id)
                await asyncio.sleep(1)
            
            # Start normal priority servers
            logger.info("Starting NORMAL priority servers...")
            for server_id in normal_priority_servers:
                await self._start_server(server_id)
                await asyncio.sleep(1)
            
            self.orchestrator_status = "running"
            logger.info("All MCP servers started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start all MCP servers: {e}")
            self.orchestrator_status = "failed"
            return False
    
    async def _start_server(self, server_id: str, server_info_override: Optional[Dict] = None) -> bool:
        """Start a specific MCP server"""
        try:
            logger.info(f"Starting {server_id}...")
            
            # For now, we'll simulate server startup
            # In a real implementation, this would actually start the server processes
            
            server_info = server_info_override or self.server_registry[server_id]
            
            # Create server status
            server_status = MCPServerInfo(
                server_id=server_id,
                server_name=server_info["name"],
                server_type=server_info["type"],
                priority=server_info["priority"],
                status="starting",
                progress=0.0,
                mcp_status="MCP_TRACKED",
                last_updated=datetime.now().isoformat(),
                health_status="healthy",
                uptime="0s"
            )
            
            self.server_status[server_id] = server_status
            
            # Simulate server startup
            await asyncio.sleep(0.5)
            
            # Update status to running
            server_status.status = "running"
            server_status.last_updated = datetime.now().isoformat()
            
            logger.info(f"{server_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {server_id}: {e}")
            if server_id in self.server_status:
                self.server_status[server_id].status = "failed"
                self.server_status[server_id].health_status = "unhealthy"
            return False
    
    async def stop_all_servers(self):
        """Stop all MCP servers"""
        try:
            logger.info("Stopping all MCP servers...")
            
            # Use list(self.server_status.keys()) to avoid issues with changing dict size during iteration
            for server_id in list(self.server_status.keys()):
                await self._stop_server(server_id)
                await asyncio.sleep(0.5)
            
            self.orchestrator_status = "stopped"
            logger.info("All MCP servers stopped")
            
        except Exception as e:
            logger.error(f"Error stopping servers: {e}")
    
    async def _stop_server(self, server_id: str):
        """Stop a specific MCP server"""
        try:
            logger.info(f"Stopping {server_id}...")
            
            if server_id in self.server_status:
                self.server_status[server_id].status = "stopping"
                await asyncio.sleep(0.2)
                self.server_status[server_id].status = "stopped"
            
            logger.info(f"{server_id} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping {server_id}: {e}")

    async def monitor_servers(self):
        """Monitor all MCP servers and perform auto-scaling."""
        try:
            logger.info("Starting server monitoring...")
            
            while self.orchestrator_status == "running":
                # Update server health and status
                await self._update_server_health()

                # Perform auto-scaling
                await self._perform_autoscaling()
                
                # Log system status
                await self._log_system_status()
                
                # Wait before next check
                await asyncio.sleep(15)  # Check more frequently for scaling
                
        except Exception as e:
            logger.error(f"Error in server monitoring: {e}")

    async def _perform_autoscaling(self):
        """Check metrics and perform scaling actions if needed."""
        decision = self.autoscaler.make_scaling_decision()
        if decision == ScalingDecision.SCALE_UP:
            await self._scale_up()
        elif decision == ScalingDecision.SCALE_DOWN:
            await self._scale_down()

    async def _scale_up(self):
        """
        Simulates scaling up by adding a new agent server to the pool.
        NOTE: In a real-world scenario, this method would interface with a
        container orchestrator (like Docker, Kubernetes) to start a new agent container.
        """
        if len(mcp_server.agents) >= self.autoscaler.max_agents:
            logger.debug("Max agents reached, cannot scale up.")
            return

        new_agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        logger.info(f"Scaling up: adding new agent {new_agent_id}")

        # Register the new agent with the MCP server
        await mcp_server.register_agent(
            agent_id=new_agent_id,
            name=f"AutoScaledAgent-{new_agent_id}",
            capabilities=["general_purpose"]
        )

        # Create a server entry for it in the orchestrator to simulate it running
        server_info = {
            "name": f"Auto-Scaled Agent Server {new_agent_id}",
            "type": "ai_agent",
            "priority": "NORMAL",
        }
        await self._start_server(new_agent_id, server_info_override=server_info)
        logger.info(f"Agent {new_agent_id} added to orchestrator pool.")

    async def _scale_down(self):
        """
        Simulates scaling down by removing an idle agent server from the pool.
        NOTE: In a real-world scenario, this method would interface with a
        container orchestrator to stop an agent container.
        """
        if len(mcp_server.agents) <= self.autoscaler.min_agents:
            logger.debug("Min agents reached, cannot scale down.")
            return

        idle_agent_id = await self._find_idle_agent_server()
        if idle_agent_id:
            logger.info(f"Scaling down: removing idle agent {idle_agent_id}")
            # Simulate stopping the server and remove it from tracking
            await self._stop_server(idle_agent_id)
            if idle_agent_id in self.server_status:
                del self.server_status[idle_agent_id]
            if idle_agent_id in mcp_server.agents:
                del mcp_server.agents[idle_agent_id]
            logger.info(f"Agent {idle_agent_id} removed from pool.")
        else:
            logger.debug("No idle agents found to scale down.")

    async def _find_idle_agent_server(self) -> Optional[str]:
        """Finds an agent server that is currently idle."""
        for agent_id, agent in mcp_server.agents.items():
            if not agent.current_tasks:
                # Only scale down agents that are not part of the original, fixed registry
                if agent_id not in self.server_registry:
                     return agent_id
        return None
    
    async def _update_server_health(self):
        """Update health status of all servers"""
        try:
            current_time = datetime.now()
            
            # Use list() to create a copy, allowing dict to be modified during iteration
            for server_id, server_status in list(self.server_status.items()):
                if server_status.status == "running":
                    # Update uptime
                    start_time = datetime.fromisoformat(server_status.last_updated)
                    uptime = current_time - start_time
                    server_status.uptime = str(uptime).split('.')[0]  # Remove microseconds
                    
                    # Simulate progress updates
                    if server_status.progress < 100.0:
                        server_status.progress += 0.1
                        if server_status.progress > 100.0:
                            server_status.progress = 100.0
                            server_status.mcp_status = "MCP_COMPLETED"
                    
                    # Update last updated timestamp
                    server_status.last_updated = current_time.isoformat()
                    
                    # Randomly update health status (simulate real monitoring)
                    if server_status.health_status == "healthy" and server_status.progress > 50.0:
                        server_status.health_status = "optimal"
                    elif server_status.health_status == "optimal" and server_status.progress > 75.0:
                        server_status.health_status = "excellent"
                
        except Exception as e:
            logger.error(f"Error updating server health: {e}")
    
    async def _log_system_status(self):
        """Log current system status"""
        try:
            running_servers = len([s for s in self.server_status.values() if s.status == "running"])
            total_servers = len(self.server_status)
            overall_progress = sum(s.progress for s in self.server_status.values()) / total_servers if total_servers > 0 else 0
            
            logger.info(f"System Status: {running_servers}/{total_servers} servers running, "
                       f"Overall Progress: {overall_progress:.1f}%")
            
        except Exception as e:
            logger.error(f"Error logging system status: {e}")
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "orchestrator_status": self.orchestrator_status,
            "start_time": self.start_time.isoformat(),
            "uptime": str(datetime.now() - self.start_time).split('.')[0],
            "total_servers": len(self.server_status),
            "running_servers": len([s for s in self.server_status.values() if s.status == "running"]),
            "stopped_servers": len([s for s in self.server_status.values() if s.status == "stopped"]),
            "failed_servers": len([s for s in self.server_status.values() if s.status == "failed"]),
            "overall_progress": sum(s.progress for s in self.server_status.values()) / len(self.server_status) if self.server_status else 0
        }
    
    def get_server_status(self, server_id: str = None) -> Dict[str, Any]:
        """Get status of specific server or all servers"""
        if server_id:
            if server_id in self.server_status:
                return asdict(self.server_status[server_id])
            else:
                return {"error": f"Server {server_id} not found"}
        else:
            return {server_id: asdict(status) for server_id, status in self.server_status.items()}
    
    def get_mcp_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive MCP system summary"""
        try:
            critical_servers = [s for s in self.server_status.values() if s.priority == "CRITICAL"]
            high_priority_servers = [s for s in self.server_status.values() if s.priority == "HIGH"]
            normal_priority_servers = [s for s in self.server_status.values() if s.priority == "NORMAL"]
            
            completed_servers = [s for s in self.server_status.values() if s.mcp_status == "MCP_COMPLETED"]
            in_progress_servers = [s for s in self.server_status.values() if s.mcp_status == "MCP_TRACKED"]
            
            return {
                "orchestrator_status": self.get_orchestrator_status(),
                "server_distribution": {
                    "critical": len(critical_servers),
                    "high_priority": len(high_priority_servers),
                    "normal_priority": len(normal_priority_servers)
                },
                "implementation_status": {
                    "completed": len(completed_servers),
                    "in_progress": len(in_progress_servers),
                    "total": len(self.server_status)
                },
                "progress_summary": {
                    "overall_progress": sum(s.progress for s in self.server_status.values()) / len(self.server_status) if self.server_status else 0,
                    "critical_progress": sum(s.progress for s in critical_servers) / len(critical_servers) if critical_servers else 0,
                    "high_priority_progress": sum(s.progress for s in high_priority_servers) / len(high_priority_servers) if high_priority_servers else 0,
                    "normal_priority_progress": sum(s.progress for s in normal_priority_servers) / len(normal_priority_servers) if normal_priority_servers else 0
                },
                "health_summary": {
                    "healthy": len([s for s in self.server_status.values() if s.health_status == "healthy"]),
                    "optimal": len([s for s in self.server_status.values() if s.health_status == "optimal"]),
                    "excellent": len([s for s in self.server_status.values() if s.health_status == "excellent"]),
                    "unhealthy": len([s for s in self.server_status.values() if s.health_status == "unhealthy"])
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting MCP system summary: {e}")
            return {"error": str(e)}


async def main():
    """Main function to run MCP Server Orchestrator"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize orchestrator
    orchestrator = MCPServerOrchestrator()

    # Initialize and load plugins
    plugin_manager = PluginManager(plugin_folder="../../plugins")
    plugin_manager.discover_and_load_plugins()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        plugin_manager.shutdown()
        asyncio.create_task(orchestrator.stop_all_servers())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all servers
        success = await orchestrator.start_all_servers()
        
        if success:
            print("✅ All MCP servers started successfully!")
            
            # Start monitoring
            monitor_task = asyncio.create_task(orchestrator.monitor_servers())
            
            # Keep orchestrator running
            while orchestrator.orchestrator_status == "running":
                # Display status every 10 seconds
                status = orchestrator.get_orchestrator_status()
                print(f"\n📊 MCP System Status: {status['orchestrator_status']}")
                print(f"🔄 Running Servers: {status['running_servers']}/{status['total_servers']}")
                print(f"📈 Overall Progress: {status['overall_progress']:.1f}%")
                print(f"⏱️  Uptime: {status['uptime']}")
                
                await asyncio.sleep(10)
                
        else:
            print("❌ Failed to start MCP servers!")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down MCP Server Orchestrator...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await orchestrator.stop_all_servers()
        plugin_manager.shutdown()
        print("👋 MCP Server Orchestrator shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
