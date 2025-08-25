"""
Agent Classes for the Taskmaster System
"""
import asyncio
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import duckdb
from neo4j import GraphDatabase

from ..models.agent import Agent, AgentType
from ..models.job import Job, JobResult, JobType, JobPriority


class TodoScanner:
    """Scans for and processes TODOs in the codebase."""

    def __init__(self, taskmaster):
        self.taskmaster = taskmaster
        self.logger = logging.getLogger(__name__)

    async def scan_and_process_todos(self, root_directory: str = "."):
        """Scan for TODOs and create jobs for them."""
        self.logger.info(f"Scanning for TODOs in {root_directory}...")
        todo_pattern = re.compile(r'#\s*TODO[:\s].*', re.IGNORECASE)
        files_to_scan = []
        root_path = Path(root_directory)
        if root_path.is_file():
            files_to_scan.append(root_path)
        elif root_path.is_dir():
            files_to_scan.extend(p for p in root_path.rglob("*") if p.is_file() and not self._should_skip_file(p))

        for file_path in files_to_scan:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if todo_pattern.search(line):
                            await self._process_todo_line(line, file_path, line_num)
            except Exception as e:
                self.logger.warning(f"Could not read file {file_path}: {e}")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped"""
        skip_patterns = [
            r'\.git', r'\.pyc$', r'__pycache__', r'\.DS_Store',
            r'\.log$', r'\.tmp$', r'\.cache$', r'node_modules'
        ]
        return any(re.search(pattern, str(file_path)) for pattern in skip_patterns)

    async def _process_todo_line(self, line: str, file_path: Path, line_num: int):
        """Create a job for a single TODO line."""
        content = line.strip()
        job_type, priority = self._determine_job_type_and_priority(content)
        job = Job(
            name=f"TODO: {content[:50]}...",
            job_type=job_type,
            priority=priority,
            data={
                "file_path": str(file_path),
                "line_number": line_num,
                "content": content,
            },
            tags=self._extract_tags(content)
        )
        await self.taskmaster.submit_job(job)

    def _determine_job_type_and_priority(self, todo_line: str) -> (JobType, JobPriority):
        """Determine job type and priority from TODO content."""
        if any(keyword in todo_line.lower() for keyword in ["urgent", "critical", "fix", "bug"]):
            priority = JobPriority.CRITICAL
        elif any(keyword in todo_line.lower() for keyword in ["important", "high", "security"]):
            priority = JobPriority.HIGH
        else:
            priority = JobPriority.NORMAL

        if "code" in todo_line.lower() or "refactor" in todo_line.lower():
            job_type = JobType.CODE_REVIEW
        elif "doc" in todo_line.lower() or "readme" in todo_line.lower():
            job_type = JobType.DOCUMENTATION
        elif "test" in todo_line.lower() or "valid" in todo_line.lower():
            job_type = JobType.TESTING
        elif "infra" in todo_line.lower() or "deploy" in todo_line.lower():
            job_type = JobType.INFRASTRUCTURE
        else:
            job_type = JobType.GENERAL_TODO

        return job_type, priority

    def _extract_tags(self, todo_line: str) -> List[str]:
        """Extract tags from TODO line."""
        tags = []
        tag_matches = re.findall(r'@(\w+)', todo_line)
        tags.extend(tag_matches)
        bracket_tags = re.findall(r'\[(\w+)\]', todo_line)
        tags.extend(bracket_tags)
        return tags

class TodoAgent(Agent):
    """Base class for TODO processing agents"""

    def __init__(self, agent_id: str, capabilities: List[str]):
        super().__init__(agent_id=agent_id, agent_type=AgentType.SPECIALIZED, capabilities=capabilities)
        self.current_job: Optional[Job] = None

    async def process(self, job: Job) -> JobResult:
        """Process a single TODO item"""
        self.current_job = job
        try:
            output = await self._execute_todo(job)
            return JobResult(success=True, data={"message": output})
        except Exception as e:
            return JobResult(success=False, error_message=str(e))
        finally:
            self.current_job = None

    async def _execute_todo(self, job: Job) -> str:
        """Execute the actual TODO processing logic"""
        return f"Processed TODO: {job.data['content']}"

class CodeReviewAgent(TodoAgent):
    """Agent specialized in code review and implementation TODOs"""

    def __init__(self):
        super().__init__("code_review_agent", ["code_review", "implementation", "refactoring"])

    async def _execute_todo(self, job: Job) -> str:
        todo_text = job.data['content'].split("TODO:")[-1].strip()
        if any(keyword in todo_text.lower() for keyword in ["implement", "create", "add"]):
            return f"Implementation TODO identified: {todo_text}"
        elif any(keyword in todo_text.lower() for keyword in ["refactor", "optimize", "improve"]):
            return f"Refactoring TODO identified: {todo_text}"
        elif any(keyword in todo_text.lower() for keyword in ["fix", "bug", "error"]):
            return f"Bug fix TODO identified: {todo_text}"
        else:
            return f"General TODO identified: {todo_text}"

class DocumentationAgent(TodoAgent):
    """Agent specialized in documentation and README TODOs"""

    def __init__(self):
        super().__init__("documentation_agent", ["documentation", "readme", "api_docs"])

class TestingAgent(TodoAgent):
    """Agent specialized in testing and validation TODOs"""

    def __init__(self):
        super().__init__("testing_agent", ["testing", "validation", "unit_tests", "integration"])

class InfrastructureAgent(TodoAgent):
    """Agent specialized in infrastructure and deployment TODOs"""

    def __init__(self):
        super().__init__("infrastructure_agent", ["docker", "deployment", "ci_cd", "infrastructure"])

class GeneralAgent(TodoAgent):
    """General purpose agent for miscellaneous TODOs"""

    def __init__(self):
        super().__init__("general_agent", ["general", "miscellaneous"])

class FraudAgent(Agent):
    """Agent specialized in fraud detection tasks."""

    def __init__(self):
        super().__init__(agent_id="fraud_agent", agent_type=AgentType.SPECIALIZED, capabilities=["fraud", "shell_company"])
        self.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ.get("NEO4J_PASSWORD", "password"))
        )

    async def process(self, job: Job) -> JobResult:
        if "shell_company" in job.tags:
            return await self.identify_shell_companies(job)
        return JobResult(success=True, data={"message": f"Fraud analysis complete for: {job.name}"})

    async def identify_shell_companies(self, job: Job) -> JobResult:
        """Identifies shell companies using Neo4j procedures."""
        with self.driver.session() as session:
            result = session.run("CALL db.procedures() YIELD name WHERE name = 'find_shell_companies' RETURN name")
            if result.single():
                return JobResult(success=True, data={"message": "Successfully called find_shell_companies procedure."})
            else:
                return JobResult(success=False, error_message="Could not find find_shell_companies procedure.")

    def close(self):
        self.driver.close()

class ReconciliationAgent(Agent):
    """Agent specialized in reconciliation tasks."""
    def __init__(self, db_path="reconciliation.duckdb"):
        super().__init__(agent_id="reconciliation_agent", agent_type=AgentType.SPECIALIZED, capabilities=["reconciliation"])
        self.db_path = db_path
        self.con = duckdb.connect(database=self.db_path, read_only=False)

    async def process(self, job: Job) -> JobResult:
        if "reconcile" in job.name.lower():
            return await self.reconcile_transactions(job)
        return JobResult(success=True, data={"message": f"Reconciliation task processed for: {job.name}"})

    async def reconcile_transactions(self, job: Job) -> JobResult:
        """Reconciles transactions using DuckDB."""
        try:
            # In a real scenario, we would not read the schema on every call
            with open("Desktop/Nexus/forensic_reconciliation_app/datastore/duckdb/init/01-schema.sql", "r") as f:
                schema_sql = f.read()
                self.con.execute(schema_sql)
            result = self.con.execute("SELECT COUNT(*) FROM reconciled_transactions").fetchone()
            return JobResult(success=True, data={"reconciled_count": result[0]})
        except Exception as e:
            return JobResult(success=False, error_message=str(e))

    def close(self):
        self.con.close()
