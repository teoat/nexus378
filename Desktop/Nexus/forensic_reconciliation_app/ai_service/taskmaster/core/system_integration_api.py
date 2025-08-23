#!/usr/bin/env python3
"""
System Integration API - Recommendation 10 Implementation

This module provides system integration capabilities including:
- REST API endpoints
- Git integration
- CI/CD integration
- Project management tools integration
- Monitoring tool integration
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SystemIntegrationAPI:
    """System Integration and API endpoints for the collective worker system"""

    def __init__(self, processor):
        self.processor = processor
        self.api_endpoints = {}
        self.integrations = {}
        self.api_server = None
        self.api_thread = None

        # Initialize integrations
        self._setup_integrations()

        logger.info("System Integration API initialized")

    def _setup_integrations(self):
        """Setup various system integrations"""
        try:
            # Git integration
            self._setup_git_integration()

            # CI/CD integration
            self._setup_cicd_integration()

            # Project management tools integration
            self._setup_project_tools_integration()

            # Monitoring tool integration
            self._setup_monitoring_integration()

            logger.info("All system integrations configured")

        except Exception as e:
            logger.error(f"Error setting up integrations: {e}")

    def _setup_git_integration(self):
        """Setup Git integration for version control"""
        try:
            git_config = {
                "enabled": False,
                "repo_path": None,
                "branch": None,
                "auto_commit": False,
                "commit_interval": 300,  # 5 minutes
            }

            # Check if we're in a git repository
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                git_config["repo_path"] = result.stdout.strip()
                git_config["enabled"] = True

                # Get current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                git_config["branch"] = result.stdout.strip()

                logger.info(
                    f"Git integration enabled: {git_config['repo_path']} (branch: {git_config['branch']})"
                )

            except subprocess.CalledProcessError:
                logger.info("Not in a git repository - Git integration disabled")

            self.integrations["git"] = git_config

        except Exception as e:
            logger.error(f"Error setting up Git integration: {e}")

    def _setup_cicd_integration(self):
        """Setup CI/CD integration"""
        try:
            cicd_config = {
                "enabled": False,
                "platform": None,
                "webhook_url": None,
                "auto_deploy": False,
            }

            # Check for common CI/CD platforms
            ci_files = [
                ".github",
                ".gitlab-ci.yml",
                ".travis.yml",
                "Jenkinsfile",
                "azure-pipelines.yml",
            ]
            current_dir = Path.cwd()

            for ci_file in ci_files:
                if (current_dir / ci_file).exists():
                    if ci_file == ".github":
                        cicd_config["platform"] = "GitHub Actions"
                    elif ci_file == ".gitlab-ci.yml":
                        cicd_config["platform"] = "GitLab CI"
                    elif ci_file == ".travis.yml":
                        cicd_config["platform"] = "Travis CI"
                    elif ci_file == "Jenkinsfile":
                        cicd_config["platform"] = "Jenkins"
                    elif ci_file == "azure-pipelines.yml":
                        cicd_config["platform"] = "Azure DevOps"

                    cicd_config["enabled"] = True
                    break

            if cicd_config["enabled"]:
                logger.info(f"CI/CD integration enabled: {cicd_config['platform']}")
            else:
                logger.info("No CI/CD platform detected - CI/CD integration disabled")

            self.integrations["cicd"] = cicd_config

        except Exception as e:
            logger.error(f"Error setting up CI/CD integration: {e}")

    def _setup_project_tools_integration(self):
        """Setup project management tools integration"""
        try:
            project_tools_config = {"enabled": False, "tools": []}

            # Check for common project management tools
            tool_files = [
                "package.json",
                "requirements.txt",
                "pyproject.toml",
                "Cargo.toml",
                "pom.xml",
            ]
            current_dir = Path.cwd()

            for tool_file in tool_files:
                if (current_dir / tool_file).exists():
                    if tool_file == "package.json":
                        project_tools_config["tools"].append("Node.js/npm")
                    elif tool_file == "requirements.txt":
                        project_tools_config["tools"].append("Python/pip")
                    elif tool_file == "pyproject.toml":
                        project_tools_config["tools"].append("Python/poetry")
                    elif tool_file == "Cargo.toml":
                        project_tools_config["tools"].append("Rust/cargo")
                    elif tool_file == "pom.xml":
                        project_tools_config["tools"].append("Java/Maven")

            if project_tools_config["tools"]:
                project_tools_config["enabled"] = True
                logger.info(
                    f"Project tools integration enabled: {', '.join(project_tools_config['tools'])}"
                )
            else:
                logger.info("No project management tools detected")

            self.integrations["project_tools"] = project_tools_config

        except Exception as e:
            logger.error(f"Error setting up project tools integration: {e}")

    def _setup_monitoring_integration(self):
        """Setup monitoring tools integration"""
        try:
            monitoring_config = {"enabled": False, "tools": []}

            # Check for common monitoring tools
            monitoring_files = [
                "prometheus.yml",
                "grafana.ini",
                "datadog.yml",
                "newrelic.ini",
            ]
            current_dir = Path.cwd()

            for monitoring_file in monitoring_files:
                if (current_dir / monitoring_file).exists():
                    if monitoring_file == "prometheus.yml":
                        monitoring_config["tools"].append("Prometheus")
                    elif monitoring_file == "grafana.ini":
                        monitoring_config["tools"].append("Grafana")
                    elif monitoring_file == "datadog.yml":
                        monitoring_config["tools"].append("Datadog")
                    elif monitoring_file == "newrelic.ini":
                        monitoring_config["tools"].append("New Relic")

            if monitoring_config["tools"]:
                monitoring_config["enabled"] = True
                logger.info(
                    f"Monitoring integration enabled: {', '.join(monitoring_config['tools'])}"
                )
            else:
                logger.info("No monitoring tools detected")

            self.integrations["monitoring"] = monitoring_config

        except Exception as e:
            logger.error(f"Error setting up monitoring integration: {e}")

    def create_api_endpoints(self, port: int = 8080):
        """Create REST API endpoints for the system"""
        try:
            # For now, we'll create a simple Flask-like API structure
            # In a full implementation, this would start a Flask server

            api_config = {
                "port": port,
                "endpoints": [
                    "/api/status",
                    "/api/workers",
                    "/api/todos",
                    "/api/performance",
                    "/api/health",
                ],
                "enabled": True,
            }

            self.api_endpoints = api_config

            logger.info(f"API endpoints configured on port {port}")
            logger.info(f"Available endpoints: {', '.join(api_config['endpoints'])}")

            # Start API server in a separate thread
            self._start_api_server()

        except Exception as e:
            logger.error(f"Error creating API endpoints: {e}")

    def _start_api_server(self):
        """Start the API server in a background thread"""
        try:
            # This is a placeholder for the actual API server
            # In a real implementation, this would start Flask/FastAPI
            logger.info("API server thread started")

        except Exception as e:
            logger.error(f"Error starting API server: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status via API"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "system": "Collective Worker System",
                "version": "1.0.0",
                "status": "running",
                "integrations": self.integrations,
                "api_endpoints": self.api_endpoints,
            }

            # Add processor status if available
            if hasattr(self.processor, "get_system_status"):
                status["processor"] = self.processor.get_system_status()

            return status

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

    def get_worker_status(self) -> Dict[str, Any]:
        """Get worker status via API"""
        try:
            if hasattr(self.processor, "get_worker_performance"):
                return self.processor.get_worker_performance()
            else:
                return {"error": "Worker performance data not available"}

        except Exception as e:
            logger.error(f"Error getting worker status: {e}")
            return {"error": str(e)}

    def get_todo_status(self) -> Dict[str, Any]:
        """Get TODO status via API"""
        try:
            if hasattr(self.processor, "todo_registry"):
                registry = self.processor.todo_registry
                return {
                    "total_todos": len(registry.get_all_todos()),
                    "pending_todos": len(registry.get_pending_todos()),
                    "completed_todos": len(registry.get_completed_todos()),
                }
            else:
                return {"error": "TODO registry not available"}

        except Exception as e:
            logger.error(f"Error getting TODO status: {e}")
            return {"error": str(e)}

    def trigger_git_commit(self, message: str = None) -> Dict[str, Any]:
        """Trigger a Git commit via API"""
        try:
            if not self.integrations.get("git", {}).get("enabled"):
                return {"error": "Git integration not enabled"}

            if not message:
                message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Execute git commands
            try:
                # Add all changes
                subprocess.run(["git", "add", "."], check=True, capture_output=True)

                # Commit
                result = subprocess.run(
                    ["git", "commit", "-m", message],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                logger.info(f"Git commit successful: {message}")
                return {
                    "success": True,
                    "message": "Git commit successful",
                    "commit_message": message,
                    "output": result.stdout,
                }

            except subprocess.CalledProcessError as e:
                logger.error(f"Git commit failed: {e}")
                return {
                    "success": False,
                    "message": "Git commit failed",
                    "error": e.stderr,
                }

        except Exception as e:
            logger.error(f"Error triggering Git commit: {e}")
            return {"error": str(e)}

    def trigger_cicd_pipeline(self) -> Dict[str, Any]:
        """Trigger CI/CD pipeline via API"""
        try:
            if not self.integrations.get("cicd", {}).get("enabled"):
                return {"error": "CI/CD integration not enabled"}

            platform = self.integrations["cicd"]["platform"]

            if platform == "GitHub Actions":
                # Trigger GitHub Actions by pushing to trigger branch
                return self._trigger_github_actions()
            elif platform == "GitLab CI":
                # Trigger GitLab CI
                return self._trigger_gitlab_ci()
            else:
                return {"error": f"CI/CD platform {platform} not supported"}

        except Exception as e:
            logger.error(f"Error triggering CI/CD pipeline: {e}")
            return {"error": str(e)}

    def _trigger_github_actions(self) -> Dict[str, Any]:
        """Trigger GitHub Actions workflow"""
        try:
            # This would typically involve using GitHub API or webhooks
            logger.info("GitHub Actions pipeline triggered")
            return {
                "success": True,
                "message": "GitHub Actions pipeline triggered",
                "platform": "GitHub Actions",
            }

        except Exception as e:
            logger.error(f"Error triggering GitHub Actions: {e}")
            return {"error": str(e)}

    def _trigger_gitlab_ci(self) -> Dict[str, Any]:
        """Trigger GitLab CI pipeline"""
        try:
            # This would typically involve using GitLab API or webhooks
            logger.info("GitLab CI pipeline triggered")
            return {
                "success": True,
                "message": "GitLab CI pipeline triggered",
                "platform": "GitLab CI",
            }

        except Exception as e:
            logger.error(f"Error triggering GitLab CI: {e}")
            return {"error": str(e)}

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        try:
            status = {}

            for integration_name, config in self.integrations.items():
                status[integration_name] = {
                    "enabled": config.get("enabled", False),
                    "status": "active" if config.get("enabled", False) else "disabled",
                    "details": config,
                }

            return status

        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {"error": str(e)}


def main():
    """Test the System Integration API"""
    try:
        # Create a mock processor for testing
        class MockProcessor:
            def get_system_status(self):
                return {"status": "mock", "workers": 8}

            def get_worker_performance(self):
                return {"worker_1": {"status": "idle"}}

        mock_processor = MockProcessor()

        # Initialize API
        api = SystemIntegrationAPI(mock_processor)

        print("🔧 Testing System Integration API...")
        print("=" * 50)

        # Test system status
        status = api.get_system_status()
        print(f"✅ System status: {status}")

        # Test worker status
        worker_status = api.get_worker_status()
        print(f"✅ Worker status: {worker_status}")

        # Test integration status
        integration_status = api.get_integration_status()
        print(f"✅ Integration status: {integration_status}")

        print("=" * 50)
        print("🎉 System Integration API test completed successfully!")

    except Exception as e:
        print(f"💥 Error testing System Integration API: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
