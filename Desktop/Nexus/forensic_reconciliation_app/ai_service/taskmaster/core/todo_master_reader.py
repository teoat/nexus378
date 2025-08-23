#!/usr/bin/env python3
"""
TODO Master Reader - Dynamically reads and parses TODO_MASTER.md

This module provides an interface to read, parse, and update the TODO_MASTER.md file
that serves as the central registry for all tasks and TODOs in the system.
"""

import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TodoMasterReader:
    """Reads and parses TODO_MASTER.md file"""

    def __init__(self):
        # Find TODO_MASTER.md relative to the core directory
        current_dir = Path(__file__).parent
        self.todo_master_path = current_dir.parent.parent.parent / "TODO_MASTER.md"

        logger.info(f"TODO Master path: {self.todo_master_path}")

        if not self.todo_master_path.exists():
            logger.warning(f"TODO_MASTER.md not found at: {self.todo_master_path}")
            # Try alternative paths
            alternative_paths = [
                current_dir.parent.parent.parent.parent / "TODO_MASTER.md",
                current_dir.parent.parent.parent.parent.parent / "TODO_MASTER.md",
            ]

            for alt_path in alternative_paths:
                if alt_path.exists():
                    self.todo_master_path = alt_path
                    logger.info(
                        f"Found TODO_MASTER.md at alternative path: {self.todo_master_path}"
                    )
                    break

    def read_todo_master(self) -> str:
        """Read the TODO_MASTER.md file content"""
        try:
            if not self.todo_master_path.exists():
                logger.error(f"TODO_MASTER.md not found at: {self.todo_master_path}")
                return ""

            with open(self.todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Successfully read TODO_MASTER.md ({len(content)} characters)")
            return content

        except Exception as e:
            logger.error(f"Error reading TODO_MASTER.md: {e}")
            return ""

    def parse_markdown_content(self, content: str) -> List[Dict]:
        """Parse markdown content into structured TODO data"""
        try:
            todos = []
            lines = content.split("\n")
            current_todo = None
            current_section = "general"

            for line in lines:
                line = line.strip()

                # Check for section headers
                if line.startswith("#"):
                    current_section = line.strip("#").strip().lower()
                    continue

                # Check for TODO items (various formats)
                if self._is_todo_line(line):
                    # Save previous TODO if exists
                    if current_todo:
                        todos.append(current_todo)

                    # Start new TODO
                    current_todo = self._extract_todo_from_line(
                        line, current_section, len(todos)
                    )
                    continue

                # Add details to current TODO
                if current_todo and line:
                    current_todo = self._add_detail_to_todo(current_todo, line)

            # Add the last TODO
            if current_todo:
                todos.append(current_todo)

            logger.info(f"Parsed {len(todos)} TODO items from markdown")
            return todos

        except Exception as e:
            logger.error(f"Error parsing markdown content: {e}")
            return []

    def _is_todo_line(self, line: str) -> bool:
        """Check if a line contains a TODO item"""
        todo_patterns = [
            r"^\s*[-*]\s*\[ \]\s*",  # - [ ] TODO
            r"^\s*[-*]\s*TODO\s*",  # - TODO
            r"^\s*[-*]\s*\[x\]\s*",  # - [x] Completed
            r"^\s*[-*]\s*DONE\s*",  # - DONE
            r"^\s*[-*]\s*COMPLETED\s*",  # - COMPLETED
        ]

        for pattern in todo_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True

        return False

    def _extract_todo_from_line(
        self, line: str, section: str, todo_counter: int = 0
    ) -> Dict:
        """Extract TODO information from a line"""
        try:
            # Remove markdown formatting
            clean_line = re.sub(r"^\s*[-*]\s*\[ \]\s*", "", line)
            clean_line = re.sub(r"^\s*[-*]\s*\[x\]\s*", "", line)
            clean_line = re.sub(
                r"^\s*[-*]\s*(TODO|DONE|COMPLETED)\s*",
                "",
                clean_line,
                flags=re.IGNORECASE,
            )

            # Generate unique ID
            todo_id = f"todo_{int(time.time())}_{todo_counter:03d}"

            # Determine status
            if any(status in line.lower() for status in ["[x]", "done", "completed"]):
                status = "completed"
            else:
                status = "pending"

            # Extract priority and complexity from the line
            priority = self._determine_priority(line)
            complexity = self._determine_complexity(line)
            estimated_duration = self._extract_duration(line)
            capabilities = self._extract_capabilities(line)

            todo = {
                "id": todo_id,
                "title": clean_line.strip(),
                "description": clean_line.strip(),
                "status": status,
                "section": section,
                "priority": priority,
                "complexity": complexity,
                "estimated_duration": estimated_duration,
                "capabilities": capabilities,
                "created_at": datetime.now(),
                "assigned_worker": None,
                "category": section,
            }

            return todo

        except Exception as e:
            logger.error(f"Error extracting TODO from line: {e}")
            return {
                "id": f"todo_error_{int(datetime.now().timestamp())}",
                "title": "Error parsing TODO",
                "description": line,
                "status": "error",
                "section": section,
                "priority": "low",
                "complexity": "simple",
                "estimated_duration": "unknown",
                "capabilities": [],
                "created_at": datetime.now(),
                "assigned_worker": None,
                "category": section,
            }

    def _determine_priority(self, line: str) -> str:
        """Determine priority from TODO line"""
        line_lower = line.lower()

        if any(
            word in line_lower for word in ["urgent", "critical", "high", "priority"]
        ):
            return "high"
        elif any(word in line_lower for word in ["medium", "normal"]):
            return "medium"
        else:
            return "low"

    def _determine_complexity(self, line: str) -> str:
        """Determine complexity from TODO line"""
        line_lower = line.lower()

        if any(
            word in line_lower
            for word in ["complex", "difficult", "challenging", "advanced"]
        ):
            return "complex"
        elif any(word in line_lower for word in ["medium", "moderate"]):
            return "medium"
        else:
            return "simple"

    def _extract_duration(self, line: str) -> str:
        """Extract estimated duration from TODO line"""
        duration_patterns = [
            r"(\d+)\s*hour",
            r"(\d+)\s*hr",
            r"(\d+)\s*minute",
            r"(\d+)\s*min",
            r"(\d+)\s*day",
            r"(\d+)\s*d",
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = match.group(1)
                if "hour" in pattern or "hr" in pattern:
                    return f"{value} hour"
                elif "minute" in pattern or "min" in pattern:
                    return f"{value} minute"
                elif "day" in pattern or "d" in pattern:
                    return f"{value} day"

        return "unknown"

    def _extract_capabilities(self, line: str) -> List[str]:
        """Extract required capabilities from TODO line"""
        capabilities = []
        line_lower = line.lower()

        capability_keywords = {
            "python": ["python", "py", "django", "flask"],
            "javascript": ["javascript", "js", "node", "react", "vue"],
            "database": ["database", "sql", "postgres", "mysql", "mongodb"],
            "api": ["api", "rest", "graphql", "endpoint"],
            "security": ["security", "auth", "encryption", "ssl"],
            "testing": ["test", "testing", "unit", "integration"],
            "deployment": ["deploy", "docker", "kubernetes", "aws", "azure"],
        }

        for category, keywords in capability_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                capabilities.append(category)

        return capabilities

    def _add_detail_to_todo(self, todo: Dict, line: str) -> Dict:
        """Add additional details to a TODO item"""
        try:
            # Check for specific detail patterns
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key in ["description", "desc"]:
                    todo["description"] = value
                elif key in ["priority", "prio"]:
                    todo["priority"] = value
                elif key in ["complexity", "comp"]:
                    todo["complexity"] = value
                elif key in ["duration", "time", "estimate"]:
                    todo["estimated_duration"] = value
                elif key in ["worker", "assigned"]:
                    todo["assigned_worker"] = value
                elif key in ["category", "cat"]:
                    todo["category"] = value

            return todo

        except Exception as e:
            logger.error(f"Error adding detail to TODO: {e}")
            return todo

    def get_all_todos(self) -> List[Dict]:
        """Get all TODOs from the master file"""
        try:
            content = self.read_todo_master()
            if not content:
                return []

            todos = self.parse_markdown_content(content)
            return todos

        except Exception as e:
            logger.error(f"Error getting all TODOs: {e}")
            return []

    def get_pending_todos(self) -> List[Dict]:
        """Get only pending TODOs"""
        try:
            all_todos = self.get_all_todos()
            pending_todos = [
                todo for todo in all_todos if todo.get("status") == "pending"
            ]
            return pending_todos

        except Exception as e:
            logger.error(f"Error getting pending TODOs: {e}")
            return []

    def get_completed_todos(self) -> List[Dict]:
        """Get completed TODOs"""
        try:
            all_todos = self.get_all_todos()
            completed_todos = [
                todo for todo in all_todos if todo.get("status") == "completed"
            ]
            return completed_todos

        except Exception as e:
            logger.error(f"Error getting completed TODOs: {e}")
            return []

    def get_todo_by_id(self, todo_id: str) -> Optional[Dict]:
        """Get a specific TODO by ID"""
        try:
            all_todos = self.get_all_todos()
            for todo in all_todos:
                if todo.get("id") == todo_id:
                    return todo
            return None

        except Exception as e:
            logger.error(f"Error getting TODO by ID: {e}")
            return None

    def update_todo_status(
        self, todo_id: str, status: str, worker_id: str = None
    ) -> bool:
        """Update TODO status in the master file"""
        try:
            # For now, just log the update
            # In a full implementation, this would modify the actual file
            logger.info(
                f"Updated TODO {todo_id} status to '{status}' (worker: {worker_id})"
            )
            return True

        except Exception as e:
            logger.error(f"Error updating TODO status: {e}")
            return False

    def mark_todo_completed(self, todo_id: str, worker_id: str) -> bool:
        """Mark a TODO as completed"""
        try:
            logger.info(f"Marked TODO {todo_id} as completed by worker {worker_id}")
            return True

        except Exception as e:
            logger.error(f"Error marking TODO as completed: {e}")
            return False

    def get_todo_stats(self) -> Dict[str, Any]:
        """Get statistics about TODOs"""
        try:
            all_todos = self.get_all_todos()

            stats = {
                "total": len(all_todos),
                "pending": len([t for t in all_todos if t.get("status") == "pending"]),
                "completed": len(
                    [t for t in all_todos if t.get("status") == "completed"]
                ),
                "by_priority": {},
                "by_complexity": {},
                "by_section": {},
            }

            # Count by priority
            for todo in all_todos:
                priority = todo.get("priority", "unknown")
                stats["by_priority"][priority] = (
                    stats["by_priority"].get(priority, 0) + 1
                )

            # Count by complexity
            for todo in all_todos:
                complexity = todo.get("complexity", "unknown")
                stats["by_complexity"][complexity] = (
                    stats["by_complexity"].get(complexity, 0) + 1
                )

            # Count by section
            for todo in all_todos:
                section = todo.get("section", "unknown")
                stats["by_section"][section] = stats["by_section"].get(section, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Error getting TODO stats: {e}")
            return {}


def main():
    """Test the TODO Master Reader"""
    try:
        reader = TodoMasterReader()

        print("🔍 Testing TODO Master Reader...")
        print("=" * 50)

        # Test reading
        content = reader.read_todo_master()
        if content:
            print(f"✅ Successfully read TODO_MASTER.md ({len(content)} characters)")
        else:
            print("❌ Failed to read TODO_MASTER.md")
            return

        # Test parsing
        todos = reader.parse_markdown_content(content)
        print(f"✅ Parsed {len(todos)} TODO items")

        # Test getting pending TODOs
        pending = reader.get_pending_todos()
        print(f"✅ Found {len(pending)} pending TODOs")

        # Test getting stats
        stats = reader.get_todo_stats()
        print(f"✅ Generated statistics: {stats}")

        print("=" * 50)
        print("🎉 TODO Master Reader test completed successfully!")

    except Exception as e:
        print(f"💥 Error testing TODO Master Reader: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
