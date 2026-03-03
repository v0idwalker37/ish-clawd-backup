# Vercel Cutover Commands (Template)

> Fill placeholders before running. These are mutating commands.

## 1) Link local frontend to new GougeAlert project

```bash
cd /home/ungouge/clawd/projects/ungouge-app/frontend
vercel link
```

## 2) Set env vars for NEW GougeAlert project (production)

```bash
printf "https://gougealert.com" | vercel env add NEXT_PUBLIC_SITE_URL production
printf "https://api.gougealert.com" | vercel env add NEXT_PUBLIC_API_URL production
printf "https://api.gougealert.com" | vercel env add NEXT_PUBLIC_API_ORIGIN production
# Keep unset/absent for new project:
# NEXT_PUBLIC_SUNSET_MODE
```

## 3) Deploy new project

```bash
vercel --prod
```

## 4) For OLD ungouge.ai project (sunset)

> Relink to old project folder context first if needed.

```bash
printf "1" | vercel env add NEXT_PUBLIC_SUNSET_MODE production
vercel --prod
```

## 5) Verify

```bash
/home/ungouge/clawd/projects/gougealert-transition/cutover-preflight.sh
```

## Notes
- This assumes `vercel login` has already been completed on Beast.
- DNS/domain assignment still needs Vercel dashboard + Cloudflare DNS.
