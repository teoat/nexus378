
"""
Frenly Meta Agent - Central App Manager & Orchestrator

Frenly is the intelligent conductor that manages the entire forensic reconciliation app.
She orchestrates specialized AI agents, manages app modes, and provides contextual guidance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import asyncio
import threading
import time
import json
import requests # Added for service status checks
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration to prevent typos."""
    ACTIVE = "active"
    FAILED = "failed"
    RESTARTING = "restarting"
    UNKNOWN = "unknown"


class AppMode(Enum):
    """What the app calculates - the core accounting methodology."""
    CONSTRUCTION = "construction"  # Construction project accounting (different calculations)
    REGULAR = "regular"           # Standard business accounting (traditional statements)
    ACCOUNTING = "accounting"     # Default accounting functions (always available)
    AUDIT = "audit"              # Default audit functions (always available)


class ThinkingPerspective(Enum):
    """How to assess and analyze the data - the analytical approach."""
    INVESTIGATION = "investigation"  # Forensic investigation thinking
    LITIGATION = "litigation"        # Legal/legal proceedings thinking


class AIMode(Enum):
    """How to produce final results - the processing intensity."""
    GUIDED = "guided"    # Step-by-step guidance with explanations
    ECO = "eco"          # Minimal AI usage, heuristic-based
    EXTREME = "extreme"  # Full AI orchestration, predictive analysis


class DashboardView(Enum):
    """Available dashboard views for different user needs."""
    RECONCILIATION = "reconciliation"
    FRAUD_ANALYSIS = "fraud_analysis"
    EVIDENCE_VIEWER = "evidence_viewer"
    ENTITY_NETWORK = "entity_network"
    LEGAL_ANALYSIS = "legal_analysis"
    CONSTRUCTION_PROJECTS = "construction_projects"
    FINANCIAL_STATEMENTS = "financial_statements"
    AUDIT_TRAILS = "audit_trails"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_REPORTS = "compliance_reports"


class UserRole(Enum):
    """User roles that determine access and capabilities."""
    AUDITOR = "auditor"
    INVESTIGATOR = "investigator"
    PROSECUTOR = "prosecutor"
    JUDGE = "judge"
    ACCOUNTANT = "accountant"
    PROJECT_MANAGER = "project_manager"


class SystemComponent(Enum):
    """Core system components that Frenly manages."""
    AI_AGENTS = "ai_agents"
    DATABASE = "database"
    FILE_STORAGE = "file_storage"
    API_GATEWAY = "api_gateway"
    FRONTEND = "frontend"
    MONITORING = "monitoring"


@dataclass
class AppContext:
    """Current application context and state."""
    app_mode: AppMode = AppMode.ACCOUNTING
    thinking_perspective: Optional[ThinkingPerspective] = None
    ai_mode: AIMode = AIMode.GUIDED
    dashboard_view: DashboardView = DashboardView.RECONCILIATION
    user_role: UserRole = UserRole.AUDITOR
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AppCommand:
    """Commands that can be sent to Frenly for app management."""
    command_type: str
    target_mode: Optional[str] = None
    target_perspective: Optional[str] = None
    target_ai_mode: Optional[str] = None
    target_view: Optional[str] = None
    user_role: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppResponse:
    """Frenly's response to app management commands."""
    success: bool
    message: str
    new_context: Optional[AppContext] = None
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)


@dataclass
class ModeIntersection:
    """Represents the intersection of app mode, thinking perspective, and AI mode."""
    app_mode: AppMode
    thinking_perspective: Optional[ThinkingPerspective]
    ai_mode: AIMode
    description: str
    features: List[str]
    limitations: List[str]
    recommended_views: List[DashboardView]
    agent_priorities: List[str]
    calculation_methods: List[str]
    assessment_approaches: List[str]


