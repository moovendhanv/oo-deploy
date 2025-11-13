u# Ouroboros Deploy - Lightweight Container Deployment

A lightweight deployment repository for quickly spinning up the latest Ouroboros application via Docker Hub and docker-compose. This repo provides instant access to the full Ouroboros compute environment with minimal setup.

## 🚀 Quick Start

Get Ouroboros running in under 2 minutes:

```bash
# 1. Clone this repository
git clone https://github.com/MJ-Ouroboros/oo_deploy.git
cd oo_deploy

# 2. Set up environment variables (copy and edit)
cp .env.example .env
# Edit .env with your API keys (OpenAI, Anthropic, etc.)

# 3. Start the entire Ouroboros environment
docker-compose up -d

# 4. Verify it's running
python run.py --list --type all

# 5. Try an interactive execution
python run.py --interactive
```

The environment includes:
- **oo-compute-api** (port 5001) - Main Ouroboros API
- **MongoDB** (port 27017) - Workflow storage
- **Redis** (port 6379) - Caching and queuing

## 📦 What's Inside the Container

The `oo-compute` container includes the complete **oo-compute-api** - a Flask-based REST API that provides:

- **Graph Management**: Discovery and execution of Ouroboros graphs
- **Workflow Management**: Full lifecycle workflow execution and monitoring
- **MCP Server Integration**: Model Context Protocol server management
- **Service Health Monitoring**: Comprehensive health checks and metrics

The API runs on **port 5001** and automatically discovers available graphs and workflows from the containerized Ouroboros core.

## 🛠️ The run.py Script - Your Primary Interface

The `run.py` script is a powerful unified runner that provides easy interaction with the Ouroboros API. It's your main tool for executing graphs, workflows, and managing the system.

### Key Features

- **Interactive Mode**: Discover and select targets with guided prompts
- **Graph Execution**: Execute Ouroboros graphs with input states
- **Workflow Execution**: Run workflows with dynamic input collection
- **Health Monitoring**: Check API and service health
- **Discovery**: List available graphs and workflows
- **Error Handling**: Comprehensive error reporting and debugging

### Basic Usage

```bash
# Interactive mode - best for beginners
python run.py --interactive

# List all available targets
python run.py --list --type all
python run.py --list --type graphs
python run.py --list --type workflows

# Check system health
python run.py --api-url http://localhost:5001
```

### Graph Execution

Execute Ouroboros graphs with input states:

```bash
# Execute a specific graph with JSON input
python run.py --type graph --name "ASIS" --input input_state.json

# Execute with inline system kwargs
python run.py --type graph --name "complexity_level_1" --system-workspace /path/to/workspace

# Get graph details first
python run.py --type graph --name "ASIS"  # Shows required inputs
```

Example `input_state.json`:
```json
{
  "original_prompt": "Analyze the market potential for AI-powered drone operations in agriculture",
  "system_workspace": "/tmp/workspace",
  "sender": "run.py"
}
```

### Workflow Execution

Execute workflows with dynamic input collection:

```bash
# Dynamic input collection (interactive prompts)
python run.py --type workflow --name "sample_workflow" --dynamic-input

# Provide input variables directly
python run.py --type workflow --name "sample_workflow" --input-vars topic="AI" school_level="college" subject="computer science"

# Use JSON input file
python run.py --type workflow --name "sample_workflow" --input workflow_input.json

# Disable dynamic input (use defaults only)
python run.py --type workflow --name "sample_workflow" --no-dynamic-input
```

Example workflow input:
```json
{
  "topic": "artificial intelligence",
  "school_level": "college", 
  "subject": "computer science",
  "custom_parameter": "value"
}
```

### Advanced Options

```bash
# Enable LangSmith tracing for debugging
python run.py --langsmith --type workflow --name "sample_workflow" --dynamic-input

# Set custom timeout (default: no timeout)
python run.py --timeout 300 --type graph --name "ASIS" --input input.json

# Custom API URL (if running elsewhere)
python run.py --api-url http://remote-host:5001 --list --type all

# Async workflow execution
python run.py --type workflow --name "long_workflow" --async --input workflow_input.json

# Save execution results to file
python run.py --type graph --name "ASIS" --input input.json --output results.json

# Verbose output for debugging
python run.py --verbose --type workflow --name "sample_workflow" --dynamic-input
```

### Interactive Mode Walkthrough

The interactive mode (`--interactive`) provides the best experience for new users:

1. **Discovery**: Automatically finds all available graphs and workflows
2. **Selection**: Displays a numbered list of targets with descriptions
3. **Input Collection**: For workflows, dynamically prompts for required inputs
4. **Validation**: Validates inputs against workflow schemas
5. **Execution**: Runs the selected target and displays results
6. **Error Handling**: Provides clear error messages and suggestions

