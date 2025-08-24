#!/bin/bash
set -e
echo "🚀 Starting deployment..."
docker-compose -f docker-compose.prod.yml up -d
