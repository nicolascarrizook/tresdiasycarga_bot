#!/bin/bash
# Sistema Mayra - Automated Backup Script
# This script performs automated backups of all system components

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="sistema-mayra"
PROJECT_PATH="/opt/${PROJECT_NAME}"
BACKUP_PATH="/opt/backups"
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}
S3_BUCKET=${S3_BUCKET:-""}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-""}
ADMIN_TELEGRAM_ID=${ADMIN_TELEGRAM_ID:-""}
LOG_FILE="/var/log/${PROJECT_NAME}/backup-$(date +%Y%m%d-%H%M%S).log"

# Backup timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_PATH}/${PROJECT_NAME}-${TIMESTAMP}"

# Functions
log() {
    echo -e "${2:-$BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${LOG_FILE}"
}

error() {
    log "ERROR: $1" "$RED"
    send_notification "❌ Backup Failed" "$1"
    exit 1
}

success() {
    log "SUCCESS: $1" "$GREEN"
}

warning() {
    log "WARNING: $1" "$YELLOW"
}

# Send Telegram notification
send_notification() {
    local subject=$1
    local message=$2
    
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_TELEGRAM_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -H "Content-Type: application/json" \
            -d "{
                \"chat_id\": \"${ADMIN_TELEGRAM_ID}\",
                \"text\": \"💾 *Sistema Mayra Backup*\n\n${subject}\n${message}\n\nTime: $(date)\",
                \"parse_mode\": \"Markdown\"
            }" > /dev/null || true
    fi
}

# Create backup directory
create_backup_directory() {
    log "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    success "Backup directory created: $BACKUP_DIR"
}

# Backup PostgreSQL database
backup_postgresql() {
    log "Backing up PostgreSQL database..."
    
    cd "$PROJECT_PATH"
    
    # Check if database container is running
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "mayra_db_prod.*Up"; then
        warning "PostgreSQL container is not running"
        return
    fi
    
    # Get database credentials from environment
    DB_NAME=$(docker-compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_DB)
    DB_USER=$(docker-compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_USER)
    
    # Perform backup
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_DIR/database.sql.gz"
    
    # Verify backup
    if [ -s "$BACKUP_DIR/database.sql.gz" ]; then
        local size=$(du -h "$BACKUP_DIR/database.sql.gz" | cut -f1)
        success "PostgreSQL backup completed: $size"
    else
        error "PostgreSQL backup failed - empty file"
    fi
}

# Backup Redis data
backup_redis() {
    log "Backing up Redis data..."
    
    cd "$PROJECT_PATH"
    
    # Check if Redis container is running
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "mayra_redis_prod.*Up"; then
        warning "Redis container is not running"
        return
    fi
    
    # Get Redis password
    REDIS_PASSWORD=$(docker-compose -f docker-compose.prod.yml exec -T redis printenv REDIS_PASSWORD)
    
    # Trigger Redis save
    docker-compose -f docker-compose.prod.yml exec -T redis redis-cli --no-auth-warning -a "$REDIS_PASSWORD" BGSAVE
    
    # Wait for save to complete
    log "Waiting for Redis save to complete..."
    sleep 5
    
    # Copy dump file
    docker cp mayra_redis_prod:/data/dump.rdb "$BACKUP_DIR/redis.rdb" 2>/dev/null || true
    
    if [ -f "$BACKUP_DIR/redis.rdb" ]; then
        local size=$(du -h "$BACKUP_DIR/redis.rdb" | cut -f1)
        success "Redis backup completed: $size"
    else
        warning "Redis backup not found - Redis might be empty"
    fi
}

# Backup ChromaDB data
backup_chromadb() {
    log "Backing up ChromaDB data..."
    
    # Check if ChromaDB directory exists
    if [ -d "$PROJECT_PATH/data/chroma_db" ]; then
        tar -czf "$BACKUP_DIR/chromadb.tar.gz" -C "$PROJECT_PATH/data" chroma_db
        
        if [ -f "$BACKUP_DIR/chromadb.tar.gz" ]; then
            local size=$(du -h "$BACKUP_DIR/chromadb.tar.gz" | cut -f1)
            success "ChromaDB backup completed: $size"
        fi
    else
        warning "ChromaDB directory not found"
    fi
}

