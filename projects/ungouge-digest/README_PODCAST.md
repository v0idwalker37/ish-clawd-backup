# UnGouge Digest Podcast Distribution

Complete toolkit for turning your YouTube channel into a multi-platform podcast.

---

## 📚 Documentation

This folder contains everything you need to launch and manage the UnGouge Digest podcast:

### 🚀 [QUICK_START.md](QUICK_START.md)
**Start here!** Fastest path from zero to published podcast (2-3 hours).
- Step-by-step setup instructions
- Minimal explanations, maximum action
- Perfect for "just get it done" mode

### 📖 [PODCAST_SETUP_GUIDE.md](PODCAST_SETUP_GUIDE.md)
**Complete reference guide** with detailed explanations (26k words).
- Comprehensive Anchor.fm setup
- Audio extraction techniques (ffmpeg, yt-dlp)
- Platform submission walkthroughs
- Branding guidelines
- Automation workflows
- Troubleshooting section
- Templates and examples

### 📝 [episode_template.md](episode_template.md)
**Copy-paste templates** for every episode.
- Episode description template
- Social media promotion templates
- Production checklist
- Quick reference commands

### 🤖 [publish_episode.sh](publish_episode.sh)
**Automation script** for episode preparation.
- One command to extract audio from YouTube
- Automatic metadata tagging
- Consistent file naming
- Color-coded output with next steps

---

## 🎯 Quick Reference

### Extract Audio from YouTube

**Automated (recommended):**
```bash
./publish_episode.sh "https://youtube.com/watch?v=VIDEO_ID" "Episode Title"
```

**Manual:**
```bash
yt-dlp -x --audio-format mp3 --audio-quality 192k "VIDEO_URL"
```

### Upload to Anchor

1. Log in: https://anchor.fm
2. New episode → Upload MP3
3. Add title, description, show notes
4. Publish

### Promote

- Twitter/X
- YouTube community tab
- Discord (if applicable)

---

## 📊 Workflow Overview

```
YouTube Video
      ↓
Run publish_episode.sh
      ↓
Audio file ready (MP3, 192kbps)
      ↓
Upload to Anchor.fm
      ↓
Add description & show notes
      ↓
Publish
      ↓
Auto-distributes to all platforms
      ↓
Promote on social media
```

**Time per episode:** ~10 minutes after initial setup

---

## 🛠️ Tools Required

### Essential
- **ffmpeg** - Audio/video processing
- **yt-dlp** - YouTube download
- **Anchor.fm account** - Podcast hosting (free)

### Optional
- **id3v2** - MP3 metadata tagging
- **Canva** - Cover art design
- **Zapier/Make** - Advanced automation

### Installation (macOS)
```bash
brew install ffmpeg yt-dlp id3v2
```

---

## 📋 Platform Distribution

Through Anchor.fm, your podcast will automatically appear on:

- ✅ **Spotify** (instant)
- ✅ **Apple Podcasts** (3-5 days)
- ✅ **Google Podcasts** (1-3 days)
- ✅ **Amazon Music** (5-7 days)
- ✅ **Pocket Casts**
- ✅ **Castbox**
- ✅ **Podcast Addict**
- ✅ And 20+ other platforms

**Your RSS feed:** `https://anchor.fm/s/[YOUR-ID]/podcast/rss`

---

## ✅ Setup Checklist

**One-time setup:**
- [ ] Install required tools (ffmpeg, yt-dlp)
- [ ] Create Anchor.fm account
- [ ] Configure podcast (name, description, artwork)
- [ ] Upload first episode
- [ ] Submit to all platforms
- [ ] Claim podcast on Spotify/Apple/Google

**Per episode (recurring):**
- [ ] Extract audio from YouTube video
- [ ] Upload to Anchor
- [ ] Add description and show notes
- [ ] Publish episode
- [ ] Promote on social media

---

## 🎨 Branding Requirements

### Podcast Cover Art
- **Size:** 3000x3000 pixels
- **Format:** JPEG or PNG
- **File size:** Under 500 KB
- **Color space:** RGB
- **Design tip:** High contrast, readable at small sizes

