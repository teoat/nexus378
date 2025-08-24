document.addEventListener('DOMContentLoaded', () => {
    const appModeElement = document.getElementById('appMode');
    const thinkingPerspectiveElement = document.getElementById('thinkingPerspective');
    const aiModeElement = document.getElementById('aiMode');
    const dashboardViewElement = document.getElementById('dashboardView');
    const userRoleElement = document.getElementById('userRole');
    const sessionIdElement = document.getElementById('sessionId');
    const lastUpdatedElement = document.getElementById('lastUpdated');
    const agentStatusGrid = document.getElementById('agentStatusGrid');
    const workflowStatusGrid = document.getElementById('workflowStatusGrid'); // New
    const startReconciliationWorkflowButton = document.getElementById('startReconciliationWorkflow'); // New
    const eventLog = document.getElementById('eventLog');
    const overallHealthStatusElement = document.getElementById('overallHealthStatus'); // New
    const healthScoreElement = document.getElementById('healthScore'); // New
    const restartAllFailedAgentsButton = document.getElementById('restartAllFailedAgentsButton'); // New
    const errorLogElement = document.getElementById('errorLog'); // New
    const totalCommandsElement = document.getElementById('totalCommands'); // New
    const successfulCommandsElement = document.getElementById('successfulCommands'); // New
    const failedCommandsElement = document.getElementById('failedCommands'); // New
    const avgResponseTimeElement = document.getElementById('avgResponseTime'); // New

    const appModeButtons = document.getElementById('appModeButtons');
    const thinkingPerspectiveButtons = document.getElementById('thinkingPerspectiveButtons');
    const aiModeButtons = document.getElementById('aiModeButtons');

    const API_BASE_URL = 'http://localhost:8000/api/frenly';

    let ws;

    function connectWebSocket() {
        ws = new WebSocket(`ws://localhost:8000/api/frenly/ws/frenly`);

        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('WebSocket message received:', message);

            if (message.type === 'initial_state' || message.type === 'state_update') {
                updateDashboard(message.data);
            }
        };

        ws.onclose = (event) => {
            console.log('WebSocket disconnected', event);
            // Attempt to reconnect after a delay
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            ws.close();
        };
    }

    function updateDashboard(data) {
        const { app_context, agent_status, recent_events } = data;

        // Update App Context
        if (app_context) {
            appModeElement.textContent = app_context.app_mode;
            thinkingPerspectiveElement.textContent = app_context.thinking_perspective || 'None';
            aiModeElement.textContent = app_context.ai_mode;
            dashboardViewElement.textContent = app_context.dashboard_view;
            userRoleElement.textContent = app_context.user_role;
            sessionIdElement.textContent = app_context.session_id;
            lastUpdatedElement.textContent = new Date(app_context.timestamp).toLocaleString();

            // Update active button states
            updateButtonActiveState(appModeButtons, app_context.app_mode);
            updateButtonActiveState(thinkingPerspectiveButtons, app_context.thinking_perspective || 'none');
            updateButtonActiveState(aiModeButtons, app_context.ai_mode);
        }

        // Update Agent Status
        if (agent_status) {
            agentStatusGrid.innerHTML = ''; // Clear previous status
            for (const agentName in agent_status) {
                const status = agent_status[agentName];
                const agentCard = document.createElement('div');
                agentCard.classList.add('agent-card', status.status.toLowerCase());
                agentCard.innerHTML = `
                    <div class="agent-name">${agentName}</div>
                    <div>Status: ${status.status}</div>
                    <div>Last Seen: ${new Date(status.last_seen).toLocaleTimeString()}</div>
                `;
                agentStatusGrid.appendChild(agentCard);
            }
        }

        // Update Workflow Status
        if (data.workflow_status) {
            workflowStatusGrid.innerHTML = ''; // Clear previous status
            const workflows = Object.values(data.workflow_status);
            if (workflows.length === 0) {
                workflowStatusGrid.innerHTML = 'No active workflows.';
            } else {
                workflows.forEach(workflow => {
                    const workflowCard = document.createElement('div');
                    workflowCard.classList.add('agent-card', workflow.status.toLowerCase()); // Reusing agent-card styling
                    workflowCard.innerHTML = `
                        <div class="agent-name">Workflow: ${workflow.name} (${workflow.id.substring(0, 8)}...)</div>
                        <div>Status: ${workflow.status}</div>
                        <div>Current Step: ${workflow.current_step !== -1 ? workflow.steps[workflow.current_step].name : 'N/A'}</div>
                        <div>Message: ${workflow.message}</div>
                        <div>Started: ${new Date(workflow.start_time).toLocaleTimeString()}</div>
                    `;
                    workflowStatusGrid.appendChild(workflowCard);
                });
            }
        }

        // Update Recent Events
        if (recent_events) {
            eventLog.innerHTML = ''; // Clear previous events
            recent_events.forEach(event => {
                const eventItem = document.createElement('div');
                eventItem.classList.add('event-item');
                eventItem.innerHTML = `
                    <span class="event-timestamp">${new Date(event.timestamp).toLocaleString()}</span>
                    <span class="event-severity-${event.severity}">${event.severity}:</span>
                    ${event.event_type} - ${JSON.stringify(event.details)}
                `;
                eventLog.appendChild(eventItem);
            });
        }

        // Update System Health
        if (data.system_health) {
            overallHealthStatusElement.textContent = data.system_health.overall_status;
            healthScoreElement.textContent = data.system_health.health_score;
        }

        // Update Error Log
        if (data.error_log) {
            errorLogElement.innerHTML = ''; // Clear previous errors
            data.error_log.forEach(error => {
                const errorItem = document.createElement('div');
                errorItem.classList.add('event-item'); // Reusing event-item styling
                errorItem.innerHTML = `
                    <span class="event-timestamp">${new Date(error.timestamp).toLocaleString()}</span>
                    <span class="event-severity-${error.severity}">${error.severity}:</span>
                    ${error.event_type} - ${JSON.stringify(error.details)}
                `;
                errorLogElement.appendChild(errorItem);
            });
        }

        // Update Metrics
        if (data.metrics) {
            totalCommandsElement.textContent = data.metrics.total_commands;
            successfulCommandsElement.textContent = data.metrics.successful_commands;
            failedCommandsElement.textContent = data.metrics.failed_commands;
            avgResponseTimeElement.textContent = `${data.metrics.average_response_time_ms} ms`;
        }
    }

    function updateButtonActiveState(buttonContainer, activeValue) {
        Array.from(buttonContainer.children).forEach(button => {
            if (button.dataset.mode === activeValue) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    async function sendModeChangeRequest(modeType, value) {
        const payload = {};
        if (modeType === 'app_mode') payload.app_mode = value;
        else if (modeType === 'thinking_perspective') payload.thinking_perspective = value;
        else if (modeType === 'ai_mode') payload.ai_mode = value;

        try {
            const response = await fetch(`${API_BASE_URL}/switch-mode`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();
            if (result.success) {
                console.log('Mode change successful:', result.message);
                // WebSocket will push the update, so no need to manually update UI here
            } else {
                console.error('Mode change failed:', result.message);
                alert(`Failed to change mode: ${result.message}`);
            }
        } catch (error) {
            console.error('Error sending mode change request:', error);
            alert('Network error or API is down.');
        }
    }

    // Add event listeners to buttons
    appModeButtons.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON') {
            sendModeChangeRequest('app_mode', event.target.dataset.mode);
        }
    });

    thinkingPerspectiveButtons.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON') {
            sendModeChangeRequest('thinking_perspective', event.target.dataset.mode);
        }
    });

    aiModeButtons.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON') {
            sendModeChangeRequest('ai_mode', event.target.dataset.mode);
        }
    });

    async function startWorkflow(workflowName) {
        try {
            const response = await fetch(`${API_BASE_URL}/workflows/${workflowName}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            if (result.success) {
                console.log('Workflow started successfully:', result.message);
                // WebSocket will push the update, so no need to manually update UI here
            } else {
                console.error('Failed to start workflow:', result.message);
                alert(`Failed to start workflow: ${result.message}`);
            }
        } catch (error) {
            console.error('Error sending workflow request:', error);
            alert('Network error or API is down.');
        }
    }

    startReconciliationWorkflowButton.addEventListener('click', () => {
        startWorkflow('reconciliation_check');
    });

    restartAllFailedAgentsButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/agents/restart-all-failed`, {
                method: 'POST',
            });
            const result = await response.json();
            if (result.success) {
                console.log('Restart all failed agents successful:', result.message);
            } else {
                console.error('Failed to restart all failed agents:', result.message);
                alert(`Failed to restart all failed agents: ${result.message}`);
            }
        } catch (error) {
            console.error('Error restarting all failed agents:', error);
            alert('Network error or API is down.');
        }
    });

    // Initial WebSocket connection
    connectWebSocket();
});
