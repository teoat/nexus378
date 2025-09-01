#!/usr/bin/env python3
Corrected TODO Master Reader
Properly reads and parses the real TODO_MASTER.md format

import logging
import re

logger = logging.getLogger(__name__)

class CorrectedTodoMasterReader:

            if "core" in str(current_dir):
                # We're in the core directory, go up to find TODO_MASTER.md
                self.todo_master_path = (
                    current_dir.parent.parent.parent / "TODO_MASTER.md"
                )
            else:
                # Try to find it in the project root
                self.todo_master_path = current_dir / "TODO_MASTER.md"

        logger.info(f"Corrected TODO Master path: {self.todo_master_path}")

    def read_todo_master(self) -> List[Dict[str, Any]]:

            logger.error(f"TODO_MASTER.md not found at: {self.todo_master_path}")
            return []

        try:
            with open(self.todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self._parse_real_markdown_content(content)

        except Exception as e:
            logger.error(f"Error reading TODO_MASTER.md: {e}")
            return []

    def _parse_real_markdown_content(self, content: str) -> List[Dict[str, Any]]:

        sections = content.split("\n## ")

        for section in sections:
            if not section.strip():
                continue

            # Look for TODO items in each section
            section_todos = self._extract_real_todos_from_section(section)
            todos.extend(section_todos)

        logger.info(f"Correctly parsed {len(todos)} TODO items from TODO_MASTER.md")
        return todos

    def _extract_real_todos_from_section(self, section: str) -> List[Dict[str, Any]]:

        lines = section.split("\n")
        section_title = lines[0].strip() if lines else "Unknown"

        for line in lines:
            line = line.strip()

            # Look for the real TODO format: - [ ] **Task Name**: Description
            if line.startswith("- [ ]") and "**" in line:
                # Extract task name and description
                task_match = re.search(r"-\s*\[ \]\s*\*\*([^*]+)\*\*:\s*(.+)", line)
                if task_match:
                    task_name = task_match.group(1).strip()
                    description = task_match.group(2).strip()

                    # Determine priority based on context
                    priority = self._determine_real_priority(section_title, task_name)

                    # Determine capabilities based on task type
                    capabilities = self._determine_real_capabilities(
                        task_name, description
                    )

                    # Determine duration based on task complexity
                    duration = self._determine_real_duration(task_name, description)

                    todo = {
                        "id": f"todo_{len(todos) + 1:03d}",
                        "name": task_name,
                        "description": description,
                        "priority": priority,
                        "estimated_duration": duration,
                        "required_capabilities": capabilities,
                        "section": section_title,
                        "status": "pending",
                        "original_line": line,
                    }

                    todos.append(todo)
                    logger.debug(
                        f"Extracted TODO: {task_name} from section: {section_title}"
                    )

        return todos

    def _determine_real_priority(self, section_title: str, task_name: str) -> str:

            for word in ["critical", "immediate", "action required"]
        ):
            return "HIGH"

        # High priority for security and syntax issues
        if any(
            word in task_lower for word in ["syntax", "security", "critical", "urgent"]
        ):
            return "HIGH"

        # Medium priority for quality improvements
        if any(
            word in task_lower
            for word in ["formatting", "pylint", "documentation", "import"]
        ):
            return "NORMAL"

        # Default to normal
        return "NORMAL"

    def _determine_real_capabilities(
        self, task_name: str, description: str
    ) -> List[str]:

            word in task_lower for word in ["syntax", "formatting", "pylint", "import"]
        ):
            capabilities.extend(
                ["python_development", "code_quality", "general_implementation"]
            )

        # Security tasks
        if any(
            word in task_lower for word in ["security", "authentication", "encryption"]
        ):
            capabilities.extend(["security", "authentication", "encryption"])

        # Documentation tasks
        if any(word in task_lower for word in ["documentation", "docstrings"]):
            capabilities.extend(["documentation", "technical_writing"])

        # Performance tasks
        if any(word in task_lower for word in ["performance", "optimization"]):
            capabilities.extend(["performance", "optimization"])

        # Error handling tasks
        if any(word in task_lower for word in ["error", "exception", "handling"]):
            capabilities.extend(["python_development", "error_handling"])

        # If no specific capabilities found, add general ones
        if not capabilities:
            capabilities = ["python_development", "general_implementation"]

        return capabilities

    def _determine_real_duration(self, task_name: str, description: str) -> str:

        if "syntax" in task_lower:
            return "1-2 hours"

        # Formatting and import cleanup
        if any(word in task_lower for word in ["formatting", "import", "pylint"]):
            return "2-4 hours"

        # Documentation and error handling
        if any(word in task_lower for word in ["documentation", "error", "handling"]):
            return "3-5 hours"

        # Performance and optimization
        if any(word in task_lower for word in ["performance", "optimization"]):
            return "4-6 hours"

        # Default duration
        return "2-4 hours"

    def get_section_summary(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:

            section = todo.get("section", "Unknown")
            if section not in section_summary:
                section_summary[section] = {
                    "count": 0,
                    "high_priority": 0,
                    "normal_priority": 0,
                    "todos": [],
                }

            section_summary[section]["count"] += 1
            section_summary[section]["todos"].append(todo)

            if todo.get("priority") == "HIGH":
                section_summary[section]["high_priority"] += 1
            else:
                section_summary[section]["normal_priority"] += 1

        return section_summary
