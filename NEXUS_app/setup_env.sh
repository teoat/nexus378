#!/bin/bash

# =============================================================================
# NEXUS PLATFORM - ENVIRONMENT SETUP SCRIPT
# =============================================================================

echo "🔧 Setting up Nexus Platform environment variables..."

# Generate secure passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Generate encryption key
generate_encryption_key() {
    openssl rand -hex 32
}

# Generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "=+/"
}

# Create .env file
cat > .env << EOF
# =============================================================================
# NEXUS PLATFORM - PRODUCTION ENVIRONMENT CONFIGURATION
# =============================================================================

# Database Configuration
POSTGRES_DB=forensic_prod_db
POSTGRES_USER=forensic_prod_user
POSTGRES_PASSWORD=$(generate_password)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Neo4j Configuration
NEO4J_AUTH=neo4j:$(generate_password)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=$(generate_password)

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$(generate_password)
REDIS_DB=0

# RabbitMQ Configuration
RABBITMQ_USER=forensic_user
RABBITMQ_PASSWORD=$(generate_password)
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/

# MinIO Configuration
MINIO_ROOT_USER=forensic_admin
MINIO_ROOT_PASSWORD=$(generate_password)
MINIO_ENDPOINT=minio:9000
MINIO_SECURE=false
MINIO_BUCKET_NAME=forensic-evidence

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$(generate_password)

# Prometheus Configuration
PROMETHEUS_RETENTION_TIME=200h

# AI Service Configuration
AI_SERVICE_HOST=0.0.0.0
AI_SERVICE_PORT=8000
AI_SERVICE_WORKERS=4
AI_SERVICE_WORKER_CLASS=uvicorn.workers.UvicornWorker

# Security Configuration
API_GATEWAY_JWT_SECRET=$(generate_jwt_secret)
ENCRYPTION_KEY=$(generate_encryption_key)
ENCRYPTION_ALGORITHM=AES-256-GCM

# MFA Configuration
MFA_ISSUER=Nexus_Forensic_Platform
MFA_ALGORITHM=SHA1
MFA_DIGITS=6
MFA_PERIOD=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=/app/logs

# Performance Configuration
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
REDIS_POOL_SIZE=10
RABBITMQ_POOL_SIZE=5
REQUEST_TIMEOUT=30
DB_TIMEOUT=10
REDIS_TIMEOUT=5
RABBITMQ_TIMEOUT=10

# Feature Flags
ENABLE_AI_ANALYSIS=true
ENABLE_EVIDENCE_PROCESSING=true
ENABLE_CHAIN_OF_CUSTODY=true
ENABLE_COMPLIANCE_REPORTING=true
ENABLE_AUDIT_LOGGING=true
ENABLE_PERFORMANCE_MONITORING=true

# Development Overrides
DEBUG=false
TESTING=false
DEVELOPMENT_MODE=false
EOF

echo "✅ Environment file created successfully!"
echo "🔐 Generated secure passwords and keys"
echo "�� Please review .env file and update API keys manually"
echo ""
echo "⚠️  IMPORTANT: Update these values manually:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - GOOGLE_API_KEY"
echo "   - Any other external API keys"
echo ""
echo "🚀 Ready to launch Docker services!"
