# Deploy Coming Soon Page to Cloudflare Pages

## Option A: Direct Upload (Fastest - 5 min)

1. Go to **https://dash.cloudflare.com** (sign in as V0idwalker@icloud.com)

2. Click **"Workers & Pages"** in the left sidebar

3. Click **"Create application"** → **"Pages"** → **"Upload assets"**

4. Name it: `ungouge-site`

5. Drag and drop the `index.html` file (or this whole folder)

6. Click **"Deploy site"**

7. Once deployed, go to **"Custom domains"** tab

8. Click **"Set up a custom domain"**

9. Enter: `ungouge.ai`

10. Cloudflare will auto-configure DNS (since you own the domain there)

**Done!** Site will be live at https://ungouge.ai within minutes.

---

## Option B: Git-connected (Better for updates)

1. Push `coming-soon/` to a GitHub repo

2. In Cloudflare Pages, connect to GitHub

3. Auto-deploys on every push

---

## After Deploying

- Test: https://ungouge.ai loads correctly
- Test: Email signup shows success message
- Test: Mobile responsive

## To Set Up Real Email Collection

1. Create free account at **formspree.io**
2. Create a form, get the endpoint URL
3. Replace `action="https://formspree.io/f/placeholder"` in index.html
4. Emails will be collected and forwarded to you

---

## Files in This Folder

```
coming-soon/
├── index.html    ← The landing page (upload this)
└── DEPLOY.md     ← These instructions
```

Single file, no build step, no dependencies. Just upload.