### Audio Specs
- **Format:** MP3 (recommended) or M4A
- **Bitrate:** 192 kbps (sweet spot for speech)
- **Sample rate:** 44.1 kHz
- **Channels:** Stereo or mono

---

## 📈 Analytics & Growth

### Track Performance
- **Spotify for Podcasters:** https://podcasters.spotify.com
- **Apple Podcasts Connect:** https://podcastsconnect.apple.com
- **Google Podcasts Manager:** https://podcastsmanager.google.com

### Key Metrics
- Total plays
- Completion rate (how much people listen)
- Platform breakdown
- Geographic data
- Episode performance comparison

### Growth Tips
1. **Consistency** - Publish on a regular schedule
2. **Cross-promotion** - Mention podcast in YouTube videos
3. **SEO** - Use keywords in titles and descriptions
4. **Reviews** - Ask listeners to leave reviews (helps discovery)
5. **Social proof** - Share milestones (100 downloads, etc.)

---

## 🆘 Troubleshooting

### Common Issues

**"ffmpeg not found"**
```bash
brew install ffmpeg
```

**"Script not executable"**
```bash
chmod +x publish_episode.sh
```

**"Audio quality is poor"**
- Increase bitrate to 256k or 320k
- Check source video quality
- Use `-ab 320k` flag in ffmpeg

**"Anchor upload fails"**
- File too large (max 250 MB)
- Wrong format (use MP3 or M4A)
- Network issue (try again)

**"Podcast not on Apple Podcasts after 5 days"**
- Check artwork size (must be 3000x3000)
- Validate RSS feed: https://podba.se/validate/
- Check Apple Podcasts Connect for rejection notice

---

## 🔗 Useful Links

**Hosting & Distribution:**
- Anchor.fm: https://anchor.fm
- Spotify for Podcasters: https://podcasters.spotify.com
- Apple Podcasts Connect: https://podcastsconnect.apple.com

**Tools:**
- ffmpeg: https://ffmpeg.org
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- Canva (cover art): https://canva.com

**Validation:**
- RSS Feed Validator: https://podba.se/validate/
- Cast Feed Validator: https://www.castfeedvalidator.com/

**Learning:**
- r/podcasting: https://reddit.com/r/podcasting
- Anchor Help: https://help.anchor.fm

---

## 📞 Getting Help

**Questions about this setup?**
- Review the full guide: `PODCAST_SETUP_GUIDE.md`
- Check troubleshooting section
- Test the automation script: `./publish_episode.sh --help`

**Platform-specific issues?**
- Anchor support: help@anchor.fm
- Apple Podcasts: https://help.apple.com/itc/podcasts_connect/
- Spotify: https://support.spotify.com

**Community support:**
- r/podcasting on Reddit
- Podcast Movement community
- YouTube creator forums

---

## 🎯 Goal: Make Podcasting Easy

The barrier to entry for podcasting is **technical setup**, not content creation. You already create great content for YouTube - this toolkit removes the technical friction so you can reach podcast listeners with minimal extra effort.

**After initial setup:**
- 2 minutes: Extract audio
- 5 minutes: Upload and publish
- 3 minutes: Promote

**Total: ~10 minutes per episode**

The hard part (creating the content) is done. The easy part (distribution) should be automated.

---

## 📝 Version History

- **v1.0** (Feb 2026) - Initial release
  - Complete setup guide
  - Automation script
  - Templates for episodes
  - Quick start guide

---

## 🚀 Next Steps

1. **Read QUICK_START.md** if you want to launch ASAP
2. **OR read PODCAST_SETUP_GUIDE.md** if you want to understand everything
3. **Test the automation:** `./publish_episode.sh "URL" "Title"`
4. **Publish your first episode**
5. **Iterate and improve**

---

**Ready to expand your reach? Let's make UnGouge Digest accessible to podcast listeners worldwide.** 🎙️

*Documentation created February 2026*
*Maintained by: Jason Trask / UnGouge Digest*
