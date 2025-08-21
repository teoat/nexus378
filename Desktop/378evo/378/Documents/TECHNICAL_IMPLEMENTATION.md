# IntelliAudit AI: Technical Implementation Guide

## Modular Architecture Deep Dive

This document provides an updated, detailed explanation of the IntelliAudit AI application's modular architecture, including the new multi-mode operational system.

### Core Philosophy: The Power of Pipelines & User Control

IntelliAudit is a **data processing pipeline** that provides users with multiple levels of control over the analysis process. Data flows through a sequence of modules, and the user can choose how much automation to apply at each stage.

### High-Level Architectural Workflow & Operational Modes

The application now operates in one of three modes, which fundamentally changes how the pipeline is executed.

- **Guided Mode**: The default mode. The user manually triggers each major step: ingestion, mapping review, and the final analysis. All AI enhancement modules are configurable through the UI.
- **Automated Mode**: A "full power" mode. After file ingestion, the entire reconciliation and forensic analysis pipeline runs automatically. All AI modules are forcibly enabled for the most comprehensive results.
- **Cost-Optimized Mode**: A streamlined automated mode. The pipeline runs automatically but uses faster, less expensive AI models and disables non-essential, computationally-intensive enhancements (like sentiment analysis).

### Detailed Module Breakdown

#### Phase 2: Core Reconciliation Engine (Upgraded)

This is the heart of the application, where transactions are matched. It now uses a sophisticated, **iterative multi-pass strategy** for maximum accuracy.

- **1. Multi-Pass Matching Engine**: The `runMultiPassMatchingEngine` orchestrates the core reconciliation. Instead of a single pass, it iterates through a series of **Tolerance Tiers**.
  - **Strict Pass**: The first pass uses the user's exact tolerance settings, catching the most obvious matches with a high confidence score.
  - **Iterative Loosening**: Subsequent passes are run on the *remaining* unmatched data, each with slightly looser date or amount tolerances.
  - **Weighted Confidence Scoring**: Matches found in these more lenient passes are assigned a progressively lower confidence score, providing a clear indication of the match's quality.
- **2. AI Fuzzy Matching**: For records that remain unmatched after the multi-pass engine, this AI flow is invoked. It compares transaction descriptions using fuzzy logic to find the most difficult, non-exact matches. This step is configurable in Guided Mode and always active in Automated Mode.
- **3. ReconciliationTable UI**: This powerful interactive component displays the results of all matching passes, allowing for manual review and serving as the primary user workspace.

## Monitoring Plan: Server-Side Migration

This document outlines the key metrics and procedures for monitoring the health and performance of the new server-side architecture.

### Key Metrics to Monitor

The following metrics should be closely monitored to ensure the stability and performance of the new server-side flows:

#### Error Rates
- **Server-Side Errors (5xx)**: Monitor the error rates for the new AI flows (`ingestFileFlow`, `runAnalysisFlow`). A sudden spike in these errors could indicate a problem with the new implementation.
- **Client-Side Errors (4xx)**: Monitor for any unexpected client-side errors that may be related to the new server-side flows.

#### Performance
- **API Latency**: Monitor the latency of the new server-side flows. A significant increase in latency could indicate a performance bottleneck.
- **Page Load Times**: Monitor the page load times for the key pages in the application, such as the dashboard and the ingestion view.

#### Resource Utilization
- **CPU and Memory Usage**: Monitor the CPU and memory usage of the server. A sudden spike in resource utilization could indicate a problem with the new implementation.
- **Database Connections**: Monitor the number of database connections. A sudden spike in connections could indicate a problem with the new implementation.

### Monitoring Tools

The following tools will be used to monitor the key metrics:

- **Google Cloud Monitoring**: Use Google Cloud's built-in monitoring tools to track error rates, performance, and resource utilization.
- **Sentry**: Use Sentry for real-time error tracking and performance monitoring.
- **Custom Dashboards**: Create custom dashboards to visualize the key metrics and track trends over time.

### Alerting

Configure alerts to notify the team of any significant changes in the key metrics. Alerts should be sent via email and Slack to ensure that the team is aware of any potential issues in a timely manner.

### On-Call Rotation

Establish an on-call rotation to ensure that there is always someone available to respond to alerts and address any issues that may arise.

## Master TODO List & Future Roadmap

