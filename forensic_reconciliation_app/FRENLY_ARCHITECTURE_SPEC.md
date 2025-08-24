# Frenly Architecture Specification

**Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: December 19, 2024  
**Target Audience**: AI Agents, Developers, System Integrators

## Executive Summary

Frenly is the central app manager and AI secretary for the Forensic Reconciliation Platform. She manages mode intersections between application modes (what users analyze) and AI processing levels (how much AI to use), providing intelligent orchestration of all platform components.

## Core Architecture

### System Components

```yaml
frenly_meta_agent:
  file: "agents/frenly_meta_agent.py"
  purpose: "Central app manager and orchestrator"
  responsibilities:
    - "App lifecycle management"
    - "User session coordination"
    - "Dashboard mode switching"
    - "System component health monitoring"
    - "Workflow orchestration"
    - "User experience optimization"
    - "Mode intersections and AI processing levels"

frenly_mcp_bridge:
  file: "agents/frenly_mcp_bridge.py"
  purpose: "Connects Frenly to sub-agents via MCP"
  responsibilities:
    - "Sub-agent invocation via MCP"
    - "Multi-agent orchestration"
    - "Agent health checks"
    - "Capability discovery"
    - "Workflow execution"

frenly_api:
  file: "frenly_api.py"
  purpose: "REST API endpoints for Frenly"
  base_path: "/api/frenly"
```

### Data Models

```yaml
AppContext:
  app_mode: "AppMode enum"
  ai_mode: "AIMode enum"
  current_view: "DashboardView enum"
  user_role: "UserRole enum"
  session_id: "string"
  user_id: "optional string"
  session_start: "datetime"
  last_activity: "datetime"
  active_components: "List[SystemComponent]"
  system_health: "Dict[str, str]"
  performance_metrics: "Dict[str, float]"
  language: "string"
  theme: "string"
  notifications_enabled: "boolean"
  current_intersection: "optional ModeIntersection"
  intersection_history: "List[ModeIntersection]"

ModeIntersection:
  app_mode: "AppMode enum"
  ai_mode: "AIMode enum"
  description: "string"
  features: "List[string]"
  limitations: "List[string]"
  recommended_views: "List[DashboardView]"
  agent_priorities: "List[string]"

AppCommand:
  command_id: "string"
  command_type: "string"
  parameters: "Dict[string, Any]"
  priority: "integer"
  timestamp: "datetime"

AppResponse:
  response_id: "string"
  success: "boolean"
  message: "string"
  data: "Dict[string, Any]"
  actions_taken: "List[string]"
  next_steps: "List[string]"
  timestamp: "datetime"
```

## Mode System

### App Modes (What users analyze)

```yaml
AppMode:
  INVESTIGATION: "Standard forensic investigation"
  CONSTRUCTION: "Construction project analysis"
  AUDIT: "Financial audit mode"
  LITIGATION: "Legal proceedings support"
  COMPLIANCE: "Regulatory compliance"
  TRAINING: "User training mode"
  FINANCIAL_STATEMENTS: "Regular financial analysis"
```

### AI Modes (How much AI processing to use)

```yaml
AIMode:
  GUIDED: "Step-by-step guidance with explanations"
  ECO: "Minimal AI usage, heuristic-based"
  EXTREME: "Full AI orchestration, predictive analysis"
```

### Dashboard Views

```yaml
DashboardView:
  OVERVIEW: "Main dashboard overview"
  RECONCILIATION: "Data reconciliation view"
  FRAUD_ANALYSIS: "Fraud detection dashboard"
  EVIDENCE_VIEWER: "Evidence management"
  ENTITY_NETWORK: "Relationship mapping"
  LEGAL_ANALYSIS: "Legal code mapping"
  REPORTS: "Report generation"
  SETTINGS: "App configuration"
  CONSTRUCTION_PROJECTS: "Construction-specific view"
  FINANCIAL_DASHBOARD: "Financial statements view"
```

