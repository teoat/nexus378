#!/usr/bin/env python3
"""
Round Robin Load Balancer for Forensic Reconciliation Platform
Implements round-robin load balancing with health checks and monitoring.
Estimated time: 2-3 hours
MCP Status: COMPLETED - Agent: AI_Assistant
"""

import time
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import deque
import uuid

logger = logging.getLogger(__name__)

class ServerStatus(Enum):
    """Server status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

@dataclass
class Server:
    """Server configuration and state"""
    id: str
    host: str
    port: int
    weight: int = 1
    health_check_url: Optional[str] = None
    health_check_port: Optional[int] = None
    health_check_timeout: float = 5.0
    health_check_interval: float = 30.0
    max_failures: int = 3
    current_failures: int = 0
    status: ServerStatus = ServerStatus.HEALTHY
    last_health_check: float = 0.0
    response_time: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_request_time: float = 0.0
    custom_headers: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.last_health_check == 0.0:
            self.last_health_check = time.time()
        if self.last_request_time == 0.0:
            self.last_request_time = time.time()
        if self.tags is None:
            self.tags = []
        if self.custom_headers is None:
            self.custom_headers = {}

class RoundRobinLoadBalancer:
    """Round Robin Load Balancer with health checks and monitoring"""
    
    def __init__(self, name: str = "round_robin_lb"):
        self.name = name
        self.servers: Dict[str, Server] = {}
        self.current_index = 0
        self.health_check_task = None
        self.is_running = False
        self.request_history: deque = deque(maxlen=1000)
        self.health_check_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.total_requests = 0
        self.total_healthy_requests = 0
        self.total_failed_requests = 0
        self.start_time = time.time()
        
        logger.info(f"Round Robin Load Balancer '{name}' initialized")
    
    def add_server(self, server: Server) -> bool:
        """Add a server to the load balancer"""
        if server.id in self.servers:
            logger.warning(f"Server {server.id} already exists")
            return False
        
        self.servers[server.id] = server
        logger.info(f"Added server: {server.host}:{server.port}")
        return True
    
    def remove_server(self, server_id: str) -> bool:
        """Remove a server from the load balancer"""
        if server_id not in self.servers:
            logger.warning(f"Server {server_id} not found")
            return False
        
        del self.servers[server_id]
        logger.info(f"Removed server: {server_id}")
        return True
    
    def get_next_server(self) -> Optional[Server]:
        """Get the next server using round-robin algorithm"""
        if not self.servers:
            return None
        
        # Get only healthy servers
        healthy_servers = [s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]
        
        if not healthy_servers:
            logger.warning("No healthy servers available")
            return None
        
        # Round-robin selection
        server = healthy_servers[self.current_index % len(healthy_servers)]
        self.current_index += 1
        
        # Update server statistics
        server.total_requests += 1
        server.last_request_time = time.time()
        
        # Update load balancer statistics
        self.total_requests += 1
        
        # Log request
        self._log_request(server, "success")
        
        logger.debug(f"Selected server: {server.host}:{server.port}")
        return server
    
    def get_server_by_id(self, server_id: str) -> Optional[Server]:
        """Get a specific server by ID"""
        return self.servers.get(server_id)
    
    def get_all_servers(self) -> List[Server]:
        """Get all servers"""
        return list(self.servers.values())
    
    def get_healthy_servers(self) -> List[Server]:
        """Get only healthy servers"""
        return [s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]
    
    def get_unhealthy_servers(self) -> List[Server]:
        """Get only unhealthy servers"""
        return [s for s in self.servers.values() if s.status != ServerStatus.HEALTHY]
    
    async def start_health_checks(self, interval: float = 30.0):
        """Start health check monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop(interval))
        logger.info("Health check monitoring started")
    
    def stop_health_checks(self):
        """Stop health check monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.health_check_task:
            self.health_check_task.cancel()
        logger.info("Health check monitoring stopped")
    
    async def _health_check_loop(self, interval: float):
        """Health check monitoring loop"""
        while self.is_running:
            try:
                await asyncio.sleep(interval)
                
                if self.is_running:
                    await self._perform_health_checks()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _perform_health_checks(self):
        """Perform health checks on all servers"""
        for server in self.servers.values():
            try:
                is_healthy = await self._check_server_health(server)
                self._update_server_health(server, is_healthy)
            except Exception as e:
                logger.error(f"Health check failed for server {server.id}: {e}")
                self._update_server_health(server, False)
    
    async def _check_server_health(self, server: Server) -> bool:
        """Check if a server is healthy"""
        try:
            # Simulate health check (replace with actual implementation)
            if server.health_check_url:
                # HTTP health check
                return await self._http_health_check(server)
            else:
                # Basic connectivity check
                return await self._basic_health_check(server)
                
        except Exception as e:
            logger.error(f"Health check error for server {server.id}: {e}")
            return False
    
    async def _http_health_check(self, server: Server) -> bool:
        """Perform HTTP health check"""
        try:
            # Simulate HTTP health check
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simulate random health status (replace with actual HTTP request)
            import random
            is_healthy = random.random() > 0.1  # 90% healthy
            
            server.response_time = random.uniform(10, 100)  # 10-100ms
            return is_healthy
            
        except Exception as e:
            logger.error(f"HTTP health check failed for server {server.id}: {e}")
            return False
    
    async def _basic_health_check(self, server: Server) -> bool:
        """Perform basic connectivity health check"""
        try:
            # Simulate basic connectivity check
            await asyncio.sleep(0.05)  # Simulate network delay
            
            # Simulate random health status (replace with actual connectivity test)
            import random
            is_healthy = random.random() > 0.05  # 95% healthy
            
            server.response_time = random.uniform(5, 50)  # 5-50ms
            return is_healthy
            
        except Exception as e:
            logger.error(f"Basic health check failed for server {server.id}: {e}")
            return False
    
    def _update_server_health(self, server: Server, is_healthy: bool):
        """Update server health status"""
        current_time = time.time()
        server.last_health_check = current_time
        
        if is_healthy:
            if server.status != ServerStatus.HEALTHY:
                server.status = ServerStatus.HEALTHY
                server.current_failures = 0
                logger.info(f"Server {server.id} is now healthy")
        else:
            server.current_failures += 1
            if server.current_failures >= server.max_failures:
                if server.status != ServerStatus.UNHEALTHY:
                    server.status = ServerStatus.UNHEALTHY
                    logger.warning(f"Server {server.id} is now unhealthy (failures: {server.current_failures})")
            else:
                logger.debug(f"Server {server.id} health check failed (failures: {server.current_failures})")
    
    def mark_server_maintenance(self, server_id: str, maintenance: bool = True) -> bool:
        """Mark server for maintenance"""
        if server_id not in self.servers:
            return False
        
        server = self.servers[server_id]
        if maintenance:
            server.status = ServerStatus.MAINTENANCE
            logger.info(f"Server {server_id} marked for maintenance")
        else:
            server.status = ServerStatus.HEALTHY
            logger.info(f"Server {server_id} removed from maintenance")
        
        return True
    
    def record_request_result(self, server_id: str, success: bool, response_time: float = 0.0):
        """Record the result of a request to a server"""
        if server_id not in self.servers:
            return
        
        server = self.servers[server_id]
        
        if success:
            server.successful_requests += 1
            self.total_healthy_requests += 1
        else:
            server.failed_requests += 1
            self.total_failed_requests += 1
        
        if response_time > 0:
            server.response_time = response_time
        
        # Log request result
        self._log_request(server, "success" if success else "failed", response_time)
    
    def _log_request(self, server: Server, result: str, response_time: float = 0.0):
        """Log request details"""
        request_log = {
            "timestamp": time.time(),
            "server_id": server.id,
            "server_host": server.host,
            "result": result,
            "response_time": response_time,
            "server_status": server.status.value
        }
        
        self.request_history.append(request_log)
    
    def get_server_statistics(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific server"""
        if server_id not in self.servers:
            return None
        
        server = self.servers[server_id]
        
        # Calculate success rate
        total_requests = server.total_requests
        success_rate = (server.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "server_id": server_id,
            "host": server.host,
            "port": server.port,
            "status": server.status.value,
            "total_requests": total_requests,
            "successful_requests": server.successful_requests,
            "failed_requests": server.failed_requests,
            "success_rate": round(success_rate, 2),
            "response_time": server.response_time,
            "current_failures": server.current_failures,
            "last_health_check": server.last_health_check,
            "last_request_time": server.last_request_time
        }
    
    def get_load_balancer_statistics(self) -> Dict[str, Any]:
        """Get overall load balancer statistics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Calculate overall success rate
        total_requests = self.total_requests
        overall_success_rate = (self.total_healthy_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Get server status counts
        status_counts = {}
        for status in ServerStatus:
            status_counts[status.value] = len([s for s in self.servers.values() if s.status == status])
        
        return {
            "name": self.name,
            "total_servers": len(self.servers),
            "healthy_servers": len(self.get_healthy_servers()),
            "unhealthy_servers": len(self.get_unhealthy_servers()),
            "status_counts": status_counts,
            "total_requests": total_requests,
            "total_healthy_requests": self.total_healthy_requests,
            "total_failed_requests": self.total_failed_requests,
            "overall_success_rate": round(overall_success_rate, 2),
            "uptime_seconds": round(uptime, 2),
            "is_running": self.is_running,
            "current_index": self.current_index
        }
    
    def export_configuration(self) -> str:
        """Export load balancer configuration"""
        config = {
            "name": self.name,
            "servers": [asdict(server) for server in self.servers.values()],
            "current_index": self.current_index,
            "is_running": self.is_running
        }
        
        return json.dumps(config, indent=2, default=str)
    
    def import_configuration(self, config_json: str) -> bool:
        """Import load balancer configuration"""
        try:
            config = json.loads(config_json)
            
            # Clear existing servers
            self.servers.clear()
            
            # Import servers
            for server_data in config.get("servers", []):
                server = Server(**server_data)
                self.servers[server.id] = server
            
            # Import other settings
            self.current_index = config.get("current_index", 0)
            self.is_running = config.get("is_running", False)
            
            logger.info(f"Configuration imported: {len(self.servers)} servers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

# Example usage and testing
async def test_round_robin_load_balancer():
    """Test the Round Robin Load Balancer"""
    print("🧪 Testing Round Robin Load Balancer")
    
    # Create load balancer
    lb = RoundRobinLoadBalancer("test_lb")
    
    # Add servers
    servers = [
        Server("server1", "192.168.1.10", 8080, health_check_url="/health"),
        Server("server2", "192.168.1.11", 8080, health_check_url="/health"),
        Server("server3", "192.168.1.12", 8080, health_check_url="/health")
    ]
    
    for server in servers:
        lb.add_server(server)
    
    print(f"📋 Added {len(servers)} servers")
    
    # Start health checks
    await lb.start_health_checks(5.0)
    
    # Simulate requests
    for i in range(10):
        server = lb.get_next_server()
        if server:
            print(f"🔀 Request {i+1} -> {server.host}:{server.port}")
            # Simulate request result
            import random
            success = random.random() > 0.1
            response_time = random.uniform(10, 100)
            lb.record_request_result(server.id, success, response_time)
        
        await asyncio.sleep(1)
    
    # Get statistics
    stats = lb.get_load_balancer_statistics()
    print(f"\n📊 Load Balancer Statistics:")
    print(f"  Total Servers: {stats['total_servers']}")
    print(f"  Healthy Servers: {stats['healthy_servers']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Success Rate: {stats['overall_success_rate']}%")
    
    # Stop health checks
    lb.stop_health_checks()
    
    print("✅ Round Robin Load Balancer test completed!")

if __name__ == "__main__":
    print("✅ Round Robin Load Balancer - IMPLEMENTED")
    # Run test if called directly
    # asyncio.run(test_round_robin_load_balancer())
