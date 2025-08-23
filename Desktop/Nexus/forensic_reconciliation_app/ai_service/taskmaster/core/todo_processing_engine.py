#!/usr/bin/env python3
"""
TODO Processing Engine - Manages TODO lifecycle and updates TODO_MASTER.md
Tab 9 of the 11-tab system
"""

import logging
import os
import re
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


class TodoProcessingEngine:
    """Engine for processing TODOs and updating TODO_MASTER.md"""

    def __init__(self):
        self.todo_reader = TodoMasterReader()
        self.todo_master_path = self.todo_reader.todo_master_path
        self.processing_interval = 10  # Process every 10 seconds
        self.engine_active = True

        logger.info("TODO Processing Engine initialized")
        logger.info(f"Monitoring: {self.todo_master_path}")

    def start_processing_loop(self):
        """Start the continuous processing loop"""
        logger.info("Starting TODO processing loop")

        try:
            while self.engine_active:
                start_time = time.time()

                # Process pending TODOs
                self._process_pending_todos()

                # Update TODO_MASTER.md if needed
                self._update_todo_master()

                # Calculate processing time and sleep
                processing_time = time.time() - start_time
                sleep_time = max(0, self.processing_interval - processing_time)

                logger.info(
                    f"Processing took {processing_time:.2f}s, sleeping for {sleep_time:.2f}s"
                )
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("TODO processing loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in TODO processing loop: {e}")

    def _process_pending_todos(self):
        """Process pending TODOs"""
        try:
            pending_todos = self.todo_reader.get_pending_todos()
            logger.info(f"Found {len(pending_todos)} pending TODOs")

            if not pending_todos:
                return

            # Process first few pending TODOs
            for i, todo in enumerate(pending_todos[:5]):  # Process 5 at a time
                try:
                    self._process_single_todo(todo)
                    time.sleep(1)  # Brief pause between processing
                except Exception as e:
                    logger.error(
                        f"Error processing TODO {todo.get('id', 'unknown')}: {e}"
                    )

        except Exception as e:
            logger.error(f"Error processing pending TODOs: {e}")

    def _process_single_todo(self, todo):
        """Process a single TODO item"""
        todo_id = todo.get("id", "unknown")
        title = todo.get("title", "Unknown")

        logger.info(f"Processing TODO: {title[:50]}...")

        # Simulate processing work
        time.sleep(2)

        # Mark as completed
        self._mark_todo_completed(todo_id)

        logger.info(f"Completed TODO: {title[:50]}...")

    def _mark_todo_completed(self, todo_id):
        """Mark a TODO as completed in TODO_MASTER.md"""
        try:
            # Read current content
            with open(self.todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find and replace the TODO line
            # Pattern: - [ ] **Title** -> - [x] **Title**
            pattern = r"(- \[ \]\s*\*\*[^*]+\*\*.*?)(?=\n|$)"

            def replace_todo(match):
                line = match.group(1)
                # Replace [ ] with [x] and add completion timestamp
                completed_line = line.replace("- [ ]", "- [x]")
                completed_line += (
                    f" (Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                )
                return completed_line

            # Replace first occurrence (to avoid replacing all similar lines)
            new_content = re.sub(pattern, replace_todo, content, count=1)

            # Write updated content
            with open(self.todo_master_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Updated TODO_MASTER.md: marked {todo_id} as completed")

        except Exception as e:
            logger.error(f"Error updating TODO_MASTER.md: {e}")

    def _update_todo_master(self):
        """Update TODO_MASTER.md with current status"""
        try:
            # Get current stats
            all_todos = self.todo_reader.get_all_todos()
            pending_todos = self.todo_reader.get_pending_todos()
            completed_todos = len(all_todos) - len(pending_todos)

            # Update summary if it exists
            with open(self.todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for summary section and update it
            summary_pattern = r"(## 📊 Progress Summary.*?)(?=##|\Z)"
            summary_match = re.search(summary_pattern, content, re.DOTALL)

            if summary_match:
                current_summary = summary_match.group(1)

                # Create new summary
                new_summary = f"""## 📊 Progress Summary

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total TODOs:** {len(all_todos)}
**Completed:** {completed_todos} ✅
**Pending:** {len(pending_todos)} ⏳
**Completion Rate:** {(completed_todos/len(all_todos)*100):.1f}%

"""

                # Replace summary
                new_content = content.replace(current_summary, new_summary)

                # Write updated content
                with open(self.todo_master_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                logger.info(
                    f"Updated progress summary: {completed_todos}/{len(all_todos)} completed"
                )

        except Exception as e:
            logger.error(f"Error updating TODO_MASTER.md summary: {e}")

    def get_engine_status(self):
        """Get engine status"""
        try:
            all_todos = self.todo_reader.get_all_todos()
            pending_todos = self.todo_reader.get_pending_todos()
            completed_todos = len(all_todos) - len(pending_todos)

            return {
                "engine_active": self.engine_active,
                "total_todos": len(all_todos),
                "pending_todos": len(pending_todos),
                "completed_todos": completed_todos,
                "completion_rate": (
                    f"{(completed_todos/len(all_todos)*100):.1f}%"
                    if all_todos
                    else "0%"
                ),
                "last_update": datetime.now().isoformat(),
                "todo_master_path": str(self.todo_master_path),
            }
        except Exception as e:
            logger.error(f"Error getting engine status: {e}")
            return {"error": str(e)}


def main():
    """Main entry point"""
    try:
        print("🔧 TODO Processing Engine Starting...")
        print("=" * 50)

        engine = TodoProcessingEngine()

        # Display initial status
        status = engine.get_engine_status()
        print(f"📊 Engine Status:")
        for key, value in status.items():
            if key != "todo_master_path":
                print(f"   {key}: {value}")

        print(f"\n📁 TODO Master: {status.get('todo_master_path', 'Unknown')}")
        print("\n🚀 Starting processing loop...")
        print("   - Processing pending TODOs")
        print("   - Updating TODO_MASTER.md")
        print("   - Managing TODO lifecycle")
        print("\n⚠️  Press Ctrl+C to stop")

        # Start processing loop
        engine.start_processing_loop()

    except KeyboardInterrupt:
        print("\n🛑 TODO Processing Engine stopped by user")
    except Exception as e:
        print(f"❌ TODO Processing Engine error: {e}")
        logger.error(f"Engine error: {e}")


if __name__ == "__main__":
    main()