# Backup application files
backup_application_files() {
    log "Backing up application files..."
    
    # Backup configuration files
    cp "$PROJECT_PATH/docker-compose.prod.yml" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$PROJECT_PATH/.env" "$BACKUP_DIR/.env.encrypted" 2>/dev/null || true
    
    # Encrypt sensitive .env file
    if [ -f "$BACKUP_DIR/.env.encrypted" ] && command -v openssl &> /dev/null; then
        openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/.env.encrypted" -out "$BACKUP_DIR/.env.encrypted" -k "${BACKUP_ENCRYPTION_KEY:-defaultkey}" 2>/dev/null || true
    fi
    
    # Backup n8n workflows
    if [ -d "$PROJECT_PATH/n8n_workflows" ]; then
        tar -czf "$BACKUP_DIR/n8n_workflows.tar.gz" -C "$PROJECT_PATH" n8n_workflows
        success "n8n workflows backed up"
    fi
    
    # Backup uploaded files (if any)
    if [ -d "$PROJECT_PATH/uploads" ]; then
        tar -czf "$BACKUP_DIR/uploads.tar.gz" -C "$PROJECT_PATH" uploads
        success "Uploaded files backed up"
    fi
    
    success "Application files backup completed"
}

# Backup Docker volumes
backup_docker_volumes() {
    log "Backing up Docker volumes..."
    
    cd "$PROJECT_PATH"
    
    # Get list of volumes used by the project
    volumes=$(docker-compose -f docker-compose.prod.yml config --volumes 2>/dev/null || true)
    
    if [ -n "$volumes" ]; then
        mkdir -p "$BACKUP_DIR/volumes"
        
        for volume in $volumes; do
            volume_name="${PROJECT_NAME}_${volume}"
            if docker volume inspect "$volume_name" &>/dev/null; then
                log "Backing up volume: $volume_name"
                docker run --rm -v "$volume_name:/data" -v "$BACKUP_DIR/volumes:/backup" alpine tar -czf "/backup/${volume}.tar.gz" -C /data .
            fi
        done
        
        success "Docker volumes backup completed"
    else
        warning "No Docker volumes found to backup"
    fi
}

# Create backup metadata
create_backup_metadata() {
    log "Creating backup metadata..."
    
    cat > "$BACKUP_DIR/backup_metadata.json" <<EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "$(cd $PROJECT_PATH && git describe --tags --always 2>/dev/null || echo 'unknown')",
    "components": {
        "postgresql": $([ -f "$BACKUP_DIR/database.sql.gz" ] && echo "true" || echo "false"),
        "redis": $([ -f "$BACKUP_DIR/redis.rdb" ] && echo "true" || echo "false"),
        "chromadb": $([ -f "$BACKUP_DIR/chromadb.tar.gz" ] && echo "true" || echo "false"),
        "n8n_workflows": $([ -f "$BACKUP_DIR/n8n_workflows.tar.gz" ] && echo "true" || echo "false"),
        "uploads": $([ -f "$BACKUP_DIR/uploads.tar.gz" ] && echo "true" || echo "false")
    },
    "size": "$(du -sh $BACKUP_DIR | cut -f1)",
    "retention_days": $BACKUP_RETENTION_DAYS
}
EOF
    
    success "Backup metadata created"
}

# Compress backup
compress_backup() {
    log "Compressing backup..."
    
    cd "$BACKUP_PATH"
    tar -czf "${PROJECT_NAME}-${TIMESTAMP}.tar.gz" "${PROJECT_NAME}-${TIMESTAMP}"
    
    if [ -f "${PROJECT_NAME}-${TIMESTAMP}.tar.gz" ]; then
        # Remove uncompressed directory
        rm -rf "$BACKUP_DIR"
        BACKUP_FILE="${BACKUP_PATH}/${PROJECT_NAME}-${TIMESTAMP}.tar.gz"
        local size=$(du -h "$BACKUP_FILE" | cut -f1)
        success "Backup compressed: $size"
    else
        error "Failed to compress backup"
    fi
}