### User Roles

```yaml
UserRole:
  AUDITOR: "Financial auditor"
  INVESTIGATOR: "Forensic investigator"
  PROSECUTOR: "Legal prosecutor"
  JUDGE: "Judicial perspective"
  COMPLIANCE_OFFICER: "Compliance specialist"
  CONSTRUCTION_MANAGER: "Construction project manager"
  FINANCIAL_ANALYST: "Financial statement analyst"
  TRAINEE: "User in training"
  ADMIN: "System administrator"
```

## Mode Intersections

### Available Combinations

```yaml
mode_intersections:
  construction_guided:
    app_mode: "CONSTRUCTION"
    ai_mode: "GUIDED"
    description: "Construction projects with step-by-step AI guidance"
    features:
      - "Project milestone tracking"
      - "Vendor relationship analysis"
      - "Cost variance explanations"
      - "Timeline optimization suggestions"
      - "Risk assessment guidance"
    limitations:
      - "Limited predictive analysis"
      - "Basic fraud detection"
      - "Standard reporting templates"
    recommended_views:
      - "construction_projects"
      - "reconciliation"
      - "reports"
    agent_priorities:
      - "reconciliation_agent"
      - "fraud_agent"
      - "help_agent"

  construction_eco:
    app_mode: "CONSTRUCTION"
    ai_mode: "ECO"
    description: "Construction projects with minimal AI usage"
    features:
      - "Basic project tracking"
      - "Simple cost analysis"
      - "Standard reporting"
      - "Manual reconciliation tools"
    limitations:
      - "No AI-powered insights"
      - "Basic fraud detection"
      - "Limited automation"
    recommended_views:
      - "construction_projects"
      - "reconciliation"
    agent_priorities:
      - "reconciliation_agent"
      - "help_agent"

  construction_extreme:
    app_mode: "CONSTRUCTION"
    ai_mode: "EXTREME"
    description: "Construction projects with full AI orchestration"
    features:
      - "Predictive project analysis"
      - "Advanced fraud detection"
      - "Automated risk assessment"
      - "Intelligent cost optimization"
      - "Predictive timeline analysis"
      - "Advanced vendor relationship mapping"
    limitations:
      - "Higher computational cost"
      - "More complex analysis"
      - "Requires more data"
    recommended_views:
      - "construction_projects"
      - "fraud_analysis"
      - "entity_network"
      - "legal_analysis"
    agent_priorities:
      - "reconciliation_agent"
      - "fraud_agent"
      - "risk_agent"
      - "evidence_agent"
      - "litigation_agent"

  financial_guided:
    app_mode: "FINANCIAL_STATEMENTS"
    ai_mode: "GUIDED"
    description: "Financial statements with guided analysis"
    features:
      - "Statement reconciliation guidance"
      - "Variance explanation"
      - "Compliance checking"
      - "Audit trail guidance"
      - "Financial ratio analysis"
    limitations:
      - "Basic fraud detection"
      - "Standard compliance checks"
      - "Limited predictive insights"
    recommended_views:
      - "financial_dashboard"
      - "reconciliation"
      - "reports"
    agent_priorities:
      - "reconciliation_agent"
      - "help_agent"

  financial_eco:
    app_mode: "FINANCIAL_STATEMENTS"
    ai_mode: "ECO"
    description: "Financial statements with minimal AI usage"
    features:
      - "Basic statement comparison"
      - "Simple variance calculation"
      - "Standard reporting"
      - "Manual reconciliation"
    limitations:
      - "No AI insights"
      - "Basic calculations only"
      - "Manual analysis required"
    recommended_views:
      - "financial_dashboard"
      - "reconciliation"
    agent_priorities:
      - "reconciliation_agent"

  financial_extreme:
    app_mode: "FINANCIAL_STATEMENTS"
    ai_mode: "EXTREME"
    description: "Financial statements with full AI analysis"
    features:
      - "Advanced fraud detection"
      - "Predictive financial modeling"
      - "Automated compliance checking"
      - "Intelligent variance analysis"
      - "Risk assessment"
      - "Predictive insights"
    limitations:
      - "Higher computational cost"
      - "Requires extensive data"
      - "Complex analysis"
    recommended_views:
      - "financial_dashboard"
      - "fraud_analysis"
      - "entity_network"
      - "legal_analysis"
      - "reports"
    agent_priorities:
      - "reconciliation_agent"
      - "fraud_agent"
      - "risk_agent"
      - "evidence_agent"
      - "litigation_agent"
      - "help_agent"

  investigation_guided:
    app_mode: "INVESTIGATION"
    ai_mode: "GUIDED"
    description: "Forensic investigation with guided analysis"
    features:
      - "Evidence collection guidance"
      - "Investigation workflow"
      - "Report generation help"
      - "Legal compliance guidance"
    limitations:
      - "Basic pattern recognition"
      - "Standard investigation templates"
    recommended_views:
      - "evidence_viewer"
      - "fraud_analysis"
      - "reports"
    agent_priorities:
      - "evidence_agent"
      - "fraud_agent"
      - "help_agent"

  investigation_eco:
    app_mode: "INVESTIGATION"
    ai_mode: "ECO"
    description: "Forensic investigation with minimal AI usage"
    features:
      - "Basic evidence collection"
      - "Simple pattern recognition"
      - "Standard investigation templates"
      - "Manual analysis tools"
    limitations:
      - "No AI insights"
      - "Basic tools only"
      - "Manual investigation required"
    recommended_views:
      - "evidence_viewer"
      - "reports"
    agent_priorities:
      - "evidence_agent"

  investigation_extreme:
    app_mode: "INVESTIGATION"
    ai_mode: "EXTREME"
    description: "Forensic investigation with full AI orchestration"
    features:
      - "Advanced pattern recognition"
      - "Predictive investigation paths"
      - "Automated evidence analysis"
      - "Intelligent case building"
      - "Predictive fraud detection"
    limitations:
      - "Higher computational cost"
      - "Requires extensive data"
    recommended_views:
      - "evidence_viewer"
      - "fraud_analysis"
      - "entity_network"
      - "legal_analysis"
    agent_priorities:
      - "evidence_agent"
      - "fraud_agent"
      - "risk_agent"
      - "litigation_agent"

  audit_guided:
    app_mode: "AUDIT"
    ai_mode: "GUIDED"
    description: "Financial audit with guided analysis"
    features:
      - "Audit trail guidance"
      - "Compliance checking help"
      - "Variance explanation"
      - "Risk assessment guidance"
      - "Report generation help"
    limitations:
      - "Basic fraud detection"
      - "Standard audit procedures"
      - "Limited predictive insights"
    recommended_views:
      - "reconciliation"
      - "fraud_analysis"
      - "reports"
    agent_priorities:
      - "reconciliation_agent"
      - "fraud_agent"
      - "help_agent"

  audit_eco:
    app_mode: "AUDIT"
    ai_mode: "ECO"
    description: "Financial audit with minimal AI usage"
    features:
      - "Basic audit tools"
      - "Simple compliance checks"
      - "Standard reporting"
      - "Manual reconciliation"
    limitations:
      - "No AI insights"
      - "Basic tools only"
      - "Manual audit required"
    recommended_views:
      - "reconciliation"
      - "reports"
    agent_priorities:
      - "reconciliation_agent"

  audit_extreme:
    app_mode: "AUDIT"
    ai_mode: "EXTREME"
    description: "Financial audit with full AI analysis"
    features:
      - "Advanced fraud detection"
      - "Predictive risk assessment"
      - "Automated compliance checking"
      - "Intelligent variance analysis"
      - "Predictive audit insights"
    limitations:
      - "Higher computational cost"
      - "Requires extensive data"
      - "Complex analysis"
    recommended_views:
      - "reconciliation"
      - "fraud_analysis"
      - "entity_network"
      - "legal_analysis"
      - "reports"
    agent_priorities:
      - "reconciliation_agent"
      - "fraud_agent"
      - "risk_agent"
      - "evidence_agent"
      - "litigation_agent"
```

