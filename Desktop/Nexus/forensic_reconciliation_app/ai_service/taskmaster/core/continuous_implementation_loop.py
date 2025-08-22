#!/usr/bin/env python3
"""
Continuous Implementation Loop - Automatically process and update unimplemented TODOs
Features: Automated looping, progress tracking, status updates, continuous logging
"""

import json
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import schedule

from simple_batch_processor import SimpleBatchProcessor
from implement_unimplemented_todos import generate_unimplemented_todos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_implementation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ImplementationCycle:
    """Represents a complete implementation cycle"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_todos: int
    successful_implementations: int
    failed_implementations: int
    total_micro_tasks: int
    total_estimated_hours: float
    cycle_duration: float
    status: str  # running, completed, failed
    notes: List[str]
    progress_updates: List[Dict[str, Any]]

class ContinuousImplementationLoop:
    """Continuous loop system for implementing unimplemented TODOs with enhanced features"""
    
    def __init__(self, loop_interval_seconds: int = 15, max_cycles: int = 10, 
                 target_micro_tasks_per_cycle: int = 75, complexity_distribution: Dict[str, float] = None):
        self.loop_interval = loop_interval_seconds
        self.max_cycles = max_cycles
        self.target_micro_tasks_per_cycle = target_micro_tasks_per_cycle
        self.current_cycle = None
        self.cycle_history: List[ImplementationCycle] = []
        self.total_cycles = 0
        self.is_running = False
        self.loop_thread = None
        self.processor = SimpleBatchProcessor(max_workers=75)
        
        # Enhanced statistics tracking
        self.stats = {
            "total_cycles": 0,
            "total_todos_processed": 0,
            "total_micro_tasks_created": 0,
            "total_estimated_hours": 0.0,
            "average_cycle_duration": 0.0,
            "success_rate": 0.0,
            "cycle_efficiency": [],
            "complexity_distribution": complexity_distribution or {"low": 0.2, "medium": 0.4, "high": 0.3, "critical": 0.1}
        }
        
        # Single cycle optimization configuration
        self.cycle_config = {
            "target_micro_tasks": target_micro_tasks_per_cycle,
            "max_todos_per_cycle": 15,  # Reduced for smaller micro-task target
            "complexity_optimization": True,
            "balanced_distribution": True,
            "efficiency_tracking": True
        }
        
        logger.info(f"Optimized Single-Cycle ImplementationLoop initialized with {loop_interval_seconds} second intervals")
        logger.info(f"Target micro-tasks per cycle: {target_micro_tasks_per_cycle:,}")
        logger.info(f"Complexity distribution: {self.stats['complexity_distribution']}")
    
    def _generate_optimized_todos(self) -> List[Dict[str, Any]]:
        """Generate optimized TODOs to meet target micro-task count for single cycle"""
        current_cycle = self.total_cycles + 1
        target_micro_tasks = self.cycle_config["target_micro_tasks"]
        
        logger.info(f"Generating optimized TODOs for cycle {current_cycle} targeting {target_micro_tasks:,} micro-tasks")
        
        # Core TODO categories optimized for single cycle
        optimized_categories = [
            "fraud_detection", "evidence_management", "risk_assessment", "security_implementation",
            "api_development", "database_optimization", "user_interface", "monitoring_system",
            "data_analytics", "machine_learning", "blockchain_integration", "cloud_infrastructure",
            "performance_optimization", "scalability_engineering", "compliance_automation"
        ]
        
        todos = []
        current_micro_tasks = 0
        todo_count = 0
        
        # Generate TODOs until we reach target micro-task count
        while current_micro_tasks < target_micro_tasks and todo_count < self.cycle_config["max_todos_per_cycle"]:
            # Use balanced complexity distribution for optimal cycle efficiency
            complexity = self._balanced_complexity_choice()
            
            # Calculate optimal duration to reach target
            remaining_micro_tasks = target_micro_tasks - current_micro_tasks
            optimal_hours = self._calculate_optimal_duration(complexity, remaining_micro_tasks, len(todos) + 1)
            
            # Generate capabilities based on complexity
            capabilities = self._generate_optimized_capabilities(complexity)
            
            todo = {
                "id": f"OPTIMIZED_TODO_{current_cycle:02d}_{todo_count+1:03d}",
                "name": f"Optimized {optimized_categories[todo_count % len(optimized_categories)].replace('_', ' ').title()} Implementation",
                "description": f"Efficient implementation of {optimized_categories[todo_count % len(optimized_categories)]} optimized for cycle {current_cycle}",
                "estimated_duration": f"{optimal_hours}-{int(optimal_hours * 1.2)} hours",
                "complexity": complexity,
                "priority": self._determine_priority(complexity, current_cycle),
                "category": optimized_categories[todo_count % len(optimized_categories)],
                "required_capabilities": capabilities,
                "dependencies": [],
                "business_value": f"Cycle {current_cycle} optimized implementation with {complexity} complexity",
                "technical_debt_impact": f"Efficiently modernizes {optimized_categories[todo_count % len(optimized_categories)]} systems",
                "estimated_micro_tasks": self._estimate_micro_tasks_for_todo(optimal_hours, complexity)
            }
            
            estimated_micro_tasks = todo["estimated_micro_tasks"]
            
            # Only add if it doesn't exceed target significantly
            if current_micro_tasks + estimated_micro_tasks <= target_micro_tasks * 1.1:
                todos.append(todo)
                current_micro_tasks += estimated_micro_tasks
                todo_count += 1
                
                # Update complexity distribution stats
                self.stats["complexity_distribution"][complexity] += 1
            else:
                break
        
        logger.info(f"Generated {len(todos)} optimized TODOs with {current_micro_tasks:,} estimated micro-tasks")
        logger.info(f"Complexity distribution: {self.stats['complexity_distribution']}")
        
        return todos
    
    def _balanced_complexity_choice(self) -> str:
        """Choose complexity based on balanced distribution for optimal cycle efficiency"""
        import random
        
        # Use the configured complexity distribution
        complexities = list(self.stats["complexity_distribution"].keys())
        weights = list(self.stats["complexity_distribution"].values())
        
        return random.choices(complexities, weights=weights)[0]
    
    def _calculate_optimal_duration(self, complexity: str, remaining_micro_tasks: int, current_todo_count: int) -> int:
        """Calculate optimal duration to efficiently reach target micro-task count"""
        # Base durations optimized for single cycle with smaller targets
        base_durations = {
            "low": 2, "medium": 4, "high": 6, "critical": 8
        }
        
        base_hours = base_durations[complexity]
        
        # Adjust based on remaining micro-tasks needed
        if remaining_micro_tasks > 50:
            # Need many more micro-tasks, use higher complexity
            if complexity == "low":
                base_hours = min(base_hours * 1.5, 6)
            elif complexity == "medium":
                base_hours = min(base_hours * 1.3, 8)
        elif remaining_micro_tasks < 20:
            # Almost at target, use lower complexity
            base_hours = max(base_hours * 0.8, 1)
        
        # Ensure reasonable bounds for smaller targets
        return max(min(base_hours, 10), 1)
    
    def _generate_optimized_capabilities(self, complexity: str) -> List[str]:
        """Generate optimized capabilities for single cycle efficiency"""
        base_capabilities = ["python_development", "system_design"]
        
        # Add complexity-specific capabilities
        complexity_capabilities = {
            "low": ["basic_development", "testing"],
            "medium": ["api_development", "database_design", "security"],
            "high": ["machine_learning", "distributed_systems", "performance_optimization"],
            "critical": ["ai_development", "enterprise_architecture", "scalability_engineering"]
        }
        
        all_capabilities = base_capabilities + complexity_capabilities[complexity]
        
        # Return optimal number of capabilities
        max_capabilities = {"low": 3, "medium": 5, "high": 7, "critical": 8}
        return list(set(all_capabilities))[:max_capabilities[complexity]]
    
    def _estimate_micro_tasks_for_todo(self, hours: int, complexity: str) -> int:
        """Estimate micro-tasks for a TODO based on hours and complexity"""
        # Base estimate: 4 micro-tasks per hour (15-minute tasks)
        base_estimate = hours * 4
        
        # Complexity multiplier for more accurate estimation
        complexity_multiplier = {
            "low": 0.8,      # Simpler tasks, fewer micro-tasks
            "medium": 1.0,   # Standard complexity
            "high": 1.3,     # More complex, more micro-tasks
            "critical": 1.6  # Very complex, significantly more micro-tasks
        }
        
        estimated = int(base_estimate * complexity_multiplier[complexity])
        return max(estimated, 3)  # Minimum 3 micro-tasks for smaller targets
    

    
    def _generate_enhanced_dependencies(self, todo_index: int, cycle: int) -> List[str]:
        """Generate enhanced dependencies for more complex systems"""
        if not self.scaling_config["dependency_chaining"] or todo_index == 0:
            return []
        
        # Create dependency chains based on cycle complexity
        dependencies = []
        if cycle >= 2 and todo_index > 0:
            dependencies.append(f"ENHANCED_TODO_{cycle:02d}_{todo_index:03d}")
        if cycle >= 3 and todo_index > 2:
            dependencies.append(f"ENHANCED_TODO_{cycle:02d}_{todo_index-2:03d}")
        
        return dependencies
    
    def _generate_enhanced_features(self, complexity: str, cycle: int) -> List[str]:
        """Generate enhanced features based on complexity and cycle"""
        features = []
        
        if complexity in ["high", "critical"]:
            features.extend(["real_time_processing", "ai_enhanced_analytics", "auto_scaling"])
        
        if cycle >= 2:
            features.extend(["advanced_monitoring", "predictive_analytics"])
        
        if cycle >= 3:
            features.extend(["machine_learning_pipelines", "distributed_processing"])
        
        if cycle >= 4:
            features.extend(["quantum_ready_algorithms", "edge_intelligence"])
        
        return features
    
    def _generate_integration_points(self, complexity: str, cycle: int) -> List[str]:
        """Generate integration points for enhanced systems"""
        integrations = ["api_gateway", "message_queue", "database"]
        
        if complexity in ["high", "critical"]:
            integrations.extend(["ai_services", "blockchain", "cloud_services"])
        
        if cycle >= 2:
            integrations.extend(["monitoring_systems", "logging_platforms"])
        
        if cycle >= 3:
            integrations.extend(["ml_platforms", "data_lakes", "streaming_platforms"])
        
        return integrations
    
    def _generate_performance_targets(self, complexity: str, cycle: int) -> Dict[str, Any]:
        """Generate performance targets for enhanced systems"""
        targets = {
            "response_time": "100ms",
            "throughput": "1000 req/sec",
            "availability": "99.9%"
        }
        
        if complexity in ["high", "critical"]:
            targets.update({
                "response_time": "50ms",
                "throughput": "10000 req/sec",
                "availability": "99.99%",
                "scalability": "auto-scaling to 100x load"
            })
        
        if cycle >= 3:
            targets.update({
                "ai_processing": "real-time inference",
                "data_processing": "streaming analytics"
            })
        
        return targets
    
    def _determine_priority(self, complexity: str, cycle: int) -> str:
        """Determine priority based on complexity and cycle"""
        if complexity == "critical" or cycle <= 2:
            return "high"
        elif complexity == "high" or cycle <= 4:
            return "medium"
        else:
            return "low"
    
    def _weighted_random_choice(self, weights: Dict[str, float]) -> str:
        """Make weighted random choice based on probability weights"""
        import random
        choices = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(choices, weights=probabilities)[0]
    
    def _estimate_micro_tasks(self, todo: Dict[str, Any]) -> int:
        """Estimate number of micro-tasks for a TODO"""
        duration_str = todo["estimated_duration"]
        try:
            # Extract hours from duration string
            hours = int(duration_str.split("-")[0])
            # Estimate 4 micro-tasks per hour (15-minute tasks)
            return max(hours * 4, 8)  # Minimum 8 micro-tasks
        except:
            return 20  # Default estimate
    
    def _start_continuous_loop(self):
        """Start the continuous implementation loop in a separate thread"""
        if self.is_running:
            logger.warning("Continuous loop is already running")
            return
        
        self.is_running = True
        self.loop_thread = threading.Thread(target=self._run_continuous_loop, daemon=True)
        self.loop_thread.start()
        
        logger.info(f"Continuous loop started - will run every {self.loop_interval} seconds")
    
    def _run_continuous_loop(self):
        """Run the continuous implementation loop"""
        logger.info("Starting continuous implementation loop")
        
        # Schedule the first cycle immediately
        schedule.every(self.loop_interval).seconds.do(self._run_implementation_cycle)
        
        while self.is_running and self.total_cycles < self.max_cycles:
            schedule.run_pending()
            time.sleep(1)  # Check every second
            
            # Check if we should stop
            if self.total_cycles >= self.max_cycles:
                logger.info(f"Reached maximum cycles ({self.max_cycles}), stopping loop")
                break
        
        self.is_running = False
        logger.info("Continuous implementation loop stopped")
    
    def stop_continuous_loop(self):
        """Stop the continuous implementation loop"""
        self.is_running = False
        schedule.clear()
        
        if self.loop_thread:
            self.loop_thread.join(timeout=5)
        
        logger.info("Continuous implementation loop stopped")
    
    def _loop_worker(self):
        """Main loop worker thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _run_implementation_cycle(self):
        """Run a single implementation cycle"""
        if self.total_cycles >= self.max_cycles:
            logger.info(f"Maximum cycles ({self.max_cycles}) reached, stopping loop")
            self.stop_continuous_loop()
            return
        
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting implementation cycle {cycle_id}")
        
        # Create cycle record
        self.current_cycle = ImplementationCycle(
            cycle_id=cycle_id,
            start_time=start_time,
            end_time=None,
            total_todos=0,
            successful_implementations=0,
            failed_implementations=0,
            total_micro_tasks=0,
            total_estimated_hours=0.0,
            cycle_duration=0.0,
            status="running",
            notes=[],
            progress_updates=[]
        )
        
        try:
            # Generate optimized TODOs for single cycle efficiency
            todos = self._generate_optimized_todos()
            self.current_cycle.total_todos = len(todos)
            
            # Calculate actual micro-tasks created
            actual_micro_tasks = sum(todo.get("estimated_micro_tasks", 0) for todo in todos)
            
            # Add progress update
            self.current_cycle.progress_updates.append({
                "timestamp": datetime.now().isoformat(),
                "action": "generated_optimized_todos",
                "details": f"Generated {len(todos)} optimized TODOs targeting {self.cycle_config['target_micro_tasks']:,} micro-tasks, achieved {actual_micro_tasks:,} micro-tasks"
            })
            
            # Process the batch
            logger.info(f"Processing {len(todos)} TODOs in cycle {cycle_id}")
            
            batch_result = self.processor.process_todo_batch(
                todos, 
                f"cycle_{cycle_id}_batch"
            )
            
            # Update cycle with results
            self.current_cycle.successful_implementations = batch_result.successful
            self.current_cycle.failed_implementations = batch_result.failed
            self.current_cycle.total_micro_tasks = batch_result.total_micro_tasks
            self.current_cycle.total_estimated_hours = batch_result.total_estimated_hours
            
            # Mark cycle as completed
            end_time = datetime.now()
            self.current_cycle.end_time = end_time
            self.current_cycle.cycle_duration = (end_time - start_time).total_seconds()
            self.current_cycle.status = "completed"
            
            # Add completion note
            self.current_cycle.notes.append(
                f"Cycle completed successfully: {batch_result.successful} successful, "
                f"{batch_result.failed} failed, {batch_result.total_micro_tasks} micro-tasks created"
            )
            
            # Update statistics with cycle efficiency tracking
            self._update_stats()
            
            # Calculate cycle efficiency (how close to target we got)
            target_micro_tasks = self.cycle_config["target_micro_tasks"]
            actual_micro_tasks = self.current_cycle.total_micro_tasks
            efficiency = (actual_micro_tasks / target_micro_tasks * 100) if target_micro_tasks > 0 else 0
            
            logger.info(f"Cycle {cycle_id} efficiency: {efficiency:.1f}% of target micro-tasks")
            
            # Add cycle efficiency metrics
            efficiency_metric = {
                "cycle": self.total_cycles,
                "todos_processed": self.current_cycle.total_todos,
                "micro_tasks_created": self.current_cycle.total_micro_tasks,
                "target_micro_tasks": target_micro_tasks,
                "efficiency_percentage": efficiency,
                "complexity_distribution": self.stats["complexity_distribution"].copy()
            }
            self.stats["cycle_efficiency"].append(efficiency_metric)
            
            logger.info(f"Cycle {cycle_id} completed successfully in {self.current_cycle.cycle_duration:.2f} seconds")
            logger.info(f"Cycle efficiency metrics: {efficiency_metric}")
            
        except Exception as e:
            # Mark cycle as failed
            end_time = datetime.now()
            self.current_cycle.end_time = end_time
            self.current_cycle.cycle_duration = (end_time - start_time).total_seconds()
            self.current_cycle.status = "failed"
            self.current_cycle.notes.append(f"Cycle failed with error: {str(e)}")
            
            logger.error(f"Cycle {cycle_id} failed: {e}")
        
        # Add cycle to history
        self.cycle_history.append(self.current_cycle)
        self.total_cycles += 1
        
        # Log cycle summary
        self._log_cycle_summary()
        
        # Clear current cycle
        self.current_cycle = None
    
    def _update_stats(self):
        """Update overall statistics"""
        if not self.current_cycle:
            return
        
        self.stats["total_cycles"] = len(self.cycle_history)
        self.stats["total_todos_processed"] += self.current_cycle.total_todos
        self.stats["total_micro_tasks_created"] += self.current_cycle.total_micro_tasks
        self.stats["total_estimated_hours"] += self.current_cycle.total_estimated_hours
        
        # Calculate averages
        if self.stats["total_cycles"] > 0:
            total_duration = sum(c.cycle_duration for c in self.cycle_history)
            self.stats["average_cycle_duration"] = total_duration / self.stats["total_cycles"]
            
            total_successful = sum(c.successful_implementations for c in self.cycle_history)
            total_processed = sum(c.total_todos for c in self.cycle_history)
            if total_processed > 0:
                self.stats["success_rate"] = (total_successful / total_processed) * 100
    
    def _log_cycle_summary(self):
        """Log summary of the completed cycle"""
        if not self.current_cycle:
            return
        
        cycle = self.current_cycle
        
        print(f"\n{'='*60}")
        print(f"🔄 IMPLEMENTATION CYCLE {cycle.cycle_id} COMPLETED")
        print(f"{'='*60}")
        print(f"📊 Status: {cycle.status.upper()}")
        print(f"⏰ Duration: {cycle.cycle_duration:.2f} seconds")
        print(f"📋 TODOs Processed: {cycle.total_todos}")
        print(f"✅ Successful: {cycle.successful_implementations}")
        print(f"❌ Failed: {cycle.failed_implementations}")
        print(f"🔢 Micro-tasks Created: {cycle.total_micro_tasks:,}")
        print(f"⏰ Estimated Work: {cycle.total_estimated_hours:.1f} hours")
        
        if cycle.notes:
            print(f"\n📝 Notes:")
            for note in cycle.notes:
                print(f"   - {note}")
        
        # Show overall progress
        print(f"\n📈 OVERALL PROGRESS:")
        print(f"   - Total Cycles: {self.stats['total_cycles']}")
        print(f"   - Total TODOs: {self.stats['total_todos_processed']:,}")
        print(f"   - Total Micro-tasks: {self.stats['total_micro_tasks_created']:,}")
        print(f"   - Total Estimated Work: {self.stats['total_estimated_hours']:.1f} hours")
        print(f"   - Success Rate: {self.stats['success_rate']:.1f}%")
        print(f"   - Average Cycle Time: {self.stats['average_cycle_duration']:.2f} seconds")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current status of the implementation loop"""
        return {
            "is_running": self.is_running,
            "loop_interval_seconds": self.loop_interval,
            "total_cycles": self.total_cycles,
            "max_cycles": self.max_cycles,
            "current_cycle": asdict(self.current_cycle) if self.current_cycle else None,
            "stats": self.stats
        }
    
    def get_cycle_history(self) -> List[Dict[str, Any]]:
        """Get history of all implementation cycles"""
        return [asdict(cycle) for cycle in self.cycle_history]
    
    def export_implementation_report(self) -> str:
        """Export comprehensive implementation report"""
        report = {
            "report_generated_at": datetime.now().isoformat(),
            "loop_configuration": {
                "loop_interval_seconds": self.loop_interval,
                "max_cycles": self.max_cycles,
                "is_running": self.is_running
            },
            "overall_statistics": self.stats,
            "cycle_history": self.get_cycle_history(),
            "current_status": self.get_current_status()
        }
        
        return json.dumps(report, indent=2)

def demo_continuous_implementation():
    """Demonstrate the optimized single-cycle implementation loop"""
    print("=== Optimized Single-Cycle Implementation Loop Demo ===\n")
    
    # Initialize the optimized single-cycle loop
    loop = ContinuousImplementationLoop(
        loop_interval_seconds=15, 
        max_cycles=10, 
        target_micro_tasks_per_cycle=75  # Target 75 micro-tasks per cycle
    )
    
    print("🚀 Optimized Single-Cycle Implementation Loop Configuration:")
    print(f"   🎯 Target Micro-tasks per Cycle: {loop.target_micro_tasks_per_cycle:,}")
    print(f"   ⏰ Loop Interval: {loop.loop_interval} seconds")
    print(f"   🔄 Max Cycles: {loop.max_cycles}")
    print(f"   📊 Max TODOs per Cycle: {loop.cycle_config['max_todos_per_cycle']}")
    print(f"   🎯 Complexity Optimization: {'Enabled' if loop.cycle_config['complexity_optimization'] else 'Disabled'}")
    print(f"   ⚖️ Balanced Distribution: {'Enabled' if loop.cycle_config['balanced_distribution'] else 'Disabled'}")
    print(f"   🚀 Parallel Workers: {loop.processor.max_workers}")
    
    print(f"\n📊 Expected Cycle Performance:")
    for cycle in range(1, loop.max_cycles + 1):
        print(f"   🔄 Cycle {cycle}: Target ~{loop.target_micro_tasks_per_cycle:,} micro-tasks every {loop.loop_interval}s")
    
    print(f"\nStarting optimized single-cycle implementation loop...")
    print("Press Ctrl+C to stop early\n")
    
    try:
        # Start the loop
        loop._start_continuous_loop()
        
        # Monitor progress
        start_time = time.time()
        while loop.is_running and loop.total_cycles < loop.max_cycles:
            time.sleep(30)  # Check every 30 seconds
            
            # Show current status
            status = loop.get_current_status()
            if status["current_cycle"]:
                cycle = status["current_cycle"]
                if cycle["status"] == "running":
                    # Handle both string and datetime objects
                    cycle_start_time = cycle["start_time"]
                    if isinstance(cycle_start_time, str):
                        cycle_start_time = datetime.fromisoformat(cycle_start_time)
                    elapsed = (datetime.now() - cycle_start_time).total_seconds()
                    print(f"\r🔄 Cycle {cycle['cycle_id']} running... {elapsed:.0f}s elapsed", end="")
        
        # Wait for final cycle to complete
        time.sleep(10)
        
        # Stop the loop
        loop.stop_continuous_loop()
        
        total_time = time.time() - start_time
        
        # Show final results
        print(f"\n\n{'='*80}")
        print(f"🎯 ENHANCED CONTINUOUS IMPLEMENTATION LOOP COMPLETED!")
        print(f"{'='*80}")
        print(f"⏰ Total Runtime: {total_time:.1f} seconds")
        print(f"🔄 Total Cycles: {loop.total_cycles}")
        print(f"📊 Final Statistics:")
        
        stats = loop.stats
        print(f"   - Total TODOs Processed: {stats['total_todos_processed']:,}")
        print(f"   - Total Micro-tasks Created: {stats['total_micro_tasks_created']:,}")
        print(f"   - Total Estimated Work: {stats['total_estimated_hours']:.1f} hours")
        print(f"   - Success Rate: {stats['success_rate']:.1f}%")
        print(f"   - Average Cycle Time: {stats['average_cycle_duration']:.2f} seconds")
        
        # Show cycle efficiency metrics
        if stats["cycle_efficiency"]:
            print(f"\n🎯 CYCLE EFFICIENCY ANALYSIS:")
            for i, efficiency_metric in enumerate(stats["cycle_efficiency"], 1):
                cycle = efficiency_metric["cycle"]
                todos = efficiency_metric["todos_processed"]
                micro_tasks = efficiency_metric["micro_tasks_created"]
                target = efficiency_metric["target_micro_tasks"]
                efficiency = efficiency_metric["efficiency_percentage"]
                efficiency_emoji = "✅" if efficiency >= 90 else "🟡" if efficiency >= 70 else "🟠" if efficiency >= 50 else "🔴"
                print(f"   {efficiency_emoji} Cycle {cycle}: {todos} TODOs → {micro_tasks:,} micro-tasks "
                      f"({efficiency:.1f}% of {target:,} target)")
            
            # Calculate overall efficiency
            if len(stats["cycle_efficiency"]) > 0:
                avg_efficiency = sum(m["efficiency_percentage"] for m in stats["cycle_efficiency"]) / len(stats["cycle_efficiency"])
                print(f"\n   📊 Overall Cycle Efficiency: {avg_efficiency:.1f}% of target micro-tasks")
        
        # Show complexity distribution
        print(f"\n🎯 COMPLEXITY DISTRIBUTION ACROSS ALL CYCLES:")
        complexity_stats = stats["complexity_distribution"]
        total_complexity = sum(complexity_stats.values())
        for complexity, count in complexity_stats.items():
            percentage = (count / total_complexity * 100) if total_complexity > 0 else 0
            complexity_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
            print(f"   {complexity_emoji.get(complexity, '⚪')} {complexity.title()}: {count} ({percentage:.1f}%)")
        
        # Show cycle summary
        print(f"\n📈 CYCLE SUMMARY:")
        for i, cycle in enumerate(loop.cycle_history, 1):
            status_emoji = "✅" if cycle.status == "completed" else "❌"
            print(f"   {status_emoji} Cycle {i}: {cycle.total_todos} TODOs, "
                  f"{cycle.total_micro_tasks} micro-tasks, {cycle.cycle_duration:.1f}s")
        
        # Export report
        report = loop.export_implementation_report()
        with open('implementation_report.json', 'w') as f:
            f.write(report)
        print(f"\n📄 Detailed report exported to: implementation_report.json")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stopping continuous loop...")
        loop.stop_continuous_loop()
        print("Loop stopped by user")

if __name__ == "__main__":
    demo_continuous_implementation()
