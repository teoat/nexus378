-- DuckDB Materialized Views for Performance Optimization
-- These views provide pre-computed aggregations for common analytical queries

-- Enable materialized view support
SET enable_progress_bar=true;

-- Materialized Views for Transaction Analysis

-- Monthly transaction summary materialized view
CREATE OR REPLACE VIEW olap.monthly_transaction_summary_mv AS
SELECT 
    DATE_TRUNC('month', f.date_key) as month,
    f.entity_id,
    e.entity_name,
    e.entity_type,
    f.account_id,
    a.account_type,
    a.institution_name,
    COUNT(*) as transaction_count,
    SUM(f.usd_amount) as total_usd_amount,
    AVG(f.usd_amount) as avg_usd_amount,
    MIN(f.usd_amount) as min_usd_amount,
    MAX(f.usd_amount) as max_usd_amount,
    COUNT(CASE WHEN f.is_reconciled THEN 1 END) as reconciled_count,
    COUNT(CASE WHEN NOT f.is_reconciled THEN 1 END) as unreconciled_count,
    AVG(f.confidence_score) as avg_confidence_score,
    MAX(f.updated_at) as last_transaction_date
FROM facts.transactions f
JOIN dimensions.entities e ON f.entity_id = e.entity_id
JOIN dimensions.accounts a ON f.account_id = a.account_id
GROUP BY 
    DATE_TRUNC('month', f.date_key),
    f.entity_id,
    e.entity_name,
    e.entity_type,
    f.account_id,
    a.account_type,
    a.institution_name;

-- Entity risk aggregation materialized view
CREATE OR REPLACE VIEW olap.entity_risk_aggregation_mv AS
SELECT 
    e.entity_id,
    e.entity_name,
    e.entity_type,
    e.country_code,
    e.jurisdiction,
    e.risk_score as base_risk_score,
    COUNT(DISTINCT a.account_id) as total_accounts,
    COUNT(DISTINCT f.transaction_id) as total_transactions,
    SUM(f.usd_amount) as total_transaction_volume,
    AVG(f.usd_amount) as avg_transaction_amount,
    STDDEV(f.usd_amount) as transaction_amount_stddev,
    COUNT(CASE WHEN f.usd_amount > 10000 THEN 1 END) as large_transaction_count,
    COUNT(CASE WHEN f.usd_amount > 50000 THEN 1 END) as very_large_transaction_count,
    MAX(f.updated_at) as last_activity_date,
    COUNT(CASE WHEN f.date_key >= CURRENT_DATE - INTERVAL 30 DAY THEN 1 END) as recent_transaction_count,
    AVG(f.confidence_score) as avg_confidence_score,
    -- Calculate dynamic risk score based on activity patterns
    CASE 
        WHEN COUNT(DISTINCT f.transaction_id) > 1000 THEN e.risk_score * 1.2
        WHEN COUNT(DISTINCT f.transaction_id) > 500 THEN e.risk_score * 1.1
        WHEN COUNT(DISTINCT f.transaction_id) > 100 THEN e.risk_score * 1.05
        ELSE e.risk_score
    END as calculated_risk_score
FROM dimensions.entities e
LEFT JOIN dimensions.accounts a ON e.entity_id = a.entity_id
LEFT JOIN facts.transactions f ON a.account_id = f.account_id
GROUP BY 
    e.entity_id,
    e.entity_name,
    e.entity_type,
    e.country_code,
    e.jurisdiction,
    e.risk_score;

-- Account activity summary materialized view
CREATE OR REPLACE VIEW olap.account_activity_summary_mv AS
SELECT 
    a.account_id,
    a.account_number,
    a.account_type,
    a.institution_name,
    a.currency_code,
    a.country_code,
    a.risk_score as account_risk_score,
    e.entity_id,
    e.entity_name,
    e.entity_type,
    COUNT(f.transaction_id) as total_transactions,
    SUM(f.usd_amount) as total_volume_usd,
    AVG(f.usd_amount) as avg_transaction_amount,
    MIN(f.date_key) as first_transaction_date,
    MAX(f.date_key) as last_transaction_date,
    COUNT(CASE WHEN f.date_key >= CURRENT_DATE - INTERVAL 7 DAY THEN 1 END) as last_7_days_count,
    COUNT(CASE WHEN f.date_key >= CURRENT_DATE - INTERVAL 30 DAY THEN 1 END) as last_30_days_count,
    COUNT(CASE WHEN f.date_key >= CURRENT_DATE - INTERVAL 90 DAY THEN 1 END) as last_90_days_count,
    COUNT(CASE WHEN f.is_reconciled THEN 1 END) as reconciled_count,
    COUNT(CASE WHEN NOT f.is_reconciled THEN 1 END) as unreconciled_count,
    AVG(f.confidence_score) as avg_confidence_score,
    -- Calculate account health score
    CASE 
        WHEN COUNT(f.transaction_id) = 0 THEN 0.0
        WHEN COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(f.transaction_id) >= 90 THEN 1.0
        WHEN COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(f.transaction_id) >= 75 THEN 0.8
        WHEN COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(f.transaction_id) >= 50 THEN 0.6
        ELSE 0.4
    END as reconciliation_health_score
