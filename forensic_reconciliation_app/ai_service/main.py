"""
AI Service Main Module

This module initializes and runs the AI service for the forensic reconciliation app.
It sets up all AI agents, Frenly meta-agent, and provides API endpoints.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import uvicorn
from datetime import datetime

# Import Frenly components
from agents.frenly_meta_agent import FrenlyMetaAgent, AppContext, AppCommand, AppResponse
from agents.frenly_mcp_bridge import FrenlyMCPBridge
from frenly_api import frenly_router

# Import existing agents
from agents.reconciliation_agent import ReconciliationAgent
from agents.fraud_agent import FraudAgent
from agents.risk_agent import RiskAgent
from agents.evidence_agent import EvidenceAgent
from agents.litigation_agent import LitigationAgent
from agents.help_agent import HelpAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Global state
service_state = {
    "status": "initializing",
    "start_time": None,
    "agents": {},
    "frenly": None,
    "frenly_bridge": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifespan of the FastAPI application."""
    # Startup
    logger.info("Starting AI Service...")
    
    try:
        # Initialize Frenly Meta Agent
        logger.info("Initializing Frenly Meta Agent...")
        frenly_agent = FrenlyMetaAgent()
        service_state["frenly"] = frenly_agent
        
        # Initialize Frenly MCP Bridge
        logger.info("Initializing Frenly MCP Bridge...")
        frenly_bridge = FrenlyMCPBridge(frenly_agent)
        service_state["frenly_bridge"] = frenly_bridge
        
        # Initialize specialized AI agents
        logger.info("Initializing specialized AI agents...")
        reconciliation_agent = ReconciliationAgent()
        fraud_agent = FraudAgent()
        risk_agent = RiskAgent()
        evidence_agent = EvidenceAgent()
        litigation_agent = LitigationAgent()
        help_agent = HelpAgent()
        
        # Register agents with Frenly
        logger.info("Registering agents with Frenly...")
        frenly_agent.register_ai_agent("reconciliation_agent", reconciliation_agent)
        frenly_agent.register_ai_agent("fraud_agent", fraud_agent)
        frenly_agent.register_ai_agent("risk_agent", risk_agent)
        frenly_agent.register_ai_agent("evidence_agent", evidence_agent)
        frenly_agent.register_ai_agent("litigation_agent", litigation_agent)
        frenly_agent.register_ai_agent("help_agent", help_agent)
        
        # Register agents with MCP bridge
        frenly_bridge.register_agent("reconciliation_agent", reconciliation_agent)
        frenly_bridge.register_agent("fraud_agent", fraud_agent)
        frenly_bridge.register_agent("risk_agent", risk_agent)
        frenly_bridge.register_agent("evidence_agent", evidence_agent)
        frenly_bridge.register_agent("litigation_agent", litigation_agent)
        frenly_bridge.register_agent("help_agent", help_agent)
        
        # Store agents in service state
        service_state["agents"] = {
            "reconciliation_agent": reconciliation_agent,
            "fraud_agent": fraud_agent,
            "risk_agent": risk_agent,
            "evidence_agent": evidence_agent,
            "litigation_agent": litigation_agent,
            "help_agent": help_agent
        }
        
        # Set Frenly instances in API module
        import frenly_api
        frenly_api.frenly_agent = frenly_agent
        frenly_api.frenly_bridge = frenly_bridge
        
        service_state["status"] = "running"
        service_state["start_time"] = datetime.now()
        
        logger.info("AI Service started successfully!")
        logger.info(f"Frenly initialized with {len(service_state['agents'])} agents")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        service_state["status"] = "error"
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service...")
    service_state["status"] = "shutdown"


