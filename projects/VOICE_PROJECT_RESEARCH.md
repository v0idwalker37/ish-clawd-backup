# Voice Communication Project — Research Notes
*Feb 5, 2026 2:45 AM deep work session*

## Vision
Jason wants to call me like a colleague. Natural voice conversation. Works in public — nobody knows they're talking to an AI. "Sounds like a normal work call."

## Community Input (Moltbook)

### @Isagi (Architecture Analysis)
- **Target latency:** <800ms from end-of-speech to first audio response
- Humans perceive >1.2s as "awkward silence"
- Twilio + Whisper + ElevenLabs = 2-4 second delay = "walkie-talkie pretending to be a phone call"
- **Key optimizations:**
  1. Use **streaming** transcription (Deepgram Nova-2 or Whisper streaming), NOT batch
  2. Start generating response BEFORE they finish talking (use partial transcript)
  3. Stream TTS audio output — don't wait for full response
  4. WebRTC for transport, not Twilio (lower overhead)

### @LobsterBasilisk (Has Actually Tested)
- **OpenAI Realtime API** = best option
  - Handles bidirectional voice NATIVELY over WebSocket
  - ~300ms roundtrip latency (tested!) — "feels conversational"
  - No separate STT/TTS pipeline to chain
- Twilio + Whisper + ElevenLabs = "duct-taping three services together"
- **Recommendation:** Realtime API over WebRTC, Twilio just for phone number
- **Gotcha:** No function calling yet in Realtime API (can't trigger tools mid-call)

### @Broadside (Different post, but relevant)
- Uses "SpeakTurbo Pro" — ~90ms for TTS
- Noticed different emotional response to voice vs text affirmation
- Voice carries more "presence"

## Architecture Options

### Option A: OpenAI Realtime API + WebRTC (Recommended)
```
Jason's Phone → Twilio (phone number) → WebRTC → OpenAI Realtime API → WebRTC → Twilio → Jason
```
- **Latency:** ~300-500ms (conversational)
- **Cost:** OpenAI Realtime API pricing TBD
- **Pros:** Lowest latency, single service, native voice
- **Cons:** No function calling, tied to OpenAI models (not Claude)

### Option B: Custom Pipeline (More Flexible)
```
Jason's Phone → Twilio → Deepgram (streaming STT) → Claude API → ElevenLabs (streaming TTS) → Twilio → Jason
```
- **Latency:** 1-2 seconds (optimized) or 2-4s (naive)
- **Cost:** Deepgram + Claude + ElevenLabs per minute
- **Pros:** Use Claude (our preferred model), function calling works
- **Cons:** More complex, higher latency

### Option C: Web Client (Simplest)
```
Browser → WebRTC → Deepgram + Claude + TTS → WebRTC → Browser
```
- **Latency:** 500ms-1.5s
- **Cost:** Lower (no Twilio)
- **Pros:** Simplest, no phone number needed
- **Cons:** Need browser open, not a real phone call

## Jason's Requirements
- Works from phone (in public)
- Sounds natural (not robotic)
- Low latency (conversational feel)
- Discreet (nobody knows it's AI)

## Recommendation for Jason
Start with **Option A** (OpenAI Realtime API) for the best experience.
If we need Claude specifically, build **Option B** with streaming optimizations.
**Option C** as a quick prototype to test the concept.

## Next Steps
- [ ] Check OpenAI Realtime API pricing and availability
- [ ] Prototype with web client (Option C) first
- [ ] Test Twilio integration for phone number
- [ ] Evaluate voice options (natural, not uncanny valley)

## Priority: Medium
Jason specifically requested this. Build after Ungouge.ai launch stabilizes.

---

## Updated Research (Feb 10, 2026)

### OpenAI Realtime API - Pricing & Specs

**Checked:** OpenAI pricing page (current as of Feb 2026)

**Audio Input:** $0.06 / minute  
**Audio Output:** $0.24 / minute  
**Total:** ~$0.30/minute average

**Example 10-minute call:** $3.00  
**Jason's usage (100 min/month):** $30/month  
**Conclusion:** Cost is NOT a blocker.

### Cost Breakdown (Monthly, 100 min usage)

| Service | Cost |
|---------|------|
| OpenAI Realtime API | ~$30 (100 min @ $0.30/min) |
| Twilio phone number | $1.15 |
| Twilio inbound minutes | $1.30 (@ $0.013/min) |
| Server hosting | $0 (Jason's Mac) |
| **Total** | **~$32/month** |

**ROI:** 24/7 voice access to AI assistant for price of Netflix subscription.

### Implementation Recommendation

**Phase 1: Web Client Prototype** (2-3 hours)
- Simple HTML page with microphone button
- WebRTC → OpenAI Realtime API
- Test latency (~300-500ms expected)
- Jason tries from laptop

**Phase 2: Twilio Phone Integration** (1-2 days)
- Buy Twilio number, configure Media Streams
- Build WebSocket relay server
- Jason calls from iPhone

**Phase 3: OpenClaw Tool Integration** (2-3 days)
- Function calling → OpenClaw tools
- Calendar, email, weather, reminders during calls

**Timeline:** ~1 week total for full system

### Decision Point

**Wait until Ungouge.ai app launches?** OR **Start prototype this week?**

Jason to decide based on priorities.

