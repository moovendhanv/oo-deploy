# Ouroboros Deploy v2.1 Modernization Summary

This document summarizes the major changes made to modernize oo_deploy to align with the current Ouroboros architecture.

## Overview

oo_deploy has been updated from v1.x (MongoDB-based) to v2.1 (PostgreSQL-based) to match the modern Ouroboros stack. This update brings significant improvements in execution tracking, performance monitoring, and API capabilities.

---

## Major Changes

### 1. Database Migration: MongoDB → PostgreSQL

**Removed:**
- MongoDB service and all references
- Redis service (no longer required)
- MongoDB environment variables
- mongo-related configuration

**Added:**
- PostgreSQL 15+ service
- PostgreSQL connection configuration
- Connection pooling settings
- Database propagation controls

**Benefits:**
- Better relational data modeling for workflows
- Enhanced query performance
- ACID transactions for execution tracking
- Better analytics and reporting capabilities

### 2. Enhanced Execution Tracking

**New Features:**
- **Step-level execution tracking**: Monitor individual workflow steps
- **Per-step timeouts**: Fine-grained timeout control (default: 1.5 hours per step)
- **Parallel step execution**: Run up to 5 steps concurrently
- **Step retry mechanism**: Automatic retry with exponential backoff
- **Execution metrics**: Detailed performance tracking

**Configuration Variables:**
```bash
STEP_EXECUTION_TRACKING_ENABLED=true
STEP_EXECUTION_TIMEOUT=5400  # 1.5 hours per step
STEP_EXECUTION_RETRY_COUNT=3
STEP_EXECUTION_PARALLEL_LIMIT=5
WORKFLOW_MONITORING_INTERVAL=10
STEP_PROGRESS_UPDATE_INTERVAL=5
```

### 3. Expanded API Endpoints

The API has been significantly expanded with new endpoints:

#### New Workflow Endpoints:
- `GET /workflows/{slug}/analytics` - Performance analytics
- `GET /workflows/{slug}/steps` - Strategy steps
- `GET /workflows/{slug}/steps/{number}` - Step details
- `POST /workflows/{slug}/validate-input` - Input validation
- `POST /workflows/{slug}/execute/stream` - SSE streaming

#### New Execution Endpoints:
- `GET /executions/{id}/steps` - Step-level tracking
- `GET /executions/{id}/events` - Event logs
- `GET /executions/{id}/node-executions` - Node execution details

#### New Step Execution Endpoints:
- `GET /step-executions/{id}` - Step execution details
- `POST /step-executions/{id}/cancel` - Cancel step
- `GET /step-executions` - List active steps
- `GET /metrics/step-executions` - Aggregated metrics

#### Enhanced MCP Endpoints:
- `GET /mcp-servers/settings` - Configuration details
- `GET /mcp-servers/status` - Server health checks

### 4. New Python Interface Module

A lightweight, standalone Python client library has been added at `oo_interface/`:

**Features:**
- Complete API coverage
- Automatic retry and error handling
- Type hints for IDE support
- Zero dependencies on main Ouroboros codebase
- Production-ready and deployment-friendly

**Usage:**
```python
from oo_interface import OuroborosClient

client = OuroborosClient('http://localhost:5001')

# Execute workflow
result = client.execute_workflow(
    'business-plan-optimization',
    inputs={'business_type': 'retail', 'budget': 50000}
)

# Track execution
status = client.get_execution_status(result['execution_id'])
```

### 5. MCP Server Integration

**New API Keys Required:**
- `PERPLEXITY_API_KEY` - Perplexity AI search
- `APIFY_TOKEN` - Web scraping and automation

**MCP Configuration:**
```ini
[mcp]
mcp_settings_file = ./oo_mcp_servers/mcp_settings.json
mcp_base_path = /app/oo_mcp_servers
perplexity_api_key = <your-key>
apify_token = <your-token>
```

### 6. Resource Allocation Changes

**oo-compute Container:**
- Memory: 4G → 6G (increased for step execution)
- CPU: 2.0 → 3.0 cores (increased for parallel processing)
- Reservations: 1G → 2G memory, 0.5 → 1.0 CPU

**postgresql Container:**
- Memory: 2G limit, 512M reservation
- CPU: 1.0 core limit, 0.25 reservation
- Persistent volume for data

