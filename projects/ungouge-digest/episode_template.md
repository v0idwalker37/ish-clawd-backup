# Episode Template - UnGouge Digest

Use this template for each new episode. Fill in the blanks and copy/paste into Anchor.fm.

---

## Episode Information

**Episode Number:** [e.g., Episode 12]  
**Title:** [Clear, descriptive, under 60 characters]  
**Publication Date:** [YYYY-MM-DD]  
**Duration:** [XX:XX]  
**YouTube URL:** [Link to video version]

---

## Episode Description (for Anchor.fm)

```
[EPISODE TITLE]

[Write a compelling 2-3 sentence hook that makes people want to listen. What's the most interesting/controversial/important thing covered?]

This week on UnGouge Digest, we're diving into [main theme]. From [story 1] to [story 2], here's everything you need to know about [topic].

⏱️ TIMESTAMPS:
00:00 - Introduction
[XX:XX] - [Story/Topic 1 Title]
[XX:XX] - [Story/Topic 2 Title]
[XX:XX] - [Story/Topic 3 Title]
[XX:XX] - Final Thoughts & Wrap-up

🔗 SOURCES & LINKS:
• [Article/Source Title] - [URL]
• [Article/Source Title] - [URL]
• [Article/Source Title] - [URL]
• [Add more as needed]

💡 KEY TAKEAWAYS:
✓ [Main point or insight #1]
✓ [Main point or insight #2]
✓ [Main point or insight #3]

---

📺 WATCH THE VIDEO VERSION:
[YouTube URL for this specific episode]

🎙️ ABOUT UNGOUGE DIGEST:
Tech news without the corporate BS. No ads, no sponsors, just honest commentary on the stories that matter. Hosted by Jason Trask.

🔔 SUBSCRIBE & FOLLOW:
• YouTube: [Channel URL]
• Twitter: [Handle]
• Website: [URL]
• Community: [Discord/Forum if applicable]

⭐ ENJOYED THIS EPISODE?
Leave a review on Apple Podcasts or Spotify - it helps others discover the show!

#TechNews #Technology #UnGougeDigest #[Add relevant topic tags]

---
Published: [Date]
Duration: [Length]
Episode: [Number]
```

---

## Social Media Promotion

### Twitter/X Post

```
🎙️ New UnGouge Digest episode is live!

[EPISODE TITLE]

[One-line teaser about the most interesting story]

🎧 Listen: [Spotify/Apple/Anchor link]
📺 Watch: [YouTube link]

#TechNews #[Topic] #UnGougeDigest
```

### YouTube Community Post

```
🎙️ Podcast listeners! New episode of UnGouge Digest is now available on all podcast platforms.

Episode: [TITLE]

Topics covered:
• [Story 1]
• [Story 2]
• [Story 3]

Listen on:
🎧 Spotify: [link]
🎧 Apple Podcasts: [link]
🎧 Google Podcasts: [link]
🎧 Or search "UnGouge Digest" on your favorite podcast app!

Already watched the video? The podcast format is perfect for your commute or workout!
```

### Discord/Community Announcement

```
@everyone New episode alert! 🎙️

**[EPISODE TITLE]** is now live on all podcast platforms.

Quick summary: [2-3 sentences about main topics]

🎧 Listen wherever you get podcasts
📺 Or watch on YouTube: [link]

What did you think of [specific story/topic]? Drop your thoughts below! 💬
```

---

## Production Checklist

Use this to ensure you don't miss any steps:

**Pre-Production:**
- [ ] Video published on YouTube
- [ ] Title finalized (under 60 chars, keyword-optimized)
- [ ] Topics/stories documented with timestamps
- [ ] Source links collected

**Audio Processing:**
- [ ] Audio extracted from video (192 kbps MP3)
- [ ] Audio quality checked (no distortion, good levels)
- [ ] Metadata added (artist, title, year, genre)
- [ ] File renamed with consistent naming convention

**Upload to Anchor.fm:**
- [ ] Logged into Anchor
- [ ] New episode created
- [ ] Audio file uploaded successfully
- [ ] Episode title added
- [ ] Full description with timestamps pasted
- [ ] Show notes with source links added
- [ ] Episode artwork added (if using custom per-episode art)
- [ ] Episode type set (Full Episode / Bonus / etc.)
- [ ] Explicit content tag set correctly
- [ ] Publication date/time set

**Post-Production:**
- [ ] Episode published on Anchor
- [ ] Verified episode appears in Anchor feed
- [ ] Checked Spotify for new episode (within hours)
- [ ] Shared on Twitter/X
- [ ] Posted in YouTube Community tab
- [ ] Announced in Discord (if applicable)
- [ ] Added to episode tracking spreadsheet (if you maintain one)

**Weekly/Monthly:**
- [ ] Review analytics (which topics/titles perform best?)
- [ ] Check for listener reviews/comments
- [ ] Respond to feedback
- [ ] Update templates based on learnings

---

## Quick Reference

**Audio Extraction Command:**
```bash
./publish_episode.sh "YOUTUBE_URL" "Episode Title"
```

**Or manual:**
```bash
yt-dlp -x --audio-format mp3 --audio-quality 192k "[URL]"
```

**Metadata Command:**
```bash
id3v2 --artist "Jason Trask" --album "UnGouge Digest" \
      --song "[TITLE]" --year "2026" --genre "Podcast" [FILE.mp3]
```

**Anchor.fm URL:** https://anchor.fm

**RSS Feed URL:** https://anchor.fm/s/[YOUR-ID]/podcast/rss

---

## Episode Ideas / Topics to Cover

Keep a running list of potential topics:

- [ ] [Topic idea 1]
- [ ] [Topic idea 2]
- [ ] [Topic idea 3]

---

## Notes & Lessons Learned

Document what works and what doesn't:

**What's working well:**
- [e.g., Shorter episodes (<30 min) get more completion]
- [e.g., Controversial titles drive more clicks]

**What to improve:**
- [e.g., Add more specific timestamps]
- [e.g., Promote podcast more on YouTube]

**Technical notes:**
- [e.g., 192 kbps is sweet spot for quality/size]
- [e.g., M4A has better compression than MP3]

---

*Template version 1.0 - Update as needed based on your workflow*
