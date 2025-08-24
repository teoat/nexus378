#!/usr/bin/env python3
"""
Task Breakdown Engine for Nexus Platform
Breaks down complex tasks into manageable subtasks
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any

class TaskBreakdownEngine:
    def __init__(self):
        self.project_root = Path.cwd()
        self.complex_tasks = []
        self.subtasks = []
        
    def discover_complex_tasks(self) -> List[Dict[str, Any]]:
        """Discover complex tasks that need breakdown"""
        complex_tasks = []
        
        # Look for tasks in various sources
        sources = [
            "master_todo.md",
            "TODO_MASTER.md",
            "IMPLEMENTATION_COMPLETE_SUMMARY.md"
        ]
        
        for source in sources:
            source_path = self.project_root / source
            if source_path.exists():
                tasks = self.extract_tasks_from_file(source_path)
                complex_tasks.extend(tasks)
                
        return complex_tasks
    
    def extract_tasks_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract tasks from a markdown file"""
        tasks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('- [ ]') and len(line.strip()) > 50:
                    # This might be a complex task
                    description = line.replace('- [ ]', '').strip()
                    complexity_score = self.assess_complexity(description)
                    
                    if complexity_score > 7:  # High complexity threshold
                        tasks.append({
                            'source_file': str(file_path),
                            'line_number': i + 1,
                            'description': description,
                            'complexity_score': complexity_score,
                            'needs_breakdown': True
                        })
                        
        except Exception as e:
            print(f"Error extracting tasks from {file_path}: {e}")
            
        return tasks
    
    def assess_complexity(self, task_description: str) -> int:
        """Assess the complexity of a task (1-10 scale)"""
        complexity_indicators = [
            'implement', 'develop', 'create', 'build', 'design',
            'integrate', 'configure', 'deploy', 'test', 'optimize',
            'database', 'API', 'frontend', 'backend', 'infrastructure',
            'monitoring', 'security', 'authentication', 'deployment'
        ]
        
        score = 1
        description_lower = task_description.lower()
        
        for indicator in complexity_indicators:
            if indicator in description_lower:
                score += 1
                
        # Length factor
        if len(task_description) > 100:
            score += 1
        if len(task_description) > 200:
            score += 1
            
        return min(score, 10)
    
    def break_down_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down a complex task into subtasks"""
        subtasks = []
        description = task['description']
        
        # Simple breakdown logic based on common patterns
        if 'implement' in description.lower():
            subtasks.extend([
                {'title': 'Research requirements', 'priority': 'high'},
                {'title': 'Design architecture', 'priority': 'high'},
                {'title': 'Implement core functionality', 'priority': 'high'},
                {'title': 'Write tests', 'priority': 'medium'},
                {'title': 'Document implementation', 'priority': 'medium'}
            ])
        elif 'deploy' in description.lower():
            subtasks.extend([
                {'title': 'Prepare deployment environment', 'priority': 'high'},
                {'title': 'Configure services', 'priority': 'high'},
                {'title': 'Deploy application', 'priority': 'high'},
                {'title': 'Verify deployment', 'priority': 'high'},
                {'title': 'Monitor performance', 'priority': 'medium'}
            ])
        elif 'test' in description.lower():
            subtasks.extend([
                {'title': 'Plan test strategy', 'priority': 'high'},
                {'title': 'Write unit tests', 'priority': 'high'},
                {'title': 'Write integration tests', 'priority': 'high'},
                {'title': 'Execute test suite', 'priority': 'medium'},
                {'title': 'Report results', 'priority': 'medium'}
            ])
        else:
            # Generic breakdown
            subtasks.extend([
                {'title': 'Analyze requirements', 'priority': 'high'},
                {'title': 'Plan implementation', 'priority': 'high'},
                {'title': 'Execute implementation', 'priority': 'high'},
                {'title': 'Validate results', 'priority': 'medium'},
                {'title': 'Document work', 'priority': 'medium'}
            ])
            
        # Add metadata to subtasks
        for i, subtask in enumerate(subtasks):
            subtask.update({
                'parent_task': task['description'][:50] + '...',
                'subtask_id': f"{task['line_number']}.{i+1}",
                'status': 'pending',
                'created_at': time.time()
            })
            
        return subtasks
    
    def process_complex_tasks(self):
        """Process all complex tasks and break them down"""
        print("⚡ Task Breakdown Engine Starting...")
        print("=" * 50)
        
        complex_tasks = self.discover_complex_tasks()
        print(f"🔍 Discovered {len(complex_tasks)} complex tasks:")
        
        for task in complex_tasks:
            print(f"   📋 {task['description'][:60]}... (Complexity: {task['complexity_score']}/10)")
            
        print("\n🔄 Breaking down complex tasks...")
        
        for task in complex_tasks:
            subtasks = self.break_down_task(task)
            self.subtasks.extend(subtasks)
            print(f"   📝 {task['description'][:50]}... → {len(subtasks)} subtasks")
            
        print(f"\n📊 Total subtasks created: {len(self.subtasks)}")
        
        return self.subtasks
    
    def run(self):
        """Main run loop for the task breakdown engine"""
        print("🚀 Task Breakdown Engine - Nexus Platform")
        print("=" * 60)
        
        while True:
            try:
                subtasks = self.process_complex_tasks()
                
                print("\n🔄 Processing cycle complete. Waiting 45 seconds...")
                print("Press Ctrl+C to stop")
                
                time.sleep(45)
                
            except KeyboardInterrupt:
                print("\n🛑 Task Breakdown Engine stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error in Task Breakdown Engine: {e}")
                time.sleep(15)

if __name__ == "__main__":
    engine = TaskBreakdownEngine()
    engine.run()
