#!/bin/bash
# Sistema Mayra - DigitalOcean Droplet Setup Script
# This script sets up a fresh DigitalOcean droplet for the Sistema Mayra deployment

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
LOG_PATH="/var/log/${PROJECT_NAME}"

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        error "Please run as root (use sudo)"
    fi
}

# Update system packages
update_system() {
    log "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        ufw \
        fail2ban \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        python3-pip \
        rsync \
        jq
    
    success "System packages updated"
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Install docker-compose
    DOCKER_COMPOSE_VERSION="2.24.0"
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Verify installation
    docker --version
    docker-compose --version
    
    success "Docker installed successfully"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (change port if needed)
    ufw allow 22/tcp comment 'SSH'
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Allow n8n (if exposed)
    # ufw allow 5678/tcp comment 'n8n'
    
    # Allow monitoring ports (internal only)
    # ufw allow from 10.0.0.0/8 to any port 9090 comment 'Prometheus'
    # ufw allow from 10.0.0.0/8 to any port 3000 comment 'Grafana'
    
    # Enable firewall
    ufw --force enable
    
    success "Firewall configured"
}

# Configure fail2ban
configure_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create jail.local
    cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = admin@yourdomain.com
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2
EOF
    
    # Start and enable fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    success "fail2ban configured"
}

# Create system user
create_system_user() {
    log "Creating system user..."
    
    local username="mayra"
    
    # Create user if not exists
    if ! id "$username" &>/dev/null; then
        useradd -m -s /bin/bash "$username"
        usermod -aG docker "$username"
        
        # Set up SSH key (you should replace this with your actual public key)
        mkdir -p /home/$username/.ssh
        touch /home/$username/.ssh/authorized_keys
        chmod 700 /home/$username/.ssh
        chmod 600 /home/$username/.ssh/authorized_keys
        chown -R $username:$username /home/$username/.ssh
        
        warning "Remember to add your SSH public key to /home/$username/.ssh/authorized_keys"
    else
        log "User $username already exists"
    fi
    
    success "System user configured"
}

# Setup directory structure
setup_directories() {
    log "Setting up directory structure..."
    
    # Create project directories
    mkdir -p "$PROJECT_PATH"
    mkdir -p "$BACKUP_PATH"
    mkdir -p "$LOG_PATH"
    mkdir -p "/etc/$PROJECT_NAME"
    
    # Set permissions
    chown -R mayra:mayra "$PROJECT_PATH"
    chown -R mayra:mayra "$BACKUP_PATH"
    chown -R mayra:mayra "$LOG_PATH"
    
    success "Directory structure created"
}

# Install monitoring tools
install_monitoring() {
    log "Installing monitoring tools..."
    
    # Install Node Exporter for Prometheus
    NODE_EXPORTER_VERSION="1.7.0"
    wget "https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
    tar xvf "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
    cp "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter" /usr/local/bin/
    rm -rf "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64"*
    
    # Create systemd service for node_exporter
    cat > /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=nobody
Group=nogroup
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl start node_exporter
    systemctl enable node_exporter
    
    success "Monitoring tools installed"
}

# Configure swap
configure_swap() {
    log "Configuring swap..."
    
    # Check if swap already exists
    if [ ! -f /swapfile ]; then
        # Create 2GB swap file
        fallocate -l 2G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        
        # Make permanent
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
        
        # Configure swappiness
        echo "vm.swappiness=10" >> /etc/sysctl.conf
        sysctl -p
        
        success "Swap configured (2GB)"
    else
        log "Swap already configured"
    fi
}

# Configure system limits
configure_limits() {
    log "Configuring system limits..."
    
    # Increase file descriptors
    cat >> /etc/security/limits.conf <<EOF
* soft nofile 65535
* hard nofile 65535
* soft nproc 32768
* hard nproc 32768
EOF
    
    # Configure sysctl
    cat >> /etc/sysctl.conf <<EOF
# Network optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30

# Memory optimizations
vm.overcommit_memory = 1
EOF
    
    sysctl -p
    
    success "System limits configured"
}

# Install SSL certificate manager
install_certbot() {
    log "Installing Certbot for SSL certificates..."
    
    snap install core
    snap refresh core
    snap install --classic certbot
    ln -sf /snap/bin/certbot /usr/bin/certbot
    
    success "Certbot installed"
}

# Configure automatic security updates
configure_auto_updates() {
    log "Configuring automatic security updates..."
    
    apt-get install -y unattended-upgrades
    
    cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
EOF
    
    # Enable automatic updates
    echo 'APT::Periodic::Update-Package-Lists "1";' > /etc/apt/apt.conf.d/20auto-upgrades
    echo 'APT::Periodic::Unattended-Upgrade "1";' >> /etc/apt/apt.conf.d/20auto-upgrades
    
    success "Automatic security updates configured"
}

# Setup backup cron
setup_backup_cron() {
    log "Setting up backup cron..."
    
    # Create backup script placeholder
    cat > "$PROJECT_PATH/scripts/deployment/backup.sh" <<'EOF'
#!/bin/bash
# Backup script will be created by deployment process
echo "Backup script not yet configured"
exit 0
EOF
    
    chmod +x "$PROJECT_PATH/scripts/deployment/backup.sh"
    
    # Add to crontab (will be activated after deployment)
    # (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_PATH/scripts/deployment/backup.sh") | crontab -
    
    success "Backup cron prepared"
}

# Print summary
print_summary() {
    echo ""
    echo "========================================"
    echo "   Sistema Mayra Droplet Setup Complete"
    echo "========================================"
    echo ""
    echo "✅ System updated and secured"
    echo "✅ Docker and docker-compose installed"
    echo "✅ Firewall configured (UFW)"
    echo "✅ Fail2ban configured"
    echo "✅ Monitoring tools installed"
    echo "✅ SSL certificate manager installed"
    echo "✅ Automatic updates configured"
    echo ""
    echo "📝 Next steps:"
    echo "1. Add your SSH key to /home/mayra/.ssh/authorized_keys"
    echo "2. Configure your domain DNS to point to this server"
    echo "3. Copy your .env.prod file to the server"
    echo "4. Run the deployment script: ./scripts/deployment/deploy.sh"
    echo ""
    echo "🔒 Security notes:"
    echo "- Change SSH port in /etc/ssh/sshd_config if needed"
    echo "- Review firewall rules with: ufw status"
    echo "- Monitor fail2ban with: fail2ban-client status"
    echo ""
    echo "📊 Server info:"
    echo "- IP: $(curl -s ifconfig.me)"
    echo "- Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo "- Disk: $(df -h / | awk 'NR==2 {print $2}')"
    echo "- CPU: $(nproc) cores"
    echo ""
}

# Main setup flow
main() {
    log "Starting Sistema Mayra droplet setup..."
    
    # Check if running as root
    check_root
    
    # Execute setup steps
    update_system
    install_docker
    configure_firewall
    configure_fail2ban
    create_system_user
    setup_directories
    install_monitoring
    configure_swap
    configure_limits
    install_certbot
    configure_auto_updates
    setup_backup_cron
    
    # Print summary
    print_summary
    
    success "Droplet setup completed!"
    warning "Remember to reboot the system to apply all changes"
}

# Run main function
main "$@"