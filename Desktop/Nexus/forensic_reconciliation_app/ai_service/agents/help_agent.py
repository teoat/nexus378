"""
Help Agent RAG System - Retrieval-Augmented Generation for Interactive Guidance

This module implements the HelpAgent class that provides
comprehensive help and guidance capabilities using RAG technology
for the forensic platform.
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
import numpy as np
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import tiktoken

from ...taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class QueryType(Enum):
    """Types of user queries."""
    GENERAL_HELP = "general_help"                           # General help questions
    WORKFLOW_GUIDANCE = "workflow_guidance"                  # Workflow guidance
    TECHNICAL_SUPPORT = "technical_support"                  # Technical support
    FEATURE_EXPLANATION = "feature_explanation"             # Feature explanation
    ERROR_TROUBLESHOOTING = "error_troubleshooting"          # Error troubleshooting
    BEST_PRACTICES = "best_practices"                        # Best practices
    TUTORIAL_REQUEST = "tutorial_request"                    # Tutorial requests
    REFERENCE_LOOKUP = "reference_lookup"                    # Reference lookups


class ResponseType(Enum):
    """Types of responses."""
    DIRECT_ANSWER = "direct_answer"                          # Direct answer to question
    STEP_BY_STEP = "step_by_step"                           # Step-by-step guidance
    REFERENCE_LINK = "reference_link"                        # Reference to documentation
    TUTORIAL_CONTENT = "tutorial_content"                    # Tutorial content
    ERROR_SOLUTION = "error_solution"                        # Error solution
    BEST_PRACTICE_TIP = "best_practice_tip"                  # Best practice tip
    WORKFLOW_SUGGESTION = "workflow_suggestion"              # Workflow suggestion


@dataclass
class KnowledgeBaseEntry:
    """A knowledge base entry."""
    
    entry_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_date: datetime
    last_updated: datetime
    source: str
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserQuery:
    """A user query for help."""
    
    query_id: str
    user_id: str
    query_text: str
    query_type: QueryType
    context: Dict[str, Any]
    timestamp: datetime
    priority: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HelpResponse:
    """A help response to a user query."""
    
    response_id: str
    query_id: str
    response_type: ResponseType
    response_content: str
    confidence_score: float
    source_entries: List[str]
    generated_timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """A step in a workflow guidance."""
    
    step_id: str
    step_number: int
    step_title: str
    step_description: str
    step_instructions: List[str]
    expected_outcome: str
    prerequisites: List[str]
    estimated_time: int  # minutes
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowGuide:
    """A complete workflow guide."""
    
    guide_id: str
    guide_title: str
    guide_description: str
    workflow_steps: List[WorkflowStep]
    total_estimated_time: int  # minutes
    difficulty_level: str
    prerequisites: List[str]
    created_date: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class HelpAgent:
    """
    Comprehensive help and guidance system using RAG technology.
    
    The HelpAgent is responsible for:
    - Processing user queries and requests for help
    - Retrieving relevant information from knowledge base
    - Generating contextual responses using RAG
    - Providing workflow guidance and tutorials
    - Supporting interactive help sessions
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the HelpAgent."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.knowledge_base_path = config.get('knowledge_base_path', './knowledge_base')
        self.max_response_length = config.get('max_response_length', 2000)
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
        self.max_retrieved_entries = config.get('max_retrieved_entries', 5)
        
        # Knowledge base management
        self.knowledge_entries: Dict[str, KnowledgeBaseEntry] = {}
        self.entry_index: Dict[str, List[str]] = defaultdict(list)
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.entry_vectors: Optional[np.ndarray] = None
        
        # Query processing
        self.user_queries: Dict[str, UserQuery] = {}
        self.help_responses: Dict[str, HelpResponse] = {}
        self.query_history: Dict[str, List[str]] = defaultdict(list)
        
        # Workflow management
        self.workflow_guides: Dict[str, WorkflowGuide] = {}
        self.workflow_templates: Dict[str, str] = {}
        
        # Performance tracking
        self.total_queries_processed = 0
        self.total_responses_generated = 0
        self.average_response_time = 0.0
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        # Initialize knowledge base
        self._initialize_knowledge_base()
        
        self.logger.info("HelpAgent initialized successfully")
    
    async def start(self):
        """Start the HelpAgent."""
        self.logger.info("Starting HelpAgent...")
        
        # Initialize help components
        await self._initialize_help_components()
        
        # Start background tasks
        asyncio.create_task(self._update_knowledge_base())
        asyncio.create_task(self._cleanup_old_data())
        
        self.logger.info("HelpAgent started successfully")
    
    async def stop(self):
        """Stop the HelpAgent."""
        self.logger.info("Stopping HelpAgent...")
        self.logger.info("HelpAgent stopped")
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base."""
        try:
            # Create knowledge base directory
            kb_path = Path(self.knowledge_base_path)
            kb_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize default knowledge entries
            self._initialize_default_knowledge()
            
            # Initialize vectorizer
            self._initialize_vectorizer()
            
            self.logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing knowledge base: {e}")
    
    def _initialize_default_knowledge(self):
        """Initialize default knowledge entries."""
        try:
            # Create default knowledge entries
            default_entries = [
                {
                    'title': 'Getting Started with Forensic Platform',
                    'content': 'Welcome to the forensic platform. This platform provides comprehensive tools for forensic analysis, risk assessment, and evidence management.',
                    'category': 'getting_started',
                    'tags': ['introduction', 'platform', 'forensic']
                },
                {
                    'title': 'Evidence Collection Best Practices',
                    'content': 'When collecting evidence, always maintain chain of custody, document everything, and use appropriate tools for different evidence types.',
                    'category': 'best_practices',
                    'tags': ['evidence', 'collection', 'chain_of_custody']
                },
                {
                    'title': 'Risk Assessment Workflow',
                    'content': 'The risk assessment workflow involves: 1) Identify risks, 2) Assess probability and impact, 3) Prioritize risks, 4) Develop mitigation strategies.',
                    'category': 'workflow',
                    'tags': ['risk_assessment', 'workflow', 'mitigation']
                }
            ]
            
            for entry_data in default_entries:
                entry = KnowledgeBaseEntry(
                    entry_id=str(uuid.uuid4()),
                    title=entry_data['title'],
                    content=entry_data['content'],
                    category=entry_data['category'],
                    tags=entry_data['tags'],
                    created_date=datetime.utcnow(),
                    last_updated=datetime.utcnow(),
                    source='system',
                    confidence_score=0.9
                )
                
                self.knowledge_entries[entry.entry_id] = entry
                
                # Index by category and tags
                self.entry_index[entry.category].append(entry.entry_id)
                for tag in entry.tags:
                    self.entry_index[tag].append(entry.entry_id)
            
            self.logger.info(f"Initialized {len(default_entries)} default knowledge entries")
            
        except Exception as e:
            self.logger.error(f"Error initializing default knowledge: {e}")
    
    def _initialize_vectorizer(self):
        """Initialize the TF-IDF vectorizer."""
        try:
            if not self.knowledge_entries:
                return
            
            # Prepare text for vectorization
            texts = [entry.content for entry in self.knowledge_entries.values()]
            
            # Create and fit vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            self.entry_vectors = self.vectorizer.fit_transform(texts).toarray()
            
            self.logger.info("Vectorizer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing vectorizer: {e}")
    
    async def add_knowledge_entry(self, title: str, content: str, category: str,
                                 tags: List[str], source: str) -> KnowledgeBaseEntry:
        """Add a new knowledge base entry."""
        try:
            entry = KnowledgeBaseEntry(
                entry_id=str(uuid.uuid4()),
                title=title,
                content=content,
                category=category,
                tags=tags,
                created_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                source=source,
                confidence_score=0.8  # Default confidence
            )
            
            # Store entry
            self.knowledge_entries[entry.entry_id] = entry
            
            # Update indexes
            self.entry_index[category].append(entry.entry_id)
            for tag in tags:
                self.entry_index[tag].append(entry.entry_id)
            
            # Update vectorizer if needed
            if self.vectorizer:
                await self._update_vectorizer()
            
            self.logger.info(f"Added knowledge entry: {entry.entry_id} - {title}")
            
            return entry
            
        except Exception as e:
            self.logger.error(f"Error adding knowledge entry: {e}")
            raise
    
    async def _update_vectorizer(self):
        """Update the vectorizer with new entries."""
        try:
            if not self.vectorizer or not self.knowledge_entries:
                return
            
            # Reinitialize vectorizer with all entries
            texts = [entry.content for entry in self.knowledge_entries.values()]
            self.entry_vectors = self.vectorizer.fit_transform(texts).toarray()
            
            self.logger.info("Vectorizer updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating vectorizer: {e}")
    
    async def process_help_query(self, user_id: str, query_text: str, query_type: QueryType = None,
                                context: Dict[str, Any] = None) -> HelpResponse:
        """Process a user help query using RAG technology."""
        try:
            start_time = datetime.utcnow()
            
            # Determine query type if not provided
            if not query_type:
                query_type = self._classify_query_type(query_text)
            
            # Create user query
            query = UserQuery(
                query_id=str(uuid.uuid4()),
                user_id=user_id,
                query_text=query_text,
                query_type=query_type,
                context=context or {},
                timestamp=datetime.utcnow(),
                priority='normal'
            )
            
            # Store query
            self.user_queries[query.query_id] = query
            self.query_history[user_id].append(query.query_id)
            
            self.logger.info(f"Processing help query: {query.query_id} - Type: {query_type.value}")
            
            # Retrieve relevant knowledge
            relevant_entries = await self._retrieve_relevant_knowledge(query_text)
            
            # Generate response using RAG
            response = await self._generate_rag_response(query, relevant_entries)
            
            # Store response
            self.help_responses[response.response_id] = response
            
            # Update statistics
            self.total_queries_processed += 1
            self.total_responses_generated += 1
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.average_response_time = (self.average_response_time + processing_time) / 2
            
            self.logger.info(f"Generated help response: {response.response_id}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing help query: {e}")
            raise
    
    def _classify_query_type(self, query_text: str) -> QueryType:
        """Classify the type of user query."""
        try:
            query_lower = query_text.lower()
            
            # Simple keyword-based classification
            if any(word in query_lower for word in ['how', 'step', 'workflow', 'process']):
                return QueryType.WORKFLOW_GUIDANCE
            elif any(word in query_lower for word in ['error', 'problem', 'issue', 'bug']):
                return QueryType.ERROR_TROUBLESHOOTING
            elif any(word in query_lower for word in ['what is', 'explain', 'feature', 'function']):
                return QueryType.FEATURE_EXPLANATION
            elif any(word in query_lower for word in ['best practice', 'recommendation', 'tip']):
                return QueryType.BEST_PRACTICES
            elif any(word in query_lower for word in ['tutorial', 'learn', 'guide']):
                return QueryType.TUTORIAL_REQUEST
            elif any(word in query_lower for word in ['reference', 'documentation', 'manual']):
                return QueryType.REFERENCE_LOOKUP
            else:
                return QueryType.GENERAL_HELP
            
        except Exception as e:
            self.logger.error(f"Error classifying query type: {e}")
            return QueryType.GENERAL_HELP
    
    async def _retrieve_relevant_knowledge(self, query_text: str) -> List[KnowledgeBaseEntry]:
        """Retrieve relevant knowledge base entries for a query."""
        try:
            if not self.vectorizer or self.entry_vectors is None:
                # Fallback to simple text search
                return self._simple_text_search(query_text)
            
            # Vectorize query
            query_vector = self.vectorizer.transform([query_text]).toarray()
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.entry_vectors)[0]
            
            # Get top similar entries
            top_indices = np.argsort(similarities)[::-1][:self.max_retrieved_entries]
            
            relevant_entries = []
            for idx in top_indices:
                if similarities[idx] >= self.similarity_threshold:
                    entry_id = list(self.knowledge_entries.keys())[idx]
                    relevant_entries.append(self.knowledge_entries[entry_id])
            
            return relevant_entries
            
        except Exception as e:
            self.logger.error(f"Error retrieving relevant knowledge: {e}")
            return []
    
    def _simple_text_search(self, query_text: str) -> List[KnowledgeBaseEntry]:
        """Simple text-based search as fallback."""
        try:
            query_lower = query_text.lower()
            relevant_entries = []
            
            for entry in self.knowledge_entries.values():
                # Calculate simple relevance score
                title_score = sum(1 for word in query_lower.split() if word in entry.title.lower())
                content_score = sum(1 for word in query_lower.split() if word in entry.content.lower())
                tag_score = sum(1 for word in query_lower.split() if word in [tag.lower() for tag in entry.tags])
                
                total_score = title_score * 2 + content_score + tag_score * 1.5
                
                if total_score > 0:
                    entry.metadata['relevance_score'] = total_score
                    relevant_entries.append(entry)
            
            # Sort by relevance score
            relevant_entries.sort(key=lambda x: x.metadata.get('relevance_score', 0), reverse=True)
            
            return relevant_entries[:self.max_retrieved_entries]
            
        except Exception as e:
            self.logger.error(f"Error in simple text search: {e}")
            return []
    
    async def _generate_rag_response(self, query: UserQuery, relevant_entries: List[KnowledgeBaseEntry]) -> HelpResponse:
        """Generate a response using RAG technology."""
        try:
            if not relevant_entries:
                # Generate fallback response
                response_content = self._generate_fallback_response(query)
                response_type = ResponseType.DIRECT_ANSWER
                confidence_score = 0.5
                source_entries = []
            else:
                # Generate RAG response
                response_content = await self._generate_contextual_response(query, relevant_entries)
                response_type = self._determine_response_type(query.query_type)
                confidence_score = min(0.95, len(relevant_entries) / self.max_retrieved_entries + 0.3)
                source_entries = [entry.entry_id for entry in relevant_entries]
            
            response = HelpResponse(
                response_id=str(uuid.uuid4()),
                query_id=query.query_id,
                response_type=response_type,
                response_content=response_content,
                confidence_score=confidence_score,
                source_entries=source_entries,
                generated_timestamp=datetime.utcnow()
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating RAG response: {e}")
            raise
    
    def _generate_fallback_response(self, query: UserQuery) -> str:
        """Generate a fallback response when no relevant knowledge is found."""
        try:
            fallback_responses = {
                QueryType.GENERAL_HELP: "I understand you need help. Let me search our knowledge base for relevant information.",
                QueryType.WORKFLOW_GUIDANCE: "I can help you with workflow guidance. Please provide more specific details about what you're trying to accomplish.",
                QueryType.TECHNICAL_SUPPORT: "For technical support, please describe the specific issue you're experiencing.",
                QueryType.FEATURE_EXPLANATION: "I'd be happy to explain features. Which specific feature would you like to know more about?",
                QueryType.ERROR_TROUBLESHOOTING: "I can help troubleshoot errors. Please share the error message and what you were doing when it occurred.",
                QueryType.BEST_PRACTICES: "I can provide best practices guidance. What specific area are you interested in?",
                QueryType.TUTORIAL_REQUEST: "I can help you find tutorials. What would you like to learn about?",
                QueryType.REFERENCE_LOOKUP: "I can help you find reference information. What specific topic are you looking for?"
            }
            
            return fallback_responses.get(query.query_type, "I'm here to help. Please let me know what you need assistance with.")
            
        except Exception as e:
            self.logger.error(f"Error generating fallback response: {e}")
            return "I'm here to help. Please let me know what you need assistance with."
    
    async def _generate_contextual_response(self, query: UserQuery, relevant_entries: List[KnowledgeBaseEntry]) -> str:
        """Generate a contextual response based on relevant knowledge entries."""
        try:
            # Combine relevant knowledge
            combined_knowledge = "\n\n".join([
                f"**{entry.title}**\n{entry.content}"
                for entry in relevant_entries
            ])
            
            # Generate response based on query type
            if query.query_type == QueryType.WORKFLOW_GUIDANCE:
                response = self._generate_workflow_response(query, relevant_entries)
            elif query.query_type == QueryType.ERROR_TROUBLESHOOTING:
                response = self._generate_troubleshooting_response(query, relevant_entries)
            elif query.query_type == QueryType.BEST_PRACTICES:
                response = self._generate_best_practices_response(query, relevant_entries)
            else:
                response = self._generate_general_response(query, relevant_entries)
            
            # Limit response length
            if len(response) > self.max_response_length:
                response = response[:self.max_response_length] + "..."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating contextual response: {e}")
            return self._generate_fallback_response(query)
    
    def _generate_workflow_response(self, query: UserQuery, relevant_entries: List[KnowledgeBaseEntry]) -> str:
        """Generate a workflow-focused response."""
        try:
            response_parts = [
                f"Based on your query about '{query.query_text}', here's a step-by-step workflow:"
            ]
            
            for i, entry in enumerate(relevant_entries, 1):
                response_parts.append(f"\n**Step {i}: {entry.title}**")
                response_parts.append(entry.content)
            
            response_parts.append("\nThis workflow should help you accomplish your goal. Let me know if you need clarification on any step!")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating workflow response: {e}")
            return self._generate_fallback_response(query)
    
    def _generate_troubleshooting_response(self, query: UserQuery, relevant_entries: List[KnowledgeBaseEntry]) -> str:
        """Generate a troubleshooting-focused response."""
        try:
            response_parts = [
                f"Here are solutions for the issue you're experiencing:"
            ]
            
            for entry in relevant_entries:
                response_parts.append(f"\n**{entry.title}**")
                response_parts.append(entry.content)
            
            response_parts.append("\nTry these solutions in order. If the issue persists, please provide more details about the error.")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating troubleshooting response: {e}")
            return self._generate_fallback_response(query)
    
    def _generate_best_practices_response(self, query: UserQuery, relevant_entries: List[KnowledgeBaseEntry]) -> str:
        """Generate a best practices-focused response."""
        try:
            response_parts = [
                f"Here are best practices related to your query:"
            ]
            
            for entry in relevant_entries:
                response_parts.append(f"\n**{entry.title}**")
                response_parts.append(entry.content)
            
            response_parts.append("\nFollowing these best practices will help ensure successful outcomes.")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating best practices response: {e}")
            return self._generate_fallback_response(query)
    
    def _generate_general_response(self, query: UserQuery, relevant_entries: List[KnowledgeBaseEntry]) -> str:
        """Generate a general response."""
        try:
            response_parts = [
                f"Here's information that should help with your query:"
            ]
            
            for entry in relevant_entries:
                response_parts.append(f"\n**{entry.title}**")
                response_parts.append(entry.content)
            
            response_parts.append("\nI hope this information is helpful. Let me know if you need further clarification!")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating general response: {e}")
            return self._generate_fallback_response(query)
    
    def _determine_response_type(self, query_type: QueryType) -> ResponseType:
        """Determine the appropriate response type based on query type."""
        try:
            response_type_mapping = {
                QueryType.GENERAL_HELP: ResponseType.DIRECT_ANSWER,
                QueryType.WORKFLOW_GUIDANCE: ResponseType.STEP_BY_STEP,
                QueryType.TECHNICAL_SUPPORT: ResponseType.ERROR_SOLUTION,
                QueryType.FEATURE_EXPLANATION: ResponseType.DIRECT_ANSWER,
                QueryType.ERROR_TROUBLESHOOTING: ResponseType.ERROR_SOLUTION,
                QueryType.BEST_PRACTICES: ResponseType.BEST_PRACTICE_TIP,
                QueryType.TUTORIAL_REQUEST: ResponseType.TUTORIAL_CONTENT,
                QueryType.REFERENCE_LOOKUP: ResponseType.REFERENCE_LINK
            }
            
            return response_type_mapping.get(query_type, ResponseType.DIRECT_ANSWER)
            
        except Exception as e:
            self.logger.error(f"Error determining response type: {e}")
            return ResponseType.DIRECT_ANSWER
    
    async def create_workflow_guide(self, title: str, description: str, steps: List[Dict[str, Any]]) -> WorkflowGuide:
        """Create a new workflow guide."""
        try:
            workflow_steps = []
            total_time = 0
            
            for i, step_data in enumerate(steps, 1):
                step = WorkflowStep(
                    step_id=str(uuid.uuid4()),
                    step_number=i,
                    step_title=step_data.get('title', f'Step {i}'),
                    step_description=step_data.get('description', ''),
                    step_instructions=step_data.get('instructions', []),
                    expected_outcome=step_data.get('expected_outcome', ''),
                    prerequisites=step_data.get('prerequisites', []),
                    estimated_time=step_data.get('estimated_time', 15)
                )
                
                workflow_steps.append(step)
                total_time += step.estimated_time
            
            guide = WorkflowGuide(
                guide_id=str(uuid.uuid4()),
                guide_title=title,
                guide_description=description,
                workflow_steps=workflow_steps,
                total_estimated_time=total_time,
                difficulty_level='medium',  # Default
                prerequisites=[],
                created_date=datetime.utcnow()
            )
            
            # Store guide
            self.workflow_guides[guide.guide_id] = guide
            
            self.logger.info(f"Created workflow guide: {guide.guide_id} - {title}")
            
            return guide
            
        except Exception as e:
            self.logger.error(f"Error creating workflow guide: {e}")
            raise
    
    async def _update_knowledge_base(self):
        """Update the knowledge base."""
        while True:
            try:
                # This would update knowledge base from external sources
                # For now, just log activity
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                self.logger.error(f"Error updating knowledge base: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old data and queries."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=30)  # Keep 30 days of data
                
                # Clean up old queries
                old_queries = [
                    query_id for query_id, query in self.user_queries.items()
                    if query.timestamp < cutoff_time
                ]
                
                for query_id in old_queries:
                    del self.user_queries[query_id]
                
                # Clean up old responses
                old_responses = [
                    response_id for response_id, response in self.help_responses.items()
                    if response.generated_timestamp < cutoff_time
                ]
                
                for response_id in old_responses:
                    del self.help_responses[response_id]
                
                if old_queries or old_responses:
                    self.logger.info(f"Cleaned up {len(old_queries)} old queries and {len(old_responses)} old responses")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _initialize_help_components(self):
        """Initialize help components."""
        try:
            # Initialize default components
            await self._initialize_default_components()
            
            self.logger.info("Help components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing help components: {e}")
    
    async def _initialize_default_components(self):
        """Initialize default help components."""
        try:
            # This would initialize default components
            # For now, just log initialization
            self.logger.info("Default help components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing default components: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_queries_processed': self.total_queries_processed,
            'total_responses_generated': self.total_responses_generated,
            'average_response_time': self.average_response_time,
            'query_types_supported': [t.value for t in QueryType],
            'response_types_supported': [t.value for t in ResponseType],
            'total_knowledge_entries': len(self.knowledge_entries),
            'total_workflow_guides': len(self.workflow_guides),
            'knowledge_base_path': self.knowledge_base_path,
            'similarity_threshold': self.similarity_threshold
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'knowledge_base_path': './knowledge_base',
        'max_response_length': 2000,
        'similarity_threshold': 0.7,
        'max_retrieved_entries': 5
    }
    
    # Initialize help agent
    agent = HelpAgent(config)
    
    print("HelpAgent system initialized successfully!")