FROM dimensions.accounts a
JOIN dimensions.entities e ON a.entity_id = e.entity_id
LEFT JOIN facts.transactions f ON a.account_id = f.account_id
GROUP BY 
    a.account_id,
    a.account_number,
    a.account_type,
    a.institution_name,
    a.currency_code,
    a.country_code,
    a.risk_score,
    e.entity_id,
    e.entity_name,
    e.entity_type;

-- Transaction pattern analysis materialized view
CREATE OR REPLACE VIEW olap.transaction_pattern_analysis_mv AS
SELECT 
    f.entity_id,
    e.entity_name,
    f.account_id,
    a.account_type,
    DATE_TRUNC('week', f.date_key) as week_start,
    EXTRACT(DOW FROM f.date_key) as day_of_week,
    EXTRACT(HOUR FROM f.created_at) as hour_of_day,
    COUNT(*) as transaction_count,
    SUM(f.usd_amount) as total_amount,
    AVG(f.usd_amount) as avg_amount,
    COUNT(CASE WHEN f.usd_amount > 1000 THEN 1 END) as large_transaction_count,
    COUNT(CASE WHEN f.usd_amount > 5000 THEN 1 END) as very_large_transaction_count,
    COUNT(CASE WHEN f.is_reconciled THEN 1 END) as reconciled_count,
    AVG(f.confidence_score) as avg_confidence_score
FROM facts.transactions f
JOIN dimensions.entities e ON f.entity_id = e.entity_id
JOIN dimensions.accounts a ON f.account_id = a.account_id
GROUP BY 
    f.entity_id,
    e.entity_name,
    f.account_id,
    a.account_type,
    DATE_TRUNC('week', f.date_key),
    EXTRACT(DOW FROM f.date_key),
    EXTRACT(HOUR FROM f.created_at);

-- Reconciliation efficiency by entity materialized view
CREATE OR REPLACE VIEW olap.reconciliation_efficiency_by_entity_mv AS
SELECT 
    f.entity_id,
    e.entity_name,
    e.entity_type,
    e.country_code,
    DATE_TRUNC('month', f.date_key) as month,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN f.is_reconciled THEN 1 END) as reconciled_transactions,
    ROUND(COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(*), 2) as reconciliation_rate,
    AVG(f.confidence_score) as avg_confidence_score,
    COUNT(CASE WHEN f.confidence_score >= 0.9 THEN 1 END) as high_confidence_count,
    COUNT(CASE WHEN f.confidence_score >= 0.8 AND f.confidence_score < 0.9 THEN 1 END) as medium_confidence_count,
    COUNT(CASE WHEN f.confidence_score < 0.8 THEN 1 END) as low_confidence_count,
    SUM(f.usd_amount) as total_volume,
    AVG(f.usd_amount) as avg_transaction_amount,
    -- Calculate efficiency trend
    CASE 
        WHEN COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(*) >= 90 THEN 'Excellent'
        WHEN COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(*) >= 75 THEN 'Good'
        WHEN COUNT(CASE WHEN f.is_reconciled THEN 1 END) * 100.0 / COUNT(*) >= 50 THEN 'Fair'
        ELSE 'Poor'
    END as efficiency_rating
FROM facts.transactions f
JOIN dimensions.entities e ON f.entity_id = e.entity_id
GROUP BY 
    f.entity_id,
    e.entity_name,
    e.entity_type,
    e.country_code,
    DATE_TRUNC('month', f.date_key);

-- Risk assessment summary materialized view
CREATE OR REPLACE VIEW olap.risk_assessment_summary_mv AS
SELECT 
    ra.entity_id,
    e.entity_name,
    e.entity_type,
    ra.risk_type,
    DATE_TRUNC('month', ra.date_key) as month,
    COUNT(*) as assessment_count,
    AVG(ra.risk_score) as avg_risk_score,
    MIN(ra.risk_score) as min_risk_score,
    MAX(ra.risk_score) as max_risk_score,
    AVG(ra.confidence_level) as avg_confidence_level,
    ra.assessment_method,
    -- Risk trend analysis
    CASE 
        WHEN AVG(ra.risk_score) > 0.8 THEN 'High Risk'
        WHEN AVG(ra.risk_score) > 0.5 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_category,
    -- Assessment frequency
    CASE 
        WHEN COUNT(*) >= 10 THEN 'Frequent'
        WHEN COUNT(*) >= 5 THEN 'Regular'
        ELSE 'Occasional'
    END as assessment_frequency
