#!/usr/bin/env python3
"""
AI Service - Nexus Platform
Comprehensive API endpoints for all AI functionalities
"""

import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service state
service_state = {}

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

async def lifespan(app):
    """Application lifespan manager"""
    logger.info("Starting AI Service...")
    
    # Initialize service components
    try:
        # Initialize Taskmaster
        from taskmaster.core.taskmaster import Taskmaster
        taskmaster = Taskmaster()
        service_state["taskmaster"] = taskmaster
        logger.info("Taskmaster initialized successfully")
        
        # Initialize AI Agents
        from agents.reconciliation_agent import ReconciliationAgent
        from agents.fraud_agent import FraudAgent
        from agents.risk_agent import RiskAgent
        from agents.evidence_agent import EvidenceAgent
        from agents.litigation_agent import LitigationAgent
        from agents.help_agent import HelpAgent
        
        service_state["reconciliation_agent"] = ReconciliationAgent()
        service_state["fraud_agent"] = FraudAgent()
        service_state["risk_agent"] = RiskAgent()
        service_state["evidence_agent"] = EvidenceAgent()
        service_state["litigation_agent"] = LitigationAgent()
        service_state["help_agent"] = HelpAgent()
        
        logger.info("AI Agents initialized successfully")
        
        # Initialize Frenly Meta Agent and MCP Bridge
        from agents.frenly_meta_agent import FrenlyMetaAgent
        from agents.frenly_mcp_bridge import FrenlyMCPBridge
        
        # Create Frenly with configuration
        frenly_config = {
            "enable_ai_classification": True,
            "enable_memory": True,
            "max_memory_size": 1000,
            "response_timeout": 30.0
        }
        
        frenly_agent = FrenlyMetaAgent(frenly_config)
        mcp_bridge = FrenlyMCPBridge({
            "default_timeout": 30.0,
            "max_retries": 3,
            "retry_delay": 1.0
        })
        
        # Register all sub-agents with Frenly and MCP bridge
        frenly_agent.sub_agents = {
            "reconciliation_agent": service_state["reconciliation_agent"],
            "fraud_agent": service_state["fraud_agent"],
            "risk_agent": service_state["risk_agent"],
            "evidence_agent": service_state["evidence_agent"],
            "litigation_agent": service_state["litigation_agent"],
            "help_agent": service_state["help_agent"]
        }
        
        # Register agents with MCP bridge
        for agent_name, agent in frenly_agent.sub_agents.items():
            mcp_bridge.register_agent(agent_name, agent)
        
        # Store Frenly components in service state
        service_state["frenly_agent"] = frenly_agent
        service_state["mcp_bridge"] = mcp_bridge
        
        # Start Frenly components
        await frenly_agent.start()
        await mcp_bridge.start()
        
        logger.info("Frenly Meta Agent and MCP Bridge initialized successfully")
        
        # Initialize Orchestration
        from orchestration.orchestration_manager import OrchestrationManager
        orchestration_manager = OrchestrationManager()
        service_state["orchestration_manager"] = orchestration_manager
        logger.info("Orchestration Manager initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize service components: {e}")
        raise
    
    logger.info("AI Service started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service...")
    # Cleanup resources if needed

# Create FastAPI app
app = FastAPI(
    title="Nexus + Fraud Platform - AI Service",
    description="AI-powered Nexus and fraud detection service with Frenly Meta Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Frenly API routes
from frenly_api import frenly_router
app.include_router(frenly_router)

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Nexus + Fraud Platform - AI Service with Frenly Meta Agent",
        "status": "running",
        "frenly": "Available at /api/frenly"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ai_service",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/status")
async def service_status():
    """Get service status and component health"""
    status = {
        "service": "ai_service",
        "status": "running",
        "components": {}
    }
    
    # Check component status
    for component_name, component in service_state.items():
        try:
            if hasattr(component, 'health_check'):
                health = await component.health_check()
                status["components"][component_name] = health
            else:
                status["components"][component_name] = {"status": "unknown"}
        except Exception as e:
            status["components"][component_name] = {"status": "error", "error": str(e)}
    
    return status

@app.get("/frenly/status")
async def frenly_status():
    """Get Frenly meta agent status"""
    try:
        frenly_agent = service_state.get("frenly_agent")
        mcp_bridge = service_state.get("mcp_bridge")
        
        if not frenly_agent or not mcp_bridge:
            raise HTTPException(status_code=503, detail="Frenly components not available")
        
        agent_status = frenly_agent.get_agent_status()
        bridge_status = mcp_bridge.get_bridge_status()
        
        return {
            "frenly_agent": agent_status,
            "mcp_bridge": bridge_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Frenly status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/reconciliation")
async def process_reconciliation(data: Dict[str, Any]):
    """Process reconciliation request"""
    try:
        reconciliation_agent = service_state.get("reconciliation_agent")
        if not reconciliation_agent:
            raise HTTPException(status_code=500, detail="Reconciliation agent not available")
        
        # Process the reconciliation request
        result = await reconciliation_agent.process_reconciliation(data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Reconciliation processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/fraud")
async def process_fraud(data: Dict[str, Any]):
    """Process fraud detection request"""
    try:
        fraud_agent = service_state.get("fraud_agent")
        if not fraud_agent:
            raise HTTPException(status_code=500, detail="Fraud agent not available")
        
        # Process the fraud detection request
        result = await fraud_agent.process_fraud_detection(data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Fraud detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
