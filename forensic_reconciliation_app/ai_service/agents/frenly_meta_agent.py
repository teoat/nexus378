"""
Frenly Meta Agent - Central App Manager & Orchestrator

Frenly is the intelligent conductor that manages the entire forensic reconciliation app.
She orchestrates specialized AI agents, manages app modes, and provides contextual guidance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        
        # Initialize mode intersections
        self._initialize_mode_intersections()
        
        # Initialize system components
        self._initialize_system_components()
        
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
                return self._change_user_role(command.target_role)
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
        """Register an AI agent with Frenly."""
        self.ai_agents[agent_name] = agent_instance
        logger.info(f"Registered AI agent: {agent_name}")
    
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
    
    def get_overall_system_health(self) -> Dict[str, Any]:
        """Get the overall system health status."""
        health_status = {
            "overall_status": "healthy",
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
      