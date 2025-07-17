#!/bin/bash
# Sistema Mayra - Monitoring Setup Script
# This script sets up comprehensive monitoring for the deployment

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
MONITORING_PATH="/opt/monitoring"
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-"admin"}
PROMETHEUS_RETENTION=${PROMETHEUS_RETENTION:-"15d"}
ALERT_WEBHOOK=${ALERT_WEBHOOK:-""}

# Functions
log() {
    echo -e "${2:-$BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
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

# Create monitoring directories
setup_directories() {
    log "Setting up monitoring directories..."
    
    mkdir -p "$MONITORING_PATH"/{prometheus,grafana,alertmanager}
    mkdir -p "$MONITORING_PATH"/prometheus/{rules,targets}
    mkdir -p "$MONITORING_PATH"/grafana/{dashboards,provisioning}
    
    success "Monitoring directories created"
}

# Configure Prometheus
configure_prometheus() {
    log "Configuring Prometheus..."
    
    # Create Prometheus configuration
    cat > "$MONITORING_PATH/prometheus/prometheus.yml" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'sistema-mayra'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules
rule_files:
  - "rules/*.yml"

# Scrape configurations
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+):.*'

  # Docker containers
  - job_name: 'docker'
    static_configs:
      - targets: ['cadvisor:8080']

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # API endpoints
  - job_name: 'api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api:8000']
    relabel_configs:
      - source_labels: [__address__]
        target_label: service
        replacement: 'mayra-api'

  # n8n workflows
  - job_name: 'n8n'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['n8n:5678']
    relabel_configs:
      - source_labels: [__address__]
        target_label: service
        replacement: 'n8n-workflows'

  # Blackbox exporter for endpoint monitoring
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - http://api:8000/health
          - http://n8n:5678/healthz
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
EOF
    
    success "Prometheus configured"
}

# Create alerting rules
create_alert_rules() {
    log "Creating alert rules..."
    
    # System alerts
    cat > "$MONITORING_PATH/prometheus/rules/system_alerts.yml" <<EOF
groups:
  - name: system_alerts
    interval: 30s
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ \$labels.instance }}"
          description: "CPU usage is above 80% (current value: {{ \$value }}%)"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ \$labels.instance }}"
          description: "Memory usage is above 85% (current value: {{ \$value }}%)"

      # Disk space low
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ \$labels.instance }}"
          description: "Disk space is below 20% (current value: {{ \$value }}%)"

      # High load average
      - alert: HighLoadAverage
        expr: node_load15 / on(instance) group_left() count(node_cpu_seconds_total{mode="idle"}) by (instance) > 2
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High load average on {{ \$labels.instance }}"
          description: "15-minute load average is high (current value: {{ \$value }})"
