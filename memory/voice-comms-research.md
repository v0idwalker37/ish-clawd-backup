# Voice Communication Research — Feb 14, 2026

**Context:** Jason is interested in voice communication for Ish (both inbound and outbound). Two use cases:
1. **Ungouge.ai voice widget** — Customer calls in to discuss their quote report
2. **Personal Ish voice interface** — Jason talks to Ish via phone/computer instead of typing

**Requirements:**
- Low latency (<500ms ideal, <1s acceptable)
- Natural conversation (interruptions, thinking, context awareness)
- Cost-effective (~$0.50-1.00 per 10-min call target)
- Integration with existing tools (MEMORY.md, calendar, email, etc.)

---

## Voice Widget for Ungouge.ai (Customer-Facing)

### Use Case
Customer pays $19.99 → gets PDF report → sees "Talk through your report" button → 10-min voice call with AI agent pre-loaded with their specific quote analysis.

### Technical Options

#### Option 1: OpenAI Realtime API (Recommended)
**Pros:**
- Native real-time voice API (GPT-4o voice mode)
- ~300ms latency
- Handles interruptions, natural conversation
- Built-in function calling (can look up data during call)
- Text + audio input/output

**Cons:**
- Relatively expensive (~$0.06/min input audio, $0.24/min output audio)
- Requires WebSocket connection (not simple REST)
- Still in beta (as of Feb 2026)

**Cost Estimate (10-min call):**
- Input audio: $0.60
- Output audio: $2.40
- Function calls: ~$0.10
- **Total: ~$3.00 per call**

**ROI:**
- Customer paid $19.99
- Report generation: ~$0.50-1.00 (AI analysis)
- Voice call: ~$3.00
- Net: ~$16 per customer with voice enabled
- If 50% use voice: still profitable

**Implementation:**
- Frontend: WebRTC or WebSocket client (React component)
- Backend: OpenAI Realtime API proxy (FastAPI endpoint)
- Context injection: Load quote report JSON into system prompt
- Session timeout: 15 minutes max (prevent runaway costs)

---

#### Option 2: Twilio + Speech-to-Text + LLM + Text-to-Speech (Traditional Pipeline)
**Pros:**
- Phone number-based (no app required, customer calls from any phone)
- More control over each component
- Can use cheaper TTS (ElevenLabs, Google Cloud)

**Cons:**
- Higher latency (3-step pipeline: STT → LLM → TTS = 2-5 seconds)
- More complex to build (multiple API integrations)
- Harder to handle interruptions naturally

**Cost Estimate (10-min call):**
- Twilio phone minutes: $0.013/min × 10 = $0.13
- Speech-to-text (Google Cloud): $0.016/15sec × 40 = $0.64
- LLM (Claude Sonnet): ~$0.40 (estimated 20K tokens)
- Text-to-speech (ElevenLabs): $0.30/min × 5min output = $1.50
- **Total: ~$2.67 per call**

**Tradeoff:** Cheaper but worse UX (latency kills natural conversation).

---

#### Option 3: VAPI.ai (Managed Voice Agent Platform)
**Pros:**
- Fully managed platform
- Low-code setup
- Twilio integration built-in
- Real-time conversation handling
- Custom functions/tools support

**Cons:**
- Markup over raw APIs (~$0.10-0.15/min)
- Less control over voice quality
- Vendor lock-in

**Cost Estimate (10-min call):**
- VAPI platform fee: ~$1.00-1.50
- Underlying services (Twilio + STT + LLM + TTS): ~$2.00-2.50
- **Total: ~$3.00-4.00 per call**

**Verdict:** Similar cost to OpenAI Realtime but less control. Only makes sense if development time is constrained.

---

### Recommendation for Ungouge.ai

**Phase 1 (MVP, 2-3 weeks post-launch):**
- Use OpenAI Realtime API
- Web-only (browser-based voice widget, no phone number)
- 15-minute session limit
- Pre-loaded with quote report context
- **Cost: ~$3/call, acceptable given $19.99 price point**

**Phase 2 (if popular, 2-3 months post-launch):**
- Add Twilio phone number (customers can call from any phone)
- Hybrid approach: OpenAI Realtime for web, Twilio pipeline for phone
- Session recording + transcription (quality assurance + training data)

**Build Time:**
- Phase 1: 2-3 weeks (WebSocket client, backend proxy, context injection)
- Phase 2: +1-2 weeks (Twilio integration, phone routing)

---

## Personal Ish Voice Interface (Jason-Facing)

### Use Case
Jason calls Ish via phone or talks to Ish through his computer (like Siri/Alexa but actually useful).