**Rule:** This document is the **single source of truth** for all planned enhancements, features, and optimizations. All new tasks, ideas, and backlogged items must be added here to ensure a unified project roadmap.

### ✅ **Hydration Error Eradication Initiative (Completed)**

**Objective:** Systematically identify and eliminate all Next.js hydration errors to ensure a stable and reliable user experience. This was the highest priority task and is now complete.

**Workflow:**
1. [x] **Install Comprehensive Debugger**: Integrate a hydration debugger that provides both full HTML snapshot diffs and real-time node mismatch detection.
2. [x] **Run & Analyze**: Build and run the application in a production-like environment (`npm run build && npm start`) and analyze the developer console for the debugger's output.
3. [x] **Identify Root Cause**: Use the debugger's output and the knowledge base below to pinpoint the exact component and line of code causing the server/client mismatch.
4. [x] **Implement Targeted Fix**: Apply a definitive, targeted fix based on the recommendations.
5. [x] **Loop or Conclude**: All known hydration error patterns have been addressed and fixed.

### **Hydration Error Knowledge Base: Key Categories**

#### **Category: Environment & Data Divergence**
- **`new Date()`**: Server and client have different times/timezones. **Solution**: Render a placeholder on the server. Use a `useEffect` hook to set and format the date exclusively on the client.
- **`Math.random()`**: Generates different numbers on server and client. **Solution**: Generate the random number within a `useEffect` hook and store it in state.
- **`window` / `document` / `navigator`**: These objects only exist on the client. **Solution**: Guard access with `typeof window !## 'undefined'` or, for rendering, move the component logic into a `useEffect`.

#### **Category: React & State Management**
- **Incorrect Initial State**: `useState` or a store (Zustand, Redux) initialized with a dynamic or client-only value. **Solution**: The default state must be a static value that is identical on server and client.
- **Conditional Rendering Mismatches**: e.g., `isMobile ? #A /# : #B /#`. **Solution**: Base the `isMobile` check on a custom hook that uses `useEffect` to safely check the window size on the client.
- **Missing `key` Prop in Lists**: Rendering a list without a stable, unique `key` for each item. **Solution**: Always provide a unique and consistent `key` (like a database ID) for every element in a mapped array.

#### **Category: HTML & CSS Structure**
- **Invalid HTML Nesting**: e.g., `#p#` inside another `#p#`, or a `#div#` inside a `#span#`. **Solution**: Use a validator and ensure your JSX produces semantically correct HTML. The browser's auto-correction will cause a mismatch.
- **Missing `#tbody#`**: Browsers automatically insert `#tbody#` into `#table#` elements. **Solution**: Always explicitly include `#tbody#` in your React components for tables to match the browser's behavior.
- **HTML Attribute Mismatches**: Conditionally adding an attribute like `disabled` or a `data-*` attribute. **Solution**: The presence/absence of attributes must be consistent. Control this with state that is updated after hydration.

#### **Category: Next.js & Tooling**
- **Incorrect `next/dynamic` Usage**: Forgetting to set `ssr: false` for a client-only component. **Solution**: Always include `{ ssr: false }` when dynamically importing a component that cannot be server-rendered.
- **Dynamic `RootLayout` Modification**: Modifying `#html#` or `#body#` in `layout.tsx` based on client-side state. **Solution**: These tags must be static. Use a client-side provider within `#body#` for theme or class changes.
- **Using `useRouter` for Rendering**: The `router` object from `useRouter` is not fully populated on the server. Using `router.query` to render content will cause a mismatch. **Solution**: In App Router, use the `params` prop for initial data.

## Future Development Roadmap

### Phase 1: Core System Stabilization (Completed)
- ✅ Hydration error eradication
- ✅ Server-side architecture migration
- ✅ Multi-pass reconciliation engine
- ✅ AI flow integration

### Phase 2: Advanced Analytics & Intelligence (In Progress)
- Enhanced entity relationship mapping
- Advanced behavioral analysis algorithms
- Real-time risk scoring updates
- Predictive fraud detection models

### Phase 3: Enterprise Features & Scalability
- Multi-tenant architecture
- Advanced role-based access control
- Enterprise SSO integration
- Advanced reporting and compliance tools

### Phase 4: AI Enhancement & Automation
- Self-learning fraud detection models
- Automated compliance monitoring
- Advanced natural language processing
- Predictive analytics and trend analysis
