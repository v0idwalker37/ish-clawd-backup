# Voice Communication Research — OpenAI Realtime API

*Research conducted: 2026-02-12, 3:30-4:00 AM*

## Executive Summary

**Goal:** Enable Jason to call Ish via phone/web for real-time voice conversations about Ungouge quotes, project status, etc.

**Best Option:** OpenAI Realtime API (GPT-4o Realtime)  
**Cost:** ~$0.06/minute audio input + $0.24/minute audio output = **$0.30/minute** (~$5 for 15-min call)  
**Latency:** ~300-500ms (acceptable for conversation)  
**Quality:** Near-human, handles interruptions, natural speech patterns

**ROI for Ungouge:** Massive. Turns $19.99 quote analysis into interactive consultation. Potential upsell: "$9.99 text analysis, $29.99 voice consultation"

---

## Implementation Architecture

### Phase 1: Web Client (Proof of Concept)
**Timeline:** 1-2 weeks  
**Effort:** 8-12 hours  
**Tech Stack:** Next.js frontend + WebSocket connection to OpenAI Realtime API

**Flow:**
1. User clicks "Talk to Ish" on dashboard
2. Frontend requests session token from backend (authenticated)
3. Backend creates ephemeral OpenAI Realtime session, returns token
4. Frontend opens WebSocket to `wss://api.openai.com/v1/realtime`
5. Browser captures microphone, streams audio
6. OpenAI returns audio stream, browser plays via Audio API
7. Session ends, backend logs conversation summary

**Code Sketch (Frontend):**
```javascript
// 1. Request session token
const response = await fetch('/api/voice/start-session', {
  method: 'POST',
  credentials: 'include'
});
const { sessionToken } = await response.json();

// 2. Connect to OpenAI Realtime
const ws = new WebSocket(`wss://api.openai.com/v1/realtime?token=${sessionToken}`);

// 3. Capture microphone
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mediaRecorder = new MediaRecorder(stream);

mediaRecorder.ondataavailable = (event) => {
  // Send audio chunks to OpenAI
  ws.send(event.data);
};

// 4. Receive audio response
ws.onmessage = (event) => {
  const audioData = event.data; // OpenAI audio stream
  playAudio(audioData); // Browser Audio API
};

// 5. End session
function endCall() {
  ws.close();
  mediaRecorder.stop();
  stream.getTracks().forEach(track => track.stop());
}
```

**Code Sketch (Backend):**
```python
from fastapi import APIRouter, Depends
import httpx
import os

router = APIRouter()