class FrenlyMetaAgent:
    """
    Frenly - Central App Manager & Orchestrator
    
    Frenly manages the entire forensic reconciliation app, orchestrating specialized AI agents
    and providing intelligent guidance based on the current app context.
    """
    
    def __init__(self):
        """Initialize Frenly with default app context and mode intersections."""
        self.app_context = AppContext()
        self.active_sessions: Dict[str, AppContext] = {}
        self.system_components: Dict[SystemComponent, Dict[str, Any]] = {}
        self.ai_agents: Dict[str, Any] = {}
        self.mode_intersections: Dict[str, ModeIntersection] = {}
        self.known_services: Dict[str, Dict[str, Any]] = {} # New: For service discovery
        
        # Agent health monitoring
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        self.heartbeat_thread = None
        self.heartbeat_running = False
        self.state_change_callbacks: List[callable] = [] # New: Callbacks for state changes
        self.workflows: Dict[str, Dict[str, Any]] = {} # New: Store workflow definitions
        self.workflow_status: Dict[str, Dict[str, Any]] = {} # New: Track running workflow instances
        self.error_log: List[Dict[str, Any]] = [] # New: Store error events
        self.metrics: Dict[str, Any] = { # New: Store basic metrics
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "command_response_times": [] # Store response times for average
        }
        
        # Initialize mode intersections
        self._initialize_mode_intersections()
        
        # Initialize system components
        self._initialize_system_components()
        # Initialize workflows
        self._initialize_workflows()
        
        # State file paths
        self.state_dir = Path(".taskmaster")
        self.state_dir.mkdir(exist_ok=True)
        self.context_file = self.state_dir / "frenly_state.json"
        self.modes_file = self.state_dir / "frenly_modes.json"
        
        # Load saved state on startup
        self._load_context_from_file()
        self._load_modes_from_file()
        
        logger.info("Frenly Meta Agent initialized successfully")
    
    def _initialize_mode_intersections(self):
        """Initialize all possible mode intersections with their characteristics."""
        
        # Construction Mode Intersections
        self.mode_intersections["construction_guided"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=None,
            ai_mode=AIMode.GUIDED,
            description="Construction projects with guided AI assistance",
            features=[
                "Step-by-step project cost analysis",
                "Guided milestone tracking",
                "Construction-specific calculations",
                "Vendor payment reconciliation",
                "Project timeline management"
            ],
            limitations=[
                "Limited predictive analysis",
                "Basic fraud detection",
                "Standard risk assessment"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.RECONCILIATION,
                DashboardView.FRAUD_ANALYSIS
            ],
            agent_priorities=[
                "reconciliation_agent",
                "fraud_agent",
                "risk_agent"
            ],
            calculation_methods=[
                "Percentage of completion method",
                "Completed contract method",
                "Cost-plus pricing calculations",
                "Change order impact analysis"
            ],
            assessment_approaches=[
                "Milestone-based progress tracking",
                "Cost variance analysis",
                "Schedule performance index"
            ]
        )
        
        self.mode_intersections["construction_eco"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=None,
            ai_mode=AIMode.ECO,
            description="Construction projects with minimal AI usage",
            features=[
                "Basic project cost calculations",
                "Simple milestone tracking",
                "Heuristic-based analysis",
                "Standard reporting"
            ],
            limitations=[
                "No predictive analysis",
                "Basic fraud detection",
                "Limited risk assessment"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.RECONCILIATION
            ],
            agent_priorities=[
                "reconciliation_agent",
                "fraud_agent"
            ],
            calculation_methods=[
                "Basic percentage of completion",
                "Simple cost tracking",
                "Standard variance calculations"
            ],
            assessment_approaches=[
                "Basic progress tracking",
                "Simple cost analysis"
            ]
        )
        
        self.mode_intersections["construction_extreme"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=None,
            ai_mode=AIMode.EXTREME,
            description="Construction projects with full AI orchestration",
            features=[
                "Predictive project analysis",
                "Advanced fraud detection",
                "Automated risk assessment",
                "Intelligent cost optimization",
                "Predictive timeline analysis",
                "Advanced vendor relationship mapping"
            ],
            limitations=[
                "Higher computational cost",
                "More complex analysis",
                "Requires more data"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.FRAUD_ANALYSIS,
                DashboardView.ENTITY_NETWORK,
                DashboardView.LEGAL_ANALYSIS
            ],
            agent_priorities=[
                "reconciliation_agent",
                "fraud_agent",
                "risk_agent",
                "evidence_agent",
                "litigation_agent"
            ],
            calculation_methods=[
                "Advanced percentage of completion",
                "Predictive cost modeling",
                "Machine learning-based variance analysis",
                "AI-powered change order impact"
            ],
            assessment_approaches=[
                "Predictive progress tracking",
                "Advanced risk modeling",
                "AI-powered fraud detection"
            ]
        )
        
        # Regular Mode Intersections
        self.mode_intersections["regular_guided"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=None,
            ai_mode=AIMode.GUIDED,
            description="Regular business accounting with guided AI assistance",
            features=[
                "Step-by-step financial analysis",
                "Guided reconciliation processes",
                "Standard accounting calculations",
                "Business performance tracking",
                "Financial statement preparation"
            ],
            limitations=[
                "Limited predictive analysis",
                "Basic anomaly detection",
                "Standard risk assessment"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.RECONCILIATION,
                DashboardView.FRAUD_ANALYSIS
            ],
            agent_priorities=[
                "reconciliation_agent",
                "fraud_agent",
                "risk_agent"
            ],
            calculation_methods=[
                "Accrual accounting",
                "Cash basis accounting",
                "Standard financial ratios",
                "Variance analysis"
            ],
            assessment_approaches=[
                "Financial statement analysis",
                "Ratio analysis",
                "Trend analysis"
            ]
        )
        
        self.mode_intersections["regular_eco"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=None,
            ai_mode=AIMode.ECO,
            description="Regular business accounting with minimal AI usage",
            features=[
                "Basic financial calculations",
                "Simple reconciliation",
                "Heuristic-based analysis",
                "Standard reporting"
            ],
            limitations=[
                "No predictive analysis",
                "Basic fraud detection",
                "Limited risk assessment"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.RECONCILIATION
            ],
            agent_priorities=[
                "reconciliation_agent",
                "fraud_agent"
            ],
            calculation_methods=[
                "Basic accrual accounting",
                "Simple financial ratios",
                "Standard variance calculations"
            ],
            assessment_approaches=[
                "Basic financial analysis",
                "Simple trend analysis"
            ]
        )
        
        self.mode_intersections["regular_extreme"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=None,
            ai_mode=AIMode.EXTREME,
            description="Regular business accounting with full AI orchestration",
            features=[
                "Predictive financial analysis",
                "Advanced fraud detection",
                "Automated risk assessment",
                "Intelligent financial optimization",
                "Predictive cash flow analysis",
                "Advanced business intelligence"
            ],
            limitations=[
                "Higher computational cost",
                "More complex analysis",
                "Requires more data"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.FRAUD_ANALYSIS,
                DashboardView.ENTITY_NETWORK,
                DashboardView.LEGAL_ANALYSIS
            ],
            agent_priorities=[
                "reconciliation_agent",
                "fraud_agent",
                "risk_agent",
                "evidence_agent",
                "litigation_agent"
            ],
            calculation_methods=[
                "Advanced financial modeling",
                "Predictive analytics",
                "Machine learning-based analysis",
                "AI-powered risk assessment"
            ],
            assessment_approaches=[
                "Predictive financial analysis",
                "Advanced risk modeling",
                "AI-powered fraud detection"
            ]
        )
        
        # Add missing investigation mode intersections
        self.mode_intersections["construction_investigation_guided"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=ThinkingPerspective.INVESTIGATION,
            ai_mode=AIMode.GUIDED,
            description="Construction projects with investigation thinking and guided AI",
            features=[
                "Forensic project analysis",
                "Evidence collection guidance",
                "Suspicious pattern detection",
                "Guided investigation workflow",
                "Construction fraud detection"
            ],
            limitations=[
                "Limited predictive analysis",
                "Basic evidence analysis",
                "Standard investigation tools"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.EVIDENCE_VIEWER,
                DashboardView.FRAUD_ANALYSIS
            ],
            agent_priorities=[
                "evidence_agent",
                "fraud_agent",
                "reconciliation_agent"
            ],
            calculation_methods=[
                "Forensic cost analysis",
                "Evidence-based calculations",
                "Suspicious pattern identification"
            ],
            assessment_approaches=[
                "Forensic investigation methodology",
                "Evidence chain analysis",
                "Pattern recognition"
            ]
        )
        
        self.mode_intersections["regular_investigation_guided"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=ThinkingPerspective.INVESTIGATION,
            ai_mode=AIMode.GUIDED,
            description="Regular business with investigation thinking and guided AI",
            features=[
                "Forensic financial analysis",
                "Evidence collection guidance",
                "Suspicious pattern detection",
                "Guided investigation workflow",
                "Business fraud detection"
            ],
            limitations=[
                "Limited predictive analysis",
                "Basic evidence analysis",
                "Standard investigation tools"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.EVIDENCE_VIEWER,
                DashboardView.FRAUD_ANALYSIS
            ],
            agent_priorities=[
                "evidence_agent",
                "fraud_agent",
                "reconciliation_agent"
            ],
            calculation_methods=[
                "Forensic financial analysis",
                "Evidence-based calculations",
                "Suspicious pattern identification"
            ],
            assessment_approaches=[
                "Forensic investigation methodology",
                "Evidence chain analysis",
                "Pattern recognition"
            ]
        )
        
        # Add litigation mode intersections
        self.mode_intersections["construction_litigation_guided"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=ThinkingPerspective.LITIGATION,
            ai_mode=AIMode.GUIDED,
            description="Construction projects with litigation thinking and guided AI",
            features=[
                "Legal compliance analysis",
                "Contract violation detection",
                "Guided legal assessment",
                "Construction law compliance",
                "Litigation preparation support"
            ],
            limitations=[
                "Limited predictive analysis",
                "Basic legal analysis",
                "Standard compliance tools"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.LEGAL_ANALYSIS,
                DashboardView.COMPLIANCE_REPORTS
            ],
            agent_priorities=[
                "litigation_agent",
                "reconciliation_agent",
                "fraud_agent"
            ],
            calculation_methods=[
                "Legal compliance calculations",
                "Contract violation analysis",
                "Regulatory requirement checking"
            ],
            assessment_approaches=[
                "Legal compliance methodology",
                "Contract analysis",
                "Regulatory assessment"
            ]
        )
        
        self.mode_intersections["regular_litigation_guided"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=ThinkingPerspective.LITIGATION,
            ai_mode=AIMode.GUIDED,
            description="Regular business with litigation thinking and guided AI",
            features=[
                "Legal compliance analysis",
                "Contract violation detection",
                "Guided legal assessment",
                "Business law compliance",
                "Litigation preparation support"
            ],
            limitations=[
                "Limited predictive analysis",
                "Basic legal analysis",
                "Standard compliance tools"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.LEGAL_ANALYSIS,
                DashboardView.COMPLIANCE_REPORTS
            ],
            agent_priorities=[
                "litigation_agent",
                "reconciliation_agent",
                "fraud_agent"
            ],
            calculation_methods=[
                "Legal compliance calculations",
                "Contract violation analysis",
                "Regulatory requirement checking"
            ],
            assessment_approaches=[
                "Legal compliance methodology",
                "Contract analysis",
                "Regulatory assessment"
            ]
        )
        
        # Add missing extreme mode intersections
        self.mode_intersections["construction_investigation_extreme"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=ThinkingPerspective.INVESTIGATION,
            ai_mode=AIMode.EXTREME,
            description="Construction projects with investigation thinking and extreme AI",
            features=[
                "Advanced forensic project analysis",
                "AI-powered evidence collection",
                "Predictive pattern detection",
                "Automated investigation workflow",
                "Advanced construction fraud detection"
            ],
            limitations=[
                "Higher computational cost",
                "More complex analysis",
                "Requires more data"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.EVIDENCE_VIEWER,
                DashboardView.FRAUD_ANALYSIS,
                DashboardView.ENTITY_NETWORK
            ],
            agent_priorities=[
                "evidence_agent",
                "fraud_agent",
                "reconciliation_agent",
                "risk_agent",
                "litigation_agent"
            ],
            calculation_methods=[
                "AI-powered forensic cost analysis",
                "Machine learning evidence analysis",
                "Predictive pattern identification"
            ],
            assessment_approaches=[
                "AI-enhanced investigation methodology",
                "Predictive evidence chain analysis",
                "Advanced pattern recognition"
            ]
        )
        
        self.mode_intersections["regular_investigation_extreme"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=ThinkingPerspective.INVESTIGATION,
            ai_mode=AIMode.EXTREME,
            description="Regular business with investigation thinking and extreme AI",
            features=[
                "Advanced forensic financial analysis",
                "AI-powered evidence collection",
                "Predictive pattern detection",
                "Automated investigation workflow",
                "Advanced business fraud detection"
            ],
            limitations=[
                "Higher computational cost",
                "More complex analysis",
                "Requires more data"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.EVIDENCE_VIEWER,
                DashboardView.FRAUD_ANALYSIS,
                DashboardView.ENTITY_NETWORK
            ],
            agent_priorities=[
                "evidence_agent",
                "fraud_agent",
                "reconciliation_agent",
                "risk_agent",
                "litigation_agent"
            ],
            calculation_methods=[
                "AI-powered forensic financial analysis",
                "Machine learning evidence analysis",
                "Predictive pattern identification"
            ],
            assessment_approaches=[
                "AI-enhanced investigation methodology",
                "Predictive evidence chain analysis",
                "Advanced pattern recognition"
            ]
        )
        
        self.mode_intersections["construction_litigation_extreme"] = ModeIntersection(
            app_mode=AppMode.CONSTRUCTION,
            thinking_perspective=ThinkingPerspective.LITIGATION,
            ai_mode=AIMode.EXTREME,
            description="Construction projects with litigation thinking and extreme AI",
            features=[
                "Advanced legal compliance analysis",
                "AI-powered contract violation detection",
                "Predictive legal assessment",
                "Advanced construction law compliance",
                "AI-enhanced litigation preparation"
            ],
            limitations=[
                "Higher computational cost",
                "More complex analysis",
                "Requires more data"
            ],
            recommended_views=[
                DashboardView.CONSTRUCTION_PROJECTS,
                DashboardView.LEGAL_ANALYSIS,
                DashboardView.COMPLIANCE_REPORTS,
                DashboardView.ENTITY_NETWORK
            ],
            agent_priorities=[
                "litigation_agent",
                "reconciliation_agent",
                "fraud_agent",
                "risk_agent",
                "evidence_agent"
            ],
            calculation_methods=[
                "AI-powered legal compliance calculations",
                "Machine learning contract analysis",
                "Predictive regulatory assessment"
            ],
            assessment_approaches=[
                "AI-enhanced legal methodology",
                "Predictive contract analysis",
                "Advanced regulatory assessment"
            ]
        )
        
        self.mode_intersections["regular_litigation_extreme"] = ModeIntersection(
            app_mode=AppMode.REGULAR,
            thinking_perspective=ThinkingPerspective.LITIGATION,
            ai_mode=AIMode.EXTREME,
            description="Regular business with litigation thinking and extreme AI",
            features=[
                "Advanced legal compliance analysis",
                "AI-powered contract violation detection",
                "Predictive legal assessment",
                "Advanced business law compliance",
                "AI-enhanced litigation preparation"
            ],
            limitations=[
                "Higher computational cost",
                "More complex analysis",
                "Requires more data"
            ],
            recommended_views=[
                DashboardView.FINANCIAL_STATEMENTS,
                DashboardView.LEGAL_ANALYSIS,
                DashboardView.COMPLIANCE_REPORTS,
                DashboardView.ENTITY_NETWORK
            ],
            agent_priorities=[
                "litigation_agent",
                "reconciliation_agent",
                "fraud_agent",
                "risk_agent",
                "evidence_agent"
            ],
            calculation_methods=[
                "AI-powered legal compliance calculations",
                "Machine learning contract analysis",
                "Predictive regulatory assessment"
            ],
            assessment_approaches=[
                "AI-enhanced legal methodology",
                "Predictive contract analysis",
                "Advanced regulatory assessment"
            ]
        )
    
    def _initialize_system_components(self):
        """Initialize system component status tracking."""
        for component in SystemComponent:
            self.system_components[component] = {
                "status": "operational",
                "last_check": datetime.now(),
                "performance_metrics": {}
            }
        
        # Initialize known services for basic service discovery
        self.known_services = {
            "frontend": {"url": "http://localhost:3000", "status": "unknown", "last_check": None},
            "backend": {"url": "http://localhost:8000", "status": "unknown", "last_check": None},
            "database": {"url": "postgresql://localhost:5432", "status": "unknown", "last_check": None} # Placeholder URL
        }

    def _initialize_workflows(self):
        """Define and initialize known workflows."""
        self.workflows["reconciliation_check"] = {
            "name": "reconciliation_check",
            "description": "Performs a basic reconciliation check workflow.",
            "steps": [
                {"name": "start_reconciliation", "agent": "reconciliation_agent", "status": "pending"},
                {"name": "process_transactions", "agent": "transaction_agent", "status": "pending"},
                {"name": "complete_check", "agent": "reporting_agent", "status": "pending"}
            ]
        }
        logger.info("Workflows initialized.")
    
    def _save_context_to_file(self):
        """Save the current app context to a JSON file."""
        try:
            # Create backup of previous state
            if self.context_file.exists():
                backup_file = self.context_file.with_suffix('.backup')
                self.context_file.rename(backup_file)
            
            # Save current context with version info
            context_data = {
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "app_context": {
                    "app_mode": self.app_context.app_mode.value,
                    "thinking_perspective": self.app_context.thinking_perspective.value if self.app_context.thinking_perspective else None,
                    "ai_mode": self.app_context.ai_mode.value,
                    "dashboard_view": self.app_context.dashboard_view.value,
                    "user_role": self.app_context.user_role.value,
                    "session_id": self.app_context.session_id,
                    "timestamp": self.app_context.timestamp.isoformat()
                }
            }
            
            # Use atomic file operation (write to temp, then rename)
            temp_file = self.context_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(context_data, f, indent=2, default=str)
            
            temp_file.rename(self.context_file)
            logger.info(f"App context saved to {self.context_file}")
            
        except Exception as e:
            logger.error(f"Error saving context to file: {e}")
            # Restore backup if save failed
            if 'backup_file' in locals() and backup_file.exists():
                backup_file.rename(self.context_file)
    
    def _load_context_from_file(self):
        """Load the app context from a JSON file."""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    loaded_data = json.load(f)
                
                # Validate loaded data
                if "app_context" in loaded_data and "version" in loaded_data:
                    context_data = loaded_data["app_context"]
                    
                    # Check required fields
                    required_fields = ["app_mode", "ai_mode", "dashboard_view", "user_role"]
                    if all(field in context_data for field in required_fields):
                        # Reconstruct AppContext
                        self.app_context.app_mode = AppMode(context_data["app_mode"])
                        self.app_context.ai_mode = AIMode(context_data["ai_mode"])
                        self.app_context.dashboard_view = DashboardView(context_data["dashboard_view"])
                        self.app_context.user_role = UserRole(context_data["user_role"])
                        
                        if context_data.get("thinking_perspective"):
                            self.app_context.thinking_perspective = ThinkingPerspective(context_data["thinking_perspective"])
                        
                        if context_data.get("session_id"):
                            self.app_context.session_id = context_data["session_id"]
                        
                        if context_data.get("timestamp"):
                            try:
                                self.app_context.timestamp = datetime.fromisoformat(context_data["timestamp"])
                            except ValueError:
                                self.app_context.timestamp = datetime.now()
                        
                        logger.info(f"App context loaded from {self.context_file}")
                        logger.info(f"Loaded context: mode={self.app_context.app_mode.value}, ai_mode={self.app_context.ai_mode.value}")
                    else:
                        logger.warning(f"Missing required fields in context file. Using default context.")
                else:
                    logger.warning(f"Invalid context file format. Using default context.")
                    
            except json.JSONDecodeError:
                logger.warning(f"Could not decode JSON from {self.context_file}. Starting with default context.")
            except Exception as e:
                logger.error(f"Error loading context from file: {e}")
        else:
            logger.info(f"No existing context file found at {self.context_file}. Starting with default context.")
    
    def _save_modes_to_file(self):
        """Save all mode intersections to a JSON file."""
        try:
            # Create backup of previous state
            if self.modes_file.exists():
                backup_file = self.modes_file.with_suffix('.backup')
                self.modes_file.rename(backup_file)
            
            # Convert mode intersections to serializable format
            serializable_modes = {}
            for key, mode_intersection in self.mode_intersections.items():
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
            
            # Add metadata
            modes_data = {
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "mode_intersections": serializable_modes
            }
            
            # Use atomic file operation
            temp_file = self.modes_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(modes_data, f, indent=2, default=str)
            
            temp_file.rename(self.modes_file)
            logger.info(f"Mode intersections saved to {self.modes_file}")
            
        except Exception as e:
            logger.error(f"Error saving modes to file: {e}")
            # Restore backup if save failed
            if 'backup_file' in locals() and backup_file.exists():
                backup_file.rename(self.modes_file)
    
    def _load_modes_from_file(self):
        """Load mode intersections from a JSON file."""
        if self.modes_file.exists():
            try:
                with open(self.modes_file, 'r') as f:
                    loaded_data = json.load(f)
                
                # Validate loaded data
                if "mode_intersections" in loaded_data and "version" in loaded_data:
                    modes_data = loaded_data["mode_intersections"]
                    
                    # Reconstruct mode intersections
                    for key, mode_data in modes_data.items():
                        try:
                            app_mode = AppMode(mode_data["app_mode"])
                            ai_mode = AIMode(mode_data["ai_mode"])
                            thinking_perspective = None
                            if mode_data.get("thinking_perspective"):
                                thinking_perspective = ThinkingPerspective(mode_data["thinking_perspective"])
                            
                            recommended_views = [DashboardView(view) for view in mode_data["recommended_views"]]
                            
                            mode_intersection = ModeIntersection(
                                app_mode=app_mode,
                                thinking_perspective=thinking_perspective,
                                ai_mode=ai_mode,
                                description=mode_data["description"],
                                features=mode_data["features"],
                                limitations=mode_data["limitations"],
                                recommended_views=recommended_views,
                                agent_priorities=mode_data["agent_priorities"],
                                calculation_methods=mode_data["calculation_methods"],
                                assessment_approaches=mode_data["assessment_approaches"]
                            )
                            
                            self.mode_intersections[key] = mode_intersection
                            
                        except (ValueError, KeyError) as e:
                            logger.warning(f"Error reconstructing mode intersection {key}: {e}")
                            continue
                    
                    logger.info(f"Mode intersections loaded from {self.modes_file}")
                    
                else:
                    logger.warning(f"Invalid modes file format. Using default mode intersections.")
                    
            except json.JSONDecodeError:
                logger.warning(f"Could not decode JSON from {self.modes_file}. Using default mode intersections.")
            except Exception as e:
                logger.error(f"Error loading modes from file: {e}")
        else:
            logger.info(f"No existing modes file found at {self.modes_file}. Using default mode intersections.")
    
    def manage_app(self, command: AppCommand) -> AppResponse:
        """
        Main method for managing the app based on commands.
        
        Args:
            command: The command to execute
            
        Returns:
            AppResponse with results and recommendations
        """
        try:
            if command.command_type == "switch_app_mode":
                return self._switch_app_mode(command.target_mode)
            elif command.command_type == "change_thinking_perspective":
                return self._change_thinking_perspective(command.target_perspective)
            elif command.command_type == "change_ai_mode":
                return self._change_ai_mode(command.target_ai_mode)
            elif command.command_type == "change_dashboard_view":
                return self._change_dashboard_view(command.target_view)
            elif command.command_type == "change_user_role":
                return self._change_user_role(command.user_role)
            elif command.command_type == "get_status":
                return self._get_app_status()
            elif command.command_type == "get_mode_intersection":
                return self._get_current_mode_intersection_response()
            else:
                return AppResponse(
                    success=False,
                    message=f"Unknown command type: {command.command_type}"
                )
        except Exception as e:
            logger.error(f"Error managing app: {str(e)}")
            return AppResponse(
                success=False,
                message=f"App management error: {str(e)}"
            )
    
    def _switch_app_mode(self, new_mode: str) -> AppResponse:
        """Switch the app mode (what the app calculates)."""
        try:
            old_mode = self.app_context.app_mode
            self.app_context.app_mode = AppMode(new_mode)
            self.app_context.timestamp = datetime.now()
            
            # Update mode intersection
            self._update_mode_intersection()
            
            # Auto-save context and modes
            self._save_context_to_file()
            self._save_modes_to_file()
            
            # Notify state change
            await self._notify_state_change()
            
            # Log the mode change event
            self._log_event("mode_change", {
                "old_mode": old_mode.value,
                "new_mode": new_mode,
                "timestamp": self.app_context.timestamp.isoformat()
            })
            
            return AppResponse(
                success=True,
                message=f"Successfully switched from {old_mode.value} to {new_mode}",
                new_context=self.app_context,
                recommendations=[
                    f"Use {new_mode} calculation methods",
                    "Update dashboard views for new mode",
                    "Adjust agent priorities for mode-specific tasks"
                ],
                next_actions=[
                    "Review mode-specific features",
                    "Update dashboard configuration",
                    "Configure specialized agents"
                ]
            )
        except ValueError:
            return AppResponse(
                success=False,
                message=f"Invalid app mode: {new_mode}. Valid modes: {[mode.value for mode in AppMode]}"
            )
    
    def _change_thinking_perspective(self, new_perspective: str) -> AppResponse:
        """Change the thinking perspective (how to assess data)."""
        try:
            old_perspective = self.app_context.thinking_perspective
            if new_perspective:
                self.app_context.thinking_perspective = ThinkingPerspective(new_perspective)
            else:
                self.app_context.thinking_perspective = None
            
            self.app_context.timestamp = datetime.now()
            
            # Update mode intersection
            self._update_mode_intersection()
            
            # Auto-save context and modes
            self._save_context_to_file()
            self._save_modes_to_file()
            
            # Notify state change
            await self._notify_state_change()
            
            # Log the perspective change event
            self._log_event("perspective_change", {
                "old_perspective": old_perspective.value if old_perspective else "None",
                "new_perspective": new_perspective if new_perspective else "None",
                "timestamp": self.app_context.timestamp.isoformat()
            })
            
            return AppResponse(
                success=True,
                message=f"Successfully changed thinking perspective from {old_perspective.value if old_perspective else 'None'} to {new_perspective if new_perspective else 'None'}",
                new_context=self.app_context,
                recommendations=[
                    "Apply perspective-specific assessment methods",
                    "Use appropriate analytical frameworks",
                    "Focus on perspective-relevant evidence"
                ],
                next_actions=[
                    "Update assessment methodology",
                    "Configure perspective-specific views",
                    "Adjust agent priorities"
                ]
            )
        except ValueError:
            return AppResponse(
                success=False,
                message=f"Invalid thinking perspective: {new_perspective}. Valid perspectives: {[p.value for p in ThinkingPerspective]}"
            )
    
    def _change_ai_mode(self, new_ai_mode: str) -> AppResponse:
        """Change the AI mode (how to produce final results)."""
        try:
            old_ai_mode = self.app_context.ai_mode
            self.app_context.ai_mode = AIMode(new_ai_mode)
            self.app_context.timestamp = datetime.now()
            
            # Update mode intersection
            self._update_mode_intersection()
            
            # Auto-save context and modes
            self._save_context_to_file()
            self._save_modes_to_file()
            
            # Notify state change
            await self._notify_state_change()
            
            return AppResponse(
                success=True,
                message=f"Successfully changed AI mode from {old_ai_mode.value} to {new_ai_mode}",
                new_context=self.app_context,
                recommendations=[
                    f"Use {new_ai_mode} processing methods",
                    "Adjust computational resources",
                    "Configure appropriate agent capabilities"
                ],
                next_actions=[
                    "Update processing configuration",
                    "Adjust resource allocation",
                    "Configure agent capabilities"
                ]
            )
        except ValueError:
            return AppResponse(
                success=False,
                message=f"Invalid AI mode: {new_ai_mode}. Valid modes: {[mode.value for mode in AIMode]}"
            )
    
    def _change_dashboard_view(self, new_view: str) -> AppResponse:
        """Change the dashboard view."""
        try:
            old_view = self.app_context.dashboard_view
            self.app_context.dashboard_view = DashboardView(new_view)
            self.app_context.timestamp = datetime.now()
            
            # Auto-save context and modes
            self._save_context_to_file()
            self._save_modes_to_file()
            
            # Notify state change
            await self._notify_state_change()
            
            return AppResponse(
                success=True,
                message=f"Successfully changed dashboard view from {old_view.value} to {new_view}",
                new_context=self.app_context,
                recommendations=[
                    f"Focus on {new_view} specific features",
                    "Use view-appropriate tools and agents",
                    "Configure view-specific settings"
                ],
                next_actions=[
                    "Load view-specific data",
                    "Configure view tools",
                    "Update agent priorities"
                ]
            )
        except ValueError:
            return AppResponse(
                success=False,
                message=f"Invalid dashboard view: {new_view}. Valid views: {[view.value for view in DashboardView]}"
            )
    
    def _change_user_role(self, new_role: str) -> AppResponse:
        """Change the user role."""
        try:
            old_role = self.app_context.user_role
            self.app_context.user_role = UserRole(new_role)
            self.app_context.timestamp = datetime.now()
            
            # Auto-save context and modes
            self._save_context_to_file()
            self._save_modes_to_file()
            
            # Notify state change
            await self._notify_state_change()
            
            return AppResponse(
                success=True,
                message=f"Successfully changed user role from {old_role.value} to {new_role}",
                new_context=self.app_context,
                recommendations=[
                    f"Use {new_role} specific tools and views",
                    "Apply role-appropriate access controls",
                    "Configure role-specific features"
                ],
                next_actions=[
                    "Update access permissions",
                    "Configure role-specific views",
                    "Adjust feature availability"
                ]
            )
        except ValueError:
            return AppResponse(
                success=False,
                message=f"Invalid user role: {new_role}. Valid roles: {[role.value for role in UserRole]}"
            )
    
    def _get_app_status(self) -> AppResponse:
        """Get the current app status."""
        return AppResponse(
            success=True,
            message="App status retrieved successfully",
            new_context=self.app_context,
            recommendations=[
                f"Current app mode: {self.app_context.app_mode.value}",
                f"Current thinking perspective: {self.app_context.thinking_perspective.value if self.app_context.thinking_perspective else 'None'}",
                f"Current AI mode: {self.app_context.ai_mode.value}",
                f"Current dashboard view: {self.app_context.dashboard_view.value}",
                f"Current user role: {self.app_context.user_role.value}"
            ],
            next_actions=[
                "Review current configuration",
                "Check mode intersection details",
                "Verify agent priorities"
            ]
        )
    
    def _get_current_mode_intersection_response(self) -> AppResponse:
        """Get the current mode intersection details."""
        intersection = self._get_current_mode_intersection()
        
        if intersection:
            return AppResponse(
                success=True,
                message="Mode intersection retrieved successfully",
                recommendations=[
                    f"Features: {', '.join(intersection.features)}",
                    f"Limitations: {', '.join(intersection.limitations)}",
                    f"Recommended views: {', '.join([v.value for v in intersection.recommended_views])}",
                    f"Agent priorities: {', '.join(intersection.agent_priorities)}",
                    f"Calculation methods: {', '.join(intersection.calculation_methods)}",
                    f"Assessment approaches: {', '.join(intersection.assessment_approaches)}"
                ],
                next_actions=[
                    "Review available features",
                    "Configure recommended views",
                    "Set agent priorities"
                ]
            )
        else:
            return AppResponse(
                success=False,
                message="No mode intersection found for current configuration"
            )
    
    def _get_current_mode_intersection(self) -> Optional[ModeIntersection]:
        """Get the current mode intersection based on app context."""
        # Create the intersection key
        app_mode_short = self.app_context.app_mode.value
        thinking_perspective_short = self.app_context.thinking_perspective.value if self.app_context.thinking_perspective else ""
        ai_mode_short = self.app_context.ai_mode.value
        
        # Build the intersection key
        if thinking_perspective_short:
            intersection_key = f"{app_mode_short}_{thinking_perspective_short}_{ai_mode_short}"
        else:
            intersection_key = f"{app_mode_short}_{ai_mode_short}"
        
        return self.mode_intersections.get(intersection_key)
    
    def _update_mode_intersection(self):
        """Update the current mode intersection based on app context."""
        intersection = self._get_current_mode_intersection()
        if intersection:
            logger.info(f"Updated mode intersection: {intersection.description}")
        else:
            logger.warning("No mode intersection found for current configuration")
    
    def register_ai_agent(self, agent_name: str, agent_instance: Any):
        """Register an AI agent with Frenly and initialize health monitoring."""
        self.ai_agents[agent_name] = agent_instance
        
        # Initialize agent health tracking
        self.agent_health[agent_name] = {
            "is_alive": True,
            "last_seen": datetime.utcnow(),
            "status": AgentStatus.ACTIVE.value,
            "failure_count": 0,
            "last_failure": None,
            "failure_reason": None
        }
        
        logger.info(f"Registered AI agent: {agent_name} with health monitoring")
    
    def check_agent_alive(self, agent_name: str) -> bool:
        """Check if an agent is alive and update health status."""
        if agent_name not in self.ai_agents:
            logger.warning(f"Agent {agent_name} not found")
            return False
        
        try:
            # Simple health check - try to access agent
            agent = self.ai_agents[agent_name]
            if hasattr(agent, 'health_check'):
                # If agent has health_check method, use it
                is_alive = agent.health_check()
            else:
                # Basic check - agent exists and is accessible
                is_alive = agent is not None
            
            # Update health status
            self.agent_health[agent_name]["is_alive"] = is_alive
            self.agent_health[agent_name]["last_seen"] = datetime.utcnow()
            
            if is_alive:
                self.agent_health[agent_name]["status"] = AgentStatus.ACTIVE.value
                self.agent_health[agent_name]["failure_count"] = 0
                self.agent_health[agent_name]["last_failure"] = None
                self.agent_health[agent_name]["failure_reason"] = None
                logger.debug(f"Agent {agent_name} health check passed")
            else:
                self._mark_agent_failed(agent_name, "Health check failed")
            
            return is_alive
            
        except Exception as e:
            error_msg = f"Health check error: {str(e)}"
            logger.error(f"Agent {agent_name} health check failed: {error_msg}")
            self._mark_agent_failed(agent_name, error_msg)
            return False
    
    def _mark_agent_failed(self, agent_name: str, reason: str):
        """Mark an agent as failed with reason and timestamp."""
        if agent_name in self.agent_health:
            self.agent_health[agent_name]["is_alive"] = False
            self.agent_health[agent_name]["status"] = AgentStatus.FAILED.value
            self.agent_health[agent_name]["last_failure"] = datetime.utcnow()
            self.agent_health[agent_name]["failure_reason"] = reason
            self.agent_health[agent_name]["failure_count"] += 1
            
            # Log the agent failure event
            self._log_event("agent_failure", {
                "agent_name": agent_name,
                "reason": reason,
                "failure_count": self.agent_health[agent_name]["failure_count"],
                "timestamp": self.agent_health[agent_name]["last_failure"].isoformat()
            }, severity="WARNING")
            
            logger.warning(f"Agent {agent_name} marked as failed: {reason}")
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific agent."""
        if agent_name not in self.agent_health:
            return {"error": "Agent not found"}
        
        return self.agent_health[agent_name].copy()
    
    def get_all_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents."""
        return self.agent_health.copy()
    
    def start_heartbeat_monitoring(self, interval_seconds: int = 30):
        """Start background heartbeat monitoring of all agents."""
        if self.heartbeat_running:
            logger.warning("Heartbeat monitoring already running")
            return
        
        self.heartbeat_running = True
        
        def heartbeat_loop():
            while self.heartbeat_running:
                try:
                    logger.debug("Running agent heartbeat check...")
                    for agent_name in self.ai_agents.keys():
                        self.check_agent_alive(agent_name)
                    
                    # Log heartbeat results
                    active_count = sum(1 for status in self.agent_health.values() if status["is_alive"])
                    total_count = len(self.agent_health)
                    logger.info(f"Heartbeat complete: {active_count}/{total_count} agents active")
                    
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Heartbeat monitoring error: {str(e)}")
                    time.sleep(interval_seconds)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        logger.info(f"Started heartbeat monitoring with {interval_seconds}s interval")
    
    def stop_heartbeat_monitoring(self):
        """Stop background heartbeat monitoring."""
        self.heartbeat_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        logger.info("Stopped heartbeat monitoring")

    def register_state_change_callback(self, callback: callable):
        """Register a callback function to be called on state changes."""
        self.state_change_callbacks.append(callback)
        logger.info(f"Registered state change callback: {callback.__name__}")

    async def _notify_state_change(self):
        """Notify all registered callbacks about a state change."""
        current_state = {
            "app_context": {
                "app_mode": self.app_context.app_mode.value,
                "thinking_perspective": self.app_context.thinking_perspective.value if self.app_context.thinking_perspective else None,
                "ai_mode": self.app_context.ai_mode.value,
                "dashboard_view": self.app_context.dashboard_view.value,
                "user_role": self.app_context.user_role.value,
                "session_id": self.app_context.session_id,
                "timestamp": self.app_context.timestamp.isoformat()
            },
            "agent_status": self.get_all_agent_status(),
            "recent_events": self.get_recent_events(limit=10),
            "workflow_status": self.get_workflow_status(), # Include workflow status
            "error_log": self.get_error_log(limit=10) # Include error log
        }
        for callback in self.state_change_callbacks:
            try:
                # Callbacks should be awaited if they are async
                if asyncio.iscoroutinefunction(callback):
                    await callback(current_state)
                else:
                    callback(current_state)
            except Exception as e:
                logger.error(f"Error in state change callback {callback.__name__}: {e}")

    def restart_agent(self, agent_name: str, force: bool = False) -> bool:
        """Restart an agent with retry logic and exponential backoff."""
        if agent_name not in self.agent_health:
            logger.error(f"Cannot restart agent {agent_name}: not found")
            return False
        
        # Check retry limit unless forced
        if not force and self.agent_health[agent_name]["failure_count"] >= 3:
            logger.warning(f"Agent {agent_name} has reached retry limit (3). Use force=True to override.")
            return False
        
        try:
            logger.info(f"Attempting to restart agent {agent_name} (attempt {self.agent_health[agent_name]['failure_count'] + 1}/3)")
            
            # Mark as restarting
            self.agent_health[agent_name]["status"] = AgentStatus.RESTARTING.value
            
            # Get the agent instance
            agent = self.ai_agents[agent_name]
            
            # Try to restart if agent has restart method
            if hasattr(agent, 'restart'):
                restart_success = agent.restart()
            else:
                # Basic restart - just mark as active and reset health
                restart_success = True
            
            if restart_success:
                # Reset health status
                self.agent_health[agent_name]["is_alive"] = True
                self.agent_health[agent_name]["status"] = AgentStatus.ACTIVE.value
                self.agent_health[agent_name]["last_seen"] = datetime.utcnow()
                self.agent_health[agent_name]["last_failure"] = None
                self.agent_health[agent_name]["failure_reason"] = None
                
                # Log the successful restart event
                self._log_event("agent_restart_success", {
                    "agent_name": agent_name,
                    "attempt": self.agent_health[agent_name]["failure_count"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"Agent {agent_name} restarted successfully")
                return True
            else:
                self._mark_agent_failed(agent_name, "Restart failed")
                return False
                
        except Exception as e:
            error_msg = f"Restart error: {str(e)}"
            logger.error(f"Failed to restart agent {agent_name}: {error_msg}")
            self._mark_agent_failed(agent_name, error_msg)
            return False
    
    def restart_all_failed_agents(self) -> Dict[str, bool]:
        """Restart all failed agents and return results."""
        results = {}
        failed_agents = [
            name for name, health in self.agent_health.items() 
            if health["status"] == AgentStatus.FAILED.value
        ]
        
        logger.info(f"Attempting to restart {len(failed_agents)} failed agents")
        
        for agent_name in failed_agents:
            results[agent_name] = self.restart_agent(agent_name)
        
        success_count = sum(results.values())
        logger.info(f"Restart complete: {success_count}/{len(failed_agents)} agents restarted successfully")
        
        return results

    def execute_workflow(self, workflow_name: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a defined workflow."""
        if workflow_name not in self.workflows:
            logger.error(f"Workflow '{workflow_name}' not found.")
            return {"success": False, "message": f"Workflow '{workflow_name}' not found."}

        if workflow_id is None:
            workflow_id = f"{workflow_name}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        workflow_definition = self.workflows[workflow_name]
        self.workflow_status[workflow_id] = {
            "name": workflow_name,
            "id": workflow_id,
            "status": "pending",
            "current_step": -1,
            "steps": [{"name": step["name"], "status": "pending", "agent": step["agent"]} for step in workflow_definition["steps"]],
            "start_time": datetime.now(),
            "end_time": None,
            "message": "Workflow initialized."
        }
        logger.info(f"Workflow '{workflow_name}' (ID: {workflow_id}) initialized.")

        # Start workflow execution in a separate thread/task to avoid blocking
        # In a real system, this would be a proper task queue/orchestrator
        asyncio.create_task(self._run_workflow(workflow_id)) # Assuming this is called from an async context
        # If not, use threading.Thread(target=asyncio.run, args=(self._run_workflow(workflow_id),)).start()

        return {"success": True, "message": f"Workflow '{workflow_name}' (ID: {workflow_id}) started.", "workflow_id": workflow_id}

    async def _run_workflow(self, workflow_id: str):
        """Internal method to run workflow steps."""
        workflow_instance = self.workflow_status[workflow_id]
        workflow_instance["status"] = "running"
        logger.info(f"Workflow '{workflow_instance['name']}' (ID: {workflow_id}) is running.")
        await self._notify_state_change() # Notify frontend that workflow started

        for i, step in enumerate(workflow_instance["steps"]):
            workflow_instance["current_step"] = i
            step["status"] = "in-progress"
            workflow_instance["message"] = f"Executing step: {step['name']}"
            logger.info(f"Workflow {workflow_id}: Executing step '{step['name']}' with agent '{step['agent']}'.")
            await self._notify_state_change() # Notify frontend of step change

            try:
                # Simulate agent execution
                # In a real system, this would call the actual agent method
                agent = self.get_ai_agent(step["agent"])
                if agent:
                    logger.info(f"Calling agent {step["agent"]} for step {step["name"]}.")
                    # await agent.execute_step(step["name"], workflow_id) # Example call
                    await asyncio.sleep(2) # Simulate work
                    step["status"] = "completed"
                    logger.info(f"Workflow {workflow_id}: Step '{step["name"]}' completed.")
                else:
                    step["status"] = "failed"
                    workflow_instance["status"] = "failed"
                    workflow_instance["message"] = f"Step '{step["name"]}' failed: Agent '{step["agent"]}' not found or not available."
                    logger.error(workflow_instance["message"])
                    break # Stop workflow on agent failure

            except Exception as e:
                step["status"] = "failed"
                workflow_instance["status"] = "failed"
                workflow_instance["message"] = f"Step '{step["name"]}' failed: {str(e)}"
                logger.error(workflow_instance["message"])
                break # Stop workflow on step failure
            
            await self._notify_state_change() # Notify frontend of step completion/failure

        if workflow_instance["status"] == "running": # If not already failed
            workflow_instance["status"] = "completed"
            workflow_instance["message"] = "Workflow completed successfully."
            logger.info(f"Workflow '{workflow_instance["name"]}' (ID: {workflow_id}) completed successfully.")
        
        workflow_instance["end_time"] = datetime.now()
        await self._notify_state_change() # Final notification

    def get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of a specific workflow or all running workflows."""
        if workflow_id:
            return self.workflow_status.get(workflow_id, {"error": "Workflow not found"})
        return self.workflow_status.copy()

    def get_overall_system_health(self) -> Dict[str, Any>:
        """Get the overall system health status including agent health."""
        # Count agent statuses
        agent_statuses = {}
        active_agents = 0
        failed_agents = 0
        restarting_agents = 0
        
        for agent_name, health in self.agent_health.items():
            status = health["status"]
            agent_statuses[agent_name] = status
            
            if status == AgentStatus.ACTIVE.value:
                active_agents += 1
            elif status == AgentStatus.FAILED.value:
                failed_agents += 1
            elif status == AgentStatus.RESTARTING.value:
                restarting_agents += 1
        
        # Calculate overall health score (0-100)
        total_agents = len(self.agent_health)
        if total_agents > 0:
            health_score = int((active_agents / total_agents) * 100)
        else:
            health_score = 100
        
        # Determine overall status
        if failed_agents == 0:
            overall_status = "healthy"
        elif failed_agents < total_agents / 2:
            overall_status = "degraded"
        else:
            overall_status = "critical"
        
        health_status = {
            "overall_status": overall_status,
            "health_score": health_score,
            "agents": {
                "total": total_agents,
                "active": active_agents,
                "failed": failed_agents,
                "restarting": restarting_agents,
                "statuses": agent_statuses
            },
            "components": {},
            "last_check": datetime.now(),
            "active_sessions": len(self.active_sessions),
            "registered_agents": len(self.ai_agents)
        }
        
        for component, status in self.system_components.items():
            health_status["components"][component.value] = status["status"]
            if status["status"] != "operational":
                health_status["overall_status"] = "degraded"
        
        return health_status

    def get_ai_agent(self, agent_name: str) -> Optional[Any]:
        """Get a registered AI agent."""
        return self.ai_agents.get(agent_name)
    
    def list_ai_agents(self) -> List[str]:
        """List all registered AI agents."""
        return list(self.ai_agents.keys())
    
    def get_session_context(self, session_id: str) -> Optional[AppContext]:
        """Get the context for a specific session."""
        return self.active_sessions.get(session_id)
    
    def create_session(self, session_id: str, context: AppContext):
        """Create a new session with the given context."""
        self.active_sessions[session_id] = context
        logger.info(f"Created session: {session_id}")
    
    def update_session(self, session_id: str, context: AppContext):
        """Update an existing session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id] = context
            logger.info(f"Updated session: {session_id}")
    
    def remove_session(self, session_id: str):
        """Remove a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Removed session: {session_id}")
    
    def get_system_component_status(self, component: SystemComponent) -> Dict[str, Any]:
        """Get the status of a system component."""
        return self.system_components.get(component, {})
    
    def update_system_component_status(self, component: SystemComponent, status: str, metrics: Dict[str, Any] = None):
        """Update the status of a system component."""
        if component in self.system_components:
            self.system_components[component]["status"] = status
            self.system_components[component]["last_check"] = datetime.now()
            if metrics:
                self.system_components[component]["performance_metrics"] = metrics
            logger.info(f"Updated {component.value} status: {status}")

    def check_service_status(self, service_name: str) -> Dict[str, Any]:
        """Check the status of a known service."""
        if service_name not in self.known_services:
            logger.warning(f"Service {service_name} not a known service.")
            return {"status": "unknown", "message": "Service not registered"}

        service_info = self.known_services[service_name]
        url = service_info["url"]
        status = "unknown"
        message = ""

        try:
            # Simple HTTP GET for health check
            # In a real scenario, use a proper HTTP client like requests or httpx
            # and handle various response codes.
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status = "operational"
                message = "Service is reachable and healthy."
            else:
                status = "degraded"
                message = f"Service reachable but returned status code {response.status_code}."
        except requests.exceptions.ConnectionError:
            status = "down"
            message = "Service is unreachable."
        except requests.exceptions.Timeout:
            status = "timeout"
            message = "Service check timed out."
        except Exception as e:
            status = "error"
            message = f"Error checking service: {str(e)}"

        service_info["status"] = status
        service_info["last_check"] = datetime.now()
        service_info["message"] = message

        logger.info(f"Service {service_name} status: {status} - {message}")
        return service_info

    def check_all_services_status(self):
        """Check the status of all known services."""
        logger.info("Checking status of all known services...")
        for service_name in self.known_services.keys():
            self.check_service_status(service_name)
        logger.info("All known services status checked.")

    def get_known_services_status(self) -> Dict[str, Any]:
        """Get the current status of all known services."""
        return self.known_services.copy()

    def save_context_to_file(self):
        """Public method to save context to file."""
        self._save_context_to_file()

    def load_context_from_file(self):
        """Public method to load context from file."""
        self._load_context_from_file()

    def save_modes_to_file(self):
        """Public method to save modes to file."""
        self._save_modes_to_file()

    def load_modes_from_file(self):
        """Public method to load modes from file."""
        self._load_modes_from_file()
    
    def _log_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log an event with timestamp and details."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        # Add to event log (limit to last 1000 events)
        if not hasattr(self, 'event_log'):
            self.event_log = []
        
        self.event_log.append(event)
        
        # Keep only last 1000 events to prevent memory bloat
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]

        # Add to error log if severity is ERROR or CRITICAL
        if severity.upper() in ["ERROR", "CRITICAL"]:
            if not hasattr(self, 'error_log'):
                self.error_log = []
            self.error_log.append(event)
            # Keep only last 500 error events
            if len(self.error_log) > 500:
                self.error_log = self.error_log[-500:]
        
        # Log to standard logger as well
        log_message = f"Event: {event_type} - {details}"
        if severity.upper() == "ERROR":
            logger.error(log_message)
        elif severity.upper() == "WARNING":
            logger.warning(log_message)
        elif severity.upper() == "CRITICAL":
            logger.critical(log_message)
        else:
            logger.info(log_message)
    
    def get_recent_events(self, limit: int = 50, event_type: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get recent events with optional filtering."""
        if not hasattr(self, 'event_log'):
            return []
        
        events = self.event_log.copy()
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        # Filter by severity if specified
        if severity:
            events = [e for e in events if e["severity"] == severity]
        
        # Return most recent events up to limit
        return events[-limit:] if limit > 0 else events
    
    def get_event_summary(self) -> Dict[str, Any>:
        """Get a summary of events by type and severity."""
        if not hasattr(self, 'event_log'):
            return {"total_events": 0, "by_type": {}, "by_severity": {}}
        
        summary = {
            "total_events": len(self.event_log),
            "by_type": {},
            "by_severity": {},
            "recent_activity": len([e for e in self.event_log if e["timestamp"] > (datetime.utcnow() - timedelta(hours=1)).isoformat()])
        }
        
        # Count by event type
        for event in self.event_log:
            event_type = event["event_type"]
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1
        
        # Count by severity
        for event in self.event_log:
            severity = event["severity"]
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        return summary

    def get_error_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent error events from the error log."""
        if not hasattr(self, 'error_log'):
            return []
        return self.error_log[-limit:] if limit > 0 else self.error_log

    # ============================================================================
    # Phase 5: Workflow Integration (Items 21-25)
    # ============================================================================
    
    def _initialize_workflows(self):
        """Initialize basic workflows for Frenly."""
        self.workflows = {
            "reconciliation_check": {
                "name": "Reconciliation Check",
                "description": "Basic reconciliation workflow with 3 steps",
                "steps": [
                    {
                        "name": "initialize_reconciliation",
                        "description": "Initialize reconciliation process",
                        "agent": "reconciliation",
                        "estimated_duration": 5,
                        "dependencies": []
                    },
                    {
                        "name": "process_transactions",
                        "description": "Process and match transactions",
                        "agent": "reconciliation",
                        "estimated_duration": 30,
                        "dependencies": ["initialize_reconciliation"]
                    },
                    {
                        "name": "generate_report",
                        "description": "Generate reconciliation report",
                        "agent": "reconciliation",
                        "estimated_duration": 10,
                        "dependencies": ["process_transactions"]
                    }
                ],
                "estimated_total_duration": 45
            },
            "fraud_detection": {
                "name": "Fraud Detection",
                "description": "Fraud detection workflow",
                "steps": [
                    {
                        "name": "scan_transactions",
                        "description": "Scan for suspicious transactions",
                        "agent": "fraud",
                        "estimated_duration": 15,
                        "dependencies": []
                    },
                    {
                        "name": "analyze_patterns",
                        "description": "Analyze fraud patterns",
                        "agent": "fraud",
                        "estimated_duration": 25,
                        "dependencies": ["scan_transactions"]
                    },
                    {
                        "name": "flag_suspicious",
                        "description": "Flag suspicious activities",
                        "agent": "fraud",
                        "estimated_duration": 10,
                        "dependencies": ["analyze_patterns"]
                    }
                ],
                "estimated_total_duration": 50
            }
        }
        
        # Initialize workflow status tracking
        self.workflow_status = {}
        self.workflow_execution_id = 0
        
        logger.info(f"Initialized {len(self.workflows)} workflows")

    def execute_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Execute a workflow by name."""
        if workflow_name not in self.workflows:
            return {"success": False, "message": f"Workflow '{workflow_name}' not found"}
        
        # Generate unique execution ID
        self.workflow_execution_id += 1
        workflow_id = f"{workflow_name}_{self.workflow_execution_id}"
        
        # Initialize workflow execution
        workflow = self.workflows[workflow_name]
        workflow_instance = {
            "id": workflow_id,
            "name": workflow["name"],
            "description": workflow["description"],
            "status": "pending",
            "start_time": datetime.now(),
            "estimated_completion": datetime.now() + timedelta(seconds=workflow["estimated_total_duration"]),
            "current_step": 0,
            "steps": workflow["steps"].copy(),
            "progress": 0,
            "message": "Workflow initialized"
        }
        
        # Initialize step statuses
        for step in workflow_instance["steps"]:
            step["status"] = "pending"
            step["start_time"] = None
            step["end_time"] = None
            step["error"] = None
        
        # Store workflow instance
        self.workflow_status[workflow_id] = workflow_instance
        
        # Start workflow execution in background
        asyncio.create_task(self._run_workflow(workflow_id))
        
        # Log workflow start
        self._log_event("workflow_started", {
            "workflow_name": workflow_name,
            "workflow_id": workflow_id,
            "estimated_duration": workflow["estimated_total_duration"]
        })
        
        return {"success": True, "message": f"Workflow '{workflow_name}' (ID: {workflow_id}) started.", "workflow_id": workflow_id}

    async def _run_workflow(self, workflow_id: str):
        """Internal method to run workflow steps."""
        workflow_instance = self.workflow_status[workflow_id]
        workflow_instance["status"] = "running"
        logger.info(f"Workflow '{workflow_instance['name']}' (ID: {workflow_id}) is running.")
        await self._notify_state_change() # Notify frontend that workflow started

        for i, step in enumerate(workflow_instance["steps"]):
            workflow_instance["current_step"] = i
            step["status"] = "in-progress"
            workflow_instance["message"] = f"Executing step: {step['name']}"
            logger.info(f"Workflow {workflow_id}: Executing step '{step['name']}' with agent '{step['agent']}'.")
            await self._notify_state_change() # Notify frontend of step change

            try:
                # Simulate agent execution
                # In a real system, this would call the actual agent method
                agent = self.get_ai_agent(step["agent"])
                if agent:
                    logger.info(f"Calling agent {step['agent']} for step {step['name']}.")
                    # await agent.execute_step(step['name'], workflow_id) # Example call
                    await asyncio.sleep(2) # Simulate work
                    step["status"] = "completed"
                    logger.info(f"Workflow {workflow_id}: Step '{step['name']}' completed.")
                else:
                    step["status"] = "failed"
                    workflow_instance["status"] = "failed"
                    workflow_instance["message"] = f"Step '{step['name']}' failed: Agent '{step['agent']}' not found or not available."
                    logger.error(workflow_instance["message"])
                    break # Stop workflow on agent failure

            except Exception as e:
                step["status"] = "failed"
                workflow_instance["status"] = "failed"
                workflow_instance["message"] = f"Step '{step['name']}' failed: {str(e)}"
                logger.error(workflow_instance["message"])
                break # Stop workflow on step failure
            
            await self._notify_state_change() # Notify frontend of step completion/failure

        if workflow_instance["status"] == "running": # If not already failed
            workflow_instance["status"] = "completed"
            workflow_instance["message"] = "Workflow completed successfully."
            logger.info(f"Workflow '{workflow_instance['name']}' (ID: {workflow_id}) completed successfully.")
        
        workflow_instance["end_time"] = datetime.now()
        await self._notify_state_change() # Final notification

    def get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of a specific workflow or all running workflows."""
        if workflow_id:
            return self.workflow_status.get(workflow_id, {"error": "Workflow not found"})
        return self.workflow_status.copy()

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows."""
        return [
            {
                "name": name,
                "description": workflow["description"],
                "steps_count": len(workflow["steps"]),
                "estimated_duration": workflow["estimated_total_duration"]
            }
            for name, workflow in self.workflows.items()
        ]

    async def _notify_state_change(self):
        """Notify frontend of state change (placeholder for WebSocket)."""
        # This would send WebSocket messages in a real implementation
        pass

    # ============================================================================
    # Phase 7: Performance & Monitoring (Items 26-30)
    # ============================================================================
    
    def _initialize_metrics(self):
        """Initialize performance metrics tracking."""
        self.metrics = {
            "commands_executed": 0,
            "commands_successful": 0,
            "commands_failed": 0,
            "response_times": [],
            "last_100_commands": [],
            "start_time": datetime.now(),
            "memory_usage": [],
            "cpu_usage": []
        }
        
        logger.info("Performance metrics tracking initialized")

    def _record_command_execution(self, command_type: str, success: bool, response_time: float):
        """Record command execution metrics."""
        if not hasattr(self, 'metrics'):
            self._initialize_metrics()
        
        # Increment counters
        self.metrics["commands_executed"] += 1
        if success:
            self.metrics["commands_successful"] += 1
        else:
            self.metrics["commands_failed"] += 1
        
        # Record response time
        self.metrics["response_times"].append(response_time)
        
        # Keep only last 100 response times
        if len(self.metrics["response_times"]) > 100:
            self.metrics["response_times"] = self.metrics["response_times"][-100:]
        
        # Record command details
        command_record = {
            "timestamp": datetime.now(),
            "type": command_type,
            "success": success,
            "response_time": response_time
        }
        
        self.metrics["last_100_commands"].append(command_record)
        
        # Keep only last 100 commands
        if len(self.metrics["last_100_commands"]) > 100:
            self.metrics["last_100_commands"] = self.metrics["last_100_commands"][-100:]
        
        # Log metrics periodically
        if self.metrics["commands_executed"] % 10 == 0:
            logger.info(f"Metrics: {self.metrics['commands_executed']} commands, "
                       f"{self.metrics['commands_successful']} successful, "
                       f"{self.metrics['commands_failed']} failed")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not hasattr(self, 'metrics'):
            self._initialize_metrics()
        
        # Calculate response time statistics
        response_times = self.metrics["response_times"]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            sorted_times = sorted(response_times)
            p50 = sorted_times[len(sorted_times) // 2]
            p90 = sorted_times[int(len(sorted_times) * 0.9)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
        else:
            avg_response_time = p50 = p90 = p95 = 0
        
        # Calculate success rate
        total_commands = self.metrics["commands_executed"]
        success_rate = (self.metrics["commands_successful"] / total_commands * 100) if total_commands > 0 else 0
        
        # Calculate uptime
        uptime = datetime.now() - self.metrics["start_time"]
        
        metrics = {
            "overview": {
                "total_commands": total_commands,
                "successful_commands": self.metrics["commands_successful"],
                "failed_commands": self.metrics["commands_failed"],
                "success_rate": round(success_rate, 2),
                "uptime_seconds": int(uptime.total_seconds())
            },
            "response_times": {
                "average": round(avg_response_time, 3),
                "p50": round(p50, 3),
                "p90": round(p90, 3),
                "p95": round(p95, 3),
                "min": round(min(response_times), 3) if response_times else 0,
                "max": round(max(response_times), 3) if response_times else 0
            },
            "recent_activity": {
                "last_10_commands": [
                    {
                        "timestamp": cmd["timestamp"].isoformat(),
                        "type": cmd["type"],
                        "success": cmd["success"],
                        "response_time": round(cmd["response_time"], 3)
                    }
                    for cmd in self.metrics["last_100_commands"][-10:]
                ]
            },
            "system_health": {
                "overall_score": self.get_overall_system_health()["health_score"],
                "active_agents": len([h for h in self.agent_health.values() if h["status"] == AgentStatus.ACTIVE.value]),
                "total_agents": len(self.agent_health)
            }
        }
        
        return metrics

    def _update_metrics_on_command(self, command_type: str, success: bool, start_time: datetime):
        """Update metrics when a command is executed."""
        response_time = (datetime.now() - start_time).total_seconds()
        self._record_command_execution(command_type, success, response_time)


# Example usage
if __name__ == "__main__":
    # Initialize Frenly
    frenly = FrenlyMetaAgent()
    
    # Test mode switching
    response = frenly.manage_app(AppCommand(
        command_type="switch_app_mode",
        target_mode="construction"
    ))
    print(f"Mode switch response: {response.message}")
    
    # Test AI mode change
    response = frenly.manage_app(AppCommand(
        command_type="change_ai_mode",
        target_ai_mode="extreme"
    ))
    print(f"AI mode change response: {response.message}")
    
    # Test thinking perspective change
    response = frenly.manage_app(AppCommand(
        command_type="change_thinking_perspective",
        target_perspective="investigation"
    ))
    print(f"Thinking perspective change response: {response.message}")
    
    # Get current status
    response = frenly.manage_app(AppCommand(command_type="get_status"))
    print(f"Status response: {response.message}")
    
    # Get mode intersection
    response = frenly.manage_app(AppCommand(command_type="get_mode_intersection"))
    print(f"Mode intersection response: {response.message}")
      