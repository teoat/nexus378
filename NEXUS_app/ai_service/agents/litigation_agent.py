#!/usr/bin/env python3
"""
Litigation Agent Core System - Case Management and Legal Support

This module implements the LitigationAgent class that provides
comprehensive litigation support capabilities for the forensic platform.
"""

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType

class CaseStatus(Enum):
    """Status of litigation cases."""

    OPEN = "open"  # Case is open and active
    INVESTIGATION = "investigation"  # Under investigation
    EVIDENCE_COLLECTION = "evidence_collection"  # Collecting evidence
    ANALYSIS = "analysis"  # Analyzing evidence
    PREPARATION = "preparation"  # Preparing for trial
    TRIAL = "trial"  # In trial
    SETTLEMENT = "settlement"  # Settlement negotiations
    CLOSED = "closed"  # Case closed
    APPEAL = "appeal"  # Under appeal
    ARCHIVED = "archived"  # Case archived

class CaseType(Enum):
    """Types of litigation cases."""

    CIVIL = "civil"  # Civil litigation
    CRIMINAL = "criminal"  # Criminal prosecution
    ADMINISTRATIVE = "administrative"  # Administrative proceedings
    INTELLECTUAL_PROPERTY = "intellectual_property"  # IP disputes
    CONTRACT = "contract"  # Contract disputes
    EMPLOYMENT = "employment"  # Employment disputes
    ENVIRONMENTAL = "environmental"  # Environmental cases
    SECURITIES = "securities"  # Securities fraud
    ANTITRUST = "antitrust"  # Antitrust cases
    CUSTOM = "custom"  # Custom case type

class EvidenceType(Enum):
    """Types of evidence."""

    DOCUMENT = "document"  # Written documents
    ELECTRONIC = "electronic"  # Digital evidence
    PHYSICAL = "physical"  # Physical evidence
    TESTIMONY = "testimony"  # Witness testimony
    EXPERT = "expert"  # Expert opinion
    PHOTOGRAPHIC = "photographic"  # Photographs/videos
    AUDIO = "audio"  # Audio recordings
    FINANCIAL = "financial"  # Financial records
    COMMUNICATION = "communication"  # Communications
    FORENSIC = "forensic"  # Forensic analysis

