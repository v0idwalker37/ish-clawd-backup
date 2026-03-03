# Gemini Vision Migration Guide

**Status:** Ready for API key  
**Date:** 2026-02-02  
**Reason:** Gemini vision significantly outperforms GPT-4o for quote extraction accuracy

---

## What Changed

**Before:** OpenAI GPT-4 with OCR text extraction  
**After:** Google Gemini 2.0 Flash with direct vision processing

**Why:** During testing, Gemini vision showed dramatically better accuracy at:
- Extracting line items from contractor quotes
- Parsing quantities and units correctly
- Understanding document structure
- Handling various quote formats

---

## Migration Steps

### 1. Get Gemini API Key

1. Sign into https://aistudio.google.com/app/apikey with the project Google account
2. Click "Create API Key"
3. Copy the key

### 2. Install Gemini Dependencies

```bash
cd /Users/moltbot/clawd/projects/ungouge-app/backend
source venv/bin/activate
pip install google-generativeai pdf2image
```

**Note:** `pdf2image` requires `poppler` on macOS:
```bash
brew install poppler
```

### 3. Add API Key to Environment

Add to `backend/.env`:
```bash
GEMINI_API_KEY=your_key_here
```

### 4. Update Quote Router

Replace the import in `backend/routers/quotes.py`:

**Change:**
```python
from services.quote_parser import process_quote_file
```

**To:**
```python
from services.quote_parser_gemini import process_quote_file
```

That's it! The function signature is identical, so no other code changes needed.

### 5. Test the Integration

Run the test script:
```bash
cd /Users/moltbot/clawd/projects/ungouge-app/backend
python3 test_gemini_parser.py path/to/sample_quote.pdf
```

Or test via the API:
```bash
# Start the backend
cd /Users/moltbot/clawd/projects/ungouge-app/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# In another terminal, test quote upload
curl -X POST http://localhost:8000/api/quotes/upload \
  -F "file=@/path/to/sample_quote.pdf"
```

---

## Cost Comparison

| Provider | Model | Input Cost | Accuracy |
|----------|-------|------------|----------|
| OpenAI | GPT-4o | $2.50/1M tokens | Low |
| Google | Gemini 2.0 Flash | $0.075/1M tokens | High |

**Savings:** ~97% cheaper + better accuracy = no-brainer

---

## Rollback Plan

If you need to revert:

1. Change import back to `quote_parser` (original)
2. Comment out Gemini key in `.env`
3. Restart backend

The old code is still in `services/quote_parser.py` (unchanged).

---

## Files Changed

- ✅ `services/quote_parser_gemini.py` - New Gemini implementation
- ⏳ `routers/quotes.py` - Update import (waiting on API key test)
- ⏳ `requirements.txt` - Add google-generativeai + pdf2image
- ⏳ `.env` - Add GEMINI_API_KEY
- ✅ `GEMINI_MIGRATION.md` - This file

---

## Next Steps

1. Jason provides Gemini API key
2. Run installation commands above
3. Test on sample quotes
4. Verify accuracy matches Jason's testing
5. Update requirements.txt
6. Deploy to production

---

## Questions?

Ping Ish if anything breaks or doesn't work as expected.
