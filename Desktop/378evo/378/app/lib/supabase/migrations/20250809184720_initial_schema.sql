-- Cases table
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    currency TEXT DEFAULT 'USD',
    thousand_separator TEXT DEFAULT ',',
    source_file_content TEXT,
    bank_file_content TEXT,
    source_file_row_count INTEGER DEFAULT 0,
    bank_file_row_count INTEGER DEFAULT 0,
    column_mapping JSONB,
    bank_column_mapping JSONB,
    analysis_result JSONB,
    tolerances JSONB DEFAULT '{"date": 2, "amount": 1}',
    rules JSONB DEFAULT '[]',
    operation_mode TEXT DEFAULT 'guided',
    version_history JSONB DEFAULT '[]'
);

-- Anomalies table (for better querying)
CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    date DATE,
    description TEXT,
    amount DECIMAL(15,2),
    category TEXT,
    reason TEXT,
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    status TEXT DEFAULT 'Unreviewed',
    notes TEXT,
    original_data JSONB,
    audit_history JSONB DEFAULT '[]',
    sentiment TEXT,
    legal_risk_tags TEXT[],
    case_linkability_score INTEGER,
    legal_risk_narrative TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File uploads table
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type TEXT NOT NULL,
    upload_type TEXT NOT NULL, -- 'source' or 'bank'
    status TEXT DEFAULT 'pending',
    storage_path TEXT,
    metadata JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_cases_owner_id ON cases(owner_id);
CREATE INDEX idx_cases_updated_at ON cases(updated_at);
CREATE INDEX idx_anomalies_case_id ON anomalies(case_id);
CREATE INDEX idx_anomalies_status ON anomalies(status);
CREATE INDEX idx_anomalies_risk_score ON anomalies(risk_score);
CREATE INDEX idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX idx_file_uploads_status ON file_uploads(status);

-- Row Level Security (RLS) Policies
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_uploads ENABLE ROW LEVEL SECURITY;

-- Cases policies
CREATE POLICY "Users can view own cases" ON cases
    FOR SELECT USING (auth.uid() = owner_id);

CREATE POLICY "Users can create own cases" ON cases
    FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Users can update own cases" ON cases
    FOR UPDATE USING (auth.uid() = owner_id);

CREATE POLICY "Users can delete own cases" ON cases
    FOR DELETE USING (auth.uid() = owner_id);

-- Anomalies policies
CREATE POLICY "Users can view anomalies from own cases" ON anomalies
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM cases 
            WHERE cases.id = anomalies.case_id 
            AND cases.owner_id = auth.uid()
        )
    );

-- File uploads policies
CREATE POLICY "Users can manage own uploads" ON file_uploads
    FOR ALL USING (auth.uid() = user_id);