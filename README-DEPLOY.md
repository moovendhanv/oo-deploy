# Ouroboros Deployment Guide

Deploy the complete Ouroboros AI Agent Framework with pre-built Docker images for seamless cross-platform deployment.

## 🚀 Quick Start

```bash
# 1. Copy environment template and add your API keys
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# 2. Start Ouroboros
docker-compose up -d

# 3. Verify deployment
python run.py --list --type all

# 4. Try interactive mode
python run.py --interactive

# 5. Direct API access (optional)
# Ouroboros API: http://localhost:5001
# MongoDB: localhost:27017
# Redis: localhost:6379
```

## 📋 Prerequisites

- **Docker Desktop** (Windows/MacOS) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **API Keys** for OpenAI, Anthropic, and LangChain (see Configuration)

### Platform Support

✅ **Windows** - Docker Desktop with WSL2  
✅ **MacOS** - Docker Desktop (Intel and Apple Silicon)  
✅ **Linux** - Docker Engine with Docker Compose  

## 🔧 Configuration

### Required API Keys

Edit `.env` file with your API keys:

```bash
# OpenAI API Key (required for GPT models)
OPENAI_API_KEY=sk-proj-your-actual-openai-key

# Anthropic API Key (required for Claude models)  
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key

# LangChain API Key (required for tracing)
LANGCHAIN_API_KEY=lsv2_pt_your-actual-langchain-key
```

#### Where to Get API Keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **LangChain**: https://smith.langchain.com/

### Optional Configuration

```bash
# Database password (optional, defaults to 'ouroboros_secure')
MONGODB_PASSWORD=your-secure-password

# Application environment (optional, defaults to 'production')
NODE_ENV=production
```

## 🐳 Services

### Ouroboros Compute API
- **Port**: 5001
- **Health Check**: http://localhost:5001/health
- **Image**: `oocreate/oo-compute:latest`
- **Platform**: Multi-platform (AMD64/ARM64)

### MongoDB Database  
- **Port**: 27017
- **Image**: `oocreate/mongodb:latest`
- **Features**: Pre-loaded with 8 workflow templates
- **Platform**: Multi-platform (AMD64/ARM64)

### Redis Cache
- **Port**: 6379  
- **Image**: `oocreate/redis:latest`
- **Configuration**: Optimized for Ouroboros workloads
- **Platform**: Multi-platform (AMD64/ARM64)

## 📁 Directory Structure

```
oo_deploy/
├── docker-compose.yml          # Main deployment file
├── run.py                      # Unified execution runner (primary interface)
├── .env.example               # Environment template
├── .env                       # Your API keys (create this)
├── README.md                  # Main documentation
├── README-DEPLOY.md          # This deployment guide
├── Overview.md               # Technical overview
├── CROSS_PLATFORM_GUIDE.md  # Platform-specific help
├── workspace/                # Ouroboros workspace (auto-created)
└── logs/                    # Application logs (auto-created)
```

## 🔄 Common Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up oo-compute
```

### Monitor Services
```bash
# View logs
docker-compose logs

# View logs for specific service  
docker-compose logs oo-compute

# Follow logs in real-time
docker-compose logs -f
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Test API health
curl http://localhost:5001/health

# Test with run.py (recommended)
python run.py --list --type all

# Test MongoDB connection
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Test Redis connection  
docker-compose exec redis redis-cli ping
```

## 🎯 API Usage

### Health Check
```bash
curl http://localhost:5001/health
```

### List Available Workflows
```bash
curl http://localhost:5001/workflows
```

### Execute a Workflow
```bash
curl -X POST http://localhost:5001/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "sample_workflow",
    "input_data": {
      "research_query": "artificial intelligence trends 2024"
    }
  }'
```

## 📊 Pre-loaded Workflows

The MongoDB image comes with 8 ready-to-use workflow templates:

1. **Business Plan Optimization** - Strategic business analysis
2. **Curriculum Generation** - Educational content creation  
3. **Grant Application** - Proposal development
4. **Growth Strategy** - Business expansion planning
5. **Market Research Simulation** - Competitive analysis
6. **Market Validation** - Product feasibility analysis
7. **Patent Analysis** - IP landscape research
8. **Sample Workflow** - Demo/testing workflow

## 🛠 Troubleshooting

### Service Won't Start
```bash
# Check container logs
docker-compose logs [service-name]

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart [service-name]

# Use run.py for health checking
python run.py --verbose --list --type all
```

### Memory Issues
If you encounter out-of-memory errors:

```bash
# Check current resource limits
docker stats

# Increase Docker Desktop memory allocation:
# Docker Desktop → Settings → Resources → Advanced → Memory
# Recommended: 8GB minimum, 16GB preferred
```

### Platform Issues
For platform-specific troubleshooting, see `CROSS_PLATFORM_GUIDE.md`.

### Port Conflicts
If ports are already in use:

```bash
# Check what's using the ports
lsof -i :5001  # Ouroboros API
lsof -i :27017 # MongoDB
lsof -i :6379  # Redis

# Stop conflicting services or modify ports in docker-compose.yml
```

### API Key Issues
```bash
# Verify API keys are loaded
docker-compose exec oo-compute env | grep API_KEY

# Test with run.py instead
python run.py --verbose --api-url http://localhost:5001

# Common issues:
# - Missing quotes around keys with special characters
# - Trailing spaces in .env file
# - Wrong environment variable names
```

## 🔒 Security Considerations

### Production Deployment
- Change default MongoDB password
- Use strong passwords and rotate regularly  
- Enable Docker secrets for API keys
- Configure firewall rules to limit access
- Use HTTPS reverse proxy (nginx example included but commented)

### API Key Security
- Never commit API keys to version control
- Use environment variables or secret management
- Rotate API keys regularly
- Monitor API usage for anomalies

## 📈 Performance Tuning

### Resource Allocation
Default resource limits:
- **Ouroboros**: 4GB RAM, 2 CPU cores
- **MongoDB**: 2GB RAM, 1 CPU core  
- **Redis**: 512MB RAM, 0.5 CPU cores

Modify in `docker-compose.yml` under `deploy.resources` sections.

### Scaling
```bash
# Scale oo-compute service (if load balancer configured)
docker-compose up --scale oo-compute=3
```

## 📝 Maintenance

### Backup Data
```bash
# Backup MongoDB (if using persistent volumes)
docker-compose exec mongodb mongodump --out /backup

# Export Redis data  
docker-compose exec redis redis-cli BGSAVE
```

### Update Images
```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d

# Verify updates with run.py
python run.py --list --type all
```

### Clean Up
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

## 📞 Support

For issues and support:
- Check troubleshooting section above
- Review `CROSS_PLATFORM_GUIDE.md` for platform-specific help
- Check Docker logs for detailed error messages
- Verify all prerequisites are installed correctly

---

**Version**: v1.0.0  
**Last Updated**: September 2025  
**Compatibility**: Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)
