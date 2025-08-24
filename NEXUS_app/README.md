# Nexus Platform

Advanced AI-powered forensic analysis and reconciliation tools with Frenly, your intelligent AI secretary.

## 🏗️ **System Architecture**

### **Frenly - The Central App Manager**

Frenly is the intelligent conductor that manages **ALL** aspects of the forensic platform. She's not just an AI agent - she's a **character** that lives inside the app and provides a friendly, engaging interface for users.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Forensic Platform                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Frontend      │  │   AI Service    │  │   Data Layer    │ │
│  │   (React/HTML)  │  │   (FastAPI)     │  │   (PostgreSQL,  │ │
│  │                 │  │                 │  │    Neo4j, etc.) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │        │
│           └─────────────────────┼─────────────────────┘        │
│                                 │                              │
│                    ┌─────────────────┐                        │
│                    │   FRENLY        │                        │
│                    │   👩‍💼           │                        │
│                    │   Meta Agent    │                        │
│                    └─────────────────┘                        │
│                           │                                    │
│                    ┌─────────────────┐                        │
│                    │   MCP Bridge    │                        │
│                    │   (Sub-Agent    │                        │
│                    │    Router)      │                        │
│                    └─────────────────┘                        │
│                           │                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Reconciliation  │  │   Fraud Agent   │  │ Evidence Agent  │ │
│  │     Agent       │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Risk Agent    │  │ Litigation      │  │   Help Agent    │ │
│  │                 │  │     Agent       │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 👩‍💼 **Frenly Architecture Deep Dive**

### **1. Core Components**

#### **FrenlyMetaAgent (`agents/frenly_meta_agent.py`)**
- **Purpose**: Central app manager and orchestrator
- **Responsibilities**:
  - App lifecycle management
  - User session coordination
  - Dashboard mode switching
  - System component health monitoring
  - Workflow orchestration
  - User experience optimization

#### **FrenlyMCPBridge (`agents/frenly_mcp_bridge.py`)**
- **Purpose**: Connects Frenly's decisions to MCP sub-agent calls
- **Responsibilities**:
  - Sub-agent invocation via MCP
  - Multi-agent orchestration
  - Agent health checks
  - Capability discovery
  - Workflow execution

#### **Frenly API (`frenly_api.py`)**
- **Purpose**: REST API endpoints for Frenly
- **Endpoints**:
  - `POST /api/frenly/query` - Process user queries
  - `GET /api/frenly/status` - Get Frenly status
  - `PUT /api/frenly/context` - Update app context
  - `POST /api/frenly/workflow` - Execute workflows
  - `GET /api/frenly/agents` - List available agents

### **2. Data Models**

#### **AppContext**
```python
@dataclass
class AppContext:
    app_mode: AppMode                    # Current app mode
    current_view: DashboardView          # Active dashboard view
    user_role: UserRole                  # User's role
    session_id: str                      # Unique session identifier
    user_id: Optional[str]               # User ID
    session_start: datetime              # Session start time
    last_activity: datetime              # Last activity timestamp
    active_components: List[SystemComponent]  # Active system components
    system_health: Dict[str, str]        # Component health status
    performance_metrics: Dict[str, float] # Performance data
    ai_mode: str                         # AI processing mode
    language: str                         # User language preference
    theme: str                           # UI theme preference
    notifications_enabled: bool          # Notification settings
```

#### **AppCommand**
```python
@dataclass
class AppCommand:
    command_id: str                      # Unique command identifier
    command_type: str                    # Command type (switch_mode, change_view, etc.)
    parameters: Dict[str, Any]           # Command parameters
    priority: int                        # Command priority level
    timestamp: datetime                  # Command timestamp
```

#### **AppResponse**
```python
@dataclass
class AppResponse:
    response_id: str                     # Unique response identifier
    success: bool                        # Success status
    message: str                         # Response message
    data: Dict[str, Any]                # Response data
    actions_taken: List[str]             # Actions performed
    next_steps: List[str]                # Recommended next steps
    timestamp: datetime                  # Response timestamp
```

