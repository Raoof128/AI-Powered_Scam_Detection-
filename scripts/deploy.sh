#!/bin/bash
###############################################################################
# Deployment Script
# ~~~~~~~~~~~~~~~~~
#
# Automated deployment script for scam detection platform.
#
# Usage:
#   ./scripts/deploy.sh [environment]
#
# Arguments:
#   environment: dev, staging, or production (default: staging)
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-staging}"
PROJECT_NAME="scam-detector"
DOCKER_COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" == "production" ]; then
    DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
fi

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check environment file
    if [ "$ENVIRONMENT" == "production" ] && [ ! -f ".env.production" ]; then
        log_error ".env.production file not found"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

run_tests() {
    log_info "Running tests..."

    if ! pytest tests/ -v --tb=short; then
        log_error "Tests failed. Deployment aborted."
        exit 1
    fi

    log_info "Tests passed"
}

build_images() {
    log_info "Building Docker images..."

    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache

    log_info "Docker images built successfully"
}

backup_database() {
    if [ "$ENVIRONMENT" == "production" ]; then
        log_info "Creating database backup..."

        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"

        # Backup using pg_dump (requires postgres container to be running)
        docker-compose exec -T postgres pg_dump -U scam_detector scam_detector > "$BACKUP_DIR/database.sql"

        log_info "Database backup created: $BACKUP_DIR/database.sql"
    fi
}

run_migrations() {
    log_info "Running database migrations..."

    docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm api alembic upgrade head

    log_info "Migrations completed"
}

deploy() {
    log_info "Deploying to $ENVIRONMENT..."

    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down

    # Start new containers
    log_info "Starting new containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10

    log_info "Deployment completed"
}

run_health_check() {
    log_info "Running health check..."

    MAX_RETRIES=10
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

show_status() {
    log_info "Deployment status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

###############################################################################
# Main Deployment Flow
###############################################################################

main() {
    log_info "Starting deployment for environment: $ENVIRONMENT"

    # Step 1: Check prerequisites
    check_prerequisites

    # Step 2: Run tests (skip in production if using CI/CD)
    if [ "$ENVIRONMENT" != "production" ]; then
        run_tests
    fi

    # Step 3: Backup database (production only)
    backup_database

    # Step 4: Build Docker images
    build_images

    # Step 5: Run database migrations
    run_migrations

    # Step 6: Deploy
    deploy

    # Step 7: Health check
    if ! run_health_check; then
        log_error "Deployment failed health check"
        log_info "Rolling back..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        exit 1
    fi

    # Step 8: Show status
    show_status

    log_info "✅ Deployment successful!"
    log_info "API is running at: http://localhost:8000"
    log_info "Documentation: http://localhost:8000/docs"
}

# Run main function
main "$@"
