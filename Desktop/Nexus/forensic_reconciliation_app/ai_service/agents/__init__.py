"""
AI Service Agents Package

This package contains specialized AI agents for various tasks including:
- Reconciliation and matching
- Fraud detection and analysis
- Risk assessment and scoring
- Evidence processing and analysis
- Litigation support
- Help and guidance
"""

from .automated_escalation import AutomatedEscalationSystem
from .compliance_rule_engine import ComplianceRuleEngine
from .entity_network_analyzer import EntityNetworkAnalyzer
from .exif_extractor import EXIFExtractor
from .explainable_ai_scorer import ExplainableAIScorer
from .hash_verifier import HashVerifier
from .help_agent import HelpAgent
from .litigation_agent import LitigationAgent
from .multi_factor_risk_assessor import MultiFactorRiskAssessor
from .nlp_processor import NLPProcessor
from .ocr_processor import OCRProcessor
from .pattern_detector import PatternDetector

# Core AI agents
from .reconciliation_agent import ReconciliationAgent
from .risk_scorer import RiskScorer
from .risk_trend_analyzer import RiskTrendAnalyzer

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation Platform Team"

__all__ = [
    # Core agents
    "ReconciliationAgent",
    "EntityNetworkAnalyzer",
    "PatternDetector",
    "RiskScorer",
    "MultiFactorRiskAssessor",
    "ComplianceRuleEngine",
    "ExplainableAIScorer",
    "AutomatedEscalationSystem",
    "RiskTrendAnalyzer",
    "HashVerifier",
    "EXIFExtractor",
    "OCRProcessor",
    "NLPProcessor",
    "LitigationAgent",
    "HelpAgent",
]
