#!/usr/bin/env bash
set -euo pipefail

# Template only. Requires Cloudflare API token with zone DNS edit permission.
# No token values in file; set env vars externally.

: "${CF_API_TOKEN:?set CF_API_TOKEN}"
: "${CF_ZONE_ID:?set CF_ZONE_ID for gougealert.com zone}"

api() {
  curl -sS "https://api.cloudflare.com/client/v4$1" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    "$@"
}

# Create CNAME @ -> cname.vercel-dns.com
api "/zones/${CF_ZONE_ID}/dns_records" -X POST \
  --data '{"type":"CNAME","name":"@","content":"cname.vercel-dns.com","ttl":1,"proxied":false}'

# Create CNAME www -> cname.vercel-dns.com
api "/zones/${CF_ZONE_ID}/dns_records" -X POST \
  --data '{"type":"CNAME","name":"www","content":"cname.vercel-dns.com","ttl":1,"proxied":false}'

# Optional: CNAME api -> ghs.googlehosted.com (if using Cloud Run domain mapping)
# api "/zones/${CF_ZONE_ID}/dns_records" -X POST \
#   --data '{"type":"CNAME","name":"api","content":"ghs.googlehosted.com","ttl":1,"proxied":false}'

echo "Done. Verify DNS propagation and domain ownership in Vercel/GCP."