EOF

    # Application alerts
    cat > "$MONITORING_PATH/prometheus/rules/application_alerts.yml" <<EOF
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # API down
      - alert: APIDown
        expr: up{job="api"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API is down"
          description: "Sistema Mayra API has been down for more than 2 minutes"

      # Database down
      - alert: PostgreSQLDown
        expr: up{job="postgresql"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL database has been down for more than 2 minutes"

      # Redis down
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"
          description: "Redis cache has been down for more than 2 minutes"

      # n8n workflows down
      - alert: N8NDown
        expr: up{job="n8n"} == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "n8n is down"
          description: "n8n workflow automation has been down for more than 5 minutes"

      # High API response time
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "95th percentile API response time is above 1 second (current value: {{ \$value }}s)"

      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on API"
          description: "Error rate is above 5% (current value: {{ \$value }}%)"

      # Database connection pool exhausted
      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "PostgreSQL connection usage is above 80% (current value: {{ \$value }}%)"
EOF

    # Backup alerts
    cat > "$MONITORING_PATH/prometheus/rules/backup_alerts.yml" <<EOF
groups:
  - name: backup_alerts
    interval: 1h
    rules:
      # Backup not completed
      - alert: BackupNotCompleted
        expr: time() - backup_last_success_timestamp > 86400
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Backup not completed in 24 hours"
          description: "Last successful backup was {{ \$value | humanizeDuration }} ago"

      # Backup size anomaly
      - alert: BackupSizeAnomaly
        expr: abs(backup_size_bytes - avg_over_time(backup_size_bytes[7d])) / avg_over_time(backup_size_bytes[7d]) > 0.5
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Backup size anomaly detected"
          description: "Backup size differs by more than 50% from 7-day average"
EOF

    success "Alert rules created"
}

# Configure Alertmanager
configure_alertmanager() {
    log "Configuring Alertmanager..."
    
    cat > "$MONITORING_PATH/alertmanager/alertmanager.yml" <<EOF
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default-receiver'
  routes:
    - match:
        severity: critical
      receiver: critical-receiver
      continue: true
    - match:
        severity: warning
      receiver: warning-receiver

receivers:
  - name: 'default-receiver'
    webhook_configs:
      - url: '${ALERT_WEBHOOK}'
        send_resolved: true

  - name: 'critical-receiver'
    webhook_configs:
      - url: '${ALERT_WEBHOOK}'
        send_resolved: true
    telegram_configs:
      - bot_token: '${TELEGRAM_BOT_TOKEN}'
        chat_id: '${ADMIN_TELEGRAM_ID}'
        parse_mode: 'Markdown'
        message: |
          🚨 *CRITICAL ALERT*
          *Alert:* {{ .GroupLabels.alertname }}
          *Summary:* {{ .CommonAnnotations.summary }}
          *Description:* {{ .CommonAnnotations.description }}
          *Status:* {{ .Status }}

  - name: 'warning-receiver'
    webhook_configs:
      - url: '${ALERT_WEBHOOK}'
        send_resolved: true
    telegram_configs:
      - bot_token: '${TELEGRAM_BOT_TOKEN}'
        chat_id: '${ADMIN_TELEGRAM_ID}'
        parse_mode: 'Markdown'
        message: |
          ⚠️ *WARNING ALERT*
          *Alert:* {{ .GroupLabels.alertname }}
          *Summary:* {{ .CommonAnnotations.summary }}
          *Description:* {{ .CommonAnnotations.description }}
          *Status:* {{ .Status }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

    success "Alertmanager configured"
}

# Configure Grafana
configure_grafana() {
    log "Configuring Grafana..."
    
    # Grafana provisioning - datasources
    mkdir -p "$MONITORING_PATH/grafana/provisioning/datasources"
    cat > "$MONITORING_PATH/grafana/provisioning/datasources/prometheus.yml" <<EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF

    # Grafana provisioning - dashboards
    mkdir -p "$MONITORING_PATH/grafana/provisioning/dashboards"
    cat > "$MONITORING_PATH/grafana/provisioning/dashboards/dashboards.yml" <<EOF
apiVersion: 1

providers:
  - name: 'Sistema Mayra Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

    # Create system overview dashboard
    create_grafana_dashboard
    
    success "Grafana configured"
}

# Create Grafana dashboard
create_grafana_dashboard() {
    log "Creating Grafana dashboard..."
    
    cat > "$MONITORING_PATH/grafana/dashboards/sistema-mayra-overview.json" <<'EOF'
{
  "dashboard": {
    "id": null,
    "uid": "sistema-mayra-overview",
    "title": "Sistema Mayra - Overview",
    "tags": ["sistema-mayra", "overview"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "id": 1,
        "title": "System CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ]
      },
      {
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "id": 2,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memory Usage %"
          }
        ]
      },
      {
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
        "id": 3,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
        "id": 4,
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"api\"}",
            "legendFormat": "API"
          },
          {
            "expr": "up{job=\"postgresql\"}",
            "legendFormat": "PostgreSQL"
          },
          {
            "expr": "up{job=\"redis\"}",
            "legendFormat": "Redis"
          },
          {
            "expr": "up{job=\"n8n\"}",
            "legendFormat": "n8n"
          }
        ]
      }
    ]
  }
}
EOF

    success "Grafana dashboard created"
}

