#!/usr/bin/env bash
# cf_resend_dns.sh — Cloudflare DNS + Resend domain setup
# Reads CLOUDFLARE_API_TOKEN and RESEND_API_KEY from Secret Manager.
# Idempotent: checks existence before creating, updates if necessary.
#
# Usage:
#   ./cf_resend_dns.sh --zone-id <CF_ZONE_ID> --domain <domain.com> [--vercel-cname <cname.vercel-dns.com>]
set -euo pipefail

LOG_PREFIX="[cf_resend_dns]"
log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

# ── Parse args ───────────────────────────────────────────────────────────────
ZONE_ID=""
DOMAIN=""
VERCEL_CNAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --zone-id) ZONE_ID="$2"; shift 2;;
    --domain) DOMAIN="$2"; shift 2;;
    --vercel-cname) VERCEL_CNAME="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ -z "${ZONE_ID}" ] || [ -z "${DOMAIN}" ]; then
  echo "Usage: $0 --zone-id <ZONE_ID> --domain <domain.com> [--vercel-cname <cname>]"
  exit 1
fi

PROJECT="${PROJECT_ID:-ungouge-app}"

# ── Fetch tokens from Secret Manager (never printed) ─────────────────────────
log "Fetching API tokens from Secret Manager..."
CF_TOKEN=$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN --project="${PROJECT}" 2>/dev/null)
RESEND_KEY=$(gcloud secrets versions access latest --secret=RESEND_API_KEY --project="${PROJECT}" 2>/dev/null)

if [ -z "${CF_TOKEN}" ]; then
  log "ERROR: Could not fetch CLOUDFLARE_API_TOKEN from Secret Manager"
  exit 1
fi

# ── Helper: Cloudflare DNS upsert ────────────────────────────────────────────
cf_upsert_record() {
  local type="$1" name="$2" content="$3" proxied="${4:-false}" ttl="${5:-1}"

  # Check if record exists
  local existing
  existing=$(curl -s -X GET \
    "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?type=${type}&name=${name}" \
    -H "Authorization: Bearer ${CF_TOKEN}" \
    -H "Content-Type: application/json")

  local count
  count=$(echo "${existing}" | grep -oP '"count"\s*:\s*\K[0-9]+' | head -1 || echo "0")

  if [ "${count}" -gt 0 ]; then
    # Update existing record
    local record_id
    record_id=$(echo "${existing}" | grep -oP '"id"\s*:\s*"\K[^"]+' | head -1)
    log "Updating ${type} record: ${name} -> ${content} (id: ${record_id})"
    curl -s -X PUT \
      "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${record_id}" \
      -H "Authorization: Bearer ${CF_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"type\":\"${type}\",\"name\":\"${name}\",\"content\":\"${content}\",\"proxied\":${proxied},\"ttl\":${ttl}}" \
      > /dev/null
  else
    # Create new record
    log "Creating ${type} record: ${name} -> ${content}"
    curl -s -X POST \
      "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
      -H "Authorization: Bearer ${CF_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"type\":\"${type}\",\"name\":\"${name}\",\"content\":\"${content}\",\"proxied\":${proxied},\"ttl\":${ttl}}" \
      > /dev/null
  fi
}

# ── Vercel DNS records ───────────────────────────────────────────────────────
if [ -n "${VERCEL_CNAME}" ]; then
  log "--- Vercel DNS ---"
  # Root domain A record (Vercel's IP for apex domains)
  cf_upsert_record "A" "${DOMAIN}" "76.76.21.21" "false"
  # www CNAME
  cf_upsert_record "CNAME" "www.${DOMAIN}" "${VERCEL_CNAME}" "false"
  log "Vercel DNS records configured"
else
  log "SKIP: No --vercel-cname provided"
fi

