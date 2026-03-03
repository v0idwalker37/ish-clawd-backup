# URGENT: ungouge.ai Containment (Manual, 10–15 min)

Current status (from preflight):
- `ungouge.ai` resolves and returns HTTP 200.
- `robots.txt` still allows indexing and references old sitemap.
- `sitemap.xml` still exposes old URLs.

This should be contained immediately to reduce public/SEO exposure.

## Step 1 — Vercel old project: force sunset mode

In the **old ungouge.ai Vercel project**:
- Add/update env var:
  - `NEXT_PUBLIC_SUNSET_MODE=1` (Production)
- Trigger redeploy.

Expected result:
- `https://ungouge.ai` renders sunset page/maintenance UX.
- `robots.txt` disallow-all behavior active.
- sitemap generation for old domain is empty/noindex-safe.

## Step 2 — Cloudflare temporary redirect safety net (optional but recommended)

If GougeAlert frontend is live:
- Redirect `ungouge.ai/*` -> `https://gougealert.com/$1` (301)

If GougeAlert not live yet:
- Keep traffic on sunset page until new site is live.

## Step 3 — Verify with script

Run:
```bash
/home/ungouge/clawd/projects/gougealert-transition/cutover-preflight.sh
```

Containment pass criteria:
- `ungouge.ai` no longer serves active marketing/product pages.
- `ungouge.ai/robots.txt` blocks indexing.
- `ungouge.ai/sitemap.xml` is empty/suppressed.

## Step 4 — Search Console cleanup

- Add removal requests for top old URLs/domain paths.
- Keep noindex/robots block in place until de-indexing stabilizes.

## Note
I cannot flip Vercel/Cloudflare account settings directly from this session without your authenticated dashboard/CLI access. Everything above is ready for immediate execution once access is available.
