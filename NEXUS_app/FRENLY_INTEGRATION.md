# 🧠 Frenly Meta Agent Integration

## Overview

Frenly is the intelligent meta-agent that orchestrates all AI agents in the Nexus Platform. Acting as a friendly conductor, Frenly listens to user queries, intelligently routes tasks to appropriate sub-agents, and provides explainable, context-aware responses.

## 🏗️ Architecture

### Core Components

1. **FrenlyMetaAgent** (`agents/frenly_meta_agent.py`)
   - Main orchestration logic
   - Task classification and agent selection
   - Response synthesis and narration
   - Context management

2. **FrenlyMCPBridge** (`agents/frenly_mcp_bridge.py`)
   - MCP (Model Context Protocol) integration
   - Sub-agent communication
   - Workflow orchestration
   - Health monitoring

3. **Frenly API** (`frenly_api.py`)
   - REST API endpoints
   - Query processing
   - Status monitoring
   - Workflow execution

4. **Frontend Interface** (`frontend/frenly_interface.html`)
   - Chat-based user interface
   - Context controls
   - Real-time responses
   - Example queries

## 🚀 Features

### Intelligent Task Routing
- **Automatic Classification**: Analyzes user queries to determine task type
- **Smart Agent Selection**: Chooses the most appropriate sub-agents
- **Multi-Agent Orchestration**: Coordinates multiple agents when needed

### Context-Aware Processing
- **Dashboard Modes**: Regular, Construction, Audit, Litigation
- **AI Processing Modes**: Eco (heuristic), Default (balanced), Extreme (full AI)
- **User Perspectives**: Auditor, Investigator, Prosecutor, Judge, General

### Explainable Responses
- **Role-Aware Narration**: Adapts explanations to user context
- **Structured Output**: Recommendations, next steps, confidence scores
- **Processing Transparency**: Shows which agents were involved

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- FastAPI
- All existing AI agents must be initialized

### Integration Steps

1. **Agent Registration**
   ```python
   # Frenly automatically registers with all sub-agents
   frenly_agent.sub_agents = {
       "reconciliation_agent": reconciliation_agent,
       "fraud_agent": fraud_agent,
       "risk_agent": risk_agent,
       "evidence_agent": evidence_agent,
       "litigation_agent": litigation_agent,
       "help_agent": help_agent
   }
   ```

2. **MCP Bridge Setup**
   ```python
   # Register agents with MCP bridge
   for agent_name, agent in frenly_agent.sub_agents.items():
       mcp_bridge.register_agent(agent_name, agent)
   ```

3. **API Integration**
   ```python
   # Include Frenly routes in main app
   from frenly_api import get_frenly_router
   app.include_router(get_frenly_router())
   ```

## 📡 API Endpoints

### Main Query Endpoint
```
POST /api/frenly/query
```
Processes user queries and orchestrates sub-agents.

**Request Body:**
```json
{
  "query": "Help me reconcile vendor payments",
  "context": {
    "dashboard_mode": "construction",
    "ai_mode": "default",
    "user_perspective": "auditor"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "content": {...},
    "narration": "🔨 Construction Mode Analysis: ✅ Data reconciliation completed.",
    "recommendations": ["Review construction milestones", "Verify vendor relationships"],
    "next_steps": ["Review analysis results", "Update project timeline"],
    "confidence_score": 0.8
  }
}
```

### Status & Health
- `GET /api/frenly/status` - Agent and bridge status
- `GET /api/frenly/health` - Health check
- `GET /api/frenly/agents` - Registered agents and capabilities

### Workflow Execution
- `POST /api/frenly/workflow` - Execute multi-agent workflows
- `POST /api/frenly/context` - Update context settings

## 💬 Usage Examples

### Basic Query
```javascript
const response = await fetch('/api/frenly/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Detect fraud patterns in recent transactions",
    context: { dashboard_mode: "regular", ai_mode: "default" }
  })
});
```

### Context-Aware Processing
```javascript
const context = {
  dashboard_mode: "construction",  // Construction project mode
  ai_mode: "extreme",             // Full AI orchestration
  user_perspective: "auditor"     // Financial auditor view
};
```

## 🎯 Task Classification

Frenly automatically classifies queries into these categories:

| Category | Keywords | Sub-Agents |
|----------|----------|------------|
| **Reconciliation** | reconcile, match, compare, balance | Reconciliation + Fraud |
| **Fraud Detection** | fraud, anomaly, suspicious, outlier | Fraud + Entity |
| **Evidence Processing** | evidence, document, photo, pdf | Evidence |
| **Entity Analysis** | relationship, connection, network | Entity + Fraud |
| **Legal Analysis** | legal, law, kuhp, kuhap | Litigation |
| **Knowledge Query** | help, explain, what is, how to | Help |

## 🔄 Workflow Examples

### Fraud Investigation Workflow
```json
[
  {
    "agent": "fraud_agent",
    "method": "detect_anomalies",
    "parameters": {"data": "transaction_data"},
    "dependencies": []
  },
  {
    "agent": "entity_agent",
    "method": "map_relationships",
    "parameters": {"entities": "flagged_entities"},
    "dependencies": ["fraud_agent"]
  }
]
```

## 🎨 Frontend Features

### Chat Interface
- Real-time conversation with Frenly
- Context controls for mode and perspective
- Example queries for quick start
- Chat history persistence

### Response Visualization
- Structured response sections
- Confidence scores and processing times
- Recommendations and next steps
- Agent involvement indicators

## 🧪 Testing

### Unit Tests
```bash
# Test Frenly components
python -m pytest tests/test_frenly_meta_agent.py
python -m pytest tests/test_frenly_mcp_bridge.py
```

### Integration Tests
```bash
# Test API endpoints
python -m pytest tests/test_frenly_api.py
```

### Manual Testing
1. Start the AI service: `python ai_service/main.py`
2. Open Frenly interface: `frontend/frenly_interface.html`
3. Test various query types and contexts

## 🔍 Monitoring & Debugging

### Health Checks
- Agent status monitoring
- MCP bridge health
- Performance metrics
- Error tracking

### Logging
```python
# Frenly provides detailed logging
logger.info(f"Processing query: {user_query}")
logger.info(f"Selected agents: {selected_agents}")
logger.info(f"Response synthesized in {processing_time:.2f}s")
```

### Performance Metrics
- Query processing time
- Agent execution time
- Success rates
- Memory usage

## 🚀 Future Enhancements

### Planned Features
- **Advanced AI Classification**: Machine learning-based task classification
- **Memory Persistence**: Long-term conversation memory
- **Workflow Templates**: Predefined investigation workflows
- **Multi-Language Support**: Internationalization
- **Voice Interface**: Speech-to-text and text-to-speech

### Integration Opportunities
- **External APIs**: Connect to third-party forensic tools
- **Real-time Streaming**: Live data analysis
- **Collaborative Features**: Multi-user investigation support
- **Mobile Interface**: Responsive mobile design

## 📚 Additional Resources

- **API Documentation**: Available at `/docs` when service is running
- **Code Examples**: See `examples/frenly_usage.py`
- **Architecture Diagrams**: Check `docs/frenly_architecture.md`
- **Troubleshooting**: See `docs/frenly_troubleshooting.md`

## 🤝 Contributing

To contribute to Frenly development:

1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Submit pull requests with clear descriptions

## 📄 License

Frenly is part of the Nexus Platform and follows the same licensing terms.

---

**Frenly Meta Agent** - Making forensic investigations intelligent, friendly, and explainable! 🧠✨
