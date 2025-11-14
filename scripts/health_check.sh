#!/bin/bash
###############################################################################
# Health Check Script
# ~~~~~~~~~~~~~~~~~~~
#
# Comprehensive health check for the scam detection platform.
#
# Usage:
#   ./scripts/health_check.sh [host]
#
# Arguments:
#   host: API host (default: http://localhost:8000)
###############################################################################

set -euo pipefail

# Configuration
HOST="${1:-http://localhost:8000}"
TIMEOUT=5

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

###############################################################################
# Helper Functions
###############################################################################

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

###############################################################################
# Health Checks
###############################################################################

check_api_health() {
    log_info "Checking API health..."

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$HOST/health" || echo "000")

    if [ "$response" -eq 200 ]; then
        log_success "API is healthy (HTTP $response)"
        return 0
    else
        log_error "API health check failed (HTTP $response)"
        return 1
    fi
}

check_api_readiness() {
    log_info "Checking API readiness..."

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$HOST/health/ready" || echo "000")

    if [ "$response" -eq 200 ]; then
        log_success "API is ready (HTTP $response)"
        return 0
    else
        log_error "API readiness check failed (HTTP $response)"
        return 1
    fi
}

check_api_liveness() {
    log_info "Checking API liveness..."

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$HOST/health/live" || echo "000")

    if [ "$response" -eq 200 ]; then
        log_success "API is live (HTTP $response)"
        return 0
    else
        log_error "API liveness check failed (HTTP $response)"
        return 1
    fi
}

check_detection_endpoint() {
    log_info "Checking detection endpoint..."

    payload='{"message": "Test message", "message_type": "email"}'
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" \
        -X POST "$HOST/api/v1/detect" \
        -H "Content-Type: application/json" \
        -d "$payload" || echo "000")

    if [ "$response" -eq 200 ]; then
        log_success "Detection endpoint is working (HTTP $response)"
        return 0
    else
        log_error "Detection endpoint check failed (HTTP $response)"
        return 1
    fi
}

check_statistics_endpoint() {
    log_info "Checking statistics endpoint..."

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$HOST/api/v1/stats/overview" || echo "000")

    if [ "$response" -eq 200 ]; then
        log_success "Statistics endpoint is working (HTTP $response)"
        return 0
    else
        log_error "Statistics endpoint check failed (HTTP $response)"
        return 1
    fi
}

check_response_time() {
    log_info "Checking API response time..."

    start_time=$(date +%s%3N)
    curl -s -o /dev/null --max-time "$TIMEOUT" "$HOST/health" || true
    end_time=$(date +%s%3N)

    response_time=$((end_time - start_time))

    if [ "$response_time" -lt 500 ]; then
        log_success "Response time is acceptable (${response_time}ms)"
        return 0
    else
        log_error "Response time is too slow (${response_time}ms)"
        return 1
    fi
}

get_system_info() {
    log_info "Fetching system information..."

    info=$(curl -s --max-time "$TIMEOUT" "$HOST/" || echo "{}")

    if [ -n "$info" ]; then
        echo "$info" | python3 -m json.tool 2>/dev/null || echo "$info"
    fi
}

###############################################################################
# Main
###############################################################################

main() {
    echo "=================================="
    echo "🏥 Health Check Report"
    echo "=================================="
    echo "Target: $HOST"
    echo "Time: $(date)"
    echo ""

    FAILED=0

    # Run all checks
    check_api_health || FAILED=$((FAILED + 1))
    check_api_readiness || FAILED=$((FAILED + 1))
    check_api_liveness || FAILED=$((FAILED + 1))
    check_detection_endpoint || FAILED=$((FAILED + 1))
    check_statistics_endpoint || FAILED=$((FAILED + 1))
    check_response_time || FAILED=$((FAILED + 1))

    echo ""
    echo "=================================="
    echo "📊 System Information"
    echo "=================================="
    get_system_info

    echo ""
    echo "=================================="
    if [ $FAILED -eq 0 ]; then
        log_success "All health checks passed!"
        echo "=================================="
        exit 0
    else
        log_error "$FAILED health check(s) failed"
        echo "=================================="
        exit 1
    fi
}

main "$@"