**Removed:**
- redis container (no longer needed)

### 7. Health Check Improvements

**Enhanced Health Checks:**
- Longer start periods (120s for oo-compute to allow database migration)
- Comprehensive service health endpoint
- Database connection pool monitoring
- MCP server status checks

**New Health Endpoints:**
```
GET /health                 - Basic health
GET /service/health         - Comprehensive health
GET /service/metrics        - Performance metrics
```

### 8. Logging Enhancements

**New Log Directories:**
```yaml
volumes:
  - ./logs:/app/logs
  - ./logs/step-execution:/app/logs/step-execution
  - ./logs/workflow-execution:/app/logs/workflow-execution
```

**Log Categories:**
- General application logs
- Step execution logs (detailed per-step tracking)
- Workflow execution logs (workflow-level tracking)

---

## Configuration Changes

### Environment Variables (.env)

**Removed:**
- `MONGODB_PASSWORD`
- `MONGODB_HOST`
- `MONGODB_PORT`
- `REDIS_URL`

**Added:**
- `POSTGRESQL_PASSWORD` (default: ouroboros_secure)
- `POSTGRESQL_HOST` (default: postgresql)
- `POSTGRESQL_PORT` (default: 5432)
- `POSTGRESQL_ENABLE_PROPAGATION` (default: true)
- `POSTGRESQL_ENABLE_STRATEGY_TRACKING` (default: true)
- `PERPLEXITY_API_KEY` (optional, for MCP)
- `APIFY_TOKEN` (optional, for MCP)
- `STEP_EXECUTION_*` variables (execution tracking)

### config.ini Updates

**New Sections:**

```ini
[postgresql]
host = postgresql
port = 5432
database = ouroboros_workflows
username = ouroboros
password = ouroboros_secure
pool_size = 20
max_overflow = 10
ssl_mode = disable

[execution]
step_execution_tracking_enabled = true
step_execution_timeout = 5400
step_execution_retry_count = 3
step_execution_parallel_limit = 5
workflow_monitoring_interval = 10
step_progress_update_interval = 5
```

---

## Migration Guide

### For Existing Users

If you're upgrading from v1.x to v2.1:

1. **Update your .env file:**
   ```bash
   cp .env.example .env.new
   # Copy your API keys from old .env to .env.new
   # Add new variables: POSTGRESQL_PASSWORD, PERPLEXITY_API_KEY, APIFY_TOKEN
   mv .env.new .env
   ```

2. **Update config.ini:**
   ```bash
   # Backup old config
   cp config.ini config.ini.backup
   # Add new [postgresql] and [execution] sections
   ```

3. **Pull new Docker images:**
   ```bash
   docker-compose pull
   ```

4. **Remove old volumes:**
   ```bash
   docker-compose down -v
   # This removes MongoDB and Redis data
   ```

5. **Start with new stack:**
   ```bash
   docker-compose up -d
   ```

6. **Verify migration:**
   ```bash
   python run.py --list --type all
   curl http://localhost:5001/service/health
   ```

### For New Users

Simply follow the Quick Start in README.md. All modernizations are already configured.

---

## Breaking Changes

### Removed Features:
1. MongoDB storage - All workflows now in PostgreSQL
2. Redis caching - No longer used
3. Legacy workflow execution APIs (use new endpoints)

### Changed Behaviors:
1. **Timeouts**: Now per-step (5400s default) instead of workflow-level
2. **Execution tracking**: More granular with step-level details
3. **Health checks**: Longer startup times due to database migrations
4. **Resource usage**: Higher memory/CPU requirements

### API Compatibility:
- Most v1.x endpoints still work
- New endpoints provide enhanced functionality
- Deprecated endpoints marked in API docs

---

## New Capabilities

### 1. Step-Level Execution Control

Monitor and control individual workflow steps:

```python
# Get step executions
steps = client.get_execution_steps('wfexec_abc123')

# Monitor specific step
step = client.get_step_execution('stepexec_xyz789')
print(f"Step {step['step_name']}: {step['status']}")

# Cancel problematic step
client.cancel_step_execution('stepexec_xyz789')
```

### 2. Advanced Analytics

Track workflow performance over time:

