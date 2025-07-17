#!/bin/bash
# Sistema Mayra - Production Deployment Script
# This script handles the deployment to DigitalOcean droplet

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_USER=${DEPLOY_USER:-"root"}
DEPLOY_HOST=${DEPLOY_HOST:-""}
PROJECT_NAME="sistema-mayra"
PROJECT_PATH="/opt/${PROJECT_NAME}"
BACKUP_PATH="/opt/backups"
LOG_FILE="/var/log/${PROJECT_NAME}/deploy-$(date +%Y%m%d-%H%M%S).log"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
MAX_HEALTH_CHECKS=30
HEALTH_CHECK_INTERVAL=10

# Functions
log() {
    echo -e "${2:-$BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${LOG_FILE}"
}

error() {
    log "ERROR: $1" "$RED"
    exit 1
}

success() {
    log "SUCCESS: $1" "$GREEN"
}

warning() {
    log "WARNING: $1" "$YELLOW"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Starting pre-deployment checks..."
    
    # Check if DEPLOY_HOST is set
    if [ -z "$DEPLOY_HOST" ]; then
        error "DEPLOY_HOST environment variable is not set"
    fi
    
    # Check SSH connection
    log "Testing SSH connection to ${DEPLOY_HOST}..."
    if ! ssh -o ConnectTimeout=10 "${DEPLOY_USER}@${DEPLOY_HOST}" "echo 'SSH connection successful'"; then
        error "Cannot connect to ${DEPLOY_HOST}"
    fi
    
    # Check if Docker is installed on remote
    log "Checking Docker installation on remote..."
    if ! ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "docker --version"; then
        error "Docker is not installed on ${DEPLOY_HOST}"
    fi
    
    # Check if docker-compose is installed on remote
    log "Checking docker-compose installation on remote..."
    if ! ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "docker-compose --version"; then
        error "docker-compose is not installed on ${DEPLOY_HOST}"
    fi
    
    success "Pre-deployment checks passed"
}

# Backup current deployment
backup_current_deployment() {
    log "Backing up current deployment..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        
        # Create backup directory
        BACKUP_DIR="${BACKUP_PATH}/${PROJECT_NAME}-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "\${BACKUP_DIR}"
        
        # Backup database
        if docker ps --format '{{.Names}}' | grep -q 'mayra_db_prod'; then
            echo "Backing up PostgreSQL database..."
            docker exec mayra_db_prod pg_dump -U \${POSTGRES_USER:-postgres} \${POSTGRES_DB:-mayra_db} | gzip > "\${BACKUP_DIR}/database.sql.gz"
        fi
        
        # Backup Redis data
        if docker ps --format '{{.Names}}' | grep -q 'mayra_redis_prod'; then
            echo "Backing up Redis data..."
            docker exec mayra_redis_prod redis-cli --no-auth-warning -a \${REDIS_PASSWORD} BGSAVE
            sleep 5
            docker cp mayra_redis_prod:/data/dump.rdb "\${BACKUP_DIR}/redis.rdb"
        fi
        
        # Backup current docker-compose files
        if [ -d "${PROJECT_PATH}" ]; then
            cp -r "${PROJECT_PATH}/docker-compose.prod.yml" "\${BACKUP_DIR}/" || true
            cp -r "${PROJECT_PATH}/.env" "\${BACKUP_DIR}/" || true
        fi
        
        # Backup n8n workflows
        if [ -d "${PROJECT_PATH}/n8n_workflows" ]; then
            cp -r "${PROJECT_PATH}/n8n_workflows" "\${BACKUP_DIR}/" || true
        fi
        
        echo "Backup completed: \${BACKUP_DIR}"
EOF
    
    success "Backup completed"
}

# Deploy application
deploy_application() {
    log "Starting deployment..."
    
    # Create necessary directories on remote
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "mkdir -p ${PROJECT_PATH} /var/log/${PROJECT_NAME}"
    
    # Copy project files
    log "Copying project files..."
    rsync -avz --exclude-from='.gitignore' \
        --exclude '.git' \
        --exclude 'node_modules' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.env.local' \
        --exclude '.env.dev' \
        --exclude 'test_scripts/output' \
        ./ "${DEPLOY_USER}@${DEPLOY_HOST}:${PROJECT_PATH}/"
    
    # Deploy with docker-compose
    log "Deploying with docker-compose..."
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Pull latest images if using registry
        if [ -n "${DOCKER_REGISTRY}" ]; then
            echo "Pulling images from registry..."
            docker-compose -f docker-compose.prod.yml pull
        fi
        
        # Build images if needed
        echo "Building Docker images..."
        docker-compose -f docker-compose.prod.yml build --no-cache
        
        # Stop current containers (if any)
        echo "Stopping current containers..."
        docker-compose -f docker-compose.prod.yml down || true
        
        # Start new containers
        echo "Starting new containers..."
        docker-compose -f docker-compose.prod.yml up -d
        
        # Run database migrations
        echo "Running database migrations..."
        sleep 10  # Wait for database to be ready
        docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head
        
        # Load initial data if needed
        if ! docker-compose -f docker-compose.prod.yml exec -T api python -c "from database.models import Recipe; from database.session import get_session; import asyncio; async def check(): async with get_session() as db: result = await db.execute('SELECT COUNT(*) FROM recipes'); return result.scalar() > 0; print(asyncio.run(check()))" | grep -q "True"; then
            echo "Loading initial data..."
            docker-compose -f docker-compose.prod.yml exec -T api python -m database.seeders.main --mode=all
            docker-compose -f docker-compose.prod.yml exec -T api python -m data_processor.main
        fi
EOF
    
    success "Application deployed"
}

