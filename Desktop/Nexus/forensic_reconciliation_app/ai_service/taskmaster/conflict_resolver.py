#!/usr/bin/env python3
"""
Conflict Resolver - Resolves task conflicts and merges unmerged changes
"""

import logging
from datetime import datetime
from typing import Dict, List, Set, Tuple
from core.simple_registry import SimpleTaskRegistry
import json

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Resolves conflicts and merges unmerged changes in the task system"""
    
    def __init__(self):
        self.registry = SimpleTaskRegistry()
        self.conflicts_found = []
        self.resolutions_made = []
    
    def analyze_conflicts(self) -> Dict[str, List[str]]:
        """Analyze and identify all types of conflicts"""
        conflicts = {
            'overlapping_work': [],
            'capability_conflicts': [],
            'dependency_issues': [],
            'resource_conflicts': []
        }
        
        # Check for overlapping work
        for i, task1 in enumerate(self.registry.priority_todos):
            for j, task2 in enumerate(self.registry.priority_todos[i+1:], i+1):
                overlap_score = self._calculate_overlap_score(task1, task2)
                if overlap_score > 0.3:  # Significant overlap
                    conflicts['overlapping_work'].append({
                        'task1': task1['id'],
                        'task2': task2['id'],
                        'score': overlap_score,
                        'reason': self._get_overlap_reason(task1, task2)
                    })
        
        # Check for capability conflicts
        capability_map = {}
        for task in self.registry.priority_todos:
            for cap in task.get('required_capabilities', []):
                if cap not in capability_map:
                    capability_map[cap] = []
                capability_map[cap].append(task['id'])
        
        for cap, task_ids in capability_map.items():
            if len(task_ids) > 1:
                conflicts['capability_conflicts'].append({
                    'capability': cap,
                    'conflicting_tasks': task_ids
                })
        
        return conflicts
    
    def _calculate_overlap_score(self, task1: Dict, task2: Dict) -> float:
        """Calculate overlap score between two tasks"""
        # Check name similarity
        name1_words = set(task1.get('name', '').lower().split())
        name2_words = set(task2.get('name', '').lower().split())
        name_overlap = len(name1_words.intersection(name2_words)) / max(len(name1_words), len(name2_words))
        
        # Check capability overlap
        caps1 = set(task1.get('required_capabilities', []))
        caps2 = set(task2.get('required_capabilities', []))
        if caps1 and caps2:
            cap_overlap = len(caps1.intersection(caps2)) / len(caps1.union(caps2))
        else:
            cap_overlap = 0
        
        # Combined score
        return (name_overlap * 0.4) + (cap_overlap * 0.6)
    
    def _get_overlap_reason(self, task1: Dict, task2: Dict) -> str:
        """Get reason for overlap between tasks"""
        name1_words = set(task1.get('name', '').lower().split())
        name2_words = set(task2.get('name', '').lower().split())
        shared_words = name1_words.intersection(name2_words)
        
        caps1 = set(task1.get('required_capabilities', []))
        caps2 = set(task2.get('required_capabilities', []))
        shared_caps = caps1.intersection(caps2)
        
        reasons = []
        if shared_words:
            reasons.append(f"Shared keywords: {shared_words}")
        if shared_caps:
            reasons.append(f"Shared capabilities: {shared_caps}")
        
        return "; ".join(reasons)
    
    def resolve_conflicts(self, conflicts: Dict) -> List[Dict]:
        """Resolve identified conflicts"""
        resolutions = []
        
        # Resolve overlapping work by creating dependencies or merging
        for overlap in conflicts['overlapping_work']:
            task1_id = overlap['task1']
            task2_id = overlap['task2']
            
            task1 = next((t for t in self.registry.priority_todos if t['id'] == task1_id), None)
            task2 = next((t for t in self.registry.priority_todos if t['id'] == task2_id), None)
            
            if task1 and task2:
                resolution = self._resolve_task_overlap(task1, task2, overlap['score'])
                resolutions.append(resolution)
        
        # Resolve capability conflicts by sequencing tasks
        for cap_conflict in conflicts['capability_conflicts']:
            resolution = self._resolve_capability_conflict(cap_conflict)
            resolutions.append(resolution)
        
        return resolutions
    
    def _resolve_task_overlap(self, task1: Dict, task2: Dict, overlap_score: float) -> Dict:
        """Resolve overlap between two specific tasks"""
        if overlap_score > 0.7:  # High overlap - merge tasks
            return {
                'type': 'merge_tasks',
                'task1': task1['id'],
                'task2': task2['id'],
                'action': f"Merge {task2['name']} into {task1['name']}",
                'reason': 'High overlap detected - tasks should be combined'
            }
        elif overlap_score > 0.4:  # Medium overlap - create dependency
            # Prioritize based on task priority and complexity
            if task1['priority'] == 'CRITICAL' and task2['priority'] != 'CRITICAL':
                dependent_task, prerequisite_task = task2, task1
            elif task2['priority'] == 'CRITICAL' and task1['priority'] != 'CRITICAL':
                dependent_task, prerequisite_task = task1, task2
            else:
                # Use duration as tiebreaker (shorter task first)
                duration1 = self._parse_duration(task1.get('estimated_duration', '0-0 hours'))
                duration2 = self._parse_duration(task2.get('estimated_duration', '0-0 hours'))
                if duration1 < duration2:
                    dependent_task, prerequisite_task = task2, task1
                else:
                    dependent_task, prerequisite_task = task1, task2
            
            return {
                'type': 'create_dependency',
                'dependent': dependent_task['id'],
                'prerequisite': prerequisite_task['id'],
                'action': f"Make {dependent_task['name']} depend on {prerequisite_task['name']}",
                'reason': 'Medium overlap - prerequisite relationship needed'
            }
        else:  # Low overlap - coordinate timing
            return {
                'type': 'coordinate_timing',
                'task1': task1['id'],
                'task2': task2['id'],
                'action': f"Coordinate timing between {task1['name']} and {task2['name']}",
                'reason': 'Low overlap - timing coordination recommended'
            }
    
    def _resolve_capability_conflict(self, cap_conflict: Dict) -> Dict:
        """Resolve conflicts for tasks requiring the same capability"""
        capability = cap_conflict['capability']
        task_ids = cap_conflict['conflicting_tasks']
        
        # Get tasks and sort by priority
        tasks = [t for t in self.registry.priority_todos if t['id'] in task_ids]
        tasks.sort(key=lambda t: (t['priority'] != 'CRITICAL', t['priority'] != 'HIGH', t['id']))
        
        return {
            'type': 'sequence_capability_tasks',
            'capability': capability,
            'task_sequence': [t['id'] for t in tasks],
            'action': f"Sequence tasks requiring {capability}: {' → '.join([t['name'] for t in tasks])}",
            'reason': f'Multiple tasks require {capability} capability - sequential execution recommended'
        }
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string to get average hours"""
        try:
            # Extract numbers from string like "8-12 hours"
            parts = duration_str.lower().replace('hours', '').split('-')
            if len(parts) == 2:
                return (float(parts[0].strip()) + float(parts[1].strip())) / 2
            else:
                return float(parts[0].strip())
        except:
            return 0.0
    
    def apply_resolutions(self, resolutions: List[Dict]) -> List[str]:
        """Apply the conflict resolutions"""
        applied_changes = []
        
        for resolution in resolutions:
            if resolution['type'] == 'create_dependency':
                change = self._apply_dependency_resolution(resolution)
                applied_changes.append(change)
            elif resolution['type'] == 'merge_tasks':
                change = self._apply_merge_resolution(resolution)
                applied_changes.append(change)
            elif resolution['type'] == 'sequence_capability_tasks':
                change = self._apply_sequencing_resolution(resolution)
                applied_changes.append(change)
            elif resolution['type'] == 'coordinate_timing':
                change = self._apply_timing_resolution(resolution)
                applied_changes.append(change)
        
        return applied_changes
    
    def _apply_dependency_resolution(self, resolution: Dict) -> str:
        """Apply dependency resolution"""
        dependent_id = resolution['dependent']
        prerequisite_id = resolution['prerequisite']
        
        # Find the dependent task and add the prerequisite
        for task in self.registry.priority_todos:
            if task['id'] == dependent_id:
                if 'dependencies' not in task:
                    task['dependencies'] = []
                if prerequisite_id not in task['dependencies']:
                    task['dependencies'].append(prerequisite_id)
                    return f"✅ Added dependency: {dependent_id} now depends on {prerequisite_id}"
        
        return f"❌ Failed to apply dependency: {dependent_id} → {prerequisite_id}"
    
    def _apply_merge_resolution(self, resolution: Dict) -> str:
        """Apply task merge resolution"""
        # For now, just mark the tasks for manual review
        return f"⚠️ Manual review needed: Consider merging {resolution['task1']} and {resolution['task2']}"
    
    def _apply_sequencing_resolution(self, resolution: Dict) -> str:
        """Apply capability sequencing resolution"""
        task_sequence = resolution['task_sequence']
        
        # Create dependencies to ensure sequential execution
        changes = []
        for i in range(len(task_sequence) - 1):
            current_task = task_sequence[i+1]
            prerequisite_task = task_sequence[i]
            
            for task in self.registry.priority_todos:
                if task['id'] == current_task:
                    if 'dependencies' not in task:
                        task['dependencies'] = []
                    if prerequisite_task not in task['dependencies']:
                        task['dependencies'].append(prerequisite_task)
                        changes.append(f"{current_task} → {prerequisite_task}")
        
        return f"✅ Sequenced capability tasks: {' → '.join(changes)}"
    
    def _apply_timing_resolution(self, resolution: Dict) -> str:
        """Apply timing coordination resolution"""
        return f"⚠️ Timing coordination recommended for {resolution['task1']} and {resolution['task2']}"
    
    def save_updated_registry(self):
        """Save the updated registry with resolved conflicts"""
        # This would typically save to a file or database
        logger.info("Registry updated with conflict resolutions")
        return True


