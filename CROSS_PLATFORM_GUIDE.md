# Cross-Platform Deployment Guide

This guide provides platform-specific instructions for deploying Ouroboros on Windows, macOS, and Linux.

## 🖥️ Windows Deployment

### Prerequisites
- **Windows 10/11** (version 1903 or higher)
- **Docker Desktop for Windows** with WSL2 backend
- **WSL2** (Windows Subsystem for Linux)

### Installation Steps

#### 1. Enable WSL2
```powershell
# Run in PowerShell as Administrator
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart Windows
# Then set WSL2 as default
wsl --set-default-version 2
```

#### 2. Install Docker Desktop
1. Download from https://docker.com/products/docker-desktop
2. Install with WSL2 backend enabled
3. Start Docker Desktop
4. Verify: `docker --version` in PowerShell

#### 3. Deploy Ouroboros
```powershell
# Navigate to deployment directory
cd path\to\oo_deploy

# Copy and edit environment file
copy .env.example .env
notepad .env  # Add your API keys

# Start deployment
docker compose -f docker-compose-deploy.yml up -d

# Verify deployment
curl http://localhost:5001/health
```

### Windows-Specific Troubleshooting

#### Docker Desktop Issues
```powershell
# Check Docker status
docker info

# Restart Docker Desktop service
net stop com.docker.service
net start com.docker.service

# Update WSL if needed
wsl --update
```

#### File Path Issues
- Use forward slashes in .env file paths
- Avoid spaces in directory names
- Use full paths if relative paths fail

#### Network Issues
```powershell
# Check Windows Firewall
# Allow Docker Desktop through Windows Defender Firewall
# Or temporarily disable for testing:
netsh advfirewall set allprofiles state off
```

---

## 🍎 macOS Deployment  

### Prerequisites
- **macOS 12** (Monterey) or higher
- **Docker Desktop for Mac**
- **Intel or Apple Silicon** (both supported)

### Installation Steps

#### 1. Install Docker Desktop
```bash
# Download from https://docker.com/products/docker-desktop
# Or install via Homebrew
brew install --cask docker

# Start Docker Desktop
open -a Docker

# Verify installation
docker --version
docker compose version
```

#### 2. Deploy Ouroboros
```bash
# Navigate to deployment directory
cd /path/to/oo_deploy

# Copy and edit environment file  
cp .env.example .env
nano .env  # Add your API keys

# Start deployment
docker compose -f docker-compose-deploy.yml up -d

# Verify deployment
curl http://localhost:5001/health
```

### macOS-Specific Troubleshooting

#### Apple Silicon (M1/M2/M3) Issues
```bash
# Verify platform compatibility
docker buildx ls

# Force AMD64 if needed (not recommended)
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Check architecture
uname -m  # Should show "arm64" on Apple Silicon
```

#### Permission Issues
```bash
# Fix Docker socket permissions
sudo chown $(whoami) /var/run/docker.sock

# Fix file permissions in deployment directory
chmod -R 755 ./workspace ./logs
```

#### Memory Issues
```bash
# Increase Docker Desktop memory
# Docker Desktop → Preferences → Resources → Advanced
# Set Memory to at least 8GB

# Check current allocation
docker system info | grep Memory
```

---

## 🐧 Linux Deployment

### Prerequisites
- **Ubuntu 20.04+**, **CentOS 8+**, **Debian 11+**, or similar
- **Docker Engine** 
- **Docker Compose** (v2.0+)

### Installation Steps

#### 1. Install Docker Engine
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. Install Docker Compose
```bash
# Install Docker Compose v2
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker compose version
```

#### 3. Deploy Ouroboros
```bash
# Navigate to deployment directory
cd /path/to/oo_deploy

# Copy and edit environment file
cp .env.example .env
nano .env  # Add your API keys

# Start deployment
docker compose -f docker-compose-deploy.yml up -d

# Verify deployment
curl http://localhost:5001/health
```

### Linux-Specific Troubleshooting

#### Service Management
```bash
# Check Docker service status
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker

# View Docker logs
sudo journalctl -u docker.service
```

#### Firewall Configuration
```bash
# Ubuntu/Debian - Configure UFW
sudo ufw allow 5001/tcp    # Ouroboros API
sudo ufw allow 27017/tcp   # MongoDB (optional, for external access)
sudo ufw allow 6379/tcp    # Redis (optional, for external access)

# CentOS/RHEL - Configure firewalld
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

#### SELinux Issues (CentOS/RHEL)
```bash
# Check SELinux status
sestatus

