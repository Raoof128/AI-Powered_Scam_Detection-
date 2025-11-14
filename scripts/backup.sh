#!/bin/bash
###############################################################################
# Database Backup Script
# ~~~~~~~~~~~~~~~~~~~~~
#
# Create backups of the database with rotation.
#
# Usage:
#   ./scripts/backup.sh [backup_dir]
#
# Arguments:
#   backup_dir: Directory to store backups (default: backups/)
###############################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${1:-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="scam_detector_${TIMESTAMP}.sql"
KEEP_DAYS=30

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
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

create_backup_directory() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log_info "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

backup_database() {
    log_info "Creating database backup..."

    # Check if postgres container is running
    if ! docker-compose ps postgres | grep -q "Up"; then
        log_error "PostgreSQL container is not running"
        exit 1
    fi

    # Create backup using pg_dump
    docker-compose exec -T postgres pg_dump \
        -U scam_detector \
        -d scam_detector \
        --no-owner \
        --no-acl \
        > "${BACKUP_DIR}/${BACKUP_NAME}"

    # Compress backup
    gzip "${BACKUP_DIR}/${BACKUP_NAME}"

    log_info "Backup created: ${BACKUP_DIR}/${BACKUP_NAME}.gz"
}

get_backup_size() {
    local file="$1"
    local size=$(du -h "$file" | cut -f1)
    echo "$size"
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than $KEEP_DAYS days..."

    count=0
    while IFS= read -r -d '' file; do
        rm "$file"
        count=$((count + 1))
    done < <(find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +$KEEP_DAYS -print0)

    if [ $count -gt 0 ]; then
        log_info "Removed $count old backup(s)"
    else
        log_info "No old backups to remove"
    fi
}

list_backups() {
    log_info "Available backups:"

    if [ -d "$BACKUP_DIR" ]; then
        count=0
        for file in "$BACKUP_DIR"/*.sql.gz; do
            if [ -f "$file" ]; then
                size=$(get_backup_size "$file")
                date=$(stat -c %y "$file" 2>/dev/null || stat -f %Sm "$file" 2>/dev/null)
                echo "  - $(basename "$file") ($size) - $date"
                count=$((count + 1))
            fi
        done

        if [ $count -eq 0 ]; then
            log_warn "No backups found"
        else
            log_info "Total backups: $count"
        fi
    else
        log_warn "Backup directory does not exist"
    fi
}

verify_backup() {
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}.gz"

    log_info "Verifying backup..."

    # Check file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi

    # Check file size
    local size=$(stat -c%s "$backup_file" 2>/dev/null || stat -f%z "$backup_file" 2>/dev/null)
    if [ "$size" -lt 100 ]; then
        log_error "Backup file is too small (${size} bytes)"
        exit 1
    fi

    # Test gzip integrity
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log_error "Backup file is corrupted"
        exit 1
    fi

    log_info "Backup verification passed"
}

###############################################################################
# Main
###############################################################################

main() {
    echo "=================================="
    echo "🗄️  Database Backup Utility"
    echo "=================================="
    echo "Time: $(date)"
    echo ""

    # Create backup directory
    create_backup_directory

    # Create backup
    backup_database

    # Verify backup
    verify_backup

    # Show backup size
    backup_size=$(get_backup_size "${BACKUP_DIR}/${BACKUP_NAME}.gz")
    log_info "Backup size: $backup_size"

    # Cleanup old backups
    cleanup_old_backups

    # List all backups
    echo ""
    list_backups

    echo ""
    log_info "✅ Backup completed successfully!"
}

main "$@"