# ── Resend domain setup ─────────────────────────────────────────────────────
if [ -n "${RESEND_KEY}" ]; then
  log "--- Resend Domain Setup ---"

  # Check if domain already exists in Resend
  EXISTING_DOMAINS=$(curl -s -X GET "https://api.resend.com/domains" \
    -H "Authorization: Bearer ${RESEND_KEY}" \
    -H "Content-Type: application/json")

  DOMAIN_EXISTS=$(echo "${EXISTING_DOMAINS}" | grep -c "\"${DOMAIN}\"" || echo "0")

  if [ "${DOMAIN_EXISTS}" -gt 0 ]; then
    log "Domain ${DOMAIN} already exists in Resend"
    DOMAIN_ID=$(echo "${EXISTING_DOMAINS}" | grep -oP '"id"\s*:\s*"\K[^"]+' | head -1)
  else
    log "Creating domain ${DOMAIN} in Resend..."
    CREATE_RESP=$(curl -s -X POST "https://api.resend.com/domains" \
      -H "Authorization: Bearer ${RESEND_KEY}" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"${DOMAIN}\"}")
    DOMAIN_ID=$(echo "${CREATE_RESP}" | grep -oP '"id"\s*:\s*"\K[^"]+' | head -1 || echo "")
    log "Domain created: ${DOMAIN_ID}"
  fi

  # Fetch DNS records Resend needs
  if [ -n "${DOMAIN_ID}" ]; then
    log "Fetching Resend DNS requirements for domain ${DOMAIN_ID}..."
    DOMAIN_INFO=$(curl -s -X GET "https://api.resend.com/domains/${DOMAIN_ID}" \
      -H "Authorization: Bearer ${RESEND_KEY}" \
      -H "Content-Type: application/json")

    echo ""
    log "=== Resend DNS Records (add to Cloudflare) ==="
    echo "${DOMAIN_INFO}" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    records = data.get('records', [])
    for r in records:
        rtype = r.get('record_type', r.get('type', ''))
        name = r.get('name', '')
        value = r.get('value', '')
        priority = r.get('priority', '')
        status = r.get('status', '')
        prio_str = f' (priority: {priority})' if priority else ''
        print(f'  {rtype} {name} -> {value}{prio_str} [{status}]')
except Exception as e:
    print(f'  (Could not parse: {e})')
" 2>/dev/null || log "Could not parse domain info"

    # Auto-add DKIM/SPF/MX records to Cloudflare
    log "Auto-adding Resend DNS records to Cloudflare..."
    echo "${DOMAIN_INFO}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
records = data.get('records', [])
for r in records:
    rtype = r.get('record_type', r.get('type', ''))
    name = r.get('name', '')
    value = r.get('value', '')
    priority = r.get('priority', '')
    # Output as tab-separated for bash to consume
    print(f'{rtype}\t{name}\t{value}\t{priority}')
" 2>/dev/null | while IFS=$'\t' read -r rtype rname rvalue rpriority; do
      if [ "${rtype}" = "MX" ]; then
        # MX records need special handling with priority
        log "Adding MX: ${rname} -> ${rvalue} (pri: ${rpriority})"
        curl -s -X POST \
          "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
          -H "Authorization: Bearer ${CF_TOKEN}" \
          -H "Content-Type: application/json" \
          -d "{\"type\":\"MX\",\"name\":\"${rname}\",\"content\":\"${rvalue}\",\"priority\":${rpriority:-10},\"ttl\":1}" \
          > /dev/null 2>&1 || true
      elif [ "${rtype}" = "TXT" ] || [ "${rtype}" = "CNAME" ]; then
        cf_upsert_record "${rtype}" "${rname}" "${rvalue}" "false"
      fi
    done

    log "Resend DNS records added. Verify at: https://resend.com/domains"
  fi
else
  log "SKIP: No RESEND_API_KEY available"
fi

echo ""
log "Done. DNS propagation may take 1-60 minutes."
log "Verify: dig +short ${DOMAIN} && dig +short www.${DOMAIN}"
