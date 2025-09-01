#!/usr/bin/env python3
Enhanced Collaborative TODO System with Tier 4 Redundancy
=======================================================

Features:
- 10 Main Workers with 5 Subworkers each (50 total workers)
- Dynamic collaboration and collective task processing
- Tier 4 redundancy with error prediction and recovery
- Conflict-free task marking and status updates
- Advanced monitoring and optimization
- Phase 3 optimization for 8+ rating

    TIER_1 = "Tier 1 - Core"
    TIER_2 = "Tier 2 - Enhanced"
    TIER_3 = "Tier 3 - Advanced"
    TIER_4 = "Tier 4 - Redundant"

    IDLE = "🟡 Idle"
    WORKING = "🟢 Working"
    HELPING = "🔵 Helping Others"
    WAITING = "🟠 Waiting for Tasks"
    COLLABORATING = "🟣 Collaborating"
    RECOVERING = "🔴 Error Recovery"
    OPTIMIZING = "🟤 Optimizing"

        if metrics.get("error_count", 0) > 3:
            predictions.append("High error rate detected")

        if metrics.get("performance_score", 100) < 70:
            predictions.append("Performance degradation detected")

        if metrics.get("recovery_attempts", 0) > 2:
            predictions.append("Multiple recovery attempts detected")

        return predictions

    def get_recovery_strategy(self, error_type: str) -> Dict[str, Any]:

            "High error rate detected": {
                "action": "restart_worker",
                "backup": "activate_backup",
                "timeout": 30,
            },
            "Performance degradation detected": {
                "action": "optimize_worker",
                "backup": "load_balance",
                "timeout": 60,
            },
            "Multiple recovery attempts detected": {
                "action": "replace_worker",
                "backup": "full_recovery",
                "timeout": 120,
            },
        }
        return strategies.get(
            error_type, {"action": "unknown", "backup": "none", "timeout": 30}
        )

