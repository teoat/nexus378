#!/usr/bin/env python3
Working TODO Reader
Reads the actual TODO_MASTER.md format

import logging
import re

logger = logging.getLogger(__name__)

class WorkingTodoReader:

            if "core" in str(current_dir):
                # We're in the core directory, go up to find TODO_MASTER.md
                self.todo_master_path = (
                    current_dir.parent.parent.parent.parent / "TODO_MASTER.md"
                )
            else:
                # Try to find it in the project root
                self.todo_master_path = current_dir / "TODO_MASTER.md"

        logger.info(f"Working TODO Master path: {self.todo_master_path}")
        logger.info(f"Path exists: {self.todo_master_path.exists()}")

        # If the path doesn't exist, try alternative paths
        if not self.todo_master_path.exists():
            alternative_paths = [
                current_dir.parent.parent.parent.parent / "TODO_MASTER.md",
                current_dir.parent.parent.parent / "TODO_MASTER.md",
                current_dir.parent.parent / "TODO_MASTER.md",
                current_dir.parent / "TODO_MASTER.md",
                current_dir / "TODO_MASTER.md",
            ]

            for alt_path in alternative_paths:
                if alt_path.exists():
                    self.todo_master_path = alt_path
                    logger.info(f"Found TODO_MASTER.md at alternative path: {alt_path}")
                    break

    def read_todo_master(self) -> List[Dict[str, Any]]:

            logger.error(f"TODO_MASTER.md not found at: {self.todo_master_path}")
            return []

        try:
            with open(self.todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self._parse_actual_format(content)

        except Exception as e:
            logger.error(f"Error reading TODO_MASTER.md: {e}")
            return []

    def _parse_actual_format(self, content: str) -> List[Dict[str, Any]]:

        pattern = r"(\d+)\.\s*\*\*🔄\s*([^*]+):\s*([^*]+)\*\*\s*-\s*([^-]+)\s*Priority\s*-\s*([^-]+)\s*-\s*(.+)"

        matches = re.findall(pattern, content, re.MULTILINE)

        for match in matches:
            number, todo_id, description, priority, duration, phase = match

            # Clean up the extracted values
            todo_id = todo_id.strip()
            description = description.strip()
            priority = priority.strip()
            duration = duration.strip()
            phase = phase.strip()

            # Determine capabilities based on task type
            capabilities = self._determine_capabilities(todo_id, description)

            todo = {
                "id": todo_id,
                "name": description,
                "description": f"{description} - {phase}",
                "priority": self._normalize_priority(priority),
                "estimated_duration": duration,
                "required_capabilities": capabilities,
                "section": phase,
                "status": "pending",
                "number": int(number),
            }

            todos.append(todo)
            logger.debug(f"Extracted TODO: {todo_id} - {description}")

        logger.info(f"Successfully parsed {len(todos)} TODO items from TODO_MASTER.md")
        return todos

    def _normalize_priority(self, priority: str) -> str:

        if "high" in priority_lower:
            return "HIGH"
        elif "medium" in priority_lower:
            return "NORMAL"
        elif "low" in priority_lower:
            return "LOW"
        else:
            return "NORMAL"

    def _determine_capabilities(self, todo_id: str, description: str) -> List[str]:

        if "deploy" in todo_lower:
            capabilities.extend(["deployment", "devops", "infrastructure"])

        # Docker tasks
        if "docker" in desc_lower:
            capabilities.extend(["docker", "containerization", "devops"])

        # Kubernetes tasks
        if "kubernetes" in desc_lower:
            capabilities.extend(["kubernetes", "orchestration", "devops"])

        # API tasks
        if "api" in desc_lower:
            capabilities.extend(["api_development", "backend", "integration"])

        # Database tasks
        if "database" in desc_lower or "migration" in desc_lower:
            capabilities.extend(["database", "data_management", "backend"])

        # Security tasks
        if "ssl" in desc_lower or "tls" in desc_lower or "certificate" in desc_lower:
            capabilities.extend(["security", "ssl_tls", "certificates"])

        # Monitoring tasks
        if "monitoring" in desc_lower or "health" in desc_lower:
            capabilities.extend(["monitoring", "observability", "devops"])

        # CI/CD tasks
        if "ci/cd" in desc_lower or "pipeline" in desc_lower:
            capabilities.extend(["ci_cd", "automation", "devops"])

        # If no specific capabilities found, add general ones
        if not capabilities:
            capabilities = ["general_implementation", "devops", "backend"]

        return capabilities
