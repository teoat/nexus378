# 🕵️ Forensic Reconciliation + Fraud Platform - MASTER README

*Single Source of Truth for Project Overview, Setup, and Usage*

## 🎯 **PROJECT MISSION**

Transform forensic investigations and compliance workflows by integrating AI-powered reconciliation, fraud detection, and litigation support into a single, unified platform that provides forensic-grade evidence management with explainable AI insights through intelligent multi-agent orchestration.

---

## 🌟 **KEY VALUE PROPOSITIONS**

### 🔍 **Unified Investigation Experience**
- **Single Dashboard**: One interface for all investigation modes (Investigator vs Executive)
- **Integrated Workflows**: Seamless transition between reconciliation, fraud analysis, and litigation
- **Real-time Collaboration**: Multi-user investigation support with role-based access

### 🤖 **AI-Powered Intelligence**
- **Multi-Agent Orchestration**: Specialized AI agents working in parallel via Taskmaster system
- **Explainable AI**: Transparent decision-making with factor breakdowns
- **Continuous Learning**: Self-improving algorithms based on investigation outcomes

### 🏛️ **Forensic-Grade Evidence Management**
- **Chain-of-Custody**: Complete audit trail for all evidence handling
- **Hash Verification**: SHA256 integrity checks with tamper detection
- **Multi-format Support**: PDFs, images, chat logs, bank statements, receipts

### 📊 **Advanced Analytics & Visualization**
- **Interactive Fraud Graphs**: Neo4j-powered entity relationship mapping
- **Risk Heatmaps**: Visual risk assessment with drill-down capabilities
- **Timeline Analysis**: Chronological investigation views with evidence linking

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │Unified      │ │Fraud Graph  │ │Risk Scores  │ │Evidence  │  │
│  │Dashboard    │ │Interactive  │ │Explainable  │ │Viewer    │  │
│  │(Investigator│ │Neo4j Graph  │ │AI Scoring   │ │EXIF/PDF  │  │
│  │vs Executive)│ │             │ │             │ │Chat Logs │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                       Gateway Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │Reconciliation│ │Fraud Graph │ │Evidence     │ │Litigation│  │
│  │API          │ │API         │ │API          │ │API       │  │
│  │GraphQL      │ │GraphQL     │ │GraphQL      │ │GraphQL   │  │
│  └─────────────┘ └────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                    TASKMASTER ORCHESTRATION LAYER               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │Job          │ │Task         │ │Workflow     │ │Resource  │  │
│  │Scheduler    │ │Router       │ │Orchestrator │ │Monitor   │  │
│  └─────────────┘ └────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                      AI Service Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │Reconciliation│ │Fraud       │ │Risk         │ │Evidence  │  │
│  │Agent        │ │Agent       │ │Agent        │ │Agent     │  │
│  │(Det+AI)     │ │(Parallel   │ │(Explainable)│ │(Hash+NLP)│  │
│  │             │ │AI)         │ │             │ │           │  │
│  └─────────────┘ └────────────┘ └─────────────┘ └──────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │Litigation   │ │Help Agent   │ │ML Models    │              │
│  │Agent        │ │(Interactive │ │& Pipelines  │              │
│  │(Case Mgmt)  │ │RAG)         │ │             │              │
│  └─────────────┘ └────────────┘ └─────────────┘              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                      Datastore Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │DuckDB       │ │Neo4j       │ │Postgres     │ │Redis     │  │
│  │OLAP Engine  │ │Graph DB    │ │Metadata     │ │Cache &   │  │
│  │Reconciliation│ │Fraud       │ │Audit Logs   │ │Queues    │  │
│  │             │ │Entities    │ │             │ │           │  │
│  └─────────────┘ └────────────┘ └─────────────┘ └──────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Evidence Store                           │ │
│  │              EXIF, PDFs, Chat Logs, Photos                  │ │
│  │              Hash Verification, Chain-of-Custody            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**For detailed architecture information, see [MASTER_ARCHITECTURE.md](MASTER_ARCHITECTURE.md)**

---

## 🛠️ **TECHNOLOGY STACK**

### **Frontend**
- **Rust + Tauri**: Desktop application framework
- **React**: User interface components
- **D3.js**: Interactive data visualizations
- **Leaflet/Mapbox**: Geographic mapping

### **Backend**
- **Node.js**: API gateway and orchestration
- **GraphQL**: Flexible data querying
- **Python**: AI/ML services and agents
- **LangGraph**: Multi-agent orchestration

### **Databases**
- **DuckDB**: OLAP reconciliation processing
- **Neo4j**: Graph fraud analysis
- **PostgreSQL**: Metadata and audit logs
- **Redis**: Caching and message queues

