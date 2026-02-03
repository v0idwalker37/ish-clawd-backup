# UnGouge Digest Podcast - Quick Start Guide

**Goal:** Get your podcast live in under 3 hours. This is the shortest path from zero to published.

---

## Prerequisites (15 minutes)

### Install Required Tools

**macOS:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install ffmpeg yt-dlp id3v2
```

**Verify installation:**
```bash
ffmpeg -version
yt-dlp --version
id3v2 --version
```

All three commands should return version information. If not, troubleshoot before continuing.

---

## Step 1: Create Anchor Account (10 minutes)

1. Go to **https://anchor.fm**
2. Click **"Sign up"**
3. Sign in with Spotify (easiest) or create account
4. Verify your email

✅ **Checkpoint:** You're logged into Anchor

---

## Step 2: Set Up Your Podcast (20 minutes)

### Basic Info

1. Click **"Create podcast"** or **"New podcast"**
2. Fill in:
   - **Name:** UnGouge Digest
   - **Category:** Technology
   - **Language:** English
   - **Type:** Episodic

### Description

Copy and customize this:

```
UnGouge Digest - Your weekly dose of tech news without the corporate BS.

Join Jason Trask as he cuts through the noise to bring you the tech stories that actually matter. From AI developments to privacy concerns, from big tech shenanigans to grassroots innovations - we cover it all with a healthy dose of skepticism and a commitment to truth.

No ads. No sponsors. No BS. Just honest tech commentary.

New episodes weekly.
```

### Cover Art

**You need:** 3000x3000 pixel image, JPEG or PNG, under 500 KB

**Quick options:**
- Use Canva's free podcast cover templates: https://canva.com
- Use your YouTube channel art (resize to 3000x3000)
- Create simple text-based design with brand colors

**Upload** the cover art in Anchor settings.

✅ **Checkpoint:** Podcast created, description added, artwork uploaded

---

## Step 3: Prepare Your First Episode (30 minutes)

### Option A: Use the Automation Script (Recommended)

1. Navigate to your ungouge-digest folder:
```bash
cd projects/ungouge-digest
```

2. Run the script with your YouTube URL:
```bash
./publish_episode.sh "YOUR_YOUTUBE_URL" "Your Episode Title"
```

The script will:
- Download the video
- Extract audio (MP3, 192 kbps)
- Add metadata
- Save to `podcast_episodes/` folder

### Option B: Manual Method

```bash
# Download and extract audio in one step
yt-dlp -x --audio-format mp3 --audio-quality 192k "YOUR_YOUTUBE_URL"

# Add metadata
id3v2 --artist "Jason Trask" \
      --album "UnGouge Digest" \
      --song "Your Episode Title" \
      --year "2026" \
      --genre "Podcast" \
      filename.mp3
```

✅ **Checkpoint:** You have an MP3 file ready to upload

---

## Step 4: Upload First Episode (15 minutes)

1. **Log into Anchor:** https://anchor.fm
2. Click **"New episode"**
3. **Upload** your MP3 file (drag and drop or browse)
4. Wait for upload to complete

### Episode Details

**Title:** Keep it clear and under 60 characters
- ✅ Good: "AI Hype vs Reality: What You Need to Know"
- ❌ Too long: "In This Episode We Discuss the Current State of Artificial Intelligence..."

**Description:** Use the template from `episode_template.md` or this quick version:

```
[2-3 sentence summary of what you covered]

⏱️ TIMESTAMPS:
00:00 - Intro
[Add your timestamps]

🔗 LINKS:
[Add source links]

📺 Watch on YouTube: [Your video URL]

#TechNews #Technology #UnGougeDigest
```

**Settings:**
- Episode type: **Full episode**
- Explicit: **No** (unless you use explicit language)
- Season/Episode numbers: Optional

5. Click **"Publish now"** (or schedule for later)

✅ **Checkpoint:** First episode is live on Anchor

---

## Step 5: Distribute to Platforms (10 minutes setup, then wait)

### In Anchor:

1. Go to **Settings → Distribution**
2. Toggle ON for all platforms:
   - ✅ Spotify
   - ✅ Apple Podcasts
   - ✅ Google Podcasts
   - ✅ Amazon Music
   - ✅ All others

3. Click **"Submit"** or **"Distribute"**

**Timeline:**
- **Spotify:** Instant (hours)
- **Apple Podcasts:** 3-5 business days
- **Google Podcasts:** 1-3 days
- **Amazon Music:** 5-7 days

### Save Your RSS Feed URL

1. Go to **Settings → Distribution**
2. Find your RSS feed URL: `https://anchor.fm/s/[YOUR-ID]/podcast/rss`
3. **Save this** - you'll need it to claim your podcast on platforms

✅ **Checkpoint:** Submitted to all major platforms

---

## Step 6: Verify & Monitor (Ongoing)

### After 24 Hours:

Check Spotify:
```
Open Spotify → Search "UnGouge Digest" → Should appear
```