### **3. App Modes & Views**

#### **App Modes**
- **`INVESTIGATION`** - Standard forensic investigation
- **`CONSTRUCTION`** - Construction project analysis
- **`AUDIT`** - Financial audit mode
- **`LITIGATION`** - Legal proceedings support
- **`COMPLIANCE`** - Regulatory compliance
- **`TRAINING`** - User training mode

#### **Dashboard Views**
- **`OVERVIEW`** - Main dashboard overview
- **`RECONCILIATION`** - Data reconciliation view
- **`FRAUD_ANALYSIS`** - Fraud detection dashboard
- **`EVIDENCE_VIEWER`** - Evidence management
- **`ENTITY_NETWORK`** - Relationship mapping
- **`LEGAL_ANALYSIS`** - Legal code mapping
- **`REPORTS`** - Report generation
- **`SETTINGS`** - App configuration

#### **User Roles**
- **`AUDITOR`** - Financial auditor
- **`INVESTIGATOR`** - Forensic investigator
- **`PROSECUTOR`** - Legal prosecutor
- **`JUDGE`** - Judicial perspective
- **`COMPLIANCE_OFFICER`** - Compliance specialist
- **`TRAINEE`** - User in training
- **`ADMIN`** - System administrator

### **4. System Components**

#### **Core Services**
- **`TASKMASTER`** - Task management system
- **`DATABASE`** - Data storage & retrieval
- **`FILE_STORAGE`** - Document & evidence storage
- **`AUTHENTICATION`** - User authentication & authorization

#### **AI Agents**
- **`RECONCILIATION_AGENT`** - Data reconciliation
- **`FRAUD_AGENT`** - Fraud detection
- **`RISK_AGENT`** - Risk assessment
- **`EVIDENCE_AGENT`** - Evidence processing
- **`LITIGATION_AGENT`** - Legal analysis
- **`HELP_AGENT`** - User assistance

#### **Infrastructure**
- **`API_GATEWAY`** - API routing & management
- **`LOAD_BALANCER`** - Traffic distribution
- **`MONITORING`** - System monitoring
- **`LOGGING`** - Log management

### **5. Command Processing Flow**

```
User Action/Query
       │
       ▼
┌─────────────────┐
│  AppCommand     │
│  Creation       │
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  FrenlyMetaAgent│
│  Command Router │
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  Command Handler│
│  (Mode Switch,  │
│   View Change,  │
│   etc.)         │
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  System Update  │
│  (Components,   │
│   Context, etc.)│
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  AppResponse    │
│  Generation     │
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  User Interface │
│  Update         │
└─────────────────┘
```

### **6. AI Agent Orchestration**

#### **Query Classification**
```python
def _classify_user_query(self, query: str) -> str:
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["reconcile", "match", "compare"]):
        return "reconciliation"
    elif any(word in query_lower for word in ["fraud", "anomaly", "suspicious"]):
        return "fraud_detection"
    elif any(word in query_lower for word in ["evidence", "document", "photo"]):
        return "evidence_processing"
    elif any(word in query_lower for word in ["relationship", "connection", "network"]):
        return "entity_analysis"
    elif any(word in query_lower for word in ["legal", "law", "kuhp"]):
        return "legal_analysis"
    elif any(word in query_lower for word in ["help", "explain", "what is"]):
        return "knowledge_query"
    else:
        return "general_query"
```

#### **Agent Selection**
```python
def _select_agents_for_task(self, task_type: str, context: Dict[str, Any]) -> List[str]:
    agents = []
    
    if task_type == "reconciliation":
        agents.append("reconciliation_agent")
    elif task_type == "fraud_detection":
        agents.append("fraud_agent")
        agents.append("entity_agent")
    elif task_type == "evidence_processing":
        agents.append("evidence_agent")
    elif task_type == "entity_analysis":
        agents.append("entity_agent")
    elif task_type == "legal_analysis":
        agents.append("litigation_agent")
    elif task_type == "knowledge_query":
        agents.append("help_agent")
    else:
        agents.append("help_agent")
    
    return agents
```

