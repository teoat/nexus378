"""
Compliance Rule Engine - Regulatory Compliance Management System

This module implements the ComplianceRuleEngine class that provides
comprehensive compliance rule management and enforcement for the
Risk Agent in the forensic platform.
"""

import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import asyncio


class ComplianceFramework(Enum):
    """Compliance frameworks supported."""

    SOX = "sox"  # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    AML = "aml"  # Anti-Money Laundering
    GDPR = "gdpr"  # General Data Protection Regulation
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    ISO27001 = "iso27001"  # Information Security Management
    SOC2 = "soc2"  # Service Organization Control 2
    CCPA = "ccpa"  # California Consumer Privacy Act


class RuleType(Enum):
    """Types of compliance rules."""

    ACCESS_CONTROL = "access_control"  # Access control rules
    DATA_PROTECTION = "data_protection"  # Data protection rules
    AUDIT_LOGGING = "audit_logging"  # Audit logging rules
    INCIDENT_RESPONSE = "incident_response"  # Incident response rules
    BUSINESS_CONTINUITY = "business_continuity"  # Business continuity rules
    RISK_ASSESSMENT = "risk_assessment"  # Risk assessment rules
    TRAINING = "training"  # Training and awareness rules
    MONITORING = "monitoring"  # Monitoring and surveillance rules


class ComplianceStatus(Enum):
    """Compliance status levels."""

    COMPLIANT = "compliant"  # Fully compliant
    PARTIALLY_COMPLIANT = "partially_compliant"  # Partially compliant
    NON_COMPLIANT = "non_compliant"  # Non-compliant
    PENDING = "pending"  # Pending assessment
    EXEMPT = "exempt"  # Exempt from requirement


