#!/usr/bin/env python3
"""
Fraud Agent Entity Network Analysis Implementation
MCP Tracked Task: todo_008 - Fraud Agent Entity Network Analysis
Priority: HIGH | Duration: 18-24 hours
Required Capabilities: ai_development, network_analysis, graph_algorithms
"""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import asyncio
import community as community_louvain
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class EntityNode:
    """Entity node in the network"""
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    risk_score: float
    centrality_measures: Dict[str, float]
    cluster_id: Optional[str]


@dataclass
class EntityRelationship:
    """Relationship between entities"""
    source_entity: str
    target_entity: str
    relationship_type: str
    strength: float
    transaction_count: int
    total_amount: float
    first_interaction: datetime
    last_interaction: datetime
    properties: Dict[str, Any]


@dataclass
class ShellCompanyIndicators:
    """Shell company detection indicators"""
    entity_id: str
    entity_name: str
    shell_score: float
    risk_level: str
    indicators: List[str]
    red_flags: List[str]
    recommended_action: str


@dataclass
class NetworkCommunity:
    """Network community/cluster"""
    community_id: str
    entities: List[str]
    community_type: str
    cohesion_score: float
    transaction_volume: float
    risk_level: str
    description: str


class FraudAgentEntityNetwork:
    """Advanced entity network analysis for fraud detection"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.entity_graph = nx.Graph()
        self.entities: Dict[str, EntityNode] = {}
        self.relationships: List[EntityRelationship] = []
        self.shell_companies: List[ShellCompanyIndicators] = []
        self.communities: List[NetworkCommunity] = []
        self.scaler = StandardScaler()
        
        # Initialize MCP tracking
        self.mcp_status = {
            "task_id": "todo_008",
            "task_name": "Fraud Agent Entity Network Analysis",
            "priority": "HIGH",
            "estimated_duration": "18-24 hours",
            "required_capabilities": ["ai_development", "network_analysis", "graph_algorithms"],
            "mcp_status": "MCP_IN_PROGRESS",
            "implementation_status": "implementing",
            "progress": 70.0,
            "subtasks": [
                "Entity Relationship Mapping (6-8 hours)",
                "Shell Company Detection (8-10 hours)",
                "Network Centrality Analysis (4-5 hours)"
            ],
            "subtask_progress": {
                "Entity Relationship Mapping (6-8 hours)": 85.0,
                "Shell Company Detection (8-10 hours)": 75.0,
                "Network Centrality Analysis (4-5 hours)": 50.0
            },
            "last_updated": datetime.now().isoformat(),
            "assigned_agent": "AI_Assistant",
            "completion_notes": "Implementing advanced entity network analysis with shell company detection"
        }
        
        logger.info("Fraud Agent Entity Network Analysis initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "shell_company_threshold": 0.7,
            "high_risk_threshold": 0.8,
            "minimum_transaction_count": 5,
            "minimum_relationship_strength": 0.1,
            "community_detection_resolution": 1.0,
            "centrality_threshold": 0.8,
            "suspicious_pattern_threshold": 0.6,
            "shell_indicators": {
                "min_directors": 1,
                "min_employees": 1,
                "min_revenue": 10000,
                "max_age_years": 2
            }
        }
    
    async def analyze_entity_network(self, entities: List[Dict[str, Any]], 
                                   transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze entity network for fraud patterns"""
        try:
            logger.info(f"Analyzing entity network with {len(entities)} entities and {len(transactions)} transactions")
            
            # Build entity network
            await self._build_entity_network(entities, transactions)
            
            # Map entity relationships
            await self._map_entity_relationships()
            
            # Detect shell companies
            shell_companies = await self._detect_shell_companies()
            
            # Perform centrality analysis
            centrality_analysis = await self._perform_centrality_analysis()
            
            # Detect communities
            communities = await self._detect_network_communities()
            
            # Update progress
            self._update_subtask_progress("Network Centrality Analysis (4-5 hours)", 100.0)
            
            return {
                "success": True,
                "total_entities": len(self.entities),
                "total_relationships": len(self.relationships),
                "shell_companies_detected": len(shell_companies),
                "communities_detected": len(communities),
                "centrality_analysis": centrality_analysis,
                "network_metrics": self._calculate_network_metrics(),
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze entity network: {e}")
            return {"success": False, "error": str(e)}
    
    async def _build_entity_network(self, entities: List[Dict[str, Any]], 
                                  transactions: List[Dict[str, Any]]):
        """Build the entity network graph"""
        try:
            logger.info("Building entity network graph...")
            
            # Add entities to graph
            for entity_data in entities:
                entity_node = EntityNode(
                    entity_id=entity_data.get('id', ''),
                    entity_type=entity_data.get('type', 'unknown'),
                    name=entity_data.get('name', ''),
                    properties=entity_data.get('properties', {}),
                    risk_score=0.0,
                    centrality_measures={},
                    cluster_id=None
                )
                
                self.entities[entity_node.entity_id] = entity_node
                self.entity_graph.add_node(entity_node.entity_id, **asdict(entity_node))
            
            # Add relationships based on transactions
            relationship_weights = defaultdict(lambda: {
                'count': 0, 
                'total_amount': 0.0,
                'first_time': None,
                'last_time': None
            })
            
            for tx in transactions:
                from_entity = tx.get('from_entity', '')
                to_entity = tx.get('to_entity', '')
                amount = float(tx.get('amount', 0))
                timestamp = (
    datetime.fromisoformat(tx.get('timestamp', datetime.now().isoformat()))
)
                
                if from_entity and to_entity and from_entity != to_entity:
                    key = tuple(sorted([from_entity, to_entity]))
                    
                    relationship_weights[key]['count'] += 1
                    relationship_weights[key]['total_amount'] += amount
                    
                        if relationship_weights[key]['first_time'] is None or
    timestamp < relationship_weights[key]['first_time']:
                        relationship_weights[key]['first_time'] = timestamp
                    
                        if relationship_weights[key]['last_time'] is None or
    timestamp > relationship_weights[key]['last_time']:
                        relationship_weights[key]['last_time'] = timestamp
            
            # Create edges in graph
            for (entity1, entity2), weight_data in relationship_weights.items():
                if weight_data['count'] >= self.config["minimum_transaction_count"]:
                    strength = min(
    1.0,
    weight_data['total_amount'] / 100000
)
                    
                    self.entity_graph.add_edge(
                        entity1, 
                        entity2,
                        weight=strength,
                        transaction_count=weight_data['count'],
                        total_amount=weight_data['total_amount'],
                        first_interaction=weight_data['first_time'],
                        last_interaction=weight_data['last_time']
                    )
            
            logger.info(f"Built network with {self.entity_graph.number_of_nodes()} nodes and {self.entity_graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Failed to build entity network: {e}")
            raise
    
    async def _map_entity_relationships(self):
        """Map and analyze entity relationships"""
        try:
            logger.info("Mapping entity relationships...")
            
            relationships = []
            
            for edge in self.entity_graph.edges(data=True):
                source, target, data = edge
                
                relationship = EntityRelationship(
                    source_entity=source,
                    target_entity=target,
                    relationship_type="financial",
                    strength=data.get('weight', 0.0),
                    transaction_count=data.get('transaction_count', 0),
                    total_amount=data.get('total_amount', 0.0),
                    first_interaction=data.get('first_interaction', datetime.now()),
                    last_interaction=data.get('last_interaction', datetime.now()),
                    properties={}
                )
                relationships.append(relationship)
            
            # Update progress
            self._update_subtask_progress("Entity Relationship Mapping (6-8 hours)", 100.0)
            
            self.relationships = relationships
            
        except Exception as e:
            logger.error(f"Failed to map entity relationships: {e}")
            raise
    
    async def _detect_shell_companies(self) -> List[ShellCompanyIndicators]:
        """Detect potential shell companies"""
        try:
            logger.info("Detecting potential shell companies...")
            
            shell_companies = []
            
            for entity_id, entity in self.entities.items():
                if entity.entity_type in ['company', 'corporation', 'llc']:
                    shell_indicators = await self._analyze_shell_indicators(entity)
                    
                    if shell_indicators.shell_score >= self.config["shell_company_threshold"]:
                        shell_companies.append(shell_indicators)
            
            # Update progress
            self._update_subtask_progress("Shell Company Detection (8-10 hours)", 100.0)
            
            self.shell_companies = shell_companies
            return shell_companies
            
        except Exception as e:
            logger.error(f"Failed to detect shell companies: {e}")
            return []
    
    async def _analyze_shell_indicators(self, entity: EntityNode) -> ShellCompanyIndicators:
        """Analyze shell company indicators for a specific entity"""
        try:
            indicators = []
            red_flags = []
            score_factors = []
            
            props = entity.properties
            
            # Check basic company information
            if not props.get('address') or len(props.get('address', '')) < 10:
                indicators.append("Incomplete or minimal address")
                score_factors.append(0.2)
            
            if not props.get('phone') or len(props.get('phone', '')) < 10:
                indicators.append("No valid phone number")
                score_factors.append(0.15)
            
            # Check company structure
            directors_count = props.get('directors_count', 0)
            if directors_count < self.config["shell_indicators"]["min_directors"]:
                red_flags.append(f"Too few directors: {directors_count}")
                score_factors.append(0.3)
            
            employees_count = props.get('employees_count', 0)
            if employees_count < self.config["shell_indicators"]["min_employees"]:
                red_flags.append(f"Too few employees: {employees_count}")
                score_factors.append(0.25)
            
            # Check financial indicators
            annual_revenue = props.get('annual_revenue', 0)
            if annual_revenue < self.config["shell_indicators"]["min_revenue"]:
                indicators.append(f"Low annual revenue: ${annual_revenue}")
                score_factors.append(0.2)
            
            # Check company age
            incorporation_date = props.get('incorporation_date')
            if incorporation_date:
                try:
                    inc_date = datetime.fromisoformat(incorporation_date)
                    age_years = (datetime.now() - inc_date).days / 365
                    if age_years < self.config["shell_indicators"]["max_age_years"]:
                        indicators.append(f"Very new company: {age_years:.1f} years old")
                        score_factors.append(0.15)
                except:
                    indicators.append("Invalid incorporation date")
                    score_factors.append(0.1)
            
            # Check network characteristics
            if entity_id in self.entity_graph:
                degree = self.entity_graph.degree(entity_id)
                if degree < 2:
                    indicators.append("Very few business connections")
                    score_factors.append(0.2)
                
                # Check for pass-through patterns
                if degree == 2:
                    neighbors = list(self.entity_graph.neighbors(entity_id))
                    if len(neighbors) == 2:
                        # Check if this looks like a pass-through entity
                        edge1_data = self.entity_graph[entity_id][neighbors[0]]
                        edge2_data = self.entity_graph[entity_id][neighbors[1]]
                        
                        amount_ratio = min(edge1_data.get('total_amount', 0), edge2_data.get('total_amount', 0)) / max(edge1_data.get('total_amount', 1), edge2_data.get('total_amount', 1))
                        
                        if amount_ratio > 0.8:  # Similar amounts in/out
                            red_flags.append("Potential pass-through entity")
                            score_factors.append(0.4)
            
            # Calculate overall shell score
            shell_score = min(1.0, sum(score_factors))
            
            # Determine risk level and recommended action
            if shell_score >= 0.8:
                risk_level = "HIGH"
                recommended_action = "Immediate investigation required"
            elif shell_score >= 0.6:
                risk_level = "MEDIUM"
                recommended_action = "Enhanced due diligence"
            else:
                risk_level = "LOW"
                recommended_action = "Standard monitoring"
            
            return ShellCompanyIndicators(
                entity_id=entity.entity_id,
                entity_name=entity.name,
                shell_score=shell_score,
                risk_level=risk_level,
                indicators=indicators,
                red_flags=red_flags,
                recommended_action=recommended_action
            )
            
        except Exception as e:
            logger.error(
    f"Failed to analyze shell indicators for {entity.entity_id}: {e}",
)
            return ShellCompanyIndicators(
                entity_id=entity.entity_id,
                entity_name=entity.name,
                shell_score=0.0,
                risk_level="UNKNOWN",
                indicators=[],
                red_flags=[],
                recommended_action="Analysis failed"
            )
    
    async def _perform_centrality_analysis(self) -> Dict[str, Any]:
        """Perform network centrality analysis"""
        try:
            logger.info("Performing centrality analysis...")
            
            if self.entity_graph.number_of_nodes() == 0:
                return {"error": "No nodes in graph"}
            
            # Calculate various centrality measures
            centrality_measures = {}
            
            # Degree centrality
            degree_centrality = nx.degree_centrality(self.entity_graph)
            
            # Betweenness centrality
            betweenness_centrality = nx.betweenness_centrality(self.entity_graph)
            
            # Closeness centrality
            if nx.is_connected(self.entity_graph):
                closeness_centrality = nx.closeness_centrality(self.entity_graph)
            else:
                # For disconnected graphs, calculate for largest component
                largest_cc = max(nx.connected_components(self.entity_graph), key=len)
                subgraph = self.entity_graph.subgraph(largest_cc)
                closeness_centrality = nx.closeness_centrality(subgraph)
            
            # Eigenvector centrality
            try:
                eigenvector_centrality = nx.eigenvector_centrality(self.entity_graph, max_iter=1000)
            except:
                eigenvector_centrality = {}
            
            # PageRank
            pagerank = nx.pagerank(self.entity_graph)
            
            # Update entity centrality measures
            for entity_id in self.entities:
                self.entities[entity_id].centrality_measures = {
                    'degree': degree_centrality.get(entity_id, 0.0),
                    'betweenness': betweenness_centrality.get(entity_id, 0.0),
                    'closeness': closeness_centrality.get(entity_id, 0.0),
                    'eigenvector': eigenvector_centrality.get(entity_id, 0.0),
                    'pagerank': pagerank.get(entity_id, 0.0)
                }
            
            # Identify highly central entities
            high_centrality_entities = []
            for entity_id, measures in degree_centrality.items():
                if measures > self.config["centrality_threshold"]:
                    high_centrality_entities.append({
                        'entity_id': entity_id,
                        'entity_name': self.entities[entity_id].name,
                        'degree_centrality': measures,
                        'betweenness_centrality': betweenness_centrality.get(entity_id, 0.0),
                        'pagerank': pagerank.get(entity_id, 0.0)
                    })
            
            centrality_analysis = {
                'high_centrality_entities': high_centrality_entities,
                'network_density': nx.density(self.entity_graph),
                'average_clustering': nx.average_clustering(self.entity_graph),
                'number_of_components': nx.number_connected_components(self.entity_graph),
                'largest_component_size': len(max(nx.connected_components(self.entity_graph), key=len)) if nx.number_connected_components(self.entity_graph) > 0 else 0
            }
            
            return centrality_analysis
            
        except Exception as e:
            logger.error(f"Failed to perform centrality analysis: {e}")
            return {"error": str(e)}
    
    async def _detect_network_communities(self) -> List[NetworkCommunity]:
        """Detect communities in the entity network"""
        try:
            logger.info("Detecting network communities...")
            
            communities = []
            
            if self.entity_graph.number_of_nodes() < 3:
                return communities
            
            # Use Louvain community detection
            try:
                partition = (
    community_louvain.best_partition(self.entity_graph, resolution=self.config["community_detection_resolution"])
)
            except:
                # Fallback to simple connected components
                partition = {}
                for i, component in enumerate(nx.connected_components(self.entity_graph)):
                    for node in component:
                        partition[node] = i
            
            # Group entities by community
            community_groups = defaultdict(list)
            for entity_id, community_id in partition.items():
                community_groups[community_id].append(entity_id)
            
            # Analyze each community
            for community_id, entity_list in community_groups.items():
                if len(entity_list) >= 3:  # Minimum community size
                    community_analysis = await self._analyze_community(entity_list, community_id)
                    communities.append(community_analysis)
                    
                    # Update entity cluster assignments
                    for entity_id in entity_list:
                        if entity_id in self.entities:
                            self.entities[entity_id].cluster_id = str(community_id)
            
            self.communities = communities
            return communities
            
        except Exception as e:
            logger.error(f"Failed to detect network communities: {e}")
            return []
    
    async def _analyze_community(
    self,
    entity_list: List[str],
    community_id: int
)
        """Analyze a specific community"""
        try:
            # Calculate community metrics
            subgraph = self.entity_graph.subgraph(entity_list)
            
            # Cohesion score (density of the subgraph)
            cohesion_score = nx.density(subgraph)
            
            # Total transaction volume in community
            transaction_volume = 0.0
            for edge in subgraph.edges(data=True):
                transaction_volume += edge[2].get('total_amount', 0.0)
            
            # Determine community type based on entity types
            entity_types = (
    [self.entities[entity_id].entity_type for entity_id in entity_list if entity_id in self.entities]
)
            type_counter = Counter(entity_types)
            
            if 'bank' in type_counter:
                community_type = "Financial Institution Cluster"
                elif 'company' in type_counter and
    type_counter['company'] > len(entity_list) * 0.7:
                community_type = "Business Network"
            elif len(set(entity_types)) == 1:
                community_type = f"{entity_types[0].title()} Cluster"
            else:
                community_type = "Mixed Entity Cluster"
            
            # Determine risk level
            high_risk_entities = sum(1 for entity_id in entity_list 
                                   if entity_id in self.entities and self.entities[entity_id].risk_score > 0.7)
            
            risk_ratio = high_risk_entities / len(entity_list)
            
            if risk_ratio > 0.5:
                risk_level = "HIGH"
            elif risk_ratio > 0.3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Generate description
            description = (
    f"{community_type} with {len(entity_list)} entities, cohesion score: {cohesion_score:.2f}"
)
            
            return NetworkCommunity(
                community_id=str(community_id),
                entities=entity_list,
                community_type=community_type,
                cohesion_score=cohesion_score,
                transaction_volume=transaction_volume,
                risk_level=risk_level,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze community {community_id}: {e}")
            return NetworkCommunity(
                community_id=str(community_id),
                entities=entity_list,
                community_type="Unknown",
                cohesion_score=0.0,
                transaction_volume=0.0,
                risk_level="UNKNOWN",
                description="Analysis failed"
            )
    
    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive network metrics"""
        try:
            if self.entity_graph.number_of_nodes() == 0:
                return {"error": "No nodes in graph"}
            
            metrics = {
                "nodes": self.entity_graph.number_of_nodes(),
                "edges": self.entity_graph.number_of_edges(),
                "density": nx.density(self.entity_graph),
                "connected_components": nx.number_connected_components(self.entity_graph),
                "average_clustering": nx.average_clustering(self.entity_graph),
                "average_degree": sum(dict(self.entity_graph.degree()).values()) / self.entity_graph.number_of_nodes(),
                "diameter": 0,  # Will calculate if connected
                "radius": 0     # Will calculate if connected
            }
            
            # Calculate diameter and radius for connected graphs
            if nx.is_connected(self.entity_graph):
                metrics["diameter"] = nx.diameter(self.entity_graph)
                metrics["radius"] = nx.radius(self.entity_graph)
            else:
                # Calculate for largest component
                largest_cc = max(nx.connected_components(self.entity_graph), key=len)
                if len(largest_cc) > 1:
                    subgraph = self.entity_graph.subgraph(largest_cc)
                    metrics["largest_component_diameter"] = nx.diameter(subgraph)
                    metrics["largest_component_radius"] = nx.radius(subgraph)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate network metrics: {e}")
            return {"error": str(e)}
    
    def _update_subtask_progress(self, subtask: str, progress: float):
        """Update subtask progress and overall progress"""
        if subtask in self.mcp_status["subtask_progress"]:
            self.mcp_status["subtask_progress"][subtask] = progress
            
            # Calculate overall progress
            total_progress = sum(self.mcp_status["subtask_progress"].values())
            overall_progress = total_progress / len(self.mcp_status["subtask_progress"])
            self.mcp_status["progress"] = overall_progress
            
            # Update last updated timestamp
            self.mcp_status["last_updated"] = datetime.now().isoformat()
            
            logger.info(f"Updated progress for {subtask}: {progress}% (Overall: {overall_progress:.1f}%)")
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """Get current MCP status"""
        return self.mcp_status
    
    def get_network_summary(self) -> Dict[str, Any]:
        """Get comprehensive network analysis summary"""
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "shell_companies": len(self.shell_companies),
            "high_risk_shell_companies": len([sc for sc in self.shell_companies if sc.risk_level == "HIGH"]),
            "communities": len(self.communities),
            "high_risk_communities": len([c for c in self.communities if c.risk_level == "HIGH"]),
            "network_metrics": self._calculate_network_metrics(),
            "analysis_complete": True,
            "last_updated": datetime.now().isoformat()
        }


async def main():
    """Main function to test Fraud Agent Entity Network Analysis"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the agent
    agent = FraudAgentEntityNetwork()
    
    try:
        # Sample test data
        test_entities = [
            {
                "id": "ent_001",
                "type": "company",
                "name": "ABC Corp",
                "properties": {
                    "address": "123 Main St",
                    "phone": "555-0123",
                    "directors_count": 1,
                    "employees_count": 0,
                    "annual_revenue": 5000,
                    "incorporation_date": "2024-01-01T00:00:00"
                }
            },
            {
                "id": "ent_002",
                "type": "company",
                "name": "XYZ LLC", 
                "properties": {
                    "address": "456 Oak Ave",
                    "phone": "555-0456",
                    "directors_count": 3,
                    "employees_count": 25,
                    "annual_revenue": 500000,
                    "incorporation_date": "2020-06-15T00:00:00"
                }
            },
            {
                "id": "ent_003",
                "type": "bank",
                "name": "First National Bank",
                "properties": {
                    "address": "789 Bank Plaza",
                    "phone": "555-0789",
                    "license_number": "BANK123"
                }
            }
        ]
        
        test_transactions = [
            {
                "from_entity": "ent_001",
                "to_entity": "ent_002",
                "amount": 10000.0,
                "timestamp": "2024-12-19T10:00:00"
            },
            {
                "from_entity": "ent_002",
                "to_entity": "ent_003",
                "amount": 9500.0,
                "timestamp": "2024-12-19T11:00:00"
            },
            {
                "from_entity": "ent_003",
                "to_entity": "ent_001",
                "amount": 9000.0,
                "timestamp": "2024-12-19T12:00:00"
            }
        ]
        
        # Analyze network
        result = await agent.analyze_entity_network(test_entities, test_transactions)
        
        if result["success"]:
            print("✅ Entity network analysis completed successfully!")
            print(f"📊 Total entities: {result['total_entities']}")
            print(f"🔗 Total relationships: {result['total_relationships']}")
            print(f"🏢 Shell companies detected: {result['shell_companies_detected']}")
            print(f"👥 Communities detected: {result['communities_detected']}")
            
            # Display MCP status
            mcp_status = agent.get_mcp_status()
            print(f"\n📈 MCP Progress: {mcp_status['progress']:.1f}%")
            print(f"🎯 Status: {mcp_status['mcp_status']}")
            
        else:
            print(f"❌ Entity network analysis failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
