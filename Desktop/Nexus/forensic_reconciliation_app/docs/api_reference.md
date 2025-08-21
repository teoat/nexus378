# Forensic Reconciliation + Fraud Platform - API Reference

## 🔌 API Overview

This document provides comprehensive API reference for the forensic reconciliation platform, including GraphQL schemas, endpoints, and data structures for all major services.

## 🏗️ GraphQL Schema

### Root Schema
```graphql
schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}
```

## 📊 Query Endpoints

### 1. Reconciliation API

#### Get Reconciliation Results
```graphql
query GetReconciliationResults($filters: ReconciliationFilters) {
  reconciliationResults(filters: $filters) {
    id
    transactionId
    bankStatementId
    receiptId
    confidence
    matchType
    outlierScore
    auditTrail {
      timestamp
      action
      userId
      details
    }
    createdAt
    updatedAt
  }
}

# Input Types
input ReconciliationFilters {
  dateRange: DateRange
  confidenceThreshold: Float
  matchType: MatchType
  outlierScore: Float
  entityId: ID
}

enum MatchType {
  DETERMINISTIC
  FUZZY_AI
  MANUAL
  OUTLIER
}
```

#### Get Reconciliation Statistics
```graphql
query GetReconciliationStats($filters: ReconciliationFilters) {
  reconciliationStats(filters: $filters) {
    totalTransactions
    matchedCount
    unmatchedCount
    outlierCount
    averageConfidence
    processingTime
    lastUpdated
  }
}
```

### 2. Fraud Graph API

#### Get Entity Network
```graphql
query GetEntityNetwork($entityId: ID!, $depth: Int = 3) {
  entityNetwork(entityId: $entityId, depth: $depth) {
    entities {
      id
      name
      type
      riskScore
      fraudIndicators
      connections {
        targetId
        relationshipType
        strength
        riskScore
      }
    }
    patterns {
      id
      type
      riskLevel
      description
      entities
    }
  }
}

enum EntityType {
  VENDOR
  CUSTOMER
  EMPLOYEE
  SHELL_COMPANY
  FAMILY_MEMBER
}

enum RelationshipType {
  TRANSACTION
  OWNERSHIP
  FAMILY
  BUSINESS
  SUSPICIOUS
}
```

#### Get Fraud Patterns
```graphql
query GetFraudPatterns($filters: FraudPatternFilters) {
  fraudPatterns(filters: $filters) {
    id
    type
    riskLevel
    confidence
    description
    entities {
      id
      name
      type
      role
    }
    transactions {
      id
      amount
      date
      riskScore
    }
    createdAt
    updatedAt
  }
}

input FraudPatternFilters {
  riskLevel: RiskLevel
  patternType: PatternType
  dateRange: DateRange
  entityIds: [ID!]
}

enum RiskLevel {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum PatternType {
  CIRCULAR_TRANSACTION
  SHELL_COMPANY
  FAMILY_CONNECTION
  SUSPICIOUS_TIMING
  AMOUNT_ANOMALY
}
```

### 3. Risk Assessment API

#### Get Risk Scores
```graphql
query GetRiskScores($entityId: ID!, $includeFactors: Boolean = true) {
  riskScores(entityId: $entityId) {
    overallScore
    transactionRisk
    entityRisk
    patternRisk
    complianceRisk
    factors {
      name
      score
      weight
      description
      evidence
    }
    recommendations {
      action
      priority
      description
      impact
    }
    lastCalculated
  }
}

input RiskScoreFilters {
  entityIds: [ID!]
  riskThreshold: Float
  includeFactors: Boolean
  dateRange: DateRange
}
```

#### Get Compliance Violations
```graphql
query GetComplianceViolations($filters: ComplianceFilters) {
  complianceViolations(filters: $filters) {
    id
    type
    severity
    entityId
    description
    regulation
    violationDate
    status
    remediation
    auditTrail {
      timestamp
      action
      userId
      details
    }
  }
}

input ComplianceFilters {
  regulation: Regulation
  severity: Severity
  status: ViolationStatus
  dateRange: DateRange
  entityIds: [ID!]
}

enum Regulation {
  SOX
  PCI
  AML
  GDPR
  HIPAA
}

enum Severity {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum ViolationStatus {
  OPEN
  IN_PROGRESS
  RESOLVED
  ESCALATED
}
```

### 4. Evidence Management API