@router.post("/api/voice/start-session")
async def start_voice_session(user_info: dict = Depends(require_auth)):
    """Create ephemeral OpenAI Realtime session"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-realtime",
                "instructions": f"You are Ish, assistant to {user_info['name']}. Help with Ungouge.ai questions, project status, quote analysis.",
                "voice": "nova",
                "modalities": ["text", "audio"],
                "turn_detection": {"type": "server_vad"}  # Voice Activity Detection
            }
        )
        
        session_data = response.json()
        
        # Log session start
        log_voice_session(user_info['email'], session_data['id'], "started")
        
        return {
            "sessionToken": session_data['client_secret']['value'],
            "sessionId": session_data['id']
        }

@router.post("/api/voice/end-session")
async def end_voice_session(session_id: str, user_info: dict = Depends(require_auth)):
    """End session and log summary"""
    
    # Fetch conversation transcript from OpenAI
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.openai.com/v1/realtime/sessions/{session_id}",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        )
        
        session_data = response.json()
        
        # Log to database
        log_voice_session(
            user_info['email'],
            session_id,
            "ended",
            duration=session_data['duration_seconds'],
            cost=session_data['usage']['total_cost']
        )
        
        return {"status": "ended", "duration": session_data['duration_seconds']}
```

**Pros:**
- Fast to build (1-2 weeks)
- No phone infrastructure needed
- Works on desktop + mobile browsers
- Full control over UI/UX

**Cons:**
- Requires browser (not true phone call)
- Internet connection required (WiFi or data)
- User must navigate to website

---

### Phase 2: Twilio Integration (Real Phone Calls)
**Timeline:** 3-4 weeks after Phase 1  
**Effort:** 12-16 hours  
**Tech Stack:** Twilio Voice + OpenAI Realtime API + SIP bridge

**Flow:**
1. User calls Ungouge phone number (e.g., 1-800-UNGOUGE)
2. Twilio receives call, initiates webhook to our backend
3. Backend creates OpenAI Realtime session
4. Twilio streams audio to/from OpenAI via WebSocket
5. User talks to Ish over phone (PSTN)
6. Call ends, backend logs transcript + cost

**Twilio TwiML (call routing):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">
        Connecting you to Ish, your Ungouge assistant.
    </Say>
    <Connect>
        <Stream url="wss://dashboard.ungouge.ai/voice/twilio-stream" />
    </Connect>
</Response>
```

**Backend WebSocket Handler:**
```python
from fastapi import WebSocket
import asyncio
import httpx

@app.websocket("/voice/twilio-stream")
async def twilio_stream(websocket: WebSocket):
    await websocket.accept()
    
    # Parse Twilio metadata
    start_msg = await websocket.receive_json()
    call_sid = start_msg['start']['callSid']
    
    # Create OpenAI Realtime session
    openai_ws = await create_openai_realtime_session()
    
    # Bidirectional audio streaming
    async def twilio_to_openai():
        while True:
            msg = await websocket.receive_json()
            if msg['event'] == 'media':
                audio_chunk = base64.b64decode(msg['media']['payload'])
                await openai_ws.send(audio_chunk)
            elif msg['event'] == 'stop':
                break
    
    async def openai_to_twilio():
        while True:
            audio_chunk = await openai_ws.receive()
            await websocket.send_json({
                "event": "media",
                "media": {
                    "payload": base64.b64encode(audio_chunk).decode()
                }
            })
    
    # Run both streams concurrently
    await asyncio.gather(twilio_to_openai(), openai_to_twilio())
    
    # Cleanup
    await openai_ws.close()
    await websocket.close()
```

**Cost Breakdown (Twilio):**
- Phone number: $1/month
- Inbound calls: $0.0085/minute (US)
- Outbound calls: $0.013/minute (if we call user)
- **Total per 10-min call:** $0.085 (Twilio) + $3.00 (OpenAI) = **$3.09**

**Pros:**
- True phone calls (no browser needed)
- Familiar UX (just dial a number)
- Works on any phone (flip phones, landlines, smartphones)

**Cons:**
- More complex infrastructure
- Twilio costs (small but ongoing)
- Phone number to manage
- Audio quality depends on PSTN (can be poor)

---

### Phase 3: Context Injection (Memory + Tools)
**Timeline:** 2-3 weeks after Phase 2  
**Effort:** 8-12 hours  
**Goal:** Make Ish truly useful during calls (access to Jason's data, tools)

**Context to Inject:**
1. **User profile:** Name, email, recent projects, quote history
2. **Recent activity:** Last 5 dashboard tasks, upcoming calendar events
3. **MEMORY.md:** Jason's preferences, project context, waiting-on list
4. **Tool access:** Query database, create tasks, fetch documents

**Implementation:**
```python
async def build_realtime_context(user_email: str) -> str:
    """Build context string for OpenAI Realtime session"""
    
    # Fetch user data
    user = get_user_by_email(user_email)
    recent_tasks = get_recent_tasks(user_email, limit=5)
    upcoming_events = get_calendar_events(user_email, days_ahead=7)
    memory = read_memory_file()  # MEMORY.md
    
    context = f"""
You are Ish, AI assistant to {user.name}.

## Current Context
- User: {user.name} ({user.email})
- Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
- Location: {user.timezone}

## Recent Work
{format_tasks(recent_tasks)}

## Upcoming Events
{format_events(upcoming_events)}

## Memory (Key Facts)
{extract_key_facts(memory)}

## Available Tools
- create_task(title, description, project, priority)
- get_project_status(project_name)
- analyze_quote(quote_text)
- search_memory(query)