# If needed, set permissive mode temporarily
sudo setenforce 0

# For permanent SELinux compatibility
sudo setsebool -P container_manage_cgroup on
```

---

## 🚨 Common Cross-Platform Issues

### Port Conflicts
```bash
# Check what's using ports (all platforms)
# Linux/macOS:
lsof -i :5001
lsof -i :27017  
lsof -i :6379

# Windows:
netstat -ano | findstr :5001
netstat -ano | findstr :27017
netstat -ano | findstr :6379
```

### Docker Network Issues
```bash
# Reset Docker networks
docker network prune

# Recreate the network
docker compose -f docker-compose-deploy.yml down
docker compose -f docker-compose-deploy.yml up -d
```

### Container Startup Issues
```bash
# Check container logs (all platforms)
docker compose -f docker-compose-deploy.yml logs oo-compute
docker compose -f docker-compose-deploy.yml logs mongodb  
docker compose -f docker-compose-deploy.yml logs redis

# Check container status
docker compose -f docker-compose-deploy.yml ps

# Restart specific service
docker compose -f docker-compose-deploy.yml restart oo-compute
```

### Resource Constraints
```bash
# Check system resources
docker stats

# Check available disk space
df -h  # Linux/macOS
dir C:\ # Windows

# Clean up Docker resources
docker system prune
docker volume prune
```

---

## 🔧 Platform-Specific Optimizations

### Windows Optimizations
- Enable Hyper-V if available (better than WSL2 for some workloads)
- Use Windows Terminal for better Docker experience
- Configure Windows Defender exclusions for Docker directories
- Use PowerShell 7+ for better cross-platform compatibility

### macOS Optimizations  
- Increase Docker Desktop memory allocation to 8GB+
- Enable "Use gRPC FUSE for file sharing" in Docker preferences
- Use Rosetta 2 emulation for Intel containers on Apple Silicon (automatic)
- Configure Time Machine to exclude Docker directories

### Linux Optimizations
- Use systemd for proper Docker service management
- Configure log rotation for Docker containers
- Use overlay2 storage driver (default on modern systems)
- Set up automatic Docker updates via package manager

---

## 📊 Performance Comparison

| Platform | Startup Time | Memory Usage | CPU Performance | Notes |
|----------|-------------|-------------|----------------|-------|
| **Linux** | ~45s | Lowest | Best | Native performance |
| **macOS Intel** | ~60s | Medium | Good | VM overhead minimal |
| **macOS Apple Silicon** | ~50s | Medium | Very Good | ARM64 native |
| **Windows WSL2** | ~75s | Highest | Good | VM + translation overhead |

### Performance Tips
- **Linux**: Best overall performance, use for production
- **macOS**: Great for development, ARM64 provides better performance than Intel
- **Windows**: Suitable for development and testing, WSL2 adds some overhead

---

## 🆘 Emergency Troubleshooting

### Complete Reset (All Platforms)
```bash
# Stop all services
docker compose -f docker-compose-deploy.yml down

# Remove all containers, networks, and volumes
docker system prune -a --volumes

# Remove deployment-specific volumes
docker volume rm $(docker volume ls -q | grep oo-deploy)

# Restart Docker service
# Linux: sudo systemctl restart docker
# macOS/Windows: Restart Docker Desktop

# Start fresh deployment
docker compose -f docker-compose-deploy.yml up -d
```

### Health Check Commands
```bash
# System health
docker info
docker version
docker compose version

# Service health
curl -f http://localhost:5001/health
docker compose -f docker-compose-deploy.yml exec mongodb mongosh --eval "db.adminCommand('ping')"
docker compose -f docker-compose-deploy.yml exec redis redis-cli ping

# Resource usage
docker stats --no-stream
```

---

## 📞 Platform-Specific Support

### Windows Support Resources
- Docker Desktop Windows Documentation
- WSL2 Troubleshooting Guide
- Windows Container Platform Support

### macOS Support Resources  
- Docker Desktop Mac Documentation
- Apple Silicon Compatibility Guide
- Homebrew Package Management

### Linux Support Resources
- Docker Engine Installation Guide
- Docker Compose Installation Guide  
- Distribution-specific Docker documentation

---

*This guide covers the most common scenarios across Windows, macOS, and Linux. For issues not covered here, consult the main README-DEPLOY.md troubleshooting section.*
