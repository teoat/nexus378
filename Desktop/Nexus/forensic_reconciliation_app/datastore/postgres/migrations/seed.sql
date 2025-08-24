-- Seed data for the Forensic Reconciliation + Fraud Platform

-- Insert sample users
-- Note: Passwords should be properly hashed in a real application.
-- These are placeholders.
INSERT INTO users (username, email, password_hash, role) VALUES
('jdoe', 'john.doe@example.com', 'hashed_password_1', 'analyst'),
('asmith', 'alice.smith@example.com', 'hashed_password_2', 'manager'),
('bjenkins', 'bob.jenkins@example.com', 'hashed_password_3', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Insert sample cases
-- This assumes the users above were inserted successfully.
INSERT INTO cases (case_name, description, status, assigned_to) VALUES
('Suspicious Wire Transfers Q4 2023', 'Investigating a series of large, unusual wire transfers.', 'in_progress', (SELECT id FROM users WHERE email = 'john.doe@example.com')),
('Potential Insider Trading Scheme', 'Analyzing trades made by employees before a major announcement.', 'new', (SELECT id FROM users WHERE email = 'alice.smith@example.com')),
('Closed Case: Phishing Attack on Finance Dept', 'A phishing attack that was successfully mitigated.', 'closed', (SELECT id FROM users WHERE email = 'john.doe@example.com'))
ON CONFLICT (case_name) DO NOTHING;

-- Insert sample transactions
INSERT INTO transactions (amount, currency, transaction_date, description, from_account, to_account, is_suspicious, risk_score) VALUES
(50000.00, 'USD', '2023-10-15 10:30:00+00', 'Wire Transfer to Offshore Account', 'ACC123456', 'OFFSHORE789', TRUE, 0.95),
(1250.75, 'USD', '2023-11-20 14:00:00+00', 'Payment for Services', 'ACC987654', 'VENDOR456', FALSE, 0.10),
(25000.00, 'EUR', '2023-12-01 09:00:00+00', 'Stock Purchase', 'EMP_BROKERAGE_1', 'MARKET', TRUE, 0.80),
(300.00, 'GBP', '2023-12-05 18:45:00+00', 'Online Purchase', 'CUST555', 'ECOMMERCE_SITE', FALSE, 0.05)
ON CONFLICT DO NOTHING;

-- Insert sample evidence
-- This assumes the cases above were inserted successfully.
INSERT INTO evidence (case_id, file_path, file_hash, type, description, uploaded_by) VALUES
((SELECT id FROM cases WHERE case_name = 'Suspicious Wire Transfers Q4 2023'), '/evidence_store/case1/wire_transfer_logs.csv', 'sha256_hash_of_file_1', 'log_file', 'Log files of all wire transfers in Q4 2023.', (SELECT id FROM users WHERE email = 'john.doe@example.com')),
((SELECT id FROM cases WHERE case_name = 'Suspicious Wire Transfers Q4 2023'), '/evidence_store/case1/bank_statement.pdf', 'sha256_hash_of_file_2', 'document', 'Bank statement for account ACC123456.', (SELECT id FROM users WHERE email = 'john.doe@example.com')),
((SELECT id FROM cases WHERE case_name = 'Potential Insider Trading Scheme'), '/evidence_store/case2/trading_records.xlsx', 'sha256_hash_of_file_3', 'document', 'Employee trading records.', (SELECT id FROM users WHERE email = 'alice.smith@example.com'))
ON CONFLICT DO NOTHING;

-- Link transactions to cases
INSERT INTO case_transactions (case_id, transaction_id) VALUES
((SELECT id FROM cases WHERE case_name = 'Suspicious Wire Transfers Q4 2023'), (SELECT id FROM transactions WHERE from_account = 'ACC123456')),
((SELECT id FROM cases WHERE case_name = 'Potential Insider Trading Scheme'), (SELECT id FROM transactions WHERE from_account = 'EMP_BROKERAGE_1'))
ON CONFLICT DO NOTHING;

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, target_resource, target_id, details) VALUES
((SELECT id FROM users WHERE email = 'alice.smith@example.com'), 'create_case', 'cases', (SELECT id FROM cases WHERE case_name = 'Potential Insider Trading Scheme'), '{"description": "Analyzing trades made by employees before a major announcement."}'),
((SELECT id FROM users WHERE email = 'john.doe@example.com'), 'add_evidence', 'evidence', (SELECT id FROM evidence WHERE file_path = '/evidence_store/case1/wire_transfer_logs.csv'), '{"file_size": "2.5MB"}');

-- Log completion
\echo 'Database seeding completed.'
