# Forensic Reconciliation Platform - Makefile
# Provides common Docker operations and shortcuts

.PHONY: help build build-prod build-cache clean up down logs restart health stats

# Default target
help:
	@echo "Forensic Reconciliation Platform - Available Commands:"
	@echo ""
	@echo "Build Commands:"
	@echo "  build           Build all services with optimization"
	@echo "  build-prod      Build production services"
	@echo "  build-cache     Build cache images only"
	@echo "  build-fast      Build with parallel processing"
	@echo ""
	@echo "Runtime Commands:"
	@echo "  up              Start all services"
	@echo "  up-prod         Start production services"
	@echo "  down            Stop all services"
	@echo "  restart         Restart all services"
	@echo "  logs            Show logs for all services"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean           Clean up Docker resources"
	@echo "  health          Run health checks"
	@echo "  stats           Show build statistics"
	@echo "  shell           Open shell in main app container"
	@echo "  shell-gateway   Open shell in API gateway container"
	@echo "  backup          Create backup of data volumes"
	@echo "  restore         Restore from backup"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev             Start development environment"
	@echo "  test            Run tests"
	@echo "  lint            Run linting"
	@echo "  format          Format code"
	@echo ""
	@echo "Examples:"
	@echo "  make build      # Build all services"
	@echo "  make up         # Start services"
	@echo "  make logs       # View logs"

# Build commands
build:
	@echo "Building all services with optimization..."
	./build_optimized.sh build

build-prod:
	@echo "Building production services..."
	./build_optimized.sh build-prod

build-cache:
	@echo "Building cache images..."
	./build_optimized.sh cache

build-fast:
	@echo "Building with parallel processing..."
	./build_optimized.sh build -p 8

# Runtime commands
up:
	@echo "Starting all services..."
	docker-compose up -d

up-prod:
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d

down:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	@echo "Showing logs for all services..."
	docker-compose logs -f

logs-app:
	@echo "Showing logs for main application..."
	docker-compose logs -f forensic_app

logs-gateway:
	@echo "Showing logs for API gateway..."
	docker-compose logs -f api_gateway

# Utility commands
clean:
	@echo "Cleaning up Docker resources..."
	./build_optimized.sh clean

health:
	@echo "Running health checks..."
	./build_optimized.sh health

stats:
	@echo "Showing build statistics..."
	./build_optimized.sh stats

shell:
	@echo "Opening shell in main app container..."
	docker-compose exec forensic_app /bin/bash

shell-gateway:
	@echo "Opening shell in API gateway container..."
	docker-compose exec api_gateway /bin/sh

# Backup and restore
backup:
	@echo "Creating backup of data volumes..."
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	docker run --rm -v forensic_reconciliation_app_postgres_data:/data -v $(PWD)/backups/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
	docker run --rm -v forensic_reconciliation_app_neo4j_data:/data -v $(PWD)/backups/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/neo4j_data.tar.gz -C /data .
	docker run --rm -v forensic_reconciliation_app_redis_data:/data -v $(PWD)/backups/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
	@echo "Backup created in backups/$(shell date +%Y%m%d_%H%M%S)/"

restore:
	@echo "Restoring from backup..."
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "Error: Please specify backup directory with BACKUP_DIR=<path>"; \
		echo "Example: make restore BACKUP_DIR=backups/20241201_120000"; \
		exit 1; \
	fi
	@if [ ! -d "$(BACKUP_DIR)" ]; then \
		echo "Error: Backup directory $(BACKUP_DIR) does not exist"; \
		exit 1; \
	fi
	docker run --rm -v forensic_reconciliation_app_postgres_data:/data -v $(PWD)/$(BACKUP_DIR):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
	docker run --rm -v forensic_reconciliation_app_neo4j_data:/data -v $(PWD)/$(BACKUP_DIR):/backup alpine tar xzf /backup/neo4j_data.tar.gz -C /data
	docker run --rm -v forensic_reconciliation_app_redis_data:/data -v $(PWD)/$(BACKUP_DIR):/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
	@echo "Restore completed from $(BACKUP_DIR)"

# Development commands
dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.yml up -d
	@echo "Development environment started!"
	@echo "Services available at:"
	@echo "  - Main App: http://localhost:8000"
	@echo "  - API Gateway: http://localhost:3000"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Neo4j: http://localhost:7474"
	@echo "  - MinIO: http://localhost:9001"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3001"
	@echo "  - Kibana: http://localhost:5601"

test:
	@echo "Running tests..."
	docker-compose exec forensic_app python -m pytest

lint:
	@echo "Running linting..."
	docker-compose exec forensic_app python -m flake8
	docker-compose exec forensic_app python -m black --check .
	docker-compose exec forensic_app python -m mypy .

format:
	@echo "Formatting code..."
	docker-compose exec forensic_app python -m black .
	docker-compose exec forensic_app python -m isort .

# Monitoring commands
monitor:
	@echo "Opening monitoring dashboards..."
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001"
	@echo "Kibana: http://localhost:5601"
	@echo "MinIO Console: http://localhost:9001"

# Database commands
db-shell:
	@echo "Opening PostgreSQL shell..."
	docker-compose exec postgres psql -U postgres -d forensic_reconciliation

neo4j-shell:
	@echo "Opening Neo4j shell..."
	docker-compose exec neo4j cypher-shell -u neo4j -p secure_password_123

redis-cli:
	@echo "Opening Redis CLI..."
	docker-compose exec redis redis-cli

# Quick status check
status:
	@echo "Service Status:"
	docker-compose ps
	@echo ""
	@echo "Resource Usage:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Performance optimization
optimize:
	@echo "Optimizing Docker performance..."
	docker system prune -f
	docker builder prune -f
	docker image prune -f
	@echo "Optimization completed"

# Security scan
security-scan:
	@echo "Running security scan on images..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image forensic_reconciliation_app:latest
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image forensic_reconciliation_app-api_gateway:latest
