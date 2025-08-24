"""
Frenly API - FastAPI endpoints for interacting with Frenly Meta Agent

This module provides REST API endpoints for managing the forensic reconciliation app
through Frenly's intelligent orchestration system.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from agents.frenly_meta_agent import AppContext, AppCommand, AppResponse, FrenlyMetaAgent
from agents.frenly_mcp_bridge import FrenlyMCPBridge

# Create router
frenly_router = APIRouter(prefix="/api/frenly", tags=["frenly"])

# Global instances (will be initialized in main.py)
frenly_agent: Optional[FrenlyMetaAgent] = None
frenly_bridge: Optional[FrenlyMCPBridge] = None


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
def get_frenly_instances():
    """Get the Frenly agent and bridge instances."""
    if frenly_agent is None or frenly_bridge is None:
        raise HTTPException(status_code=503, detail="Frenly system not initialized")
    return frenly_agent, frenly_bridge


# API Endpoints

@frenly_router.post("/query", response_model=FrenlyQueryResponse)
async def query_frenly(
    request: FrenlyQueryRequest,
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Send a query to Frenly for intelligent processing.
    
    This endpoint allows users to ask Frenly questions or request actions,
    and Frenly will intelligently route the request to appropriate agents.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Create an AppCommand from the query
        command = AppCommand(
            command_type="query",
            parameters={"query": request.query, "context": request.context or {}}
        )
        
        # Execute through Frenly
        response = frenly_bridge.execute_command(command)
        
        return FrenlyQueryResponse(
            success=response.success,
            message=response.message,
            response=response,
            context=request.context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@frenly_router.get("/status", response_model=FrenlyStatusResponse)
async def get_frenly_status(
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Get the current status of Frenly and the app.
    
    Returns comprehensive status information including app context,
    system health, and agent status.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Get app status
        status_response = frenly_agent.manage_app(AppCommand(command_type="get_status"))
        
        # Get system health
        system_health = frenly_agent.get_overall_system_health()
        
        # Get agent status
        agent_status = frenly_bridge.get_agent_status()
        
        return FrenlyStatusResponse(
            success=status_response.success,
            message=status_response.message,
            app_context=status_response.new_context.__dict__ if status_response.new_context else None,
            system_health=system_health,
            agent_status=agent_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@frenly_router.post("/context", response_model=FrenlyContextResponse)
async def update_frenly_context(
    request: FrenlyContextRequest,
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Update Frenly's app context.
    
    Allows updating various aspects of the app context including
    app mode, thinking perspective, AI mode, dashboard view, and user role.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Store old context
        old_context = frenly_agent.app_context.__dict__.copy()
        
        # Update context based on request
        if request.app_mode:
            frenly_agent.manage_app(AppCommand(
                command_type="switch_app_mode",
                target_mode=request.app_mode
            ))
        
        if request.thinking_perspective:
            frenly_agent.manage_app(AppCommand(
                command_type="change_thinking_perspective",
                target_perspective=request.thinking_perspective
            ))
        
        if request.ai_mode:
            frenly_agent.manage_app(AppCommand(
                command_type="change_ai_mode",
                target_ai_mode=request.ai_mode
            ))
        
        if request.dashboard_view:
            frenly_agent.manage_app(AppCommand(
                command_type="change_dashboard_view",
                target_view=request.dashboard_view
            ))
        
        if request.user_role:
            frenly_agent.manage_app(AppCommand(
                command_type="change_user_role",
                target_role=request.user_role
            ))
        
        # Get new context
        new_context = frenly_agent.app_context.__dict__.copy()
        
        return FrenlyContextResponse(
            success=True,
            message="Context updated successfully",
            old_context=old_context,
            new_context=new_context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating context: {str(e)}")


@frenly_router.post("/workflow", response_model=FrenlyWorkflowResponse)
async def execute_frenly_workflow(
    request: FrenlyWorkflowRequest,
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Execute a predefined workflow through Frenly.
    
    Allows execution of complex workflows that involve multiple agents
    and coordinated actions.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Create command for workflow execution
        command = AppCommand(
            command_type="execute_workflow",
            parameters={
                "workflow_name": request.workflow_name,
                "workflow_params": request.parameters or {}
            }
        )
        
        # Execute through Frenly
        response = frenly_bridge.execute_command(command)
        
        return FrenlyWorkflowResponse(
            success=response.success,
            message=response.message,
            workflow_result=response.__dict__ if response else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")


@frenly_router.post("/switch-mode", response_model=FrenlyModeSwitchResponse)
async def switch_frenly_mode(
    request: FrenlyModeSwitchRequest,
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Switch Frenly's operational mode.
    
    Allows switching between different app modes, thinking perspectives,
    and AI modes to adapt the system behavior.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Store old configuration
        old_config = {
            "app_mode": frenly_agent.app_context.app_mode.value,
            "thinking_perspective": frenly_agent.app_context.thinking_perspective.value if frenly_agent.app_context.thinking_perspective else None,
            "ai_mode": frenly_agent.app_context.ai_mode.value
        }
        
        # Execute mode switches
        if request.app_mode:
            frenly_agent.manage_app(AppCommand(
                command_type="switch_app_mode",
                target_mode=request.app_mode
            ))
        
        if request.thinking_perspective:
            frenly_agent.manage_app(AppCommand(
                command_type="change_thinking_perspective",
                target_perspective=request.thinking_perspective
            ))
        
        if request.ai_mode:
            frenly_agent.manage_app(AppCommand(
                command_type="change_ai_mode",
                target_ai_mode=request.ai_mode
            ))
        
        # Get new configuration
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
        raise HTTPException(status_code=500, detail=f"Error switching mode: {str(e)}")


@frenly_router.get("/mode-intersection")
async def get_frenly_mode_intersection(
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Get the current mode intersection details.
    
    Returns detailed information about the current mode intersection
    including features, limitations, recommended views, and agent priorities.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Get mode intersection
        response = frenly_agent.manage_app(AppCommand(command_type="get_mode_intersection"))
        
        if response.success:
            return {
                "success": True,
                "message": response.message,
                "recommendations": response.recommendations,
                "next_actions": response.next_actions
            }
        else:
            raise HTTPException(status_code=404, detail=response.message)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mode intersection: {str(e)}")


@frenly_router.get("/agents")
async def get_frenly_agents(
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Get information about all registered agents.
    
    Returns status and information about all AI agents
    registered with Frenly.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Get agent information
        agent_status = frenly_bridge.get_agent_status()
        registered_agents = frenly_agent.list_ai_agents()
        
        return {
            "success": True,
            "registered_agents": registered_agents,
            "agent_status": agent_status,
            "total_agents": len(registered_agents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent information: {str(e)}")


@frenly_router.get("/workflows")
async def get_frenly_workflows(
    frenly_instances = Depends(get_frenly_instances)
):
    """
    Get information about all registered workflows.
    
    Returns information about all workflows registered
    with Frenly's MCP bridge.
    """
    try:
        frenly_agent, frenly_bridge = frenly_instances
        
        # Get workflow information
        workflow_status = frenly_bridge.get_workflow_status()
        
        return {
            "success": True,
            "workflows": workflow_status,
            "total_workflows": len(workflow_status)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting workflow information: {str(e)}")


# Health check endpoint
@frenly_router.get("/health")
async def frenly_health_check():
    """
    Health check endpoint for Frenly.
    
    Returns basic health status without requiring
    Frenly instances to be initialized.
    """
    return {
        "status": "healthy",
        "service": "frenly-api",
        "message": "Frenly API is running"
    }