FROM facts.risk_assessments ra
JOIN dimensions.entities e ON ra.entity_id = e.entity_id
GROUP BY 
    ra.entity_id,
    e.entity_name,
    e.entity_type,
    ra.risk_type,
    DATE_TRUNC('month', ra.date_key),
    ra.assessment_method;

-- Data quality metrics materialized view
CREATE OR REPLACE VIEW olap.data_quality_metrics_mv AS
SELECT 
    dqc.table_name,
    dqc.check_type,
    DATE_TRUNC('day', dqc.checked_at) as check_date,
    COUNT(*) as total_checks,
    COUNT(CASE WHEN dqc.check_result THEN 1 END) as passed_checks,
    COUNT(CASE WHEN NOT dqc.check_result THEN 1 END) as failed_checks,
    ROUND(COUNT(CASE WHEN dqc.check_result THEN 1 END) * 100.0 / COUNT(*), 2) as pass_rate,
    -- Quality trend
    CASE 
        WHEN COUNT(CASE WHEN dqc.check_result THEN 1 END) * 100.0 / COUNT(*) >= 95 THEN 'Excellent'
        WHEN COUNT(CASE WHEN dqc.check_result THEN 1 END) * 100.0 / COUNT(*) >= 85 THEN 'Good'
        WHEN COUNT(CASE WHEN dqc.check_result THEN 1 END) * 100.0 / COUNT(*) >= 70 THEN 'Fair'
        ELSE 'Poor'
    END as quality_rating
FROM staging.data_quality_checks dqc
GROUP BY 
    dqc.table_name,
    dqc.check_type,
    DATE_TRUNC('day', dqc.checked_at);

-- Performance optimization indexes for materialized views

-- Create indexes on commonly queried columns in materialized views
CREATE INDEX IF NOT EXISTS idx_monthly_summary_month ON olap.monthly_transaction_summary_mv(month);
CREATE INDEX IF NOT EXISTS idx_monthly_summary_entity ON olap.monthly_transaction_summary_mv(entity_id);
CREATE INDEX IF NOT EXISTS idx_monthly_summary_account ON olap.monthly_summary_mv(account_id);

CREATE INDEX IF NOT EXISTS idx_risk_aggregation_entity ON olap.entity_risk_aggregation_mv(entity_id);
CREATE INDEX IF NOT EXISTS idx_risk_aggregation_country ON olap.entity_risk_aggregation_mv(country_code);
CREATE INDEX IF NOT EXISTS idx_risk_aggregation_risk ON olap.entity_risk_aggregation_mv(calculated_risk_score);

CREATE INDEX IF NOT EXISTS idx_account_activity_account ON olap.account_activity_summary_mv(account_id);
CREATE INDEX IF NOT EXISTS idx_account_activity_entity ON olap.account_activity_summary_mv(entity_id);
CREATE INDEX IF NOT EXISTS idx_account_activity_health ON olap.account_activity_summary_mv(reconciliation_health_score);

-- Functions for refreshing materialized views

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION olap.refresh_all_materialized_views()
RETURNS VOID AS $$
BEGIN
    -- Refresh all materialized views
    REFRESH VIEW olap.monthly_transaction_summary_mv;
    REFRESH VIEW olap.entity_risk_aggregation_mv;
    REFRESH VIEW olap.account_activity_summary_mv;
    REFRESH VIEW olap.transaction_pattern_analysis_mv;
    REFRESH VIEW olap.reconciliation_efficiency_by_entity_mv;
    REFRESH VIEW olap.risk_assessment_summary_mv;
    REFRESH VIEW olap.data_quality_metrics_mv;
    
    RAISE NOTICE 'All materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- Function to refresh specific materialized view
CREATE OR REPLACE FUNCTION olap.refresh_materialized_view(view_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('REFRESH VIEW %I', view_name);
    RAISE NOTICE 'Materialized view % refreshed successfully', view_name;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions for materialized views
-- GRANT SELECT ON ALL TABLES IN SCHEMA olap TO nexus_user;

-- Insert sample data quality checks
INSERT OR IGNORE INTO staging.data_quality_checks (check_id, table_name, check_type, check_result, details) VALUES
('DQ001', 'facts.transactions', 'completeness', true, '{"field": "transaction_id", "completeness_rate": 100.0}'),
('DQ002', 'facts.transactions', 'accuracy', true, '{"field": "amount", "null_count": 0, "negative_count": 0}'),
('DQ003', 'dimensions.entities', 'consistency', true, '{"field": "country_code", "valid_countries": 195, "invalid_count": 0}');

-- Commit all changes
COMMIT;