#### Get Evidence Files
```graphql
query GetEvidenceFiles($filters: EvidenceFilters) {
  evidenceFiles(filters: $filters) {
    id
    filename
    fileType
    hash
    size
    uploadedAt
    metadata {
      exif
      ocr
      nlp
      custom
    }
    integrity {
      hashVerified
      tamperDetected
      chainOfCustody
    }
    linkedEntities {
      entityId
      entityType
      relationship
    }
    linkedTransactions {
      transactionId
      relationship
    }
  }
}

input EvidenceFilters {
  fileType: FileType
  dateRange: DateRange
  entityIds: [ID!]
  transactionIds: [ID!]
  integrityStatus: IntegrityStatus
}

enum FileType {
  PDF
  IMAGE
  CHAT_LOG
  BANK_STATEMENT
  RECEIPT
  CONTRACT
  EMAIL
}

enum IntegrityStatus {
  VERIFIED
  TAMPERED
  PENDING
  FAILED
}
```

#### Get Evidence Chain of Custody
```graphql
query GetEvidenceChainOfCustody($evidenceId: ID!) {
  evidenceChainOfCustody(evidenceId: $evidenceId) {
    evidenceId
    chain {
      timestamp
      action
      userId
      userRole
      location
      hash
      details
    }
    currentStatus
    lastVerified
  }
}
```

### 5. Litigation Support API

#### Get Cases
```graphql
query GetCases($filters: CaseFilters) {
  cases(filters: $filters) {
    id
    title
    description
    status
    priority
    assignedTo
    createdAt
    updatedAt
    evidence {
      id
      filename
      type
      relevance
    }
    findings {
      id
      type
      description
      riskScore
      evidence
    }
    timeline {
      id
      event
      timestamp
      details
      evidence
    }
  }
}

input CaseFilters {
  status: CaseStatus
  priority: Priority
  assignedTo: ID
  dateRange: DateRange
  entityIds: [ID!]
}

enum CaseStatus {
  OPEN
  IN_PROGRESS
  REVIEW
  CLOSED
  ESCALATED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}
```

#### Get Case Timeline
```graphql
query GetCaseTimeline($caseId: ID!) {
  caseTimeline(caseId: $caseId) {
    caseId
    events {
      id
      timestamp
      eventType
      description
      evidence
      participants
      location
    }
    relationships {
      sourceEvent
      targetEvent
      relationshipType
      strength
    }
  }
}
```

## 🔄 Mutation Endpoints

### 1. Reconciliation Mutations

#### Update Reconciliation Match
```graphql
mutation UpdateReconciliationMatch($input: UpdateReconciliationInput!) {
  updateReconciliationMatch(input: $input) {
    success
    message
    reconciliation {
      id
      confidence
      matchType
      updatedAt
      auditTrail {
        timestamp
        action
        userId
        details
      }
    }
  }
}

input UpdateReconciliationInput {
  id: ID!
  confidence: Float
  matchType: MatchType
  notes: String
  userId: ID!
}
```

#### Flag Outlier
```graphql
mutation FlagOutlier($input: FlagOutlierInput!) {
  flagOutlier(input: $input) {
    success
    message
    outlier {
      id
      status
      flaggedBy
      flaggedAt
      reason
      auditTrail {
        timestamp
        action
        userId
        details
      }
    }
  }
}

input FlagOutlierInput {
  transactionId: ID!
  reason: String!
  riskLevel: RiskLevel
  userId: ID!
}
```

### 2. Evidence Mutations

#### Upload Evidence
```graphql
mutation UploadEvidence($input: UploadEvidenceInput!) {
  uploadEvidence(input: $input) {
    success
    message
    evidence {
      id
      filename
      hash
      uploadedAt
      integrity {
        hashVerified
        tamperDetected
      }
    }
  }
}

input UploadEvidenceInput {
  file: Upload!
  caseId: ID
  entityIds: [ID!]
  transactionIds: [ID!]
  metadata: JSON
  userId: ID!
}
```

#### Link Evidence
```graphql
mutation LinkEvidence($input: LinkEvidenceInput!) {
  linkEvidence(input: $input) {
    success
    message
    links {
      evidenceId
      entityId
      entityType
      relationship
      strength
    }
  }
}

input LinkEvidenceInput {
  evidenceId: ID!
  links: [EvidenceLinkInput!]!
  userId: ID!
}

input EvidenceLinkInput {
  entityId: ID
  entityType: EntityType
  transactionId: ID
  relationship: String
  strength: Float
}
```

### 3. Case Management Mutations

