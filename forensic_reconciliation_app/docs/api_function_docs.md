# API and Function Documentation

This document outlines the API endpoints and key functions within the Frenly system.

## API Endpoints (FastAPI)

The Frenly API is built using FastAPI and provides the following endpoints:

*   `/api/frenly/status`: Get Frenly's current status and context.
*   `/api/frenly/context`: Get Frenly's current app context.
*   `/api/frenly/switch-mode`: Switch Frenly's operating mode.
*   `/api/frenly/mode-intersection`: Get the current mode intersection details.
*   `/api/frenly/workflow`: Execute a workflow through Frenly.
*   `/api/frenly/workflows`: List available workflows.
*   `/api/frenly/agents`: List all registered agents.
*   `/api/frenly/agents/health`: Get health status of all agents.
*   `/api/frenly/agents/{agent_name}/health`: Get health status of a specific agent.
*   `/api/frenly/agents/{agent_name}/restart`: Restart a specific agent.
*   `/api/frenly/agents/restart-all-failed`: Restart all failed agents.
*   `/api/frenly/agents/heartbeat/start`: Start heartbeat monitoring of all agents.
*   `/api/frenly/agents/heartbeat/stop`: Stop heartbeat monitoring of all agents.
*   `/api/frenly/health/detailed`: Get detailed system health including agent health.
*   `/api/frenly/state/save`: Save current Frenly state to files.
*   `/api/frenly/state/load`: Load Frenly state from files.
*   `/api/frenly/state/context`: Get the currently saved app context.
*   `/api/frenly/state/modes`: Get the currently saved mode intersections.
*   `/api/frenly/events`: Get recent events with optional filtering.
*   `/api/frenly/events/summary`: Get a summary of events by type and severity.
*   `/api/frenly/events/types`: Get all available event types.
*   `/api/frenly/events/severities`: Get all available event severity levels.
*   `/api/frenly/errors`: Get recent error events from the error log.
*   `/api/frenly/metrics`: Get current performance metrics.
*   `/ws/frenly`: WebSocket endpoint for real-time state updates.

## Key Functions (Python)

This section will detail key functions within `frenly_meta_agent.py` and other modules.

### `FrenlyMetaAgent`

*   `__init__()`: Initializes the agent, loads state, and starts heartbeat monitoring.
*   `manage_app(command: AppCommand)`: Central method for processing app commands.
*   `_switch_app_mode(new_mode: str)`: Switches the application mode.
*   `_change_thinking_perspective(new_perspective: str)`: Changes the thinking perspective.
*   `_change_ai_mode(new_ai_mode: str)`: Changes the AI mode.
*   `_change_dashboard_view(new_view: str)`: Changes the dashboard view.
*   `_change_user_role(new_role: str)`: Changes the user role.
*   `_get_app_status()`: Retrieves the current application status.
*   `_get_current_mode_intersection_response()`: Gets details of the current mode intersection.
*   `_get_current_mode_intersection()`: Determines the current mode intersection.
*   `_update_mode_intersection()`: Updates the current mode intersection.
*   `register_ai_agent(agent_name: str, agent_instance: Any)`: Registers an AI agent.
*   `check_agent_alive(agent_name: str)`: Checks if an agent is alive.
*   `_mark_agent_failed(agent_name: str, reason: str)`: Marks an agent as failed.
*   `get_agent_status(agent_name: str)`: Gets status of a specific agent.
*   `get_all_agent_status()`: Gets status of all registered agents.
*   `start_heartbeat_monitoring(interval_seconds: int)`: Starts background heartbeat monitoring.
*   `stop_heartbeat_monitoring()`: Stops background heartbeat monitoring.
*   `register_state_change_callback(callback: callable)`: Registers a callback for state changes.
*   `_notify_state_change()`: Notifies registered callbacks of state changes.
*   `restart_agent(agent_name: str, force: bool)`: Restarts an agent.
*   `restart_all_failed_agents()`: Restarts all failed agents.
*   `execute_workflow(workflow_name: str, workflow_id: Optional[str])`: Executes a workflow.
*   `_run_workflow(workflow_id: str)`: Internal method to run workflow steps.
*   `get_workflow_status(workflow_id: Optional[str])`: Gets workflow status.
*   `get_overall_system_health()`: Gets overall system health.
*   `get_ai_agent(agent_name: str)`: Gets a registered AI agent.
*   `list_ai_agents()`: Lists all registered AI agents.
*   `get_session_context(session_id: str)`: Gets session context.
*   `create_session(session_id: str, context: AppContext)`: Creates a new session.
*   `update_session(session_id: str, context: AppContext)`: Updates an existing session.
*   `remove_session(session_id: str)`: Removes a session.
*   `get_system_component_status(component: SystemComponent)`: Gets system component status.
*   `update_system_component_status(component: SystemComponent, status: str, metrics: Dict[str, Any])`: Updates system component status.
*   `check_service_status(service_name: str)`: Checks status of a known service.
*   `check_all_services_status()`: Checks status of all known services.
*   `get_known_services_status()`: Gets status of all known services.
*   `_save_context_to_file()`: Saves app context to file.
*   `_load_context_from_file()`: Loads app context from file.
*   `_save_modes_to_file()`: Saves modes to file.
*   `_load_modes_from_file()`: Loads modes from file.
*   `_log_event(event_type: str, details: Dict[str, Any], severity: str)`: Logs an event.
*   `get_recent_events(limit: int, event_type: str, severity: str)`: Gets recent events.
*   `get_event_summary()`: Gets event summary.
*   `get_error_log(limit: int)`: Gets recent error events.
*   `get_metrics()`: Gets current performance metrics.

### Other Modules

*   `frenly_data_stream_consumer.py`: RabbitMQ consumer for real-time data streaming.
*   `data_validator_cleanser.py`: Data validation and cleansing logic.
*   `frenly_data_storage.py`: PostgreSQL integration for data storage.
*   `conflict_resolver.py`: Logic for resolving data conflicts.
*   `anomaly_detector.py`: Anomaly detection using IsolationForest.
*   `frenly_reporter.py`: Text-based reconciliation reports.
*   `frenly_alerter.py`: Logging-based alert mechanisms.
*   `distributed_processor.py`: Simulated distributed computation.
