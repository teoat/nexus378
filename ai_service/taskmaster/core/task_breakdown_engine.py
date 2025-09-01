#!/usr/bin/env python3
Task Breakdown Engine - Converts complex TODOs to microtasks
Tab 10 of the 11-tab system

import json
import logging
import sys
import time
from datetime import datetime

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TaskBreakdownEngine:

            "max_microtasks_per_todo": 20,  # Increased from default
            "min_microtasks_per_todo": 5,  # Minimum microtasks per TODO
            "parallel_breakdown_limit": 5,  # Process 5 TODOs simultaneously
            "microtask_complexity_levels": ["simple", "medium", "complex"],
        }

        # Create microtasks directory
        self.microtasks_dir = current_dir / "microtasks"
        self.microtasks_dir.mkdir(exist_ok=True)

        logger.info("Enhanced Task Breakdown Engine initialized for 32-worker system")
        logger.info(f"Microtasks directory: {self.microtasks_dir}")
        logger.info(f"Settings: {self.microtask_settings}")

    def start_breakdown_loop(self):

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

            logger.info(f"Found {len(complex_todos)} complex TODOs for breakdown")

            # Process multiple complex TODOs simultaneously for 32-worker system
            for todo in complex_todos[
                : self.microtask_settings["parallel_breakdown_limit"]
            ]:
                if not self._is_already_breakdown(todo):
                    self._breakdown_todo(todo)
                    time.sleep(1)  # Reduced pause for faster processing

        except Exception as e:
            logger.error(f"Error finding complex TODOs: {e}")

    def _is_complex_todo(self, todo):

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

        todo_id = todo.get("id", "unknown")
        return todo_id in self.microtasks_cache

    def _breakdown_todo(self, todo):

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

        title = todo.get("title", "")
        description = todo.get("description", "")

        microtasks = []

        # Enhanced analysis for 32-worker system - generate more granular microtasks
        if "fix all" in title.lower() or "multiple files" in title.lower():
            # Generate file-by-file microtasks with enhanced granularity
            microtasks = self._generate_file_based_microtasks(todo)
        elif "database" in title.lower() or "api" in title.lower():
            # Generate component-based microtasks with enhanced granularity
            microtasks = self._generate_component_based_microtasks(todo)
        elif "refactor" in title.lower() or "restructure" in title.lower():
            # Generate refactoring microtasks with enhanced granularity
            microtasks = self._generate_refactoring_microtasks(todo)
        elif "deploy" in title.lower() or "deployment" in title.lower():
            # Generate deployment-specific microtasks
            microtasks = self._generate_deployment_microtasks(todo)
        else:
            # Generate generic microtasks with enhanced granularity
            microtasks = self._generate_generic_microtasks(todo)

        # Ensure minimum microtasks for better worker distribution
        if len(microtasks) < self.microtask_settings["min_microtasks_per_todo"]:
            additional_microtasks = self._generate_additional_microtasks(
                todo,
                self.microtask_settings["min_microtasks_per_todo"] - len(microtasks),
            )
            microtasks.extend(additional_microtasks)

        return microtasks

    def _generate_file_based_microtasks(self, todo):

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

    def _generate_deployment_microtasks(self, todo):

        title = todo.get("title", "")
        description = todo.get("description", "")

        microtasks = []

        # Deployment preparation microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_1",
                "title": f"Prepare deployment environment for {title[:30]}...",
                "description": "Set up deployment environment and dependencies",
                "estimated_duration": "10min",
                "complexity": "medium",
                "status": "pending",
            }
        )

        # Code review microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_2",
                "title": f"Code review and validation for {title[:30]}...",
                "description": "Review code changes and validate functionality",
                "estimated_duration": "15min",
                "complexity": "medium",
                "status": "pending",
            }
        )

        # Testing microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_3",
                "title": f"Run automated tests for {title[:30]}...",
                "description": "Execute test suite and validate results",
                "estimated_duration": "20min",
                "complexity": "medium",
                "status": "pending",
            }
        )

        # Build microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_4",
                "title": f"Build deployment package for {title[:30]}...",
                "description": "Create deployment artifacts and packages",
                "estimated_duration": "15min",
                "complexity": "medium",
                "status": "pending",
            }
        )

        # Deployment execution microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_5",
                "title": f"Execute deployment for {title[:30]}...",
                "description": "Deploy to target environment",
                "estimated_duration": "25min",
                "complexity": "high",
                "status": "pending",
            }
        )

        # Verification microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_6",
                "title": f"Verify deployment for {title[:30]}...",
                "description": "Verify deployment success and functionality",
                "estimated_duration": "20min",
                "complexity": "medium",
                "status": "pending",
            }
        )

        # Rollback preparation microtasks
        microtasks.append(
            {
                "id": f"{todo.get('id', 'unknown')}_deploy_prep_7",
                "title": f"Prepare rollback plan for {title[:30]}...",
                "description": "Create rollback procedures and documentation",
                "estimated_duration": "15min",
                "complexity": "low",
                "status": "pending",
            }
        )

        return microtasks

    def _generate_additional_microtasks(self, todo, count_needed):

                "id": f"{todo.get('id', 'unknown')}_additional_{i+1}",
                "title": f"Additional microtask {i+1} for {todo.get('title', 'Unknown')[:30]}...",
                "description": f"Supporting microtask to ensure proper task distribution",
                "estimated_duration": "10min",
                "complexity": "simple",
                "status": "pending",
            }
            additional_microtasks.append(microtask)

        return additional_microtasks

def main():

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