### After 3-5 Days:

Check Apple Podcasts:
```
Open Apple Podcasts app → Search "UnGouge Digest" → Should appear
```

### Claim Your Podcast:

1. **Spotify for Podcasters:** https://podcasters.spotify.com
   - Sign in → Claim your podcast → Access analytics

2. **Apple Podcasts Connect:** https://podcastsconnect.apple.com
   - Sign in → Add your RSS feed → Verify ownership

3. **Google Podcasts Manager:** https://podcastsmanager.google.com
   - Sign in → Add show → Verify ownership

✅ **Checkpoint:** Podcast verified on all platforms

---

## Step 7: Promote (15 minutes per episode)

### Twitter/X

```
🎙️ New podcast episode!

[TITLE]

[One sentence teaser]

Listen: [Link]

#TechNews #UnGougeDigest
```

### YouTube Community Tab

```
🎙️ New podcast episode now available!

Already watched the video? Listen on the go:
🎧 Spotify: [link]
🎧 Apple Podcasts: [link]
🎧 Or search "UnGouge Digest" on your podcast app
```

### In Your Next YouTube Video

Add to description:
```
🎙️ LISTEN AS A PODCAST:
This show is available on all podcast platforms!
Search "UnGouge Digest" on Spotify, Apple Podcasts, Google Podcasts, or anywhere you listen.
```

Mention in your video:
> "By the way, if you prefer podcasts, UnGouge Digest is now available on Spotify, Apple Podcasts, and everywhere else. Just search 'UnGouge Digest'."

✅ **Checkpoint:** Promoted to your audience

---

## Ongoing Workflow (10 minutes per episode)

Once setup is complete, publishing new episodes is fast:

1. **Extract audio** (2 min):
   ```bash
   ./publish_episode.sh "YOUTUBE_URL" "Episode Title"
   ```

2. **Upload to Anchor** (5 min):
   - New episode → Upload MP3 → Add description → Publish

3. **Promote** (3 min):
   - Tweet
   - YouTube community post

**Total time per episode:** ~10 minutes

---

## Troubleshooting Quick Fixes

### "ffmpeg not found"
```bash
brew install ffmpeg
```

### "yt-dlp not found"
```bash
brew install yt-dlp
```

### Upload fails on Anchor
- Check file size (must be under 250 MB)
- Ensure it's MP3 or M4A format
- Try re-encoding:
  ```bash
  ffmpeg -i original.mp3 -c:a libmp3lame -b:a 192k fixed.mp3
  ```

### Podcast not showing on Apple Podcasts after 5 days
- Verify artwork is exactly 3000x3000 px
- Check for rejection email in Apple Podcasts Connect
- Validate RSS feed: https://podba.se/validate/

---

## Next Steps After First Episode

1. **Publish 2-3 more episodes** within first two weeks
   - Builds your catalog
   - Shows you're active
   - Helps with discovery algorithms

2. **Get your first reviews**
   - Ask friends/early listeners to leave honest reviews on Apple Podcasts
   - Reviews help with rankings and discovery

3. **Establish a schedule**
   - Weekly? Bi-weekly?
   - Consistency matters more than frequency

4. **Monitor analytics**
   - Check Spotify for Podcasters weekly
   - See which episodes/topics perform best
   - Adjust titles and descriptions accordingly

---

## Success Checklist

**Setup (one-time):**
- [x] Tools installed (ffmpeg, yt-dlp)
- [x] Anchor account created
- [x] Podcast configured (name, description, art)
- [x] First episode published
- [x] Distributed to all platforms
- [x] RSS feed saved

**Per Episode:**
- [ ] Audio extracted from YouTube
- [ ] Uploaded to Anchor
- [ ] Description and show notes added
- [ ] Published
- [ ] Promoted on social media

**Weekly:**
- [ ] Check analytics
- [ ] Respond to comments/reviews
- [ ] Plan next episode

---

## Time Estimates Summary

| Task | First Time | Ongoing |
|------|-----------|---------|
| Install tools | 15 min | - |
| Anchor setup | 30 min | - |
| Create artwork | 30-60 min | - |
| First episode | 30 min | - |
| Platform submission | 10 min | - |
| **TOTAL SETUP** | **~2-3 hours** | - |
| Per episode | - | **~10 min** |

---

## Resources

**Full Guide:** See `PODCAST_SETUP_GUIDE.md` for detailed explanations

**Episode Template:** See `episode_template.md` for copy-paste templates

**Automation Script:** `./publish_episode.sh` for one-command audio extraction

**Help:**
- Anchor support: https://help.anchor.fm
- ffmpeg docs: https://ffmpeg.org/documentation.html
- yt-dlp docs: https://github.com/yt-dlp/yt-dlp

---

**You've got this!** 🎙️

The hardest part is starting. Once the infrastructure is set up, publishing new episodes becomes routine. Focus on creating great content - the technical stuff is just a few commands.

*Quick Start Guide v1.0 - February 2026*
