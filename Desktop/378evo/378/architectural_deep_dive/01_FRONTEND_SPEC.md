# Frontend Specification: Forensic Analysis Platform

**Version:** 1.0
**Status:** Draft

## 1. Overview

### 1.1. What & Why

This document details the architecture and implementation plan for the frontend of the Forensic Analysis Platform. The primary goal is to create a highly interactive, responsive, and intuitive user interface that can handle complex data visualization and user workflows.

The "what" is a modern web application built with **React and Next.js**. The "why" is to leverage a mature, component-based ecosystem that excels at building data-intensive applications, while benefiting from Next.js's performance optimizations (SSR, SSG) and developer experience features.

### 1.2. When (Development Timeline)

*   **Months 1-2:** Core UI kit and component library development. Setup of Storybook for component isolation.
*   **Months 3-4:** Implementation of core layouts, navigation, and user authentication flows.
*   **Months 5-7:** Development of the main feature UIs: Case Management, Data Ingestion, and the Reconciliation/Adjudication interface.
*   **Months 8-10:** Focus on advanced data visualizations, including the entity relationship graph and interactive financial dashboards.
*   **Months 11-12:** User testing, performance optimization, accessibility audit (WCAG compliance), and final polish.

## 2. UI/UX Design Philosophy

*   **Clarity Over Clutter:** The UI must present complex information in a clear and digestible manner. Use progressive disclosure to avoid overwhelming the user.
*   **Interactive & Responsive:** All components, especially charts and graphs, must be interactive, allowing users to drill down into the data. The application must be fully responsive and functional across modern desktop browsers.
*   **Guided Workflows:** The UI should guide the user through complex tasks like data reconciliation or case investigation, providing clear next steps and contextual information.
*   **Educational:** As per the project requirements, the UI will incorporate educational elements (e.g., tooltips, simple illustrations) to explain complex forensic and accounting concepts to non-expert users.

## 3. Core Modules & Components

### 3.1. Module Breakdown

*   `components/`: Reusable, atomic UI components (buttons, inputs, modals).
*   `features/`: Composed components that encapsulate the logic for a specific application feature (e.g., `CaseDashboard`, `TransactionTable`).
*   `lib/`: Shared utilities, API client, and helper functions.
*   `hooks/`: Custom React hooks for managing state and side effects.
*   `pages/`: Next.js page routes.
*   `state/`: Global state management logic (e.g., Zustand or Redux Toolkit).
*   `styles/`: Global styles and theme configuration (e.g., Tailwind CSS config).
*   `stories/`: Storybook stories for each component.

### 3.2. Key UI Components (Examples)

*   **`InteractiveDataTable`:** A virtualized and server-paginated table for displaying millions of transactions efficiently. Will support sorting, filtering, and row selection.
*   **`GraphVisualizer`:** A component using a library like `react-flow` or `d3` to render the interactive Neo4j entity relationship maps.
*   **`MultiStepForm`:** A wizard-like component to guide users through the data ingestion and case setup process.
*   **`AdjudicationPanel`:** A side-by-side view for manually comparing and reconciling two transactions, with controls for linking evidence and adding notes.
*   **`DashboardWidget`:** A generic container for displaying KPIs and charts on the main dashboard, configurable for different metrics.
*   **`ColumnMappingInterface`:** An advanced UI for the data ingestion flow. It will allow users to visually map columns from an uploaded file to the system's target fields. It will support both **Primary Matching Fields** (required for reconciliation) and **Additional Data Fields** (for future analysis), and allow users to save and load these mappings as templates.
*   **`ReconciliationScopeForm`:** A new component that allows users to define the scope of the automated matching process (e.g., by month, trimester, or all transactions).
*   **`LiveReconciliationDashboard`:** A new real-time dashboard that replaces static progress bars. It will use WebSockets to display a live feed of **Matched** and **Unmatched** transactions as the AI processes them, including a "Match Rationale" for transparency.
*   **`DiscrepancyReport`:** A component to display data quality issues, such as missing statements or balance mismatches, with clear explanations and links to resolve them. This will be presented as a final, integrated step in the ingestion workflow.

## 4. Functions & Methods (Conceptual)

*   **`useApi(endpoint, options)`:** A custom hook that wraps `fetch` or `axios` for standardized data fetching, caching (with `swr` or `react-query`), and error handling.
*   **`formatCurrency(amount, currency)`:** A utility function for consistent currency formatting.
*   **`api.cases.create(data)`:** An example function from the typed API client for interacting with the Node.js gateway.

## 5. Error Handling

*   **Component Boundaries:** Use React's Error Boundaries to catch rendering errors in specific parts of the UI, preventing a full application crash. A generic "Something went wrong" component will be displayed.
*   **API Errors:** The `useApi` hook will have a standardized way of catching and handling API errors. Toast notifications will be used for non-critical errors, while modals or dedicated error pages will be used for critical failures (e.g., 403 Forbidden, 500 Internal Server Error).
*   **Form Validation:** Use a library like `react-hook-form` or `formik` for robust, real-time client-side form validation before submitting data to the backend.

