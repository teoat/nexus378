# 🐳 Docker Management System

## Overview

This folder contains the **unified Docker management system** for the Nexus Platform. All Docker-related configurations, scripts, and documentation have been consolidated here to eliminate duplicates and provide a single source of truth.

## 📁 File Organization

```
docker/
├── README.md                           # This file - Docker system overview
├── docker-compose.unified.yml          # 🚀 UNIFIED MASTER CONFIGURATION
├── Dockerfile.unified                  # 🏗️ UNIFIED MULTI-STAGE DOCKERFILE
├── docker-manage.sh                    # 🛠️ COMPREHENSIVE MANAGEMENT SCRIPT
└── DOCKER_UNIFIED_README.md           # 📚 COMPLETE DOCUMENTATION
```

## 🚀 Quick Access

### From Main Nexus Folder

The main Nexus folder contains a convenient access script:

```bash
# Quick commands from Nexus root
./nexus-docker.sh start              # Start development
./nexus-docker.sh production         # Start production
./nexus-docker.sh status             # Check status
./nexus-docker.sh logs               # View logs
./nexus-docker.sh health             # Health check
```

### From Docker Folder

For advanced operations, work directly in the Docker folder:

```bash
cd docker/

# Full management commands
./docker-manage.sh start production
./docker-manage.sh scale ai-service 5
./docker-manage.sh security production
./docker-manage.sh monitor
```

## 🎯 Key Features

### ✅ **Consolidated Configuration**
- **Single docker-compose file** for all environments
- **Unified Dockerfile** with multiple build targets
- **Environment-specific overrides** for customization
- **No more duplicate configurations**

### ✅ **Advanced Management**
- **Multi-environment support** (dev/staging/prod/testing)
- **Service scaling** and resource management
- **Health monitoring** and auto-recovery
- **Security auditing** and vulnerability scanning

### ✅ **Production Ready**
- **Monitoring stack** (Prometheus, Grafana, ELK)
- **Security hardening** with AppArmor profiles
- **Performance optimization** and resource limits
- **Backup/restore** capabilities

## 🔧 Usage Examples

### Basic Operations

```bash
# Start development environment
./nexus-docker.sh start

# Start production environment
./nexus-docker.sh production

# Check service status
./nexus-docker.sh status

# View service logs
./nexus-docker.sh logs ai-service
```

### Advanced Operations

```bash
# Scale services
./nexus-docker.sh scale api-gateway 5

# Security audit
./nexus-docker.sh security production

# Performance optimization
./nexus-docker.sh optimize

# Start monitoring
./nexus-docker.sh monitor
```

### Environment Management

```bash
# Development
./nexus-docker.sh start development

# Staging
./nexus-docker.sh start staging

# Production
./nexus-docker.sh start production

# Testing
./nexus-docker.sh start testing
```

## 🏗️ Build Targets

The unified Dockerfile supports multiple build targets:

```bash
# Development (with hot reload)
docker build --target development -f docker/Dockerfile.unified .

# Testing (with test dependencies)
docker build --target testing -f docker/Dockerfile.unified .

# Production (optimized)
docker build --target production -f docker/Dockerfile.unified .

# Security hardened
docker build --target security-hardened -f docker/Dockerfile.unified .
```

## 🌍 Environment Configuration

### Environment Variables

Set environment variables for customization:

```bash
export NEXUS_ENV=production
export POSTGRES_PASSWORD=secure_password
export ANTHROPIC_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

### Environment-Specific Overrides

Create override files for custom configurations:

```yaml
# docker-compose.production.override.yml
version: '3.8'
services:
  ai-service:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
```

## 📊 Monitoring and Observability

### Available Services

- **Prometheus** - Metrics collection (port 9090)
- **Grafana** - Visualization dashboards (port 3000)
- **AlertManager** - Alert management (port 9093)
- **Elasticsearch** - Log storage (port 9200)
- **Kibana** - Log visualization (port 5601)

### Quick Access

```bash
# Start monitoring stack
./nexus-docker.sh monitor

# Check health
./nexus-docker.sh health

