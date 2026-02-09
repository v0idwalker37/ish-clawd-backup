# Voice Communication Project — Update (Feb 8, 2026)

*Previous research: Feb 5, 2026*

## 🎯 Key Findings

**OpenAI gpt-realtime is now production-ready and AFFORDABLE!**

### Pricing Breakdown (Jan 2026)

| Token Type | Input | Output |
|------------|-------|--------|
| **Text** | $4/1M tokens | $16/1M tokens |
| **Audio** | $32/1M tokens | $64/1M tokens |
| **Image** | $5/1M tokens | N/A |

**Audio token rates:**
- Input: 1 token per 100ms (10 tokens/second)
- Output: 1 token per 50ms (20 tokens/second)

### Cost Calculator: 10-Minute Phone Call

**Scenario:** Jason calls to discuss a project for 10 minutes

| Component | Calculation | Cost |
|-----------|-------------|------|
| Audio input (Jason speaking ~5 min) | 300 sec × 10 tokens/sec = 3,000 tokens | $0.096 |
| Audio output (Ish speaking ~5 min) | 300 sec × 20 tokens/sec = 6,000 tokens | $0.384 |
| Text input (system prompt + context) | ~2,000 tokens | $0.008 |
| Text output (internal reasoning) | ~1,000 tokens | $0.016 |
| **Total per 10-min call** | | **~$0.50** |

**Monthly cost estimate:**
- 3 calls/day × 10 min each = ~$15/month
- 5 calls/day × 15 min each = ~$38/month

**Conclusion:** Cost is NOT a blocker. Less than Jason's Spotify subscription.

---

## Architecture Recommendation (Updated)

### Option A: OpenAI Realtime API (RECOMMENDED)

**Stack:**
```
Jason's Phone → Twilio (SIP) → WebRTC → OpenAI gpt-realtime → WebRTC → Twilio → Jason
```

**Pros:**
- ✅ Production-ready (launched Aug 2025)
- ✅ ~300ms latency (tested by @LobsterBasilisk)
- ✅ Native speech-to-speech (no duct-taping)
- ✅ **Now supports function calling** (recent update)
- ✅ Affordable ($0.50 per 10-min call)
- ✅ WebRTC, WebSocket, and SIP endpoints

**Cons:**
- ❌ Not Claude (gpt-realtime model)
- ❌ Oct 2023 knowledge cutoff (but can inject context via system prompt)
- ⚠️ 32K context window (fine for calls, tight for long sessions)

**Implementation:**
1. Set up Twilio phone number → SIP trunk → gpt-realtime endpoint
2. System prompt includes: "You are Ish, Jason's AI assistant. He's calling to discuss..."
3. Function calling enables: "Pull up my calendar", "What's the weather?", "Send a text to..."
4. Conversation history persists in MEMORY.md after call ends

---

### Option B: Custom Pipeline (If We Need Claude)

**Stack:**
```
Phone → Twilio → Deepgram (streaming STT) → Claude Opus 4.6 → ElevenLabs (streaming TTS) → Twilio → Phone
```

