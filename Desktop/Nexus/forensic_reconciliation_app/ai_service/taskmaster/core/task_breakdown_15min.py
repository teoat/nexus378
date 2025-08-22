"""
Task Breakdown System - Convert Complex TODOs into 15-Minute Manageable Tasks
Enhanced with Time-Based Task Management and Progress Tracking
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import math

logger = logging.getLogger(__name__)


@dataclass
class MicroTask:
    """15-minute manageable task unit"""
    task_id: str
    parent_todo_id: str
    title: str
    description: str
    estimated_minutes: int
    required_capabilities: List[str]
    dependencies: List[str]
    status: str  # pending, in_progress, completed, blocked
    priority: str  # critical, high, medium, low
    assigned_agent: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    actual_minutes: Optional[int]
    notes: str
    complexity_score: int  # 1-5 scale
    tags: List[str]


@dataclass
class TaskBreakdown:
    """Complete breakdown of a complex TODO into micro-tasks"""
    todo_id: str
    todo_name: str
    original_estimated_hours: str
    total_micro_tasks: int
    total_estimated_minutes: int
    micro_tasks: List[MicroTask]
    breakdown_created_at: datetime
    breakdown_version: str
    status: str  # created, in_progress, completed


class TaskBreakdownEngine:
    """Engine for breaking down complex TODOs into 15-minute tasks"""
    
    def __init__(self):
        self.breakdowns: Dict[str, TaskBreakdown] = {}
        self.micro_task_templates = self._load_micro_task_templates()
        
    def _load_micro_task_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load predefined micro-task templates for common TODO types"""
        return {
            "ai_agent_development": [
                {"title": "Core Class Structure", "minutes": 15, "capabilities": ["python_development", "class_design"]},
                {"title": "Method Implementation", "minutes": 15, "capabilities": ["python_development", "algorithm_implementation"]},
                {"title": "Error Handling", "minutes": 15, "capabilities": ["python_development", "error_handling"]},
                {"title": "Unit Tests", "minutes": 15, "capabilities": ["python_development", "testing"]},
                {"title": "Integration Tests", "minutes": 15, "capabilities": ["python_development", "integration_testing"]},
                {"title": "Documentation", "minutes": 15, "capabilities": ["python_development", "documentation"]},
                {"title": "Performance Optimization", "minutes": 15, "capabilities": ["python_development", "performance_optimization"]},
                {"title": "Configuration Management", "minutes": 15, "capabilities": ["python_development", "configuration_management"]}
            ],
            "database_setup": [
                {"title": "Schema Design", "minutes": 15, "capabilities": ["database_design", "schema_planning"]},
                {"title": "Table Creation", "minutes": 15, "capabilities": ["database_administration", "sql"]},
                {"title": "Index Creation", "minutes": 15, "capabilities": ["database_administration", "performance_optimization"]},
                {"title": "Data Migration", "minutes": 15, "capabilities": ["database_administration", "data_migration"]},
                {"title": "Backup Strategy", "minutes": 15, "capabilities": ["database_administration", "backup_recovery"]},
                {"title": "Security Configuration", "minutes": 15, "capabilities": ["database_administration", "security"]},
                {"title": "Performance Testing", "minutes": 15, "capabilities": ["database_administration", "performance_testing"]},
                {"title": "Monitoring Setup", "minutes": 15, "capabilities": ["database_administration", "monitoring"]}
            ],
            "security_implementation": [
                {"title": "Security Requirements Analysis", "minutes": 15, "capabilities": ["security_analysis", "requirements_gathering"]},
                {"title": "Core Security Implementation", "minutes": 15, "capabilities": ["security_implementation", "python_development"]},
                {"title": "Security Testing", "minutes": 15, "capabilities": ["security_testing", "penetration_testing"]},
                {"title": "Security Documentation", "minutes": 15, "capabilities": ["security_documentation", "compliance"]},
                {"title": "Security Review", "minutes": 15, "capabilities": ["security_review", "code_review"]},
                {"title": "Security Monitoring", "minutes": 15, "capabilities": ["security_monitoring", "alerting"]}
            ],
            "api_development": [
                {"title": "API Design", "minutes": 15, "capabilities": ["api_design", "rest_api"]},
                {"title": "Endpoint Implementation", "minutes": 15, "capabilities": ["python_development", "fastapi"]},
                {"title": "Request Validation", "minutes": 15, "capabilities": ["python_development", "data_validation"]},
                {"title": "Response Formatting", "minutes": 15, "capabilities": ["python_development", "data_formatting"]},
                {"title": "Error Handling", "minutes": 15, "capabilities": ["python_development", "error_handling"]},
                {"title": "API Documentation", "minutes": 15, "capabilities": ["api_documentation", "openapi"]},
                {"title": "API Testing", "minutes": 15, "capabilities": ["api_testing", "integration_testing"]},
                {"title": "Performance Optimization", "minutes": 15, "capabilities": ["performance_optimization", "caching"]}
            ]
        }
    
    def breakdown_todo_into_15min_tasks(self, todo_data: Dict[str, Any]) -> TaskBreakdown:
        """Break down a complex TODO into 15-minute micro-tasks"""
        
        todo_id = todo_data.get("id", "unknown")
        todo_name = todo_data.get("name", "Unknown TODO")
        estimated_duration = todo_data.get("estimated_duration", "0 hours")
        required_capabilities = todo_data.get("required_capabilities", [])
        task_type = todo_data.get("task_type", "simple_task")
        
        # Parse estimated duration
        hours = self._parse_duration_to_hours(estimated_duration)
        
        # Determine template type based on TODO characteristics
        template_type = self._determine_template_type(todo_data)
        
        # Generate micro-tasks
        micro_tasks = self._generate_micro_tasks(
            todo_id, todo_name, hours, required_capabilities, template_type
        )
        
        # Calculate totals
        total_minutes = sum(task.estimated_minutes for task in micro_tasks)
        
        breakdown = TaskBreakdown(
            todo_id=todo_id,
            todo_name=todo_name,
            original_estimated_hours=estimated_duration,
            total_micro_tasks=len(micro_tasks),
            total_estimated_minutes=total_minutes,
            micro_tasks=micro_tasks,
            breakdown_created_at=datetime.now(),
            breakdown_version="1.0",
            status="created"
        )
        
        self.breakdowns[todo_id] = breakdown
        return breakdown
    
    def _parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        try:
            if "hours" in duration_str.lower():
                # Extract numeric value
                import re
                numbers = re.findall(r'\d+', duration_str)
                if len(numbers) >= 2:
                    # Range format like "4-6 hours"
                    return (float(numbers[0]) + float(numbers[1])) / 2
                elif len(numbers) == 1:
                    return float(numbers[0])
            return 1.0  # Default
        except:
            return 1.0
    
    def _determine_template_type(self, todo_data: Dict[str, Any]) -> str:
        """Determine which template to use based on TODO characteristics"""
        name = todo_data.get("name", "").lower()
        capabilities = todo_data.get("required_capabilities", [])
        
        if any("agent" in name for name in [name]):
            return "ai_agent_development"
        elif any("database" in cap.lower() for cap in capabilities):
            return "database_setup"
        elif any("security" in cap.lower() for cap in capabilities):
            return "security_implementation"
        elif any("api" in cap.lower() for cap in capabilities):
            return "api_development"
        else:
            return "ai_agent_development"  # Default
    
    def _generate_micro_tasks(self, todo_id: str, todo_name: str, hours: float, 
                             capabilities: List[str], template_type: str) -> List[MicroTask]:
        """Generate micro-tasks based on template and requirements"""
        
        micro_tasks = []
        template = self.micro_task_templates.get(template_type, [])
        
        # Calculate number of 15-minute blocks needed
        total_minutes = hours * 60
        num_blocks = math.ceil(total_minutes / 15)
        
        # Generate tasks based on template
        for i in range(min(num_blocks, len(template))):
            template_task = template[i]
            
            # Create unique task ID
            task_id = f"{todo_id}_micro_{i+1:03d}"
            
            # Determine dependencies
            dependencies = []
            if i > 0:
                dependencies.append(f"{todo_id}_micro_{i:03d}")
            
            # Determine priority
            priority = "high" if i < 2 else "medium"  # First tasks are higher priority
            
            # Create micro task
            micro_task = MicroTask(
                task_id=task_id,
                parent_todo_id=todo_id,
                title=f"{template_task['title']} - {todo_name}",
                description=f"Implement {template_task['title']} for {todo_name}",
                estimated_minutes=template_task['minutes'],
                required_capabilities=template_task['capabilities'],
                dependencies=dependencies,
                status="pending",
                priority=priority,
                assigned_agent=None,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                actual_minutes=None,
                notes="",
                complexity_score=2,  # Default complexity
                tags=[template_type, "micro_task", "15min"]
            )
            
            micro_tasks.append(micro_task)
        
        # Add remaining blocks if needed
        remaining_blocks = num_blocks - len(template)
        for i in range(remaining_blocks):
            task_id = f"{todo_id}_micro_{len(template) + i + 1:03d}"
            
            micro_task = MicroTask(
                task_id=task_id,
                parent_todo_id=todo_id,
                title=f"Additional Implementation - {todo_name}",
                description=f"Complete remaining implementation for {todo_name}",
                estimated_minutes=15,
                required_capabilities=capabilities,
                dependencies=[f"{todo_id}_micro_{len(template) + i:03d}"] if i > 0 else [],
                status="pending",
                priority="medium",
                assigned_agent=None,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                actual_minutes=None,
                notes="",
                complexity_score=2,
                tags=[template_type, "micro_task", "15min", "additional"]
            )
            
            micro_tasks.append(micro_task)
        
        return micro_tasks
    
    def get_breakdown(self, todo_id: str) -> Optional[TaskBreakdown]:
        """Get breakdown for a specific TODO"""
        return self.breakdowns.get(todo_id)
    
    def update_micro_task_status(self, task_id: str, status: str, 
                                agent: Optional[str] = None, notes: str = "") -> bool:
        """Update status of a micro task"""
        for breakdown in self.breakdowns.values():
            for task in breakdown.micro_tasks:
                if task.task_id == task_id:
                    task.status = status
                    if agent:
                        task.assigned_agent = agent
                    if notes:
                        task.notes = notes
                    
                    # Update timestamps
                    if status == "in_progress" and not task.started_at:
                        task.started_at = datetime.now()
                    elif status == "completed" and not task.completed_at:
                        task.completed_at = datetime.now()
                    
                    return True
        return False
    
    def get_available_micro_tasks(self, agent_capabilities: List[str]) -> List[MicroTask]:
        """Get available micro tasks for an agent based on capabilities"""
        available_tasks = []
        
        for breakdown in self.breakdowns.values():
            for task in breakdown.micro_tasks:
                if (task.status == "pending" and 
                    task.assigned_agent is None and
                    self._agent_can_handle_task(agent_capabilities, task.required_capabilities) and
                    self._dependencies_met(task, breakdown.micro_tasks)):
                    available_tasks.append(task)
        
        return sorted(available_tasks, key=lambda x: x.priority, reverse=True)
    
    def _agent_can_handle_task(self, agent_capabilities: List[str], 
                               required_capabilities: List[str]) -> bool:
        """Check if agent can handle a task based on capabilities"""
        return any(cap in agent_capabilities for cap in required_capabilities)
    
    def _dependencies_met(self, task: MicroTask, all_tasks: List[MicroTask]) -> bool:
        """Check if all dependencies for a task are met"""
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            dep_task = next((t for t in all_tasks if t.task_id == dep_id), None)
            if not dep_task or dep_task.status != "completed":
                return False
        
        return True
    
    def export_breakdown_to_json(self, todo_id: str) -> Optional[str]:
        """Export breakdown to JSON format"""
        breakdown = self.get_breakdown(todo_id)
        if breakdown:
            # Convert datetime objects to strings for JSON serialization
            data = asdict(breakdown)
            data['breakdown_created_at'] = data['breakdown_created_at'].isoformat()
            
            for task in data['micro_tasks']:
                task['created_at'] = task['created_at'].isoformat()
                if task['started_at']:
                    task['started_at'] = task['started_at'].isoformat()
                if task['completed_at']:
                    task['completed_at'] = task['completed_at'].isoformat()
            
            return json.dumps(data, indent=2)
        return None
    
    def get_breakdown_summary(self) -> Dict[str, Any]:
        """Get summary of all breakdowns"""
        summary = {
            "total_breakdowns": len(self.breakdowns),
            "total_micro_tasks": 0,
            "completed_micro_tasks": 0,
            "in_progress_micro_tasks": 0,
            "pending_micro_tasks": 0,
            "breakdowns": []
        }
        
        for breakdown in self.breakdowns.values():
            breakdown_summary = {
                "todo_id": breakdown.todo_id,
                "todo_name": breakdown.todo_name,
                "total_micro_tasks": breakdown.total_micro_tasks,
                "completed": len([t for t in breakdown.micro_tasks if t.status == "completed"]),
                "in_progress": len([t for t in breakdown.micro_tasks if t.status == "in_progress"]),
                "pending": len([t for t in breakdown.micro_tasks if t.status == "pending"]),
                "progress_percentage": 0
            }
            
            if breakdown.total_micro_tasks > 0:
                breakdown_summary["progress_percentage"] = (
                    breakdown_summary["completed"] / breakdown_summary["total_micro_tasks"]
                ) * 100
            
            summary["breakdowns"].append(breakdown_summary)
            summary["total_micro_tasks"] += breakdown.total_micro_tasks
            summary["completed_micro_tasks"] += breakdown_summary["completed"]
            summary["in_progress_micro_tasks"] += breakdown_summary["in_progress"]
            summary["pending_micro_tasks"] += breakdown_summary["pending"]
        
        return summary


# Global instance
task_breakdown_engine = TaskBreakdownEngine()


def create_15min_breakdown_for_todo(todo_data: Dict[str, Any]) -> TaskBreakdown:
    """Convenience function to create 15-minute breakdown for a TODO"""
    return task_breakdown_engine.breakdown_todo_into_15min_tasks(todo_data)


def get_available_15min_tasks(agent_capabilities: List[str]) -> List[MicroTask]:
    """Get available 15-minute tasks for an agent"""
    return task_breakdown_engine.get_available_micro_tasks(agent_capabilities)


def update_15min_task_status(task_id: str, status: str, agent: Optional[str] = None, notes: str = "") -> bool:
    """Update status of a 15-minute task"""
    return task_breakdown_engine.update_micro_task_status(task_id, status, agent, notes)


def export_15min_breakdown(todo_id: str) -> Optional[str]:
    """Export 15-minute breakdown to JSON"""
    return task_breakdown_engine.export_breakdown_to_json(todo_id)


def get_15min_breakdown_summary() -> Dict[str, Any]:
    """Get summary of all 15-minute breakdowns"""
    return task_breakdown_engine.get_breakdown_summary()
