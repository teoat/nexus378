#!/bin/bash

echo "🔍 Checking Nexus Platform environment configuration..."
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "✅ .env file found"
else
    echo "❌ .env file not found"
    exit 1
fi

# Check required variables
required_vars=(
    "POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD"
    "NEO4J_AUTH" "REDIS_PASSWORD" "RABBITMQ_USER" "RABBITMQ_PASSWORD"
    "MINIO_ROOT_USER" "MINIO_ROOT_PASSWORD"
    "GRAFANA_ADMIN_USER" "GRAFANA_ADMIN_PASSWORD"
    "API_GATEWAY_JWT_SECRET" "ENCRYPTION_KEY"
)

echo "📋 Checking required environment variables:"
for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" .env; then
        value=$(grep "^${var}=" .env | cut -d'=' -f2)
        if [ -n "$value" ] && [ "$value" != "your_*" ]; then
            echo "  ✅ $var: Set"
        else
            echo "  ⚠️  $var: Not properly configured"
        fi
    else
        echo "  ❌ $var: Missing"
    fi
done

echo ""
echo "�� Checking API keys:"
api_keys=("OPENAI_API_KEY" "ANTHROPIC_API_KEY" "GOOGLE_API_KEY")
for key in "${api_keys[@]}"; do
    if grep -q "^${key}=" .env; then
        value=$(grep "^${key}=" .env | cut -d'=' -f2)
        if [ -n "$value" ] && [ "$value" != "your_*" ]; then
            echo "  ✅ $key: Configured"
        else
            echo "  ⚠️  $key: Needs configuration"
        fi
    else
        echo "  ❌ $key: Missing"
    fi
done

echo ""
echo "🚀 Environment check complete!"
