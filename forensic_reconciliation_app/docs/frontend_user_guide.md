# Frontend User Guide

This guide provides instructions on how to use the Frenly Dashboard frontend.

## Getting Started

1.  Ensure the Frenly API and WebSocket server are running.
2.  Open `frenly_dashboard.html` in your web browser.

## Dashboard Overview

The dashboard displays the current state of the Frenly system, including:

*   **Current App State:** Shows the active App Mode, Thinking Perspective, AI Mode, Dashboard View, User Role, Session ID, and Last Updated timestamp.
*   **Change Modes:** Buttons to switch between different App Modes, Thinking Perspectives, and AI Modes.
*   **Agent Status:** Real-time status of all registered AI agents.
*   **Workflow Status:** Status of currently running workflows.
*   **Recent Events:** A log of recent system events.
*   **System Health:** Overall health status and score of the Frenly system.
*   **Error Log:** A log of recent error events.
*   **Performance Metrics:** Key performance indicators like total commands, successful/failed commands, and average response time.

## Changing Modes

To change the Frenly's operating mode:

1.  Navigate to the "Change Modes" section.
2.  Click on the desired button under "App Mode", "Thinking Perspective", or "AI Mode".
3.  The dashboard will update in real-time to reflect the new state.

## Monitoring Agents

The "Agent Status" section provides an overview of all AI agents. Agents are color-coded:

*   **Green:** Active
*   **Yellow:** Restarting
*   **Red:** Failed

## Managing Workflows

To start a new workflow, click the "Start Reconciliation Workflow" button in the "Workflow Status" section. The status of running workflows will be displayed in real-time.

## Troubleshooting

Refer to the [Troubleshooting Guide](troubleshooting_guide.md) for common issues and solutions.