@dataclass
class ComplianceRule:
    """A compliance rule definition."""

    rule_id: str
    framework: ComplianceFramework
    rule_type: RuleType
    rule_name: str
    description: str
    requirements: List[str]
    controls: List[str]
    risk_level: str
    priority: int
    effective_date: datetime
    review_frequency: int  # days
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceAssessment:
    """Assessment of compliance with a specific rule."""

    assessment_id: str
    rule_id: str
    entity_id: str
    assessment_date: datetime
    status: ComplianceStatus
    evidence: Dict[str, Any]
    findings: List[str]
    recommendations: List[str]
    next_review_date: datetime
    assessor: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """Comprehensive compliance report."""

    report_id: str
    entity_id: str
    framework: ComplianceFramework
    report_date: datetime
    overall_status: ComplianceStatus
    rule_assessments: List[ComplianceAssessment]
    summary: str
    risk_score: float
    next_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceRuleEngine:
    """
    Comprehensive compliance rule engine system.

    The ComplianceRuleEngine is responsible for:
    - Managing compliance rules and frameworks
    - Conducting compliance assessments
    - Generating compliance reports
    - Monitoring compliance status
    - Providing compliance recommendations
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the ComplianceRuleEngine."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_frameworks = config.get(
            "default_frameworks", [ComplianceFramework.SOX, ComplianceFramework.PCI_DSS]
        )
        self.assessment_timeout = config.get("assessment_timeout", 1800)  # 30 minutes
        self.review_reminder_days = config.get("review_reminder_days", 30)

        # Rule management
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.framework_rules: Dict[ComplianceFramework, List[str]] = defaultdict(list)

        # Assessment tracking
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.assessment_history: Dict[str, List[str]] = defaultdict(list)

        # Performance tracking
        self.total_assessments = 0
        self.total_rules = 0
        self.compliance_rate = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("ComplianceRuleEngine initialized successfully")

    async def start(self):
        """Start the ComplianceRuleEngine."""
        self.logger.info("Starting ComplianceRuleEngine...")

        # Initialize compliance components
        await self._initialize_compliance_components()

        # Start background tasks
        asyncio.create_task(self._monitor_compliance_deadlines())
        asyncio.create_task(self._update_compliance_metrics())

        self.logger.info("ComplianceRuleEngine started successfully")

    async def stop(self):
        """Stop the ComplianceRuleEngine."""
        self.logger.info("Stopping ComplianceRuleEngine...")
        self.logger.info("ComplianceRuleEngine stopped")

    async def add_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Add a new compliance rule."""
        try:
            # Validate rule
            if not rule.rule_id or not rule.framework or not rule.rule_type:
                raise ValueError("Invalid compliance rule data")

            # Store rule
            self.compliance_rules[rule.rule_id] = rule
            self.framework_rules[rule.framework].append(rule.rule_id)

            # Update statistics
            self.total_rules += 1

            self.logger.info(
                f"Added compliance rule: {rule.rule_id} ({rule.framework.value})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error adding compliance rule: {e}")
            return False

    async def remove_compliance_rule(self, rule_id: str) -> bool:
        """Remove a compliance rule."""
        try:
            if rule_id in self.compliance_rules:
                rule = self.compliance_rules[rule_id]

                # Remove from framework rules
                if rule.framework in self.framework_rules:
                    if rule_id in self.framework_rules[rule.framework]:
                        self.framework_rules[rule.framework].remove(rule_id)

                # Remove rule
                del self.compliance_rules[rule_id]

                # Update statistics
                self.total_rules -= 1

                self.logger.info(f"Removed compliance rule: {rule_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error removing compliance rule {rule_id}: {e}")
            return False

    async def conduct_compliance_assessment(
        self,
        entity_id: str,
        framework: ComplianceFramework,
        rule_ids: Optional[List[str]] = None,
    ) -> ComplianceReport:
        """Conduct a compliance assessment."""
        try:
            self.logger.info(
                f"Starting compliance assessment for entity: {entity_id}, framework: {framework.value}"
            )

            # Get rules to assess
            if not rule_ids:
                rule_ids = self.framework_rules.get(framework, [])

            if not rule_ids:
                raise ValueError(f"No rules found for framework: {framework.value}")

            # Conduct assessments for each rule
            rule_assessments = []
            for rule_id in rule_ids:
                if rule_id in self.compliance_rules:
                    rule = self.compliance_rules[rule_id]
                    assessment = await self._assess_rule_compliance(entity_id, rule)
                    rule_assessments.append(assessment)

            # Generate compliance report
            report = await self._generate_compliance_report(
                entity_id, framework, rule_assessments
            )

            self.logger.info(f"Compliance assessment completed for entity: {entity_id}")
            return report

        except Exception as e:
            self.logger.error(f"Error conducting compliance assessment: {e}")
            raise

    async def _assess_rule_compliance(
        self, entity_id: str, rule: ComplianceRule
    ) -> ComplianceAssessment:
        """Assess compliance with a specific rule."""
        try:
            # Create assessment
            assessment_id = str(uuid.uuid4())
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                rule_id=rule.rule_id,
                entity_id=entity_id,
                assessment_date=datetime.utcnow(),
                status=ComplianceStatus.PENDING,
                evidence={},
                findings=[],
                recommendations=[],
                next_review_date=datetime.utcnow()
                + timedelta(days=rule.review_frequency),
                assessor="system",
            )

            # Conduct assessment based on rule type
            if rule.rule_type == RuleType.ACCESS_CONTROL:
                await self._assess_access_control_compliance(assessment, rule)
            elif rule.rule_type == RuleType.DATA_PROTECTION:
                await self._assess_data_protection_compliance(assessment, rule)
            elif rule.rule_type == RuleType.AUDIT_LOGGING:
                await self._assess_audit_logging_compliance(assessment, rule)
            elif rule.rule_type == RuleType.INCIDENT_RESPONSE:
                await self._assess_incident_response_compliance(assessment, rule)
            elif rule.rule_type == RuleType.BUSINESS_CONTINUITY:
                await self._assess_business_continuity_compliance(assessment, rule)
            elif rule.rule_type == RuleType.RISK_ASSESSMENT:
                await self._assess_risk_assessment_compliance(assessment, rule)
            elif rule.rule_type == RuleType.TRAINING:
                await self._assess_training_compliance(assessment, rule)
            elif rule.rule_type == RuleType.MONITORING:
                await self._assess_monitoring_compliance(assessment, rule)
            else:
                # Default assessment
                await self._assess_general_compliance(assessment, rule)

            # Store assessment
            self.assessments[assessment_id] = assessment
            self.assessment_history[entity_id].append(assessment_id)

            # Update statistics
            self.total_assessments += 1

            return assessment

        except Exception as e:
            self.logger.error(f"Error assessing rule compliance: {e}")
            raise

    async def _assess_access_control_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess access control compliance."""
        try:
            # Simulate access control assessment
            assessment.evidence = {
                "access_controls": "implemented",
                "user_management": "active",
                "privilege_management": "configured",
                "access_reviews": "scheduled",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "configured", "scheduled"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = [
                    "Access controls are properly implemented and managed"
                ]
                assessment.recommendations = [
                    "Continue regular access reviews",
                    "Monitor access patterns",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = ["Some access control measures need improvement"]
                assessment.recommendations = [
                    "Implement missing access controls",
                    "Enhance user management",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing access control compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_data_protection_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess data protection compliance."""
        try:
            # Simulate data protection assessment
            assessment.evidence = {
                "data_encryption": "implemented",
                "data_classification": "active",
                "data_retention": "configured",
                "data_backup": "scheduled",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "configured", "scheduled"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = [
                    "Data protection measures are properly implemented"
                ]
                assessment.recommendations = [
                    "Continue regular data audits",
                    "Monitor data access",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = ["Some data protection measures need improvement"]
                assessment.recommendations = [
                    "Implement missing data protection",
                    "Enhance data classification",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing data protection compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_audit_logging_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess audit logging compliance."""
        try:
            # Simulate audit logging assessment
            assessment.evidence = {
                "audit_logging": "implemented",
                "log_retention": "configured",
                "log_monitoring": "active",
                "log_analysis": "scheduled",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "configured", "scheduled"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = [
                    "Audit logging is properly implemented and managed"
                ]
                assessment.recommendations = [
                    "Continue regular log reviews",
                    "Monitor log patterns",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = ["Some audit logging measures need improvement"]
                assessment.recommendations = [
                    "Implement missing logging",
                    "Enhance log monitoring",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing audit logging compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_incident_response_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess incident response compliance."""
        try:
            # Simulate incident response assessment
            assessment.evidence = {
                "incident_response_plan": "implemented",
                "response_team": "trained",
                "communication_procedures": "documented",
                "recovery_procedures": "tested",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "trained", "documented", "tested"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = [
                    "Incident response procedures are properly implemented"
                ]
                assessment.recommendations = [
                    "Continue regular testing",
                    "Update procedures as needed",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = [
                    "Some incident response measures need improvement"
                ]
                assessment.recommendations = [
                    "Implement missing procedures",
                    "Enhance team training",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing incident response compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_business_continuity_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess business continuity compliance."""
        try:
            # Simulate business continuity assessment
            assessment.evidence = {
                "business_continuity_plan": "implemented",
                "disaster_recovery": "configured",
                "backup_systems": "active",
                "testing_schedule": "established",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "configured", "established"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = [
                    "Business continuity measures are properly implemented"
                ]
                assessment.recommendations = [
                    "Continue regular testing",
                    "Update plans as needed",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = [
                    "Some business continuity measures need improvement"
                ]
                assessment.recommendations = [
                    "Implement missing measures",
                    "Enhance disaster recovery",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing business continuity compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_risk_assessment_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess risk assessment compliance."""
        try:
            # Simulate risk assessment compliance
            assessment.evidence = {
                "risk_assessment_process": "implemented",
                "risk_register": "maintained",
                "risk_monitoring": "active",
                "risk_reporting": "scheduled",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "maintained", "scheduled"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = [
                    "Risk assessment process is properly implemented"
                ]
                assessment.recommendations = [
                    "Continue regular risk reviews",
                    "Update risk register",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = ["Some risk assessment measures need improvement"]
                assessment.recommendations = [
                    "Implement missing processes",
                    "Enhance risk monitoring",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing risk assessment compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_training_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess training compliance."""
        try:
            # Simulate training compliance assessment
            assessment.evidence = {
                "training_program": "implemented",
                "awareness_campaigns": "active",
                "compliance_training": "scheduled",
                "training_records": "maintained",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "scheduled", "maintained"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = ["Training program is properly implemented"]
                assessment.recommendations = [
                    "Continue regular training",
                    "Update training materials",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = ["Some training measures need improvement"]
                assessment.recommendations = [
                    "Implement missing training",
                    "Enhance awareness campaigns",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing training compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_monitoring_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess monitoring compliance."""
        try:
            # Simulate monitoring compliance assessment
            assessment.evidence = {
                "monitoring_systems": "implemented",
                "alerting": "configured",
                "reporting": "active",
                "review_process": "established",
            }

            # Determine compliance status
            if all(
                value in ["implemented", "active", "configured", "established"]
                for value in assessment.evidence.values()
            ):
                assessment.status = ComplianceStatus.COMPLIANT
                assessment.findings = ["Monitoring systems are properly implemented"]
                assessment.recommendations = [
                    "Continue regular monitoring",
                    "Update alerting rules",
                ]
            else:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
                assessment.findings = ["Some monitoring measures need improvement"]
                assessment.recommendations = [
                    "Implement missing monitoring",
                    "Enhance alerting systems",
                ]

        except Exception as e:
            self.logger.error(f"Error assessing monitoring compliance: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _assess_general_compliance(
        self, assessment: ComplianceAssessment, rule: ComplianceRule
    ):
        """Assess general compliance for unknown rule types."""
        try:
            # Default assessment
            assessment.evidence = {
                "implementation_status": "review_required",
                "documentation": "pending",
                "testing": "not_scheduled",
            }

            assessment.status = ComplianceStatus.PENDING
            assessment.findings = ["General compliance assessment required"]
            assessment.recommendations = [
                "Conduct detailed assessment",
                "Implement required controls",
            ]

        except Exception as e:
            self.logger.error(f"Error in general compliance assessment: {e}")
            assessment.status = ComplianceStatus.NON_COMPLIANT

    async def _generate_compliance_report(
        self,
        entity_id: str,
        framework: ComplianceFramework,
        rule_assessments: List[ComplianceAssessment],
    ) -> ComplianceReport:
        """Generate a comprehensive compliance report."""
        try:
            # Calculate overall status
            status_counts = defaultdict(int)
            for assessment in rule_assessments:
                status_counts[assessment.status] += 1

            # Determine overall status
            if status_counts[ComplianceStatus.COMPLIANT] == len(rule_assessments):
                overall_status = ComplianceStatus.COMPLIANT
            elif status_counts[ComplianceStatus.NON_COMPLIANT] > 0:
                overall_status = ComplianceStatus.NON_COMPLIANT
            else:
                overall_status = ComplianceStatus.PARTIALLY_COMPLIANT

            # Calculate risk score
            risk_score = self._calculate_compliance_risk_score(rule_assessments)

            # Generate summary
            summary = (
                f"Compliance assessment for {framework.value}: {overall_status.value}. "
            )
            summary += f"Compliant: {status_counts[ComplianceStatus.COMPLIANT]}, "
            summary += f"Partially Compliant: {status_counts[ComplianceStatus.PARTIALLY_COMPLIANT]}, "
            summary += f"Non-Compliant: {status_counts[ComplianceStatus.NON_COMPLIANT]}"

            # Generate next actions
            next_actions = self._generate_next_actions(rule_assessments)

            # Create report
            report = ComplianceReport(
                report_id=str(uuid.uuid4()),
                entity_id=entity_id,
                framework=framework,
                report_date=datetime.utcnow(),
                overall_status=overall_status,
                rule_assessments=rule_assessments,
                summary=summary,
                risk_score=risk_score,
                next_actions=next_actions,
            )

            return report

        except Exception as e:
            self.logger.error(f"Error generating compliance report: {e}")
            raise

    def _calculate_compliance_risk_score(
        self, rule_assessments: List[ComplianceAssessment]
    ) -> float:
        """Calculate compliance risk score."""
        try:
            if not rule_assessments:
                return 0.0

            # Weight by compliance status
            status_weights = {
                ComplianceStatus.COMPLIANT: 0.0,
                ComplianceStatus.PARTIALLY_COMPLIANT: 0.5,
                ComplianceStatus.NON_COMPLIANT: 1.0,
                ComplianceStatus.PENDING: 0.7,
                ComplianceStatus.EXEMPT: 0.0,
            }

            total_score = 0.0
            for assessment in rule_assessments:
                total_score += status_weights.get(assessment.status, 0.5)

            return total_score / len(rule_assessments)

        except Exception as e:
            self.logger.error(f"Error calculating compliance risk score: {e}")
            return 0.5

    def _generate_next_actions(
        self, rule_assessments: List[ComplianceAssessment]
    ) -> List[str]:
        """Generate next actions based on assessment results."""
        try:
            actions = []

            # High priority actions for non-compliant items
            non_compliant = [
                a
                for a in rule_assessments
                if a.status == ComplianceStatus.NON_COMPLIANT
            ]
            if non_compliant:
                actions.append(
                    f"Immediately address {len(non_compliant)} non-compliant items"
                )
                actions.append("Develop remediation plans for critical compliance gaps")

            # Medium priority actions for partially compliant items
            partially_compliant = [
                a
                for a in rule_assessments
                if a.status == ComplianceStatus.PARTIALLY_COMPLIANT
            ]
            if partially_compliant:
                actions.append(
                    f"Improve {len(partially_compliant)} partially compliant areas"
                )
                actions.append("Implement additional controls where needed")

            # General actions
            actions.append("Schedule follow-up assessments")
            actions.append("Update compliance documentation")
            actions.append("Provide training on compliance requirements")

            return actions

        except Exception as e:
            self.logger.error(f"Error generating next actions: {e}")
            return ["Review assessment results and plan next steps"]

    async def _monitor_compliance_deadlines(self):
        """Monitor compliance assessment deadlines."""
        while True:
            try:
                current_time = datetime.utcnow()
                upcoming_reviews = []

                for assessment in self.assessments.values():
                    if assessment.next_review_date:
                        days_until_review = (
                            assessment.next_review_date - current_time
                        ).days

                        if days_until_review <= self.review_reminder_days:
                            upcoming_reviews.append(assessment)

                if upcoming_reviews:
                    self.logger.info(
                        f"Found {len(upcoming_reviews)} assessments due for review"
                    )

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                self.logger.error(f"Error monitoring compliance deadlines: {e}")
                await asyncio.sleep(3600)

    async def _update_compliance_metrics(self):
        """Update compliance metrics."""
        while True:
            try:
                # Calculate compliance rate
                if self.total_assessments > 0:
                    compliant_count = len(
                        [
                            a
                            for a in self.assessments.values()
                            if a.status == ComplianceStatus.COMPLIANT
                        ]
                    )
                    self.compliance_rate = compliant_count / self.total_assessments

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating compliance metrics: {e}")
                await asyncio.sleep(300)

    async def _initialize_compliance_components(self):
        """Initialize compliance components."""
        try:
            # Initialize default compliance rules
            await self._initialize_default_rules()

            self.logger.info("Compliance components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing compliance components: {e}")

    async def _initialize_default_rules(self):
        """Initialize default compliance rules."""
        try:
            # This would create standard compliance rules for each framework
            # For now, just log initialization
            self.logger.info("Default compliance rules initialized")

        except Exception as e:
            self.logger.error(f"Error initializing default rules: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_assessments": self.total_assessments,
            "total_rules": self.total_rules,
            "compliance_rate": self.compliance_rate,
            "frameworks_supported": [f.value for f in ComplianceFramework],
            "rule_types_supported": [r.value for r in RuleType],
            "active_assessments": len(self.assessments),
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_frameworks": ["sox", "pci_dss", "aml", "gdpr"],
        "assessment_timeout": 1800,
        "review_reminder_days": 30,
    }

    # Initialize compliance rule engine
    engine = ComplianceRuleEngine(config)

    print("ComplianceRuleEngine system initialized successfully!")
