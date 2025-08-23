#!/usr/bin/env python3
"""
Monitor Collective System - Real-time monitoring dashboard for the collective worker system

This script provides real-time monitoring of the 9-tab system:
- Tab 9: Monitoring (this script)
- Tabs 1-8: Workers running collective_worker_processor.py
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CollectiveSystemMonitor:
    """Real-time monitor for the collective worker system"""

    def __init__(self):
        self.monitoring_interval = 5  # Update every 5 seconds
        self.system_start_time = datetime.now()
        self.monitoring_active = True

        # System status tracking
        self.system_status = {
            "overall_health": "healthy",
            "workers_active": 0,
            "total_workers": 8,
            "system_uptime": "0:00:00",
            "last_update": datetime.now().isoformat(),
        }

        # Worker status tracking
        self.worker_status = {}
        self.worker_performance = {}

        logger.info("Collective System Monitor initialized")
        logger.info("Monitoring 9-tab system: 8 workers + 1 monitor")

    def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("🚀 Starting Collective System Monitor...")
        logger.info("📊 Tab 9: Monitoring Dashboard")
        logger.info("🔧 Tabs 1-8: Worker Processes")
        logger.info("=" * 60)

        try:
            while self.monitoring_active:
                self._update_system_status()
                self._display_status_dashboard()
                time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

    def _update_system_status(self):
        """Update system status information"""
        try:
            # Update system uptime
            uptime = datetime.now() - self.system_start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.system_status["system_uptime"] = f"{hours}:{minutes:02d}:{seconds:02d}"

            # Check worker processes
            self._check_worker_processes()

            # Update overall health
            self._assess_system_health()

            # Update timestamp
            self.system_status["last_update"] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error updating system status: {e}")

    def _check_worker_processes(self):
        """Check for active worker processes"""
        try:
            active_workers = 0
            worker_processes = {}

            # Look for Python processes running collective_worker_processor.py
            for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
                try:
                    if proc.info["name"] == "python" or proc.info["name"] == "python3":
                        cmdline = proc.info["cmdline"]
                        if cmdline and "collective_worker_processor.py" in " ".join(
                            cmdline
                        ):
                            # Extract worker info
                            worker_id = self._extract_worker_id(cmdline)
                            if worker_id:
                                worker_processes[worker_id] = {
                                    "pid": proc.info["pid"],
                                    "status": "running",
                                    "uptime": self._get_process_uptime(
                                        proc.info["create_time"]
                                    ),
                                    "memory_mb": proc.memory_info().rss / 1024 / 1024,
                                    "cpu_percent": proc.cpu_percent(),
                                }
                                active_workers += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self.system_status["workers_active"] = active_workers
            self.worker_status = worker_processes

        except Exception as e:
            logger.error(f"Error checking worker processes: {e}")

    def _extract_worker_id(self, cmdline):
        """Extract worker ID from command line"""
        try:
            # Look for worker identifier in command line
            cmd_str = " ".join(cmdline)
            if "worker" in cmd_str.lower():
                # Try to extract worker number
                import re

                match = re.search(r"worker[_-]?(\d+)", cmd_str.lower())
                if match:
                    return f"worker_{match.group(1)}"

            # Default worker ID based on process
            return "worker_unknown"

        except Exception:
            return "worker_unknown"

    def _get_process_uptime(self, create_time):
        """Get process uptime"""
        try:
            uptime = time.time() - create_time
            hours, remainder = divmod(int(uptime), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        except:
            return "unknown"

    def _assess_system_health(self):
        """Assess overall system health"""
        try:
            active_workers = self.system_status["workers_active"]
            total_workers = self.system_status["total_workers"]

            if active_workers == 0:
                self.system_status["overall_health"] = "critical"
            elif active_workers < total_workers * 0.5:
                self.system_status["overall_health"] = "warning"
            elif active_workers < total_workers:
                self.system_status["overall_health"] = "degraded"
            else:
                self.system_status["overall_health"] = "healthy"

        except Exception as e:
            logger.error(f"Error assessing system health: {e}")

    def _display_status_dashboard(self):
        """Display the status dashboard"""
        try:
            # Clear screen (works on most terminals)
            os.system("clear" if os.name == "posix" else "cls")

            # Display header
            print("🚀 COLLECTIVE WORKER SYSTEM MONITOR")
            print("=" * 60)
            print(f"📊 Status: {self.system_status['overall_health'].upper()}")
            print(f"⏱️  Uptime: {self.system_status['system_uptime']}")
            print(f"🔄 Last Update: {datetime.now().strftime('%H:%M:%S')}")
            print(
                f"👥 Workers: {self.system_status['workers_active']}/{self.system_status['total_workers']}"
            )
            print("=" * 60)

            # Display worker status
            print("🔧 WORKER STATUS:")
            print("-" * 40)

            if self.worker_status:
                for worker_id, info in self.worker_status.items():
                    status_icon = "✅" if info["status"] == "running" else "❌"
                    print(
                        f"{status_icon} {worker_id}: PID {info['pid']} | "
                        f"Uptime: {info['uptime']} | "
                        f"Memory: {info['memory_mb']:.1f}MB | "
                        f"CPU: {info['cpu_percent']:.1f}%"
                    )
            else:
                print("❌ No worker processes detected")

            print("-" * 40)

            # Display system tips
            print("💡 SYSTEM TIPS:")
            print("-" * 40)

            if self.system_status["overall_health"] == "critical":
                print("🚨 CRITICAL: No workers are running!")
                print("   Start workers in Tabs 1-8 with:")
                print("   python collective_worker_processor.py")
            elif self.system_status["overall_health"] == "warning":
                print("⚠️  WARNING: Some workers are down")
                print("   Check worker processes and restart if needed")
            elif self.system_status["overall_health"] == "degraded":
                print("🔶 DEGRADED: System running below capacity")
                print("   Some workers may need attention")
            else:
                print("✅ HEALTHY: All workers are running normally")
                print("   System is operating at full capacity")

            print("-" * 40)
            print("📋 Press Ctrl+C to stop monitoring")
            print("=" * 60)

        except Exception as e:
            logger.error(f"Error displaying status dashboard: {e}")

    def stop_monitoring(self):
        """Stop the monitoring"""
        self.monitoring_active = False
        logger.info("Monitoring stopped")


def main():
    """Main entry point"""
    try:
        monitor = CollectiveSystemMonitor()
        monitor.start_monitoring()

    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Monitor error: {e}")


if __name__ == "__main__":
    main()
