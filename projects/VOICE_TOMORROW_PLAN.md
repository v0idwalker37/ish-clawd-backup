# Voice Communication — Tomorrow's Plan
*Prep for Feb 6, 2026 morning session*

## Context
- Jason has Inara until ~3 PM (no school)
- Subaru appointment at 9:15 AM
- May have interruptions — need modular work chunks

## Goal
Get a working voice prototype: Jason talks → I hear and respond → Jason hears me

## Recommended Approach: OpenAI Realtime API

Per Moltbook research (@LobsterBasilisk tested it): ~300ms latency, "feels conversational"

### Phase 1: Web Prototype (30-60 min)
Skip Twilio initially. Get voice working in browser first.

**What we need:**
1. OpenAI API key (Jason has ChatGPT Plus — should have API access)
2. Simple HTML page with WebRTC
3. OpenAI Realtime API WebSocket connection

**Quickstart code:**
```javascript
// OpenAI Realtime API connection
const ws = new WebSocket('wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01', {
  headers: { 'Authorization': 'Bearer ' + OPENAI_API_KEY }
});
```

### Phase 2: Add Twilio for Phone Number (60-90 min)
Once web works, add phone access so Jason can call a real number.

**What we need:**
1. Twilio account (free trial gives $15 credit)
2. Buy a phone number (~$1/mo)
3. Connect Twilio to our WebSocket handler

### Decisions for Jason
1. **OpenAI Realtime vs Custom Pipeline?**
   - Realtime: 300ms latency, uses GPT-4o (not Claude)
   - Custom: 1-2s latency, can use Claude
   - Recommendation: Start with Realtime for the experience

2. **Okay to create Twilio account?**
   - Free tier: $15.50 credit
   - Phone number: ~$1/mo + usage
   - No surprise charges until we discuss

3. **Web prototype first or straight to phone?**
   - Web is faster to prototype
   - Phone is the actual goal
   - Recommendation: Web first (15 min test), then phone

## Files to Create
- `/projects/voice-prototype/` — project folder
- `index.html` — web client
- `server.py` — WebSocket bridge (if needed for Twilio)
- `.env` — API keys (gitignored)

## OpenAI Realtime API Key Details (from docs)

**Connection Methods:**
1. **WebRTC** — ideal for browser/client-side
2. **WebSocket** — ideal for server-side
3. **SIP** — for VoIP telephony (Twilio integration)

**Fastest Path: Agents SDK for TypeScript**
```javascript
import { RealtimeAgent, RealtimeSession } from "@openai/agents/realtime";

const agent = new RealtimeAgent({
  name: "Ish",
  instructions: "You are Ish, Jason's AI assistant...",
});

const session = new RealtimeSession(agent);
await session.connect({ apiKey: "<client-api-key>" });
```

**Ephemeral Keys (for browser use):**
- Generate via: `POST /v1/realtime/client_secrets`
- Returns token like: `ek_68af296e8e408191a1120ab6383263c2`
- Safe for client-side use

**Model:** `gpt-realtime`

**Voice Config:**
```javascript
audio: {
  output: { voice: "marin" }  // or other voices
}
```

**Note:** This uses GPT-4o's realtime model, NOT Claude. For voice calls, that's acceptable since it's about presence, not deep reasoning.

## Links
- OpenAI Realtime API docs: https://platform.openai.com/docs/guides/realtime
- Agents SDK Quickstart: https://openai.github.io/openai-agents-js/guides/voice-agents/quickstart/
- Twilio Voice WebSocket: https://www.twilio.com/docs/voice/twiml/stream
- Research notes: `/projects/VOICE_PROJECT_RESEARCH.md`

## Success Criteria
Jason can speak into something (browser or phone) and hear my voice response within 1 second.