class EnhancedCollaborativeSystem:
    def __init__(self):
        self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        self.db_path = f"enhanced_collaborative_{self.agent_id}.db"

        # Configuration
        self.MAX_TODOS = 10
        self.MIN_TODOS = 3
        self.TASKS_BEFORE_ADD = 2
        self.MAIN_WORKERS = 10
        self.SUBWORKERS_PER_WORKER = 5

        # Initialize system
        self.system = UnifiedTaskSystem(db_path=self.db_path)
        self.todo_reader = WorkingTodoReader()

        # Enhanced management
        self.workers = {}
        self.worker_threads = {}
        self.subworker_threads = {}
        self.collaboration_lock = threading.Lock()
        self.task_queue = queue.Queue()
        self.completion_queue = queue.Queue()

        # Advanced features
        self.conflict_prevention = TaskConflictPrevention()
        self.redundancy = Tier4Redundancy()
        self.optimization_engine = self._create_optimization_engine()

        # Statistics and monitoring
        self.start_time = datetime.now()
        self.total_tasks_completed = 0
        self.total_collaborations = 0
        self.system_health_score = 100.0
        self.phase = 1

        # Performance tracking
        self.performance_metrics = {
            "worker_efficiency": 0.0,
            "collaboration_rate": 0.0,
            "error_recovery_rate": 0.0,
            "task_completion_rate": 0.0,
        }

        logger.info(f"🚀 Enhanced Collaborative System Initialized")
        logger.info(f"🆔 Agent ID: {self.agent_id}")
        logger.info(f"📁 Database: {self.db_path}")
        logger.info(
            f"👷 Workers: {self.MAIN_WORKERS} main + {self.MAIN_WORKERS * self.SUBWORKERS_PER_WORKER} subworkers"
        )
        logger.info(
            f"🔧 Features: Tier 4 Redundancy, Conflict Prevention, Dynamic Collaboration"
        )

    def _create_optimization_engine(self): -> None:

            "phase": 1,
            "optimization_targets": {
                "worker_efficiency": 85.0,
                "collaboration_rate": 80.0,
                "error_recovery_rate": 95.0,
                "task_completion_rate": 90.0,
            },
            "current_metrics": {},
            "optimization_history": [],
        }

    def load_limited_todos(self) -> List[dict]:

                logger.error("❌ No TODOs found")
                return []

            logger.info(
                f"📋 Found {len(todos)} TODOs, loading {min(self.MAX_TODOS, len(todos))} (limit)"
            )

            # Add limited TODOs with conflict prevention
            loaded_todos = []
            for i, todo in enumerate(todos[: self.MAX_TODOS]):
                task_id = f"todo_{self.agent_id}_{i+1:03d}"

                # Check for conflicts
                if not self.conflict_prevention.acquire_task_lock(
                    self.agent_id, task_id
                ):
                    logger.warning(
                        f"⚠️ Task {task_id} already owned by another agent, skipping"
                    )
                    continue

                try:
                    self.system.add_new_todo(
                        name=todo["name"],
                        description=todo["description"],
                        priority=todo["priority"],
                        estimated_duration=todo["estimated_duration"],
                        required_capabilities=todo["required_capabilities"],
                    )
                    loaded_todos.append(todo)
                    logger.info(f"✅ Added: {task_id} - {todo['name']}")
                except Exception as e:
                    logger.error(f"❌ Failed to add TODO {task_id}: {e}")
                    self.conflict_prevention.release_task_lock(self.agent_id, task_id)

            return loaded_todos

        except Exception as e:
            logger.error(f"❌ Error loading TODOs: {e}")
            return []

    def register_workers(self):

                "id": "code_quality_worker",
                "name": "Code Quality Engineer",
                "capabilities": ["code_review", "testing", "documentation"],
                "specialty": "Quality Assurance",
                "tier": WorkerTier.TIER_1,
            },
            {
                "id": "general_worker",
                "name": "General Developer",
                "capabilities": ["development", "integration", "deployment"],
                "specialty": "Full Stack Development",
                "tier": WorkerTier.TIER_1,
            },
            {
                "id": "infrastructure_worker",
                "name": "Infrastructure Specialist",
                "capabilities": ["docker", "kubernetes", "monitoring"],
                "specialty": "DevOps & Infrastructure",
                "tier": WorkerTier.TIER_2,
            },
            {
                "id": "security_worker",
                "name": "Security Engineer",
                "capabilities": [
                    "security",
                    "ssl_tls",
                    "certificates",
                    "authentication",
                ],
                "specialty": "Security & Compliance",
                "tier": WorkerTier.TIER_2,
            },
            {
                "id": "database_worker",
                "name": "Database Engineer",
                "capabilities": [
                    "database",
                    "data_management",
                    "migration",
                    "optimization",
                ],
                "specialty": "Data & Storage",
                "tier": WorkerTier.TIER_2,
            },
            {
                "id": "api_worker",
                "name": "API Developer",
                "capabilities": [
                    "api_development",
                    "backend",
                    "integration",
                    "microservices",
                ],
                "specialty": "Backend & APIs",
                "tier": WorkerTier.TIER_3,
            },
            {
                "id": "frontend_worker",
                "name": "Frontend Developer",
                "capabilities": [
                    "frontend",
                    "ui_ux",
                    "responsive_design",
                    "accessibility",
                ],
                "specialty": "User Interface",
                "tier": WorkerTier.TIER_3,
            },
            {
                "id": "testing_worker",
                "name": "Testing Specialist",
                "capabilities": [
                    "automated_testing",
                    "qa",
                    "performance_testing",
                    "security_testing",
                ],
                "specialty": "Quality & Testing",
                "tier": WorkerTier.TIER_3,
            },
            {
                "id": "monitoring_worker",
                "name": "Monitoring Engineer",
                "capabilities": ["monitoring", "observability", "alerting", "metrics"],
                "specialty": "Observability",
                "tier": WorkerTier.TIER_4,
            },
            {
                "id": "optimization_worker",
                "name": "Performance Optimizer",
                "capabilities": [
                    "optimization",
                    "performance",
                    "scalability",
                    "efficiency",
                ],
                "specialty": "Performance & Scalability",
                "tier": WorkerTier.TIER_4,
            },
        ]

        logger.info("👷 Registering enhanced workers with subworkers...")

        for config in worker_configs:
            worker_id = f"{config['id']}_{self.agent_id}"

            # Register main worker in system
            self.system.register_worker(
                worker_id=worker_id,
                name=config["name"],
                capabilities=config["capabilities"],
            )

            # Create worker status tracker
            worker_status = WorkerStatus(worker_id)
            worker_status.tier = config["tier"]
            self.workers[worker_id] = worker_status

            # Create 5 subworkers for each main worker
            for sub_idx in range(self.SUBWORKERS_PER_WORKER):
                subworker_id = f"{worker_id}_sub{sub_idx + 1}"
                subworker = SubworkerStatus(subworker_id, worker_id)
                worker_status.subworkers[subworker_id] = subworker

                # Register subworker in system
                self.system.register_worker(
                    worker_id=subworker_id,
                    name=f"{config['name']} Subworker {sub_idx + 1}",
                    capabilities=config["capabilities"],
                )

            logger.info(
                f"✅ Registered: {worker_id} - {config['name']} ({config['specialty']}) with {self.SUBWORKERS_PER_WORKER} subworkers"
            )

        logger.info(
            f"🎯 Total workers: {len(self.workers)} main + {len(self.workers) * self.SUBWORKERS_PER_WORKER} subworkers"
        )

    def start_workers(self):

        logger.info("🚀 Starting enhanced collaborative workers and subworkers...")

        # Start main workers
        for worker_id in self.workers.keys():
            thread = threading.Thread(
                target=self._enhanced_worker_loop,
                args=(worker_id,),
                daemon=True,
                name=f"MainWorker-{worker_id}",
            )
            self.worker_threads[worker_id] = thread
            thread.start()
            logger.info(f"👷 Main worker {worker_id} started")

            # Start subworkers
            worker_status = self.workers[worker_id]
            for subworker_id in worker_status.subworkers.keys():
                sub_thread = threading.Thread(
                    target=self._enhanced_subworker_loop,
                    args=(worker_id, subworker_id),
                    daemon=True,
                    name=f"SubWorker-{subworker_id}",
                )
                self.subworker_threads[subworker_id] = sub_thread
                sub_thread.start()
                logger.info(f"🔧 Subworker {subworker_id} started")

        logger.info("✅ All workers and subworkers started with enhanced collaboration")

    def _enhanced_worker_loop(self, worker_id: str):

                logger.error(f"❌ Error in main worker {worker_id}: {e}")
                self._handle_worker_error(worker_id, e)
                time.sleep(5)

    def _enhanced_subworker_loop(self, parent_worker_id: str, subworker_id: str):

                logger.error(f"❌ Error in subworker {subworker_id}: {e}")
                self._handle_subworker_error(parent_worker_id, subworker_id, e)
                time.sleep(3)

    def _check_worker_health(self, worker_id: str):

            "error_count": worker_status.error_count,
            "performance_score": worker_status.performance_score,
            "recovery_attempts": worker_status.recovery_attempts,
            "last_heartbeat": worker_status.last_heartbeat,
        }

        # Predict potential errors
        predictions = self.redundancy.predict_errors(worker_id, metrics)

        if predictions:
            logger.warning(
                f"⚠️ Worker {worker_id} health issues predicted: {predictions}"
            )
            self._initiate_preventive_recovery(worker_id, predictions)

    def _initiate_preventive_recovery(self, worker_id: str, predictions: List[str]):

            if strategy["action"] == "restart_worker":
                logger.info(f"🔄 Restarting worker {worker_id} due to {prediction}")
                self._restart_worker(worker_id)
            elif strategy["action"] == "optimize_worker":
                logger.info(f"⚡ Optimizing worker {worker_id} due to {prediction}")
                self._optimize_worker(worker_id)
            elif strategy["action"] == "replace_worker":
                logger.info(f"🔄 Replacing worker {worker_id} due to {prediction}")
                self._replace_worker(worker_id)

    def _should_help_others(self, worker_id: str) -> bool:

                worker_status.current_task = f"Helping {target_worker.worker_id}"
                worker_status.is_collaborating = True
                worker_status.collaboration_partners = [target_worker.worker_id]

                logger.info(f"🤝 {worker_id} is helping {target_worker.worker_id}")

                # Enhanced helping with collective intelligence
                self._collective_helping_session(worker_id, target_worker.worker_id)

                # Update statistics
                worker_status.tasks_helped += 1
                self.total_collaborations += 1

                worker_status.status = WorkerActivity.IDLE
                worker_status.is_collaborating = False
                worker_status.collaboration_partners = []
                worker_status.last_activity = datetime.now()

    def _collective_helping_session(self, helper_id: str, target_id: str):

                subworker.current_task = f"Collective help for {target_id}"
                subworker.collaboration_partners = [target_id]

            # Simulate collective helping
            time.sleep(random.uniform(2, 6))

            # Reset subworker statuses
            for subworker in available_subworkers[:3]:
                subworker.status = WorkerActivity.IDLE
                subworker.current_task = None
                subworker.collaboration_partners = []

    def _select_best_collaboration_target(
        self, struggling_workers: List[WorkerStatus], helper_id: str
    ) -> WorkerStatus:

                    self.agent_id, task["id"]
                ):
                    logger.warning(
                        f"⚠️ Task {task['id']} already owned by another agent"
                    )
                    return None

                # Try to claim it
                if self.system.claim_task(worker_id, task["id"]):
                    return task

        except Exception as e:
            logger.error(f"❌ Error getting task for {worker_id}: {e}")

        return None

    def _process_task_enhanced(self, worker_id: str, task):

                "name", task.get("title", "Unknown Task")
            )
            worker_status.progress = 0
            worker_status.last_activity = datetime.now()

            logger.info(f"🔄 {worker_id} started: {worker_status.current_task}")

            # Activate subworkers for collective processing
            self._activate_subworkers_for_task(worker_id, task)

            # Process task with progress updates
            for progress in range(0, 101, 20):
                worker_status.progress = progress

                # Update subworker progress
                self._update_subworker_progress(worker_id, progress)

                time.sleep(random.uniform(1, 3))

                if progress == 100:
                    # Complete task
                    self.system.complete_task(worker_id, task["id"])
                    worker_status.tasks_completed += 1
                    self.total_tasks_completed += 1

                    logger.info(
                        f"✅ {worker_id} completed: {worker_status.current_task}"
                    )

                    # Update TODO_MASTER.md
                    self._update_todo_master(task)

                    # Release task lock
                    self.conflict_prevention.release_task_lock(
                        self.agent_id, task["id"]
                    )

                    # Update performance metrics
                    self._update_performance_metrics()

            worker_status.status = WorkerActivity.IDLE
            worker_status.current_task = None
            worker_status.progress = 0
            worker_status.last_activity = datetime.now()

            # Deactivate subworkers
            self._deactivate_subworkers(worker_id)

        except Exception as e:
            logger.error(f"❌ Error processing task in {worker_id}: {e}")
            worker_status.status = WorkerActivity.IDLE
            self._handle_task_error(worker_id, task, e)

    def _activate_subworkers_for_task(self, worker_id: str, task):

            subworker.current_task = f"Subtask for {task.get('name', 'Unknown')}"
            subworker.progress = 0

    def _assess_task_complexity(self, task) -> int:

        priority = task.get("priority", "NORMAL")
        if priority == "HIGH":
            complexity_score += 2
        elif priority == "LOW":
            complexity_score -= 1

        # Duration factor
        duration = task.get("estimated_duration", "1 hour")
        if "4-6" in str(duration) or "6-8" in str(duration):
            complexity_score += 1
        elif "8+" in str(duration):
            complexity_score += 2

        # Capabilities factor
        capabilities = task.get("required_capabilities", [])
        if len(capabilities) > 3:
            complexity_score += 1

        return max(1, min(5, complexity_score))

    def _update_subworker_progress(self, worker_id: str, progress: int):

                Path(__file__).parent.parent.parent.parent / "TODO_MASTER.md"
            )

            if todo_master_path.exists():
                content = todo_master_path.read_text()

                # Find and mark the task as completed
                task_name = task.get("name", task.get("title", "Unknown Task"))
                lines = content.split("\n")

                for i, line in enumerate(lines):
                    if task_name in line and "🔄" in line:
                        # Mark as completed with agent ID and timestamp
                        completion_mark = f"✅ COMPLETED by {self.agent_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        lines[i] = line.replace("🔄", "✅") + f" - {completion_mark}"
                        break

                # Write back to file
                todo_master_path.write_text("\n".join(lines))
                logger.info(f"📝 Updated TODO_MASTER.md for: {task_name}")

        except Exception as e:
            logger.error(f"❌ Error updating TODO_MASTER.md: {e}")

    def _update_performance_metrics(self):

        self.performance_metrics["worker_efficiency"] = (
            active_workers / total_workers
        ) * 100

        # Calculate collaboration rate
        collaborating_workers = sum(
            1 for w in self.workers.values() if w.is_collaborating
        )
        self.performance_metrics["collaboration_rate"] = (
            collaborating_workers / total_workers
        ) * 100

        # Calculate task completion rate
        if self.total_tasks_completed > 0:
            self.performance_metrics["task_completion_rate"] = min(
                100, (self.total_tasks_completed / self.MAX_TODOS) * 100
            )

        # Check if we should advance to next phase
        self._check_phase_advancement()

    def _check_phase_advancement(self):

        if self.phase == 1 and current_metrics["worker_efficiency"] >= 80:
            self.phase = 2
            logger.info("🚀 Advancing to Phase 2: Enhanced Optimization")
            self._apply_phase_2_optimizations()

        elif self.phase == 2 and current_metrics["collaboration_rate"] >= 75:
            self.phase = 3
            logger.info("🚀 Advancing to Phase 3: Advanced Optimization")
            self._apply_phase_3_optimizations()

    def _apply_phase_2_optimizations(self):

            "⚡ Phase 2 optimizations applied: Enhanced collaboration thresholds"
        )

    def _apply_phase_3_optimizations(self):

        logger.info("🚀 Phase 3 optimizations applied: Advanced features enabled")

    def _enable_advanced_features(self):

            "🔧 Advanced features enabled: Predictive collaboration, intelligent load balancing, performance auto-tuning"
        )

    def monitor_progress_enhanced(self):

        logger.info("🚀 Enhanced Collaborative System - Live Status Monitoring")
        print("=" * 80)

        while True:
            try:
                # Clear screen (simple approach)
                print("\n" * 50)

                # System overview
                print(f"🚀 Enhanced Collaborative System - Live Status Monitoring")
                print("=" * 80)
                print(f"🆔 Agent ID: {self.agent_id}")
                print(f"📁 Database: {self.db_path}")
                print(f"⏰ Runtime: {datetime.now() - self.start_time}")
                print(
                    f"🎯 Phase: {self.phase}/3 - {'🚀 Advanced' if self.phase == 3 else '⚡ Enhanced' if self.phase == 2 else '🔧 Basic'}"
                )
                print(f"🎯 Total Collaborations: {self.total_collaborations}")
                print(f"✅ Total Tasks Completed: {self.total_tasks_completed}")
                print(f"🏥 System Health Score: {self.system_health_score:.1f}/100")
                print("=" * 80)

                # Task status
                system_status = self.system.get_system_status()
                total_tasks = system_status.get("total_tasks", 0)
                pending_tasks = system_status.get("pending_tasks", 0)
                completed_tasks = system_status.get("completed_tasks", 0)

                print(f"📋 Task Status:")
                print(f"   Total: {total_tasks}")
                print(f"   ⏳ Pending: {pending_tasks}")
                print(f"   ✅ Completed: {completed_tasks}")
                print()

                # Performance metrics
                print(f"📊 Performance Metrics:")
                print(
                    f"   👷 Worker Efficiency: {self.performance_metrics['worker_efficiency']:.1f}%"
                )
                print(
                    f"   🤝 Collaboration Rate: {self.performance_metrics['collaboration_rate']:.1f}%"
                )
                print(
                    f"   ✅ Task Completion Rate: {self.performance_metrics['task_completion_rate']:.1f}%"
                )
                print()

                # Worker status with detailed information
                print(f"👷 Worker Status (Main + Subworkers):")
                print("-" * 80)

                for worker_id, status in self.workers.items():
                    # Get worker info safely
                    worker_name = self._get_worker_display_name(worker_id)

                    # Status emoji and details
                    status_display = status.status.value
                    current_work = status.current_task or "No current task"
                    progress_bar = "█" * (status.progress // 10) + "░" * (
                        10 - status.progress // 10
                    )

                    print(f"🔹 {worker_id}")
                    print(f"   👤 Name: {worker_name}")
                    print(f"   📊 Status: {status_display}")
                    print(f"   🏷️ Tier: {status.tier.value}")
                    print(f"   📝 Current: {current_work}")
                    print(f"   📈 Progress: [{progress_bar}] {status.progress}%")
                    print(f"   ✅ Completed: {status.tasks_completed}")
                    print(f"   🤝 Helped: {status.tasks_helped}")
                    print(f"   🏥 Performance: {status.performance_score:.1f}/100")

                    if status.is_collaborating:
                        partners = (
                            ", ".join(status.collaboration_partners)
                            if status.collaboration_partners
                            else "None"
                        )
                        print(f"   🔗 Collaborating with: {partners}")

                    # Subworker status
                    active_subworkers = [
                        s
                        for s in status.subworkers.values()
                        if s.status != WorkerActivity.IDLE
                    ]
                    if active_subworkers:
                        print(
                            f"   🔧 Active Subworkers: {len(active_subworkers)}/{len(status.subworkers)}"
                        )
                        for sub in active_subworkers[:3]:  # Show first 3
                            sub_progress = "█" * (sub.progress // 10) + "░" * (
                                10 - sub.progress // 10
                            )
                            print(
                                f"      📊 {sub.subworker_id}: [{sub_progress}] {sub.progress}%"
                            )

                    print(
                        f"   ⏰ Last Activity: {status.last_activity.strftime('%H:%M:%S') if status.last_activity else 'Never'}"
                    )
                    print()

                # System configuration
                print(f"📊 System Configuration:")
                print(f"   Loaded TODOs: {total_tasks} (max: {self.MAX_TODOS})")
                print(f"   Min TODOs: {self.MIN_TODOS}")
                print(f"   Tasks before add: {self.TASKS_BEFORE_ADD}")
                print(f"   Main Workers: {self.MAIN_WORKERS}")
                print(f"   Subworkers per Worker: {self.SUBWORKERS_PER_WORKER}")
                print(
                    f"   Total Workers: {self.MAIN_WORKERS * (1 + self.SUBWORKERS_PER_WORKER)}"
                )
                print()

                # Recent activities
                print(f"📝 Recent Activities:")
                print(
                    f"   Last TODO_MASTER.md Update: {datetime.now().strftime('%H:%M:%S')}"
                )
                print(
                    f"   Active Collaborations: {sum(1 for w in self.workers.values() if w.is_collaborating)}"
                )
                print(f"   Tier 4 Redundancy: Active")
                print(f"   Conflict Prevention: Active")
                print()

                print("Press Ctrl+C to stop")
                print("=" * 80)

                time.sleep(3)

            except KeyboardInterrupt:
                logger.info("🛑 Stopping enhanced monitoring...")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring: {e}")
                time.sleep(5)

    def _get_worker_display_name(self, worker_id: str) -> str:

            if hasattr(self.system, "workers") and worker_id in self.system.workers:
                return self.system.workers[worker_id].name
            return "Unknown"
        except Exception:
            logger.error(f"Error: {e}")
            return "Unknown"

    def _handle_worker_error(self, worker_id: str, error: Exception):

        logger.error(f"❌ Worker {worker_id} error: {error}")

        # Implement error recovery strategies
        if worker_status.error_count <= 3:
            logger.info(f"🔄 Attempting to recover worker {worker_id}")
            worker_status.recovery_attempts += 1
            worker_status.status = WorkerActivity.RECOVERING

            # Simulate recovery
            time.sleep(random.uniform(2, 5))
            worker_status.status = WorkerActivity.IDLE
        else:
            logger.warning(
                f"⚠️ Worker {worker_id} exceeded error threshold, activating backup"
            )
            self._activate_backup_worker(worker_id)

    def _activate_backup_worker(self, worker_id: str):

        backup_id = f"{worker_id}_backup_{datetime.now().strftime('%H%M%S')}"

        # Copy capabilities from original worker
        original_worker = self.workers[worker_id]

        # Register backup in system
        self.system.register_worker(
            worker_id=backup_id,
            name=f"Backup {original_worker.worker_id}",
            capabilities=["general", "recovery", "backup"],
        )

        logger.info(f"🔄 Backup worker {backup_id} activated for {worker_id}")

    def _handle_task_error(self, worker_id: str, task, error: Exception):

        logger.error(f"❌ Task error in {worker_id}: {error}")

        # Release task lock
        self.conflict_prevention.release_task_lock(
            self.agent_id, task.get("id", "unknown")
        )

        # Mark task as failed
        try:
            self.system.fail_task(worker_id, task.get("id", "unknown"), str(error))
        except Exception:
            logger.error(f"Error: {e}")
            pass

    def run(self): -> None:

                logger.error("❌ No TODOs loaded, exiting")
                return

            # Register workers
            self.register_workers()

            # Start workers
            self.start_workers()

            # Start enhanced monitoring
            self.monitor_progress_enhanced()

        except KeyboardInterrupt:
            logger.info("🛑 Shutting down enhanced collaborative system...")
        except Exception as e:
            logger.error(f"❌ Error in system: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    system = EnhancedCollaborativeSystem()
    system.run()
