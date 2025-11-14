#!/bin/bash
###############################################################################
# Production Setup Script
# ~~~~~~~~~~~~~~~~~~~~~~
#
# Initial setup for production environment.
#
# Usage:
#   ./scripts/setup_production.sh
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}==>${NC} $1\n"
}

generate_secret() {
    openssl rand -hex 32
}

###############################################################################
# Setup Steps
###############################################################################

check_system_requirements() {
    log_step "Checking system requirements"

    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Operating system: Linux ✓"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Operating system: macOS ✓"
    else
        log_warn "Unsupported operating system: $OSTYPE"
    fi

    # Check Docker
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
        log_info "Docker $docker_version ✓"
    else
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        compose_version=$(docker-compose --version | cut -d ' ' -f3 | cut -d ',' -f1)
        log_info "Docker Compose $compose_version ✓"
    else
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check available disk space
    available_space=$(df -h . | awk 'NR==2 {print $4}')
    log_info "Available disk space: $available_space"
}

create_production_env() {
    log_step "Creating production environment file"

    if [ -f ".env.production" ]; then
        log_warn ".env.production already exists"
        read -p "Overwrite? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
            log_info "Skipping environment file creation"
            return
        fi
    fi

    log_info "Generating secure secrets..."

    cat > .env.production << EOF
# Production Environment Configuration
# Generated: $(date)

# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME=Scam Detector API
APP_VERSION=0.1.0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_WORKERS=4

# Security
SECRET_KEY=$(generate_secret)
JWT_SECRET=$(generate_secret)
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://scam_detector:CHANGE_THIS_PASSWORD@postgres:5432/scam_detector
POSTGRES_USER=scam_detector
POSTGRES_PASSWORD=$(generate_secret)
POSTGRES_DB=scam_detector

# Redis
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["https://your-domain.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=alerts@your-domain.com
EOF

    chmod 600 .env.production

    log_info ".env.production created"
    log_warn "⚠️  Please update the following in .env.production:"
    echo "  - POSTGRES_PASSWORD"
    echo "  - ALLOWED_HOSTS"
    echo "  - CORS_ORIGINS"
    echo "  - SMTP credentials (if using email alerts)"
}

create_directories() {
    log_step "Creating required directories"

    mkdir -p data/raw data/processed data/models
    mkdir -p logs
    mkdir -p backups
    mkdir -p monitoring/prometheus monitoring/grafana

    log_info "Directories created"
}

setup_ssl() {
    log_step "SSL/TLS Setup"

    log_info "For production, you should:"
    echo "  1. Obtain SSL certificate (Let's Encrypt recommended)"
    echo "  2. Place certificates in: ssl/cert.pem and ssl/key.pem"
    echo "  3. Update docker-compose.prod.yml with certificate paths"
    echo ""
    echo "Quick setup with Let's Encrypt:"
    echo "  certbot certonly --standalone -d your-domain.com"
}

setup_monitoring() {
    log_step "Setting up monitoring"

    # Create Prometheus config
    cat > monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'scam-detector-api'
    static_configs:
      - targets: ['api:8000']
EOF

    log_info "Prometheus configuration created"

    # Create Grafana datasource
    mkdir -p monitoring/grafana/provisioning/datasources

    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log_info "Grafana configuration created"
}

setup_firewall() {
    log_step "Firewall Configuration"

    log_info "Recommended firewall rules:"
    echo "  - Allow port 80 (HTTP)"
    echo "  - Allow port 443 (HTTPS)"
    echo "  - Allow port 22 (SSH) from trusted IPs only"
    echo "  - Block all other incoming ports"
    echo ""
    echo "Example UFW commands:"
    echo "  sudo ufw allow 80/tcp"
    echo "  sudo ufw allow 443/tcp"
    echo "  sudo ufw allow from YOUR_IP to any port 22"
    echo "  sudo ufw enable"
}

setup_systemd() {
    log_step "Systemd Service Setup (Optional)"

    log_info "To run as a systemd service, create:"
    echo "  /etc/systemd/system/scam-detector.service"
    echo ""
    echo "Example service file:"
    cat << 'EOF'
[Unit]
Description=Scam Detector API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/scam-detector
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
}

setup_backups() {
    log_step "Setting up automated backups"

    log_info "To schedule daily backups, add to crontab:"
    echo "  0 2 * * * /opt/scam-detector/scripts/backup.sh"
    echo ""
    echo "Run: crontab -e"
}

print_next_steps() {
    log_step "Next Steps"

    echo "1. Update .env.production with your configuration"
    echo "2. Review and update docker-compose.prod.yml"
    echo "3. Set up SSL certificates"
    echo "4. Configure firewall rules"
    echo "5. Run database migrations:"
    echo "     docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head"
    echo "6. Deploy the application:"
    echo "     ./scripts/deploy.sh production"
    echo "7. Set up monitoring dashboards"
    echo "8. Configure automated backups"
    echo "9. Test the deployment:"
    echo "     ./scripts/health_check.sh https://your-domain.com"
    echo ""
    log_info "Documentation: See ARCHITECTURE.md and README.md"
}

###############################################################################
# Main
###############################################################################

main() {
    echo "========================================"
    echo "🚀 Production Setup"
    echo "========================================"
    echo ""

    check_system_requirements
    create_production_env
    create_directories
    setup_ssl
    setup_monitoring
    setup_firewall
    setup_systemd
    setup_backups

    echo ""
    echo "========================================"
    log_info "✅ Production setup completed!"
    echo "========================================"
    echo ""

    print_next_steps
}

main "$@"
