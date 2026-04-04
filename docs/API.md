# Metanoia-QA API Reference

## Base URL
```
http://localhost:8000/v1/metanoia
```

## Endpoints

### Sprint Lifecycle

#### POST /sprint/start
Start a new quality mission.

**Request:**
```json
{
  "sprint_id": "SP-45",
  "sprint_goal": "Implement checkout flow",
  "risk_tolerance": "Low",
  "historical_lookback_sprints": 3
}
```

**Response:**
```json
{
  "sprint_id": "SP-45",
  "status": "context_analysis",
  "context": { ... },
  "test_plan": { ... }
}
```

### Agent Management

#### GET /agents
List all available execution agents.

**Response:**
```json
{
  "agents": [
    {
      "id": "ui-automation",
      "name": "UI Automation Agent",
      "capabilities": ["playwright", "accessibility", "visual"]
    },
    {
      "id": "performance",
      "name": "Performance Agent",
      "capabilities": ["k6", "load-testing", "profiling"]
    },
    {
      "id": "security",
      "name": "Security Agent",
      "capabilities": ["zap", "owasp", "vulnerability-scan"]
    }
  ]
}
```

#### POST /agents/{agent_id}/execute
Execute a specific agent task.

**Request:**
```json
{
  "task_type": "ui-automation",
  "target_url": "https://example.com/checkout",
  "test_scenarios": ["login-flow", "cart-update"],
  "config": {
    "viewport": "1280x720",
    "headless": true
  }
}
```

### Test Results

#### GET /results/{sprint_id}
Get test results for a sprint.

**Response:**
```json
{
  "sprint_id": "SP-45",
  "total_tests": 45,
  "passed": 42,
  "failed": 2,
  "blocked": 1,
  "results": [
    {
      "test_id": "ui-001",
      "agent": "ui-automation",
      "status": "passed",
      "duration_ms": 4521,
      "screenshots": ["path/to/screenshot.png"]
    }
  ]
}
```

### Health Check

#### GET /health
Service health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents": {
    "ui-automation": "ready",
    "performance": "ready",
    "security": "ready"
  },
  "database": "connected",
  "supabase": "connected"
}
```
