# Forensic Reconciliation Platform - Deployment Guide

## Overview
This guide covers deploying the Forensic Reconciliation Platform using Docker and Kubernetes.

## Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM available
- 20GB+ disk space

## Quick Start (Docker)

### 1. Environment Setup
```bash
# Copy production environment file
cp env.prod .env

# Edit .env with your production values
nano .env
```

### 2. Deploy Platform
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Access Services
- **Frontend**: http://localhost
- **API Gateway**: http://localhost:3000
- **AI Service**: http://localhost:8000
- **Grafana**: http://localhost:3001 (admin/SecureGrafanaPassword2024!)
- **Kibana**: http://localhost:5601

## Production Deployment

### 1. Build Production Images
```bash
# API Gateway
cd api_gateway
docker build -f Dockerfile.prod -t forensic-api-gateway:latest .
cd ..

# AI Service
cd ai_service
docker build -f Dockerfile.prod -t forensic-ai-service:latest .
cd ..

# Frontend
cd frontend
docker build -f Dockerfile.prod -t forensic-frontend:latest .
cd ..
```

### 2. Configure Production Environment
Edit `env.prod` with:
- Strong passwords
- SSL certificates
- Domain names
- Production API keys

### 3. Deploy with Production Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### 1. Create Namespace
```bash
kubectl create namespace forensic-reconciliation
```

### 2. Apply Configurations
```bash
kubectl apply -f k8s/ -n forensic-reconciliation
```

### 3. Check Status
```bash
kubectl get all -n forensic-reconciliation
```

## Monitoring & Health Checks

### Health Endpoints
- `/health` - Basic health check
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe

### Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api_gateway
```

### Resource Monitoring
```bash
# Container stats
docker stats

# System resources
docker system df
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Stop conflicting services
sudo systemctl stop apache2  # if needed
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker exec -it forensic-reconciliation_postgres_1 psql -U forensic_prod_user -d forensic_reconciliation_prod
```

#### 3. Memory Issues
```bash
# Check available memory
free -h

# Increase Docker memory limit in Docker Desktop settings
```

### Reset Platform
```bash
# Stop and remove everything
docker-compose -f docker-compose.prod.yml down -v

# Remove images
docker rmi forensic-api-gateway:latest forensic-ai-service:latest forensic-frontend:latest

# Start fresh
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

### 1. Change Default Passwords
- Update all passwords in `.env`
- Use strong, unique passwords
- Consider password manager

### 2. SSL/TLS Configuration
- Obtain valid SSL certificates
- Configure Nginx for HTTPS
- Enable HSTS headers

### 3. Network Security
- Use firewall rules
- Limit external access
- Monitor network traffic

### 4. Access Control
- Implement proper authentication
- Use role-based access control
- Regular access reviews

## Backup & Recovery

### 1. Database Backup
```bash
# PostgreSQL backup
docker exec forensic-reconciliation_postgres_1 pg_dump -U forensic_prod_user forensic_reconciliation_prod > backup.sql

# Neo4j backup
docker exec forensic-reconciliation_neo4j_1 neo4j-admin dump --database=neo4j --to=/backups/
```

### 2. File Backup
```bash
# Backup uploads and data
tar -czf forensic-data-backup.tar.gz uploads/ cache/ logs/
```

### 3. Restore
```bash
# PostgreSQL restore
docker exec -i forensic-reconciliation_postgres_1 psql -U forensic_prod_user -d forensic_reconciliation_prod < backup.sql
```

## Scaling

### Horizontal Scaling
```bash
# Scale AI Service
docker-compose -f docker-compose.prod.yml up -d --scale ai_service=3

# Scale API Gateway
docker-compose -f docker-compose.prod.yml up -d --scale api_gateway=2
```

### Load Balancing
- Nginx handles frontend load balancing
- API Gateway manages backend routing
- Consider external load balancer for production

## Performance Tuning

### 1. Database Optimization
- Adjust PostgreSQL memory settings
- Optimize Neo4j cache settings
- Monitor query performance

### 2. Application Tuning
- Adjust Node.js memory limits
- Optimize Python worker processes
- Configure connection pooling

### 3. System Tuning
- Increase file descriptor limits
- Optimize kernel parameters
- Monitor system resources

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Check resource availability
4. Review security settings

## Next Steps

After successful deployment:
1. Configure monitoring alerts
2. Set up automated backups
3. Implement CI/CD pipeline
4. Plan disaster recovery
5. Schedule security audits
