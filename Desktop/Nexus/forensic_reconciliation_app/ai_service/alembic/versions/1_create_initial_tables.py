"""Create initial tables

Revision ID: 1
Revises:
Create Date: 2024-07-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    -- Create a custom type for user roles
    CREATE TYPE user_role AS ENUM ('analyst', 'manager', 'admin');
    """)
    op.execute("""
    -- Create a custom type for case status
    CREATE TYPE case_status AS ENUM ('new', 'in_progress', 'closed', 'escalated');
    """)
    op.execute("""
    -- Create a custom type for evidence type
    CREATE TYPE evidence_type AS ENUM ('document', 'image', 'log_file', 'transaction_record');
    """)
    op.execute("""
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role user_role NOT NULL DEFAULT 'analyst',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    op.execute("""
    -- Cases table for tracking forensic investigations
    CREATE TABLE IF NOT EXISTS cases (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        case_name VARCHAR(255) NOT NULL,
        description TEXT,
        status case_status NOT NULL DEFAULT 'new',
        assigned_to UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    op.execute("""
    -- Transactions table
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        amount NUMERIC(19, 4) NOT NULL,
        currency VARCHAR(3) NOT NULL,
        transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
        description TEXT,
        from_account VARCHAR(255),
        to_account VARCHAR(255),
        is_suspicious BOOLEAN DEFAULT FALSE,
        risk_score FLOAT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    op.execute("""
    -- Evidence table to store metadata about evidence files
    CREATE TABLE IF NOT EXISTS evidence (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        case_id UUID REFERENCES cases(id) NOT NULL,
        file_path VARCHAR(1024) NOT NULL,
        file_hash VARCHAR(256) NOT NULL,
        type evidence_type NOT NULL,
        description TEXT,
        uploaded_by UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    op.execute("""
    -- Add a junction table for transactions and cases
    CREATE TABLE IF NOT EXISTS case_transactions (
        case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
        transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
        PRIMARY KEY (case_id, transaction_id)
    );
    """)
    op.execute("""
    -- Add a table for audit logs
    CREATE TABLE IF NOT EXISTS audit_logs (
        id BIGSERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id),
        action VARCHAR(255) NOT NULL,
        target_resource VARCHAR(255),
        target_id UUID,
        details JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE;")
    op.execute("DROP TABLE IF EXISTS case_transactions CASCADE;")
    op.execute("DROP TABLE IF EXISTS evidence CASCADE;")
    op.execute("DROP TABLE IF EXISTS transactions CASCADE;")
    op.execute("DROP TABLE IF EXISTS cases CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")
    op.execute("DROP TYPE IF EXISTS evidence_type;")
    op.execute("DROP TYPE IF EXISTS case_status;")
    op.execute("DROP TYPE IF EXISTS user_role;")