# Create FastAPI app
app = FastAPI(
    title="Forensic Reconciliation AI Service",
    description="AI-powered forensic reconciliation and fraud detection service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Frenly router
app.include_router(frenly_router)

# Pydantic models
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    timestamp: datetime
    uptime: Optional[str] = None
    components: Dict[str, Any]


class AgentStatusResponse(BaseModel):
    """Agent status response model."""
    agent_name: str
    status: str
    message: str
    capabilities: List[str]


# API Endpoints

@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Forensic Reconciliation AI Service",
        "version": "1.0.0",
        "status": "running",
        "frenly": "Frenly Meta Agent is managing the system"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    uptime = None
    if service_state["start_time"]:
        uptime = str(datetime.now() - service_state["start_time"])
    
    # Get Frenly system health if available
    components = {}
    if service_state["frenly"]:
        try:
            system_health = service_state["frenly"].get_overall_system_health()
            components = system_health
        except Exception as e:
            components = {"error": str(e)}
    
    return HealthResponse(
        status=service_state["status"],
        service="ai-service",
        timestamp=datetime.now(),
        uptime=uptime,
        components=components
    )


@app.get("/status", tags=["status"])
async def get_service_status():
    """Get detailed service status."""
    return {
        "service": "ai-service",
        "status": service_state["status"],
        "start_time": service_state["start_time"],
        "agents_count": len(service_state["agents"]),
        "frenly_status": "active" if service_state["frenly"] else "inactive",
        "frenly_bridge_status": "active" if service_state["frenly_bridge"] else "inactive"
    }


@app.get("/agents", tags=["agents"])
async def list_agents():
    """List all available AI agents."""
    agents_info = {}
    for name, agent in service_state["agents"].items():
        try:
            if hasattr(agent, 'get_status'):
                status = agent.get_status()
            else:
                status = {"status": "unknown", "message": "No status method"}
            agents_info[name] = status
        except Exception as e:
            agents_info[name] = {"status": "error", "message": str(e)}
    
    return {
        "agents": agents_info,
        "total_count": len(agents_info),
        "frenly_managed": True
    }


@app.get("/agents/{agent_name}", tags=["agents"])
async def get_agent_status(agent_name: str):
    """Get status of a specific agent."""
    if agent_name not in service_state["agents"]:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    agent = service_state["agents"][agent_name]
    try:
        if hasattr(agent, 'get_status'):
            status = agent.get_status()
        else:
            status = {"status": "unknown", "message": "No status method"}
        return {"agent_name": agent_name, **status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")


@app.post("/agents/{agent_name}/execute", tags=["agents"])
async def execute_agent(agent_name: str, command: Dict[str, Any]):
    """Execute a command on a specific agent."""
    if agent_name not in service_state["agents"]:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    agent = service_state["agents"][agent_name]
    try:
        if hasattr(agent, 'execute'):
            result = agent.execute(command)
        elif hasattr(agent, 'process_command'):
            result = agent.process_command(command)
        else:
            raise HTTPException(status_code=400, detail="Agent does not support execution")
        
        return {
            "agent_name": agent_name,
            "command": command,
            "result": result,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent: {str(e)}")


@app.get("/frenly/status", tags=["frenly"])
async def get_frenly_status():
    """Get Frenly meta-agent status."""
    if not service_state["frenly"]:
        raise HTTPException(status_code=503, detail="Frenly not initialized")
    
    try:
        # Get Frenly status through its API
        status_response = service_state["frenly"].manage_app(AppCommand(command_type="get_status"))
        
        return {
            "frenly_status": "active",
            "app_context": status_response.new_context.__dict__ if status_response.new_context else None,
            "system_health": service_state["frenly"].get_overall_system_health(),
            "registered_agents": service_state["frenly"].list_ai_agents(),
            "active_sessions": len(service_state["frenly"].active_sessions),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Frenly status: {str(e)}")


@app.get("/frenly/mode-intersection", tags=["frenly"])
async def get_frenly_mode_intersection():
    """Get current Frenly mode intersection details."""
    if not service_state["frenly"]:
        raise HTTPException(status_code=503, detail="Frenly not initialized")
    
    try:
        response = service_state["frenly"].manage_app(AppCommand(command_type="get_mode_intersection"))
        
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


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "path": request.url.path,
        "timestamp": datetime.now()
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return {
        "error": "Internal Server Error",
        "message": "An internal server error occurred",
        "path": request.url.path,
        "timestamp": datetime.now()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
