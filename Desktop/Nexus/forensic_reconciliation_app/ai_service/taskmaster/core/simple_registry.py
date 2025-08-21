"""
Simple Task Registry - Prevents overlapping implementations
Enhanced with Priority TODO Tracking and Overlap Prevention
"""

import hashlib
import logging
from typing import Dict, Set, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SimpleTaskRegistry:
    """Simple registry to prevent duplicate task implementations"""
    
    def __init__(self):
        self.registered_tasks: Dict[str, str] = {}  # task_hash -> agent_id
        self.task_dependencies: Dict[str, Set[str]] = {}
        self.task_status: Dict[str, Dict[str, Any]] = {}  # task_id -> status info
        self.priority_todos: List[Dict[str, Any]] = []
        self.agent_workloads: Dict[str, List[str]] = {}  # agent_id -> task_ids
        
        # Initialize with priority TODO items
        self._initialize_priority_todos()
    
    def _initialize_priority_todos(self):
        """Initialize with the next 10 priority TODO items and their subtasks - Updated Status"""
        self.priority_todos = [
            {
                "id": "todo_001",
                "name": "DuckDB OLAP Engine Setup",
                "description": "Configure DuckDB OLAP engine for high-performance reconciliation processing",
                "priority": "HIGH",
                "estimated_duration": "4-6 hours",
                "required_capabilities": ["database_setup", "olap_configuration", "performance_optimization"],
                "status": "completed",
                "assigned_agent": "AI_Assistant",
                "progress": 100.0,
                "implementation_status": "implemented",
                "task_type": "simple_task",
                "subtasks": [],
                "subtask_count": 0,
                "subtask_progress": {},
                "mcp_status": "MCP_COMPLETED",
                "last_updated": "2024-12-19",
                "completion_notes": "Full DuckDB implementation completed with OLAP configuration, data warehouse schemas, materialized views, data partitioning, performance indexes, and comprehensive testing"
            },
            {
                "id": "todo_002", 
                "name": "Multi-Factor Authentication Implementation",
                "description": "Implement TOTP, SMS, and hardware token support for enhanced security",
                "priority": "CRITICAL",
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["security", "authentication", "mfa_implementation"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "TOTP Service Implementation (3-4 hours)",
                    "SMS Service Integration (2-3 hours)",
                    "Hardware Token Support (2-3 hours)",
                    "MFA Configuration Management (1-2 hours)"
                ],
                "subtask_count": 4,
                "subtask_progress": {
                    "TOTP Service Implementation (3-4 hours)": 0.0,
                    "SMS Service Integration (2-3 hours)": 0.0,
                    "Hardware Token Support (2-3 hours)": 0.0,
                    "MFA Configuration Management (1-2 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_003",
                "name": "End-to-End Encryption Setup", 
                "description": "Implement AES-256 encryption for sensitive data with secure key management",
                "priority": "CRITICAL",
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["security", "encryption", "key_management"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "AES-256 Encryption Core (3-4 hours)",
                    "Key Management System (2-3 hours)",
                    "Encryption Pipeline Integration (1-2 hours)"
                ],
                "subtask_count": 3,
                "subtask_progress": {
                    "AES-256 Encryption Core (3-4 hours)": 0.0,
                    "Key Management System (2-3 hours)": 0.0,
                    "Encryption Pipeline Integration (1-2 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_004",
                "name": "Load Balancing Strategies Implementation",
                "description": "Implement advanced load balancing strategies for optimal agent distribution", 
                "priority": "HIGH",
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["python_development", "load_balancing", "algorithm_implementation"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "medium_task",
                "subtasks": [],
                "subtask_count": 0,
                "subtask_progress": {},
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_005",
                "name": "Queue Monitoring and Metrics",
                "description": "Set up comprehensive queue monitoring and performance metrics",
                "priority": "HIGH", 
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["python_development", "monitoring", "metrics"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "medium_task",
                "subtasks": [],
                "subtask_count": 0,
                "subtask_progress": {},
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_006",
                "name": "Reconciliation Agent AI Fuzzy Matching",
                "description": "Implement AI-powered fuzzy matching and outlier detection for reconciliation",
                "priority": "HIGH",
                "estimated_duration": "16-20 hours", 
                "required_capabilities": ["python_development", "machine_learning", "algorithm_implementation"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "Fuzzy Matching Algorithm Core (4-5 hours)",
                    "AI-Powered Similarity Scoring (6-8 hours)",
                    "Outlier Detection System (4-5 hours)",
                    "Confidence Scoring Engine (2-3 hours)"
                ],
                "subtask_count": 4,
                "subtask_progress": {
                    "Fuzzy Matching Algorithm Core (4-5 hours)": 0.0,
                    "AI-Powered Similarity Scoring (6-8 hours)": 0.0,
                    "Outlier Detection System (4-5 hours)": 0.0,
                    "Confidence Scoring Engine (2-3 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_007",
                "name": "Fraud Agent Pattern Detection", 
                "description": "Build entity network analysis and circular transaction detection algorithms",
                "priority": "HIGH",
                "estimated_duration": "24-32 hours",
                "required_capabilities": ["python_development", "graph_algorithms", "fraud_detection"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "Circular Transaction Detection (8-10 hours)",
                    "Transaction Flow Analysis (6-8 hours)",
                    "Pattern Recognition Engine (6-8 hours)",
                    "Alert Generation System (4-5 hours)"
                ],
                "subtask_count": 4,
                "subtask_progress": {
                    "Circular Transaction Detection (8-10 hours)": 0.0,
                    "Transaction Flow Analysis (6-8 hours)": 0.0,
                    "Pattern Recognition Engine (6-8 hours)": 0.0,
                    "Alert Generation System (4-5 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_008",
                "name": "Fraud Agent Entity Network Analysis",
                "description": "Implement advanced entity network analysis and shell company identification",
                "priority": "HIGH",
                "estimated_duration": "18-24 hours",
                "required_capabilities": ["python_development", "graph_algorithms", "fraud_detection", "network_analysis"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "Entity Relationship Mapping (6-8 hours)",
                    "Shell Company Detection (8-10 hours)",
                    "Network Centrality Analysis (4-5 hours)"
                ],
                "subtask_count": 3,
                "subtask_progress": {
                    "Entity Relationship Mapping (6-8 hours)": 0.0,
                    "Shell Company Detection (8-10 hours)": 0.0,
                    "Network Centrality Analysis (4-5 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_009",
                "name": "Risk Agent Compliance Engine",
                "description": "Create multi-factor risk assessment with SOX, PCI, AML, GDPR compliance",
                "priority": "HIGH",
                "estimated_duration": "18-24 hours",
                "required_capabilities": ["python_development", "compliance", "risk_assessment"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "SOX Compliance Rules (4-5 hours)",
                    "PCI DSS Compliance Engine (4-5 hours)",
                    "AML Compliance System (4-5 hours)",
                    "GDPR Compliance Engine (4-5 hours)",
                    "Risk Scoring Algorithm (2-3 hours)"
                ],
                "subtask_count": 5,
                "subtask_progress": {
                    "SOX Compliance Rules (4-5 hours)": 0.0,
                    "PCI DSS Compliance Engine (4-5 hours)": 0.0,
                    "AML Compliance System (4-5 hours)": 0.0,
                    "GDPR Compliance Engine (4-5 hours)": 0.0,
                    "Risk Scoring Algorithm (2-3 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            },
            {
                "id": "todo_010",
                "name": "Evidence Agent Processing Pipeline",
                "description": "Build file processing, hash verification, and metadata extraction systems",
                "priority": "NORMAL",
                "estimated_duration": "16-20 hours",
                "required_capabilities": ["python_development", "file_processing", "hash_verification"],
                "status": "pending",
                "assigned_agent": None,
                "progress": 0.0,
                "implementation_status": "unimplemented",
                "task_type": "complex_task",
                "subtasks": [
                    "File Processing Core (4-5 hours)",
                    "Hash Verification System (3-4 hours)",
                    "EXIF Metadata Extraction (3-4 hours)",
                    "PDF OCR Processing (4-5 hours)",
                    "Chat Log NLP Processing (2-3 hours)"
                ],
                "subtask_count": 5,
                "subtask_progress": {
                    "File Processing Core (4-5 hours)": 0.0,
                    "Hash Verification System (3-4 hours)": 0.0,
                    "EXIF Metadata Extraction (3-4 hours)": 0.0,
                    "PDF OCR Processing (4-5 hours)": 0.0,
                    "Chat Log NLP Processing (2-3 hours)": 0.0
                },
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19"
            }
        ]
        
        logger.info(f"Initialized {len(self.priority_todos)} priority TODO items with subtask breakdown")
        total_subtasks = sum(todo.get("subtask_count", 0) for todo in self.priority_todos)
        logger.info(f"Total subtasks: {total_subtasks} across all complex tasks")
        logger.info("All TODO items marked as MCP_TRACKED - Ready for agent assignment")
        logger.info("Overlap prevention system active - No duplicate implementations possible")
    
    def register_task(self, name: str, description: str, agent_id: str) -> bool:
        """Register a task implementation"""
        task_hash = self._generate_hash(name, description)
        
        if task_hash in self.registered_tasks:
            existing_agent = self.registered_tasks[task_hash]
            logger.warning(f"Task already implemented by agent {existing_agent}: {name}")
            return False
        
        self.registered_tasks[task_hash] = agent_id
        
        # Update agent workload
        if agent_id not in self.agent_workloads:
            self.agent_workloads[agent_id] = []
        self.agent_workloads[agent_id].append(task_hash)
        
        logger.info(f"Task registered: {name} by agent {agent_id}")
        return True
    
    def is_task_implemented(self, name: str, description: str) -> bool:
        """Check if a task is already implemented"""
        task_hash = self._generate_hash(name, description)
        return task_hash in self.registered_tasks
    
    def get_implementing_agent(self, name: str, description: str) -> str:
        """Get the agent that implemented a task"""
        task_hash = self._generate_hash(name, description)
        return self.registered_tasks.get(task_hash)
    
    def assign_priority_todo(self, todo_id: str, agent_id: str) -> bool:
        """Assign a priority TODO item to an agent"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id and todo["status"] == "pending":
                todo["assigned_agent"] = agent_id
                todo["status"] = "in_progress"
                todo["assigned_at"] = datetime.now().isoformat()
                
                # Update agent workload
                if agent_id not in self.agent_workloads:
                    self.agent_workloads[agent_id] = []
                self.agent_workloads[agent_id].append(todo_id)
                
                logger.info(f"Priority TODO {todo_id} assigned to agent {agent_id}")
                return True
        
        return False
    
    def update_todo_progress(self, todo_id: str, progress: float, status: str = None) -> bool:
        """Update progress for a priority TODO item"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                todo["progress"] = max(0.0, min(1.0, progress))
                if status:
                    todo["status"] = status
                
                if progress >= 1.0:
                    todo["status"] = "completed"
                    todo["completed_at"] = datetime.now().isoformat()
                
                logger.info(f"Priority TODO {todo_id} progress updated: {progress:.1%}")
                return True
        
        return False
    
    def get_available_todos(self, agent_capabilities: List[str]) -> List[Dict[str, Any]]:
        """Get available priority TODO items for an agent"""
        available = []
        
        for todo in self.priority_todos:
            if todo["status"] == "pending":
                # Check if agent has required capabilities
                if self._agent_can_handle_todo(todo, agent_capabilities):
                    available.append(todo)
        
        # Sort by priority
        priority_order = {"CRITICAL": 5, "HIGH": 4, "NORMAL": 3, "LOW": 2, "MAINTENANCE": 1}
        available.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        return available
    
    def _agent_can_handle_todo(self, todo: Dict[str, Any], agent_capabilities: List[str]) -> bool:
        """Check if agent can handle a specific TODO item"""
        required_capabilities = todo.get("required_capabilities", [])
        if not required_capabilities:
            return True
        
        agent_cap_set = set(agent_capabilities)
        required_cap_set = set(required_capabilities)
        
        # Agent must have at least 70% of required capabilities
        overlap = len(agent_cap_set.intersection(required_cap_set))
        required_count = len(required_cap_set)
        
        return (overlap / required_count) >= 0.7 if required_count > 0 else True
    
    def get_todo_status(self, todo_id: str) -> Dict[str, Any]:
        """Get status of a specific priority TODO item"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                return todo.copy()
        return {}
    
    def get_priority_todo_summary(self) -> Dict[str, Any]:
        """Get summary of all priority TODO items"""
        total = len(self.priority_todos)
        by_status = {}
        by_priority = {}
        
        for todo in self.priority_todos:
            status = todo["status"]
            priority = todo["priority"]
            
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total_todos": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "todos": self.priority_todos
        }
    
    def _generate_hash(self, name: str, description: str) -> str:
        """Generate hash for task identification"""
        content = f"{name}:{description}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_dependency(self, task_id: str, dependency_id: str):
        """Add task dependency"""
        if task_id not in self.task_dependencies:
            self.task_dependencies[task_id] = set()
        self.task_dependencies[task_id].add(dependency_id)
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """Get task dependencies"""
        return self.task_dependencies.get(task_id, set())
    
    def get_agent_workload(self, agent_id: str) -> List[str]:
        """Get current workload for an agent"""
        return self.agent_workloads.get(agent_id, [])
    
    def export_registry(self, filepath: str = None) -> str:
        """Export registry data to file"""
        if not filepath:
            filepath = f"task_registry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "registered_tasks": self.registered_tasks,
                "task_dependencies": {k: list(v) for k, v in self.task_dependencies.items()},
                "priority_todos": self.priority_todos,
                "agent_workloads": self.agent_workloads
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Registry exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export registry: {e}")
            return ""

    def get_unimplemented_todos(self) -> List[Dict[str, Any]]:
        """Get all unimplemented priority TODO items"""
        return [todo for todo in self.priority_todos if todo["implementation_status"] == "unimplemented"]
    
    def get_todo_implementation_status(self, todo_id: str) -> str:
        """Get implementation status of a specific TODO item"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                return todo.get("implementation_status", "unknown")
        return "not_found"
    
    def mark_todo_implemented(self, todo_id: str, agent_id: str, implementation_details: Dict[str, Any] = None) -> bool:
        """Mark a TODO item as implemented"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                todo["implementation_status"] = "implemented"
                todo["implemented_by"] = agent_id
                todo["implemented_at"] = datetime.now().isoformat()
                todo["implementation_details"] = implementation_details or {}
                
                # Also update the main task registry
                self.register_task(todo["name"], todo["description"], agent_id)
                
                logger.info(f"TODO {todo_id} marked as implemented by {agent_id}")
                return True
        return False
    
    def check_implementation_overlap(self, todo_id: str, agent_id: str) -> Dict[str, Any]:
        """Check for potential implementation overlap"""
        overlap_info = {
            "has_overlap": False,
            "overlap_type": None,
            "conflicting_agent": None,
            "details": None
        }
        
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                # Check if already assigned to another agent
                if todo["assigned_agent"] and todo["assigned_agent"] != agent_id:
                    overlap_info.update({
                        "has_overlap": True,
                        "overlap_type": "already_assigned",
                        "conflicting_agent": todo["assigned_agent"],
                        "details": f"TODO {todo_id} already assigned to {todo['assigned_agent']}"
                    })
                    break
                
                # Check if already implemented
                if todo["implementation_status"] == "implemented":
                    overlap_info.update({
                        "has_overlap": True,
                        "overlap_type": "already_implemented",
                        "conflicting_agent": todo.get("implemented_by"),
                        "details": f"TODO {todo_id} already implemented by {todo.get('implemented_by')}"
                    })
                    break
                
                # Check for similar tasks in progress
                similar_todos = [t for t in self.priority_todos 
                               if t["id"] != todo_id and 
                               t["status"] == "in_progress" and
                               self._are_todos_similar(todo, t)]
                
                if similar_todos:
                    overlap_info.update({
                        "has_overlap": True,
                        "overlap_type": "similar_task_in_progress",
                        "conflicting_agent": similar_todos[0]["assigned_agent"],
                        "details": f"Similar task {similar_todos[0]['id']} in progress by {similar_todos[0]['assigned_agent']}"
                    })
                    break
        
        return overlap_info
    
    def _are_todos_similar(self, todo1: Dict[str, Any], todo2: Dict[str, Any]) -> bool:
        """Check if two TODO items are similar enough to cause overlap"""
        # Check name similarity
        name1 = todo1["name"].lower()
        name2 = todo2["name"].lower()
        
        # Check for common keywords that might indicate overlap
        common_keywords = ["agent", "implementation", "setup", "configuration", "development"]
        name_overlap = any(keyword in name1 and keyword in name2 for keyword in common_keywords)
        
        # Check capability overlap
        cap1 = set(todo1.get("required_capabilities", []))
        cap2 = set(todo2.get("required_capabilities", []))
        capability_overlap = len(cap1.intersection(cap2)) > 0
        
        # Check description similarity
        desc1 = todo1["description"].lower()
        desc2 = todo2["description"].lower()
        desc_overlap = any(word in desc1 and word in desc2 
                          for word in ["agent", "implementation", "algorithm", "system"])
        
        return name_overlap or (capability_overlap and desc_overlap)
    
    def get_agent_implementation_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summary of implementations by a specific agent"""
        implemented_todos = [todo for todo in self.priority_todos 
                           if todo.get("implemented_by") == agent_id]
        
        assigned_todos = [todo for todo in self.priority_todos 
                         if todo["assigned_agent"] == agent_id]
        
        return {
            "agent_id": agent_id,
            "implemented_count": len(implemented_todos),
            "assigned_count": len(assigned_todos),
            "implemented_todos": [{"id": t["id"], "name": t["name"], "implemented_at": t.get("implemented_at")} 
                                 for t in implemented_todos],
            "assigned_todos": [{"id": t["id"], "name": t["name"], "status": t["status"], "progress": t["progress"]} 
                              for t in assigned_todos]
        }
    
    def get_implementation_metrics(self) -> Dict[str, Any]:
        """Get overall implementation metrics"""
        total_todos = len(self.priority_todos)
        implemented_todos = len([t for t in self.priority_todos if t["implementation_status"] == "implemented"])
        in_progress_todos = len([t for t in self.priority_todos if t["status"] == "in_progress"])
        pending_todos = len([t for t in self.priority_todos if t["status"] == "pending"])
        
        implementation_rate = (implemented_todos / total_todos * 100) if total_todos > 0 else 0
        
        return {
            "total_todos": total_todos,
            "implemented_todos": implemented_todos,
            "in_progress_todos": in_progress_todos,
            "pending_todos": pending_todos,
            "implementation_rate": round(implementation_rate, 2),
            "last_updated": datetime.now().isoformat()
        }

    def update_subtask_progress(self, todo_id: str, subtask_name: str, progress: float, agent_id: str = None) -> bool:
        """Update progress for a specific subtask"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                if subtask_name in todo.get("subtasks", []):
                    # Update subtask progress
                    if "subtask_progress" not in todo:
                        todo["subtask_progress"] = {}
                    todo["subtask_progress"][subtask_name] = max(0.0, min(1.0, progress))
                    
                    # Update overall progress based on subtask completion
                    if todo["subtask_progress"]:
                        total_progress = sum(todo["subtask_progress"].values())
                        total_subtasks = len(todo["subtasks"])
                        if total_subtasks > 0:
                            todo["progress"] = total_progress / total_subtasks
                    
                    # Log the progress update
                    logger.info(f"Subtask progress updated: {todo_id} - {subtask_name}: {progress:.1%}")
                    
                    # Check if all subtasks are complete
                    if todo["progress"] >= 1.0:
                        todo["status"] = "completed"
                        todo["completed_at"] = datetime.now().isoformat()
                        logger.info(f"TODO {todo_id} completed: {todo['name']}")
                    
                    return True
                else:
                    logger.warning(f"Subtask {subtask_name} not found in TODO {todo_id}")
                    return False
        
        logger.warning(f"TODO {todo_id} not found")
        return False
    
    def get_subtask_status(self, todo_id: str) -> Dict[str, Any]:
        """Get detailed status of subtasks for a TODO item"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                return {
                    "todo_id": todo_id,
                    "name": todo["name"],
                    "overall_progress": todo["progress"],
                    "subtasks": [
                        {
                            "name": subtask,
                            "progress": todo.get("subtask_progress", {}).get(subtask, 0.0),
                            "status": "completed" if todo.get("subtask_progress", {}).get(subtask, 0.0) >= 1.0 else "in_progress"
                        }
                        for subtask in todo.get("subtasks", [])
                    ],
                    "completed_subtasks": len([s for s in todo.get("subtasks", []) 
                                            if todo.get("subtask_progress", {}).get(s, 0.0) >= 1.0]),
                    "total_subtasks": len(todo.get("subtasks", []))
                }
        return {}
    
    def assign_subtask(self, todo_id: str, subtask_name: str, agent_id: str) -> bool:
        """Assign a specific subtask to an agent"""
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                if subtask_name in todo.get("subtasks", []):
                    # Check if subtask is already assigned
                    if "subtask_assignments" not in todo:
                        todo["subtask_assignments"] = {}
                    
                    if subtask_name in todo["subtask_assignments"]:
                        existing_agent = todo["subtask_assignments"][subtask_name]
                        if existing_agent != agent_id:
                            logger.warning(f"Subtask {subtask_name} already assigned to {existing_agent}")
                            return False
                    
                    # Assign the subtask
                    todo["subtask_assignments"][subtask_name] = agent_id
                    logger.info(f"Subtask {subtask_name} assigned to {agent_id} for TODO {todo_id}")
                    return True
                else:
                    logger.warning(f"Subtask {subtask_name} not found in TODO {todo_id}")
                    return False
        
        logger.warning(f"TODO {todo_id} not found")
        return False
    
    def check_subtask_overlap(self, todo_id: str, subtask_name: str, agent_id: str) -> Dict[str, Any]:
        """Check for potential overlap when assigning subtasks"""
        overlap_info = {
            "has_overlap": False,
            "overlap_type": None,
            "conflicting_agent": None,
            "details": None
        }
        
        for todo in self.priority_todos:
            if todo["id"] == todo_id:
                if subtask_name in todo.get("subtasks", []):
                    # Check if subtask is already assigned to another agent
                    if "subtask_assignments" in todo and subtask_name in todo["subtask_assignments"]:
                        assigned_agent = todo["subtask_assignments"][subtask_name]
                        if assigned_agent != agent_id:
                            overlap_info.update({
                                "has_overlap": True,
                                "overlap_type": "subtask_already_assigned",
                                "conflicting_agent": assigned_agent,
                                "details": f"Subtask {subtask_name} already assigned to {assigned_agent}"
                            })
                            return overlap_info
                    
                    # Check for similar subtasks in progress by other agents
                    similar_subtasks = self._find_similar_subtasks(todo_id, subtask_name, agent_id)
                    if similar_subtasks:
                        overlap_info.update({
                            "has_overlap": True,
                            "overlap_type": "similar_subtask_in_progress",
                            "conflicting_agent": similar_subtasks[0]["agent_id"],
                            "details": f"Similar subtask {similar_subtasks[0]['name']} in progress by {similar_subtasks[0]['agent_id']}"
                        })
                        return overlap_info
                    
                    return overlap_info
                else:
                    overlap_info.update({
                        "has_overlap": True,
                        "overlap_type": "subtask_not_found",
                        "details": f"Subtask {subtask_name} not found in TODO {todo_id}"
                    })
                    return overlap_info
        
        overlap_info.update({
            "has_overlap": True,
            "overlap_type": "todo_not_found",
            "details": f"TODO {todo_id} not found"
        })
        return overlap_info
    
    def _find_similar_subtasks(self, todo_id: str, subtask_name: str, agent_id: str) -> List[Dict[str, Any]]:
        """Find subtasks similar to the given subtask that might cause overlap"""
        similar_subtasks = []
        
        # Extract keywords from subtask name
        subtask_keywords = set(subtask_name.lower().split())
        
        for todo in self.priority_todos:
            if todo["id"] != todo_id:  # Check other TODOs
                for other_subtask in todo.get("subtasks", []):
                    other_keywords = set(other_subtask.lower().split())
                    
                    # Check for keyword overlap
                    common_keywords = subtask_keywords.intersection(other_keywords)
                    if len(common_keywords) >= 2:  # At least 2 common keywords
                        # Check if this subtask is assigned to a different agent
                        if "subtask_assignments" in todo and other_subtask in todo["subtask_assignments"]:
                            other_agent = todo["subtask_assignments"][other_subtask]
                            if other_agent != agent_id:
                                similar_subtasks.append({
                                    "name": other_subtask,
                                    "agent_id": other_agent,
                                    "todo_id": todo["id"],
                                    "common_keywords": list(common_keywords)
                                })
        
        return similar_subtasks
    
    def get_agent_subtask_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed subtask workload for a specific agent"""
        agent_workload = {
            "agent_id": agent_id,
            "assigned_todos": [],
            "assigned_subtasks": [],
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "overall_progress": 0.0
        }
        
        for todo in self.priority_todos:
            if todo["assigned_agent"] == agent_id:
                agent_workload["assigned_todos"].append({
                    "todo_id": todo["id"],
                    "name": todo["name"],
                    "progress": todo["progress"],
                    "subtask_count": todo.get("subtask_count", 0)
                })
            
            # Check subtask assignments
            if "subtask_assignments" in todo:
                for subtask_name, assigned_agent in todo["subtask_assignments"].items():
                    if assigned_agent == agent_id:
                        subtask_progress = todo.get("subtask_progress", {}).get(subtask_name, 0.0)
                        agent_workload["assigned_subtasks"].append({
                            "todo_id": todo["id"],
                            "todo_name": todo["name"],
                            "subtask_name": subtask_name,
                            "progress": subtask_progress,
                            "status": "completed" if subtask_progress >= 1.0 else "in_progress"
                        })
                        agent_workload["total_subtasks"] += 1
                        if subtask_progress >= 1.0:
                            agent_workload["completed_subtasks"] += 1
        
        # Calculate overall progress
        if agent_workload["total_subtasks"] > 0:
            agent_workload["overall_progress"] = agent_workload["completed_subtasks"] / agent_workload["total_subtasks"]
        
        return agent_workload
    
    def get_breakdown_summary(self) -> Dict[str, Any]:
        """Get summary of task breakdown and subtask distribution"""
        total_todos = len(self.priority_todos)
        simple_tasks = len([t for t in self.priority_todos if t.get("task_type") == "simple_task"])
        medium_tasks = len([t for t in self.priority_todos if t.get("task_type") == "medium_task"])
        complex_tasks = len([t for t in self.priority_todos if t.get("task_type") == "complex_task"])
        
        total_subtasks = sum(t.get("subtask_count", 0) for t in self.priority_todos)
        completed_subtasks = sum(
            len([s for s in t.get("subtasks", []) 
                 if t.get("subtask_progress", {}).get(s, 0.0) >= 1.0])
            for t in self.priority_todos
        )
        
        return {
            "total_todos": total_todos,
            "task_types": {
                "simple": simple_tasks,
                "medium": medium_tasks,
                "complex": complex_tasks
            },
            "subtasks": {
                "total": total_subtasks,
                "completed": completed_subtasks,
                "remaining": total_subtasks - completed_subtasks,
                "completion_rate": round((completed_subtasks / total_subtasks * 100), 2) if total_subtasks > 0 else 0
            },
            "breakdown_benefits": {
                "manageable_units": "Each subtask is 1-10 hours",
                "parallel_development": "Multiple developers can work simultaneously",
                "granular_tracking": "Progress monitoring at subtask level",
                "risk_reduction": "Smaller tasks reduce failure impact"
            }
        }


# Global registry instance
task_registry = SimpleTaskRegistry()