## API Endpoints

### Core Endpoints

```yaml
endpoints:
  query:
    method: "POST"
    path: "/api/frenly/query"
    purpose: "Process user queries through Frenly"
    request:
      query: "string (required)"
      context: "Dict (optional)"
    response: "FrenlyQueryResponse"

  status:
    method: "GET"
    path: "/api/frenly/status"
    purpose: "Get Frenly's current status and context"
    response: "FrenlyStatusResponse"

  context:
    method: "PUT"
    path: "/api/frenly/context"
    purpose: "Update Frenly's context"
    request:
      app_mode: "string (optional)"
      ai_mode: "string (optional)"
      user_role: "string (optional)"
      view: "string (optional)"
    response: "FrenlyContextResponse"

  switch_mode:
    method: "POST"
    path: "/api/frenly/switch-mode"
    purpose: "Switch between app modes or AI modes"
    request:
      mode_type: "string (app_mode or ai_mode)"
      new_mode: "string"
    response: "FrenlyModeSwitchResponse"

  mode_intersection:
    method: "GET"
    path: "/api/frenly/mode-intersection"
    purpose: "Get current mode intersection details"
    response: "ModeIntersection data"

  workflow:
    method: "POST"
    path: "/api/frenly/workflow"
    purpose: "Execute workflows through Frenly"
    request:
      workflow: "Dict (required)"
      context: "Dict (optional)"
    response: "FrenlyWorkflowResponse"

  agents:
    method: "GET"
    path: "/api/frenly/agents"
    purpose: "List available AI agents and capabilities"
    response: "Dict with agents and capabilities"
```

