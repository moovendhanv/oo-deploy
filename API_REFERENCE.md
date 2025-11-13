# Ouroboros Compute API Reference

Comprehensive API documentation for the Ouroboros Compute API (oo-compute-api). This REST API provides access to AI workflow orchestration, graph execution, and MCP server integration.

**Base URL**: `http://localhost:5001`

**API Version**: v2.x (PostgreSQL-based)

---

## Table of Contents

1. [Health & Service Endpoints](#health--service-endpoints)
2. [Graph Service Endpoints](#graph-service-endpoints)
3. [Workflow Service Endpoints](#workflow-service-endpoints)
4. [Execution Endpoints](#execution-endpoints)
5. [Step Execution Endpoints](#step-execution-endpoints)
6. [MCP Server Endpoints](#mcp-server-endpoints)
7. [Workspace Endpoints](#workspace-endpoints)
8. [WebSocket Events](#websocket-events)
9. [Data Models](#data-models)
10. [Error Handling](#error-handling)

---

## Health & Service Endpoints

### GET /health

Basic health check for the API service.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T12:00:00Z"
}
```

### GET /service/health

Comprehensive service health check including database connectivity and system status.

**Response**:
```json
{
  "status": "healthy",
  "database": {
    "postgresql": "connected",
    "connection_pool": {
      "size": 20,
      "available": 18,
      "in_use": 2
    }
  },
  "services": {
    "workflow_engine": "running",
    "mcp_servers": "available"
  },
  "uptime": 3600,
  "timestamp": "2025-10-24T12:00:00Z"
}
```

### GET /service/metrics

Service performance metrics and statistics.

**Response**:
```json
{
  "requests": {
    "total": 1234,
    "per_minute": 20.5,
    "by_endpoint": {
      "/workflows": 500,
      "/executions": 300
    }
  },
  "executions": {
    "active": 5,
    "completed_today": 42,
    "failed_today": 3,
    "avg_duration_seconds": 145.2
  },
  "resources": {
    "cpu_usage": 45.2,
    "memory_usage_mb": 2048,
    "disk_usage_gb": 15.3
  }
}
```

---

## Graph Service Endpoints

Graphs are low-level execution units in Ouroboros, representing LangGraph state machines.

### GET /graphs

List all available graphs with optional filtering.

**Query Parameters**:
- `category` (optional): Filter by category
- `tags` (optional): Comma-separated tags
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "graphs": [
    {
      "name": "ASIS",
      "display_name": "Agent-Step Intelligence System",
      "description": "Core agentic workflow with step-level planning",
      "category": "core",
      "tags": ["agent", "planning", "execution"],
      "version": "2.1.0",
      "input_schema": {
        "type": "object",
        "properties": {
          "task": {"type": "string"},
          "context": {"type": "object"}
        }
      }
    }
  ],
  "total": 12,
  "limit": 100,
  "offset": 0
}
```

### GET /graphs/{graph_name}

Get detailed information about a specific graph.

**Path Parameters**:
- `graph_name`: Name of the graph

**Response**:
```json
{
  "name": "ASIS",
  "display_name": "Agent-Step Intelligence System",
  "description": "Core agentic workflow with step-level planning and execution",
  "category": "core",
  "tags": ["agent", "planning", "execution"],
  "version": "2.1.0",
  "nodes": [
    {"name": "planner", "type": "llm_node"},
    {"name": "executor", "type": "tool_node"}
  ],
  "edges": [
    {"from": "planner", "to": "executor"}
  ],
  "input_schema": {
    "type": "object",
    "required": ["task"],
    "properties": {
      "task": {"type": "string", "description": "Task to execute"},
      "context": {"type": "object"}
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "result": {"type": "string"},
      "metadata": {"type": "object"}
    }
  }
}
```

### POST /graphs/{graph_name}/execute

Execute a specific graph with provided input.

**Path Parameters**:
- `graph_name`: Name of the graph to execute

**Request Body**:
```json
{
  "input": {
    "task": "Create a business plan for a coffee shop",
    "context": {
      "industry": "food_service",
      "budget": 50000
    }
  },
  "config": {
    "enable_tracing": true,
    "max_retries": 3,
    "timeout": 3600
  },
  "async": false
}
```

**Response** (synchronous):
```json
{
  "execution_id": "exec_abc123",
  "graph_name": "ASIS",
  "status": "completed",
  "result": {
    "output": "Business plan generated...",
    "metadata": {
      "nodes_executed": 12,
      "llm_calls": 5,
      "duration_seconds": 45.2
    }
  },
  "started_at": "2025-10-24T12:00:00Z",
  "completed_at": "2025-10-24T12:00:45Z"
}
```

**Response** (asynchronous):
```json
{
  "execution_id": "exec_abc123",
  "status": "initializing",
  "message": "Graph execution started. Use /executions/{execution_id} to track progress."
}
```

### POST /execute

Generic graph execution endpoint (legacy compatibility).

**Request Body**:
```json
{
  "graph_name": "ASIS",
  "input": {
    "task": "Analyze market trends"
  }
}
```

---

## Workflow Service Endpoints

Workflows are higher-level constructs that combine multiple graphs with strategy definitions.

### GET /workflows

List all workflows with filtering and search capabilities.

**Query Parameters**:
- `category` (optional): Filter by category
- `tags` (optional): Comma-separated tags
- `search` (optional): Search in workflow names and descriptions
- `status` (optional): Filter by status (active, archived, draft)
- `limit` (optional): Maximum number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `include_archived` (optional): Include archived workflows (default: false)

**Response**:
```json
{
  "workflows": [
    {
      "slug": "business-plan-optimization",
      "name": "Business Plan Optimization",
      "description": "Comprehensive business plan analysis and optimization",
      "category": "business",
      "tags": ["business", "planning", "optimization"],
      "version": "1.2.0",
      "status": "active",
      "graph_name": "ASIS",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-10-20T14:30:00Z",
      "execution_count": 142,
      "avg_duration_seconds": 180.5,
      "success_rate": 0.95
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

### POST /workflows

Upload a new workflow to the system.

**Request Body** (multipart/form-data or JSON):
```json
{
  "name": "Market Research Workflow",
  "slug": "market-research",
  "description": "Comprehensive market research and analysis",
  "category": "research",
  "tags": ["market", "research", "analysis"],
  "graph_name": "ASIS",
  "strategy_definition": {
    "steps": [
      {
        "step_number": 1,
        "name": "Market Analysis",
        "description": "Analyze market conditions"
      }
    ]
  },
  "input_fields": [
    {
      "name": "industry",
      "type": "string",
      "required": true,
      "description": "Target industry"
    }
  ]
}
```

**Response**:
```json
{
  "workflow_id": "wf_xyz789",
  "slug": "market-research",
  "status": "created",
  "message": "Workflow created successfully"
}
```

### GET /workflows/{workflow_slug}

Get detailed information about a specific workflow.

**Path Parameters**:
- `workflow_slug`: Unique slug identifier for the workflow

**Response**:
```json
{
  "workflow_id": "wf_xyz789",
  "slug": "business-plan-optimization",
  "name": "Business Plan Optimization",
  "description": "Comprehensive business plan analysis and optimization",
  "category": "business",
  "tags": ["business", "planning", "optimization"],
  "version": "1.2.0",
  "status": "active",
  "graph_name": "ASIS",
  "strategy_definition": {
    "steps": [
      {
        "step_number": 1,
        "name": "Initial Analysis",
        "description": "Analyze current business plan",
        "estimated_duration": 120
      }
    ]
  },
  "input_fields": [
    {
      "name": "business_type",
      "type": "string",
      "required": true,
      "description": "Type of business"
    }
  ],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-10-20T14:30:00Z",
  "statistics": {
    "total_executions": 142,
    "successful_executions": 135,
    "failed_executions": 7,
    "avg_duration_seconds": 180.5,
    "success_rate": 0.95
  }
}
```

### POST /workflows/{workflow_slug}/execute

Execute a workflow with provided inputs.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Request Body**:
```json
{
  "inputs": {
    "business_type": "coffee_shop",
    "location": "urban",
    "budget": 50000
  },
  "config": {
    "enable_tracing": true,
    "enable_checkpoints": true,
    "notify_on_completion": false,
    "timeout_per_step": 5400
  },
  "metadata": {
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
```

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "workflow_slug": "business-plan-optimization",
  "status": "initializing",
  "started_at": "2025-10-24T12:00:00Z",
  "estimated_completion": "2025-10-24T12:15:00Z",
  "websocket_url": "/executions?execution_id=wfexec_abc123",
  "message": "Workflow execution started. Use /executions/{execution_id} to track progress."
}
```

### POST /workflows/{workflow_slug}/execute/stream

Execute a workflow with Server-Sent Events (SSE) streaming.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Request Body**: Same as `/execute`

**Response**: Server-Sent Events stream
```
event: execution_started
data: {"execution_id": "wfexec_abc123", "status": "initializing"}

event: step_started
data: {"step_number": 1, "step_name": "Initial Analysis"}

event: llm_call
data: {"model": "gpt-4", "tokens": 150}

event: step_completed
data: {"step_number": 1, "duration": 45.2}

event: execution_completed
data: {"status": "completed", "duration": 180.5}
```

### GET /workflows/{workflow_slug}/input-fields

Get the input schema for a workflow.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Response**:
```json
{
  "workflow_slug": "business-plan-optimization",
  "input_fields": [
    {
      "name": "business_type",
      "type": "string",
      "required": true,
      "description": "Type of business",
      "validation": {
        "enum": ["retail", "service", "manufacturing", "technology"]
      },
      "default": null
    },
    {
      "name": "budget",
      "type": "number",
      "required": true,
      "description": "Available budget in USD",
      "validation": {
        "minimum": 1000,
        "maximum": 10000000
      }
    },
    {
      "name": "location",
      "type": "string",
      "required": false,
      "description": "Business location",
      "default": "urban"
    }
  ],
  "json_schema": {
    "type": "object",
    "required": ["business_type", "budget"],
    "properties": {
      "business_type": {"type": "string", "enum": ["retail", "service", "manufacturing", "technology"]},
      "budget": {"type": "number", "minimum": 1000, "maximum": 10000000},
      "location": {"type": "string", "default": "urban"}
    }
  }
}
```

### POST /workflows/{workflow_slug}/validate-input

Validate workflow input before execution.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Request Body**:
```json
{
  "inputs": {
    "business_type": "coffee_shop",
    "budget": 50000
  }
}
```

**Response** (valid):
```json
{
  "valid": true,
  "message": "Input validation successful"
}
```

**Response** (invalid):
```json
{
  "valid": false,
  "errors": [
    {
      "field": "business_type",
      "message": "Value 'coffee_shop' is not in allowed enum: [retail, service, manufacturing, technology]"
    },
    {
      "field": "location",
      "message": "Required field is missing"
    }
  ]
}
```

### GET /workflows/{workflow_slug}/steps

Get the strategy steps for a workflow.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Response**:
```json
{
  "workflow_slug": "business-plan-optimization",
  "total_steps": 5,
  "steps": [
    {
      "step_number": 1,
      "name": "Initial Analysis",
      "description": "Analyze current business plan and identify key areas",
      "estimated_duration": 120,
      "dependencies": [],
      "output_schema": {
        "type": "object",
        "properties": {
          "analysis_results": {"type": "string"}
        }
      }
    },
    {
      "step_number": 2,
      "name": "Market Research",
      "description": "Research market conditions and competitors",
      "estimated_duration": 180,
      "dependencies": [1],
      "requires_mcp": ["perplexity", "apify"]
    }
  ]
}
```

### GET /workflows/{workflow_slug}/steps/{step_number}

Get details about a specific workflow step.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier
- `step_number`: Step number (1-indexed)

**Response**:
```json
{
  "step_number": 1,
  "name": "Initial Analysis",
  "description": "Analyze current business plan and identify key areas for improvement",
  "estimated_duration": 120,
  "dependencies": [],
  "parallel_execution": false,
  "retry_policy": {
    "max_retries": 3,
    "retry_delay": 10,
    "exponential_backoff": true
  },
  "mcp_tools": [],
  "input_schema": {
    "type": "object",
    "properties": {
      "business_plan": {"type": "string"}
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "analysis_results": {"type": "string"},
      "recommendations": {"type": "array"}
    }
  }
}
```

### GET /workflows/{workflow_slug}/misc

Get miscellaneous workflow data (metadata, configurations, etc.).

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Response**:
```json
{
  "workflow_slug": "business-plan-optimization",
  "misc_data": {
    "author": "Ouroboros Team",
    "created_by": "admin",
    "license": "proprietary",
    "documentation_url": "https://docs.example.com/workflows/business-plan",
    "examples": [
      {
        "name": "Coffee Shop Example",
        "inputs": {
          "business_type": "retail",
          "budget": 50000
        }
      }
    ],
    "changelog": [
      {
        "version": "1.2.0",
        "date": "2025-10-20",
        "changes": "Added market validation step"
      }
    ]
  }
}
```

### GET /workflows/{workflow_slug}/analytics

Get analytics and performance metrics for a workflow.

**Path Parameters**:
- `workflow_slug`: Workflow slug identifier

**Query Parameters**:
- `start_date` (optional): Start date for analytics (ISO 8601)
- `end_date` (optional): End date for analytics (ISO 8601)
- `granularity` (optional): Data granularity (hour, day, week, month)

**Response**:
```json
{
  "workflow_slug": "business-plan-optimization",
  "time_range": {
    "start": "2025-10-01T00:00:00Z",
    "end": "2025-10-24T23:59:59Z"
  },
  "summary": {
    "total_executions": 142,
    "successful_executions": 135,
    "failed_executions": 7,
    "avg_duration_seconds": 180.5,
    "median_duration_seconds": 165.0,
    "p95_duration_seconds": 320.0,
    "success_rate": 0.951
  },
  "step_analytics": [
    {
      "step_number": 1,
      "step_name": "Initial Analysis",
      "avg_duration": 45.2,
      "failure_rate": 0.02,
      "retry_count_avg": 0.1
    }
  ],
  "cost_breakdown": {
    "total_cost_usd": 142.50,
    "llm_costs": {
      "gpt-4": 120.00,
      "claude-3": 22.50
    }
  },
  "timeline": [
    {
      "date": "2025-10-24",
      "executions": 8,
      "successes": 7,
      "failures": 1,
      "avg_duration": 175.3
    }
  ]
}
```

### GET /workflows/checkpoints

List all available checkpoints across workflows.

**Query Parameters**:
- `workflow_slug` (optional): Filter by workflow
- `execution_id` (optional): Filter by execution
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset

**Response**:
```json
{
  "checkpoints": [
    {
      "checkpoint_id": "cp_abc123",
      "execution_id": "wfexec_xyz789",
      "workflow_slug": "business-plan-optimization",
      "step_number": 3,
      "step_name": "Financial Analysis",
      "created_at": "2025-10-24T12:05:30Z",
      "state_snapshot": {
        "completed_steps": [1, 2],
        "current_step": 3,
        "intermediate_results": {}
      },
      "resumable": true
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

---

## Execution Endpoints

Track and manage workflow/graph executions.

### GET /executions/{execution_id}

Get the current status and progress of an execution.

**Path Parameters**:
- `execution_id`: Execution ID

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "workflow_slug": "business-plan-optimization",
  "status": "running",
  "progress": {
    "current_step": 2,
    "total_steps": 5,
    "percentage": 40
  },
  "started_at": "2025-10-24T12:00:00Z",
  "estimated_completion": "2025-10-24T12:15:00Z",
  "elapsed_seconds": 120,
  "metadata": {
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
```

### GET /executions/{execution_id}/info

Get detailed information about an execution including results.

**Path Parameters**:
- `execution_id`: Execution ID

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "workflow_slug": "business-plan-optimization",
  "status": "completed",
  "started_at": "2025-10-24T12:00:00Z",
  "completed_at": "2025-10-24T12:15:00Z",
  "duration_seconds": 900,
  "inputs": {
    "business_type": "retail",
    "budget": 50000
  },
  "outputs": {
    "business_plan": "Comprehensive business plan...",
    "financial_projections": {...}
  },
  "steps_completed": [
    {
      "step_number": 1,
      "step_name": "Initial Analysis",
      "status": "completed",
      "duration_seconds": 120,
      "started_at": "2025-10-24T12:00:00Z",
      "completed_at": "2025-10-24T12:02:00Z"
    }
  ],
  "llm_calls": {
    "total": 15,
    "by_model": {
      "gpt-4": 10,
      "claude-3": 5
    },
    "total_tokens": 45000,
    "estimated_cost_usd": 1.25
  },
  "checkpoints": [
    {
      "checkpoint_id": "cp_abc123",
      "step_number": 3,
      "created_at": "2025-10-24T12:05:30Z"
    }
  ]
}
```

### GET /executions/{execution_id}/node-executions

Get all node executions within a workflow/graph execution.

**Path Parameters**:
- `execution_id`: Execution ID

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "node_executions": [
    {
      "node_execution_id": "ne_xyz789",
      "node_name": "planner",
      "node_type": "llm_node",
      "status": "completed",
      "started_at": "2025-10-24T12:00:00Z",
      "completed_at": "2025-10-24T12:00:15Z",
      "duration_seconds": 15,
      "input": {...},
      "output": {...},
      "error": null
    }
  ],
  "total_nodes": 12,
  "completed_nodes": 12,
  "failed_nodes": 0
}
```

### GET /executions/{execution_id}/events

Get execution events and logs.

**Path Parameters**:
- `execution_id`: Execution ID

**Query Parameters**:
- `event_type` (optional): Filter by event type
- `limit` (optional): Maximum events (default: 100)
- `offset` (optional): Pagination offset

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "events": [
    {
      "event_id": "evt_abc123",
      "event_type": "execution_started",
      "timestamp": "2025-10-24T12:00:00Z",
      "data": {
        "workflow_slug": "business-plan-optimization"
      }
    },
    {
      "event_id": "evt_abc124",
      "event_type": "step_started",
      "timestamp": "2025-10-24T12:00:01Z",
      "data": {
        "step_number": 1,
        "step_name": "Initial Analysis"
      }
    },
    {
      "event_id": "evt_abc125",
      "event_type": "llm_call_completed",
      "timestamp": "2025-10-24T12:00:15Z",
      "data": {
        "model": "gpt-4",
        "tokens": 150,
        "cost": 0.003
      }
    }
  ],
  "total": 45,
  "limit": 100,
  "offset": 0
}
```

### POST /executions/{execution_id}/cancel

Cancel a running execution.

**Path Parameters**:
- `execution_id`: Execution ID

**Request Body** (optional):
```json
{
  "reason": "User requested cancellation",
  "graceful": true
}
```

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "status": "cancelling",
  "message": "Execution cancellation initiated. Current step will complete before stopping.",
  "cancelled_at": "2025-10-24T12:10:00Z"
}
```

### GET /executions/{execution_id}/steps

Get step-level execution details (new step execution tracking).

**Path Parameters**:
- `execution_id`: Execution ID

**Response**:
```json
{
  "execution_id": "wfexec_abc123",
  "step_executions": [
    {
      "step_execution_id": "stepexec_abc123",
      "step_number": 1,
      "step_name": "Initial Analysis",
      "status": "completed",
      "started_at": "2025-10-24T12:00:00Z",
      "completed_at": "2025-10-24T12:02:00Z",
      "duration_seconds": 120,
      "retry_count": 0,
      "llm_calls": 3,
      "tokens_used": 5000,
      "cost_usd": 0.15,
      "output": {...}
    },
    {
      "step_execution_id": "stepexec_abc124",
      "step_number": 2,
      "step_name": "Market Research",
      "status": "running",
      "started_at": "2025-10-24T12:02:00Z",
      "estimated_completion": "2025-10-24T12:05:00Z",
      "retry_count": 0
    }
  ],
  "total_steps": 5,
  "completed_steps": 1,
  "failed_steps": 0,
  "running_steps": 1
}
```

### GET /executions

List all active executions.

**Query Parameters**:
- `workflow_slug` (optional): Filter by workflow
- `status` (optional): Filter by status
- `limit` (optional): Maximum results (default: 50)

**Response**:
```json
{
  "executions": [
    {
      "execution_id": "wfexec_abc123",
      "workflow_slug": "business-plan-optimization",
      "status": "running",
      "started_at": "2025-10-24T12:00:00Z",
      "progress": 40
    }
  ],
  "total": 5,
  "limit": 50
}
```

---

## Step Execution Endpoints

Manage and monitor step-level executions (new in v2.x).

### GET /step-executions/{step_execution_id}

Get detailed information about a specific step execution.

**Path Parameters**:
- `step_execution_id`: Step execution ID

**Response**:
```json
{
  "step_execution_id": "stepexec_abc123",
  "execution_id": "wfexec_xyz789",
  "workflow_slug": "business-plan-optimization",
  "step_number": 2,
  "step_name": "Market Research",
  "status": "completed",
  "started_at": "2025-10-24T12:02:00Z",
  "completed_at": "2025-10-24T12:05:00Z",
  "duration_seconds": 180,
  "timeout_seconds": 5400,
  "retry_count": 1,
  "max_retries": 3,
  "parallel_execution": false,
  "input": {
    "industry": "food_service",
    "location": "urban"
  },
  "output": {
    "market_analysis": "Detailed market research results...",
    "competitors": [...]
  },
  "llm_calls": [
    {
      "model": "gpt-4",
      "tokens": 2500,
      "cost_usd": 0.075,
      "latency_ms": 3500
    }
  ],
  "mcp_tools_used": ["perplexity-search", "apify-scraper"],
  "metrics": {
    "total_tokens": 2500,
    "total_cost_usd": 0.075,
    "avg_latency_ms": 3500
  },
  "error": null
}
```

### POST /step-executions/{step_execution_id}/cancel

Cancel a running step execution.

**Path Parameters**:
- `step_execution_id`: Step execution ID

**Response**:
```json
{
  "step_execution_id": "stepexec_abc123",
  "status": "cancelled",
  "message": "Step execution cancelled successfully",
  "cancelled_at": "2025-10-24T12:04:00Z"
}
```

### GET /step-executions

List all active step executions.

**Query Parameters**:
- `execution_id` (optional): Filter by parent execution
- `workflow_slug` (optional): Filter by workflow
- `status` (optional): Filter by status
- `limit` (optional): Maximum results

**Response**:
```json
{
  "step_executions": [
    {
      "step_execution_id": "stepexec_abc123",
      "execution_id": "wfexec_xyz789",
      "step_number": 2,
      "step_name": "Market Research",
      "status": "running",
      "started_at": "2025-10-24T12:02:00Z",
      "elapsed_seconds": 120
    }
  ],
  "total": 8,
  "limit": 50
}
```

### GET /metrics/step-executions

Get aggregated metrics for step executions.

**Query Parameters**:
- `workflow_slug` (optional): Filter by workflow
- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)

**Response**:
```json
{
  "summary": {
    "total_step_executions": 1250,
    "successful": 1180,
    "failed": 70,
    "success_rate": 0.944,
    "avg_duration_seconds": 145.2,
    "avg_retry_count": 0.15
  },
  "by_workflow": {
    "business-plan-optimization": {
      "total": 500,
      "avg_duration": 180.5,
      "success_rate": 0.95
    }
  },
  "by_step": [
    {
      "step_name": "Market Research",
      "total_executions": 250,
      "avg_duration": 180.0,
      "failure_rate": 0.08,
      "avg_cost_usd": 0.15
    }
  ],
  "slow_steps": [
    {
      "step_name": "Financial Modeling",
      "avg_duration": 450.0,
      "slowest_execution": 720.0
    }
  ]
}
```

---

## MCP Server Endpoints

Model Context Protocol (MCP) server integration for extended tool capabilities.

### GET /mcp-servers

List all available MCP servers.

**Response**:
```json
{
  "mcp_servers": [
    {
      "name": "perplexity",
      "display_name": "Perplexity Search",
      "description": "AI-powered search and research",
      "status": "available",
      "version": "1.0.0",
      "capabilities": ["search", "summarize"],
      "tools_count": 3
    },
    {
      "name": "apify",
      "display_name": "Apify Web Scraper",
      "description": "Web scraping and automation",
      "status": "available",
      "version": "2.1.0",
      "capabilities": ["scrape", "crawl", "extract"],
      "tools_count": 8
    }
  ],
  "total": 5,
  "available": 4,
  "unavailable": 1
}
```

### GET /mcp-servers/tools

Get all tools available from MCP servers.

**Query Parameters**:
- `server` (optional): Filter by MCP server name
- `capability` (optional): Filter by capability

**Response**:
```json
{
  "tools": [
    {
      "tool_id": "perplexity-search",
      "server": "perplexity",
      "name": "search",
      "display_name": "Perplexity Search",
      "description": "Search the web using Perplexity AI",
      "input_schema": {
        "type": "object",
        "required": ["query"],
        "properties": {
          "query": {"type": "string"},
          "max_results": {"type": "number", "default": 5}
        }
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "results": {"type": "array"}
        }
      }
    }
  ],
  "total": 25
}
```

### GET /mcp-servers/status

Check the status of all MCP servers.

**Response**:
```json
{
  "overall_status": "healthy",
  "servers": [
    {
      "name": "perplexity",
      "status": "available",
      "last_check": "2025-10-24T12:00:00Z",
      "response_time_ms": 150,
      "error": null
    },
    {
      "name": "context7",
      "status": "unavailable",
      "last_check": "2025-10-24T12:00:00Z",
      "response_time_ms": null,
      "error": "Connection timeout"
    }
  ],
  "timestamp": "2025-10-24T12:00:00Z"
}
```

### GET /mcp-servers/settings

Get MCP server configuration settings.

**Response**:
```json
{
  "mcp_base_path": "/app/oo_mcp_servers",
  "mcp_settings_file": "/app/oo_mcp_servers/mcp_settings.json",
  "servers": [
    {
      "name": "perplexity",
      "enabled": true,
      "config": {
        "api_key_env": "PERPLEXITY_API_KEY",
        "timeout": 30,
        "max_retries": 3
      }
    }
  ]
}
```

### POST /mcp-tools/execute

Execute a specific MCP tool directly.

**Request Body**:
```json
{
  "tool_id": "perplexity-search",
  "input": {
    "query": "latest AI trends 2025",
    "max_results": 5
  },
  "config": {
    "timeout": 30,
    "retry_on_failure": true
  }
}
```

**Response**:
```json
{
  "tool_id": "perplexity-search",
  "status": "completed",
  "output": {
    "results": [
      {
        "title": "AI Trends 2025",
        "url": "https://example.com/ai-trends",
        "summary": "Latest developments in AI..."
      }
    ]
  },
  "execution_time_ms": 2500,
  "cost_usd": 0.05
}
```

---

## Workspace Endpoints

Manage execution workspaces and file artifacts.

### GET /workspace/directories

Get information about workspace directories.

**Response**:
```json
{
  "workspace_root": "/tmp/workspace",
  "directories": [
    {
      "name": "Working_Directory",
      "path": "/tmp/workspace/Working_Directory",
      "size_mb": 125.5,
      "file_count": 48
    },
    {
      "name": "Longterm_Directory",
      "path": "/tmp/workspace/Longterm_Directory",
      "size_mb": 512.3,
      "file_count": 203
    }
  ],
  "total_size_mb": 637.8
}
```

### POST /workspace/directories

Create or manage workspace directories.

**Request Body**:
```json
{
  "action": "create",
  "directory_name": "Custom_Workspace",
  "parent_path": "/tmp/workspace"
}
```

**Response**:
```json
{
  "status": "created",
  "directory_path": "/tmp/workspace/Custom_Workspace",
  "message": "Directory created successfully"
}
```

### GET /service/workspaces

List all workspaces.

**Response**:
```json
{
  "workspaces": [
    {
      "name": "default",
      "path": "/tmp/workspace",
      "created_at": "2025-10-01T00:00:00Z",
      "size_mb": 637.8,
      "execution_count": 142
    }
  ]
}
```

### GET /service/workspaces/{name}/checkpoints

Get checkpoints for a specific workspace.

**Path Parameters**:
- `name`: Workspace name

**Response**:
```json
{
  "workspace": "default",
  "checkpoints": [
    {
      "checkpoint_id": "cp_abc123",
      "execution_id": "wfexec_xyz789",
      "created_at": "2025-10-24T12:05:30Z",
      "size_kb": 45.2
    }
  ],
  "total": 25
}
```

### GET /service/workspaces/{name}/files

List files in a workspace.

**Path Parameters**:
- `name`: Workspace name

**Query Parameters**:
- `directory` (optional): Subdirectory path
- `extension` (optional): Filter by file extension
- `limit` (optional): Maximum results

**Response**:
```json
{
  "workspace": "default",
  "directory": "/tmp/workspace/Working_Directory",
  "files": [
    {
      "name": "business_plan.pdf",
      "path": "/tmp/workspace/Working_Directory/business_plan.pdf",
      "size_bytes": 524288,
      "created_at": "2025-10-24T12:05:00Z",
      "modified_at": "2025-10-24T12:05:00Z",
      "mime_type": "application/pdf"
    }
  ],
  "total": 48
}
```

### GET /service/workspaces/{name}/files/content

Get the content of a specific file.

**Path Parameters**:
- `name`: Workspace name

**Query Parameters**:
- `file_path`: Relative file path within workspace

**Response**: File content (content type varies)

### GET /service/workspace-config

Get workspace configuration settings.

**Response**:
```json
{
  "system_workspace": "/tmp/workspace",
  "output_dir": "/tmp/ouroboros_output",
  "working_directory_name": "Working_Directory",
  "longterm_directory_name": "Longterm_Directory",
  "max_workspace_size_mb": 10240,
  "auto_cleanup_enabled": true,
  "cleanup_after_days": 30
}
```

---

## WebSocket Events

Real-time event streaming for workflow executions.

**Namespace**: `/executions`

**Connection URL**: `ws://localhost:5001/socket.io/?EIO=4&transport=websocket`

### Connection

**Client → Server**:
```json
{
  "event": "join_execution",
  "data": {
    "execution_id": "wfexec_abc123"
  }
}
```

**Server → Client**:
```json
{
  "event": "connected",
  "data": {
    "execution_id": "wfexec_abc123",
    "status": "running"
  }
}
```

### Event Types

#### execution_started
```json
{
  "event": "execution_started",
  "data": {
    "execution_id": "wfexec_abc123",
    "workflow_slug": "business-plan-optimization",
    "started_at": "2025-10-24T12:00:00Z"
  }
}
```

#### step_started
```json
{
  "event": "step_started",
  "data": {
    "execution_id": "wfexec_abc123",
    "step_number": 1,
    "step_name": "Initial Analysis",
    "started_at": "2025-10-24T12:00:01Z"
  }
}
```

#### node_started
```json
{
  "event": "node_started",
  "data": {
    "execution_id": "wfexec_abc123",
    "node_name": "planner",
    "node_type": "llm_node"
  }
}
```

#### llm_call_started
```json
{
  "event": "llm_call_started",
  "data": {
    "execution_id": "wfexec_abc123",
    "model": "gpt-4",
    "prompt_tokens": 150
  }
}
```

#### llm_call_completed
```json
{
  "event": "llm_call_completed",
  "data": {
    "execution_id": "wfexec_abc123",
    "model": "gpt-4",
    "prompt_tokens": 150,
    "completion_tokens": 300,
    "total_tokens": 450,
    "cost_usd": 0.0135,
    "latency_ms": 2500
  }
}
```

#### step_completed
```json
{
  "event": "step_completed",
  "data": {
    "execution_id": "wfexec_abc123",
    "step_number": 1,
    "step_name": "Initial Analysis",
    "status": "completed",
    "duration_seconds": 120,
    "completed_at": "2025-10-24T12:02:01Z"
  }
}
```

#### execution_progress
```json
{
  "event": "execution_progress",
  "data": {
    "execution_id": "wfexec_abc123",
    "progress_percentage": 40,
    "completed_steps": 2,
    "total_steps": 5,
    "estimated_completion": "2025-10-24T12:15:00Z"
  }
}
```

#### execution_completed
```json
{
  "event": "execution_completed",
  "data": {
    "execution_id": "wfexec_abc123",
    "status": "completed",
    "duration_seconds": 900,
    "completed_at": "2025-10-24T12:15:00Z",
    "result_summary": {
      "output_files": 3,
      "llm_calls": 15,
      "total_cost_usd": 1.25
    }
  }
}
```

#### execution_failed
```json
{
  "event": "execution_failed",
  "data": {
    "execution_id": "wfexec_abc123",
    "status": "failed",
    "error": {
      "type": "StepExecutionError",
      "message": "Step 3 failed: API rate limit exceeded",
      "step_number": 3,
      "retry_count": 3
    },
    "failed_at": "2025-10-24T12:10:00Z"
  }
}
```

#### interactive_prompt
```json
{
  "event": "interactive_prompt",
  "data": {
    "execution_id": "wfexec_abc123",
    "prompt_id": "prompt_xyz789",
    "message": "Please confirm the financial projections before continuing",
    "prompt_type": "confirmation",
    "options": ["approve", "reject", "modify"]
  }
}
```

### Client Commands

#### submit_response (interactive mode)
```json
{
  "event": "submit_response",
  "data": {
    "prompt_id": "prompt_xyz789",
    "response": "approve"
  }
}
```

#### leave_execution
```json
{
  "event": "leave_execution",
  "data": {
    "execution_id": "wfexec_abc123"
  }
}
```

---

## Data Models

### Execution Status

- `initializing` - Execution is being set up
- `running` - Execution is in progress
- `completed` - Execution finished successfully
- `failed` - Execution failed
- `cancelled` - Execution was cancelled by user
- `paused` - Execution is paused (waiting for input)

### Step Execution Status

- `pending` - Step is waiting to start
- `running` - Step is currently executing
- `completed` - Step finished successfully
- `failed` - Step failed
- `retrying` - Step is being retried after failure
- `skipped` - Step was skipped
- `cancelled` - Step was cancelled

### Workflow Categories

- `business` - Business planning and optimization
- `research` - Research and analysis
- `education` - Educational content generation
- `creative` - Creative writing and content
- `technical` - Technical documentation and code
- `custom` - User-defined workflows

### Error Types

- `ValidationError` - Input validation failed
- `ExecutionError` - Error during execution
- `TimeoutError` - Execution exceeded timeout
- `RateLimitError` - API rate limit exceeded
- `ResourceError` - Insufficient resources
- `ConfigurationError` - Configuration issue
- `NetworkError` - Network connectivity issue

---

## Error Handling

All API endpoints return consistent error responses:

### Standard Error Response

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid input: field 'budget' must be greater than 0",
    "code": "ERR_VALIDATION_001",
    "details": {
      "field": "budget",
      "value": -1000,
      "constraint": "minimum: 0"
    },
    "timestamp": "2025-10-24T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted (async operation)
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Common Error Codes

- `ERR_VALIDATION_001` - Input validation failed
- `ERR_EXEC_001` - Execution initialization failed
- `ERR_EXEC_002` - Execution timeout
- `ERR_EXEC_003` - Execution cancelled
- `ERR_DB_001` - Database connection error
- `ERR_DB_002` - Database query error
- `ERR_MCP_001` - MCP server unavailable
- `ERR_MCP_002` - MCP tool execution failed
- `ERR_AUTH_001` - Authentication failed
- `ERR_RATE_001` - Rate limit exceeded

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Global limit**: 1000 requests per hour per IP
- **Execution limit**: 50 concurrent executions per account
- **MCP tool limit**: 100 tool calls per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1635432000
```

---

## Authentication

Currently, the API operates in trusted network mode. Future versions will support:

- API key authentication
- OAuth 2.0
- JWT tokens

---

## Changelog

### v2.1.0 (Current)
- Added step execution tracking endpoints
- Enhanced PostgreSQL integration
- Added step-level metrics and analytics
- Improved WebSocket events for real-time updates
- Added checkpoint management endpoints

### v2.0.0
- Migrated from MongoDB to PostgreSQL
- Removed Redis dependency
- Added MCP server integration
- Introduced workflow versioning
- Enhanced error handling and logging

### v1.2.0 (Legacy)
- MongoDB-based workflows
- Basic graph execution
- Redis caching support

---

## Support

For issues, questions, or feature requests, please refer to the main repository documentation.

**API Version**: 2.1.0
**Last Updated**: 2025-10-24