@dataclass
class LitigationCase:
    """A litigation case."""

    case_id: str
    case_number: str
    case_title: str
    case_type: CaseType
    status: CaseStatus
    parties: List[str]
    attorneys: List[str]
    filing_date: datetime
    description: str
    jurisdiction: str
    court: str
    judge: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvidenceItem:
    """An evidence item in a case."""

    evidence_id: str
    case_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    source: str
    collection_date: datetime
    chain_of_custody: List[str]
    hash_value: str
    file_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimelineEvent:
    """A timeline event in a case."""

    event_id: str
    case_id: str
    event_type: str
    title: str
    description: str
    date: datetime
    participants: List[str]
    location: str
    outcome: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PrecedentCase:
    """A precedent case for reference."""

    precedent_id: str
    case_name: str
    citation: str
    court: str
    date: datetime
    summary: str
    key_holdings: List[str]
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalReport:
    """A legal report generated for a case."""

    report_id: str
    case_id: str
    report_type: str
    title: str
    content: str
    author: str
    creation_date: datetime
    last_modified: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LitigationMetrics:
    """Metrics for litigation performance."""

    total_cases: int
    active_cases: int
    closed_cases: int
    average_case_duration: float
    evidence_items_processed: int
    reports_generated: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class LitigationAgent:
    """
    Comprehensive litigation support system.

    The LitigationAgent is responsible for:
    - Managing litigation cases and workflows
    - Constructing and analyzing timelines
    - Linking and managing evidence
    - Mapping and analyzing precedents
    - Generating legal reports
    - Supporting legal research and analysis
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the LitigationAgent."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_cases_per_agent = config.get("max_cases_per_agent", 10)
        self.evidence_storage_path = config.get("evidence_storage_path", "./evidence")
        self.report_template_path = config.get("report_template_path", "./templates")

        # Case management
        self.cases: Dict[str, LitigationCase] = {}
        self.case_assignments: Dict[str, List[str]] = defaultdict(list)
        self.case_status_history: Dict[str, List[CaseStatus]] = defaultdict(list)

        # Evidence management
        self.evidence_items: Dict[str, EvidenceItem] = {}
        self.evidence_index: Dict[str, List[str]] = defaultdict(list)
        self.evidence_relationships: nx.Graph = nx.Graph()

        # Timeline management
        self.timeline_events: Dict[str, TimelineEvent] = {}
        self.case_timelines: Dict[str, List[str]] = defaultdict(list)
        self.timeline_graphs: Dict[str, nx.DiGraph] = {}

        # Precedent management
        self.precedent_cases: Dict[str, PrecedentCase] = {}
        self.precedent_index: Dict[str, List[str]] = defaultdict(list)

        # Report management
        self.legal_reports: Dict[str, LegalReport] = {}
        self.report_templates: Dict[str, str] = {}

        # Performance tracking
        self.total_cases_managed = 0
        self.total_evidence_processed = 0
        self.total_reports_generated = 0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Initialize litigation components
        self._initialize_litigation_components()

        self.logger.info("LitigationAgent initialized successfully")

    async def start(self):
        """Start the LitigationAgent."""
        self.logger.info("Starting LitigationAgent...")

        # Initialize litigation components
        await self._initialize_litigation_components()

        # Start background tasks
        asyncio.create_task(self._update_case_statuses())
        asyncio.create_task(self._cleanup_old_evidence())

        self.logger.info("LitigationAgent started successfully")

    async def stop(self):
        """Stop the LitigationAgent."""
        self.logger.info("Stopping LitigationAgent...")
        self.logger.info("LitigationAgent stopped")

    def _initialize_litigation_components(self):
        """Initialize litigation components."""
        try:
            # Initialize case management
            self._initialize_case_management()

            # Initialize evidence management
            self._initialize_evidence_management()

            # Initialize timeline management
            self._initialize_timeline_management()

            # Initialize precedent management
            self._initialize_precedent_management()

            # Initialize report management
            self._initialize_report_management()

            self.logger.info("Litigation components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing litigation components: {e}")

    def _initialize_case_management(self):
        """Initialize case management components."""
        try:
            # Create evidence storage directory
            evidence_dir = Path(self.evidence_storage_path)
            evidence_dir.mkdir(parents=True, exist_ok=True)

            # Create report templates directory
            templates_dir = Path(self.report_template_path)
            templates_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info("Case management components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing case management: {e}")

    def _initialize_evidence_management(self):
        """Initialize evidence management components."""
        try:
            # Initialize evidence relationships graph
            self.evidence_relationships = nx.Graph()

            self.logger.info("Evidence management components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing evidence management: {e}")

    def _initialize_timeline_management(self):
        """Initialize timeline management components."""
        try:
            # Initialize timeline graphs for cases
            self.timeline_graphs = {}

            self.logger.info("Timeline management components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing timeline management: {e}")

    def _initialize_precedent_management(self):
        """Initialize precedent management components."""
        try:
            # Initialize precedent indexing
            self.precedent_index = defaultdict(list)

            self.logger.info("Precedent management components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing precedent management: {e}")

    def _initialize_report_management(self):
        """Initialize report management components."""
        try:
            # Initialize report templates
            self._load_report_templates()

            self.logger.info("Report management components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing report management: {e}")

    def _load_report_templates(self):
        """Load report templates."""
        try:
            # Basic report templates
            self.report_templates[
                "case_summary"
            ] = """
# Case Summary Report
## Case: {case_title}
## Case Number: {case_number}
## Status: {status}
## Filing Date: {filing_date}

### Parties
{parties}

### Description
{description}

### Key Events
{key_events}

### Evidence Summary
{evidence_summary}

