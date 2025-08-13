# IntelliAudit AI: Comprehensive System Overview

## What is IntelliAudit AI?

IntelliAudit AI is a forensic intelligence platform designed to help auditors, analysts, and financial professionals detect fraud, ensure compliance, and build litigation-ready cases. It leverages a multi-layered AI engine to go beyond simple anomaly detection, uncovering complex patterns, behavioral anomalies, and hidden relationships within your financial data.

## Core Features

- **Data Upload**: Allows the user to upload data files, including expense ledgers and bank statements, supporting CSV and JSON formats.
- **JSON Parsing**: Tool to extract and parse JSON objects from AI responses to ensure structured data integration.
- **Benford's Law Analysis**: Run Benford's Law analysis to check frequency of leading digits of the debit transactions to check for anomalies.
- **Manual Analysis Module**: Provides an analyst workbench replicating the functionality of the Streamlit prototype, supporting human-driven analysis for complex scenarios.
- **Interactive Audit Display**: Presents detected anomalies clearly, including score of the risk and unusual flagged activities. It is presented as interactive, read-only.
- **IntelliLedger AI Agent**: Tool leveraging the Gemini API to let controller ask natural language questions, such as 'Show me the contract for this invoice.'

## Key Capabilities

- **AI-Powered Forensic Analysis**: Automatically scans your data for over 60 types of risk factors, including sophisticated fraud schemes and familial conflicts of interest.
- **Explainable AI (XAI)**: Provides a detailed, transparent breakdown of the risk factors that contribute to an anomaly's score, so you can understand the "why" behind every finding.
- **Entity & Network Analysis**: Maps and scores the relationships between vendors and employees to uncover shell companies, conflicts of interest, and other network-based risks.
- **Legal Intelligence Layer**: Synthesizes forensic findings into actionable legal insights, complete with risk narratives and case-strength scores.
- **Conversational AI Agent**: Investigate your data using natural language. Ask questions like "Show me all vendors with a high risk score" to get instant answers.

## Who is this for?

IntelliAudit is built for:
- **Internal Auditors**: Who need to quickly identify control failures and potential fraud.
- **Forensic Accountants**: Who require deep, evidence-based analysis for legal cases.
- **Compliance Officers**: Who need to monitor for AML, PEP, and other regulatory violations.
- **Executives**: Who need a high-level, real-time view of financial risk across the organization.

## Style Guidelines

- **Primary color**: Dark slate blue (#483D8B) to convey a sense of sophistication, trust, and expertise, without being too cliché about "finance colors."
- **Background color**: A very dark grayish blue (#24232D). Dark mode enhances the modern, tech-forward impression.
- **Accent color**: Lavender (#E6E6FA). Lavender complements the primary color, providing a gentle contrast without being jarring. This color can highlight interactive elements or important data points.
- **Headline font**: 'Space Grotesk' sans-serif, for a techy, scientific feel
- **Body font**: 'Inter' sans-serif, for a modern, machined, objective, neutral look
- Use a consistent set of minimalist icons to represent different financial concepts and data types, aiding quick comprehension. Icons should follow the lavender accent color.
- Emphasize a clean, well-structured layout with clear divisions between sections. Use whitespace generously to prevent information overload. Implement a responsive design to ensure usability across devices.

## System Architecture

This document provides a high-level overview of the IntelliAudit AI system architecture, which is designed to be scalable, secure, and maintainable. The architecture is based on a modern, server-centric approach that leverages the power of serverless functions and a robust task-based system for handling long-running analysis processes.

### Core Principles

- **Server-Centric Logic**: All core business logic, including data processing, analysis, and AI-powered insights, is handled on the server side. This ensures data integrity, security, and scalability.
- **Asynchronous Operations**: Long-running tasks, such as file ingestion and forensic analysis, are handled asynchronously using a task-based architecture. This prevents blocking the main thread and ensures a responsive user experience.
- **Scalability**: The architecture is designed to be highly scalable, leveraging serverless functions and a distributed task system to handle a large number of concurrent users and analysis jobs.
- **Security**: The application is built with a security-first mindset.
  - **Encryption in Transit**: All data transmitted between the client and server is encrypted using industry-standard TLS (HTTPS).
  - **Encryption at Rest**: All data stored in Firebase services (Firestore, Storage) is automatically encrypted at rest by Google Cloud.
  - **Authentication**: User authentication is managed by Firebase Authentication, which provides secure password handling and supports multi-factor authentication.
  - **Authorization**: Role-Based Access Control (RBAC) is implemented via custom claims and Firestore security rules to ensure users can only access the data and features they are permitted to.

### System Components

#### 1. Frontend

- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **UI Components**: Radix UI

The frontend is a modern, responsive web application that provides a rich and intuitive user experience. It is responsible for rendering the UI, handling user interactions, and communicating with the backend via a set of well-defined server actions.

#### 2. Backend

- **Runtime**: Node.js
- **Framework**: Next.js (Server Actions)
- **Database**: Firestore
- **Authentication**: Firebase Authentication

The backend is built on a serverless architecture, using Next.js Server Actions to handle all API requests. This allows for a high degree of scalability and eliminates the need to manage and maintain a dedicated server.

#### 3. AI & Analysis

- **AI Flows**: Genkit
- **Task Management**: Cloud Tasks

All AI and analysis logic is encapsulated in a set of server-side AI flows, which are built using the Genkit framework. These flows are responsible for everything from file ingestion and data parsing to transaction matching and anomaly detection.

Long-running analysis jobs are managed using a task-based architecture, which leverages Google Cloud Tasks to enqueue and process jobs asynchronously. This ensures that the application remains responsive, even when handling large and complex analysis tasks.

### Data Flow

1. **File Ingestion**: The user uploads a file via the frontend. The file is then passed to the `ingestFileFlow`, which is a server-side AI flow that parses the file, extracts the relevant data, and returns it to the client.
2. **Analysis Request**: The user initiates an analysis request from the frontend. This triggers the `runAnalysisFlow`, which is a server-side AI flow that orchestrates the entire analysis workflow.
3. **Task Enqueueing**: The `runAnalysisFlow` enqueues a new analysis job in Google Cloud Tasks.
4. **Asynchronous Processing**: A dedicated server-side worker picks up the job from the queue and executes the analysis logic, which includes the `initialMatchingFlow` and the `fullForensicAnalysisFlow`.
5. **Results Storage**: The results of the analysis are stored in the Firestore database.
6. **Real-time Updates**: The frontend listens for real-time updates from the database and updates the UI as the analysis progresses.

This architecture ensures a clear separation of concerns between the frontend and the backend, and it provides a robust and scalable foundation for building a powerful and intelligent auditing application.

