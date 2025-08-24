"""
Frenly API - FastAPI endpoints for interacting with Frenly Meta Agent

This module provides REST API endpoints for managing the forensic reconciliation app
through Frenly's intelligent orchestration system.
"""

from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
import logging # Added for WebSocket logging

logger = logging.getLogger(__name__)
from agents.frenly_meta_agent import AppContext, AppCommand, AppResponse, FrenlyMetaAgent
from agents.frenly_mcp_bridge import FrenlyMCPBridge
import json
import asyncio

# Create router
frenly_router = APIRouter(prefix="/api/frenly", tags=["frenly"])

# Global instances (will be initialized in main.py)
frenly_agent: Optional[FrenlyMetaAgent] = None
frenly_bridge: Optional[FrenlyMCPBridge] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.heartbeat_task = None
        self.heartbeat_running = False
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Send message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_frenly_state(self):
        """Send current Frenly state to all connected clients."""
        if not frenly_agent:
            return
        
        try:
            # Get current state
            context = frenly_agent.app_context
            system_health = frenly_agent.get_overall_system_health()
            agent_status = frenly_agent.get_all_agent_status()
            recent_events = frenly_agent.get_recent_events(limit=10)
            
            state_data = {
                "type": "frenly_state",
                "timestamp": context.timestamp.isoformat(),
                "context": {
                    "app_mode": context.app_mode.value,
                    "thinking_perspective": context.thinking_perspective.value if context.thinking_perspective else None,
                    "ai_mode": context.ai_mode.value,
                    "dashboard_view": context.dashboard_view.value,
                    "user_role": context.user_role.value
                },
                "system_health": system_health,
                "agent_status": agent_status,
                "recent_events": recent_events
            }
            
            await self.broadcast(json.dumps(state_data))
            
        except Exception as e:
            print(f"Error sending Frenly state: {e}")
    
    def start_heartbeat(self):
        """Start heartbeat to keep connections alive."""
        if self.heartbeat_running:
            return
        
        self.heartbeat_running = True
        
        async def heartbeat_loop():
            while self.heartbeat_running:
                try:
                    if self.active_connections:
                        # Send heartbeat to all connections
                        heartbeat_msg = {
                            "type": "heartbeat",
                            "timestamp": asyncio.get_event_loop().time(),
                            "connections": len(self.active_connections)
                        }
                        await self.broadcast(json.dumps(heartbeat_msg))
                        
                        # Send Frenly state updates
                        await self.send_frenly_state()
                    
                    await asyncio.sleep(30)  # Send updates every 30 seconds
                    
                except Exception as e:
                    print(f"Heartbeat error: {e}")
                    await asyncio.sleep(30)
        
        # Start heartbeat task
        loop = asyncio.get_event_loop()
        self.heartbeat_task = loop.create_task(heartbeat_loop())
    
    def stop_heartbeat(self):
        """Stop heartbeat."""
        self.heartbeat_running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

# Create connection manager instance
connection_manager = ConnectionManager()


# Pydantic models for API requests/responses
class FrenlyQueryRequest(BaseModel):
    """Request model for Frenly queries."""
    query: str
    context: Optional[Dict[str, Any]] = None


class FrenlyQueryResponse(BaseModel):
    """Response model for Frenly queries."""
    success: bool
    message: str
    response: Optional[AppResponse] = None
    context: Optional[Dict[str, Any]] = None


class FrenlyStatusResponse(BaseModel):
    """Response model for Frenly status."""
    success: bool
    message: str
    app_context: Optional[Dict[str, Any]] = None
    system_health: Optional[Dict[str, Any]] = None
    agent_status: Optional[Dict[str, Any]] = None


class FrenlyContextRequest(BaseModel):
    """Request model for context updates."""
    app_mode: Optional[str] = None
    thinking_perspective: Optional[str] = None
    ai_mode: Optional[str] = None
    dashboard_view: Optional[str] = None
    user_role: Optional[str] = None


class FrenlyContextResponse(BaseModel):
    """Response model for context updates."""
    success: bool
    message: str
    old_context: Optional[Dict[str, Any]] = None
    new_context: Optional[Dict[str, Any]] = None


class FrenlyWorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    workflow_name: str
    parameters: Optional[Dict[str, Any]] = None


class FrenlyWorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    success: bool
    message: str
    workflow_result: Optional[Dict[str, Any]] = None


class FrenlyModeSwitchRequest(BaseModel):
    """Request model for mode switching."""
    app_mode: Optional[str] = None
    thinking_perspective: Optional[str] = None
    ai_mode: Optional[str] = None


class FrenlyModeSwitchResponse(BaseModel):
    """Response model for mode switching."""
    success: bool
    message: str
    old_config: Optional[Dict[str, Any]] = None
    new_config: Optional[Dict[str, Any]] = None


# Dependency to get Frenly instances
# Flag to ensure callback is registered only once
_callback_registered = False

def get_frenly_instances():
    """Get the Frenly agent and bridge instances."""
    global _callback_registered
    if frenly_agent is None or frenly_bridge is None:
        raise HTTPException(status_code=503, detail="Frenly system not initialized")
    
    # Register WebSocket notification callback only once
    if not _callback_registered:
        frenly_agent.register_state_change_callback(notify_websocket_clients)
        _callback_registered = True
        logger.info("WebSocket notification callback registered with FrenlyMetaAgent.")

    return frenly_agent, frenly_bridge

async def notify_websocket_clients(state_data: Dict[str, Any]):
    """Sends state updates to all connected WebSocket clients."""
    # Create a copy of the list to avoid issues with concurrent modification
    # if a client disconnects during iteration.
    disconnected_clients = []
    for connection in active_websocket_connections:
        try:
            await connection.send_json({"type": "state_update", "data": state_data})
        except WebSocketDisconnect:
            disconnected_clients.append(connection)
            logger.info("WebSocket client disconnected during state update.")
        except Exception as e:
            logger.error(f"Error sending state update to WebSocket client: {e}")
            disconnected_clients.append(connection)
    
    # Remove disconnected clients
    for client in disconnected_clients:
        if client in active_websocket_connections:
            active_websocket_connections.remove(client)


# API Endpoints