### **AI/ML**
- **LangChain**: RAG and agent frameworks
- **scikit-learn**: Traditional ML algorithms
- **PyTorch/TensorFlow**: Deep learning models
- **Explainable AI**: Factor breakdown and transparency

### **Orchestration**
- **Taskmaster System**: Intelligent job assignment and workflow management
- **RabbitMQ**: Message queuing for agent communication
- **WebSocket**: Real-time updates and collaboration

---

## 📁 **PROJECT STRUCTURE**

```
forensic_reconciliation_app/
│
├── frontend/                        # Rust/Tauri + React Desktop UI
│   ├── dashboards/
│   │   ├── unified_dashboard/        # Single dashboard with all modes
│   │   ├── fraud_graph/              # Neo4j interactive graph
│   │   ├── risk_scores/              # Explainable AI scoring
│   │   ├── litigation/               # Case-focused interactive timelines
│   │   └── evidence_viewer/          # Embedded EXIF, PDF, chat logs
│   ├── components/                   # Reusable widgets, filters, charts
│   ├── ai_assist/                    # HelpAgent (full session memory)
│   └── modes/                        # Investigator vs Executive toggles
│
├── gateway/                          # Node.js API Gateway
│   ├── api/                          # GraphQL endpoints
│   ├── websocket/                    # Real-time streaming
│   ├── auth/                         # Role-based access control
│   └── cache/                        # Redis connectors
│
├── ai_service/                       # Python AI Services
│   ├── taskmaster/                   # Taskmaster orchestration system
│   │   ├── core/                     # Core orchestration components
│   │   ├── models/                   # Data models for jobs and workflows
│   │   └── examples/                 # Usage examples and demonstrations
│   ├── agents/                       # Specialized AI agents
│   ├── explainability/               # AI transparency tools
│   ├── simulations/                  # Batch predictive simulations
│   ├── nlp/                          # Natural language processing
│   ├── ml_models/                    # Machine learning models
│   └── pipelines/                    # Data processing pipelines
│
├── datastore/                        # Multi-database architecture
│   ├── duckdb/                       # OLAP reconciliation engine
│   ├── neo4j/                        # Graph fraud analysis
│   ├── postgres/                     # Metadata and audit logs
│   ├── redis/                        # Caching and queues
│   └── evidence_store/               # Immutable evidence storage
│
├── communication/                    # Message queuing and streaming
│   ├── rabbitmq/                     # Primary message bus
│   ├── websocket/                    # Real-time updates
│   └── priority_channels/            # Priority-based processing
│
├── testing/                          # Comprehensive testing suite
│   ├── unit_tests/                   # Component testing
│   ├── integration_tests/            # Service integration
│   ├── performance/                  # Load and stress testing
│   └── forensic_scenarios/           # Real-world investigation testing
│
├── reports/                          # Export and reporting
│   ├── pdf_exports/                  # Interactive PDF generation
│   ├── compliance_reports/           # Regulatory compliance
│   └── audit_trails/                 # Complete audit logging
│
├── plugins/                          # Extensible plugin system
│   ├── insurance_fraud/              # Insurance-specific fraud detection
│   ├── crypto_laundering/            # Cryptocurrency analysis
│   └── corporate_espionage/          # Corporate investigation tools
│
├── docs/                             # Comprehensive documentation
│   ├── architecture.md               # System architecture guide
│   ├── workflows.md                  # Process workflows and agent interactions
│   ├── api_reference.md              # GraphQL API documentation
│   └── taskmaster_system.md          # Taskmaster system documentation
│
├── MASTER_ARCHITECTURE.md            # Single source of truth for architecture
├── MASTER_README.md                  # This file - single source of truth for project
├── TODO_MASTER.md                    # Single source of truth for implementation
├── docker-compose.yml                # Infrastructure services
├── env.template                      # Environment configuration template
└── QUICKSTART.md                     # Quick start guide
```

---

## 🚀 **QUICK START**

### **Prerequisites**
- **Docker & Docker Compose**: For containerized services
- **Node.js 18+**: For API gateway
- **Python 3.9+**: For AI services
- **Rust 1.70+**: For desktop application
- **PostgreSQL 14+**: For metadata storage
- **Neo4j 5+**: For graph analysis
- **Redis 7+**: For caching and queues

### **1. Clone Repository**
```bash
git clone #repository-url#
cd forensic_reconciliation_app
```

### **2. Environment Setup**
```bash
# Copy environment templates
cp env.template .env
cp docker-compose.example.yml docker-compose.yml

# Configure environment variables
nano .env
```

