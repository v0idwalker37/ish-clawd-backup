#!/usr/bin/env bash
# smoke_tests.sh — Post-deploy smoke tests for ungouge-backend
# Usage: ./smoke_tests.sh [SERVICE_URL]
# Returns non-zero on any failure. Logs error_id values from server responses.
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
SERVICE_URL="${1:-}"
PROJECT="${PROJECT_ID:-ungouge-app}"
REGION="${REGION:-us-central1}"

if [ -z "${SERVICE_URL}" ]; then
  SERVICE_URL=$(gcloud run services describe ungouge-backend \
    --region "${REGION}" --project "${PROJECT}" \
    --format "value(status.url)" 2>/dev/null || echo "")
fi

if [ -z "${SERVICE_URL}" ]; then
  echo "ERROR: No service URL. Pass as arg or deploy first."
  exit 1
fi

LOG_PREFIX="[smoke]"
PASS=0
FAIL=0
TOTAL=0

log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

check() {
  local name="$1"
  local expected_code="$2"
  local actual_code="$3"
  local body="$4"
  TOTAL=$((TOTAL + 1))

  if [ "${actual_code}" = "${expected_code}" ]; then
    PASS=$((PASS + 1))
    log "✅ ${name} (HTTP ${actual_code})"
  else
    FAIL=$((FAIL + 1))
    log "❌ ${name} expected HTTP ${expected_code}, got ${actual_code}"
    # Extract error_id if present
    local error_id
    error_id=$(echo "${body}" | grep -oP '"error_id"\s*:\s*"[^"]*"' 2>/dev/null || echo "")
    if [ -n "${error_id}" ]; then
      log "   ${error_id}"
    fi
    # Show first 200 chars of body for debugging
    log "   Body: $(echo "${body}" | head -c 200)"
  fi
}

log "Testing: ${SERVICE_URL}"
echo ""

# ── 1. Health check ──────────────────────────────────────────────────────────
log "--- Health Check ---"
BODY=$(curl -s -w '\n%{http_code}' "${SERVICE_URL}/health" --max-time 15 || echo -e "\n000")
CODE=$(echo "${BODY}" | tail -1)
RESP=$(echo "${BODY}" | sed '$d')
check "GET /health" "200" "${CODE}" "${RESP}"

# ── 2. Register ──────────────────────────────────────────────────────────────
log "--- Register ---"
RAND=$(( RANDOM % 99999 ))
TEST_EMAIL="smoketest+${RAND}@test.ungouge.ai"
TEST_PASS="SmokeTest123!@#${RAND}"

BODY=$(curl -s -w '\n%{http_code}' -X POST "${SERVICE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASS}\",\"name\":\"SmokeTest Corp\"}" \
  --max-time 15 || echo -e "\n000")
CODE=$(echo "${BODY}" | tail -1)
RESP=$(echo "${BODY}" | sed '$d')
# Accept 200, 201, or 409 (already exists) as success
if [ "${CODE}" = "200" ] || [ "${CODE}" = "201" ] || [ "${CODE}" = "409" ]; then
  check "POST /api/v1/auth/register" "${CODE}" "${CODE}" "${RESP}"
else
  check "POST /api/v1/auth/register" "200|201|409" "${CODE}" "${RESP}"
fi

# ── 3. Login ─────────────────────────────────────────────────────────────────
log "--- Login ---"
BODY=$(curl -s -w '\n%{http_code}' -X POST "${SERVICE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASS}\"}" \
  --max-time 15 || echo -e "\n000")
CODE=$(echo "${BODY}" | tail -1)
RESP=$(echo "${BODY}" | sed '$d')
TOKEN=$(echo "${RESP}" | grep -oP '"access_token"\s*:\s*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"//' || echo "")
check "POST /api/v1/auth/login" "200" "${CODE}" "${RESP}"

if [ -z "${TOKEN}" ]; then
  log "WARNING: No auth token obtained, skipping authenticated tests"
  AUTH_HDR=""
else
  AUTH_HDR="Authorization: Bearer ${TOKEN}"
fi

# ── 4. Upload minimal quote (tiny PDF or text) ──────────────────────────────
if [ -n "${AUTH_HDR}" ]; then
  log "--- Upload Quote ---"
  # Create a minimal text file as a quote
  TMP_QUOTE=$(mktemp /tmp/smoke_quote_XXXXXX.txt)
  echo "Roof Replacement Quote - SmokeTest Corp
Date: 2026-02-15
Item: Asphalt Shingles 30yr - 25 squares @ \$350/sq = \$8,750
Item: Underlayment - 25 squares @ \$45/sq = \$1,125
Item: Labor - \$4,500
Total: \$14,375" > "${TMP_QUOTE}"

  BODY=$(curl -s -w '\n%{http_code}' -X POST "${SERVICE_URL}/api/quotes/upload" \
    -H "${AUTH_HDR}" \
    -F "file=@${TMP_QUOTE};type=text/plain" \
    --max-time 30 || echo -e "\n000")
  CODE=$(echo "${BODY}" | tail -1)
  RESP=$(echo "${BODY}" | sed '$d')
  QUOTE_ID=$(echo "${RESP}" | grep -oP '"id"\s*:\s*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"//' || echo "")
  check "POST /api/v1/quotes/upload" "200" "${CODE}" "${RESP}"
  rm -f "${TMP_QUOTE}"

  # ── 5. Analyze quote ─────────────────────────────────────────────────────
  if [ -n "${QUOTE_ID}" ]; then
    log "--- Analyze Quote (id: ${QUOTE_ID}) ---"
    BODY=$(curl -s -w '\n%{http_code}' -X POST "${SERVICE_URL}/api/quotes/${QUOTE_ID}/analyze" \
      -H "${AUTH_HDR}" \
      -H "Content-Type: application/json" \
      --max-time 60 || echo -e "\n000")
    CODE=$(echo "${BODY}" | tail -1)
    RESP=$(echo "${BODY}" | sed '$d')
    # Accept 200 or 202 (async processing)
    if [ "${CODE}" = "200" ] || [ "${CODE}" = "202" ]; then
      check "POST /api/v1/quotes/{id}/analyze" "${CODE}" "${CODE}" "${RESP}"
    else
      check "POST /api/v1/quotes/{id}/analyze" "200|202" "${CODE}" "${RESP}"
    fi

    # ── 6. Request PDF report ────────────────────────────────────────────
    log "--- PDF Report ---"
    BODY=$(curl -s -w '\n%{http_code}' "${SERVICE_URL}/api/quotes/${QUOTE_ID}/report" \
      -H "${AUTH_HDR}" \
      --max-time 30 || echo -e "\n000")
    CODE=$(echo "${BODY}" | tail -1)
    # PDF returns 200; 404 means analysis not ready yet
    if [ "${CODE}" = "200" ] || [ "${CODE}" = "404" ] || [ "${CODE}" = "202" ]; then
      check "GET /api/v1/quotes/{id}/report" "${CODE}" "${CODE}" ""
    else
      RESP=$(echo "${BODY}" | sed '$d')
      check "GET /api/v1/quotes/{id}/report" "200|404|202" "${CODE}" "${RESP}"
    fi
  else
    log "SKIP: analyze + PDF (no quote_id from upload)"
  fi
else
  log "SKIP: upload, analyze, PDF (no auth token)"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
log "═══════════════════════════════════"
log "Results: ${PASS}/${TOTAL} passed, ${FAIL} failed"
log "═══════════════════════════════════"

if [ ${FAIL} -gt 0 ]; then
  exit 1
fi
exit 0
