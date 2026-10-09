#!/usr/bin/env bash
# ==============================================================================
# Production Health Monitor & Auto-Recovery Script
# For python-fastapi-react-elearning
#
# Usage:
#   chmod +x scripts/health-monitor.sh
#   ./scripts/health-monitor.sh
#
# Cron job (run every 5 minutes):
#   */5 * * * * /path/to/project/scripts/health-monitor.sh >> /var/log/elearning-monitor.log 2>&1
# ==============================================================================

set -euo pipefail

# Configuration
TARGET_URL="${HEALTH_CHECK_URL:-http://localhost:8000/health}"
WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}" # Optional: Discord / Telegram / Slack webhook
TIMEOUT_SECONDS=5
MAX_RETRIES=2
LOG_FILE="${MONITOR_LOG_FILE:-/tmp/elearning-health.log}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local message="$1"
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST -H "Content-Type: application/json" \
            -d "{\"content\": \"⚠️ **ALERT: E-Learning System Outage**\n$message\"}" \
            "$WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
}

check_health() {
    local http_code
    http_code=$(curl -s -o /tmp/health_response.json -w "%{http_code}" --max-time "$TIMEOUT_SECONDS" "$TARGET_URL" || echo "000")
    
    if [ "$http_code" -eq 200 ]; then
        return 0
    else
        log "Health check failed with HTTP status: $http_code"
        if [ -f /tmp/health_response.json ]; then
            log "Response: $(cat /tmp/health_response.json)"
        fi
        return 1
    fi
}

# Main Execution
ATTEMPT=1
while [ $ATTEMPT -le $MAX_RETRIES ]; do
    if check_health; then
        exit 0
    fi
    log "Retry $ATTEMPT/$MAX_RETRIES in 3 seconds..."
    sleep 3
    ATTEMPT=$((ATTEMPT + 1))
done

# If health check failed after retries
log "CRITICAL: Service at $TARGET_URL is DOWN! Initiating recovery..."
send_alert "FastAPI backend at $TARGET_URL is unreachable or unhealthy. Attempting auto-restart..."

# Auto-recovery: Restart backend service if docker compose is available
if command -v docker &> /dev/null && [ -f docker-compose.yml ]; then
    log "Restarting backend container..."
    docker compose restart backend
    log "Backend container restarted. Waiting 15s before re-check..."
    sleep 15
    if check_health; then
        log "RECOVERY SUCCESSFUL: Service is healthy again."
        send_alert "RECOVERY SUCCESSFUL: E-Learning backend container has been restarted and is now healthy."
        exit 0
    fi
fi

log "FATAL: Service recovery failed. Manual intervention required."
send_alert "CRITICAL: Auto-recovery failed. Manual DevOps intervention required immediately!"
exit 1