## 6. Testing Strategy

*   **Unit Tests (Jest / Vitest + React Testing Library):** Each individual component will have unit tests to verify its rendering and behavior in isolation. Target coverage: **#95%**.
*   **Integration Tests (React Testing Library):** Test the interaction between multiple components within a feature (e.g., testing the entire data ingestion form).
*   **End-to-End Tests (Cypress / Playwright):** Simulate full user workflows across the application, from login to report generation. These will run against a dedicated test environment.
*   **Visual Regression Tests (Storybook + Chromatic):** Automatically detect unintended visual changes to UI components.

## 7. Input & Output (API Interaction)

### 7.1. Intended Input (User Actions)

*   Uploading files via a drag-and-drop interface.
*   Filling out forms to create cases or configure analysis.
*   Clicking, dragging, and zooming within graph visualizations.
*   Manually linking transactions in the adjudication panel.

### 7.2. Supposed Output (API Payloads)

*   **Example: Create Case Payload**
    ```json
    // POST /api/v1/cases
    {
      "caseName": "Q3 Financial Irregularities",
      "description": "Investigating potential embezzlement in the third quarter.",
      "leadInvestigatorId": "user-uuid-123"
    }
    ```
*   **Example: Fetch Transactions Query**
    ```
    // GET /api/v1/transactions?caseId#case-uuid-456&page#1&limit#100&sortBy#date&order#desc
    ```
*   **Example: Save Column Mapping Payload (with Templates)**
    ```json
    // POST /api/v1/mappings
    {
      "templateName": "Q2 Bank Statements", // Optional
      "caseId": "case-uuid-456", // Optional: link template to a case
      "mappings": {
        "primary": [
          { "source": "Transaction ID", "target": "transactionId" },
          { "source": "Value Date", "target": "date" },
          { "source": "Amount", "target": "amount" }
        ],
        "additional": [
          { "source": "Branch Code", "target": "custom_branch_code" },
          { "source": "Memo", "target": "custom_memo" }
        ]
      }
    }
    ```
*   **Example: Start Reconciliation Payload**
    ```json
    // POST /api/v1/cases/case-uuid-456/reconciliation
    {
      "fileId": "file-uuid-789",
      "mappingId": "mapping-uuid-abc",
      "scope": "trimester", // "month", "all"
      "scopeValue": "Q3" // e.g., "July", "Q3", null
    }
    ```

## 8. Current Implementation & Future Improvements

*   **Current Coverage:** This is a new module, so initial coverage is 0%.
*   **Future Improvements:**
    *   **WebSockets:** Integrate a WebSocket client to receive real-time updates from the backend (e.g., analysis progress, new fraud alerts) without needing to poll.
    *   **Internationalization (i18n):** Architect the application with i18n in mind from the start, using a library like `react-i18next` to allow for future language support.
    *   **Theming:** Implement a robust theming system (e.g., CSS variables) to allow for easy customization and a potential "dark mode."
## 9. Advanced Feature Integration

This section details the frontend implementation for the advanced features outlined in the `07_ADVANCED_FEATURES_SPEC.md`.

### 9.1. Live Operations Dashboard

*   **New Components:**
    *   `DashboardGrid`: A customizable grid layout component (using a library like `react-grid-layout`) to host the dashboard widgets.
    *   `WebSocketProvider`: A React Context provider that will manage the WebSocket connection to the Node.js gateway and distribute real-time data to the components that need it.
    *   `StatusIndicatorWidget`: A component to display the real-time status of backend services.
    *   `ProgressWidget`: A component to display the live progress of asynchronous jobs.
*   **Data Flow:** Components within the dashboard will use a `useWebSocket()` hook to subscribe to specific real-time events. The `WebSocketProvider` will handle the underlying message parsing and state updates.

### 9.2. Proactive AI Help System

*   **New Components:**
    *   `HelpLauncher`: The floating icon that opens the help interface.
    *   `HelpChatPanel`: The chat-like interface where users can interact with the `HelpAgent`.
    *   `ContextualSuggestion`: A small, non-intrusive pop-up component that can be attached to other UI elements to display tips from the `HelpAgent`.
*   **Implementation:** A `useHelpContext()` hook will be created to send contextual information (e.g., current page, active component) to the backend and receive suggestions via the WebSocket connection.

### 9.3. Meta-Design Agent ("App-within-an-App")

*   **New Components:**
    *   `DesignStudio`: A new top-level page component that serves as the main interface for the `MetaDesignAgent`.
    *   `FileTreeBrowser`: A component to display the project's file structure.
    *   `CodeEditor`: A read-only code editor component (using a library like Monaco or CodeMirror) to display file contents.
    *   `DiffViewer`: A component to display the proposed code changes in a side-by-side or unified diff format.
*   **Workflow:** The Design Studio will be a complex state machine, managing the conversation with the agent, displaying the agent's plan, and presenting the final proposed changes for user approval.