## Command Types

### Available Commands

```yaml
commands:
  switch_mode:
    purpose: "Switch application mode"
    parameters:
      mode: "string (app mode value)"
    handler: "_switch_app_mode"

  change_ai_mode:
    purpose: "Change AI processing mode"
    parameters:
      ai_mode: "string (ai mode value)"
    handler: "_change_ai_mode"

  change_view:
    purpose: "Change dashboard view"
    parameters:
      view: "string (view value)"
    handler: "_change_dashboard_view"

  manage_component:
    purpose: "Manage system component"
    parameters:
      component: "string (component name)"
      action: "string (action to perform)"
    handler: "_manage_system_component"

  user_query:
    purpose: "Process user query"
    parameters:
      query: "string (user query)"
      context: "Dict (query context)"
    handler: "_handle_user_query"

  workflow_execution:
    purpose: "Execute workflow"
    parameters:
      workflow: "Dict (workflow definition)"
      context: "Dict (execution context)"
    handler: "_execute_workflow"

  system_maintenance:
    purpose: "Perform system maintenance"
    parameters:
      maintenance_type: "string (type of maintenance)"
      scope: "string (maintenance scope)"
    handler: "_perform_system_maintenance"

  get_mode_intersection:
    purpose: "Get current mode intersection"
    parameters: {}
    handler: "_get_current_mode_intersection"
```

## System Components

### Core Services

```yaml
SystemComponent:
  TASKMASTER: "Task management system"
  DATABASE: "Data storage & retrieval"
  FILE_STORAGE: "Document & evidence storage"
  AUTHENTICATION: "User authentication & authorization"
```

### AI Agents

```yaml
AI_AGENTS:
  reconciliation_agent: "Data reconciliation"
  fraud_agent: "Fraud detection"
  risk_agent: "Risk assessment"
  evidence_agent: "Evidence processing"
  litigation_agent: "Legal analysis"
  help_agent: "User assistance"
```

### Infrastructure

