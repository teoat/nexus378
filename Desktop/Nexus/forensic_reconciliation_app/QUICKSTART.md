# 🚀 Quick Start Guide - Forensic Reconciliation + Fraud Platform

Get your forensic reconciliation platform up and running in minutes with this step-by-step guide.

## ⚡ Prerequisites

### **Required Software**
- **Docker & Docker Compose**: [Install Docker](https://docs.docker.com/get-docker/)
- **Node.js 18+**: [Install Node.js](https://nodejs.org/)
- **Python 3.9+**: [Install Python](https://www.python.org/downloads/)
- **Rust 1.70+**: [Install Rust](https://rustup.rs/)

### **System Requirements**
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 20GB free space
- **CPU**: Multi-core processor (4+ cores recommended)
- **OS**: macOS 10.15+, Ubuntu 20.04+, Windows 10+

## 🚀 Quick Start (5 Minutes)

### 1. **Clone Repository**
```bash
git clone #repository-url#
cd forensic_reconciliation_app
```

### 2. **Setup Environment**
```bash
# Copy environment template
cp env.template .env

# Edit environment variables (optional for first run)
nano .env
```

### 3. **Start Infrastructure**
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. **Access Platform**
- **Frontend**: Desktop app (will be built in next step)
- **API Gateway**: http://localhost:4000/graphql
- **Neo4j Browser**: http://localhost:7474
- **Redis Commander**: http://localhost:8081
- **pgAdmin**: http://localhost:8080
- **MinIO Console**: http://localhost:9001

## 🔧 Full Setup (15 Minutes)

### 1. **Install Dependencies**

#### **Backend Services**
```bash
# API Gateway
cd gateway
npm install
npm run build

# AI Services
cd ../ai_service
pip install -r requirements.txt
```

#### **Frontend Application**
```bash
# Install Tauri CLI
cargo install tauri-cli

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. **Initialize Databases**
```bash
# PostgreSQL setup
cd gateway
npm run migrate

# Neo4j setup
cd ../ai_service
python scripts/init_neo4j.py
```

### 3. **Start Services**
```bash
# Start API Gateway (Terminal 1)
cd gateway
npm run dev

# Start AI Services (Terminal 2)
cd ai_service
python main.py

# Start Frontend (Terminal 3)
cd frontend
npm run tauri dev
```

## 🧪 Test Your Setup

### 1. **Health Check**
```bash
# Check all services
curl http://localhost:4000/health
curl http://localhost:8000/health
```

### 2. **GraphQL Playground**
- Open http://localhost:4000/graphql
- Try this query:
```graphql
query {
  __schema {
    types {
      name
      description
    }
  }
}
```

### 3. **Database Connections**
```bash
# Test PostgreSQL
docker exec -it forensic_postgres psql -U postgres -d forensic_reconciliation

# Test Neo4j
docker exec -it forensic_neo4j cypher-shell -u neo4j -p secure_password_change_this

# Test Redis
docker exec -it forensic_redis redis-cli -a secure_password_change_this
```

## 📊 Sample Data & Testing

### 1. **Load Sample Data**
```bash
# Load sample reconciliation data
cd ai_service
python scripts/load_sample_data.py

# Load sample fraud patterns
python scripts/load_fraud_patterns.py
```

### 2. **Test AI Agents**
```bash
# Test reconciliation agent
python -m ai_service.agents.reconciliation_agent --test

# Test fraud detection
python -m ai_service.agents.fraud_agent --test
```

### 3. **Upload Sample Evidence**
```bash
# Upload sample files
python scripts/upload_sample_evidence.py
```

## 🔍 First Investigation

### 1. **Access Dashboard**
- Launch the Tauri desktop application
- Login with default credentials (see environment file)
- Switch to "Investigator Mode"

### 2. **Upload Evidence**
- Drag and drop sample files
- Watch AI processing in real-time
- Review extracted metadata and hashes

### 3. **Run Reconciliation**
- Select bank statements and receipts
- Click "Start Reconciliation"
- Review AI-powered matches and outliers

### 4. **Explore Fraud Graph**
- Navigate to Fraud Graph dashboard
- View entity relationships
- Explore detected patterns

## 🚨 Troubleshooting

### **Common Issues**

#### **Docker Services Not Starting**
```bash
# Check Docker status
docker --version
docker-compose --version

# Restart Docker
sudo systemctl restart docker

# Clean up containers
docker-compose down -v
docker-compose up -d
```

#### **Port Conflicts**
```bash
# Check port usage
sudo lsof -i :4000
sudo lsof -i :5432
sudo lsof -i :7474

# Kill conflicting processes
sudo kill -9 #PID#
```

#### **Database Connection Issues**
```bash
# Check service logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis

# Restart specific service
docker-compose restart postgres
```

#### **Python Dependencies**
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Check Python version
python --version
```

#### **Node.js Issues**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### **Performance Issues**

#### **Low Memory**
```bash
# Check memory usage
free -h
docker stats

# Increase Docker memory limit
# Edit Docker Desktop settings
```

#### **Slow Database Queries**
```bash
# Check database performance
docker exec -it forensic_postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Optimize Neo4j
docker exec -it forensic_neo4j cypher-shell -u neo4j -p secure_password_change_this -c "CALL dbms.listConfig() YIELD name, value WHERE name CONTAINS 'memory' RETURN name, value;"
```

## 🔧 Configuration

### **Environment Variables**
Key variables to customize:
```bash
# Database passwords
POSTGRES_PASSWORD#your_secure_password
NEO4J_PASSWORD#your_secure_password
REDIS_PASSWORD#your_secure_password

# API keys
OPENAI_API_KEY#your_openai_key
JWT_SECRET#your_jwt_secret

# Service ports
GATEWAY_PORT#4000
AI_SERVICE_PORT#8000
FRONTEND_PORT#3000
```

### **Service Configuration**
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
  
  neo4j:
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    ports:
      - "7474:7474"
      - "7687:7687"
```

## 📚 Next Steps

### **1. Explore Documentation**
- [Architecture Guide](docs/architecture.md)
- [Workflows Guide](docs/workflows.md)
- [API Reference](docs/api_reference.md)

### **2. Run Tests**
```bash
# Unit tests
npm run test:unit
python -m pytest ai_service/tests/unit/

# Integration tests
npm run test:integration
python -m pytest ai_service/tests/integration/
```

### **3. Customize Platform**
- Modify agent configurations
- Add custom fraud patterns
- Integrate with external systems
- Develop custom plugins

### **4. Production Deployment**
- Set up production environment
- Configure monitoring and alerting
- Implement backup and recovery
- Set up CI/CD pipeline

## 🆘 Getting Help

### **Immediate Support**
- **Documentation**: Check the docs folder
- **Issues**: GitHub issues for bugs
- **Discussions**: GitHub discussions for questions

### **Community Resources**
- **Discord**: Real-time community support
- **Blog**: Latest updates and tutorials
- **Webinars**: Live demonstrations

### **Professional Support**
- **Enterprise Support**: 24/7 technical support
- **Training**: User and administrator training
- **Consulting**: Custom development and integration

## 🎯 Success Metrics

### **Setup Success**
- ✅ All Docker services running
- ✅ Database connections established
- ✅ API endpoints responding
- ✅ Frontend application launching
- ✅ Sample data loaded
- ✅ First investigation completed

### **Performance Benchmarks**
- **Startup Time**: # 2 minutes
- **API Response**: # 100ms
- **Database Queries**: # 50ms
- **File Processing**: # 10 seconds per MB
- **AI Agent Response**: # 5 seconds

---

## 🎉 Congratulations!

You've successfully set up your Forensic Reconciliation + Fraud Platform! 

**What's Next?**
1. **Explore the Dashboard**: Try both Investigator and Executive modes
2. **Upload Evidence**: Test with your own files
3. **Run Investigations**: Experience AI-powered reconciliation
4. **Customize**: Adapt to your specific needs
5. **Scale**: Deploy to production

**Need Help?**
- Check the troubleshooting section above
- Review the comprehensive documentation
- Join the community for support

**Happy Investigating! 🕵️**

---

*This quick start guide gets you from zero to a fully functional forensic reconciliation platform in under 15 minutes.*
