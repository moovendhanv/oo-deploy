# Ouroboros Interface

Lightweight Python client library for interacting with the Ouroboros Compute API.

## Features

- Clean, intuitive API for all Ouroboros endpoints
- Automatic retry logic and error handling
- Type hints for better IDE support
- Zero dependencies on main Ouroboros codebase
- Production-ready and obfuscated for deployment

## Installation

The interface is included with oo_deploy. No separate installation required.

Required dependencies:
```bash
pip install requests
```

## Quick Start

```python
from oo_interface import OuroborosClient

# Initialize the client
client = OuroborosClient('http://localhost:5001')

# Check API health
if client.check_health():
    print("API is healthy!")

# List available workflows
workflows = client.list_workflows()
for workflow in workflows:
    print(f"- {workflow['name']}: {workflow['description']}")

# Execute a workflow
result = client.execute_workflow(
    workflow_slug='business-plan-optimization',
    inputs={
        'business_type': 'retail',
        'budget': 50000,
        'location': 'urban'
    }
)

# Check execution status
execution_id = result['execution_id']
status = client.get_execution_status(execution_id)
print(f"Status: {status['status']}")

# Wait for completion
final_result = client.wait_for_execution(execution_id)
print(f"Completed in {final_result['duration_seconds']} seconds")
```

## Core Operations

### Health & Status

```python
# Basic health check
healthy = client.check_health()

# Detailed service health
health_info = client.get_service_health()

# Performance metrics
metrics = client.get_service_metrics()
```

### Workflow Management

```python
# List workflows with filters
workflows = client.list_workflows(
    category='business',
    status='active',
    limit=20
)

# Get workflow details
workflow = client.get_workflow('business-plan-optimization')

# Get input schema
schema = client.get_workflow_input_schema('business-plan-optimization')

# Validate inputs before execution
validation = client.validate_workflow_input(
    'business-plan-optimization',
    {'business_type': 'retail', 'budget': 50000}
)

if validation['valid']:
    # Execute the workflow
    result = client.execute_workflow(
        'business-plan-optimization',
        inputs={'business_type': 'retail', 'budget': 50000},
        config={
            'enable_tracing': True,
            'enable_checkpoints': True
        },
        metadata={'user_id': 'user_123'}
    )
```

### Execution Tracking

```python
# Get execution status
status = client.get_execution_status('wfexec_abc123')

# Get detailed execution info
info = client.get_execution_info('wfexec_abc123')

# Get execution events
events = client.get_execution_events('wfexec_abc123', event_type='llm_call')

# Get step-level details
steps = client.get_execution_steps('wfexec_abc123')

# Cancel execution
client.cancel_execution('wfexec_abc123', reason='User requested')

# List all active executions
executions = client.list_executions(workflow_slug='business-plan-optimization')
```

### Graph Execution

```python
# List available graphs
graphs = client.list_graphs()

# Get graph details
graph = client.get_graph('ASIS')

# Execute a graph
result = client.execute_graph(
    'ASIS',
    input_data={'task': 'Analyze market trends', 'context': {}},
    config={'enable_tracing': True}
)
```

### Step Execution Tracking

```python
# Get step execution details
step = client.get_step_execution('stepexec_abc123')

# Cancel a step
client.cancel_step_execution('stepexec_abc123')

# Get aggregated step metrics
metrics = client.get_step_execution_metrics(
    workflow_slug='business-plan-optimization',
    start_date='2025-10-01T00:00:00Z',
    end_date='2025-10-24T23:59:59Z'
)
```

### MCP Server Operations

```python
# List MCP servers
servers = client.list_mcp_servers()

# Get available MCP tools
tools = client.get_mcp_tools(server='perplexity')

# Check MCP server status
status = client.get_mcp_status()

# Execute an MCP tool
result = client.execute_mcp_tool(
    'perplexity-search',
    input_data={'query': 'latest AI trends', 'max_results': 5}
)
```

### Workspace Management

```python
# Get workspace info
workspace = client.get_workspace_info()

# List workspace files
files = client.list_workspace_files(
    workspace_name='default',
    directory='Working_Directory',
    extension='pdf'
)

# Get workspace configuration
config = client.get_workspace_config()
```

### Analytics

```python
# Get workflow analytics
analytics = client.get_workflow_analytics(
    'business-plan-optimization',
    start_date='2025-10-01T00:00:00Z',
    end_date='2025-10-24T23:59:59Z',
    granularity='day'
)

print(f"Success rate: {analytics['summary']['success_rate']}")
print(f"Average duration: {analytics['summary']['avg_duration_seconds']}s")
print(f"Total cost: ${analytics['cost_breakdown']['total_cost_usd']}")
```

## Error Handling

The client raises `APIError` exceptions for API-related errors:

```python
from oo_interface import OuroborosClient, APIError

client = OuroborosClient('http://localhost:5001')

try:
    result = client.execute_workflow(
        'invalid-workflow',
        inputs={'invalid': 'data'}
    )
except APIError as e:
    print(f"Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Details: {e.details}")
```

## Advanced Usage

### Custom Configuration

```python
# Initialize with custom settings
client = OuroborosClient(
    api_base_url='http://my-server:5001',
    timeout=600,  # 10 minutes
    max_retries=5
)
```

### Waiting for Execution Completion

```python
# Execute and wait for completion
result = client.execute_workflow('my-workflow', inputs={...})
execution_id = result['execution_id']

try:
    final_result = client.wait_for_execution(
        execution_id,
        poll_interval=10,  # Check every 10 seconds
        max_wait=3600      # Wait up to 1 hour
    )
    print("Execution completed!")
    print(final_result)
except APIError as e:
    print(f"Execution failed: {e.message}")
```

### Polling Execution Progress

```python
import time

execution_id = 'wfexec_abc123'

while True:
    status = client.get_execution_status(execution_id)

    if status['status'] in ['completed', 'failed', 'cancelled']:
        break

    progress = status.get('progress', {})
    print(f"Progress: {progress.get('percentage', 0)}% "
          f"({progress.get('current_step', 0)}/{progress.get('total_steps', 0)})")

    time.sleep(5)

# Get final results
info = client.get_execution_info(execution_id)
```

## API Reference

See [API_REFERENCE.md](../API_REFERENCE.md) for complete API documentation.

## Architecture

The interface is designed to be:

- **Standalone**: No dependencies on the main Ouroboros codebase
- **Lightweight**: Only requires the `requests` library
- **Obfuscated**: Suitable for deployment without revealing implementation details
- **Production-ready**: Includes retry logic, error handling, and timeouts
- **Type-safe**: Uses type hints for better IDE support

## Version

Current version: 2.1.0

Compatible with Ouroboros Compute API v2.x (PostgreSQL-based)