When user asks you to do something, use the appropriate tool and confirm completion.
"""
    
    return context

# In session creation:
session_response = await client.post(
    "https://api.openai.com/v1/realtime/sessions",
    json={
        "model": "gpt-4o-realtime",
        "instructions": await build_realtime_context(user_info['email']),
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task in the dashboard",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "project": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
                        },
                        "required": ["title", "project"]
                    }
                }
            },
            # ... other tools
        ]
    }
)
```

**Tool Execution (Server-Side):**
```python
@app.post("/api/voice/execute-tool")
async def execute_tool(
    session_id: str,
    tool_name: str,
    arguments: dict,
    user_info: dict = Depends(require_auth)
):
    """Execute tool requested by Realtime API"""
    
    if tool_name == "create_task":
        task = create_task_in_db(
            user_email=user_info['email'],
            title=arguments['title'],
            description=arguments.get('description', ''),
            project=arguments['project'],
            priority=arguments.get('priority', 'medium')
        )
        return {"success": True, "task_id": task.id}
    
    elif tool_name == "get_project_status":
        project = get_project_by_name(arguments['project_name'])
        tasks = get_tasks_by_project(project.id)
        return {
            "success": True,
            "status": project.status,
            "task_count": len(tasks),
            "completion_rate": calculate_completion_rate(tasks)
        }
    
    # ... other tools
```

**Result:** Ish can now:
- "Create a task: Review RSMeans data, high priority, Ungouge project" ✅ Created
- "What's the status of the YouTube project?" ✅ "3 tasks in progress, 2 completed"
- "When's my next calendar event?" ✅ "You have a meeting tomorrow at 2 PM"

---

## Cost Analysis (Realistic Usage)

**Scenario:** Jason calls Ish 5 times per week, 10 minutes average per call

| Item | Rate | Monthly Cost |
|------|------|--------------|
| OpenAI Realtime (200 min/month) | $0.30/min | $60 |
| Twilio phone number | $1/month | $1 |
| Twilio inbound calls (200 min) | $0.0085/min | $1.70 |
| **Total** | | **$62.70/month** |

**Value Delivered:**
- Jason's time saved: 3-5 hrs/month (faster than typing, no context switching)
- Jason's hourly rate (consulting): $150-300/hr
- **Value: $450-1,500/month**
- **ROI: 717-2,290%**

**For Ungouge Customers (Paid Feature):**
- **Pricing:** $29.99 for 15-min voice consultation (instead of $19.99 text report)
- **Cost:** $4.50 (OpenAI) + $0.13 (Twilio) = $4.63
- **Margin:** $25.36 per call (85% margin)
- **Break-even:** 3 calls/month = covers Jason's personal usage + profit

---

## Technical Challenges & Solutions

### Challenge 1: Latency
**Problem:** Voice calls feel robotic if >500ms latency  
**Solution:**
- Use OpenAI's `server_vad` (server-side voice activity detection) - faster than client-side
- Stream audio in small chunks (100ms each, not 1-second buffers)
- Use WebRTC for Twilio (lower latency than SIP)
- Host backend in same region as OpenAI servers (us-east-1 likely)

### Challenge 2: Interruptions
**Problem:** User interrupts Ish mid-sentence (natural in conversation)  
**Solution:**
- OpenAI Realtime handles this natively (turn detection)
- When user starts speaking, Ish stops immediately
- Previous response is cancelled, new response starts after user finishes

### Challenge 3: Background Noise
**Problem:** Phone calls from noisy environments (car, cafe, kids)  
**Solution:**
- OpenAI Realtime includes noise suppression
- Twilio also has noise cancellation option (enable in settings)
- Still imperfect - may misunderstand in very loud environments

### Challenge 4: Tool Execution Latency
**Problem:** If tool takes 5 seconds (e.g., database query), call feels frozen  
**Solution:**
- Ish says "Let me check on that..." immediately (acknowledgement)
- Execute tool async
- Ish continues talking while tool runs: "Just a moment... okay, I've got it. The project status is..."

### Challenge 5: Session Continuity
**Problem:** What if call drops mid-conversation?  
**Solution:**
- Log every exchange to database (transcript)
- If user calls back within 10 minutes, inject recent transcript as context
- Ish says: "Looks like we got disconnected. We were talking about [last topic]. Want to continue?"

---

## Alternative: Twilio's Native AI (Simpler but Limited)

**Option:** Use Twilio Voice Intelligence (built-in AI assistant)  
**Pros:**
- All-in-one (no OpenAI integration needed)
- Twilio handles everything (easier setup)
- Lower latency (optimized)

**Cons:**
- Less sophisticated (not GPT-4o level)
- Limited customization (can't inject full MEMORY.md)
- No tool execution (can't create tasks, query database)
- Twilio charges markup on AI usage

**Verdict:** Not suitable for Ish's needs (too limited). OpenAI Realtime is worth the extra complexity.

---

## Recommended Roadmap

**Milestone 1: Web PoC (Weeks 1-2)**
- Build Next.js voice call page
- Implement OpenAI Realtime session creation
- Test basic conversation (no tools, minimal context)
- **Deliverable:** Jason can click "Talk to Ish" and have a conversation via browser

**Milestone 2: Context Injection (Weeks 3-4)**
- Inject MEMORY.md, user profile, recent tasks into session
- Implement 3-5 core tools (create task, get status, analyze quote)
- Test tool execution during calls
- **Deliverable:** Ish can actually do useful work during calls

**Milestone 3: Twilio Integration (Weeks 5-7)**
- Set up Twilio phone number
- Build WebSocket bridge (Twilio ↔ OpenAI)
- Test end-to-end phone call
- **Deliverable:** Jason can call 1-800-UNGOUGE and talk to Ish

**Milestone 4: Production Polish (Weeks 8-10)**
- Call recording + transcription
- Cost tracking dashboard
- Error handling (dropped calls, API failures)
- User-facing feature (Ungouge customers can call)
- **Deliverable:** Publicly available feature, revenue-generating

**Total Timeline:** 8-10 weeks part-time (or 4-5 weeks full-time)  
**Total Effort:** ~40-50 hours

---

## Next Steps (When Ready)

1. **Prototype approval:** Confirm Jason wants this feature (huge value, but 40-50 hr investment)
2. **Budget approval:** ~$60-100/month ongoing cost
3. **OpenAI API access:** Verify Realtime API is included in current plan (or need to upgrade)
4. **Twilio account:** Create account, get phone number
5. **Phase 1 kickoff:** Build web PoC

**Earliest start:** After Ungouge.ai launch (focus on revenue first, voice as enhancement)

---

*Research complete. Ready to implement when Jason gives the green light.*
