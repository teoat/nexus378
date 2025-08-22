"""
Litigation Agent Core System - Case Management and Legal Support

This module implements the LitigationAgent class that provides
comprehensive litigation support capabilities for the forensic platform.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import networkx as nx
from pathlib import Path
import pandas as pd

from ...taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class CaseStatus(Enum):
    """Status of litigation cases."""
    OPEN = "open"                                         # Case is open
    INVESTIGATION = "investigation"                        # Under investigation
    EVIDENCE_COLLECTION = "evidence_collection"            # Collecting evidence
    ANALYSIS = "analysis"                                  # Analyzing evidence
    REPORTING = "reporting"                                # Generating reports
    REVIEW = "review"                                      # Under review
    CLOSED = "closed"                                      # Case closed
    ARCHIVED = "archived"                                  # Case archived


class EvidenceType(Enum):
    """Types of evidence."""
    DOCUMENT = "document"                                  # Document evidence
    IMAGE = "image"                                        # Image evidence
    AUDIO = "audio"                                        # Audio evidence
    VIDEO = "video"                                        # Video evidence
    DIGITAL = "digital"                                    # Digital evidence
    PHYSICAL = "physical"                                  # Physical evidence
    TESTIMONY = "testimony"                                # Testimony evidence
    EXPERT_OPINION = "expert_opinion"                      # Expert opinion


class TimelineEventType(Enum):
    """Types of timeline events."""
    CASE_OPENED = "case_opened"                            # Case opened
    EVIDENCE_COLLECTED = "evidence_collected"              # Evidence collected
    ANALYSIS_STARTED = "analysis_started"                  # Analysis started
    REPORT_GENERATED = "report_generated"                  # Report generated
    REVIEW_COMPLETED = "review_completed"                  # Review completed
    CASE_CLOSED = "case_closed"                            # Case closed


@dataclass
class LitigationCase:
    """A litigation case."""
    
    case_id: str
    case_number: str
    case_title: str
    case_description: str
    case_type: str
    status: CaseStatus
    opened_date: datetime
    assigned_agents: List[str]
    evidence_items: List[str]
    timeline_events: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    """An evidence item in a case."""
    
    evidence_id: str
    case_id: str
    evidence_type: EvidenceType
    description: str
    source: str
    collection_date: datetime
    file_path: str
    hash_value: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineEvent:
    """A timeline event in a case."""
    
    event_id: str
    case_id: str
    event_type: TimelineEventType
    event_description: str
    timestamp: datetime
    agent_id: str
    related_evidence: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrecedentCase:
    """A precedent case for analysis."""
    
    precedent_id: str
    case_title: str
    case_summary: str
    relevant_facts: List[str]
    legal_principles: List[str]
    outcome: str
    citation: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LegalReport:
    """A legal report generated for a case."""
    
    report_id: str
    case_id: str
    report_title: str
    report_type: str
    generated_date: datetime
    author_agent: str
    content: str
    summary: str
    recommendations: List[str]
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
        self.max_cases_per_agent = config.get('max_cases_per_agent', 10)
        self.evidence_storage_path = config.get('evidence_storage_path', './evidence')
        self.report_template_path = config.get('report_template_path', './templates')
        
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
        
        # Initialize storage
        self._initialize_storage()
        
        self.logger.info("LitigationAgent initialized successfully")
    
    async def start(self):
        """Start the LitigationAgent."""
        self.logger.info("Starting LitigationAgent...")
        
        # Initialize litigation components
        await self._initialize_litigation_components()
        
        # Start background tasks
        asyncio.create_task(self._update_case_statuses())
        asyncio.create_task(self._cleanup_old_data())
        
        self.logger.info("LitigationAgent started successfully")
    
    async def stop(self):
        """Stop the LitigationAgent."""
        self.logger.info("Stopping LitigationAgent...")
        self.logger.info("LitigationAgent stopped")
    
    def _initialize_storage(self):
        """Initialize storage directories."""
        try:
            # Create evidence storage directory
            evidence_path = Path(self.evidence_storage_path)
            evidence_path.mkdir(parents=True, exist_ok=True)
            
            # Create report templates directory
            template_path = Path(self.report_template_path)
            template_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("Storage directories initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing storage: {e}")
    
    async def create_case(self, case_number: str, case_title: str, case_description: str,
                          case_type: str, assigned_agents: List[str]) -> LitigationCase:
        """Create a new litigation case."""
        try:
            # Validate case number uniqueness
            if any(case.case_number == case_number for case in self.cases.values()):
                raise ValueError(f"Case number {case_number} already exists")
            
            # Create case
            case = LitigationCase(
                case_id=str(uuid.uuid4()),
                case_number=case_number,
                case_title=case_title,
                case_description=case_description,
                case_type=case_type,
                status=CaseStatus.OPEN,
                opened_date=datetime.utcnow(),
                assigned_agents=assigned_agents,
                evidence_items=[],
                timeline_events=[]
            )
            
            # Store case
            self.cases[case.case_id] = case
            
            # Update assignments
            for agent_id in assigned_agents:
                self.case_assignments[agent_id].append(case.case_id)
            
            # Initialize status history
            self.case_status_history[case.case_id] = [CaseStatus.OPEN]
            
            # Initialize timeline graph
            self.timeline_graphs[case.case_id] = nx.DiGraph()
            
            # Create initial timeline event
            await self._create_timeline_event(
                case.case_id,
                TimelineEventType.CASE_OPENED,
                f"Case {case_number} opened",
                assigned_agents[0] if assigned_agents else "system"
            )
            
            # Update statistics
            self.total_cases_managed += 1
            
            self.logger.info(f"Created case: {case.case_id} - {case_title}")
            
            return case
            
        except Exception as e:
            self.logger.error(f"Error creating case: {e}")
            raise
    
    async def update_case_status(self, case_id: str, new_status: CaseStatus, agent_id: str,
                                notes: str = None) -> bool:
        """Update the status of a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            case = self.cases[case_id]
            old_status = case.status
            
            # Update status
            case.status = new_status
            self.case_status_history[case_id].append(new_status)
            
            # Create timeline event
            event_description = f"Case status changed from {old_status.value} to {new_status.value}"
            if notes:
                event_description += f": {notes}"
            
            await self._create_timeline_event(
                case_id,
                TimelineEventType.ANALYSIS_STARTED if new_status == CaseStatus.ANALYSIS else TimelineEventType.CASE_OPENED,
                event_description,
                agent_id
            )
            
            self.logger.info(f"Updated case {case_id} status: {old_status.value} -> {new_status.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating case status: {e}")
            return False
    
    async def add_evidence(self, case_id: str, evidence_type: EvidenceType, description: str,
                           source: str, file_path: str, hash_value: str,
                           metadata: Dict[str, Any] = None) -> EvidenceItem:
        """Add evidence to a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            # Create evidence item
            evidence = EvidenceItem(
                evidence_id=str(uuid.uuid4()),
                case_id=case_id,
                evidence_type=evidence_type,
                description=description,
                source=source,
                collection_date=datetime.utcnow(),
                file_path=file_path,
                hash_value=hash_value,
                metadata=metadata or {}
            )
            
            # Store evidence
            self.evidence_items[evidence.evidence_id] = evidence
            self.evidence_index[case_id].append(evidence.evidence_id)
            
            # Add to case
            self.cases[case_id].evidence_items.append(evidence.evidence_id)
            
            # Create timeline event
            await self._create_timeline_event(
                case_id,
                TimelineEventType.EVIDENCE_COLLECTED,
                f"Evidence collected: {description}",
                "evidence_system"
            )
            
            # Update statistics
            self.total_evidence_processed += 1
            
            self.logger.info(f"Added evidence: {evidence.evidence_id} to case: {case_id}")
            
            return evidence
            
        except Exception as e:
            self.logger.error(f"Error adding evidence: {e}")
            raise
    
    async def _create_timeline_event(self, case_id: str, event_type: TimelineEventType,
                                    description: str, agent_id: str,
                                    related_evidence: List[str] = None) -> TimelineEvent:
        """Create a timeline event for a case."""
        try:
            event = TimelineEvent(
                event_id=str(uuid.uuid4()),
                case_id=case_id,
                event_type=event_type,
                event_description=description,
                timestamp=datetime.utcnow(),
                agent_id=agent_id,
                related_evidence=related_evidence or []
            )
            
            # Store event
            self.timeline_events[event.event_id] = event
            self.case_timelines[case_id].append(event.event_id)
            
            # Add to timeline graph
            timeline_graph = self.timeline_graphs[case_id]
            timeline_graph.add_node(event.event_id, **{
                'type': event.event_type.value,
                'description': event.event_description,
                'timestamp': event.timestamp,
                'agent': event.agent_id
            })
            
            # Add edges to previous events
            if len(self.case_timelines[case_id]) > 1:
                prev_event_id = self.case_timelines[case_id][-2]
                timeline_graph.add_edge(prev_event_id, event.event_id)
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error creating timeline event: {e}")
            raise
    
    async def get_case_timeline(self, case_id: str) -> List[TimelineEvent]:
        """Get the timeline for a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            timeline_events = []
            for event_id in self.case_timelines[case_id]:
                if event_id in self.timeline_events:
                    timeline_events.append(self.timeline_events[event_id])
            
            # Sort by timestamp
            timeline_events.sort(key=lambda x: x.timestamp)
            
            return timeline_events
            
        except Exception as e:
            self.logger.error(f"Error getting case timeline: {e}")
            return []
    
    async def add_precedent_case(self, case_title: str, case_summary: str, relevant_facts: List[str],
                                legal_principles: List[str], outcome: str, citation: str) -> PrecedentCase:
        """Add a precedent case for analysis."""
        try:
            precedent = PrecedentCase(
                precedent_id=str(uuid.uuid4()),
                case_title=case_title,
                case_summary=case_summary,
                relevant_facts=relevant_facts,
                legal_principles=legal_principles,
                outcome=outcome,
                citation=citation,
                relevance_score=0.0,  # Will be calculated later
                metadata={}
            )
            
            # Store precedent
            self.precedent_cases[precedent.precedent_id] = precedent
            
            # Index by legal principles
            for principle in legal_principles:
                self.precedent_index[principle].append(precedent.precedent_id)
            
            self.logger.info(f"Added precedent case: {precedent.precedent_id} - {case_title}")
            
            return precedent
            
        except Exception as e:
            self.logger.error(f"Error adding precedent case: {e}")
            raise
    
    async def find_relevant_precedents(self, case_id: str, search_criteria: Dict[str, Any]) -> List[PrecedentCase]:
        """Find relevant precedent cases for a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            case = self.cases[case_id]
            relevant_precedents = []
            
            # Simple relevance scoring based on case type and description
            for precedent in self.precedent_cases.values():
                relevance_score = 0.0
                
                # Score based on case type similarity
                if case.case_type.lower() in precedent.case_title.lower():
                    relevance_score += 0.3
                
                # Score based on description keywords
                case_keywords = case.case_description.lower().split()
                precedent_keywords = precedent.case_summary.lower().split()
                
                common_keywords = set(case_keywords) & set(precedent_keywords)
                if common_keywords:
                    relevance_score += min(0.4, len(common_keywords) * 0.1)
                
                # Score based on legal principles
                for principle in precedent.legal_principles:
                    if principle.lower() in case.case_description.lower():
                        relevance_score += 0.2
                
                # Update relevance score
                precedent.relevance_score = min(1.0, relevance_score)
                
                if relevance_score > 0.3:  # Threshold for relevance
                    relevant_precedents.append(precedent)
            
            # Sort by relevance score
            relevant_precedents.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return relevant_precedents
            
        except Exception as e:
            self.logger.error(f"Error finding relevant precedents: {e}")
            return []
    
    async def generate_legal_report(self, case_id: str, report_type: str, author_agent: str,
                                   content: str, summary: str, recommendations: List[str]) -> LegalReport:
        """Generate a legal report for a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            # Create report
            report = LegalReport(
                report_id=str(uuid.uuid4()),
                case_id=case_id,
                report_title=f"{report_type} Report - Case {self.cases[case_id].case_number}",
                report_type=report_type,
                generated_date=datetime.utcnow(),
                author_agent=author_agent,
                content=content,
                summary=summary,
                recommendations=recommendations
            )
            
            # Store report
            self.legal_reports[report.report_id] = report
            
            # Create timeline event
            await self._create_timeline_event(
                case_id,
                TimelineEventType.REPORT_GENERATED,
                f"{report_type} report generated",
                author_agent
            )
            
            # Update statistics
            self.total_reports_generated += 1
            
            self.logger.info(f"Generated legal report: {report.report_id} for case: {case_id}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating legal report: {e}")
            raise
    
    async def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of a case."""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            case = self.cases[case_id]
            
            # Get timeline events
            timeline_events = await self.get_case_timeline(case_id)
            
            # Get evidence summary
            evidence_summary = []
            for evidence_id in case.evidence_items:
                if evidence_id in self.evidence_items:
                    evidence = self.evidence_items[evidence_id]
                    evidence_summary.append({
                        'type': evidence.evidence_type.value,
                        'description': evidence.description,
                        'source': evidence.source,
                        'collection_date': evidence.collection_date.isoformat()
                    })
            
            # Get recent reports
            recent_reports = []
            for report in self.legal_reports.values():
                if report.case_id == case_id:
                    recent_reports.append({
                        'title': report.report_title,
                        'type': report.report_type,
                        'generated_date': report.generated_date.isoformat(),
                        'summary': report.summary
                    })
            
            # Calculate case metrics
            case_duration = datetime.utcnow() - case.opened_date
            evidence_count = len(case.evidence_items)
            timeline_length = len(timeline_events)
            report_count = len(recent_reports)
            
            summary = {
                'case_id': case.case_id,
                'case_number': case.case_number,
                'case_title': case.case_title,
                'case_type': case.case_type,
                'status': case.status.value,
                'opened_date': case.opened_date.isoformat(),
                'case_duration_days': case_duration.days,
                'assigned_agents': case.assigned_agents,
                'evidence_count': evidence_count,
                'timeline_length': timeline_length,
                'report_count': report_count,
                'evidence_summary': evidence_summary,
                'recent_reports': recent_reports,
                'status_history': [status.value for status in self.case_status_history[case_id]]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting case summary: {e}")
            return {}
    
    async def _update_case_statuses(self):
        """Update case statuses based on workflow."""
        while True:
            try:
                # This would implement automatic status updates based on workflow
                # For now, just log activity
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                self.logger.error(f"Error updating case statuses: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old data and cases."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=365)  # Keep 1 year of data
                
                # Clean up old cases
                old_cases = [
                    case_id for case_id, case in self.cases.items()
                    if case.opened_date < cutoff_time and case.status == CaseStatus.ARCHIVED
                ]
                
                for case_id in old_cases:
                    del self.cases[case_id]
                
                # Clean up old evidence
                old_evidence = [
                    evidence_id for evidence_id, evidence in self.evidence_items.items()
                    if evidence.collection_date < cutoff_time
                ]
                
                for evidence_id in old_evidence:
                    del self.evidence_items[evidence_id]
                
                if old_cases or old_evidence:
                    self.logger.info(f"Cleaned up {len(old_cases)} old cases and {len(old_evidence)} old evidence items")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _initialize_litigation_components(self):
        """Initialize litigation components."""
        try:
            # Initialize default components
            await self._initialize_default_components()
            
            self.logger.info("Litigation components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing litigation components: {e}")
    
    async def _initialize_default_components(self):
        """Initialize default litigation components."""
        try:
            # This would initialize default components
            # For now, just log initialization
            self.logger.info("Default litigation components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing default components: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_cases_managed': self.total_cases_managed,
            'total_evidence_processed': self.total_evidence_processed,
            'total_reports_generated': self.total_reports_generated,
            'active_cases': len([c for c in self.cases.values() if c.status != CaseStatus.CLOSED]),
            'case_statuses_supported': [s.value for s in CaseStatus],
            'evidence_types_supported': [t.value for t in EvidenceType],
            'timeline_event_types_supported': [t.value for t in TimelineEventType],
            'total_precedents': len(self.precedent_cases),
            'total_reports': len(self.legal_reports)
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'max_cases_per_agent': 10,
        'evidence_storage_path': './evidence',
        'report_template_path': './templates'
    }
    
    # Initialize litigation agent
    agent = LitigationAgent(config)
    
    print("LitigationAgent system initialized successfully!")