### **3. Start Infrastructure**
```bash
# Start databases and message queues
docker-compose up -d postgres neo4j redis rabbitmq

# Wait for services to be ready
docker-compose logs -f
```

### **4. Install Dependencies**
```bash
# Backend services
cd gateway && npm install
cd ../ai_service && pip install -r requirements.txt

# Frontend application
cd ../frontend && cargo install tauri-cli
npm install
```

### **5. Initialize Databases**
```bash
# Run database migrations
cd gateway && npm run migrate
cd ../ai_service && python scripts/init_db.py
```

### **6. Start Services**
```bash
# Start API gateway
cd gateway && npm run dev

# Start AI services
cd ../ai_service && python main.py

# Start frontend
cd ../frontend && npm run tauri dev
```

### **7. Access Platform**
- **Frontend Application**: Desktop app launched via Tauri
- **API Gateway**: http://localhost:4000/graphql
- **GraphQL Playground**: http://localhost:4000/graphql
- **Neo4j Browser**: http://localhost:7474
- **Redis Commander**: http://localhost:8081

**For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)**

---

## 🔧 **CONFIGURATION**

### **Environment Variables**
```bash
# Database Configuration
POSTGRES_HOST#localhost
POSTGRES_PORT#5432
POSTGRES_DB#forensic_reconciliation
POSTGRES_USER#postgres
POSTGRES_PASSWORD#secure_password

# Neo4j Configuration
NEO4J_URI#bolt://localhost:7687
NEO4J_USER#neo4j
NEO4J_PASSWORD#secure_password

# Redis Configuration
REDIS_HOST#localhost
REDIS_PORT#6379
REDIS_PASSWORD#secure_password

# RabbitMQ Configuration
RABBITMQ_HOST#localhost
RABBITMQ_PORT#5672
RABBITMQ_USER#admin
RABBITMQ_PASSWORD#secure_password

# AI Service Configuration
AI_SERVICE_HOST#localhost
AI_SERVICE_PORT#8000
OPENAI_API_KEY#your_openai_key
```

### **Taskmaster Configuration**
```yaml
# ai_service/taskmaster/config/taskmaster.yaml
taskmaster:
  general:
    max_concurrent_jobs: 1000
    max_concurrent_tasks: 5000
    job_timeout: "24 hours"
    task_timeout: "4 hours"
    
  scheduling:
    algorithm: "priority_weighted_round_robin"
    preemption: true
    fairness_factor: 0.8
    
  scaling:
    auto_scaling: true
    min_agents: 5
    max_agents: 100
    scale_up_threshold: 80%
    scale_down_threshold: 20%
```

---

## 🧪 **TESTING**

### **Run Test Suite**
```bash
# Unit tests
npm run test:unit
python -m pytest ai_service/tests/unit/

# Integration tests
npm run test:integration
python -m pytest ai_service/tests/integration/

# Performance tests
npm run test:performance
python -m pytest ai_service/tests/performance/

# Forensic scenarios
python -m pytest ai_service/tests/forensic_scenarios/
```

### **Test Coverage**
```bash
# Generate coverage reports
npm run test:coverage
python -m pytest --cov#ai_service --cov-report#html
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **Application Metrics**
- **Performance Monitoring**: Response times, throughput, error rates
- **Resource Utilization**: CPU, memory, disk, network usage
- **Business Metrics**: Reconciliation accuracy, fraud detection rates
- **User Analytics**: Dashboard usage, feature adoption

### **Taskmaster Monitoring**
- **Job Processing**: Queue status, job completion rates, SLA compliance
- **Agent Health**: CPU usage, memory usage, response times, error rates
- **System Performance**: Throughput, latency, resource utilization
- **Auto-scaling**: Scaling events, resource allocation, performance optimization

### **Logging & Tracing**
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Distributed Tracing**: Request flow across services
- **Audit Logging**: Complete user action history
- **Error Tracking**: Centralized error monitoring and alerting

---

## 🔐 **SECURITY & COMPLIANCE**

### **Authentication & Authorization**
- **Multi-factor Authentication**: TOTP, SMS, hardware tokens
- **Role-based Access Control**: Investigator, Executive, Admin, Auditor
- **Session Management**: Secure token handling with expiration
- **API Security**: Rate limiting, input validation, SQL injection protection

### **Data Protection**
- **Encryption**: End-to-end encryption for sensitive data
- **Hash Verification**: SHA256 checksums for evidence integrity
- **Chain-of-Custody**: Complete audit trail for evidence handling
- **Data Retention**: Configurable retention policies with GDPR compliance

### **Compliance Standards**
- **SOX Compliance**: Sarbanes-Oxley financial reporting
- **PCI DSS**: Payment card industry security standards
- **AML Regulations**: Anti-money laundering compliance
- **GDPR Compliance**: European data protection regulations

---

## 🚀 **DEPLOYMENT**

### **Production Deployment**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose -f docker-compose.prod.yml exec gateway npm run migrate:prod
```