### Technical Options

#### Option 1: OpenAI Realtime API + Computer Microphone
**Pros:**
- Lowest latency (~300ms)
- Best conversation quality
- Can interrupt, think, respond naturally
- Full access to tools (files, calendar, email, exec, web)

**Cons:**
- Requires app running on Mac
- Not accessible from phone (unless we build mobile app)

**Implementation:**
- Electron app or CLI tool (Node.js + OpenAI SDK)
- Push-to-talk or voice-activated
- Context injection: Load MEMORY.md, recent conversations
- Tool calling: Same tools available in chat (exec, read, write, etc.)

**Cost:**
- ~$3-5 per 10-minute conversation
- At 5 conversations/day × 30 days = $450-750/month
- **Expensive for personal use unless Jason really values it**

---

#### Option 2: Twilio Phone Number + Voice Agent
**Pros:**
- Call Ish from anywhere (iPhone, landline, etc.)
- No app required
- Works even if Mac is off (if agent runs on i9 or cloud)

**Cons:**
- Higher latency (2-5 seconds per response)
- More expensive (Twilio minutes + STT + LLM + TTS)
- Harder to handle complex multi-turn conversations

**Implementation:**
- Twilio phone number ($1/month + $0.013/min)
- Webhook to FastAPI endpoint
- Speech-to-text → Claude/GPT → Text-to-speech
- Context: Load MEMORY.md, session history
- Tools: Limited (can't exec commands over phone for security)

**Cost:**
- $1/month base + ~$3-4 per 10-min call
- If Jason calls 3x/day × 10 min = $270-360/month

**Verdict:** Expensive for personal use.

---

#### Option 3: Voice Memo Transcription + Async Response
**Pros:**
- Cheapest option
- No latency concerns (async workflow)
- Can use existing Telegram voice message feature

**Cons:**
- Not real-time conversation
- Jason records voice → Ish transcribes → Ish responds in text
- Loses conversational back-and-forth

**Implementation:**
- Jason sends Telegram voice message
- Ish transcribes (Whisper API: $0.006/min)
- Ish responds in text (or uses ElevenLabs TTS to respond with voice)

**Cost:**
- Transcription: $0.006/min
- TTS response (optional): $0.30/min
- **Total: ~$0.30-0.50 per minute** (10x cheaper than real-time)

**Use Case:**
- "Ish, remind me to check the Beast Machine status tomorrow at 9 AM"
- "Ish, what's my calendar look like this week?"
- "Ish, summarize my email from the last 2 hours"

**Verdict:** Practical, cheap, good for non-urgent queries.

---

### Recommendation for Personal Use

**Phase 1 (Immediate, no coding required):**
- Use existing Telegram voice message transcription
- Ish transcribes + responds in text or voice (ElevenLabs TTS)
- Cost: ~$0.30/minute (affordable)

**Phase 2 (If Jason wants real-time conversation, 3-4 weeks):**
- Build Mac app (Electron or CLI) with OpenAI Realtime API
- Push-to-talk or always-listening mode
- Full tool access (same as chat)
- Cost: ~$3-5 per 10-min conversation

**Phase 3 (If Jason wants phone access, 2-3 months):**
- Twilio phone number + voice agent
- Call Ish from anywhere
- Limited tools (no exec for security)
- Cost: ~$3-4 per 10-min call

---

## OpenAI Realtime API Deep Dive

**Current Status (Feb 2026):**
- Public beta (released Nov 2024)
- GPT-4o voice mode
- Function calling supported
- Supports interruptions, natural conversation

**Key Features:**
1. **Low latency:** ~300ms (vs. 2-5s for pipeline)
2. **Streaming:** Real-time audio chunks, no waiting for full response
3. **Function calling:** Can trigger tools mid-conversation
4. **Voice activity detection:** Handles interruptions naturally
5. **Text + audio input/output:** Can mix typed messages with voice

**Pricing (as of Feb 2026):**
- Audio input: $100/million tokens ($0.06/min of audio)
- Audio output: $200/million tokens ($0.24/min of audio)
- Text tokens: Standard GPT-4o rates

**Limitations:**
- WebSocket only (no REST API)
- Beta stability (occasional disconnects reported)
- Max session length: 15-30 minutes (OpenAI may cut long sessions)
- No session persistence (can't pause and resume)

**Integration Pattern:**
```javascript
// Backend proxy (FastAPI)
@app.websocket("/voice")
async def voice_proxy(websocket: WebSocket):
    await websocket.accept()
    
    # Connect to OpenAI Realtime API
    openai_ws = await connect_to_openai_realtime()
    
    # Load context (quote report, MEMORY.md, etc.)
    context = load_context(user_id)
    await openai_ws.send_json({
        "type": "session.update",
        "session": {
            "instructions": f"You are Ish helping analyze quote report. Context: {context}",
            "tools": [calendar_tool, email_tool, file_tool],
            "voice": "alloy",  # or nova, shimmer, etc.
        }
    })
    
    # Bidirectional relay
    while True:
        # Client audio → OpenAI
        client_audio = await websocket.receive_bytes()
        await openai_ws.send_json({
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(client_audio).decode()
        })
        
        # OpenAI response → Client
        openai_response = await openai_ws.receive_json()
        if openai_response["type"] == "response.audio.delta":
            audio_chunk = base64.b64decode(openai_response["delta"])
            await websocket.send_bytes(audio_chunk)
        
        # Handle function calls
        if openai_response["type"] == "response.function_call_arguments.done":
            result = await execute_tool(openai_response["call_id"], openai_response["arguments"])
            await openai_ws.send_json({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": openai_response["call_id"],
                    "output": json.dumps(result)
                }
            })
```

**Frontend (React):**
```typescript
// Voice widget component
const VoiceWidget = ({ quoteReportId }) => {
  const [ws, setWs] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  
  const startCall = async () => {
    // Connect to backend proxy
    const socket = new WebSocket('wss://api.ungouge.ai/voice');
    
    // Set up audio recording (Web Audio API)
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioContext = new AudioContext();
    const mediaStreamSource = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    
    processor.onaudioprocess = (e) => {
      const audioData = e.inputBuffer.getChannelData(0);
      // Convert Float32Array to Int16Array, then send
      const pcm16 = convertFloat32ToInt16(audioData);
      socket.send(pcm16.buffer);
    };
    
    mediaStreamSource.connect(processor);
    processor.connect(audioContext.destination);
    
    // Receive and play audio
    socket.onmessage = (event) => {
      const audioChunk = event.data;
      playAudioChunk(audioChunk);
    };
    
    setWs(socket);
    setIsRecording(true);
  };
  
  return (
    <button onClick={startCall} disabled={isRecording}>
      {isRecording ? "In call..." : "Talk through your report"}
    </button>
  );
};
```

---

## Cost Comparison Summary

| Solution | Latency | Cost (10-min) | Use Case |
|----------|---------|---------------|----------|
| **OpenAI Realtime (web)** | ~300ms | ~$3.00 | Ungouge voice widget (customer) |
| **Twilio + Pipeline** | 2-5s | ~$2.67 | Phone-based (legacy feel, budget option) |
| **VAPI.ai** | ~1s | ~$3-4 | Managed, faster dev time |
| **Telegram voice memo** | Async | ~$0.30/min | Personal Ish (non-urgent queries) |
| **Mac app (Realtime)** | ~300ms | ~$3-5 | Personal Ish (real-time conversation) |
| **Twilio phone (personal)** | 2-5s | ~$3-4 | Call Ish from anywhere |

---

## Recommendations

### For Ungouge.ai (Launch + 2-3 weeks):
1. **Ship OpenAI Realtime web widget**
   - Best UX, acceptable cost ($3/call on $19.99 revenue)
   - Pre-loaded with quote report context
   - 15-min session limit
   - Browser-only (no phone number yet)

2. **Monitor usage**
   - If <10% use voice: keep as nice-to-have
   - If >30% use voice: consider phone number (Twilio)
   - Track customer satisfaction (did voice help close deal?)

### For Personal Ish:
1. **Start with Telegram voice memos** (already works, $0.30/min)
   - Jason sends voice message
   - Ish transcribes + responds (text or voice)
   - Good for quick queries, reminders, summaries

2. **Build Mac app if Jason loves voice** (3-4 weeks, $450-750/month)
   - OpenAI Realtime API
   - Push-to-talk or always-listening
   - Full tool access (files, exec, web, etc.)

3. **Add phone number later if needed** (2-3 months, $270-360/month)
   - Call Ish from anywhere
   - Useful if Jason travels or Mac is off

---

## Next Steps

1. **Test OpenAI Realtime API** (proof-of-concept in sandbox)
2. **Build cost tracking** (monitor actual usage vs. estimates)
3. **Customer research** (would Ungouge customers pay extra for voice? or include in $19.99?)
4. **Jason preference poll** (does he want voice interface for personal use? how often would he use it?)

---

*Research date: 2026-02-14 | Researcher: Ish | Focus: Voice communication for Ungouge + personal Ish interface*