# Health checks
perform_health_checks() {
    log "Performing health checks..."
    
    local checks_passed=0
    local total_checks=0
    
    for i in $(seq 1 $MAX_HEALTH_CHECKS); do
        log "Health check attempt $i/$MAX_HEALTH_CHECKS..."
        
        # Check API health
        if ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "curl -sf http://localhost:8000/health > /dev/null"; then
            ((checks_passed++))
            success "API is healthy"
            
            # Check Telegram bot
            if ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "docker logs mayra_telegram_bot_prod 2>&1 | tail -20 | grep -q 'Bot started successfully'"; then
                success "Telegram bot is running"
                break
            else
                warning "Telegram bot not ready yet"
            fi
        else
            warning "API not ready yet"
        fi
        
        ((total_checks++))
        
        if [ $i -lt $MAX_HEALTH_CHECKS ]; then
            sleep $HEALTH_CHECK_INTERVAL
        fi
    done
    
    if [ $checks_passed -eq 0 ]; then
        error "Health checks failed after $total_checks attempts"
    fi
    
    success "Health checks passed"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Check if certbot is installed
        if ! command -v certbot &> /dev/null; then
            echo "Installing certbot..."
            apt-get update
            apt-get install -y certbot python3-certbot-nginx
        fi
        
        # Get SSL certificate if domain is configured
        if [ -n "${DOMAIN_NAME}" ]; then
            echo "Obtaining SSL certificate for ${DOMAIN_NAME}..."
            certbot certonly --standalone --non-interactive --agree-tos \
                --email ${ADMIN_EMAIL} \
                -d ${DOMAIN_NAME} \
                --pre-hook "docker-compose -f docker-compose.prod.yml stop nginx" \
                --post-hook "docker-compose -f docker-compose.prod.yml start nginx"
            
            # Update nginx configuration
            sed -i "s/yourdomain.com/${DOMAIN_NAME}/g" docker/nginx/nginx.conf
            docker-compose -f docker-compose.prod.yml restart nginx
        fi
EOF
    
    success "SSL setup completed"
}

# Deploy n8n workflows
deploy_n8n_workflows() {
    log "Deploying n8n workflows..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Start n8n if not already running
        if [ -f "n8n_workflows/configs/docker-compose.yml" ]; then
            cd n8n_workflows/configs
            docker-compose up -d
            
            # Wait for n8n to be ready
            echo "Waiting for n8n to be ready..."
            sleep 30
            
            # Import workflows
            echo "Importing workflows..."
            # This would require n8n CLI or API calls to import workflows
            # For now, manual import is required
            echo "Please manually import workflows from n8n_workflows/*.json"
        fi
EOF
    
    success "n8n deployment completed"
}

# Post-deployment tasks
post_deployment_tasks() {
    log "Running post-deployment tasks..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Clean up old Docker images
        echo "Cleaning up old Docker images..."
        docker image prune -f
        
        # Set up log rotation
        cat > /etc/logrotate.d/${PROJECT_NAME} <<EOL
/var/log/${PROJECT_NAME}/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOL
        
        # Set up cron for automatic backups
        (crontab -l 2>/dev/null; echo "0 2 * * * ${PROJECT_PATH}/scripts/deployment/backup.sh") | crontab -
        
        # Show deployment summary
        echo "===== Deployment Summary ====="
        docker-compose -f docker-compose.prod.yml ps
        echo "============================="
EOF
    
    success "Post-deployment tasks completed"
}

# Send deployment notification
send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "${TELEGRAM_BOT_TOKEN}" ] && [ -n "${ADMIN_TELEGRAM_ID}" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -H "Content-Type: application/json" \
            -d "{
                \"chat_id\": \"${ADMIN_TELEGRAM_ID}\",
                \"text\": \"=€ *Sistema Mayra Deployment*\n\nStatus: ${status}\n${message}\n\nTime: $(date)\",
                \"parse_mode\": \"Markdown\"
            }" > /dev/null
    fi
}

# Main deployment flow
main() {
    log "Starting Sistema Mayra deployment to DigitalOcean..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Load environment variables
    if [ -f ".env.prod" ]; then
        export $(grep -v '^#' .env.prod | xargs)
    else
        error ".env.prod file not found"
    fi
    
    # Execute deployment steps
    pre_deployment_checks
    backup_current_deployment
    deploy_application
    perform_health_checks
    
    # Optional steps
    if [ "${SETUP_SSL:-false}" == "true" ]; then
        setup_ssl
    fi
    
    if [ "${DEPLOY_N8N:-true}" == "true" ]; then
        deploy_n8n_workflows
    fi
    
    post_deployment_tasks
    
    # Send success notification
    send_notification " SUCCESS" "Deployment completed successfully!"
    
    success "Deployment completed successfully!"
    log "Deployment log: ${LOG_FILE}"
}

# Handle errors
trap 'error "Deployment failed! Check log: ${LOG_FILE}"' ERR

# Run main function
main "$@"