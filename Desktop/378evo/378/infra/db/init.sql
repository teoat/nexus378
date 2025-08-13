-- =================================================================
-- Users and Access Control
-- =================================================================

CREATE TABLE "users" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "email" VARCHAR(255) UNIQUE NOT NULL,
  "hashed_password" TEXT NOT NULL,
  "full_name" VARCHAR(255),
  "roles" TEXT NOT NULL DEFAULT 'investigator', -- Comma-separated roles, e.g., 'investigator,admin'
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- Core Forensic Case Management
-- =================================================================

CREATE TABLE "cases" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "case_name" VARCHAR(255) NOT NULL,
  "description" TEXT,
  "status" VARCHAR(50) NOT NULL DEFAULT 'new', -- e.g., new, active, closed, archived
  "lead_investigator_id" UUID REFERENCES "users"("id"),
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- Data Ingestion and Processing
-- =================================================================

CREATE TABLE "transactions" (
  "id" BIGSERIAL PRIMARY KEY,
  "case_id" UUID NOT NULL REFERENCES "cases"("id") ON DELETE CASCADE,
  "transaction_date" TIMESTAMPTZ,
  "description" TEXT,
  "amount" NUMERIC(19, 4),
  "currency" VARCHAR(10),
  "custom_fields" JSONB, -- For user-mapped columns
  "raw_data" JSONB, -- The original, unprocessed row data
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "column_mappings" (
  "id" SERIAL PRIMARY KEY,
  "case_id" UUID NOT NULL REFERENCES "cases"("id") ON DELETE CASCADE,
  "source_column_name" VARCHAR(255) NOT NULL,
  "target_field_name" VARCHAR(255) NOT NULL, -- e.g., 'transaction_date', 'custom_fields.vendor'
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE("case_id", "source_column_name")
);

CREATE TABLE "discrepancies" (
  "id" SERIAL PRIMARY KEY,
  "case_id" UUID NOT NULL REFERENCES "cases"("id") ON DELETE CASCADE,
  "type" VARCHAR(100) NOT NULL, -- e.g., 'missing_statement', 'balance_mismatch'
  "description" TEXT NOT NULL,
  "status" VARCHAR(50) NOT NULL DEFAULT 'open', -- e.g., open, resolved, ignored
  "data_details" JSONB, -- e.g., { "missing_start_date": "...", "missing_end_date": "..." }
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "evidence" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "case_id" UUID NOT NULL REFERENCES "cases"("id") ON DELETE CASCADE,
  "transaction_id" BIGINT REFERENCES "transactions"("id"),
  "file_name" VARCHAR(255) NOT NULL,
  "file_storage_key" TEXT NOT NULL, -- e.g., S3 object key
  "description" TEXT,
  "uploaded_by_id" UUID REFERENCES "users"("id"),
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- Analysis Results
-- =================================================================

CREATE TABLE "matching_results" (
  "id" BIGSERIAL PRIMARY KEY,
  "case_id" UUID NOT NULL REFERENCES "cases"("id") ON DELETE CASCADE,
  "transaction_a_id" BIGINT NOT NULL REFERENCES "transactions"("id"),
  "transaction_b_id" BIGINT NOT NULL REFERENCES "transactions"("id"),
  "match_score" FLOAT NOT NULL,
  "matching_strategy" VARCHAR(100),
  "is_confirmed" BOOLEAN DEFAULT NULL, -- Null = pending, True = confirmed, False = rejected
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "fraud_alerts" (
  "id" BIGSERIAL PRIMARY KEY,
  "case_id" UUID NOT NULL REFERENCES "cases"("id") ON DELETE CASCADE,
  "transaction_id" BIGINT REFERENCES "transactions"("id"),
  "rule_id" VARCHAR(100) NOT NULL, -- e.g., 'round_number_payment'
  "description" TEXT NOT NULL,
  "severity" VARCHAR(50) NOT NULL, -- e.g., low, medium, high, critical
  "status" VARCHAR(50) NOT NULL DEFAULT 'new', -- e.g., new, under_review, dismissed
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- System Auditing
-- =================================================================

CREATE TABLE "audit_log" (
  "id" BIGSERIAL PRIMARY KEY,
  "user_id" UUID REFERENCES "users"("id"),
  "action" VARCHAR(255) NOT NULL, -- e.g., 'create_case', 'login_failure'
  "details" JSONB,
  "ip_address" VARCHAR(100),
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- Indexes for Performance
-- =================================================================

CREATE INDEX idx_transactions_case_id ON "transactions"("case_id");
CREATE INDEX idx_transactions_date ON "transactions"("transaction_date");
CREATE INDEX idx_cases_status ON "cases"("status");
CREATE INDEX idx_fraud_alerts_case_id ON "fraud_alerts"("case_id");
CREATE INDEX idx_audit_log_user_id ON "audit_log"("user_id");
CREATE INDEX idx_audit_log_action ON "audit_log"("action");