@frenly_router.get("/query")
async def frenly_query(request: FrenlyQueryRequest):
    """Send a query to Frenly."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        
        # Process the query through Frenly
        response = frenly_bridge.execute_command(request.query)
        
        return FrenlyQueryResponse(
            success=True,
            message="Query processed successfully",
            response=response,
            context=frenly_agent.app_context.__dict__
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/status")
async def get_frenly_status():
    """Get Frenly's current status and context."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        
        # Get current context
        context = frenly_agent.app_context
        
        # Get system health
        system_health = frenly_agent.get_overall_system_health()
        
        # Get agent status
        agent_status = frenly_agent.get_all_agent_status()
        
        return FrenlyStatusResponse(
            success=True,
            message="Status retrieved successfully",
            app_context={
                "app_mode": context.app_mode.value,
                "thinking_perspective": context.thinking_perspective.value if context.thinking_perspective else None,
                "ai_mode": context.ai_mode.value,
                "dashboard_view": context.dashboard_view.value,
                "user_role": context.user_role.value,
                "session_id": context.session_id,
                "timestamp": context.timestamp.isoformat()
            },
            system_health=system_health,
            agent_status=agent_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/context")
async def get_frenly_context():
    """Get Frenly's current app context."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        context = frenly_agent.app_context
        
        return FrenlyContextResponse(
            success=True,
            message="Context retrieved successfully",
            new_context={
                "app_mode": context.app_mode.value,
                "thinking_perspective": context.thinking_perspective.value if context.thinking_perspective else None,
                "ai_mode": context.ai_mode.value,
                "dashboard_view": context.dashboard_view.value,
                "user_role": context.user_role.value,
                "session_id": context.session_id,
                "timestamp": context.timestamp.isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/switch-mode")
async def switch_frenly_mode(request: FrenlyModeSwitchRequest):
    """Switch Frenly's operating mode."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        
        old_config = {
            "app_mode": frenly_agent.app_context.app_mode.value,
            "thinking_perspective": frenly_agent.app_context.thinking_perspective.value if frenly_agent.app_context.thinking_perspective else None,
            "ai_mode": frenly_agent.app_context.ai_mode.value
        }
        
        # Process mode changes
        if request.app_mode:
            response = frenly_agent.manage_app(AppCommand(
                command_type="switch_app_mode",
                target_mode=request.app_mode
            ))
            if not response.success:
                raise HTTPException(status_code=400, detail=response.message)
        
        if request.thinking_perspective:
            response = frenly_agent.manage_app(AppCommand(
                command_type="change_thinking_perspective",
                target_perspective=request.thinking_perspective
            ))
            if not response.success:
                raise HTTPException(status_code=400, detail=response.message)
        
        if request.ai_mode:
            response = frenly_agent.manage_app(AppCommand(
                command_type="change_ai_mode",
                target_ai_mode=request.ai_mode
            ))
            if not response.success:
                raise HTTPException(status_code=400, detail=response.message)
        
        # Get new config
        new_config = {
            "app_mode": frenly_agent.app_context.app_mode.value,
            "thinking_perspective": frenly_agent.app_context.thinking_perspective.value if frenly_agent.app_context.thinking_perspective else None,
            "ai_mode": frenly_agent.app_context.ai_mode.value
        }
        
        return FrenlyModeSwitchResponse(
            success=True,
            message="Mode switched successfully",
            old_config=old_config,
            new_config=new_config
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/mode-intersection")
async def get_current_mode_intersection():
    """Get the current mode intersection details."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        response = frenly_agent.manage_app(AppCommand(command_type="get_mode_intersection"))
        
        if response.success:
            return {"success": True, "mode_intersection": response.message}
        else:
            return {"success": False, "message": response.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/workflow")
async def execute_workflow(request: FrenlyWorkflowRequest):
    """Execute a workflow through Frenly."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        
        # Execute workflow through MCP bridge
        result = frenly_bridge.execute_workflow(request.workflow_name, request.parameters or {})
        
        return FrenlyWorkflowResponse(
            success=True,
            message="Workflow executed successfully",
            workflow_result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/agents")
async def list_agents():
    """List all registered agents."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        agents = frenly_agent.list_ai_agents()
        return {"success": True, "agents": agents, "count": len(agents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/workflows")
async def list_workflows():
    """List available workflows."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        workflows = frenly_agent.get_workflow_status() # Get status of running workflows
        return {"success": True, "workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/agents/health")
async def get_agent_health():
    """Get health status of all agents."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        agent_health = frenly_agent.get_all_agent_status()
        return {"success": True, "agent_health": agent_health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/agents/{agent_name}/health")
async def get_specific_agent_health(agent_name: str):
    """Get health status of a specific agent."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        agent_health = frenly_agent.get_agent_status(agent_name)
        return {"success": True, "agent_health": agent_health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/agents/{agent_name}/restart")
async def restart_agent(agent_name: str, force: bool = False):
    """Restart a specific agent."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        success = frenly_agent.restart_agent(agent_name, force=force)
        
        if success:
            return {"success": True, "message": f"Agent {agent_name} restarted successfully"}
        else:
            return {"success": False, "message": f"Failed to restart agent {agent_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/agents/restart-all-failed")
async def restart_all_failed_agents():
    """Restart all failed agents."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        results = frenly_agent.restart_all_failed_agents()
        
        success_count = sum(results.values())
        total_count = len(results)
        
        return {
            "success": True, 
            "message": f"Restart complete: {success_count}/{total_count} agents restarted successfully",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/agents/heartbeat/start")
async def start_heartbeat_monitoring(interval_seconds: int = 30):
    """Start heartbeat monitoring of all agents."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        frenly_agent.start_heartbeat_monitoring(interval_seconds)
        return {"success": True, "message": f"Heartbeat monitoring started with {interval_seconds}s interval"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/agents/heartbeat/stop")
async def stop_heartbeat_monitoring():
    """Stop heartbeat monitoring of all agents."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        frenly_agent.stop_heartbeat_monitoring()
        return {"success": True, "message": "Heartbeat monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/health/detailed")
async def get_detailed_health():
    """Get detailed system health including agent health."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        system_health = frenly_agent.get_overall_system_health()
        return {"success": True, "system_health": system_health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/state/save")
async def save_state():
    """Save current Frenly state to files."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        frenly_agent.save_context_to_file()
        frenly_agent.save_modes_to_file()
        return {"success": True, "message": "State saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.post("/state/load")
async def load_state():
    """Load Frenly state from files."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        frenly_agent.load_context_from_file()
        frenly_agent.load_modes_from_file()
        return {"success": True, "message": "State loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/state/context")
async def get_saved_context():
    """Get the currently saved app context."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        context = frenly_agent.app_context
        
        # Convert to serializable format
        context_data = {
            "app_mode": context.app_mode.value,
            "thinking_perspective": context.thinking_perspective.value if context.thinking_perspective else None,
            "ai_mode": context.ai_mode.value,
            "dashboard_view": context.dashboard_view.value,
            "user_role": context.user_role.value,
            "session_id": context.session_id,
            "timestamp": context.timestamp.isoformat()
        }
        
        return {"success": True, "context": context_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/state/modes")
async def get_saved_modes():
    """Get the currently saved mode intersections."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        modes = frenly_agent.mode_intersections
        
        # Convert to serializable format
        serializable_modes = {}
        for key, mode_intersection in modes.items():
            serializable_modes[key] = {
                "app_mode": mode_intersection.app_mode.value,
                "thinking_perspective": mode_intersection.thinking_perspective.value if mode_intersection.thinking_perspective else None,
                "ai_mode": mode_intersection.ai_mode.value,
                "description": mode_intersection.description,
                "features": mode_intersection.features,
                "limitations": mode_intersection.limitations,
                "recommended_views": [view.value for view in mode_intersection.recommended_views],
                "agent_priorities": mode_intersection.agent_priorities,
                "calculation_methods": mode_intersection.calculation_methods,
                "assessment_approaches": mode_intersection.assessment_approaches
            }
        
        return {"success": True, "modes": serializable_modes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/events")
async def get_recent_events(limit: int = 50, event_type: str = None, severity: str = None):
    """Get recent events with optional filtering."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        events = frenly_agent.get_recent_events(limit=limit, event_type=event_type, severity=severity)
        return {"success": True, "events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/events/summary")
async def get_event_summary():
    """Get a summary of events by type and severity."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        summary = frenly_agent.get_event_summary()
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/events/types")
async def get_event_types():
    """Get all available event types."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        events = frenly_agent.get_recent_events(limit=1000)  # Get all events to find types
        
        # Extract unique event types
        event_types = list(set(event["event_type"] for event in events))
        event_types.sort()
        
        return {"success": True, "event_types": event_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/events/severities")
async def get_event_severities():
    """Get all available event severity levels."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        events = frenly_agent.get_recent_events(limit=1000)  # Get all events to find severities
        
        # Extract unique severity levels
        severities = list(set(event["severity"] for event in events))
        severities.sort()
        
        return {"success": True, "severities": severities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/errors")
async def get_error_log(limit: int = 50):
    """Get recent error events from the error log."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        errors = frenly_agent.get_error_log(limit=limit)
        return {"success": True, "errors": errors, "count": len(errors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/metrics")
async def get_metrics():
    """Get current performance metrics."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        metrics = frenly_agent.get_metrics()
        return {"success": True, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Workflow API Endpoints (Phase 5, Items 21-25)
# ============================================================================

@frenly_router.get("/workflows")
async def list_workflows():
    """List all available workflows."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            workflows = frenly_agent.list_workflows()
            return {"success": True, "workflows": workflows}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.post("/workflows/{workflow_name}/execute")
async def execute_workflow(workflow_name: str):
    """Execute a workflow by name."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            result = frenly_agent.execute_workflow(workflow_name)
            return result
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/workflows/status")
async def get_workflow_status(workflow_id: Optional[str] = None):
    """Get workflow status - all workflows or specific workflow."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            status = frenly_agent.get_workflow_status(workflow_id)
            return {"success": True, "status": status}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/workflows/{workflow_id}")
async def get_specific_workflow(workflow_id: str):
    """Get status of a specific workflow."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            status = frenly_agent.get_workflow_status(workflow_id)
            if "error" in status:
                raise HTTPException(status_code=404, detail=status["error"])
            return {"success": True, "workflow": status}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Performance Metrics API Endpoints (Phase 7, Items 26-30)
# ============================================================================

@frenly_router.get("/metrics")
async def get_performance_metrics():
    """Get performance metrics for Frenly system."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            metrics = frenly_agent.get_performance_metrics()
            return {"success": True, "metrics": metrics}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/metrics/overview")
async def get_metrics_overview():
    """Get high-level metrics overview."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            metrics = frenly_agent.get_performance_metrics()
            return {"success": True, "overview": metrics["overview"]}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/metrics/response-times")
async def get_response_time_metrics():
    """Get response time statistics."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            metrics = frenly_agent.get_performance_metrics()
            return {"success": True, "response_times": metrics["response_times"]}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@frenly_router.get("/metrics/recent-activity")
async def get_recent_activity():
    """Get recent command activity."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        if frenly_agent:
            metrics = frenly_agent.get_performance_metrics()
            return {"success": True, "recent_activity": metrics["recent_activity"]}
        else:
            raise HTTPException(status_code=500, detail="Frenly agent not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WebSocket endpoint
# ============================================================================

@frenly_router.websocket("/ws/frenly")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Frenly updates."""
    await connection_manager.connect(websocket)
    
    try:
        # Send initial state
        await connection_manager.send_frenly_state()
        
        # Start heartbeat if not already running
        if not connection_manager.heartbeat_running:
            connection_manager.start_heartbeat()
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    # Respond to ping with pong
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": asyncio.get_event_loop().time()}),
                        websocket
                    )
                
                elif message.get("type") == "request_state":
                    # Send current state immediately
                    await connection_manager.send_frenly_state()
                
                elif message.get("type") == "mode_change":
                    # Handle mode change requests from frontend
                    if frenly_agent:
                        try:
                            if "app_mode" in message:
                                response = frenly_agent.manage_app(AppCommand(
                                    command_type="switch_app_mode",
                                    target_mode=message["app_mode"]
                                ))
                            
                            elif "ai_mode" in message:
                                response = frenly_agent.manage_app(AppCommand(
                                    command_type="change_ai_mode",
                                    target_ai_mode=message["ai_mode"]
                                ))
                            
                            elif "thinking_perspective" in message:
                                response = frenly_agent.manage_app(AppCommand(
                                    command_type="change_thinking_perspective",
                                    target_perspective=message["thinking_perspective"]
                                ))
                            
                            # Send updated state to all clients
                            await connection_manager.send_frenly_state()
                            
                        except Exception as e:
                            error_msg = {"type": "error", "message": f"Mode change failed: {str(e)}"}
                            await connection_manager.send_personal_message(json.dumps(error_msg), websocket)
                
                else:
                    # Unknown message type
                    print(f"Unknown WebSocket message type: {message.get('type')}")
                    
            except json.JSONDecodeError:
                print("Invalid JSON received from WebSocket")
            except Exception as e:
                print(f"WebSocket message handling error: {e}")
                break
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connection_manager.disconnect(websocket)
        # Stop heartbeat if no more connections
        if not connection_manager.active_connections:
            connection_manager.stop_heartbeat()


# Health check endpoint
@frenly_router.get("/health")
async def frenly_health():
    """Health check for Frenly system."""
    try:
        frenly_agent, frenly_bridge = get_frenly_instances()
        return {"status": "healthy", "message": "Frenly system is operational"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Frenly system error: {str(e)}"}


@frenly_router.post("/websocket/broadcast")
async def broadcast_message(message: str):
    """Broadcast a message to all WebSocket connections."""
    try:
        await connection_manager.broadcast(message)
        return {"success": True, "message": f"Message broadcasted to {len(connection_manager.active_connections)} connections"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@frenly_router.get("/websocket/status")
async def get_websocket_status():
    """Get WebSocket connection status."""
    return {
        "active_connections": len(connection_manager.active_connections),
        "heartbeat_running": connection_manager.heartbeat_running
    }