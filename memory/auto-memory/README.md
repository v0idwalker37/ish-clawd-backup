# Auto-Memory System

**Status:** ✅ COMPLETE  
**Built:** 2026-02-04 9:07-9:30 AM  
**Uses:** Gemini embeddings (text-embedding-004)

## Architecture

```
memory/auto-memory/
├── database.py          # SQLite + Gemini embeddings ✅
├── capture.py           # Extract facts from conversations ✅
├── recall.py            # Query memories ✅
├── knowledge-graph.json # Structured facts template ✅
└── auto-memory.db       # SQLite database (auto-created)
```

## What This Gets You

1. **Auto-Capture**: Extract facts from conversations automatically
2. **Semantic Search**: Find memories by meaning, not keywords
3. **Categorized Storage**: credentials, preferences, decisions, facts, personal
4. **Timeline Tracking**: Facts can supersede old facts (queryable history)
5. **Tag System**: Flexible organization
6. **Confidence Scoring**: Filter by certainty

## Quick Start

### Capture a Credential
```bash
cd /Users/moltbot/clawd/memory/auto-memory
python3 capture.py --credential "iCloud" "password" "xxxx-xxxx-xxxx-xxxx"
```

### Capture from Conversation
```bash
python3 capture.py "Jason said his iCloud email is jasontrask@icloud.com and he prefers Fahrenheit over Celsius for weather"
```

### Recall Credentials
```bash
python3 recall.py --credentials
python3 recall.py --credentials iCloud
```

### Search Memories
```bash
python3 recall.py "What is Jason's email?"
python3 recall.py "weather preferences"
```

### Recall by Category
```bash
python3 recall.py --preferences
python3 recall.py --decisions
```

## Integration

### Manual Recall (When Uncertain)
```python
from memory.auto_memory.recall import MemoryRecall

recall = MemoryRecall()
memories = recall.recall_for_query("Jason's iCloud password")
print(memories)
recall.close()
```

### Auto-Capture (After Conversations)
```python
from memory.auto_memory.capture import FactExtractor

extractor = FactExtractor()
count = extractor.capture_from_text(conversation_text)
print(f"Captured {count} facts")
extractor.close()
```

## Database Schema

**memories table:**
- content: the fact as text
- embedding: Gemini vector (BLOB)
- category: credential|preference|decision|fact|personal
- confidence: 0.0-1.0
- created_at, updated_at: Unix timestamps
- metadata: JSON blob

**tags table:**
- memory_id → memories(id)
- tag: string

**supersedes table:**
- memory_id: new fact
- superseded_id: old fact it replaces

## Cost

- Gemini text-embedding-004: ~$0.00001 per 1K tokens
- Expected monthly cost: < $0.01 for typical usage
- Essentially free

## Testing

```bash
# Test database
python3 database.py

# Test capture
python3 capture.py "Jason's iCloud email is jasontrask@icloud.com"

# Test recall
python3 recall.py "What is Jason's iCloud email?"
```

## Next Steps

1. Integrate into heartbeat workflow (auto-capture from recent conversations)
2. Add recall hook to AGENTS.md (check memories before asking Jason)
3. Build cleanup script (archive old/low-confidence memories)
4. Add export to markdown (for review/audit)
