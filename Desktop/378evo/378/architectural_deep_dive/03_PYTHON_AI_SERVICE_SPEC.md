# Python AI Service Specification

**Version:** 1.0
**Status:** Draft

## 1. Overview

### 1.1. What & Why

This document details the architecture for the **Python AI Service**. This service is the analytical and computational core of the entire platform, responsible for all heavy-lifting related to data processing, machine learning, and agentic workflows.

*   **What:** A high-performance, asynchronous API service built with **FastAPI**, leveraging **LangChain** and **LangGraph** to orchestrate complex AI tasks.
*   **Why:**
    1.  **Specialization:** It isolates the complex, computationally-intensive Python environment from the rest of the application stack, allowing each component to be scaled and maintained independently.
    2.  **Performance:** FastAPI's asynchronous nature, built on Starlette and Pydantic, provides performance that is on par with Node.js and Go, making it ideal for an I/O-bound service that also handles long-running CPU-bound tasks.
    3.  **State-of-the-Art AI Tooling:** It allows us to directly leverage the rich Python ecosystem for AI/ML, including libraries like LangChain, LangGraph, scikit-learn, PyTorch, and Hugging Face transformers.
    4.  **Agentic Architecture:** LangGraph is the perfect tool to implement the specified `SuperAgent` framework, enabling the creation of stateful, cyclical, and resilient agents for forensic analysis.

### 1.2. When (Development Timeline)

*   **Months 1-3:** Develop the core Data Ingestion and Processing module, including file parsers and data validation/normalization logic.
*   **Months 4-6:** Implement the `AdvancedMatchingEngine` with its full suite of pluggable matching strategies.
*   **Months 5-7:** Build out the `FraudDetectionEngine` and integrate the rule-based logic from `fraud_rules.json`.
*   **Months 7-9:** Implement the full `SuperAgent` and specialized agent framework using LangGraph. Define the tools and workflows for each agent.
*   **Months 10-12:** Rigorous testing, performance optimization (e.g., model quantization, caching), and deployment hardening.

## 2. Core Modules & Responsibilities

### 2.1. Module Breakdown

*   **`api/`**: FastAPI application, containing the API routers and endpoint definitions.
*   **`agents/`**: Contains the LangGraph definitions for the `SuperAgent` and all specialized agents (`ValidationAgent`, `FraudScoringAgent`, `ReconciliationAgent`, etc.).
*   **`processing/`**: The core data processing pipelines.
    *   `ingestion/`: File parsers, OCR logic, data cleaning. This module will now dynamically apply user-defined column mappings during the ingestion process.
    *   `matching/`: The `AdvancedMatchingEngine` and its plugins.
    *   `fraud_detection/`: The `FraudDetectionEngine` and rule interpreters.
    *   `discrepancy_detection/`: A new module responsible for identifying data quality issues, such as gaps in statement dates or mismatches in running balances.
*   **`tools/`**: A library of "tools" that can be provided to the LangGraph agents. For example, `find_related_transactions` or `calculate_fraud_score`. These tools are the bridge between the agent's reasoning loop and the application's core logic. New tools will be added:
    *   `apply_column_mappings(data, mappings)`: Transforms raw ingested data based on user-defined mappings.
    *   `detect_statement_gaps(transactions)`: Identifies missing periods in sequential bank statements.
    *   `generate_provisional_report(data, discrepancies)`: Creates financial reports that clearly mark sections affected by data discrepancies.
*   **`workers/`**: Asynchronous task workers (e.g., Celery or ARQ) that consume jobs from the RabbitMQ message queue.
*   **`models/`**: Pydantic models for data validation and serialization, and potentially ML model files.
*   **`config/`**: Configuration management.

## 3. Functions & Methods (Conceptual)

*   **`workers.run_reconciliation_task(job_id, case_id, file_id, mapping_id, scope)`**: The entry point for the new reconciliation job. This will instantiate and run the `ReconciliationAgent`.
*   **`agents.create_super_agent_graph()`**: A function that constructs and returns a compiled LangGraph runnable, representing the main agent's workflow.
*   **`tools.transaction_matcher.invoke(input_data)`**: A LangChain `Tool` that exposes the `AdvancedMatchingEngine` to the agent framework. The agent can decide to call this tool with specific data.
*   **`api.routers.health.get()`**: A simple health check endpoint (`/health`) for monitoring and service discovery.

## 4. Error Handling

*   **FastAPI Exception Handlers:** Custom exception handlers will be registered to catch specific application errors (e.g., `AnalysisError`, `InvalidFileFormatError`) and return appropriate HTTP status codes and error details.
*   **Pydantic Validation:** FastAPI's use of Pydantic provides automatic, robust request validation. Invalid requests will immediately return a `422 Unprocessable Entity` response with detailed error messages.
*   **Asynchronous Task Retries:** The asynchronous workers will be configured with a retry policy (e.g., exponential backoff) for transient errors (e.g., temporary database unavailability). A "dead-letter queue" will be used to capture jobs that fail repeatedly for manual inspection.
*   **Agent-Level Error Handling:** Within LangGraph, transitions can be defined to handle tool execution errors, allowing an agent to retry a failed tool, try a different tool, or escalate the failure to a human reviewer.

## 5. Testing Strategy

*   **Unit Tests (pytest):** Each function, tool, and processing module will be tested in isolation. Dependencies will be heavily mocked. Target coverage: **#95%**.
*   **Integration Tests (pytest):** Test the integration between different internal modules, such as an agent calling a specific tool that interacts with a (test) database.
*   **API Contract Tests (pytest + requests):** Test the FastAPI endpoints to ensure they adhere to the defined OpenAPI specification.
*   **Workflow Tests:** Test the entire LangGraph agent workflow from start to finish with mock data to ensure the logic and state transitions are correct.

