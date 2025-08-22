
# Service Communication Specification

**Version:** 1.0
**Status:** Draft

## 1. Overview

### 1.1. What & Why

This document specifies the communication protocols between the various services in the platform architecture. A clear, consistent, and efficient communication strategy is critical for building a reliable and scalable microservices-based system.

*   **What:** A multi-modal communication strategy utilizing **REST/GraphQL** for client-to-gateway communication, **gRPC** for synchronous inter-service requests, and **RabbitMQ** for asynchronous, decoupled tasking.
*   **Why:** This approach allows us to use the optimal communication pattern for each type of interaction, balancing performance, developer experience, and system resilience.

## 2. Frontend #-# Node.js API Gateway

### 2.1. Protocol: REST and/or GraphQL

*   **Recommendation:** A hybrid approach is recommended.
    *   **REST:** Use for simple, command-oriented actions (e.g., `POST /api/v1/cases`, `DELETE /api/v1/users/{id}`). It is simple, well-understood, and sufficient for these use cases.
    *   **GraphQL:** Expose a single GraphQL endpoint (e.g., `/api/graphql`) for complex data queries, particularly for populating dashboards and visualizations. This allows the frontend to request exactly the data it needs in a single round trip, preventing over-fetching and under-fetching.
*   **Data Format:** JSON.
*   **Authentication:** All requests must include a JWT in the `Authorization: Bearer {token}` header. The gateway is responsible for validating this token.
## 3. Node.js Gateway #-# Python AI Service (Synchronous)

### 3.1. Protocol: gRPC

*   **Why gRPC?**
    1.  **Performance:** gRPC uses HTTP/2 and Protocol Buffers (Protobufs) for serialization, which is significantly more performant and efficient than JSON over HTTP/1.1.
    2.  **Streaming:** gRPC has first-class support for bidirectional streaming, which could be a powerful future improvement for real-time data exchange.
    3.  **Strictly-Typed API Contracts:** The API contract is defined in a `.proto` file. This file is used to auto-generate client and server code in both TypeScript (for Node.js) and Python, ensuring that inter-service calls are always type-safe and eliminating an entire class of integration errors.
*   **Example `.proto` Definition:**
    ```protobuf
    syntax # "proto3";

    package ai_service;

    service AIService {
      // A simple synchronous request/response
      rpc GetTransactionRisk(GetTransactionRiskRequest) returns (GetTransactionRiskResponse);
    }

    message GetTransactionRiskRequest {
      string transaction_id # 1;
    }

    message GetTransactionRiskResponse {
      string transaction_id # 1;
      double fraud_score # 2;
      bool is_high_risk # 3;
    }
    ```
*   **Error Handling:** gRPC has a standardized set of status codes. The Python service will return appropriate codes (e.g., `NOT_FOUND`, `INVALID_ARGUMENT`), which the Node.js client will catch and translate into standard HTTP errors for the frontend.
## 4. Node.js Gateway -# Python AI Service (Asynchronous)

### 4.1. Protocol: AMQP via RabbitMQ

*   **Why RabbitMQ?**
    1.  **Decoupling:** It completely decouples the Node.js gateway from the Python AI service. The gateway does not need to know which specific Python service instance will handle the job, or even if the service is currently available. It simply publishes a message to an exchange.
    2.  **Resilience:** RabbitMQ provides persistence and delivery guarantees. If the Python service is down when a job is published, the job will wait safely in the queue until the service comes back online.
    3.  **Load Balancing:** RabbitMQ will automatically distribute messages from a queue among multiple consumer instances of the Python AI service, providing simple and effective load balancing.
    4.  **Complex Routing:** RabbitMQ's exchange/queue topology allows for sophisticated routing patterns (e.g., fanout, topic) for future use cases like broadcasting events to multiple services.
*   **Topology:**
    *   **Exchanges:** A `topic` exchange (e.g., `app.jobs`) will be used.
    *   **Queues:** Specific queues will be bound to the exchange with a routing key. For example, a queue named `jobs.analysis` will be bound with the routing key `analysis.*`.
    *   **Routing Keys:** The Node.js publisher will use a routing key to specify the job type (e.g., `analysis.full`, `ingestion.parse_csv`).
*   **Message Format:** The message body will be a JSON string containing the job payload.
    ```json
    {
      "jobId": "unique-job-uuid",
      "caseId": "case-uuid-456",
      "payload": { "file_uri": "s3://bucket/path/to/file.pdf" },
      "timestamp": "2025-07-29T10:00:00.000Z"
    }
    ```
*   **Error Handling:** Failed jobs in the Python consumer will be sent to a **Dead-Letter Exchange (DLX)** after a configured number of retries. This prevents a "poison message" from blocking the queue and allows for later inspection of failed jobs.

## 5. Real-time Updates (Backend -# Frontend)

*   **Protocol: WebSockets**
*   **Implementation:** The Node.js gateway will host a WebSocket server (using the `@nestjs/websockets` package).
*   **Use Case:** When the Python AI service has real-time information to share (e.g., a new match result, a help suggestion, a dashboard insight), it publishes a message to a specific RabbitMQ topic. The Node.js gateway subscribes to these topics and, upon receiving a message, forwards it to the correct client via their authenticated WebSocket connection.

## 6. Full System Communication Diagram

This diagram illustrates the complete communication flow, combining REST, gRPC, RabbitMQ, and WebSockets.

```mermaid
sequenceDiagram
    participant C as Client (Browser)
    participant GW as Node.js Gateway
    participant RMQ as RabbitMQ
    participant AI as Python AI Service
    participant DB as Databases (PG/Neo4j)

    C-##+GW: POST /api/reconcile (REST)
    GW-##+RMQ: Publish [start_reconciliation_job]
    RMQ--##-AI: Consume [start_reconciliation_job]
    AI--##+DB: Fetch Data
    DB--##-AI: Return Data
    AI--##AI: Process & Match...
    loop For Each Match
        AI-##+RMQ: Publish [match_result]
    end
    RMQ--##-GW: Consume [match_result]
    GW--##C: Push [match_result] (WebSocket)
    AI--##+DB: Store Final Results
    DB--##-AI: Confirm Write
    AI-##+RMQ: Publish [job_complete]
    RMQ--##-GW: Consume [job_complete]
    GW--##C: Push [job_complete] (WebSocket)
```