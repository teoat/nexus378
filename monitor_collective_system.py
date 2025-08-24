#!/usr/bin/env python3


    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CollectiveSystemMonitor:
    """Enhanced monitor for 32-worker collective system with multi-source TODO support
            "total_workers_discovered": 0,
            "active_workers": 0,
            "idle_workers": 0,
            "total_todos_processed": 0,
            "system_uptime": timedelta(0),
            "last_update": datetime.now()
        }

        # Enhanced monitoring attributes
        self.todo_progress = {}
        self.todo_details = {}
        self.memory_optimization = {}
        self.system_recommendations = []
        self.multi_source_stats = {}

        # Initialize components
        self.queue_manager = QueueManager()
        self.todo_reader = TodoMasterReader()

        logger.info(f"Enhanced Collective System Monitor initialized for {self.total_workers} workers")

    def start_monitoring(self):
        """Start continuous monitoring
        logger.info("Starting enhanced continuous system monitoring...")

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
        """Update comprehensive system status with multi-source TODO support
            self.system_stats["system_uptime"] = datetime.now() - self.start_time
            self.system_stats["last_update"] = datetime.now()

            # Check worker processes
            self._check_worker_processes()

            # Scan multi-source TODO progress
            self._scan_multi_source_todo_progress()

            # Optimize memory usage
            self._optimize_memory_usage()

            # Generate system recommendations
            self._generate_system_recommendations()

        except Exception as e:
            logger.error(f"Error updating system status: {e}")

    def _check_worker_processes(self):
        """Check for running worker processes
            self.system_stats["total_workers_discovered"] = len(worker_processes)
            self.system_stats["active_workers"] = len(worker_processes)
            self.system_stats["idle_workers"] = self.total_workers - len(worker_processes)

            logger.info(f"Discovered {len(worker_processes)} worker processes")

        except Exception as e:
            logger.error(f"Error checking worker processes: {e}")

    def _scan_multi_source_todo_progress(self):
        """Scan multiple TODO sources for comprehensive progress tracking
                    "total": total_todos,
                    "completed": completed_todos,
                    "pending": stats['pending_todos'],
                    "percentage": completion_percentage,
                    "last_updated": datetime.now(),
                    "sources": source_status
                }

                # Store detailed TODO information
                self.todo_details = {
                    "pending_todos": self.todo_reader.get_pending_todos()[:10],  # Top 10 pending
                    "recent_completions": self.todo_reader.get_completed_todos()[:5],  # Top 5 completed
                    "priority_distribution": stats['priorities'],
                    "extension_distribution": stats['extensions'],
                    "phase_distribution": stats['phases']
                }

        except Exception as e:
            logger.error(f"Error scanning multi-source TODO progress: {e}")

    def _optimize_memory_usage(self):
        """Monitor and optimize memory usage
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "status": "normal"
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
        """Generate intelligent system recommendations with multi-source awareness
            worker_utilization = (self.system_stats["active_workers"] / self.total_workers) * 100
            if worker_utilization < 50:
                recommendations.append("🔧 Consider reducing worker count for better efficiency")
            elif worker_utilization > 90:
                recommendations.append("⚡ High worker utilization - system is running efficiently")

            # Memory recommendations
            if self.memory_optimization.get("status") == "critical":
                recommendations.append("🚨 Critical memory usage - consider restarting workers")
            elif self.memory_optimization.get("status") == "warning":
                recommendations.append("⚠️  High memory usage - monitor closely")

            # Multi-source TODO recommendations
            if self.todo_progress.get("percentage", 0) < 20:
                recommendations.append("📋 Low TODO completion - check worker performance")
            elif self.todo_progress.get("percentage", 0) > 80:
                recommendations.append("🎯 High TODO completion - system performing well")

            # Source-specific recommendations
            source_status = self.todo_progress.get("sources", {})
            if source_status.get("MASTER_TODO", False) and not source_status.get("TODO_MASTER", False):
                recommendations.append("📝 MASTER_TODO available - consider syncing with TODO_MASTER")
            elif source_status.get("TODO_MASTER", False) and not source_status.get("MASTER_TODO", False):
                recommendations.append("📝 TODO_MASTER available - consider syncing with MASTER_TODO")

            # Queue management recommendations
            queue_status = self.queue_manager.get_queue_status()
            if queue_status["processing_count"] == 0:
                recommendations.append("⏸️  No active processing - check TODO availability")

            # Get enhanced TODO recommendations
            try:
                todo_recommendations = self.todo_reader.get_todo_recommendations()
                recommendations.extend(todo_recommendations)
            except Exception as e:
                logger.error(f"Error getting TODO recommendations: {e}")

            self.system_recommendations = recommendations[:8]  # Top 8 recommendations

        except Exception as e:
            logger.error(f"Error generating system recommendations: {e}")

    def _display_status_dashboard(self):
        """Display comprehensive status dashboard with multi-source information
            print("🚀 ENHANCED COLLECTIVE WORKER SYSTEM MONITOR")
            print("=" * 80)
            print(f"📊 Last Update: {self.system_stats['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  System Uptime: {self._format_uptime(self.system_stats['system_uptime'])}")
            print()

            # Worker Status
            print("👥 WORKER STATUS:")
            print(f"   Total Workers: {self.total_workers}")
            print(f"   Active Workers: {self.system_stats['active_workers']}")
            print(f"   Idle Workers: {self.system_stats['idle_workers']}")
            print(f"   Utilization: {(self.system_stats['active_workers'] / self.total_workers) * 100:.1f}%")
            print()

            # Multi-Source TODO Progress
            if self.todo_progress:
                print("📋 MULTI-SOURCE TODO PROGRESS:")
                print(f"   Total TODOs: {self.todo_progress['total']}")
                print(f"   Completed: {self.todo_progress['completed']}")
                print(f"   Pending: {self.todo_progress['pending']}")
                print(f"   Completion: {self.todo_progress['percentage']:.1f}%")
                print(f"   Progress Bar: {self._create_progress_bar(self.todo_progress['percentage'])}")
                
                # Source Status
                if self.todo_progress.get('sources'):
                    print("   Sources:")
                    for source, available in self.todo_progress['sources'].items():
                        status_icon = "✅" if available else "❌"
                        print(f"     {status_icon} {source}")
                print()

            # TODO Distribution
            if self.todo_details:
                print("📊 TODO DISTRIBUTION:")
                
                # Priority Distribution
                priorities = self.todo_details.get('priority_distribution', {})
                if priorities:
                    print("   Priority:")
                    for priority, count in priorities.items():
                        if count > 0:
                            print(f"     {priority.title()}: {count}")
                
                # Extension Distribution
                extensions = self.todo_details.get('extension_distribution', {})
                if extensions:
                    print("   Extensions:")
                    for ext, count in extensions.items():
                        if count > 0:
                            print(f"     {ext}: {count}")
                
                # Phase Distribution
                phases = self.todo_details.get('phase_distribution', {})
                if phases:
                    print("   Phases:")
                    for phase, count in phases.items():
                        if count > 0:
                            print(f"     {phase}: {count}")
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
                status_color = self._get_status_color(self.memory_optimization["status"])
                print(f"💾 MEMORY STATUS ({status_color}):")
                print(f"   Total: {self.memory_optimization['total_gb']} GB")
                print(f"   Used: {self.memory_optimization['used_gb']} GB ({self.memory_optimization['usage_percent']:.1f}%)")
                print(f"   Available: {self.memory_optimization['available_gb']} GB")
                print()

            # System Recommendations
            if self.system_recommendations:
                print("💡 SYSTEM RECOMMENDATIONS:")
                for i, rec in enumerate(self.system_recommendations, 1):
                    print(f"   {i}. {rec}")
                print()

            # System Tips
            print("💡 ENHANCED SYSTEM TIPS:")
            print("   • Monitor memory usage closely with 32 workers")
            print("   • Check worker utilization for optimal performance")
            print("   • Queue limits: Min 5, Max 20 TODOs")
            print("   • Processing interval: 10 seconds")
            print("   • Multi-source TODO support: TODO_MASTER.md + master_todo.md")
            print("   • TODO extensions: API, UI, DB, SEC, TEST, DOC, etc.")
            print("   • Press Ctrl+C to stop monitoring")
            print()

        except Exception as e:
            logger.error(f"Error displaying status dashboard: {e}")

    def _get_status_color(self, status):
        """Get status color indicator
            "normal": "🟢",
            "moderate": "🟡",
            "warning": "🟠",
            "critical": "🔴"
        }
        return colors.get(status, "⚪")

    def _format_uptime(self, uptime):
        """Format uptime in human-readable format
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    def _create_progress_bar(self, percentage, width=20):
        """Create a visual progress bar
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"


def main():
    """Main function to start monitoring
        logger.error(f"Error starting monitor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
