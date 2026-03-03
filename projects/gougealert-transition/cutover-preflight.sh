#!/usr/bin/env bash
set -euo pipefail

# Read-only preflight checks for GougeAlert cutover.
# No mutating operations.

check_host() {
  local host="$1"
  echo "=== DNS: $host"
  if getent hosts "$host" >/dev/null 2>&1; then
    getent hosts "$host" | head -1
  else
    echo "NOT_RESOLVING"
  fi
}

check_http() {
  local url="$1"
  echo "=== HTTP: $url"
  local out
  if out=$(curl -sSI --max-time 12 "$url" 2>/dev/null); then
    echo "$out" | sed -n '1,12p'
  else
    echo "HTTP_CHECK_FAILED"
  fi
}

check_body_head() {
  local url="$1"
  local lines="${2:-20}"
  echo "=== BODY: $url"
  local out
  if out=$(curl -sSL --max-time 12 "$url" 2>/dev/null); then
    echo "$out" | sed -n "1,${lines}p"
  else
    echo "BODY_CHECK_FAILED"
  fi
}

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Cutover preflight @ $NOW"
echo

# Domains
check_host "gougealert.com"
check_host "www.gougealert.com"
check_host "api.gougealert.com"
check_host "ungouge.ai"
check_host "api.ungouge.ai"

echo
# Core surfaces
check_http "https://gougealert.com"
check_http "https://www.gougealert.com"
check_http "https://ungouge.ai"
check_http "https://api.gougealert.com/health"
check_http "https://api.ungouge.ai/health"

echo
# Indexability controls
check_body_head "https://ungouge.ai/robots.txt" 30
check_body_head "https://ungouge.ai/sitemap.xml" 20
check_body_head "https://gougealert.com/robots.txt" 30
check_body_head "https://gougealert.com/sitemap.xml" 20

echo
echo "Preflight complete."
