# Publishing Guide — Ungouge Quote Checker GPT

*Step-by-step instructions for Jason to publish the GPT*

---

## Prerequisites

Before publishing, ensure:

1. ✅ **ChatGPT Plus subscription** ($20/month) — required to create GPTs
2. ⏳ **ungouge.ai website is live** — the CTA needs to work
3. ⏳ **Privacy policy at ungouge.ai/privacy** — required for GPT Store
4. ⏳ **Profile picture ready** — PNG, square, at least 512x512

---

## Step 1: Access the GPT Builder

1. Go to **https://chat.openai.com**
2. Sign in with your ChatGPT Plus account
3. Click **"Explore GPTs"** (left sidebar)
4. Click **"+ Create"** (top right) or go directly to **https://chat.openai.com/gpts/editor**

---

## Step 2: Configure Basic Info

### Name
```
Ungouge Quote Checker
```

### Description
```
Analyze contractor quotes for fairness. Spot red flags. Get negotiation tips.
```

### Instructions
Copy the ENTIRE contents of `SYSTEM_PROMPT.md` (everything below the `---` line)

---

## Step 3: Upload Knowledge Files

1. Click **"Knowledge"** section
2. Click **"Upload files"**
3. Upload these files (in order):
   - `01_pricing_guidelines.md`
   - `02_red_flags.md`
   - `03_negotiation_tips.md`
   - `04_quick_reference.md`

All files are in: `projects/ungouge-app/gpt-kit/knowledge_files/`

---

## Step 4: Add Conversation Starters

Click **"Conversation starters"** and add:

1. `I just got a roofing quote. Can you check if it's fair?`
2. `Here's an HVAC replacement quote — is this price reasonable?`
3. `What red flags should I look for in a contractor quote?`
4. `I have three quotes for a kitchen remodel. Help me compare them.`

---

## Step 5: Configure Capabilities

Under **"Capabilities"**, ensure:
- ☐ Web Browsing — **OFF**
- ☐ DALL-E Image Generation — **OFF**
- ☐ Code Interpreter — **OFF**

We don't need any of these. Keeping them off makes responses faster.

---

## Step 6: Upload Profile Picture

1. Click the profile picture area
2. Upload your prepared image (PNG, 512x512 minimum)

**If you don't have one yet:**
- Use DALL-E to generate one with this prompt:
  ```
  Minimalist logo: A shield protecting a simple house silhouette, 
  with a checkmark overlay. Deep green and gold colors on white 
  background. Clean, modern, professional. No text.
  ```
- Or commission one on Fiverr ($20-50)

---

## Step 7: Test Before Publishing

1. Click **"Preview"** in the GPT Builder
2. Test with these sample queries:

**Test 1: Basic quote analysis**
```
I got a quote for replacing my roof: 
- Tear-off: $1,500
- New shingles (Owens Corning Duration): $4,500
- Underlayment: $800
- Flashing: $400
- Labor: $3,500
- Disposal: $400
Total: $11,100

Is this fair for a 2,000 sq ft home in Texas?
```

**Test 2: Red flag detection**
```
A contractor just knocked on my door after a storm and offered 
to replace my roof for $6,000 cash, today only. He said he'd 
"work with my insurance" and just needs a $3,000 deposit to 
start tomorrow. Good deal?
```

**Test 3: Comparison request**
```
I have three quotes for a bathroom remodel:
- Contractor A: $18,000
- Contractor B: $25,000  
- Contractor C: $14,000
They all include new tile, vanity, toilet, and fixtures. 
Which should I pick?
```

**What to verify:**
- Responses are helpful and specific
- Red flags are correctly identified
- CTA to ungouge.ai appears appropriately
- Tone is friendly but professional

---

## Step 8: Publish

1. Click **"Save"** (top right)
2. Choose **"Everyone"** to publish to GPT Store
3. Add the privacy policy URL: `https://ungouge.ai/privacy`
4. Click **"Confirm"**

**Note:** OpenAI reviews GPTs before they appear in the store. This can take 1-3 days.

---

## Step 9: Share and Promote

Once published, you'll get a shareable link like:
```
https://chat.openai.com/g/g-xxxx-ungouge-quote-checker
```

**Promote via:**
- Link from ungouge.ai ("Try our free Quote Checker")
- Social media posts
- Blog content
- YouTube video descriptions

---

## Updating the GPT

To update after publishing:

1. Go to **https://chat.openai.com/gpts/mine**
2. Click on "Ungouge Quote Checker"
3. Click **"Edit GPT"**
4. Make changes
5. Click **"Save"** → **"Update"**

Changes go live immediately (no re-review needed unless major).

---

## Troubleshooting

**"Name is already taken"**
- Try: "Ungouge - Quote Checker" or "Quote Checker by Ungouge"

**"Privacy policy required"**
- Ensure ungouge.ai/privacy is live and accessible

**"GPT not appearing in search"**
- Takes 1-3 days for review
- Check spam/promotional categories aren't filtered

**Responses aren't using knowledge files**
- Re-upload files
- Test with specific questions that reference the files
- Ensure files are .md format

---

## Time Estimate

| Step | Time |
|------|------|
| Configure GPT | 10 minutes |
| Upload files | 2 minutes |
| Test | 10 minutes |
| Publish | 2 minutes |
| **Total** | **~25 minutes** |

---

*You're ready! Let me know when ungouge.ai is live and we'll publish this.*
