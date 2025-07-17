#!/bin/bash
# Sistema Mayra - Rollback Script
# This script handles rolling back to a previous deployment

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
LOG_FILE="/var/log/${PROJECT_NAME}/rollback-$(date +%Y%m%d-%H%M%S).log"

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

# List available backups
list_backups() {
    log "Available backups:"
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "ls -la ${BACKUP_PATH}/${PROJECT_NAME}-* 2>/dev/null | tail -10" || echo "No backups found"
}

# Select backup to restore
select_backup() {
    local backup_name=$1
    
    if [ -z "$backup_name" ]; then
        # Get latest backup if not specified
        backup_name=$(ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "ls -1 ${BACKUP_PATH}/${PROJECT_NAME}-* 2>/dev/null | tail -1 | xargs basename")
        
        if [ -z "$backup_name" ]; then
            error "No backups found"
        fi
        
        warning "No backup specified, using latest: $backup_name"
    fi
    
    # Verify backup exists
    if ! ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "test -d ${BACKUP_PATH}/$backup_name"; then
        error "Backup $backup_name not found"
    fi
    
    echo "$backup_name"
}

# Backup current state before rollback
backup_current_state() {
    log "Backing up current state before rollback..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        
        # Create rollback backup directory
        ROLLBACK_DIR="${BACKUP_PATH}/${PROJECT_NAME}-rollback-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "\${ROLLBACK_DIR}"
        
        # Save current docker-compose state
        cd ${PROJECT_PATH}
        docker-compose -f docker-compose.prod.yml ps > "\${ROLLBACK_DIR}/docker-state.txt"
        
        # Copy current configuration
        cp docker-compose.prod.yml "\${ROLLBACK_DIR}/" || true
        cp .env "\${ROLLBACK_DIR}/" || true
        
        # Save current container logs
        for container in \$(docker-compose -f docker-compose.prod.yml ps -q); do
            container_name=\$(docker inspect -f '{{.Name}}' \$container | sed 's/\///')
            docker logs \$container > "\${ROLLBACK_DIR}/\${container_name}.log" 2>&1 || true
        done
        
        echo "Current state backed up to: \${ROLLBACK_DIR}"
EOF
    
    success "Current state backed up"
}

# Restore database
restore_database() {
    local backup_dir=$1
    
    log "Restoring database from backup..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Check if database backup exists
        if [ -f "${BACKUP_PATH}/${backup_dir}/database.sql.gz" ]; then
            echo "Found database backup, restoring..."
            
            # Stop application containers but keep database running
            docker-compose -f docker-compose.prod.yml stop api telegram_bot
            
            # Drop and recreate database
            docker-compose -f docker-compose.prod.yml exec -T db psql -U \${POSTGRES_USER:-postgres} -c "DROP DATABASE IF EXISTS \${POSTGRES_DB:-mayra_db};"
            docker-compose -f docker-compose.prod.yml exec -T db psql -U \${POSTGRES_USER:-postgres} -c "CREATE DATABASE \${POSTGRES_DB:-mayra_db};"
            
            # Restore database
            gunzip -c "${BACKUP_PATH}/${backup_dir}/database.sql.gz" | docker-compose -f docker-compose.prod.yml exec -T db psql -U \${POSTGRES_USER:-postgres} \${POSTGRES_DB:-mayra_db}
            
            echo "Database restored successfully"
        else
            echo "No database backup found, skipping database restore"
        fi
EOF
    
    success "Database restore completed"
}

# Restore Redis data
restore_redis() {
    local backup_dir=$1
    
    log "Restoring Redis data from backup..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Check if Redis backup exists
        if [ -f "${BACKUP_PATH}/${backup_dir}/redis.rdb" ]; then
            echo "Found Redis backup, restoring..."
            
            # Stop Redis
            docker-compose -f docker-compose.prod.yml stop redis
            
            # Copy backup file
            docker cp "${BACKUP_PATH}/${backup_dir}/redis.rdb" mayra_redis_prod:/data/dump.rdb
            
            # Start Redis
            docker-compose -f docker-compose.prod.yml start redis
            
            echo "Redis data restored successfully"
        else
            echo "No Redis backup found, skipping Redis restore"
        fi
EOF
    
    success "Redis restore completed"
}

