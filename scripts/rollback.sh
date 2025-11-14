#!/bin/bash
###############################################################################
# Rollback Script
# ~~~~~~~~~~~~~~
#
# Rollback deployment to previous version.
#
# Usage:
#   ./scripts/rollback.sh [backup_file]
#
# Arguments:
#   backup_file: Path to database backup to restore (optional)
###############################################################################

set -euo pipefail

# Configuration
BACKUP_FILE="${1:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

confirm_rollback() {
    log_warn "⚠️  This will rollback the deployment"

    if [ -n "$BACKUP_FILE" ]; then
        log_warn "Database will be restored from: $BACKUP_FILE"
    fi

    read -p "Are you sure you want to continue? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
}

stop_services() {
    log_info "Stopping current services..."

    docker-compose down

    log_info "Services stopped"
}

restore_database() {
    if [ -n "$BACKUP_FILE" ]; then
        log_info "Restoring database from backup..."

        # Verify backup file exists
        if [ ! -f "$BACKUP_FILE" ]; then
            log_error "Backup file not found: $BACKUP_FILE"
            exit 1
        fi

        # Start only database
        docker-compose up -d postgres
        sleep 5

        # Drop and recreate database
        docker-compose exec -T postgres psql -U scam_detector -c "DROP DATABASE IF EXISTS scam_detector;"
        docker-compose exec -T postgres psql -U scam_detector -c "CREATE DATABASE scam_detector;"

        # Restore from backup
        if [[ "$BACKUP_FILE" == *.gz ]]; then
            gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U scam_detector -d scam_detector
        else
            docker-compose exec -T postgres psql -U scam_detector -d scam_detector < "$BACKUP_FILE"
        fi

        log_info "Database restored successfully"
    else
        log_warn "No backup file specified, skipping database restore"
    fi
}

rollback_migrations() {
    log_info "Rolling back database migrations..."

    # Run migrations down (one step)
    docker-compose run --rm api alembic downgrade -1

    log_info "Migrations rolled back"
}

restart_services() {
    log_info "Restarting services with previous version..."

    # Checkout previous git commit (optional)
    # git checkout HEAD~1

    # Rebuild and restart
    docker-compose up -d --build

    log_info "Services restarted"
}

verify_rollback() {
    log_info "Verifying rollback..."

    sleep 10

    MAX_RETRIES=5
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Health check passed"
            return 0
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Health check attempt $RETRY_COUNT/$MAX_RETRIES failed, retrying..."
        sleep 5
    done

    log_error "Health check failed after $MAX_RETRIES attempts"
    return 1
}

###############################################################################
# Main
###############################################################################

main() {
    echo "=================================="
    echo "🔄 Deployment Rollback"
    echo "=================================="
    echo "Time: $(date)"
    echo ""

    # Confirm rollback
    confirm_rollback

    # Step 1: Stop services
    stop_services

    # Step 2: Restore database (if backup provided)
    restore_database

    # Step 3: Rollback migrations
    if [ -z "$BACKUP_FILE" ]; then
        rollback_migrations
    fi

    # Step 4: Restart services
    restart_services

    # Step 5: Verify
    if ! verify_rollback; then
        log_error "Rollback verification failed"
        exit 1
    fi

    echo ""
    log_info "✅ Rollback completed successfully!"
    log_info "Services are running at: http://localhost:8000"
}

main "$@"