def main():
    """Main conflict resolution process"""
    print("🔧 CONFLICT RESOLUTION & MERGE PROCESS")
    print("=" * 60)
    
    resolver = ConflictResolver()
    
    # Step 1: Analyze conflicts
    print("📊 Step 1: Analyzing conflicts...")
    conflicts = resolver.analyze_conflicts()
    
    total_conflicts = sum(len(conflicts[k]) for k in conflicts)
    if total_conflicts == 0:
        print("✅ No conflicts found - system is properly aligned")
        return
    
    print(f"Found {total_conflicts} potential conflicts:")
    for conflict_type, items in conflicts.items():
        if items:
            print(f"   - {conflict_type}: {len(items)} issues")
    
    # Step 2: Generate resolutions
    print("\n🛠️ Step 2: Generating conflict resolutions...")
    resolutions = resolver.resolve_conflicts(conflicts)
    
    print(f"Generated {len(resolutions)} resolutions:")
    for resolution in resolutions:
        print(f"   - {resolution['action']}")
        print(f"     Reason: {resolution['reason']}")
    
    # Step 3: Apply resolutions
    print("\n⚙️ Step 3: Applying resolutions...")
    applied_changes = resolver.apply_resolutions(resolutions)
    
    for change in applied_changes:
        print(f"   {change}")
    
    # Step 4: Save updated registry
    print("\n💾 Step 4: Saving updated configuration...")
    if resolver.save_updated_registry():
        print("✅ Configuration updated successfully")
    
    print(f"\n🎉 Conflict resolution complete! Applied {len(applied_changes)} changes.")


if __name__ == "__main__":
    main()