### Recommendations
{recommendations}

                "evidence_analysis"
            ] = """
# Evidence Analysis Report
## Case: {case_title}
## Evidence Item: {evidence_title}
## Analysis Date: {analysis_date}

### Evidence Details
{evidence_details}

### Analysis Results
{analysis_results}

### Chain of Custody
{chain_of_custody}

### Conclusions
{conclusions}
"""

            self.logger.info(f"Loaded {len(self.report_templates)} report templates")

        except Exception as e:
            self.logger.error(f"Error loading report templates: {e}")

    async def create_case(
        self,
        case_number: str,
        case_title: str,
        case_type: CaseType,
        parties: List[str],
        attorneys: List[str],
        description: str,
        jurisdiction: str,
        court: str,
        judge: str,
    ) -> str:
        """Create a new litigation case."""
        try:
            case_id = str(uuid.uuid4())

            case = LitigationCase(
                case_id=case_id,
                case_number=case_number,
                case_title=case_title,
                case_type=case_type,
                status=CaseStatus.OPEN,
                parties=parties,
                attorneys=attorneys,
                filing_date=datetime.utcnow(),
                description=description,
                jurisdiction=jurisdiction,
                court=court,
                judge=judge,
            )

            # Store case
            self.cases[case_id] = case

            # Initialize case timeline
            self.case_timelines[case_id] = []
            self.timeline_graphs[case_id] = nx.DiGraph()

            # Initialize status history
            self.case_status_history[case_id] = [CaseStatus.OPEN]

            # Update metrics
            self.total_cases_managed += 1

            self.logger.info(f"Created case: {case_id} - {case_title}")

            return case_id

        except Exception as e:
            self.logger.error(f"Error creating case: {e}")
            raise

    async def update_case_status(
        self, case_id: str, new_status: CaseStatus, notes: str = None
    ) -> bool:
        """Update the status of a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} does not exist")

            case = self.cases[case_id]
            old_status = case.status

            # Update status
            case.status = new_status

            # Add to status history
            self.case_status_history[case_id].append(new_status)

            # Create timeline event
            await self._create_timeline_event(
                case_id=case_id,
                event_type="status_change",
                title=f"Status changed from {old_status.value} to {new_status.value}",
                description=notes or f"Case status updated to {new_status.value}",
                participants=case.attorneys,
                outcome=new_status.value,
            )

            self.logger.info(f"Updated case {case_id} status to {new_status.value}")

            return True

        except Exception as e:
            self.logger.error(f"Error updating case status: {e}")
            return False

    async def add_evidence(
        self,
        case_id: str,
        evidence_type: EvidenceType,
        title: str,
        description: str,
        source: str,
        file_path: str = None,
    ) -> str:
        """Add evidence to a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} does not exist")

            evidence_id = str(uuid.uuid4())

            # Generate hash value
            hash_value = self._generate_evidence_hash(title, description, source)

            evidence = EvidenceItem(
                evidence_id=evidence_id,
                case_id=case_id,
                evidence_type=evidence_type,
                title=title,
                description=description,
                source=source,
                collection_date=datetime.utcnow(),
                chain_of_custody=[source],
                hash_value=hash_value,
                file_path=file_path or f"{self.evidence_storage_path}/{evidence_id}",
            )

            # Store evidence
            self.evidence_items[evidence_id] = evidence

            # Index evidence by case
            self.evidence_index[case_id].append(evidence_id)

            # Add to evidence relationships graph
            self.evidence_relationships.add_node(evidence_id, **evidence.__dict__)

            # Update metrics
            self.total_evidence_processed += 1

            self.logger.info(f"Added evidence {evidence_id} to case {case_id}")

            return evidence_id

        except Exception as e:
            self.logger.error(f"Error adding evidence: {e}")
            raise

    def _generate_evidence_hash(self, title: str, description: str, source: str) -> str:
        """Generate a hash value for evidence."""
        try:
            content = f"{title}:{description}:{source}:{datetime.utcnow().isoformat()}"
            return hashlib.sha256(content.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f"Error generating evidence hash: {e}")
            return str(uuid.uuid4())

    async def _create_timeline_event(
        self,
        case_id: str,
        event_type: str,
        title: str,
        description: str,
        participants: List[str],
        outcome: str,
        location: str = None,
    ) -> str:
        """Create a timeline event for a case."""
        try:
            event_id = str(uuid.uuid4())

            event = TimelineEvent(
                event_id=event_id,
                case_id=case_id,
                event_type=event_type,
                title=title,
                description=description,
                date=datetime.utcnow(),
                participants=participants,
                location=location or "Not specified",
                outcome=outcome,
            )

            # Store event
            self.timeline_events[event_id] = event

            # Add to case timeline
            self.case_timelines[case_id].append(event_id)

            # Add to timeline graph
            timeline_graph = self.timeline_graphs[case_id]
            timeline_graph.add_node(event_id, **event.__dict__)

            # Connect to previous event if exists
            if len(self.case_timelines[case_id]) > 1:
                previous_event_id = self.case_timelines[case_id][-2]
                timeline_graph.add_edge(previous_event_id, event_id)

            return event_id

        except Exception as e:
            self.logger.error(f"Error creating timeline event: {e}")
            return ""

    async def get_case_timeline(self, case_id: str) -> List[TimelineEvent]:
        """Get the timeline for a case."""
        try:
            if case_id not in self.cases:
                return []

            timeline_events = []
            for event_id in self.case_timelines[case_id]:
                event = self.timeline_events.get(event_id)
                if event:
                    timeline_events.append(event)

            # Sort by date
            timeline_events.sort(key=lambda x: x.date)

            return timeline_events

        except Exception as e:
            self.logger.error(f"Error getting case timeline: {e}")
            return []

    async def add_precedent_case(
        self,
        case_name: str,
        citation: str,
        court: str,
        date: datetime,
        summary: str,
        key_holdings: List[str],
        relevance_score: float = 0.5,
    ) -> str:
        """Add a precedent case for reference."""
        try:
            precedent_id = str(uuid.uuid4())

            precedent = PrecedentCase(
                precedent_id=precedent_id,
                case_name=case_name,
                citation=citation,
                court=court,
                date=date,
                summary=summary,
                key_holdings=key_holdings,
                relevance_score=relevance_score,
            )

            # Store precedent
            self.precedent_cases[precedent_id] = precedent

            # Index by key holdings
            for holding in key_holdings:
                self.precedent_index[holding.lower()].append(precedent_id)

            self.logger.info(f"Added precedent case: {precedent_id} - {case_name}")

            return precedent_id

        except Exception as e:
            self.logger.error(f"Error adding precedent case: {e}")
            raise

    async def find_relevant_precedents(
        self, query: str, max_results: int = 10
    ) -> List[PrecedentCase]:
        """Find relevant precedent cases based on a query."""
        try:
            relevant_precedents = []
            query_lower = query.lower()

            # Search in key holdings
            for holding, precedent_ids in self.precedent_index.items():
                if query_lower in holding:
                    for precedent_id in precedent_ids:
                        precedent = self.precedent_cases.get(precedent_id)
                        if precedent:
                            relevant_precedents.append(precedent)

            # Search in case names and summaries
            for precedent in self.precedent_cases.values():
                if (
                    query_lower in precedent.case_name.lower()
                    or query_lower in precedent.summary.lower()
                ):
                    if precedent not in relevant_precedents:
                        relevant_precedents.append(precedent)

            # Sort by relevance score
            relevant_precedents.sort(key=lambda x: x.relevance_score, reverse=True)

            return relevant_precedents[:max_results]

        except Exception as e:
            self.logger.error(f"Error finding relevant precedents: {e}")
            return []

    async def generate_legal_report(
        self, case_id: str, report_type: str, title: str, content: str, author: str
    ) -> str:
        """Generate a legal report for a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} does not exist")

            report_id = str(uuid.uuid4())

            report = LegalReport(
                report_id=report_id,
                case_id=case_id,
                report_type=report_type,
                title=title,
                content=content,
                author=author,
                creation_date=datetime.utcnow(),
                last_modified=datetime.utcnow(),
                version="1.0",
            )

            # Store report
            self.legal_reports[report_id] = report

            # Update metrics
            self.total_reports_generated += 1

            self.logger.info(f"Generated legal report: {report_id} - {title}")

            return report_id

        except Exception as e:
            self.logger.error(f"Error generating legal report: {e}")
            raise

    async def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of a case."""
        try:
            if case_id not in self.cases:
                return {}

            case = self.cases[case_id]

            # Get timeline events
            timeline_events = await self.get_case_timeline(case_id)

            # Get evidence items
            evidence_items = [
                self.evidence_items[ev_id] for ev_id in self.evidence_index[case_id]
            ]

            # Get legal reports
            case_reports = [
                report
                for report in self.legal_reports.values()
                if report.case_id == case_id
            ]

            summary = {
                "case": case,
                "timeline_events": timeline_events,
                "evidence_items": evidence_items,
                "legal_reports": case_reports,
                "status_history": self.case_status_history[case_id],
                "total_evidence": len(evidence_items),
                "total_reports": len(case_reports),
                "case_duration": (datetime.utcnow() - case.filing_date).days,
            }

            return summary

        except Exception as e:
            self.logger.error(f"Error getting case summary: {e}")
            return {}

    async def _update_case_statuses(self):
        """Background task to update case statuses."""
        while True:
            try:
                current_time = datetime.utcnow()

                for case_id, case in self.cases.items():
                    if case.status == CaseStatus.OPEN:
                        # Check if case should move to investigation
                        if (current_time - case.filing_date).days > 7:
                            await self.update_case_status(
                                case_id, CaseStatus.INVESTIGATION
                            )

                    elif case.status == CaseStatus.INVESTIGATION:
                        # Check if case should move to evidence collection
                        evidence_count = len(self.evidence_index[case_id])
                        if evidence_count > 5:
                            await self.update_case_status(
                                case_id, CaseStatus.EVIDENCE_COLLECTION
                            )

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                self.logger.error(f"Error updating case statuses: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_evidence(self):
        """Background task to cleanup old evidence."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_date = current_time - timedelta(days=365)  # 1 year

                old_evidence = []
                for evidence_id, evidence in self.evidence_items.items():
                    if evidence.collection_date < cutoff_date:
                        old_evidence.append(evidence_id)

                # Archive old evidence (don't delete, just mark as archived)
                for evidence_id in old_evidence:
                    evidence = self.evidence_items[evidence_id]
                    evidence.metadata["archived"] = True
                    evidence.metadata["archive_date"] = current_time.isoformat()

                if old_evidence:
                    self.logger.info(f"Archived {len(old_evidence)} old evidence items")

                await asyncio.sleep(86400)  # Check every day

            except Exception as e:
                self.logger.error(f"Error cleaning up old evidence: {e}")
                await asyncio.sleep(86400)

    def get_litigation_metrics(self) -> LitigationMetrics:
        """Get litigation performance metrics."""
        try:
            active_cases = sum(
                1 for case in self.cases.values() if case.status != CaseStatus.CLOSED
            )
            closed_cases = sum(
                1 for case in self.cases.values() if case.status == CaseStatus.CLOSED
            )

            # Calculate average case duration
            total_duration = 0
            case_count = 0
            for case in self.cases.values():
                if case.status == CaseStatus.CLOSED:
                    duration = (case.filing_date - case.filing_date).days  # Placeholder
                    total_duration += duration
                    case_count += 1

            average_duration = total_duration / case_count if case_count > 0 else 0

            return LitigationMetrics(
                total_cases=self.total_cases_managed,
                active_cases=active_cases,
                closed_cases=closed_cases,
                average_case_duration=average_duration,
                evidence_items_processed=self.total_evidence_processed,
                reports_generated=self.total_reports_generated,
                metadata={
                    "case_types_supported": [ct.value for ct in CaseType],
                    "case_statuses_supported": [cs.value for cs in CaseStatus],
                    "evidence_types_supported": [et.value for et in EvidenceType],
                    "max_cases_per_agent": self.max_cases_per_agent,
                    "evidence_storage_path": self.evidence_storage_path,
                    "report_template_path": self.report_template_path,
                },
            )

        except Exception as e:
            self.logger.error(f"Error getting litigation metrics: {e}")
            return LitigationMetrics(
                total_cases=0,
                active_cases=0,
                closed_cases=0,
                average_case_duration=0.0,
                evidence_items_processed=0,
                reports_generated=0,
            )

# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "max_cases_per_agent": 10,
        "evidence_storage_path": "./evidence",
        "report_template_path": "./templates",
    }

    # Initialize litigation agent
    litigation_agent = LitigationAgent(config)

    print("LitigationAgent system initialized successfully!")