# View metrics
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana
```

## 🔒 Security Features

### Security Commands

```bash
# Security audit
./nexus-docker.sh security production

# Vulnerability scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro \
  aquasec/trivy image nexus_ai_service_production
```

### Security Features

- **Non-root users** for all services
- **AppArmor profiles** for container isolation
- **Network isolation** with separate networks
- **JWT authentication** and API key management

## 📈 Performance and Scaling

### Scaling Commands

```bash
# Scale AI service
./nexus-docker.sh scale ai-service 5

# Scale API gateway
./nexus-docker.sh scale api-gateway 3

# Check resource usage
docker stats
```

### Performance Optimization

```bash
# Optimize performance
./nexus-docker.sh optimize

# Resource management
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
./nexus-docker.sh logs [service]

# Check health
./nexus-docker.sh health

# Verify configuration
docker-compose -f docker/docker-compose.unified.yml config
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in environment variables
export GATEWAY_PORT=8001
```

### Debug Mode

```bash
# Run in foreground
cd docker/
docker-compose -f docker-compose.unified.yml up

# Check individual service logs
docker-compose -f docker-compose.unified.yml logs [service]
```

## 🔄 Migration from Old Configurations

### Automatic Migration

The unified system automatically handles migration:

```bash
# Old way (deprecated)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# New way (unified)
./nexus-docker.sh start production
```

### Configuration Updates

1. **Update environment variables** to use new naming
2. **Migrate custom configs** to override files
3. **Update CI/CD pipelines** to use new commands
4. **Test thoroughly** in staging environment

## 📚 Documentation

### Complete Documentation

- **DOCKER_UNIFIED_README.md** - Comprehensive setup and usage guide
- **This README.md** - Quick reference and overview
- **Inline comments** in all configuration files

### Additional Resources

- **Docker Documentation** - Official Docker guides
- **Service Documentation** - Individual service guides
- **GitHub Issues** - Bug reports and feature requests

## 🆘 Support

### Getting Help

1. **Check this README** for quick solutions
2. **Review DOCKER_UNIFIED_README.md** for detailed information
3. **Use help commands** for command reference
4. **Check logs** for error details

### Help Commands

```bash
# Quick help
./nexus-docker.sh

# Detailed help
./nexus-docker.sh help

# System information
./nexus-docker.sh info
```

### Emergency Procedures

```bash
# Emergency stop
./nexus-docker.sh stop

# Emergency restart
./nexus-docker.sh restart

# Emergency backup
./nexus-docker.sh backup
```

## 📋 Best Practices

### Development

1. **Use development target** for local development
2. **Enable hot reload** for faster iteration
3. **Monitor resource usage** during development
4. **Use volume mounts** for code changes

### Production

1. **Use production target** for optimized builds
2. **Enable monitoring** for observability
3. **Implement health checks** for reliability
4. **Use resource limits** for stability

### Security

1. **Regular security audits** with security command
2. **Update base images** frequently
3. **Use secrets management** for credentials
4. **Implement network policies** for isolation

## 🔮 Future Enhancements

### Planned Features

- **Kubernetes Support** - Native K8s deployment
- **Service Mesh** - Istio integration
- **Advanced Monitoring** - Custom metrics and dashboards
- **Auto-scaling** - Dynamic resource allocation

### Roadmap

- **Q1 2025** - Enhanced monitoring and alerting
- **Q2 2025** - Kubernetes deployment support
- **Q3 2025** - Advanced security features
- **Q4 2025** - Performance optimization tools

---

## 📝 Summary

The Docker folder now contains a **unified, comprehensive Docker management system** that:

✅ **Eliminates all duplicate configurations**  
✅ **Provides consistent deployment across environments**  
✅ **Includes advanced monitoring and security features**  
✅ **Simplifies management with unified commands**  
✅ **Supports scaling and optimization**  
✅ **Maintains backward compatibility**  

**Access from Nexus root**: `./nexus-docker.sh [command]`  
**Access from Docker folder**: `./docker-manage.sh [command]`  
**Status**: Production Ready ✅  
**Version**: 1.0.0  
**Last Updated**: 2025-01-01
