#!/usr/bin/env python3
"""
Task Breakdown Engine - Converts complex TODOs to microtasks
Tab 10 of the 11-tab system
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from todo_master_reader import TodoMasterReader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaskBreakdownEngine:
    """Engine for breaking down complex TODOs into microtasks"""

    def __init__(self):
        self.todo_reader = TodoMasterReader()
        self.breakdown_interval = 15  # Process every 15 seconds
        self.engine_active = True
        self.microtasks_cache = {}
        self.breakdown_history = []

        # Create microtasks directory
        self.microtasks_dir = current_dir / "microtasks"
        self.microtasks_dir.mkdir(exist_ok=True)

        logger.info("Task Breakdown Engine initialized")
        logger.info(f"Microtasks directory: {self.microtasks_dir}")

    def start_breakdown_loop(self):
        """Start the continuous breakdown loop"""
        logger.info("Starting task breakdown loop")

        try:
            while self.engine_active:
                start_time = time.time()

                # Find complex TODOs for breakdown
                self._find_and_breakdown_complex_todos()

                # Process microtasks
                self._process_microtasks()

                # Update breakdown statistics
                self._update_breakdown_stats()

                # Calculate processing time and sleep
                processing_time = time.time() - start_time
                sleep_time = max(0, self.breakdown_interval - processing_time)

                logger.info(
                    f"Breakdown processing took {processing_time:.2f}s, sleeping for {sleep_time:.2f}s"
                )
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Task breakdown loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in task breakdown loop: {e}")

    def _find_and_breakdown_complex_todos(self):
        """Find complex TODOs and break them down"""
        try:
            pending_todos = self.todo_reader.get_pending_todos()
            complex_todos = []

            for todo in pending_todos:
                if self._is_complex_todo(todo):
                    complex_todos.append(todo)

            logger.info(f"Found {len(complex_todos)} complex TODOs for breakdown")

            # Process first 3 complex TODOs
            for todo in complex_todos[:3]:
                if not self._is_already_breakdown(todo):
                    self._breakdown_todo(todo)
                    time.sleep(2)  # Brief pause between breakdowns

        except Exception as e:
            logger.error(f"Error finding complex TODOs: {e}")

    def _is_complex_todo(self, todo):
        """Determine if a TODO is complex enough for breakdown"""
        title = todo.get("title", "").lower()
        description = todo.get("description", "").lower()

        # Complexity indicators
        complexity_indicators = [
            "multiple",
            "several",
            "all",
            "fix all",
            "refactor",
            "database",
            "api",
            "integration",
            "performance",
            "security",
            "migration",
            "upgrade",
            "restructure",
            "reorganize",
        ]

        # Check if any complexity indicators are present
        for indicator in complexity_indicators:
            if indicator in title or indicator in description:
                return True

        # Check if description is long (complex)
        if len(description) > 100:
            return True

        # Check if it mentions multiple files or components
        if any(word in title for word in ["files", "components", "modules", "systems"]):
            return True

        return False

    def _is_already_breakdown(self, todo):
        """Check if TODO has already been broken down"""
        todo_id = todo.get("id", "unknown")
        return todo_id in self.microtasks_cache

    def _breakdown_todo(self, todo):
        """Break down a complex TODO into microtasks"""
        try:
            todo_id = todo.get("id", "unknown")
            title = todo.get("title", "Unknown")

            logger.info(f"Breaking down complex TODO: {title[:50]}...")

            # Generate microtasks based on complexity
            microtasks = self._generate_microtasks(todo)

            # Store microtasks
            self.microtasks_cache[todo_id] = {
                "parent_todo": todo,
                "microtasks": microtasks,
                "created_at": datetime.now(),
                "status": "pending",
            }

            # Save to file
            self._save_microtasks(todo_id, microtasks)

            # Add to breakdown history
            self.breakdown_history.append(
                {
                    "todo_id": todo_id,
                    "title": title,
                    "microtasks_count": len(microtasks),
                    "breakdown_time": datetime.now(),
                }
            )

            logger.info(
                f"Generated {len(microtasks)} microtasks for TODO: {title[:50]}..."
            )

        except Exception as e:
            logger.error(f"Error breaking down TODO {todo.get('id', 'unknown')}: {e}")

    def _generate_microtasks(self, todo):
        """Generate microtasks for a complex TODO"""
        title = todo.get("title", "")
        description = todo.get("description", "")

        microtasks = []

        # Analyze the TODO and generate appropriate microtasks
        if "fix all" in title.lower() or "multiple files" in title.lower():
            # Generate file-by-file microtasks
            microtasks = self._generate_file_based_microtasks(todo)
        elif "database" in title.lower() or "api" in title.lower():
            # Generate component-based microtasks
            microtasks = self._generate_component_based_microtasks(todo)
        elif "refactor" in title.lower() or "restructure" in title.lower():
            # Generate refactoring microtasks
            microtasks = self._generate_refactoring_microtasks(todo)
        else:
            # Generate generic microtasks
            microtasks = self._generate_generic_microtasks(todo)

        return microtasks

    def _generate_file_based_microtasks(self, todo):
        """Generate microtasks for file-based work"""
        title = todo.get("title", "")

        # Extract number of files if mentioned
        import re

        file_count_match = re.search(r"(\d+)\s*files?", title)
        file_count = int(file_count_match.group(1)) if file_count_match else 5

        microtasks = []
        for i in range(min(file_count, 10)):  # Cap at 10 microtasks
            microtask = {
                "id": f"{todo.get('id', 'unknown')}_file_{i+1}",
                "title": f"Process file {i+1} of {file_count}",
                "description": f"Handle individual file processing for {title}",
                "estimated_duration": "15min",
                "status": "pending",
                "created_at": datetime.now(),
                "type": "file_processing",
            }
            microtasks.append(microtask)

        return microtasks

    def _generate_component_based_microtasks(self, todo):
        """Generate microtasks for component-based work"""
        components = [
            "Setup",
            "Configuration",
            "Implementation",
            "Testing",
            "Documentation",
        ]

        microtasks = []
        for i, component in enumerate(components):
            microtask = {
                "id": f"{todo.get('id', 'unknown')}_comp_{i+1}",
                "title": f"{component} Phase",
                "description": f"Complete {component.lower()} phase for {todo.get('title', '')}",
                "estimated_duration": "30min",
                "status": "pending",
                "created_at": datetime.now(),
                "type": "component_work",
            }
            microtasks.append(microtask)

        return microtasks

    def _generate_refactoring_microtasks(self, todo):
        """Generate microtasks for refactoring work"""
        phases = ["Analysis", "Planning", "Implementation", "Testing", "Validation"]

        microtasks = []
        for i, phase in enumerate(phases):
            microtask = {
                "id": f"{todo.get('id', 'unknown')}_refactor_{i+1}",
                "title": f"{phase} Phase",
                "description": f"Complete {phase.lower()} phase for refactoring {todo.get('title', '')}",
                "estimated_duration": "45min",
                "status": "pending",
                "created_at": datetime.now(),
                "type": "refactoring",
            }
            microtasks.append(microtask)

        return microtasks

    def _generate_generic_microtasks(self, todo):
        """Generate generic microtasks for any complex TODO"""
        phases = ["Research", "Planning", "Implementation", "Testing", "Documentation"]

        microtasks = []
        for i, phase in enumerate(phases):
            microtask = {
                "id": f"{todo.get('id', 'unknown')}_generic_{i+1}",
                "title": f"{phase} Phase",
                "description": f"Complete {phase.lower()} phase for {todo.get('title', '')}",
                "estimated_duration": "30min",
                "status": "pending",
                "created_at": datetime.now(),
                "type": "generic",
            }
            microtasks.append(microtask)

        return microtasks

    def _save_microtasks(self, todo_id, microtasks):
        """Save microtasks to file"""
        try:
            filename = f"microtasks_{todo_id}.json"
            filepath = self.microtasks_dir / filename

            data = {
                "todo_id": todo_id,
                "created_at": datetime.now().isoformat(),
                "microtasks": microtasks,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved microtasks to {filepath}")

        except Exception as e:
            logger.error(f"Error saving microtasks: {e}")

    def _process_microtasks(self):
        """Process pending microtasks"""
        try:
            total_microtasks = 0
            pending_microtasks = 0

            for todo_id, breakdown_data in self.microtasks_cache.items():
                microtasks = breakdown_data.get("microtasks", [])
                total_microtasks += len(microtasks)

                for microtask in microtasks:
                    if microtask["status"] == "pending":
                        pending_microtasks += 1
                        # Process a few microtasks
                        if pending_microtasks <= 3:
                            self._process_microtask(microtask)

            if pending_microtasks > 0:
                logger.info(
                    f"Processed microtasks: {total_microtasks} total, {pending_microtasks} pending"
                )

        except Exception as e:
            logger.error(f"Error processing microtasks: {e}")

    def _process_microtask(self, microtask):
        """Process a single microtask"""
        try:
            microtask_id = microtask["id"]
            title = microtask["title"]

            logger.info(f"Processing microtask: {title}")

            # Simulate processing work
            time.sleep(1)

            # Mark as completed
            microtask["status"] = "completed"
            microtask["completed_at"] = datetime.now()

            logger.info(f"Completed microtask: {title}")

        except Exception as e:
            logger.error(
                f"Error processing microtask {microtask.get('id', 'unknown')}: {e}"
            )

    def _update_breakdown_stats(self):
        """Update breakdown statistics"""
        try:
            stats = {
                "total_breakdowns": len(self.breakdown_history),
                "total_microtasks": sum(
                    len(data.get("microtasks", []))
                    for data in self.microtasks_cache.values()
                ),
                "pending_microtasks": sum(
                    1
                    for data in self.microtasks_cache.values()
                    for microtask in data.get("microtasks", [])
                    if microtask.get("status") == "pending"
                ),
                "completed_microtasks": sum(
                    1
                    for data in self.microtasks_cache.values()
                    for microtask in data.get("microtasks", [])
                    if microtask.get("status") == "completed"
                ),
                "last_update": datetime.now().isoformat(),
            }

            # Save stats to file
            stats_file = self.microtasks_dir / "breakdown_stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, default=str)

            logger.info(
                f"Updated breakdown stats: {stats['completed_microtasks']}/{stats['total_microtasks']} microtasks completed"
            )

        except Exception as e:
            logger.error(f"Error updating breakdown stats: {e}")

    def get_engine_status(self):
        """Get engine status"""
        try:
            total_microtasks = sum(
                len(data.get("microtasks", []))
                for data in self.microtasks_cache.values()
            )
            pending_microtasks = sum(
                1
                for data in self.microtasks_cache.values()
                for microtask in data.get("microtasks", [])
                if microtask.get("status") == "pending"
            )
            completed_microtasks = sum(
                1
                for data in self.microtasks_cache.values()
                for microtask in data.get("microtasks", [])
                if microtask.get("status") == "completed"
            )

            return {
                "engine_active": self.engine_active,
                "total_breakdowns": len(self.breakdown_history),
                "total_microtasks": total_microtasks,
                "pending_microtasks": pending_microtasks,
                "completed_microtasks": completed_microtasks,
                "completion_rate": (
                    f"{(completed_microtasks/total_microtasks*100):.1f}%"
                    if total_microtasks > 0
                    else "0%"
                ),
                "last_update": datetime.now().isoformat(),
                "microtasks_directory": str(self.microtasks_dir),
            }
        except Exception as e:
            logger.error(f"Error getting engine status: {e}")
            return {"error": str(e)}


def main():
    """Main entry point"""
    try:
        print("⚡ Task Breakdown Engine Starting...")
        print("=" * 50)

        engine = TaskBreakdownEngine()

        # Display initial status
        status = engine.get_engine_status()
        print(f"📊 Engine Status:")
        for key, value in status.items():
            if key not in ["microtasks_directory"]:
                print(f"   {key}: {value}")

        print(
            f"\n📁 Microtasks Directory: {status.get('microtasks_directory', 'Unknown')}"
        )
        print("\n🚀 Starting breakdown loop...")
        print("   - Finding complex TODOs")
        print("   - Breaking down into microtasks")
        print("   - Processing microtasks")
        print("   - Updating statistics")
        print("\n⚠️  Press Ctrl+C to stop")

        # Start breakdown loop
        engine.start_breakdown_loop()

    except KeyboardInterrupt:
        print("\n🛑 Task Breakdown Engine stopped by user")
    except Exception as e:
        print(f"❌ Task Breakdown Engine error: {e}")
        logger.error(f"Engine error: {e}")


if __name__ == "__main__":
    main()