Example interactive session:
```
🎯 Interactive Mode - Ouroboros Runner
==================================================

🔍 Discovering available targets...
✅ Found 3 graphs
✅ Found 5 workflows

📋 Available Targets (8):
   1. ✅ [GRAPH] ASIS (active) 
   2. ✅ [GRAPH] complexity_level_1 (active)
   3. ✅ [WORKFLOW] 🎯 sample_workflow - Basic workflow example
   4. ✅ [WORKFLOW] market_analysis - AI market analysis workflow
   5. ✅ [WORKFLOW] research_assistant - Research and analysis helper

Select target (1-5): 3

🎯 Selected: sample_workflow (workflow)
🎯 Attempting dynamic input collection for workflow: sample_workflow
================================================================

📋 Found 3 input field(s) to collect:

📝 🔴 REQUIRED Field: topic
   Type: string
   Description: The main topic to analyze
   Example: artificial intelligence

Enter value for 'topic': AI and machine learning

✅ Input validated successfully

📝 🟡 OPTIONAL Field: school_level
   Type: string  
   Description: Educational level for content
   Example: college

Enter value for 'school_level' (press Enter to skip): graduate

✅ Input validated successfully

📋 Collected Input Summary:
========================================
   topic: AI and machine learning
   school_level: graduate

✅ Proceed with these inputs? (y/N): y

🚀 Executing workflow: sample_workflow
✅ Workflow executed successfully!
   Execution ID: exec_12345
   Status: completed
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  
LANGCHAIN_API_KEY=your_langchain_key_here

# Database Configuration
MONGODB_PASSWORD=ouroboros_secure

# Optional: Custom workspace path
SYSTEM_WORKSPACE=/custom/workspace/path
```

### Docker Compose Configuration

The `docker-compose.yml` file configures:

- **oo-compute**: Main API container (oocreate/oo-compute:latest)
- **mongodb**: Workflow storage (oocreate/mongodb:latest) 
- **redis**: Caching and task queuing (oocreate/redis:latest)

Key features:
- **Health checks** for all services
- **Resource limits** to prevent runaway processes
- **Persistent logs** and workspace volumes
- **Automatic restarts** unless stopped
- **Network isolation** with service discovery

## 📡 API Reference

The containerized API provides REST endpoints on **port 5001**:

### Health & Discovery
```bash
# API health check
curl http://localhost:5001/health

# Service health (comprehensive)
curl http://localhost:5001/service/health

# List graphs
curl http://localhost:5001/graphs

# List workflows  
curl http://localhost:5001/workflows

# Get specific graph/workflow info
curl http://localhost:5001/graphs/ASIS
curl http://localhost:5001/workflows/sample_workflow
```

### Graph Execution
```bash
curl -X POST http://localhost:5001/graphs/ASIS/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input_state": {
      "original_prompt": "Analyze market trends in renewable energy",
      "system_workspace": "/tmp/workspace"
    },
    "system_kwargs": {
      "verbose": true
    }
  }'
```

### Workflow Execution
```bash
curl -X POST http://localhost:5001/workflows/sample_workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input_values": {
      "topic": "artificial intelligence",
      "school_level": "college"
    },
    "async_execution": true
  }'
```

### MCP Server Management
```bash
# List MCP servers
curl http://localhost:5001/mcp-servers

# Get MCP tools
curl http://localhost:5001/mcp-servers/tools

# Check MCP server status
curl http://localhost:5001/mcp-servers/status
```

## 🗂️ Directory Structure

```
oo_deploy/
├── docker-compose.yml      # Main deployment configuration
├── .env.example           # Environment variables template
├── run.py                 # Unified execution runner (your main tool)
├── README.md              # This file
├── workspace/             # Mounted workspace for executions
├── logs/                  # Persistent logs from containers
└── config.ini             # Optional API configuration overrides
```

## 🚨 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs oo-compute
docker-compose logs mongodb
docker-compose logs redis

# Restart services
docker-compose restart
```

**API not responding:**
```bash
# Check if API is accessible
curl http://localhost:5001/health

# Check if containers are running
docker ps

# Test with run.py health check
python run.py --api-url http://localhost:5001
```

**run.py connection errors:**
```bash
# Verify correct port (5001, not 5000)
python run.py --api-url http://localhost:5001 --list

# Check Docker containers
docker-compose up -d

# View detailed errors  
python run.py --verbose --interactive
```

**Missing API keys:**
```bash
# Check .env file exists and has required keys
cat .env

# Restart containers after .env changes
docker-compose down && docker-compose up -d
```

### Health Checking

```bash
# Basic health check
python run.py

# Comprehensive service health
curl http://localhost:5001/service/health

# Check specific components
curl http://localhost:5001/service/metrics
```

### Performance Issues

```bash
# Check resource usage
docker stats

# View container logs for errors
docker-compose logs --tail=100 oo-compute

# Check active executions
curl http://localhost:5001/executions
```

## 🔄 Updating

To get the latest Ouroboros version:

```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose down && docker-compose up -d

# Verify update
python run.py --list --type all
```

## 🌐 Production Considerations

For production deployment:

1. **Security**: Add authentication, use secrets management
2. **Monitoring**: Set up logging aggregation and metrics
3. **Scaling**: Configure resource limits appropriately
4. **Backup**: Implement MongoDB backup strategy
5. **SSL**: Add reverse proxy with SSL termination

The included nginx configuration (commented in docker-compose.yml) provides a starting point for production deployments.

## 📚 Additional Resources

- **Docker Hub**: [oocreate/oo-compute](https://hub.docker.com/r/oocreate/oo-compute)
- **Source API**: Check `/Users/wyatthenryblair/Desktop/Projects/Personal/ouroboros/oo-compute-api` for latest source
- **Graph Development**: See ouroboros_core documentation for creating custom graphs
- **Workflow Development**: MongoDB collections contain workflow templates and schemas

## 🤝 Support

For issues with:
- **Deployment**: Check this repository's issues
- **API functionality**: Refer to the oo-compute-api source
- **Graph/Workflow development**: See ouroboros_core documentation

This repository focuses on deployment simplicity - everything you need should work with just `docker-compose up -d` and `python run.py --interactive`.