```python
analytics = client.get_workflow_analytics(
    'business-plan-optimization',
    start_date='2025-10-01T00:00:00Z',
    end_date='2025-10-24T23:59:59Z'
)

print(f"Success rate: {analytics['summary']['success_rate']}")
print(f"Average cost: ${analytics['cost_breakdown']['total_cost_usd']}")
```

### 3. Real-Time Streaming

Stream execution events via SSE:

```python
# Note: Requires SSE client implementation
result = client.execute_workflow_stream(
    'my-workflow',
    inputs={...}
)
# Events stream in real-time
```

### 4. MCP Tool Integration

Direct MCP tool execution:

```python
# Search with Perplexity
result = client.execute_mcp_tool(
    'perplexity-search',
    input_data={'query': 'latest AI trends', 'max_results': 5}
)
```

### 5. Checkpoint Management

Better checkpoint visibility and management:

```python
# List checkpoints
checkpoints = client.list_checkpoints(
    workflow_slug='business-plan-optimization',
    limit=20
)

# Resume from checkpoint (via workflow execution)
```

---

## Performance Improvements

### Database Query Optimization
- Connection pooling (20 connections)
- Query result caching
- Indexed lookups for executions

### Parallel Processing
- Up to 5 concurrent step executions
- Async workflow execution support
- Non-blocking API calls

### Resource Management
- Higher memory allocation for complex workflows
- Better CPU utilization with parallel steps
- Optimized health check intervals

---

## Documentation

### New Documentation Files:
- `API_REFERENCE.md` - Complete API documentation
- `oo_interface/README.md` - Python client library guide
- `MODERNIZATION_SUMMARY.md` - This file

### Updated Files:
- `.env.example` - New environment variables
- `config.ini` - PostgreSQL and execution configuration
- `docker-compose.yml` - PostgreSQL service, updated resources

---

## Testing the Modernization

### 1. Health Check
```bash
curl http://localhost:5001/service/health
```

Expected response should show PostgreSQL connection.

### 2. List Workflows
```bash
python run.py --list --type workflows
```

Should display workflows from PostgreSQL.

### 3. Execute Workflow
```bash
python run.py --interactive
```

Select a workflow and provide inputs. Monitor step-level progress.

### 4. Check Step Execution
```bash
curl http://localhost:5001/metrics/step-executions
```

View aggregated step execution metrics.

### 5. Python Interface
```python
from oo_interface import OuroborosClient

client = OuroborosClient()
assert client.check_health()
workflows = client.list_workflows()
print(f"Found {len(workflows)} workflows")
```

---

## Troubleshooting

### PostgreSQL Connection Issues

**Symptom:** "Cannot connect to database"

**Solution:**
```bash
# Check PostgreSQL container
docker-compose logs postgresql

# Verify credentials in .env
echo $POSTGRESQL_PASSWORD

# Reset PostgreSQL volume
docker-compose down -v
docker-compose up -d
```

### Missing API Keys

**Symptom:** "API key not configured"

**Solution:**
```bash
# Check .env file
cat .env | grep -E "(OPENAI|ANTHROPIC|LANGCHAIN)"

# Restart containers after updating .env
docker-compose restart oo-compute
```

### Step Execution Timeouts

**Symptom:** Steps timing out too quickly

**Solution:**
```bash
# Increase step timeout in .env
STEP_EXECUTION_TIMEOUT=7200  # 2 hours

# Or in config.ini
[execution]
step_execution_timeout = 7200
```

### High Memory Usage

**Symptom:** Container OOM errors

**Solution:**
```yaml
# Adjust resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # Increase if needed
```

---

## Support & Resources

- **API Reference**: See `API_REFERENCE.md`
- **Python Interface**: See `oo_interface/README.md`
- **Main Documentation**: See `README.md`
- **Deployment Guide**: See `README-DEPLOY.md`

---

## Version History

### v2.1.0 (Current)
- PostgreSQL migration
- Step execution tracking
- Enhanced API endpoints
- Python interface module
- MCP server integration

### v1.2.0 (Legacy)
- MongoDB-based
- Redis caching
- Basic workflow execution

---

**Last Updated:** 2025-10-24
**Compatible With:** Ouroboros v2.1+ (PostgreSQL-based)
