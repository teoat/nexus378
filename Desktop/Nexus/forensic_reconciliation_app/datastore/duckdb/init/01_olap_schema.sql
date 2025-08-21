-- DuckDB OLAP Engine Schema for Forensic Reconciliation Platform
-- Optimized for high-performance analytical processing

-- Create database and schemas
CREATE SCHEMA IF NOT EXISTS olap;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dimensions;
CREATE SCHEMA IF NOT EXISTS facts;

-- Enable performance optimizations
SET enable_progress_bar=true;
SET enable_external_access=true;
SET memory_limit='4GB';
SET threads=4;

-- Dimension Tables for OLAP Analysis

-- Entity dimension table
CREATE TABLE IF NOT EXISTS dimensions.entities (
    entity_id VARCHAR PRIMARY KEY,
    entity_name VARCHAR NOT NULL,
    entity_type VARCHAR NOT NULL, -- 'individual', 'company', 'organization'
    registration_number VARCHAR,
    tax_id VARCHAR,
    country_code VARCHAR(3),
    jurisdiction VARCHAR,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Account dimension table
CREATE TABLE IF NOT EXISTS dimensions.accounts (
    account_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    account_number VARCHAR NOT NULL,
    account_type VARCHAR NOT NULL, -- 'bank', 'credit_card', 'investment', 'crypto'
    institution_name VARCHAR,
    currency_code VARCHAR(3) DEFAULT 'USD',
    country_code VARCHAR(3),
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    FOREIGN KEY (entity_id) REFERENCES dimensions.entities(entity_id)
);

-- Transaction dimension table
CREATE TABLE IF NOT EXISTS dimensions.transactions (
    transaction_id VARCHAR PRIMARY KEY,
    source_system VARCHAR NOT NULL, -- 'bank', 'credit_card', 'pos', 'crypto'
    transaction_type VARCHAR NOT NULL, -- 'debit', 'credit', 'transfer', 'exchange'
    category VARCHAR,
    subcategory VARCHAR,
    merchant_name VARCHAR,
    merchant_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time dimension table for efficient date-based queries
CREATE TABLE IF NOT EXISTS dimensions.time_dimension (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL,
    is_year_end BOOLEAN NOT NULL
);

-- Populate time dimension for the next 5 years
INSERT OR IGNORE INTO dimensions.time_dimension
SELECT 
    date_series.date_value as date_key,
    EXTRACT(YEAR FROM date_series.date_value) as year,
    EXTRACT(QUARTER FROM date_series.date_value) as quarter,
    EXTRACT(MONTH FROM date_series.date_value) as month,
    TO_CHAR(date_series.date_value, 'Month') as month_name,
    EXTRACT(WEEK FROM date_series.date_value) as week,
    EXTRACT(DOW FROM date_series.date_value) as day_of_week,
    TO_CHAR(date_series.date_value, 'Day') as day_name,
    EXTRACT(DOW FROM date_series.date_value) IN (0, 6) as is_weekend,
    EXTRACT(DAY FROM date_series.date_value) = EXTRACT(DAY FROM LAST_DAY(date_series.date_value)) as is_month_end,
    EXTRACT(DAY FROM date_series.date_value) = EXTRACT(DAY FROM LAST_DAY(date_series.date_value)) AND EXTRACT(MONTH FROM date_series.date_value) IN (3, 6, 9, 12) as is_quarter_end,
    EXTRACT(DAY FROM date_series.date_value) = EXTRACT(DAY FROM LAST_DAY(date_series.date_value)) AND EXTRACT(MONTH FROM date_series.date_value) = 12 as is_year_end
FROM (
    SELECT DATE '2024-01-01' + INTERVAL (seq) DAY as date_value
    FROM range(0, 1825) -- 5 years
) date_series;

-- Fact Tables for Transaction Analysis

-- Main transaction fact table
CREATE TABLE IF NOT EXISTS facts.transactions (
    transaction_id VARCHAR PRIMARY KEY,
    date_key DATE NOT NULL,
    entity_id VARCHAR NOT NULL,
    account_id VARCHAR NOT NULL,
    transaction_dim_id VARCHAR NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(10,6) DEFAULT 1.0,
    usd_amount DECIMAL(15,2) GENERATED ALWAYS AS (amount * exchange_rate) STORED,
    balance_after DECIMAL(15,2),
    description TEXT,
    reference_number VARCHAR,
    source_file VARCHAR,
    confidence_score DECIMAL(5,2) DEFAULT 1.0,
    is_reconciled BOOLEAN DEFAULT false,
    reconciliation_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dimensions.time_dimension(date_key),
    FOREIGN KEY (entity_id) REFERENCES dimensions.entities(entity_id),
    FOREIGN KEY (account_id) REFERENCES dimensions.accounts(account_id),
    FOREIGN KEY (transaction_dim_id) REFERENCES dimensions.transactions(transaction_id)
);

-- Reconciliation matches fact table
CREATE TABLE IF NOT EXISTS facts.reconciliation_matches (
    match_id VARCHAR PRIMARY KEY,
    transaction_id_1 VARCHAR NOT NULL,
    transaction_id_2 VARCHAR NOT NULL,
    match_type VARCHAR NOT NULL, -- 'exact', 'fuzzy', 'manual'
    confidence_score DECIMAL(5,2) NOT NULL,
    match_criteria JSON, -- Store matching criteria used
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    matched_by VARCHAR, -- User or system that made the match
    FOREIGN KEY (transaction_id_1) REFERENCES facts.transactions(transaction_id),
    FOREIGN KEY (transaction_id_2) REFERENCES facts.transactions(transaction_id)
);

-- Risk assessment fact table
CREATE TABLE IF NOT EXISTS facts.risk_assessments (
    assessment_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    date_key DATE NOT NULL,
    risk_type VARCHAR NOT NULL, -- 'transaction', 'behavioral', 'network', 'compliance'
    risk_score DECIMAL(5,2) NOT NULL,
    risk_factors JSON, -- Store risk factors and weights
    assessment_method VARCHAR NOT NULL, -- 'rule_based', 'ml_model', 'hybrid'
    confidence_level DECIMAL(5,2) NOT NULL,
    assessed_by VARCHAR NOT NULL,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES dimensions.entities(entity_id),
    FOREIGN KEY (date_key) REFERENCES dimensions.time_dimension(date_key)
);

-- Staging Tables for Data Ingestion

-- Raw transaction staging table
CREATE TABLE IF NOT EXISTS staging.raw_transactions (
    id INTEGER PRIMARY KEY,
    source_system VARCHAR NOT NULL,
    raw_data JSON NOT NULL, -- Store complete raw data
    processed BOOLEAN DEFAULT false,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data quality staging table
CREATE TABLE IF NOT EXISTS staging.data_quality_checks (
    check_id VARCHAR PRIMARY KEY,
    table_name VARCHAR NOT NULL,
    check_type VARCHAR NOT NULL, -- 'completeness', 'accuracy', 'consistency', 'timeliness'
    check_result BOOLEAN NOT NULL,
    details JSON,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Optimization Indexes

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_transactions_date ON facts.transactions(date_key);
CREATE INDEX IF NOT EXISTS idx_transactions_entity ON facts.transactions(entity_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON facts.transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON facts.transactions(amount);
CREATE INDEX IF NOT EXISTS idx_transactions_reconciled ON facts.transactions(is_reconciled);

CREATE INDEX IF NOT EXISTS idx_entities_country ON dimensions.entities(country_code);
CREATE INDEX IF NOT EXISTS idx_entities_risk ON dimensions.entities(risk_score);
CREATE INDEX IF NOT EXISTS idx_accounts_institution ON dimensions.accounts(institution_name);
CREATE INDEX IF NOT EXISTS idx_accounts_currency ON dimensions.accounts(currency_code);

-- Partitioning for large tables (DuckDB supports automatic partitioning)
-- Transactions table will be automatically partitioned by date_key

-- Views for Common Analytics

-- Daily transaction summary view
CREATE OR REPLACE VIEW olap.daily_transaction_summary AS
SELECT 
    t.date_key,
    t.year,
    t.month,
    t.month_name,
    COUNT(*) as transaction_count,
    SUM(f.usd_amount) as total_usd_amount,
    AVG(f.usd_amount) as avg_usd_amount,
    COUNT(CASE WHEN f.is_reconciled THEN 1 END) as reconciled_count,
    COUNT(CASE WHEN NOT f.is_reconciled THEN 1 END) as unreconciled_count
FROM dimensions.time_dimension t
LEFT JOIN facts.transactions f ON t.date_key = f.date_key
GROUP BY t.date_key, t.year, t.month, t.month_name
ORDER BY t.date_key;

-- Entity risk summary view
CREATE OR REPLACE VIEW olap.entity_risk_summary AS
SELECT 
    e.entity_id,
    e.entity_name,
    e.entity_type,
    e.country_code,
    e.risk_score as entity_risk_score,
    COUNT(DISTINCT a.account_id) as account_count,
    COUNT(f.transaction_id) as transaction_count,
    SUM(f.usd_amount) as total_transaction_volume,
    AVG(f.usd_amount) as avg_transaction_amount,
    MAX(f.updated_at) as last_transaction_date
FROM dimensions.entities e
LEFT JOIN dimensions.accounts a ON e.entity_id = a.entity_id
LEFT JOIN facts.transactions f ON a.account_id = f.account_id
GROUP BY e.entity_id, e.entity_name, e.entity_type, e.country_code, e.risk_score
ORDER BY e.risk_score DESC;

-- Reconciliation efficiency view
CREATE OR REPLACE VIEW olap.reconciliation_efficiency AS
SELECT 
    DATE_TRUNC('month', f.date_key) as month,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN f.is_reconciled THEN 1 END) as reconciled_transactions,
    ROUND(COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(*), 2) as reconciliation_rate,
    AVG(f.confidence_score) as avg_confidence_score,
    COUNT(CASE WHEN f.confidence_score >= 0.8 THEN 1 END) as high_confidence_count
FROM facts.transactions f
GROUP BY DATE_TRUNC('month', f.date_key)
ORDER BY month;

-- Functions for Common Operations

-- Function to calculate running balance for an account
CREATE OR REPLACE FUNCTION olap.calculate_running_balance(account_id_param VARCHAR, end_date DATE)
RETURNS TABLE (
    transaction_id VARCHAR,
    date_key DATE,
    amount DECIMAL(15,2),
    running_balance DECIMAL(15,2)
) AS $$
    SELECT 
        t.transaction_id,
        t.date_key,
        t.amount,
        SUM(t.amount) OVER (
            PARTITION BY t.account_id 
            ORDER BY t.date_key, t.created_at
            ROWS UNBOUNDED PRECEDING
        ) as running_balance
    FROM facts.transactions t
    WHERE t.account_id = account_id_param 
    AND t.date_key <= end_date
    ORDER BY t.date_key, t.created_at
$$;

-- Function to find potential duplicate transactions
CREATE OR REPLACE FUNCTION olap.find_potential_duplicates(
    amount_threshold DECIMAL(15,2),
    date_window_days INTEGER,
    confidence_threshold DECIMAL(5,2)
)
RETURNS TABLE (
    transaction_id_1 VARCHAR,
    transaction_id_2 VARCHAR,
    amount_1 DECIMAL(15,2),
    amount_2 DECIMAL(15,2),
    date_diff_days INTEGER,
    similarity_score DECIMAL(5,2)
) AS $$
    SELECT 
        t1.transaction_id as transaction_id_1,
        t2.transaction_id as transaction_id_2,
        t1.amount as amount_1,
        t2.amount as amount_2,
        ABS(DATE_DIFF('day', t1.date_key, t2.date_key)) as date_diff_days,
        CASE 
            WHEN t1.amount = t2.amount THEN 1.0
            WHEN ABS(t1.amount - t2.amount) <= amount_threshold THEN 0.8
            ELSE 0.5
        END as similarity_score
    FROM facts.transactions t1
    JOIN facts.transactions t2 ON t1.transaction_id < t2.transaction_id
    WHERE t1.account_id = t2.account_id
    AND ABS(DATE_DIFF('day', t1.date_key, t2.date_key)) <= date_window_days
    AND t1.amount >= amount_threshold
    AND t2.amount >= amount_threshold
    AND NOT t1.is_reconciled
    AND NOT t2.is_reconciled
    ORDER BY similarity_score DESC, date_diff_days ASC
$$;

-- Grant permissions (adjust based on your security model)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA olap TO nexus_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA staging TO nexus_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA dimensions TO nexus_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA facts TO nexus_user;

-- Insert sample data for testing
INSERT OR IGNORE INTO dimensions.entities (entity_id, entity_name, entity_type, country_code) VALUES
('ENT001', 'Sample Company Ltd', 'company', 'US'),
('ENT002', 'John Doe', 'individual', 'US'),
('ENT003', 'Test Organization', 'organization', 'CA');

-- Commit all changes
COMMIT;
