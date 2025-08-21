SPEC-1-ForensicApp

Background

This application is a comprehensive, AI-powered Forensic Analysis Platform engineered to streamline, enhance, and partially automate the complex process of financial investigation. It brings together a modern, interactive frontend UI; a secure and modular backend-for-frontend (BFF) Node.js gateway; and a powerful Python-based AI service. Together, these components create a holistic ecosystem capable of supporting fraud detection, discrepancy resolution, multi-party case management, and automated analysis reporting.

The platform is designed to be extensible and future-proof. It integrates cutting-edge AI technologies like LangGraph and LangChain for agentic reasoning, a vector search-enabled help system, and infrastructure-level resilience through event queues and real-time streams. The platform not only accelerates investigations but also improves accuracy and consistency across large teams and datasets.

Requirements

Must Have:

M: React + Next.js frontend with SSR, data visualization, drag-drop upload, and contextual workflows.

M: Node.js (NestJS) API Gateway providing REST and GraphQL endpoints, session management, and secure access to backend services.

M: FastAPI-based Python AI microservice running LangGraph agents to analyze financial data and detect anomalies.

M: Database layer combining PostgreSQL (structured), Neo4j (relational/graph), and Redis (caching/session).

M: Communication layer using gRPC for synchronous tasks and RabbitMQ for asynchronous task distribution.

M: Persistent WebSocket connections from client to gateway for live updates and notifications.

M: Testing framework that enforces determinism, runs in CI/CD, and targets #95% test coverage at all layers.

Should Have:

S: Visualization components including table virtualization, graph-based entity maps, and live KPI widgets.

S: File ingestion module with secure presigned S3 uploads, schema detection, and configurable mapping tools.

S: Column-mapping interface for reconciling user-uploaded financial datasets with internal schema.

S: Fraud detection module powered by custom rules, ML scoring, and explainability layers.

S: Error-handling framework with component-level error boundaries and structured API failure feedback.

Could Have:

C: Visual regression testing suite that integrates Storybook and Chromatic.

C: Multi-language support through i18n-ready architecture (e.g., react-i18next).

C: Gateway-level caching using Redis to minimize DB and compute usage on repeated frontend requests.

Won't Have (initially):

W: Native iOS or Android mobile app.

W: Direct frontend access to any persistence or AI layer — all communication is brokered via the Gateway.

Method

We are building the system as a set of interoperable, containerized services using a modular microservices strategy. Each service is clearly bounded, type-safe, and testable in isolation.

Architecture Diagram (PlantUML)

@startuml
actor User
package "Frontend (Next.js)" {
  [UI Components]
  [WebSocket Client]
  [React Pages]
  [Interactive Visuals]
}

package "Node.js Gateway (NestJS)" {
  [REST/GraphQL APIs]
  [WebSocket Server]
  [Auth Module]
  [Case Module]
  [Mapping Module]
  [Discrepancy Module]
  [Dashboard Module]
  [Python Client (gRPC)]
}

package "Python AI Service (FastAPI)" {
  [LangGraph Agents]
  [Data Ingestion Engine]
  [Fraud Detection Engine]
  [Discrepancy Detection]
  [HelpAgent]
  [MetaDesignAgent]
}

package "Data Stores" {
  database PostgreSQL
  database Neo4j
  database Redis
}

package "Infra" {
  [RabbitMQ]
  [S3]
  [CI/CD Pipeline]
}

User --# [UI Components]
[WebSocket Client] --# [WebSocket Server]
[React Pages] --# [REST/GraphQL APIs]
[REST/GraphQL APIs] --# [Auth Module]
[REST/GraphQL APIs] --# [Case Module]
[REST/GraphQL APIs] --# [Mapping Module]
[REST/GraphQL APIs] --# [Dashboard Module]
[Python Client (gRPC)] --# [LangGraph Agents]
[Case Module] --# PostgreSQL
[LangGraph Agents] --# PostgreSQL
[LangGraph Agents] --# Neo4j
[LangGraph Agents] --# Redis
[LangGraph Agents] --# RabbitMQ
[REST/GraphQL APIs] --# Redis
[Data Ingestion Engine] --# S3
@enduml

Database Design (PostgreSQL - Expanded Schema)

CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  last_login TIMESTAMPTZ
);

CREATE TABLE cases (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  lead_investigator_id UUID REFERENCES users(id),
  status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
  id UUID PRIMARY KEY,
  case_id UUID REFERENCES cases(id),
  raw_data JSONB NOT NULL,
  parsed_fields JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE column_mappings (
  id UUID PRIMARY KEY,
  case_id UUID REFERENCES cases(id),
  source_column_name TEXT,
  target_field_name TEXT,
  confidence_score FLOAT
);

CREATE TABLE discrepancies (
  id UUID PRIMARY KEY,
  case_id UUID REFERENCES cases(id),
  type TEXT,
  status TEXT,
  description TEXT,
  resolution_notes TEXT,
  data_details JSONB
);

CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action TEXT,
  context JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

Implementation

Frontend (Next.js + React)

Create atomic component library using Tailwind, ShadCN, and Storybook.

Develop core workflows: case lifecycle, ingestion UI, entity graphs, and discrepancy editor.

Integrate real-time help overlays, chat window, and proactive UI suggestions.

Node.js Gateway (NestJS)

Implement structured modules with gRPC and REST interfaces.

Introduce RBAC-based auth guards.

Implement WebSocket modules for job progress, alerts, dashboard metrics.

Connect PostgreSQL, Redis, RabbitMQ, and Neo4j clients.

Python AI Service (FastAPI)

Implement agent workflows: ingestion, validation, matching, discrepancy resolution.

Define toolsets: apply_column_mappings, generate_provisional_report, validate_entity_linkage.

Setup job consumers using ARQ or Celery, integrated with RabbitMQ.

Data Platform

PostgreSQL schema migration using Alembic.

Prisma integration from Node Gateway.

Neo4j population via async worker.

DevOps & Tooling

Docker Compose dev cluster.

GitHub Actions + Testcontainers for CI.

Secrets and environment config via Vault or Doppler.

Milestones

M1: Setup monorepo, Lerna or Nx for frontend/backend coordination

M2: Component library & API baseline

M3: Column mapping and ingestion pipeline (end-to-end flow)

M4: Reconciliation interface and Neo4j graph ingestion

M5: Live dashboard with WebSocket metrics and alerts

M6: Full AI ingestion-analysis-reporting loop

M7: HelpAgent, MetaDesignAgent integration

M8: CI pipeline + QA suite + Load tests + Deployment guides

Gathering Results

Use GitHub Actions test matrix to monitor CI outcomes and log coverage gaps.

Integrate Cypress dashboard for cross-browser test insights.

Generate user activity reports per case to monitor adoption.

Track AI outputs vs. investigator feedback to train scoring models.

Use Grafana + Prometheus for infra health and long-term reliability.

Need Professional Help in Developing Your Architecture?

Please contact me at sammuti.com :)

