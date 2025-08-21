-- Forensic Reconciliation + Fraud Platform Database Schema
-- PostgreSQL 15+ Initialization Script

-- =============================================================================
-- CREATE EXTENSIONS
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- CREATE SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS evidence;
CREATE SCHEMA IF NOT EXISTS investigation;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS compliance;

-- =============================================================================
-- AUTHENTICATION SCHEMA
-- =============================================================================

-- Users table
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles table
CREATE TABLE auth.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User roles junction table
CREATE TABLE auth.user_roles (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES auth.roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- Sessions table
CREATE TABLE auth.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- CORE SCHEMA
-- =============================================================================

-- Organizations table
CREATE TABLE core.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(50),
    address JSONB,
    contact_info JSONB,
    industry VARCHAR(100),
    risk_level VARCHAR(20) DEFAULT 'LOW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cases table
CREATE TABLE core.cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    case_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'OPEN',
    assigned_investigator_id UUID REFERENCES auth.users(id),
    organization_id UUID REFERENCES core.organizations(id),
    estimated_completion_date DATE,
    actual_completion_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- EVIDENCE SCHEMA
-- =============================================================================

-- Evidence files table
CREATE TABLE evidence.files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES core.cases(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    file_hash_sha256 VARCHAR(64) NOT NULL,
    file_hash_md5 VARCHAR(32),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by UUID REFERENCES auth.users(id),
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    metadata JSONB,
    tags TEXT[]
);

-- Evidence metadata table
CREATE TABLE evidence.metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES evidence.files(id) ON DELETE CASCADE,
    metadata_type VARCHAR(50) NOT NULL,
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value TEXT,
    confidence_score DECIMAL(3,2),
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evidence relationships table
CREATE TABLE evidence.relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_file_id UUID REFERENCES evidence.files(id) ON DELETE CASCADE,
    target_file_id UUID REFERENCES evidence.files(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- INVESTIGATION SCHEMA
-- =============================================================================

-- Investigation steps table
CREATE TABLE investigation.steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES core.cases(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    assigned_to UUID REFERENCES auth.users(id),
    due_date DATE,
    completed_date DATE,
    findings TEXT,
    evidence_ids UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investigation findings table
CREATE TABLE investigation.findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES core.cases(id) ON DELETE CASCADE,
    step_id UUID REFERENCES investigation.steps(id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    description TEXT NOT NULL,
    evidence_ids UUID[],
    risk_score DECIMAL(3,2),
    recommendations TEXT,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- AUDIT SCHEMA
-- =============================================================================

-- Audit logs table
CREATE TABLE audit.logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data access logs table
CREATE TABLE audit.data_access (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    access_type VARCHAR(20) NOT NULL,
    ip_address INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- COMPLIANCE SCHEMA
-- =============================================================================

-- Compliance rules table
CREATE TABLE compliance.rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    description TEXT,
    rule_definition JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance violations table
CREATE TABLE compliance.violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES core.cases(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES compliance.rules(id),
    violation_date DATE NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'OPEN',
    remediation_required TEXT,
    remediation_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

-- Users indexes
CREATE INDEX idx_users_username ON auth.users(username);
CREATE INDEX idx_users_email ON auth.users(email);
CREATE INDEX idx_users_active ON auth.users(is_active);

-- Cases indexes
CREATE INDEX idx_cases_number ON core.cases(case_number);
CREATE INDEX idx_cases_status ON core.cases(status);
CREATE INDEX idx_cases_investigator ON core.cases(assigned_investigator_id);
CREATE INDEX idx_cases_organization ON core.cases(organization_id);

-- Evidence indexes
CREATE INDEX idx_files_case_id ON evidence.files(case_id);
CREATE INDEX idx_files_hash ON evidence.files(file_hash_sha256);
CREATE INDEX idx_files_status ON evidence.files(processing_status);
CREATE INDEX idx_files_upload_date ON evidence.files(upload_date);

-- Investigation indexes
CREATE INDEX idx_steps_case_id ON investigation.steps(case_id);
CREATE INDEX idx_steps_status ON investigation.steps(status);
CREATE INDEX idx_steps_assigned ON investigation.steps(assigned_to);

-- Audit indexes
CREATE INDEX idx_audit_user ON audit.logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit.logs(timestamp);
CREATE INDEX idx_audit_action ON audit.logs(action);

-- =============================================================================
-- CREATE TRIGGERS FOR AUDIT LOGGING
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON core.organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON core.cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_steps_updated_at BEFORE UPDATE ON investigation.steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_findings_updated_at BEFORE UPDATE ON investigation.findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON compliance.rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_violations_updated_at BEFORE UPDATE ON compliance.violations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- INSERT DEFAULT DATA
-- =============================================================================

-- Insert default roles
INSERT INTO auth.roles (name, description, permissions) VALUES
('admin', 'System Administrator', '{"all": true}'),
('investigator', 'Forensic Investigator', '{"cases": ["read", "write"], "evidence": ["read", "write"], "investigation": ["read", "write"]}'),
('analyst', 'Data Analyst', '{"cases": ["read"], "evidence": ["read"], "investigation": ["read"]}'),
('viewer', 'Read-only User', '{"cases": ["read"], "evidence": ["read"]}');

-- Insert default compliance rules
INSERT INTO compliance.rules (rule_name, rule_type, description, rule_definition) VALUES
('SOX_Financial_Accuracy', 'SOX', 'Ensure financial data accuracy and completeness', '{"type": "validation", "fields": ["amount", "date", "account"], "threshold": 0.95}'),
('PCI_Data_Protection', 'PCI', 'Protect sensitive payment card information', '{"type": "encryption", "fields": ["card_number", "cvv"], "algorithm": "AES-256"}'),
('AML_Transaction_Monitoring', 'AML', 'Monitor transactions for suspicious activity', '{"type": "threshold", "fields": ["amount", "frequency"], "limits": {"daily": 10000, "monthly": 100000}}');

-- =============================================================================
-- CREATE VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Case summary view
CREATE VIEW core.case_summary AS
SELECT 
    c.id,
    c.case_number,
    c.title,
    c.case_type,
    c.priority,
    c.status,
    c.estimated_completion_date,
    c.actual_completion_date,
    u.username as assigned_investigator,
    o.name as organization_name,
    COUNT(e.id) as evidence_count,
    COUNT(s.id) as step_count,
    COUNT(f.id) as finding_count
FROM core.cases c
LEFT JOIN auth.users u ON c.assigned_investigator_id = u.id
LEFT JOIN core.organizations o ON c.organization_id = o.id
LEFT JOIN evidence.files e ON c.id = e.case_id
LEFT JOIN investigation.steps s ON c.id = s.case_id
LEFT JOIN investigation.findings f ON c.id = f.case_id
GROUP BY c.id, c.case_number, c.title, c.case_type, c.priority, c.status, 
         c.estimated_completion_date, c.actual_completion_date, u.username, o.name;

-- Evidence summary view
CREATE VIEW evidence.evidence_summary AS
SELECT 
    f.id,
    f.filename,
    f.original_filename,
    f.file_size,
    f.mime_type,
    f.processing_status,
    f.upload_date,
    u.username as uploaded_by,
    c.case_number,
    c.title as case_title
FROM evidence.files f
LEFT JOIN auth.users u ON f.uploaded_by = u.id
LEFT JOIN core.cases c ON f.case_id = c.id;

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA auth, core, evidence, investigation, audit, compliance TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth, core, evidence, investigation, audit, compliance TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth, core, evidence, investigation, audit, compliance TO postgres;

-- =============================================================================
-- COMMIT TRANSACTION
-- =============================================================================

COMMIT;
