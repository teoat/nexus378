-- DuckDB schema for the Forensic Reconciliation App
-- This schema is designed for high-performance OLAP queries on financial data.

-- Create a table for bank statements
CREATE TABLE IF NOT EXISTS bank_statements (
    id VARCHAR PRIMARY KEY,
    account_id VARCHAR,
    statement_date DATE,
    start_balance DECIMAL(18, 2),
    end_balance DECIMAL(18, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create a table for transactions
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR PRIMARY KEY,
    statement_id VARCHAR,
    transaction_date TIMESTAMP,
    description VARCHAR,
    amount DECIMAL(18, 2),
    type VARCHAR, -- e.g., 'debit', 'credit'
    category VARCHAR,
    is_suspicious BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (statement_id) REFERENCES bank_statements(id)
);

-- Create a table for receipts
CREATE TABLE IF NOT EXISTS receipts (
    id VARCHAR PRIMARY KEY,
    transaction_id VARCHAR,
    receipt_date DATE,
    vendor VARCHAR,
    total_amount DECIMAL(18, 2),
    file_path VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- Create materialized views for performance
-- Note: DuckDB does not have native materialized views like PostgreSQL.
-- Instead, we can create tables that are periodically refreshed.

-- Example: A view for reconciled transactions
CREATE TABLE IF NOT EXISTS reconciled_transactions AS
SELECT
    t.id as transaction_id,
    r.id as receipt_id,
    t.transaction_date,
    t.description,
    t.amount,
    r.vendor,
    r.total_amount as receipt_amount
FROM transactions t
JOIN receipts r ON t.id = r.transaction_id
WHERE t.amount = r.total_amount;

-- Example: A view for suspicious transactions
CREATE TABLE IF NOT EXISTS suspicious_transactions_view AS
SELECT *
FROM transactions
WHERE is_suspicious = TRUE;
