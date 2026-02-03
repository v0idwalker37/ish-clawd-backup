#!/bin/bash

# UnGouge Digest - Episode Publisher
# Complete automation script for extracting audio from YouTube and preparing for Anchor.fm
# Usage: ./publish_episode.sh "YOUTUBE_URL" "Episode Title"

set -e  # Exit on error

# Configuration
YOUTUBE_URL=$1
EPISODE_TITLE=$2
DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
OUTPUT_DIR="./podcast_episodes"
SANITIZED_TITLE=$(echo "$EPISODE_TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_-')
FILENAME="ungouge_digest_${DATE}_${SANITIZED_TITLE}.mp3"
FULL_PATH="${OUTPUT_DIR}/${FILENAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Usage check
if [ -z "$YOUTUBE_URL" ] || [ -z "$EPISODE_TITLE" ]; then
    echo ""
    echo "UnGouge Digest - Episode Publisher"
    echo "=================================="
    echo ""
    echo "Usage: ./publish_episode.sh \"YOUTUBE_URL\" \"Episode Title\""
    echo ""
    echo "Examples:"
    echo "  ./publish_episode.sh \"https://youtube.com/watch?v=abc123\" \"AI Hype Reality Check\""
    echo "  ./publish_episode.sh \"https://youtu.be/abc123\" \"Big Tech Antitrust Update\""
    echo ""
    exit 1
fi

# Check dependencies
print_step "Checking dependencies..."

command -v yt-dlp >/dev/null 2>&1 || {
    print_error "yt-dlp is not installed"
    echo "Install with: brew install yt-dlp"
    echo "Or visit: https://github.com/yt-dlp/yt-dlp"
    exit 1
}

command -v ffmpeg >/dev/null 2>&1 || {
    print_error "ffmpeg is not installed"
    echo "Install with: brew install ffmpeg"
    exit 1
}

if command -v id3v2 >/dev/null 2>&1; then
    HAS_ID3V2=true
else
    HAS_ID3V2=false
    print_warning "id3v2 not found - metadata will not be added"
    echo "Install with: brew install id3v2"
fi

print_success "All required dependencies found"

# Create output directory
print_step "Creating output directory..."
mkdir -p "$OUTPUT_DIR"
print_success "Output directory ready: $OUTPUT_DIR"

# Download and extract audio
echo ""
print_step "Downloading and extracting audio from YouTube..."
echo "URL: $YOUTUBE_URL"
echo "Output: $FILENAME"
echo ""

yt-dlp -x \
    --audio-format mp3 \
    --audio-quality 192k \
    --add-metadata \
    --embed-thumbnail \
    -o "$FULL_PATH" \
    "$YOUTUBE_URL"

if [ ! -f "$FULL_PATH" ]; then
    print_error "Audio extraction failed - file not created"
    exit 1
fi

print_success "Audio extracted successfully"

# Add ID3 metadata
if [ "$HAS_ID3V2" = true ]; then
    echo ""
    print_step "Adding ID3 metadata..."
    
    id3v2 \
        --artist "Jason Trask" \
        --album "UnGouge Digest" \
        --song "$EPISODE_TITLE" \
        --year "$YEAR" \
        --genre "Podcast" \
        --comment "Tech news without the corporate BS" \
        "$FULL_PATH"
    
    print_success "Metadata added"
fi

# Get file info
FILE_SIZE=$(du -h "$FULL_PATH" | cut -f1)
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FULL_PATH" 2>/dev/null || echo "unknown")

if [ "$DURATION" != "unknown" ]; then
    MINUTES=$(echo "$DURATION / 60" | bc)
    SECONDS=$(echo "$DURATION % 60" | bc)
    DURATION_FORMATTED="${MINUTES}m ${SECONDS}s"
else
    DURATION_FORMATTED="unknown"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Episode ready for upload!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 File: $FULL_PATH"
echo "📊 Size: $FILE_SIZE"
echo "⏱️  Duration: $DURATION_FORMATTED"
echo "🎵 Format: MP3, 192 kbps, 44.1 kHz"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🌐 Log into Anchor.fm"
echo "   → https://anchor.fm"
echo ""
echo "2. 📤 Create new episode"
echo "   → Click 'New episode'"
echo "   → Upload: $FILENAME"
echo ""
echo "3. ✍️  Add episode details"
echo "   → Title: $EPISODE_TITLE"
echo "   → Add description and show notes"
echo "   → Add timestamps"
echo ""
echo "4. 🚀 Publish"
echo "   → Review and publish"
echo ""
echo "5. 📱 Share"
echo "   → Twitter, YouTube, Discord"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