### **Kubernetes Deployment**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Monitor deployment
kubectl get pods -n forensic-reconciliation
kubectl logs -f deployment/forensic-reconciliation-gateway
```

### **CI/CD Pipeline**
```bash
# Automated testing and deployment
git push origin main
# Triggers: Build → Test → Security Scan → Deploy → Monitor
```

---

## 🤝 **CONTRIBUTING**

### **Development Workflow**
1. **Fork Repository**: Create your own fork
2. **Feature Branch**: Create feature branch from main
3. **Development**: Implement features with tests
4. **Pull Request**: Submit PR with detailed description
5. **Code Review**: Address feedback and suggestions
6. **Merge**: Merge after approval and CI passing

### **Code Standards**
- **TypeScript**: Strict typing and ESLint rules
- **Python**: PEP 8 compliance and type hints
- **Rust**: Clippy linting and formatting
- **Testing**: Minimum 80% code coverage
- **Documentation**: Comprehensive API documentation

### **Commit Convention**
```
feat: add new fraud detection algorithm
fix: resolve reconciliation confidence calculation
docs: update API documentation
test: add integration tests for evidence agent
refactor: optimize Neo4j graph queries
```

---

## 📚 **DOCUMENTATION**

### **Core Documentation**
- [**MASTER_ARCHITECTURE.md**](MASTER_ARCHITECTURE.md): System architecture and design
- [**TODO_MASTER.md**](TODO_MASTER.md): Implementation roadmap and tasks
- [**docs/architecture.md**](docs/architecture.md): Detailed architecture guide
- [**docs/workflows.md**](docs/workflows.md): Process flows and agent interactions
- [**docs/api_reference.md**](docs/api_reference.md): GraphQL API documentation
- [**docs/taskmaster_system.md**](docs/taskmaster_system.md): Taskmaster system details

### **Development Guides**
- [**Frontend Development**](frontend/README.md): React + Tauri development
- [**Backend Development**](gateway/README.md): Node.js API development
- [**AI Services**](ai_service/README.md): Python AI agent development
- [**Database Design**](datastore/README.md): Multi-database architecture

### **User Guides**
- [**Investigator Guide**](docs/user_guides/investigator.md): Forensic analysis workflows
- [**Executive Guide**](docs/user_guides/executive.md): High-level reporting and compliance
- [**Administrator Guide**](docs/user_guides/administrator.md): System configuration and management

---

## 🆘 **SUPPORT & COMMUNITY**

### **Getting Help**
- **Documentation**: Comprehensive guides and API references
- **Issues**: GitHub issues for bug reports and feature requests
- **Discussions**: GitHub discussions for questions and ideas
- **Discord**: Community chat for real-time support

### **Community Resources**
- **Blog**: Latest updates and case studies
- **Webinars**: Live demonstrations and training sessions
- **Workshops**: Hands-on training and best practices
- **Contributor Program**: Recognition for community contributions

---

## 📄 **LICENSE**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **ACKNOWLEDGMENTS**

- **Open Source Community**: For the amazing tools and libraries
- **Research Partners**: For domain expertise and validation
- **Beta Users**: For feedback and real-world testing
- **Contributors**: For code, documentation, and community support

---

## 🔄 **DOCUMENT SYNCHRONIZATION**

### **Three Sources of Truth**
This project maintains three master documents that must be kept synchronized:

1. **[MASTER_ARCHITECTURE.md](MASTER_ARCHITECTURE.md)** - System architecture and design decisions
2. **[README.md](README.md)** - This file - Project overview, setup, and usage
3. **[TODO_MASTER.md](TODO_MASTER.md)** - Implementation roadmap and tasks

### **Synchronization Rules**
- **Architecture Changes**: Must be documented in MASTER_ARCHITECTURE.md
- **Project Updates**: Must be reflected in README.md
- **Implementation Changes**: Must be tracked in TODO_MASTER.md
- **Cross-References**: All documents must maintain consistent cross-references
- **Version Control**: All changes must be committed with appropriate documentation updates

---

**Built with ❤️ for the forensic investigation and compliance community**

*Transform your reconciliation and fraud detection workflows with AI-powered intelligence and forensic-grade evidence management.*

**For implementation details, see [TODO_MASTER.md](TODO_MASTER.md)**
**For architecture details, see [MASTER_ARCHITECTURE.md](MASTER_ARCHITECTURE.md)**