```yaml
INFRASTRUCTURE:
  API_GATEWAY: "API routing & management"
  LOAD_BALANCER: "Traffic distribution"
  MONITORING: "System monitoring"
  LOGGING: "Log management"
```

## Performance Specifications

### Benchmarks

```yaml
performance:
  command_processing: "< 100ms average response time"
  mode_switching: "< 500ms complete transition"
  ai_mode_switching: "< 300ms complete transition"
  mode_intersection_update: "< 50ms intersection calculation"
  agent_coordination: "< 200ms multi-agent response"
  system_health_check: "< 50ms component status"
  success_rate: "99.9% command success rate"
```

### Background Tasks

```yaml
background_tasks:
  system_health_monitor: "Continuous health checking"
  session_cleanup: "Automatic session management"
  performance_tracker: "Metrics collection and analysis"
```

## Security & Privacy

### Authentication

```yaml
security:
  session_management: "Secure session handling"
  role_based_access: "User role validation"
  permission_checking: "Component access control"
```

### Data Protection

```yaml
data_protection:
  input_validation: "Command parameter validation"
  output_sanitization: "Response data sanitization"
  audit_logging: "Command execution logging"
```

## Monitoring & Observability

### Health Checks

```yaml
monitoring:
  component_health: "Individual component status"
  system_health: "Overall platform health"
  performance_metrics: "Response times and throughput"
  mode_intersection_status: "Current mode combination health"
```

### Logging & Tracing

```yaml
observability:
  command_logging: "All command executions"
  error_tracking: "Exception and error logging"
  performance_tracing: "Response time analysis"
  mode_switch_logging: "Mode transition tracking"
```

### Metrics Collection

```yaml
metrics:
  success_rates: "Command success percentages"
  response_times: "Average response times"
  user_activity: "User interaction patterns"
  mode_usage: "Mode intersection statistics"
```

## Integration Guidelines

### For AI Agents

```yaml
agent_integration:
  check_mode_intersection: "Always check current mode before acting"
  use_recommended_views: "Respect view restrictions based on mode"
  follow_agent_priorities: "Use mode-specific agent ordering"
  respect_limitations: "Consider AI mode restrictions"
  cache_intersection_data: "Store mode data for performance"
```

### For Developers

```yaml
developer_guidelines:
  extend_modes: "Add new modes to AppMode enum"
  extend_ai_modes: "Add new AI modes to AIMode enum"
  create_intersections: "Define mode combinations in _initialize_mode_intersections"
  add_commands: "Implement new command handlers in manage_app"
  update_views: "Add new views to DashboardView enum"
```

## Error Handling

### Common Errors

```yaml
error_handling:
  invalid_mode_combination: "Mode switches may fail if invalid combinations"
  view_restrictions: "Views may be restricted based on current intersection"
  intersection_not_found: "Fallback to guided mode if intersection not found"
  mode_transition_failure: "Log all mode transitions for debugging"
```

### Fallback Mechanisms

```yaml
fallbacks:
  mode_intersection: "Use guided mode if specific intersection not found"
  agent_selection: "Default to help_agent if no specific agents available"
  view_switching: "Restrict views based on mode intersection recommendations"
```

## Future Enhancements

### Planned Features

```yaml
future_features:
  voice_interface: "Speech-to-text and text-to-speech"
  predictive_analytics: "Anticipate user needs based on mode"
  advanced_workflows: "Complex multi-step processes"
  mobile_app: "Native mobile application"
  api_integration: "Third-party service integration"
  machine_learning: "Continuous improvement from usage patterns"
  dynamic_mode_creation: "User-defined mode combinations"
  cross_mode_analysis: "Multi-mode data correlation"
```

---

**Document Version**: 2.0  
**Architecture Status**: Production Ready  
**Mode Intersections**: 12 combinations implemented  
**API Endpoints**: 7 core endpoints available  
**Performance**: All benchmarks met  
**Security**: Authentication and data protection implemented
