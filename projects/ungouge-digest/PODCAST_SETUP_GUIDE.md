# UnGouge Digest Podcast Setup Guide

**Complete Step-by-Step Guide for Distribution**  
*Beginner-friendly | No prior podcast experience required*

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create Your Podcast on Anchor.fm](#step-1-create-your-podcast-on-anchorfm)
4. [Step 2: Extract Audio from YouTube Videos](#step-2-extract-audio-from-youtube-videos)
5. [Step 3: Prepare Your Episodes](#step-3-prepare-your-episodes)
6. [Step 4: Branding & Artwork](#step-4-branding--artwork)
7. [Step 5: Distribution to Major Platforms](#step-5-distribution-to-major-platforms)
8. [Step 6: Automation Workflow](#step-6-automation-workflow)
9. [Templates & Resources](#templates--resources)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide will help you turn your UnGouge Digest YouTube channel into a fully-distributed podcast on Spotify, Apple Podcasts, Amazon Music, and Google Podcasts using **Anchor.fm** (free hosting by Spotify).

**What you'll accomplish:**
- Set up professional podcast hosting (free)
- Extract high-quality audio from your YouTube videos
- Distribute to all major podcast platforms automatically
- Create templates for consistent episode publishing
- Optionally automate the entire workflow

**Time estimate:** 2-3 hours for initial setup, ~10 minutes per episode after automation

---

## Prerequisites

### Required Tools

1. **Anchor.fm Account** (free)
   - Sign up at: https://anchor.fm
   - Use your existing Spotify account or create new

2. **ffmpeg** (free, open-source)
   - **macOS:** `brew install ffmpeg`
   - **Windows:** Download from https://ffmpeg.org/download.html
   - **Linux:** `sudo apt install ffmpeg` or `sudo yum install ffmpeg`
   - **Verify installation:** Run `ffmpeg -version` in terminal

3. **YouTube Video URLs**
   - Your UnGouge Digest video links

4. **Podcast Cover Art**
   - See [Branding Guidelines](#step-4-branding--artwork) below

### Optional Tools for Automation

- **yt-dlp** (YouTube downloader): `brew install yt-dlp` or from https://github.com/yt-dlp/yt-dlp
- **Bash/Shell scripting** knowledge (basic)
- **Cron** or task scheduler for automation

---

## Step 1: Create Your Podcast on Anchor.fm

### 1.1 Sign Up for Anchor

1. Go to https://anchor.fm
2. Click **"Sign up"**
3. Choose sign-up method:
   - Sign in with Spotify (recommended - easier integration)
   - Sign in with Google
   - Use email + password
4. Verify your email if prompted

### 1.2 Create Your Podcast

1. Once logged in, click **"Create podcast"** or **"New podcast"**
2. You'll see a setup wizard - follow along:

**Basic Information:**

```
Podcast Name: UnGouge Digest
```

**Category Selection:**
- Primary: **Technology**
- Secondary (optional): **News** or **Business**

**Language:**
- **English**

**Podcast Type:**
- Choose **Episodic** (newest episodes appear first)

### 1.3 Write Your Podcast Description

Use this template (customize as needed):

```
UnGouge Digest - Your weekly dose of tech news without the corporate BS.

Join Jason Trask as he cuts through the noise to bring you the tech stories that actually matter. From AI developments to privacy concerns, from big tech shenanigans to grassroots innovations - we cover it all with a healthy dose of skepticism and a commitment to truth.

No ads. No sponsors. No BS. Just honest tech commentary for people who care about staying informed without getting gouged by algorithms and corporate interests.

New episodes every week.

🔗 YouTube: [Your YouTube Channel URL]
🐦 Twitter: [Your Twitter Handle]
💬 Join the conversation: [Discord/Community Link if applicable]
```

**Character limits:**
- Title: 60 characters max (for best display)
- Description: 4,000 characters max (but aim for 150-300 for the summary)

### 1.4 Upload Cover Art

See [Step 4: Branding & Artwork](#step-4-branding--artwork) for specifications.

**Quick specs:**
- **3000x3000 pixels** (required by Apple Podcasts)
- JPEG or PNG
- RGB color space
- File size under 500 KB

### 1.5 Configure Settings

**In Anchor Settings:**

1. **Distribution**
   - Enable all platforms (we'll set this up in Step 5)
   
2. **Episode Settings**
   - Default episode type: **Full episodes**
   - Explicit content: Choose based on your language use (probably "No" or "Clean")

3. **Website**
   - Anchor creates a free podcast website for you automatically
   - Customize the URL: `anchor.fm/ungouge-digest` (or similar)

4. **Social Media**
   - Link your Twitter, YouTube, website

5. **RSS Feed**
   - Your RSS feed URL will be: `https://anchor.fm/s/[YOUR-ID]/podcast/rss`
   - You'll find this in Settings → Distribution
   - **Save this URL** - you'll need it for manual platform submissions

---

## Step 2: Extract Audio from YouTube Videos

### 2.1 Basic ffmpeg Method (Recommended)

This extracts audio from already-downloaded YouTube videos.

**Step 1: Download video from YouTube**

If you have the original files, skip to Step 2. Otherwise, use yt-dlp:

```bash
# Install yt-dlp if not already installed
brew install yt-dlp

# Download video
yt-dlp "https://youtube.com/watch?v=VIDEO_ID"
```

**Step 2: Extract audio with ffmpeg**

```bash
# Basic extraction (MP3, 192kbps - good quality)
ffmpeg -i input_video.mp4 -vn -ab 192k -ar 44100 -y output.mp3

# High quality (320kbps)
ffmpeg -i input_video.mp4 -vn -ab 320k -ar 44100 -y output.mp3

# Extract as M4A (AAC - preferred by Apple Podcasts)
ffmpeg -i input_video.mp4 -vn -c:a aac -b:a 192k -ar 44100 -y output.m4a
```

**Parameter breakdown:**
- `-i input_video.mp4` = input file
- `-vn` = no video (audio only)
- `-ab 192k` = audio bitrate (192 kbps is good for speech)
- `-ar 44100` = audio sample rate (44.1 kHz - CD quality)
- `-y` = overwrite output file if exists
- `output.mp3` = output filename

### 2.2 One-Step Download + Extract (yt-dlp)

Download and extract audio in one command:

```bash
# Best audio quality (auto-selects best format)
yt-dlp -x --audio-format mp3 --audio-quality 0 "https://youtube.com/watch?v=VIDEO_ID"

# Specific bitrate (192k recommended for podcasts)
yt-dlp -x --audio-format mp3 --audio-quality 192k "https://youtube.com/watch?v=VIDEO_ID"

# Save with custom filename
yt-dlp -x --audio-format mp3 --audio-quality 192k \
  -o "UnGouge_Digest_Episode_%(upload_date)s.%(ext)s" \
  "https://youtube.com/watch?v=VIDEO_ID"
```

### 2.3 Batch Processing Multiple Videos

Create a file `video_urls.txt` with one YouTube URL per line:

```
https://youtube.com/watch?v=VIDEO_ID_1
https://youtube.com/watch?v=VIDEO_ID_2
https://youtube.com/watch?v=VIDEO_ID_3
```

Then run:

```bash
# Download and extract all
yt-dlp -x --audio-format mp3 --audio-quality 192k -a video_urls.txt

# Or use a loop with ffmpeg
while read url; do
  yt-dlp -x --audio-format mp3 --audio-quality 192k "$url"
done < video_urls.txt
```

### 2.4 Audio Quality Recommendations

**For speech/podcast content:**
- **MP3, 128-192 kbps** = Excellent quality, smaller file size
- **MP3, 320 kbps** = Overkill for speech, but max quality
- **M4A (AAC), 128-192 kbps** = Better compression than MP3, preferred by Apple

**Recommended:** MP3 at 192 kbps - best balance of quality and file size.

### 2.5 Add Metadata (Optional but Recommended)

```bash
# Install id3v2 for MP3 tagging
brew install id3v2

# Add metadata
id3v2 --artist "Jason Trask" \
      --album "UnGouge Digest" \
      --song "Episode Title Here" \
      --year "2026" \
      --genre "Podcast" \
      output.mp3
```

---

## Step 3: Prepare Your Episodes

### 3.1 Episode Naming Convention

Use consistent naming for organization:

```
UnGouge_Digest_YYYY-MM-DD_Episode_Title.mp3
```

Examples:
```
UnGouge_Digest_2026-02-02_AI_Hype_Reality_Check.mp3
UnGouge_Digest_2026-02-09_Big_Tech_Antitrust_Update.mp3
```

### 3.2 Episode Metadata Checklist

Before uploading each episode, prepare:

- ✅ **Episode Title** (clear, descriptive, under 60 chars)
- ✅ **Episode Number** (if using season/episode format)
- ✅ **Description** (see template below)
- ✅ **Show Notes** (timestamps, links, references)
- ✅ **Publication Date**
- ✅ **Episode Type** (Full, Trailer, Bonus)
- ✅ **Explicit Content Tag** (Yes/No)

### 3.3 Episode Description Template

```markdown
[EPISODE TITLE]

[Brief 2-3 sentence summary of the episode]

In this episode:
• Topic/story 1 [timestamp]
• Topic/story 2 [timestamp]
• Topic/story 3 [timestamp]

KEY POINTS:
- Main takeaway 1
- Main takeaway 2
- Main takeaway 3

LINKS & RESOURCES:
• [Link 1 title] - [URL]
• [Link 2 title] - [URL]
• [Link 3 title] - [URL]

---

ABOUT UNGOUGE DIGEST:
Your weekly dose of tech news without the corporate BS. No ads, no sponsors, just honest commentary.

📺 Watch on YouTube: [Channel URL]
🐦 Follow on Twitter: [Handle]
💬 Join the discussion: [Community link]

#TechNews #UnGougeDigest #Technology #[Relevant Tags]
```

### 3.4 Show Notes Best Practices

**Include:**
1. **Timestamps** for easy navigation
   - `00:00 - Intro`
   - `02:15 - Story 1: [Title]`
   - `15:30 - Story 2: [Title]`
   - `28:45 - Closing thoughts`

2. **Source links** for all stories mentioned
3. **Context** for listeners who don't watch video
4. **Call to action** (subscribe, comment, join Discord)

**Character limits:**
- Anchor: 4,000 characters for description
- Apple Podcasts: First ~255 characters show in previews
- **Front-load** the most important info

---

## Step 4: Branding & Artwork

### 4.1 Podcast Cover Art Specifications

**Required specs (Apple Podcasts requirements):**
- **Resolution:** 3000x3000 pixels (minimum 1400x1400, but use 3000x3000)
- **Format:** JPEG or PNG (JPEG preferred for smaller file size)
- **Color space:** RGB (not CMYK)
- **File size:** Under 500 KB
- **Aspect ratio:** 1:1 (perfect square)

**Design guidelines:**
- ✅ High contrast (readable at thumbnail size)
- ✅ Clear, bold text (if using text)
- ✅ No offensive content
- ✅ Avoid complex details (won't show at small sizes)
- ✅ Make it recognizable at 55x55 pixels

**What to include:**
- Podcast name: "UnGouge Digest"
- Tagline (optional): "Tech News Without the BS"
- Visual theme: Modern, tech-focused, trustworthy
- Color scheme: Professional but not corporate

**Design tools:**
- **Canva** (free): Has podcast cover templates
- **Adobe Photoshop** (paid)
- **GIMP** (free, open-source)
- **Figma** (free tier available)

### 4.2 Intro/Outro Suggestions

**Intro (15-30 seconds):**

Option 1 - Short & punchy:
```
[Upbeat tech music sting]
"UnGouge Digest - Tech news without the corporate BS.
I'm Jason Trask, and here's what matters this week."
[Music fades]
```

Option 2 - With tagline:
```
[Electronic/tech theme music]
"This is UnGouge Digest - your weekly dose of tech news 
without the hype, without the sponsors, and without the BS.
I'm Jason Trask. Let's dive in."
[Music transitions]
```

**Outro (20-40 seconds):**

```
[Music fades in]
"That's UnGouge Digest for this week. If you found this valuable,
subscribe on your favorite podcast platform, drop a comment on YouTube,
or join our community at [link].

No algorithms, no corporate overlords - just honest tech coverage.
I'm Jason Trask. Stay informed, stay skeptical."
[Music plays out]
```

**Music resources (royalty-free):**
- **Epidemic Sound** (paid subscription, high quality)
- **Artlist** (paid, unlimited downloads)
- **Free Music Archive** (free, Creative Commons)
- **YouTube Audio Library** (free, no attribution required)
- **Uppbeat** (free tier available)

### 4.3 Episode Artwork (Optional)

Some podcasters create unique artwork for each episode. This is optional but can increase engagement.

**Quick tools:**
- Canva templates
- Photoshop batch actions
- Automated with Bannerbear or similar APIs

---

## Step 5: Distribution to Major Platforms

### 5.1 Automatic Distribution via Anchor

Anchor automatically distributes to:
- ✅ Spotify (instant - owned by Spotify)
- ✅ Apple Podcasts
- ✅ Google Podcasts
- ✅ Amazon Music / Audible
- ✅ Pocket Casts
- ✅ RadioPublic
- ✅ Castbox
- ✅ Podcast Addict
- ✅ And many more...

**How to enable:**

1. Log into Anchor.fm
2. Go to **Settings → Distribution**
3. Toggle on all platforms you want
4. Click **"Distribute"** or **"Submit"**
5. Anchor handles the RSS submission for you

**Timeline:**
- **Spotify:** Instant (same day)
- **Apple Podcasts:** 3-5 business days for first approval
- **Google Podcasts:** 1-3 days
- **Amazon Music:** 5-7 days

**Important:** You must publish at least ONE episode before submitting for distribution.

### 5.2 Manual Submission (If Needed)

If you want more control or need to submit to platforms not covered by Anchor:

#### Apple Podcasts (Manual)

1. Go to https://podcastsconnect.apple.com
2. Sign in with Apple ID
3. Click **"+"** to add a podcast
4. Enter your RSS feed URL: `https://anchor.fm/s/[YOUR-ID]/podcast/rss`
5. Validate feed (Apple checks requirements)
6. Submit for review
7. Wait 3-5 business days for approval

**Requirements:**
- At least 1 published episode
- Valid cover art (3000x3000)
- Complete podcast metadata
- Valid RSS feed

#### Spotify (Manual - if not using Anchor auto-submit)

1. Go to https://podcasters.spotify.com
2. Sign in with Spotify account
3. Click **"Get Started"**
4. Enter RSS feed URL
5. Verify ownership (various methods)
6. Submit

**Note:** If using Anchor, Spotify submission is automatic.

#### Google Podcasts (Manual)

Google Podcasts pulls from Google Podcasts Manager:

1. Go to https://podcastsmanager.google.com
2. Sign in with Google account
3. Click **"Add show"**
4. Enter RSS feed URL
5. Verify ownership (upload file or DNS record)
6. Submit

**Timeline:** Usually appears within 24-48 hours

#### Amazon Music & Audible (Manual)

1. Go to https://podcasters.amazon.com
2. Sign in with Amazon account
3. Click **"Add your podcast"**
4. Enter RSS feed URL
5. Fill in podcast details
6. Submit for review

**Timeline:** 5-7 business days

### 5.3 Verification & Monitoring

After submission, verify your podcast appears:

**Spotify:**
- Search for "UnGouge Digest" in Spotify app
- Check https://open.spotify.com/

**Apple Podcasts:**
- Search in Apple Podcasts app
- Check https://podcasts.apple.com/

**Google Podcasts:**
- Search in Google Podcasts app or web
- Check https://podcasts.google.com/

**Amazon Music:**
- Search in Amazon Music app
- Check https://music.amazon.com/

### 5.4 Claiming Your Podcast

Some platforms allow you to "claim" your podcast for analytics:

- **Spotify for Podcasters:** https://podcasters.spotify.com
- **Apple Podcasts Connect:** https://podcastsconnect.apple.com
- **Google Podcasts Manager:** https://podcastsmanager.google.com
- **Chartable** (analytics): https://chartable.com

**Benefit:** Access to listener data, demographics, retention metrics.

---

## Step 6: Automation Workflow

### 6.1 Manual Workflow (Beginner)

**Time per episode: ~10-15 minutes**

1. Publish video on YouTube
2. Download video or copy URL
3. Extract audio using ffmpeg or yt-dlp
4. Log into Anchor.fm
5. Click **"New episode"**
6. Upload audio file
7. Add title, description, show notes
8. Add episode artwork (if using)
9. Schedule or publish immediately
10. Share on social media

### 6.2 Semi-Automated Workflow (Intermediate)

Create a bash script `publish_episode.sh`:

```bash
#!/bin/bash

# UnGouge Digest - Episode Publisher
# Usage: ./publish_episode.sh "YOUTUBE_URL" "Episode Title"

YOUTUBE_URL=$1
EPISODE_TITLE=$2
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="./podcast_episodes"
FILENAME="UnGouge_Digest_${DATE}_${EPISODE_TITLE// /_}.mp3"

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Download and extract audio
echo "📥 Downloading and extracting audio..."
yt-dlp -x --audio-format mp3 --audio-quality 192k \
  -o "${OUTPUT_DIR}/${FILENAME}" \
  "$YOUTUBE_URL"

# Add metadata
echo "🏷️  Adding metadata..."
id3v2 --artist "Jason Trask" \
      --album "UnGouge Digest" \
      --song "$EPISODE_TITLE" \
      --year "$(date +%Y)" \
      --genre "Podcast" \
      "${OUTPUT_DIR}/${FILENAME}"

echo "✅ Episode ready: ${OUTPUT_DIR}/${FILENAME}"
echo ""
echo "Next steps:"
echo "1. Log into Anchor.fm"
echo "2. Upload: ${FILENAME}"
echo "3. Add description and show notes"
echo "4. Publish!"
```

**Save and make executable:**
```bash
chmod +x publish_episode.sh
```

**Usage:**
```bash
./publish_episode.sh "https://youtube.com/watch?v=VIDEO_ID" "AI Hype Reality Check"
```

### 6.3 Fully Automated Workflow (Advanced)

**Requirements:**
- Anchor.fm API access (limited availability)
- OR Zapier/Make.com integration
- OR RSS-based automation

**Option A: Zapier/Make.com**

1. **Trigger:** New video published on YouTube (RSS feed)
2. **Action 1:** Download video (webhook to server running yt-dlp)
3. **Action 2:** Extract audio (ffmpeg)
4. **Action 3:** Upload to Anchor via API or email
5. **Action 4:** Post notification to social media

**Option B: Custom Script + Cron**

```bash
# Check YouTube RSS feed for new videos
# Extract audio automatically
# Upload to Anchor (manual step still required as of 2026)
# Send notification when ready
```

**Limitation:** As of 2026, Anchor doesn't have a public API for uploading episodes. You'll still need to manually upload to Anchor, but the audio extraction can be automated.

### 6.4 Workflow Diagram

```
YouTube Video Published
        ↓
[Automated] Download video (yt-dlp)
        ↓
[Automated] Extract audio (ffmpeg, 192k MP3)
        ↓
[Automated] Add ID3 metadata
        ↓
[Manual] Upload to Anchor.fm
        ↓
[Manual] Add description & show notes
        ↓
[Manual] Publish episode
        ↓
[Automated] Anchor distributes to all platforms
        ↓
[Automated/Manual] Share on social media
```

---

## Templates & Resources

### Episode Description Template (Detailed)

```markdown
[COMPELLING EPISODE TITLE - Under 60 characters]

[Hook: 1-2 sentence summary that makes people want to listen]

This week on UnGouge Digest, we're diving into [main topic]. From [story 1] to [story 2], here's everything you need to know about [theme].

⏱️ TIMESTAMPS:
00:00 - Introduction
02:15 - [Story 1 Title]
12:30 - [Story 2 Title]
23:45 - [Story 3 Title]
35:00 - Final Thoughts

🔗 SOURCES & LINKS:
• [Article/source title] - [URL]
• [Article/source title] - [URL]
• [Article/source title] - [URL]

💡 KEY TAKEAWAYS:
✓ [Main point 1]
✓ [Main point 2]
✓ [Main point 3]

---

📺 WATCH THE VIDEO VERSION:
[YouTube URL for this episode]

🎙️ ABOUT UNGOUGE DIGEST:
Tech news without the corporate BS. No ads, no sponsors, just honest commentary on the stories that matter. Hosted by Jason Trask.

🔔 SUBSCRIBE & FOLLOW:
• YouTube: [Channel URL]
• Twitter: [Handle]
• Website: [URL]
• Community: [Discord/Forum]

⭐ ENJOYED THIS EPISODE?
Leave a review on Apple Podcasts or Spotify - it helps others discover the show!

#TechNews #Technology #UnGougeDigest #[Topic Keywords]

---
Published: [Date]
Duration: [Length]
Episode: [Number]
```

### Quick Reference Card

**Save this for easy access:**

```
=== UNGOUGE DIGEST QUICK PUBLISH ===

1. EXTRACT AUDIO:
   yt-dlp -x --audio-format mp3 --audio-quality 192k "[URL]"

2. ADD METADATA:
   id3v2 --artist "Jason Trask" --album "UnGouge Digest" \
          --song "[TITLE]" --year "2026" --genre "Podcast" [FILE]

3. UPLOAD TO ANCHOR:
   → anchor.fm → New Episode → Upload → Add details → Publish

4. SHARE:
   → Twitter, YouTube community tab, Discord

RSS FEED: https://anchor.fm/s/[YOUR-ID]/podcast/rss

COVER ART SPECS: 3000x3000 px, RGB, JPEG, <500 KB
AUDIO SPECS: MP3, 192 kbps, 44.1 kHz, mono or stereo
```

### Platform-Specific Guidelines

| Platform | Min Episodes | Review Time | Special Requirements |
|----------|--------------|-------------|---------------------|
| Spotify | 1 | Instant | None (via Anchor) |
| Apple Podcasts | 1 | 3-5 days | 3000x3000 artwork, complete metadata |
| Google Podcasts | 1 | 1-3 days | Ownership verification |
| Amazon Music | 1 | 5-7 days | Complete show description |

---

## Troubleshooting

### Common Issues & Solutions

#### "ffmpeg not found" error

**Solution:**
```bash
# macOS
brew install ffmpeg

# Verify
ffmpeg -version

# If still not found, check PATH
echo $PATH
which ffmpeg
```

#### Audio quality sounds poor

**Solutions:**
1. Increase bitrate: `-ab 256k` or `-ab 320k`
2. Check source quality (YouTube may compress audio)
3. Use AAC instead of MP3: `--audio-format m4a`
4. Ensure sample rate is 44.1 kHz: `-ar 44100`

#### Anchor upload fails

**Common causes:**
- File too large (max 250 MB per episode)
- Unsupported format (use MP3 or M4A)
- Corrupted audio file

**Solution:**
```bash
# Re-encode to ensure compatibility
ffmpeg -i problematic.mp3 -c:a libmp3lame -b:a 192k -ar 44100 fixed.mp3
```

#### Podcast not appearing on Apple Podcasts

**Checklist:**
- ✅ Wait 3-5 business days after submission
- ✅ Verify artwork is exactly 3000x3000 px
- ✅ Check RSS feed is valid: https://podba.se/validate/
- ✅ Ensure at least 1 episode is published
- ✅ Check Apple Podcasts Connect for rejection notice

#### RSS feed errors

**Validation tools:**
- https://podba.se/validate/
- https://www.castfeedvalidator.com/
- https://validator.w3.org/feed/

**Common issues:**
- Invalid XML characters in description
- Missing required fields (title, description, artwork)
- Incorrect enclosure URL (audio file link)

#### Episodes not updating on platforms

**Solutions:**
1. Check RSS feed is updating (view source)
2. Force refresh in platform dashboards
3. Wait 24-48 hours (some platforms cache feeds)
4. Verify Anchor distribution is enabled
5. Check for platform-specific errors in dashboards

### Getting Help

**Anchor Support:**
- Help center: https://help.anchor.fm
- Email: help@anchor.fm
- Twitter: @anchor

**Platform-Specific Support:**
- Apple Podcasts: https://help.apple.com/itc/podcasts_connect/
- Spotify: https://support.spotify.com (podcasters section)
- Google: https://support.google.com/podcast-publishers/

**Community Resources:**
- r/podcasting on Reddit
- Podcast Movement community
- Podcasters' Support Group on Facebook

---

## Next Steps After Setup

### Week 1: Test Everything
1. ✅ Publish first episode as "unlisted" or "test"
2. ✅ Verify it appears on all platforms
3. ✅ Test playback on multiple devices
4. ✅ Check audio quality
5. ✅ Review show notes formatting
6. ✅ Delete test episode or make it Episode 0

### Week 2-4: Build Your Library
1. ✅ Publish 3-5 episodes to build catalog
2. ✅ Establish consistent publishing schedule
3. ✅ Refine your process (templates, scripts)
4. ✅ Gather initial listener feedback

### Month 2+: Grow Your Audience
1. ✅ Claim your podcast on all platforms
2. ✅ Review analytics (which episodes perform best?)
3. ✅ Optimize titles and descriptions based on data
4. ✅ Promote on YouTube (mention podcast in videos)
5. ✅ Cross-promote on social media
6. ✅ Engage with listeners (respond to reviews/comments)
7. ✅ Consider guest appearances on other podcasts

### Ongoing Optimization
- **Monthly:** Review analytics, adjust strategy
- **Quarterly:** Update artwork/branding if needed
- **Yearly:** Evaluate platform performance, consider premium features

---

## Summary Checklist

Use this to track your setup progress:

**Initial Setup:**
- [ ] ffmpeg installed and working
- [ ] yt-dlp installed (optional but recommended)
- [ ] Anchor.fm account created
- [ ] Podcast created on Anchor
- [ ] Cover artwork uploaded (3000x3000 px)
- [ ] Podcast description written
- [ ] Settings configured

**First Episode:**
- [ ] Audio extracted from YouTube video
- [ ] Metadata added (artist, title, etc.)
- [ ] Episode uploaded to Anchor
- [ ] Title and description added
- [ ] Show notes with timestamps
- [ ] Episode published

**Distribution:**
- [ ] Submitted to Spotify (via Anchor)
- [ ] Submitted to Apple Podcasts
- [ ] Submitted to Google Podcasts
- [ ] Submitted to Amazon Music
- [ ] RSS feed URL saved
- [ ] Podcast appears on all platforms

**Ongoing:**
- [ ] Publishing workflow documented
- [ ] Templates saved for reuse
- [ ] Automation script created (optional)
- [ ] Social media promotion plan
- [ ] Analytics tracking setup

---

## Appendix: Technical Specifications

### Audio Specifications by Platform

| Platform | Recommended Format | Bitrate | Sample Rate | Mono/Stereo |
|----------|-------------------|---------|-------------|-------------|
| Spotify | MP3, M4A | 96-320 kbps | 44.1 kHz | Stereo preferred |
| Apple Podcasts | MP3, M4A, AAC | 64-320 kbps | 44.1 kHz | Either |
| Google Podcasts | MP3, M4A | 96-320 kbps | 44.1 kHz | Either |
| Amazon Music | MP3, M4A | 96-320 kbps | 44.1 kHz | Either |

**Universal safe settings:**
- Format: MP3
- Bitrate: 192 kbps (excellent for speech)
- Sample rate: 44100 Hz
- Channels: Stereo (or mono for smaller files)

### File Size Estimates

| Duration | 128 kbps | 192 kbps | 320 kbps |
|----------|----------|----------|----------|
| 15 min | ~14 MB | ~21 MB | ~36 MB |
| 30 min | ~28 MB | ~42 MB | ~72 MB |
| 45 min | ~42 MB | ~63 MB | ~108 MB |
| 60 min | ~56 MB | ~84 MB | ~144 MB |

**Anchor limit:** 250 MB per episode (allows up to ~3 hours at 192 kbps)

### RSS Feed Structure (For Reference)

Your Anchor RSS feed will look like this:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>UnGouge Digest</title>
    <description>[Your podcast description]</description>
    <language>en-us</language>
    <link>[Your podcast website]</link>
    <image>
      <url>[Your cover art URL]</url>
      <title>UnGouge Digest</title>
    </image>
    
    <item>
      <title>[Episode Title]</title>
      <description>[Episode description]</description>
      <pubDate>[Pub date]</pubDate>
      <enclosure url="[Audio file URL]" type="audio/mpeg" length="[bytes]"/>
      <guid>[Unique episode ID]</guid>
    </item>
    
    <!-- More items for each episode -->
  </channel>
</rss>
```

---

## Final Notes

**This is a living document.** As you gain experience and Anchor/platforms update their features, update this guide with your learnings.

**Your first episode won't be perfect** - and that's okay. The important thing is to start, learn, and improve. The technical barriers are low; the hard part is creating great content (which you're already doing with UnGouge Digest).

**Questions?** Review the Troubleshooting section, check Anchor's help docs, or reach out to podcasting communities for support.

---

**Good luck with your podcast launch! 🎙️**

*Guide version 1.0 - Created February 2026*  
*For UnGouge Digest by Jason Trask*
