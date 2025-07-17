# Sistema Mayra - Deployment Guide

This guide provides comprehensive instructions for deploying Sistema Mayra to a DigitalOcean droplet.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Deployment Process](#deployment-process)
- [Post-Deployment](#post-deployment)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Prerequisites

### Local Requirements
- Git installed
- SSH key pair generated
- Access to source code repository
- `.env.prod` file configured

### DigitalOcean Requirements
- DigitalOcean account
- Droplet created with:
  - Ubuntu 22.04 LTS
  - Minimum 2GB RAM (4GB recommended)
  - 50GB SSD storage
  - SSH key added during creation

### External Services
- OpenAI API key with GPT-4 access
- Telegram Bot Token (from @BotFather)
- Domain name (optional but recommended)
- S3-compatible storage for backups (optional)

## Initial Setup

### 1. Create DigitalOcean Droplet

```bash
# Using DigitalOcean CLI (doctl)
doctl compute droplet create sistema-mayra \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys your-ssh-key-id \
  --tag-names production,sistema-mayra
```

### 2. Configure DNS (Optional)

Point your domain to the droplet IP:
- A record: `@` → `your-droplet-ip`
- A record: `www` → `your-droplet-ip`
- A record: `n8n` → `your-droplet-ip` (for n8n subdomain)

### 3. Prepare Environment File

```bash
# Copy and configure production environment
cp .env.prod.example .env.prod

# Edit with your production values
nano .env.prod

# Set proper permissions
chmod 600 .env.prod
```

### 4. Run Droplet Setup

SSH into your droplet and run the setup script:

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Download and run setup script
curl -sSL https://raw.githubusercontent.com/your-repo/sistema-mayra/main/scripts/deployment/setup-droplet.sh | sudo bash
```

Or manually:

```bash
# Clone repository on droplet
git clone https://github.com/your-repo/sistema-mayra.git /tmp/setup
cd /tmp/setup

# Make script executable
chmod +x scripts/deployment/setup-droplet.sh

# Run setup
sudo ./scripts/deployment/setup-droplet.sh
```

## Deployment Process

### 1. First Deployment

From your local machine:

```bash
# Navigate to project directory
cd /path/to/sistema-mayra

# Make deployment script executable
chmod +x scripts/deployment/deploy.sh

# Set deployment variables
export DEPLOY_HOST="your-droplet-ip"
export DEPLOY_USER="root"

# Run deployment
./scripts/deployment/deploy.sh
```

### 2. Deployment Options

The deployment script supports several options:

```bash
# Deploy with SSL setup
SETUP_SSL=true ./scripts/deployment/deploy.sh

# Deploy without n8n
DEPLOY_N8N=false ./scripts/deployment/deploy.sh

# Deploy with custom domain
DOMAIN_NAME="your-domain.com" ./scripts/deployment/deploy.sh
```

### 3. What the Deployment Does

1. **Pre-deployment checks**
   - Verifies SSH connection
   - Checks Docker installation
   - Validates environment

2. **Backup current state**
   - Database backup
   - Redis data backup
   - Configuration files

3. **Deploy application**
   - Syncs code to droplet
   - Builds Docker images
   - Starts containers
   - Runs migrations
   - Seeds initial data

4. **Health checks**
   - Verifies API is responding
   - Checks Telegram bot status
   - Validates all services

5. **Optional steps**
   - SSL certificate setup
   - n8n workflow deployment
   - Post-deployment cleanup

## Post-Deployment

### 1. Verify Deployment

```bash
# Check service status
ssh root@your-droplet-ip "cd /opt/sistema-mayra && docker-compose -f docker-compose.prod.yml ps"

# Check API health
curl https://your-domain.com/health

# Check logs
ssh root@your-droplet-ip "cd /opt/sistema-mayra && docker-compose -f docker-compose.prod.yml logs -f"
```

### 2. Configure Telegram Webhook

```bash
# Set webhook URL
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/telegram/webhook"}'

# Verify webhook
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

### 3. Import n8n Workflows

1. Access n8n at `https://n8n.your-domain.com`
2. Login with credentials from `.env.prod`
3. Import workflows from `n8n_workflows/*.json`
4. Configure credentials for each service
5. Activate workflows

### 4. Setup Monitoring

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Run monitoring setup
cd /opt/sistema-mayra
chmod +x scripts/deployment/monitoring.sh
sudo ./scripts/deployment/monitoring.sh
```

Access monitoring:
- Prometheus: `http://your-droplet-ip:9090`
- Grafana: `http://your-droplet-ip:3000`
- Alertmanager: `http://your-droplet-ip:9093`

## Maintenance

### Automated Backups

Backups run automatically at 2 AM daily. Manual backup:

```bash
ssh root@your-droplet-ip "/opt/sistema-mayra/scripts/deployment/backup.sh"
```

### Updates and Redeployment

```bash
# Pull latest changes locally
git pull origin main

# Redeploy
./scripts/deployment/deploy.sh
```

### Rollback

If deployment fails, rollback to previous version:

```bash
# List available backups
./scripts/deployment/rollback.sh --list

# Rollback to specific backup
./scripts/deployment/rollback.sh --backup sistema-mayra-20240115-120000

# Rollback to latest backup
./scripts/deployment/rollback.sh
```

### Database Maintenance

```bash
# Backup database manually
ssh root@your-droplet-ip "docker exec mayra_db_prod pg_dump -U postgres mayra_db > backup.sql"

# Restore database
ssh root@your-droplet-ip "docker exec -i mayra_db_prod psql -U postgres mayra_db < backup.sql"

# Run migrations
ssh root@your-droplet-ip "cd /opt/sistema-mayra && docker-compose -f docker-compose.prod.yml exec api alembic upgrade head"
```

### Log Management

```bash
# View logs
ssh root@your-droplet-ip "cd /opt/sistema-mayra && docker-compose -f docker-compose.prod.yml logs -f [service]"

# Rotate logs
ssh root@your-droplet-ip "logrotate -f /etc/logrotate.d/sistema-mayra"

# Clean old logs
ssh root@your-droplet-ip "find /var/log/sistema-mayra -name '*.log' -mtime +30 -delete"
```

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

```bash
# Check deployment log
cat /var/log/sistema-mayra/deploy-*.log

# Check Docker status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

#### 2. Services Not Starting

```bash
# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check resource usage
htop
df -h
docker system df
```

#### 3. Database Connection Issues

```bash
# Test database connection
docker exec mayra_db_prod pg_isready

# Check database logs
docker logs mayra_db_prod

# Verify credentials
docker exec mayra_db_prod printenv | grep POSTGRES
```

#### 4. SSL Certificate Issues

```bash
# Renew certificate manually
certbot renew --force-renewal

# Check certificate status
certbot certificates

# View nginx logs
docker logs mayra_nginx_prod
```

### Emergency Recovery

#### Complete System Recovery

```bash
# 1. Create fresh droplet
# 2. Run setup script
sudo ./scripts/deployment/setup-droplet.sh

# 3. Restore from S3 backup
aws s3 cp s3://your-bucket/backups/latest.tar.gz /opt/backups/

# 4. Extract and restore
cd /opt/backups
tar -xzf latest.tar.gz
./scripts/deployment/rollback.sh --backup sistema-mayra-timestamp
```

## Security Best Practices

### 1. Initial Hardening

```bash
# Change SSH port
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
systemctl restart sshd

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Create sudo user
adduser mayra-admin
usermod -aG sudo mayra-admin
```

### 2. Regular Updates

```bash
# Update system packages
apt update && apt upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Security Monitoring

- Review fail2ban logs: `fail2ban-client status`
- Check auth logs: `tail -f /var/log/auth.log`
- Monitor UFW: `ufw status verbose`
- Audit Docker: `docker scan mayra_api_prod`

### 4. Secrets Rotation

Rotate secrets every 90 days:

1. Generate new secrets
2. Update `.env.prod`
3. Redeploy application
4. Update external services (OpenAI, Telegram, etc.)

### 5. Backup Verification

Test backups monthly:

```bash
# Create test droplet
# Restore backup
# Verify functionality
# Document results
```

## Monitoring and Alerts

### Key Metrics to Monitor

- **System**: CPU, Memory, Disk usage
- **Application**: Response time, Error rate, Active users
- **Database**: Connection pool, Query performance, Size
- **n8n**: Workflow executions, Failed workflows, Queue size

### Alert Configuration

Alerts are sent via Telegram. Configure thresholds in:
- `/opt/monitoring/prometheus/rules/*.yml`

### Custom Dashboards

Import additional Grafana dashboards:
- System Overview: Dashboard ID 1860
- Docker Monitoring: Dashboard ID 893
- PostgreSQL: Dashboard ID 9628
- Redis: Dashboard ID 763

## Support and Maintenance

### Logs Location

- Application: `/var/log/sistema-mayra/`
- Docker: `/var/lib/docker/containers/*/`
- Nginx: `/var/log/nginx/`
- System: `/var/log/syslog`

### Health Endpoints

- API Health: `https://your-domain.com/health`
- Metrics: `https://your-domain.com/metrics`
- n8n Health: `https://n8n.your-domain.com/healthz`

### Maintenance Windows

Schedule maintenance during low-usage periods:
- Best time: 2-4 AM local time
- Notify users 24 hours in advance
- Use maintenance mode if available

## Appendix

### Useful Commands

```bash
# Docker cleanup
docker system prune -a --volumes

# Database vacuum
docker exec mayra_db_prod psql -U postgres -d mayra_db -c "VACUUM ANALYZE;"

# Redis memory optimization
docker exec mayra_redis_prod redis-cli MEMORY DOCTOR

# Certificate renewal dry run
certbot renew --dry-run

# Force container recreation
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Export/Import n8n workflows
# Export
docker exec -it sistema-mayra-n8n n8n export:workflow --all --output=/backups/workflows.json

# Import
docker exec -it sistema-mayra-n8n n8n import:workflow --input=/backups/workflows.json
```

### Environment Variables Reference

See `.env.prod.example` for complete list of configuration options.

### Architecture Diagram

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌──────▼──────┐
         │   FastAPI   │      │     n8n     │
         │   (API)     │      │ (Workflows) │
         └──────┬──────┘      └──────┬──────┘
                │                     │
    ┌───────────┼─────────────────────┤
    │           │                     │
┌───▼───┐  ┌───▼───┐  ┌──────────────▼──────┐
│PostgreSQL││ Redis │  │      ChromaDB       │
└─────────┘└───────┘  └─────────────────────┘
```

---

For additional support or questions, refer to the main project documentation or contact the development team.