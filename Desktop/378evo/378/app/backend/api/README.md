# Node.js API Gateway / BFF

## 1. Overview

This directory contains the source code for the **Node.js API Gateway**, which also serves as a **Backend-for-Frontend (BFF)**. It is built with [NestJS](https://nestjs.com/), a progressive Node.js framework for building efficient, reliable, and scalable server-side applications.

### Key Responsibilities:

*   **Single Entry Point:** Acts as the sole, authoritative entry point for all client applications.
*   **Authentication & Authorization:** Manages user authentication, JWT validation, and Role-Based Access Control (RBAC).
*   **API Orchestration:** Aggregates data from various downstream services (e.g., Python AI Service, PostgreSQL) and shapes it into optimized payloads for the frontend.
*   **Real-time Communication:** Hosts a WebSocket server to push real-time updates to clients.

For a more detailed architectural overview, please see the [Node.js API Gateway Specification](../../architectural_deep_dive/02_NODE_GATEWAY_SPEC.md).

## 2. Project Setup

To get started with the API gateway, you first need to install its dependencies. From the root of the monorepo, run:

```bash
# This will install dependencies for all packages, including the API
npm install
```

## 3. Running the Application

The application can be run in several modes. All commands should be run from the root of the monorepo.

```bash
# Development mode with hot-reloading
npm run start:dev:api

# Production mode
npm run start:prod:api
```

## 4. Running Tests

The API gateway has a comprehensive test suite.

```bash
# Run all unit and integration tests
npm run test:api

# Run tests with coverage report
npm run test:cov:api

# Run end-to-end tests
npm run test:e2e:api
```

## 5. Key Modules

The gateway is organized into the following key NestJS modules:

*   `AuthModule`: Handles authentication and authorization.
*   `UserModule`: Manages user data.
*   `CaseModule`: Manages forensic cases.
*   `DataIngestionModule`: Handles file uploads and ingestion requests.
*   `ReconciliationModule`: Orchestrates the data reconciliation process.
*   `WebSocketModule`: Manages real-time client communication.
*   `PythonAiClientModule`: Manages communication with the downstream Python AI service.

## 6. License

This project is proprietary.