# Upload to S3 (optional)
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3 bucket not configured, skipping upload"
        return
    fi
    
    log "Uploading backup to S3..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        warning "AWS CLI not installed, skipping S3 upload"
        return
    fi
    
    # Upload with progress
    if aws s3 cp "$BACKUP_FILE" "s3://${S3_BUCKET}/backups/" --storage-class GLACIER_IR; then
        success "Backup uploaded to S3: s3://${S3_BUCKET}/backups/$(basename $BACKUP_FILE)"
    else
        warning "Failed to upload backup to S3"
    fi
}

# Clean old backups
clean_old_backups() {
    log "Cleaning old backups..."
    
    # Clean local backups
    find "$BACKUP_PATH" -name "${PROJECT_NAME}-*.tar.gz" -type f -mtime +$BACKUP_RETENTION_DAYS -delete
    
    local remaining=$(ls -1 "$BACKUP_PATH/${PROJECT_NAME}-"*.tar.gz 2>/dev/null | wc -l)
    success "Old backups cleaned. Remaining backups: $remaining"
    
    # Clean S3 backups (if configured)
    if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
        log "Cleaning old S3 backups..."
        aws s3 ls "s3://${S3_BUCKET}/backups/" | while read -r line; do
            backup_date=$(echo $line | awk '{print $1}')
            backup_file=$(echo $line | awk '{print $4}')
            
            if [[ ! -z "$backup_file" ]] && [[ "$backup_file" == ${PROJECT_NAME}-* ]]; then
                if [[ $(date -d "$backup_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$backup_date" +%s) -lt $(date -d "$BACKUP_RETENTION_DAYS days ago" +%s) ]]; then
                    aws s3 rm "s3://${S3_BUCKET}/backups/$backup_file"
                    log "Deleted old S3 backup: $backup_file"
                fi
            fi
        done
    fi
}

# Generate backup report
generate_backup_report() {
    log "Generating backup report..."
    
    local report="*Backup Report*\n\n"
    report+="📅 Date: $(date)\n"
    report+="📁 Backup: $(basename $BACKUP_FILE)\n"
    report+="💾 Size: $(du -h $BACKUP_FILE | cut -f1)\n"
    report+="🔢 Retention: $BACKUP_RETENTION_DAYS days\n\n"
    
    report+="*Components:*\n"
    [ -f "$BACKUP_DIR/database.sql.gz" ] && report+="✅ PostgreSQL\n" || report+="❌ PostgreSQL\n"
    [ -f "$BACKUP_DIR/redis.rdb" ] && report+="✅ Redis\n" || report+="❌ Redis\n"
    [ -f "$BACKUP_DIR/chromadb.tar.gz" ] && report+="✅ ChromaDB\n" || report+="❌ ChromaDB\n"
    [ -f "$BACKUP_DIR/n8n_workflows.tar.gz" ] && report+="✅ n8n Workflows\n" || report+="❌ n8n Workflows\n"
    
    [ -n "$S3_BUCKET" ] && report+="\n☁️ Uploaded to S3: ✅" || report+="\n☁️ S3 Upload: Not configured"
    
    echo -e "$report"
}

# Main backup flow
main() {
    log "Starting Sistema Mayra backup..."
    
    # Load environment variables
    if [ -f "$PROJECT_PATH/.env" ]; then
        export $(grep -v '^#' "$PROJECT_PATH/.env" | xargs)
    fi
    
    # Start backup process
    send_notification "🔄 Backup Started" "Initiating system backup..."
    
    # Execute backup steps
    create_backup_directory
    backup_postgresql
    backup_redis
    backup_chromadb
    backup_application_files
    backup_docker_volumes
    create_backup_metadata
    compress_backup
    upload_to_s3
    clean_old_backups
    
    # Generate report
    REPORT=$(generate_backup_report)
    
    # Send completion notification
    send_notification "✅ Backup Completed" "$REPORT"
    
    success "Backup completed successfully!"
    log "Backup file: $BACKUP_FILE"
    log "Backup log: $LOG_FILE"
}

# Handle errors
trap 'error "Backup failed! Check log: ${LOG_FILE}"' ERR

# Check if running as root or with proper permissions
if [ "$EUID" -ne 0 ] && [ ! -w "$BACKUP_PATH" ]; then
    error "This script must be run as root or with write permissions to $BACKUP_PATH"
fi

# Run main function
main "$@"