## 6. Input & Output

### 6.1. Intended Input

*   **Synchronous API Calls (from Node.js Gateway):** gRPC or REST requests for quick, specific tasks (e.g., "validate this transaction description").
*   **Asynchronous Jobs (from RabbitMQ):** JSON payloads representing long-running tasks (e.g., "run a full analysis on this case").

### 6.2. Supposed Output

*   **Synchronous API Responses:** JSON responses containing the results of a specific task.
*   **Real-time Match Results:** During reconciliation, the `ReconciliationAgent` will publish individual match/unmatch results to a dedicated RabbitMQ topic. This provides the real-time feed for the frontend's `LiveReconciliationDashboard`.
*   **Final Results:** The primary output of the service is the data it writes to the databases (PostgreSQL and Neo4j) upon completion of an analysis.
*   **Stored Results:** The primary output of the service is the data it writes to the databases (PostgreSQL and Neo4j) upon completion of an analysis.

## 7. Current Implementation & Future Improvements

*   **Current Coverage:** The existing `378/` directory contains a significant portion of the core logic that will be refactored into this service. The task is primarily one of re-architecting, not starting from scratch.
*   **Future Improvements:**
    *   **GPU Acceleration:** For more advanced ML models, configure the service to leverage GPUs for inference to significantly improve performance.
    *   **Model Serving Optimization:** Use dedicated model serving frameworks like NVIDIA Triton Inference Server for highly optimized ML model deployment.
    *   **Multi-Agent Collaboration:** Evolve the `SuperAgent` framework to orchestrate multiple, concurrently running specialized agents that can collaborate to solve more complex problems.
## 8. Advanced Feature Integration

This section details the new agents and workflows required to power the advanced features.

### 8.1. Reconciliation Agent
*   **New Agent:** `ReconciliationAgent`
*   **Responsibility:** A new, specialized agent responsible for executing the guided reconciliation workflow.
*   **Triggers:** Consumes `reconciliation.start` jobs from RabbitMQ.
*   **Workflow:**
    1.  Retrieves the specified file and mapping template.
    2.  Applies the column mappings to the raw data.
    3.  Filters the transactions based on the user-defined `scope` (e.g., only transactions from July).
    4.  Invokes the `AdvancedMatchingEngine` on the scoped data.
    5.  As the engine produces results, the agent immediately publishes them to the `reconciliation.results` RabbitMQ topic.
    6.  Once complete, it stores the final results in the database.
*   **Tools:**
    *   `get_transactions_by_scope(scope, scope_value)`: A tool to fetch data based on the user's criteria.
    *   `invoke_matching_engine(transactions)`: The core tool to run the matching logic.
    *   `publish_match_result(result)`: A tool to publish a single result to RabbitMQ for real-time feedback.

### 8.2. Live Operations Dashboard Agent

*   **New Agent:** `DashboardAgent`
*   **Responsibility:** A long-running, stateful LangGraph agent that monitors the overall system state and generates contextual insights for the user's live dashboard.
*   **Triggers:** This agent will be initiated at the start of a user's session and will receive events from various sources (e.g., RabbitMQ topics for job progress, new fraud alerts).
*   **Tools:**
    *   `summarize_progress(job_updates)`: A tool to synthesize raw progress events into a human-readable summary.
    *   `identify_emerging_patterns(transaction_stream)`: A tool that uses statistical analysis to detect interesting patterns in the data being processed.
    *   `format_insight_for_dashboard(insight_text)`: A tool to format its findings into a structured JSON object suitable for a dashboard widget.
*   **Output:** Publishes insight messages to a dedicated RabbitMQ topic (e.g., `dashboard.insights.{userId}`), which the Node.js gateway will consume and push to the client via WebSockets.

### 8.2. Proactive AI Help System Agent

*   **New Agent:** `HelpAgent`
*   **Responsibility:** A RAG (Retrieval-Augmented Generation) agent that provides real-time, context-aware help to the user.
*   **Triggers:** Consumes user context messages from a dedicated RabbitMQ queue (`help.context`).
*   **Architecture:**
    1.  **Vector Store:** A vector database (e.g., ChromaDB, Pinecone) will be pre-loaded with embeddings of all documentation, tutorials, and best practice guides.
    2.  **Retriever:** When the agent receives a user's context, it will use a retriever to find the most relevant documents from the vector store.
    3.  **Generator:** The retrieved documents are passed, along with the user's context, to an LLM which generates a concise and helpful suggestion.
*   **Output:** Publishes the generated suggestion to a RabbitMQ topic (e.g., `help.suggestions.{userId}`) for delivery to the client via the WebSocket.

### 8.3. Meta-Design Agent

*   **New Agent:** `MetaDesignAgent`
*   **Responsibility:** A powerful, conversational agent that assists expert users in redesigning the application itself.
*   **Triggers:** Invoked via a synchronous gRPC call from the Node.js gateway.
*   **Tools (Powered by MCP):** This agent will be equipped with a powerful set of tools that interact with the local development environment via a dedicated MCP server.
    *   `list_files(directory: str) -# List[str]`: Lists files in a directory.
    *   `read_file(file_path: str) -# str`: Reads the content of a file.
    *   `write_file(file_path: str, content: str) -# bool`: Proposes writing new content to a file (requires user confirmation).
    *   `run_linter(directory: str) -# str`: Runs the project's linter to check for errors in the proposed code.
*   **Workflow (LangGraph):** The agent will follow a strict "analyze -# plan -# generate -# present" workflow, with a mandatory human-in-the-loop confirmation step before any file modifications are proposed. This ensures safety and user control.