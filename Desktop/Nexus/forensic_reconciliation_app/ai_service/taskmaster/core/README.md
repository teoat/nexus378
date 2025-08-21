# MCP (Model Context Protocol) System

A comprehensive system for coordinating AI agents and preventing overlapping task implementations in the Forensic Reconciliation App.

## Overview

The MCP system provides:
- **Centralized Task Management**: All agents coordinate through a central server
- **Duplicate Prevention**: Prevents multiple agents from implementing the same task
- **Dependency Management**: Handles task dependencies and execution order
- **Agent Coordination**: Manages agent capabilities and task distribution
- **Scalable Architecture**: Supports multiple agents and concurrent task execution

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Server   │    │  Task Registry  │    │ MCP Integration │
│                 │    │                 │    │                 │
│ • Task Queue   │◄──►│ • Prevents      │◄──►│ • Workflow      │
│ • Agent Mgmt   │    │   Duplicates    │    │   Integration   │
│ • Coordination │    │ • Dependencies   │    │ • Agent Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client   │    │   Example       │    │   Configuration │
│                 │    │   Agents        │    │                 │
│ • Agent        │    │ • Forensic      │    │ • Data Proc     │
│   Interface    │    │ • Custom        │    │ • Environment   │
│ • Task         │    │ • Validation    │    │ • Settings      │
│   Processing   │    │   Implementations│   │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### 1. MCP Server (`mcp_server.py`)
- Central coordination hub for all agents
- Manages task queue and agent registration
- Handles task assignment and status tracking

### 2. MCP Client (`mcp_client.py`)
- Interface for agents to interact with the MCP system
- Provides base classes for agent implementation
- Handles task claiming and completion

### 3. Task Registry (`simple_registry.py`)
- Prevents duplicate task implementations
- Manages task dependencies
- Tracks which agent implemented each task

### 4. MCP Integration (`mcp_integration.py`)
- Connects the MCP system with workflow orchestrator
- Manages agent lifecycle
- Provides high-level interface for workflow integration

### 5. Example Agents (`example_agent.py`)
- Demonstrates how to implement agents using the MCP system
- Shows forensic analysis and data processing agents
- Provides templates for custom agent development

### 6. Configuration (`mcp_config.py`)
- Centralized configuration management
- Environment variable support
- Validation and default values

## Quick Start

### 1. Basic Usage

```python
from .mcp_integration import mcp_integration
from .example_agent import create_example_agents

# Create and start agents
forensic_agent, data_agent = await create_example_agents(mcp_integration)

# Submit a task
task_id = await mcp_integration.register_workflow_task(
    "Analyze Memory Dump",
    "Perform memory analysis on forensic memory dump file"
)
```

### 2. Custom Agent Implementation

```python
from .mcp_client import AgentBase

class CustomAgent(AgentBase):
    def __init__(self):
        capabilities = ["custom_capability1", "custom_capability2"]
        super().__init__("CustomAgent", capabilities)
    
    def _can_handle_task(self, task):
        # Custom logic to determine if agent can handle task
        return "custom" in task.name.lower()
    
    async def _execute_task(self, task):
        # Custom task execution logic
        result = await self._perform_custom_analysis(task)
        return {"status": "completed", "result": result}
```

### 3. Task Dependencies

```python
# Create dependent tasks
task1_id = await mcp_integration.register_workflow_task(
    "Data Collection",
    "Collect forensic data from sources"
)

task2_id = await mcp_integration.register_workflow_task(
    "Data Analysis",
    "Analyze collected data",
    dependencies=[task1_id]  # Depends on task1 completion
)
```

## Configuration

### Environment Variables

```bash
# Server Configuration
export MCP_HOST=localhost
export MCP_PORT=8000
export MCP_MAX_AGENTS=100
export MCP_MAX_TASKS=1000

# Agent Configuration
export MCP_MAX_CONCURRENT_TASKS=3
export MCP_TASK_POLL_INTERVAL=5

# Logging
export MCP_LOG_LEVEL=INFO
export MCP_LOG_FILE=mcp_system.log
```

### Configuration Validation

```python
from .mcp_config import validate_config

if validate_config():
    print("Configuration is valid")
else:
    print("Configuration validation failed")
```

## Features

### Duplicate Prevention
- Automatic detection of duplicate task submissions
- Hash-based task identification
- Prevents multiple agents from implementing the same functionality

### Dependency Management
- Task dependency tracking
- Automatic dependency resolution
- Prevents circular dependencies

### Agent Capabilities
- Capability-based task assignment
- Dynamic capability registration
- Load balancing across agents

### Monitoring and Metrics
- Real-time system status
- Agent performance tracking
- Task execution metrics

## Best Practices

### 1. Agent Design
- Implement specific capabilities rather than general-purpose agents
- Use meaningful capability names
- Handle task failures gracefully

### 2. Task Design
- Use descriptive task names and descriptions
- Define clear input/output schemas
- Set appropriate dependencies

### 3. Error Handling
- Implement retry logic for failed tasks
- Log detailed error information
- Provide fallback mechanisms

### 4. Performance
- Monitor agent performance metrics
- Adjust polling intervals based on load
- Use appropriate task timeouts

## Troubleshooting

### Common Issues

1. **Agent Registration Fails**
   - Check agent capabilities configuration
   - Verify MCP server is running
   - Check network connectivity

2. **Tasks Not Being Assigned**
   - Verify agent capabilities match task requirements
   - Check task dependencies are satisfied
   - Ensure agents are actively polling for tasks

3. **Duplicate Task Detection**
   - Verify task names and descriptions are unique
   - Check task registry for existing implementations
   - Review task submission logic

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for troubleshooting
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

## API Reference

### MCP Server Methods

- `register_agent(agent_id, name, capabilities)`: Register a new agent
- `submit_task(name, description, dependencies)`: Submit a new task
- `get_available_tasks(agent_id)`: Get tasks available for an agent
- `claim_task(agent_id, task_id)`: Claim a task for execution

### MCP Client Methods

- `register_with_server(server)`: Register agent with MCP server
- `get_available_tasks(server)`: Get available tasks
- `claim_task(server, task_id)`: Claim a task
- `complete_task(server, task_id, result)`: Mark task as completed

### Task Registry Methods

- `register_task(name, description, agent_id)`: Register task implementation
- `is_task_implemented(name, description)`: Check for duplicates
- `add_dependency(task_id, dependency_id)`: Add task dependency
- `get_dependencies(task_id)`: Get task dependencies

## Contributing

1. Follow the existing code structure
2. Add comprehensive logging
3. Include error handling
4. Write unit tests for new functionality
5. Update documentation

## License

This MCP system is part of the Forensic Reconciliation App and follows the same licensing terms.