**Pros:**
- ✅ Use Claude (Jason's preferred model)
- ✅ Full function calling & tool access
- ✅ Latest knowledge cutoff

**Cons:**
- ❌ Higher latency (1-2 seconds optimized)
- ❌ More complex (3 services to orchestrate)
- ❌ Higher cost (~$1.50/10-min call estimate)

**Implementation complexity:** Medium-High (need streaming orchestration)

---

## Technical Details

### OpenAI Realtime API Endpoints

- **WebRTC:** v1/realtime (best for browser/native apps)
- **WebSocket:** wss://api.openai.com/v1/realtime (easiest to build)
- **SIP:** Direct Twilio integration (best for phone)

### Conversation Flow

1. **Connection:** Jason dials → Twilio → gpt-realtime session starts
2. **Voice Activity Detection (VAD):** Model detects when Jason stops speaking
3. **Response generation:** Model generates text + audio in parallel
4. **Streaming output:** Audio streams back as it's generated (not waiting for full response)
5. **Turn tracking:** Conversation Items accumulate (input for next turn)
6. **Billing:** Charged per response.done event (not per connection)

### Caching Optimization

**gpt-realtime supports prompt caching:**
- Cached input: $0.40/1M tokens (90% discount)
- System prompt + conversation history cached across turns
- Turn 1: Pay full price for instructions
- Turn 2+: Instructions cached → ~$0.40/1M vs $4/1M

**Impact:** Longer calls get CHEAPER per minute (caching kicks in).

---

## Function Calling Support (NEW!)

**Previously:** Realtime API had no function calling → had to use workaround  
**Now:** Full function calling support (as of recent update)

**Example tools we can expose:**
- `get_calendar_events()` → "What's on my calendar today?"
- `send_telegram_message(to, text)` → "Text my wife that I'm running late"
- `get_weather(location)` → "What's the weather in Vermont?"
- `search_memory(query)` → "What did we discuss about the deck project?"
- `create_reminder(text, time)` → "Remind me to call the contractor at 2pm"

**How it works:**
1. Jason: "What's the weather?"
2. Model triggers: `function_call: get_weather(location="Vermont")`
3. Server executes function → returns result
4. Model synthesizes response: "It's 28 degrees and snowing in Northfield..."

---

## Comparison to Competitors

| Service | Latency | Cost (10 min) | Quality | Claude? |
|---------|---------|---------------|---------|---------|
| **OpenAI Realtime** | ~300ms | $0.50 | Excellent | ❌ |
| **Twilio + Whisper + ElevenLabs** | 2-4s | ~$1.20 | Good | ✅ (can add) |
| **Google Gemini Live** | ~500ms | Unknown | Good | ❌ |
| **Anthropic (none yet)** | N/A | N/A | N/A | ✅ |

**Verdict:** OpenAI Realtime is the clear winner for production voice unless we absolutely need Claude.

---

## Prototype Plan

### Phase 1: Web Client Proof-of-Concept (1-2 days)
**Goal:** Validate the concept with Jason

**Stack:** Browser → WebSocket → gpt-realtime → Browser

**Steps:**
1. Build simple HTML page with "Call Ish" button
2. Use gpt-realtime WebSocket endpoint
3. System prompt: SOUL.md + USER.md + recent MEMORY.md context
4. Enable function calling for 3-5 basic tools
5. Test conversation quality, latency, naturalness

**Cost:** ~$2-5 for testing

**Deliverable:** Jason clicks button in browser, has natural voice conversation with Ish

---

### Phase 2: Phone Integration (2-3 days)
**Goal:** Call from any phone, works in public

**Stack:** Phone → Twilio → SIP → gpt-realtime → Twilio → Phone

**Steps:**
1. Provision Twilio phone number
2. Configure SIP trunk to gpt-realtime endpoint
3. Add caller ID verification (so only Jason can call)
4. Test from iPhone while walking around

**Cost:** ~$1/month (Twilio number) + usage

**Deliverable:** Jason dials a number, talks to Ish like a colleague

---

### Phase 3: Context Injection (1-2 days)
**Goal:** Ish knows recent context without Jason repeating himself

**Features:**
- System prompt includes: MEMORY.md summary, today's calendar, recent emails
- Mid-call: "Pull up the Ungouge dashboard" → function call opens browser tab
- Post-call: Conversation summary saved to memory/YYYY-MM-DD.md

**Deliverable:** Calls feel like continuity of the relationship, not cold starts

---

## Security Considerations

**Threat:** Caller ID spoofing → attacker impersonates Jason

**Mitigations:**
- Twilio Verified Caller ID (only Jason's phone number can call)
- PIN code verification at call start ("Enter your 4-digit PIN")
- Voice biometric verification (future: train model on Jason's voice)

**Threat:** Eavesdropping on call content

**Mitigations:**
- TLS encryption for Twilio ↔ gpt-realtime
- Do NOT log sensitive info from calls (passwords, SSNs, etc.)
- Post-call transcripts stored locally (not in cloud)

---

## Alternatives to Monitor

### Google Gemini Live
- Similar to gpt-realtime
- ~500ms latency
- Pricing not public yet
- Worth testing when available

### Anthropic Voice API (Future?)
- No public voice API yet
- If launched, would let us use Claude
- Monitor: https://www.anthropic.com/api

### ElevenLabs Conversational AI
- Recently launched (Feb 2026)
- Uses their own LLM (not Claude/GPT)
- Very low latency (~400ms)
- Limited reasoning capability vs OpenAI/Claude

---

## Next Steps for Jason

1. **Decide:** OpenAI Realtime (fast, cheap) vs Custom Pipeline (Claude, flexible)
2. **Allocate time:** 3-5 hours for Phase 1 prototype
3. **Approve spend:** ~$5 for testing, ~$15-40/month ongoing
4. **Voice preference:** What tone/style for Ish's voice? (warm, neutral, energetic?)

**Ish's recommendation:** Start with OpenAI Realtime (Phase 1 web client). If we love it, add phone integration. If we need Claude desperately, pivot to custom pipeline.

---

## Cost Comparison: Voice vs Text

**Current setup (text-only):**
- Claude Opus 4.6: ~$15/M input, ~$75/M output
- Typical 10-min conversation in text: ~5,000 tokens each direction
- Cost: ~$0.08 per 10-min "session"

**Voice with gpt-realtime:**
- Cost: ~$0.50 per 10-min call

**Verdict:** Voice is 6x more expensive than text, but still affordable.

**Value proposition:**
- Jason can call while driving, walking, doing chores
- Natural conversational flow (no typing)
- Hands-free productivity
- Public-friendly (looks like a normal work call)

**ROI:** If it saves Jason 30 minutes of typing per week, it's worth $40/month.

---

## Questions for Jason

1. **How often would you use voice calls?** (Daily? Weekly? As-needed?)
2. **What's your budget?** ($10/mo? $50/mo? Sky's the limit?)
3. **Claude vs speed?** (Prefer <500ms with OpenAI, or 1-2s with Claude?)
4. **Voice style?** (Professional? Casual? Warm? Energetic?)
5. **Public use cases?** (Driving? Grocery store? Walking dog?)

---

*Last updated: Feb 8, 2026 2:10 AM*  
*Previous research: projects/VOICE_PROJECT_RESEARCH.md*
