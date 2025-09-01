#!/usr/bin/env python3
Collective System Monitor - Real-time monitoring for 32-worker system
Enhanced with TODO progress tracking, queue status, and system recommendations

import logging
import os
import sys
import time
from datetime import datetime, timedelta

import psutil

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class CollectiveSystemMonitor:

            "total_workers_discovered": 0,
            "active_workers": 0,
            "idle_workers": 0,
            "total_todos_processed": 0,
            "system_uptime": timedelta(0),
            "last_update": datetime.now(),
        }

        # Enhanced monitoring attributes
        self.todo_progress = {}
        self.todo_details = {}
        self.memory_optimization = {}
        self.system_recommendations = []

        # Initialize components
        self.queue_manager = QueueManager()
        self.todo_reader = TodoMasterReader()

        logger.info(
            f"Collective System Monitor initialized for {self.total_workers} workers"
        )

    def start_monitoring(self):

        logger.info("Starting continuous system monitoring...")

        try:
            while True:
                self._update_system_status()
                self._display_status_dashboard()
                time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")

    def _update_system_status(self):

            self.system_stats["system_uptime"] = datetime.now() - self.start_time
            self.system_stats["last_update"] = datetime.now()

            # Check worker processes
            self._check_worker_processes()

            # Scan TODO progress
            self._scan_todo_master_progress()

            # Optimize memory usage
            self._optimize_memory_usage()

            # Generate system recommendations
            self._generate_system_recommendations()

        except Exception as e:
            logger.error(f"Error updating system status: {e}")

    def _check_worker_processes(self):

            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["name"] == "python3" and proc.info["cmdline"]:
                        cmdline = " ".join(proc.info["cmdline"])
                        if "collective_worker_processor.py" in cmdline:
                            worker_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self.system_stats["total_workers_discovered"] = len(worker_processes)
            self.system_stats["active_workers"] = len(worker_processes)
            self.system_stats["idle_workers"] = self.total_workers - len(
                worker_processes
            )

            logger.info(f"Discovered {len(worker_processes)} worker processes")

        except Exception as e:
            logger.error(f"Error checking worker processes: {e}")

    def _scan_todo_master_progress(self):

                    "total": total_todos,
                    "completed": completed_todos,
                    "pending": len(pending),
                    "percentage": completion_percentage,
                    "last_updated": datetime.now(),
                }

                # Store TODO details for analysis
                self.todo_details = {
                    "pending_todos": pending[:10],  # Top 10 pending
                    "recent_completions": [],  # Would track recent completions
                    "priority_distribution": self._analyze_priority_distribution(
                        pending
                    ),
                }

        except Exception as e:
            logger.error(f"Error scanning TODO progress: {e}")

    def _analyze_priority_distribution(self, pending_todos):

            priorities = {"high": 0, "medium": 0, "low": 0}

            for todo in pending_todos:
                title = todo.get("title", "").lower()
                if "urgent" in title or "critical" in title:
                    priorities["high"] += 1
                elif "high" in title:
                    priorities["high"] += 1
                elif "low" in title:
                    priorities["low"] += 1
                else:
                    priorities["medium"] += 1

            return priorities

        except Exception as e:
            logger.error(f"Error analyzing priority distribution: {e}")
            return {"high": 0, "medium": 0, "low": 0}

    def _optimize_memory_usage(self):

                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "status": "normal",
            }

            # Set status based on memory usage
            if memory.percent > 90:
                self.memory_optimization["status"] = "critical"
            elif memory.percent > 80:
                self.memory_optimization["status"] = "warning"
            elif memory.percent > 70:
                self.memory_optimization["status"] = "moderate"

        except Exception as e:
            logger.error(f"Error optimizing memory usage: {e}")

    def _generate_system_recommendations(self):

                self.system_stats["active_workers"] / self.total_workers
            ) * 100
            if worker_utilization < 50:
                recommendations.append(
                    "🔧 Consider reducing worker count for better efficiency"
                )
            elif worker_utilization > 90:
                recommendations.append(
                    "⚡ High worker utilization - system is running efficiently"
                )

            # Memory recommendations
            if self.memory_optimization.get("status") == "critical":
                recommendations.append(
                    "🚨 Critical memory usage - consider restarting workers"
                )
            elif self.memory_optimization.get("status") == "warning":
                recommendations.append("⚠️  High memory usage - monitor closely")

            # TODO progress recommendations
            if self.todo_progress.get("percentage", 0) < 20:
                recommendations.append(
                    "📋 Low TODO completion - check worker performance"
                )
            elif self.todo_progress.get("percentage", 0) > 80:
                recommendations.append(
                    "🎯 High TODO completion - system performing well"
                )

            # Queue management recommendations
            queue_status = self.queue_manager.get_queue_status()
            if queue_status["processing_count"] == 0:
                recommendations.append(
                    "⏸️  No active processing - check TODO availability"
                )

            self.system_recommendations = recommendations[:5]  # Top 5 recommendations

        except Exception as e:
            logger.error(f"Error generating system recommendations: {e}")

    def _display_status_dashboard(self):

            os.system("clear" if os.name == "posix" else "cls")

            print("🚀 COLLECTIVE WORKER SYSTEM MONITOR")
            print("=" * 80)
            print(
                f"📊 Last Update: {self.system_stats['last_update'].strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(
                f"⏱️  System Uptime: {self._format_uptime(self.system_stats['system_uptime'])}"
            )
            print()

            # Worker Status
            print("👥 WORKER STATUS:")
            print(f"   Total Workers: {self.total_workers}")
            print(f"   Active Workers: {self.system_stats['active_workers']}")
            print(f"   Idle Workers: {self.system_stats['idle_workers']}")
            print(
                f"   Utilization: {(self.system_stats['active_workers'] / self.total_workers) * 100:.1f}%"
            )
            print()

            # TODO Progress
            if self.todo_progress:
                print("📋 TODO PROGRESS:")
                print(f"   Total TODOs: {self.todo_progress['total']}")
                print(f"   Completed: {self.todo_progress['completed']}")
                print(f"   Pending: {self.todo_progress['pending']}")
                print(f"   Completion: {self.todo_progress['percentage']:.1f}%")
                print(
                    f"   Progress Bar: {self._create_progress_bar(self.todo_progress['percentage'])}"
                )
                print()

            # Queue Status
            queue_status = self.queue_manager.get_queue_status()
            print("🔄 QUEUE STATUS:")
            print(f"   Queue Size: {queue_status['queue_size']}")
            print(f"   Processing: {queue_status['processing_count']}")
            print(f"   Completed: {queue_status['completed_count']}")
            print(f"   Should Process: {queue_status['should_process']}")
            print()

            # Memory Status
            if self.memory_optimization:
                status_color = self._get_status_color(
                    self.memory_optimization["status"]
                )
                print(f"💾 MEMORY STATUS ({status_color}):")
                print(f"   Total: {self.memory_optimization['total_gb']} GB")
                print(
                    f"   Used: {self.memory_optimization['used_gb']} GB ({self.memory_optimization['usage_percent']:.1f}%)"
                )
                print(f"   Available: {self.memory_optimization['available_gb']} GB")
                print()

            # System Recommendations
            if self.system_recommendations:
                print("💡 SYSTEM RECOMMENDATIONS:")
                for i, rec in enumerate(self.system_recommendations, 1):
                    print(f"   {i}. {rec}")
                print()

            # System Tips
            print("💡 SYSTEM TIPS:")
            print("   • Monitor memory usage closely with 32 workers")
            print("   • Check worker utilization for optimal performance")
            print("   • Queue limits: Min 5, Max 20 TODOs")
            print("   • Processing interval: 10 seconds")
            print("   • Press Ctrl+C to stop monitoring")
            print()

        except Exception as e:
            logger.error(f"Error displaying status dashboard: {e}")

    def _get_status_color(self, status):

        colors = {"normal": "🟢", "moderate": "🟡", "warning": "🟠", "critical": "🔴"}
        return colors.get(status, "⚪")

    def _format_uptime(self, uptime):

            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    def _create_progress_bar(self, percentage, width=20):

        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

def main():

        logger.error(f"Error starting monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