#### Create Case
```graphql
mutation CreateCase($input: CreateCaseInput!) {
  createCase(input: $input) {
    success
    message
    case {
      id
      title
      description
      status
      createdAt
      assignedTo
    }
  }
}

input CreateCaseInput {
  title: String!
  description: String!
  priority: Priority!
  assignedTo: ID!
  entityIds: [ID!]
  evidenceIds: [ID!]
  userId: ID!
}
```

#### Update Case Status
```graphql
mutation UpdateCaseStatus($input: UpdateCaseStatusInput!) {
  updateCaseStatus(input: $input) {
    success
    message
    case {
      id
      status
      updatedAt
      auditTrail {
        timestamp
        action
        userId
        details
      }
    }
  }
}

input UpdateCaseStatusInput {
  caseId: ID!
  status: CaseStatus!
  notes: String
  userId: ID!
}
```

## 📡 Subscription Endpoints

### 1. Real-Time Updates

#### Reconciliation Updates
```graphql
subscription ReconciliationUpdates($filters: ReconciliationFilters) {
  reconciliationUpdates(filters: $filters) {
    type
    reconciliation {
      id
      transactionId
      confidence
      matchType
      updatedAt
    }
    timestamp
  }
}
```

#### Fraud Pattern Alerts
```graphql
subscription FraudPatternAlerts($riskThreshold: Float = 0.7) {
  fraudPatternAlerts(riskThreshold: $riskThreshold) {
    type
    pattern {
      id
      type
      riskLevel
      description
      entities
    }
    timestamp
    priority
  }
}
```

#### Risk Score Changes
```graphql
subscription RiskScoreChanges($entityIds: [ID!]) {
  riskScoreChanges(entityIds: $entityIds) {
    type
    entityId
    oldScore
    newScore
    factors
    timestamp
  }
}
```

## 📊 Data Types

### Common Types
```graphql
type DateRange {
  start: DateTime!
  end: DateTime!
}

type AuditTrail {
  timestamp: DateTime!
  action: String!
  userId: ID!
  userRole: String!
  details: JSON
  ipAddress: String
  userAgent: String
}

type PaginationInfo {
  page: Int!
  pageSize: Int!
  totalCount: Int!
  totalPages: Int!
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
}

scalar DateTime
scalar JSON
scalar Upload
```

### Error Types
```graphql
type Error {
  code: String!
  message: String!
  details: JSON
  timestamp: DateTime!
}

type ValidationError {
  field: String!
  message: String!
  code: String!
}
```

## 🔐 Authentication & Authorization

### Headers
```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
X-Request-ID: <request_id>
```

### Role-Based Access
```graphql
enum UserRole {
  INVESTIGATOR
  EXECUTIVE
  ADMIN
  AUDITOR
}

type User {
  id: ID!
  username: String!
  email: String!
  role: UserRole!
  permissions: [Permission!]!
  lastLogin: DateTime
}
```

## 📈 Performance & Pagination

### Pagination
```graphql
type PaginatedResponse<T> {
  data: [T!]!
  pagination: PaginationInfo!
  totalCount: Int!
}

# Example usage
query GetReconciliationResultsPaginated(
  $page: Int = 1
  $pageSize: Int = 50
  $filters: ReconciliationFilters
) {
  reconciliationResultsPaginated(
    page: $page
    pageSize: $pageSize
    filters: $filters
  ) {
    data {
      id
      transactionId
      confidence
      matchType
    }
    pagination {
      page
      pageSize
      totalCount
      totalPages
      hasNextPage
      hasPreviousPage
    }
  }
}
```

## 🧪 Testing & Development

### GraphQL Playground
- **URL**: `/graphql`
- **Features**: Interactive API explorer, query testing, schema documentation
- **Authentication**: JWT token support

### API Versioning
- **Current Version**: v1
- **Deprecation Policy**: 6 months notice for breaking changes
- **Backward Compatibility**: Maintained within major versions

### Rate Limiting
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 📚 SDKs & Libraries

### Official SDKs
- **JavaScript/TypeScript**: `@forensic-reconciliation/sdk`
- **Python**: `forensic-reconciliation-python`
- **Java**: `forensic-reconciliation-java`

### Community Libraries
- **Rust**: `forensic-reconciliation-rs`
- **Go**: `forensic-reconciliation-go`
- **C#**: `ForensicReconciliation.NET`

---

*This API reference provides comprehensive documentation for integrating with the forensic reconciliation platform's GraphQL API.*