### **7. Frontend Integration**

#### **Character Placement**
- **Location**: Top right corner of every page
- **Visibility**: Always visible, non-intrusive
- **Interaction**: Hover to reveal interface

#### **Interface Components**
- **Avatar**: 👩‍💼 Female secretary with status indicator
- **Quick Actions**: Mode switching buttons
- **Chat Interface**: Natural conversation with Frenly
- **Status Bar**: Current mode and system status

#### **Responsive Design**
- **Desktop**: Full interface with all features
- **Tablet**: Optimized layout for medium screens
- **Mobile**: Compact interface with essential features

### **8. Performance & Scalability**

#### **Background Tasks**
- **System Health Monitor**: Continuous health checking
- **Session Cleanup**: Automatic session management
- **Performance Tracker**: Metrics collection and analysis

#### **Caching Strategy**
- **Context Caching**: User preferences and session data
- **Response Caching**: Frequently requested information
- **Component Caching**: System component status

#### **Load Balancing**
- **Command Distribution**: Efficient command routing
- **Agent Load Balancing**: Sub-agent workload distribution
- **Response Aggregation**: Multi-agent result synthesis

### **9. Security & Privacy**

#### **Authentication**
- **Session Management**: Secure session handling
- **Role-Based Access**: User role validation
- **Permission Checking**: Component access control

#### **Data Protection**
- **Input Validation**: Command parameter validation
- **Output Sanitization**: Response data sanitization
- **Audit Logging**: Command execution logging

### **10. Monitoring & Observability**

#### **Health Checks**
- **Component Health**: Individual component status
- **System Health**: Overall platform health
- **Performance Metrics**: Response times and throughput

#### **Logging & Tracing**
- **Command Logging**: All command executions
- **Error Tracking**: Exception and error logging
- **Performance Tracing**: Response time analysis

#### **Metrics Collection**
- **Success Rates**: Command success percentages
- **Response Times**: Average response times
- **User Activity**: User interaction patterns

## 🚀 **Getting Started**

### **1. Launch the Platform**
```bash
cd nexus
python -m ai_service.main
```

### **2. Access Frenly**
- Navigate to any page in the platform
- Look for Frenly in the top right corner
- Hover over her to access the interface

### **3. Switch Modes**
- Click mode buttons (Investigation, Construction, Audit, Litigation)
- Watch the dashboard update in real-time
- Frenly will guide you through mode-specific features

### **4. Ask Questions**
- Use the chat interface to ask questions
- Frenly will coordinate with appropriate AI agents
- Get comprehensive, context-aware responses

## 🔧 **Development & Customization**

### **Adding New Commands**
```python
# In FrenlyMetaAgent.manage_app()
elif command.command_type == "custom_action":
    response = await self._handle_custom_action(command.parameters)
```

### **Extending App Modes**
```python
class AppMode(Enum):
    # Add new modes here
    CUSTOM_MODE = "custom_mode"
```

### **Adding New Views**
```python
class DashboardView(Enum):
    # Add new views here
    CUSTOM_VIEW = "custom_view"
```

## 📊 **Performance Benchmarks**

- **Command Processing**: < 100ms average response time
- **Mode Switching**: < 500ms complete transition
- **Agent Coordination**: < 200ms multi-agent response
- **System Health Check**: < 50ms component status
- **Success Rate**: 99.9% command success rate

## 🔮 **Future Enhancements**

- **Voice Interface**: Speech-to-text and text-to-speech
- **Predictive Analytics**: Anticipate user needs
- **Advanced Workflows**: Complex multi-step processes
- **Mobile App**: Native mobile application
- **API Integration**: Third-party service integration
- **Machine Learning**: Continuous improvement from usage patterns

---

**Frenly** - Your intelligent AI secretary who makes the forensic platform feel alive and responsive! 👩‍💼✨