# Create monitoring docker-compose
create_monitoring_compose() {
    log "Creating monitoring docker-compose..."
    
    cat > "$MONITORING_PATH/docker-compose.yml" <<EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: monitoring-prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION}'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - monitoring
      - mayra_network_prod

  alertmanager:
    image: prom/alertmanager:latest
    container_name: monitoring-alertmanager
    restart: unless-stopped
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: monitoring-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: monitoring-node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: monitoring-cadvisor
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring

  postgres-exporter:
    image: wrouesnel/postgres_exporter:latest
    container_name: monitoring-postgres-exporter
    restart: unless-stopped
    environment:
      DATA_SOURCE_NAME: "postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@db:5432/\${POSTGRES_DB}?sslmode=disable"
    ports:
      - "9187:9187"
    networks:
      - monitoring
      - mayra_network_prod

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: monitoring-redis-exporter
    restart: unless-stopped
    environment:
      REDIS_ADDR: "redis:6379"
      REDIS_PASSWORD: "\${REDIS_PASSWORD}"
    ports:
      - "9121:9121"
    networks:
      - monitoring
      - mayra_network_prod

  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: monitoring-blackbox-exporter
    restart: unless-stopped
    volumes:
      - ./blackbox.yml:/etc/blackbox_exporter/config.yml
    ports:
      - "9115:9115"
    networks:
      - monitoring
      - mayra_network_prod

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
  mayra_network_prod:
    external: true
EOF

    # Create blackbox exporter config
    cat > "$MONITORING_PATH/blackbox.yml" <<EOF
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200, 201, 202, 204]
      method: GET
      no_follow_redirects: false
      fail_if_ssl: false
      fail_if_not_ssl: false
      tls_config:
        insecure_skip_verify: false
EOF

    success "Monitoring docker-compose created"
}

# Start monitoring stack
start_monitoring() {
    log "Starting monitoring stack..."
    
    cd "$MONITORING_PATH"
    
    # Pull images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 30
    
    # Check services
    docker-compose ps
    
    success "Monitoring stack started"
}

# Print access information
print_access_info() {
    echo ""
    echo "========================================"
    echo "   Monitoring Setup Complete"
    echo "========================================"
    echo ""
    echo "📊 Access URLs:"
    echo "- Prometheus: http://$(curl -s ifconfig.me):9090"
    echo "- Grafana: http://$(curl -s ifconfig.me):3000"
    echo "  Username: admin"
    echo "  Password: ${GRAFANA_ADMIN_PASSWORD}"
    echo "- Alertmanager: http://$(curl -s ifconfig.me):9093"
    echo ""
    echo "📈 Exporters:"
    echo "- Node Exporter: http://localhost:9100/metrics"
    echo "- PostgreSQL Exporter: http://localhost:9187/metrics"
    echo "- Redis Exporter: http://localhost:9121/metrics"
    echo "- cAdvisor: http://localhost:8080/metrics"
    echo ""
    echo "🔔 Alerts:"
    echo "- System alerts configured"
    echo "- Application alerts configured"
    echo "- Backup alerts configured"
    echo ""
    echo "📝 Configuration files:"
    echo "- Prometheus: $MONITORING_PATH/prometheus/prometheus.yml"
    echo "- Alertmanager: $MONITORING_PATH/alertmanager/alertmanager.yml"
    echo "- Alert rules: $MONITORING_PATH/prometheus/rules/"
    echo ""
}

# Main setup flow
main() {
    log "Starting Sistema Mayra monitoring setup..."
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then 
        error "Please run as root (use sudo)"
    fi
    
    # Load environment variables
    if [ -f "$PROJECT_PATH/.env" ]; then
        export $(grep -v '^#' "$PROJECT_PATH/.env" | xargs)
    fi
    
    # Execute setup steps
    setup_directories
    configure_prometheus
    create_alert_rules
    configure_alertmanager
    configure_grafana
    create_monitoring_compose
    start_monitoring
    
    # Print access information
    print_access_info
    
    success "Monitoring setup completed!"
}

# Run main function
main "$@"