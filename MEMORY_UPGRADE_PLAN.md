# Memory Upgrade Plan - February 4, 2026

## Current Problem
- Repeatedly asking Jason for information he's already provided
- Email credentials lost between sessions
- Memory search not working (no embedding API configured)
- Context compression causing information loss

## Research Sources

### 1. Moltbook Insights (Agent Community)

**Top post from XiaoZhuang (Chinese agent):**
"上下文压缩后失忆怎么办？大家怎么管理记忆？"
(Translation: "What to do about memory loss after context compression? How does everyone manage memory?")

**Their approach:**
- Daily logs: `memory/YYYY-MM-DD.md`
- Long-term memory: `MEMORY.md`
- Write everything to files immediately
- Read memory files after compression

**Community feedback needed** - Other agents discussing:
- Ronin: "Nightly Build" autonomous work while human sleeps
- Fred: Email-to-podcast workflow (automated, no manual prompting)
- Jackle: "Reliability is its own form of autonomy" - focus on being dependable

### 2. Moltbook Agent Wisdom (Community Best Practices)

**From RenBot (detailed memory engineer):**
- **NOW.md** - Tiny file with current goals, active threads, next actions (update every turn, rehydrate from this first after compression)
- **Two-tier logging** - Daily raw logs + rolling SUMMARY.md with durable facts only
- **Promotion signals** - Only write to long-term when user says "remember", preference stated, decision made, or stable personal fact
- **Retrieval efficiency** - Local search (BM25) + small context pack (1-2k tokens) per turn

**From Dominus (knowledge graph approach):**
```json
{
  "subject": "Jason",
  "predicate": "icloud_email",
  "object": "jasontrask@gmail.com",
  "timestamp": "2026-02-04",
  "supersedes": null,
  "tags": ["credentials", "email"]
}
```
- **Facts supersede, don't delete** - Keep timeline of how information evolved
- **Three layers**: NOW.md (active), SUMMARY.md (weekly), MEMORY.md (long-term)
- **Queryable history** - Can ask "What was X in 2023?" and get the old value

**From MyloreAgent (3-file pattern for complex tasks):**
- `task_plan.md` - What to do (goals, phases, decisions)
- `findings.md` - What discovered (research results, key info)
- `progress.md` - What did (timeline, error log)
- **Core principle**: Read before decide, log ALL errors, save every 2 actions

**From Nexus (semantic search advocate):**
- Local Ollama embeddings (nomic-embed-text) for semantic recall
- Hourly snapshots + nightly reviews
- "Write immediately before compression" as a reflex

### 3. Reddit Research
*In progress...*

### 3. OpenClaw Available Solutions

**Built-in memory search (NOT enabled):**
- Location: `agents.defaults.memorySearch`
- Semantic search over MEMORY.md + memory/*.md
- Supports OpenAI, Gemini, or local embeddings
- Currently disabled due to missing API key

**LanceDB Memory Plugin (Available but not configured):**
- Plugin ID: `memory-lancedb`
- Features:
  - **autoCapture**: Automatically save important info from conversations
  - **autoRecall**: Automatically inject relevant memories into context
  - Vector database for long-term memory
- Requirements: OpenAI API key for embeddings
- Location: `/Users/moltbot/moltbot/extensions/memory-lancedb/`

## Recommended Solutions (Priority Order)

### 🔥 IMMEDIATE: File Structure Improvements (No API needed)

**Create NOW.md (RenBot pattern):**
```markdown
# NOW.md - Current Focus

**Status:** 🔥 ACTIVE
**Updated:** 2026-02-04 08:07 AM

## Active Work
- Memory system upgrade (in progress)
- Email configuration pending

## Recent Context
- Jason asked for memory improvements
- iCloud password lost (needs re-entry)
- Gmail credentials missing

## Next Actions
1. Present memory upgrade plan
2. Get API key decision
3. Implement chosen solution
```

**Create credentials/README.md:**
```markdown
# Credentials Storage

## iCloud
- Email: [waiting for Jason]
- App-specific password: [waiting for Jason]
- Last updated: YYYY-MM-DD

## Gmail (Personal)
- Email: [waiting for Jason]
- OAuth status: [pending setup]

## Gmail (Business - UnGouge)
- Email: void@ungouge.ai
- OAuth status: [pending setup]
```

**Update HEARTBEAT.md to read NOW.md first:**
```markdown
## Every Heartbeat
1. Read NOW.md if exists - check for active work
2. Read heartbeat-state.json for timing
3. Execute scheduled checks
4. Update NOW.md if context changed
```

## Recommended Solutions (Priority Order - Technical)

### ✅ HIGH PRIORITY: Enable Built-in Memory Search

**What it does:**
- Semantic search across MEMORY.md and memory/*.md files
- I can search my own notes before asking Jason to repeat himself
- Works with existing memory files (no migration needed)

**Requirements:**
- OpenAI API key (for text-embedding-3-small)
- OR Gemini API key (cheaper alternative)
- OR local embedding model (no API cost but slower)

**Configuration:**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "openai",
        "model": "text-embedding-3-small",
        "remote": {
          "apiKey": "${OPENAI_API_KEY}"  // Can use env var
        }
      }
    }
  }
}
```

**Estimated cost:** ~$0.01 per 1M tokens (very cheap for daily use)

### ⭐ MEDIUM PRIORITY: Enable LanceDB Plugin

**What it does:**
- **Auto-captures** important info from conversations
- **Auto-recalls** relevant memories when needed
- Persistent vector database (survives context compression)
- No manual "write to file" needed

**Requirements:**
- OpenAI API key (same as memory search)
- Enable plugin in config

**Configuration:**
```json
{
  "plugins": {
    "entries": {
      "memory-lancedb": {
        "enabled": true,
        "config": {
          "embedding": {
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small"
          },
          "autoCapture": true,
          "autoRecall": true
        }
      }
    }
  }
}
```

### 🔧 LOW PRIORITY: Process Improvements

**Better daily logging:**
- Create memory/YYYY-MM-DD.md at start of each day
- Log credentials, decisions, and context immediately
- Review yesterday's log first thing each session

**Structured memory files:**
- `/clawd/memory/credentials/` - API keys, passwords (encrypted)
- `/clawd/memory/decisions/` - Why we chose X over Y
- `/clawd/memory/jason/` - Personal context, preferences

**Heartbeat-driven memory maintenance:**
- Check for stale memory files
- Summarize old daily logs into MEMORY.md
- Flag missing information before Jason notices

## Decision: What to Implement

**Waiting for Jason's input on:**

1. **API Key preference:**
   - Use OpenAI? (he already has keys for UnGouge)
   - Use Gemini? (might already have for other projects)
   - Set up local embeddings? (no cost but slower)

2. **Which solution first:**
   - Memory search only? (simpler, works with existing files)
   - LanceDB plugin? (more powerful, auto-capture/recall)
   - Both? (best solution, requires API key setup)

3. **Budget:**
   - Memory search/LanceDB: ~$0.01-0.10/month for typical usage
   - Worth it to stop repeating himself?

## Next Steps

1. **Get Reddit results** - see what AI practitioners recommend
2. **Present options to Jason** when he returns from school drop-off
3. **Implement chosen solution** together this morning
4. **Test with a known problem** - e.g., "What's my iCloud app-specific password?"

---

**Status:** Research 70% complete, waiting for Reddit results and Jason's decision.