# Restore application files
restore_application() {
    local backup_dir=$1
    
    log "Restoring application configuration..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Restore docker-compose file if exists
        if [ -f "${BACKUP_PATH}/${backup_dir}/docker-compose.prod.yml" ]; then
            cp "${BACKUP_PATH}/${backup_dir}/docker-compose.prod.yml" ./
        fi
        
        # Restore environment file if exists
        if [ -f "${BACKUP_PATH}/${backup_dir}/.env" ]; then
            cp "${BACKUP_PATH}/${backup_dir}/.env" ./
        fi
        
        # Restore n8n workflows if exists
        if [ -d "${BACKUP_PATH}/${backup_dir}/n8n_workflows" ]; then
            cp -r "${BACKUP_PATH}/${backup_dir}/n8n_workflows" ./
        fi
        
        echo "Application configuration restored"
EOF
    
    success "Application restore completed"
}

# Restart services
restart_services() {
    log "Restarting services..."
    
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        # Stop all containers
        docker-compose -f docker-compose.prod.yml down
        
        # Start containers with restored configuration
        docker-compose -f docker-compose.prod.yml up -d
        
        # Wait for services to start
        sleep 30
        
        # Show status
        docker-compose -f docker-compose.prod.yml ps
EOF
    
    success "Services restarted"
}

# Verify rollback
verify_rollback() {
    log "Verifying rollback..."
    
    local api_healthy=false
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "curl -sf http://localhost:8000/health > /dev/null"; then
            api_healthy=true
            break
        fi
        
        ((attempt++))
        log "Waiting for API to be healthy... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if $api_healthy; then
        success "API is healthy after rollback"
    else
        error "API is not healthy after rollback"
    fi
    
    # Check other services
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash <<EOF
        set -e
        cd ${PROJECT_PATH}
        
        echo "=== Service Status ==="
        docker-compose -f docker-compose.prod.yml ps
        
        echo -e "\n=== Recent Logs ==="
        docker-compose -f docker-compose.prod.yml logs --tail=20
EOF
    
    success "Rollback verification completed"
}

# Send rollback notification
send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "${TELEGRAM_BOT_TOKEN}" ] && [ -n "${ADMIN_TELEGRAM_ID}" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -H "Content-Type: application/json" \
            -d "{
                \"chat_id\": \"${ADMIN_TELEGRAM_ID}\",
                \"text\": \"î *Sistema Mayra Rollback*\n\nStatus: ${status}\n${message}\n\nTime: $(date)\",
                \"parse_mode\": \"Markdown\"
            }" > /dev/null
    fi
}

# Main rollback flow
main() {
    log "Starting Sistema Mayra rollback..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Load environment variables
    if [ -f ".env.prod" ]; then
        export $(grep -v '^#' .env.prod | xargs)
    else
        error ".env.prod file not found"
    fi
    
    # Check connection
    if [ -z "$DEPLOY_HOST" ]; then
        error "DEPLOY_HOST environment variable is not set"
    fi
    
    # Parse arguments
    local backup_name=""
    local skip_database=false
    local skip_redis=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup)
                backup_name="$2"
                shift 2
                ;;
            --list)
                list_backups
                exit 0
                ;;
            --skip-database)
                skip_database=true
                shift
                ;;
            --skip-redis)
                skip_redis=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --backup <name>    Specify backup to restore (default: latest)"
                echo "  --list            List available backups"
                echo "  --skip-database   Skip database restoration"
                echo "  --skip-redis      Skip Redis restoration"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    # Select backup
    backup_name=$(select_backup "$backup_name")
    log "Rolling back to: $backup_name"
    
    # Confirm rollback
    echo -e "${YELLOW}WARNING: This will rollback to backup: $backup_name${NC}"
    echo -e "${YELLOW}This action cannot be undone automatically.${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log "Rollback cancelled by user"
        exit 0
    fi
    
    # Execute rollback steps
    backup_current_state
    
    if [ "$skip_database" = false ]; then
        restore_database "$backup_name"
    else
        warning "Skipping database restoration"
    fi
    
    if [ "$skip_redis" = false ]; then
        restore_redis "$backup_name"
    else
        warning "Skipping Redis restoration"
    fi
    
    restore_application "$backup_name"
    restart_services
    verify_rollback
    
    # Send notification
    send_notification " SUCCESS" "Rollback to $backup_name completed successfully!"
    
    success "Rollback completed successfully!"
    log "Rollback log: ${LOG_FILE}"
}

# Handle errors
trap 'send_notification "L FAILED" "Rollback failed! Check logs for details."; error "Rollback failed! Check log: ${LOG_FILE}"' ERR

# Run main function
main "$@"