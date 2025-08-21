# TODO Automation Agent

This directory contains the `todo_automation.py` script, a powerful tool for automatically finding and processing `TODO` comments within a codebase.

## Features

-   **Recursive Scanning:** Scans a given directory to find all files containing `TODO` comments.
-   **Specialized Agents:** Uses a pool of agents to process different types of TODOs based on tags (e.g., `[documentation]`, `[testing]`).
-   **Continuous Processing:** Runs in a continuous loop, periodically checking for new TODOs to process.
-   **Persistent Logging:** Tracks the status of all processed TODOs in a log file (`mcp_log.json`) to prevent re-work.

## Usage

To run the script, execute it from the root of the repository and provide the path to the directory you want to scan.

```bash
python3 Desktop/Nexus/forensic_reconciliation_app/ai_service/agents/todo_automation.py <path_to_directory>
```

### Example

To scan the entire `forensic_reconciliation_app` directory:

```bash
python3 Desktop/Nexus/forensic_reconciliation_app/ai_service/agents/todo_automation.py Desktop/Nexus/forensic_reconciliation_app/
```

You can also provide an optional second argument for the path to the log file:

```bash
python3 Desktop/Nexus/forensic_reconciliation_app/ai_service/agents/todo_automation.py <path_to_directory> <path_to_log_file>
```
