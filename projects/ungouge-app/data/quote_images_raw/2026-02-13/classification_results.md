# Classification Results — 2026-02-13 Reddit Scrape

**Scraped:** 3 images from r/homeimprovement  
**Actual Quotes:** 0/3 (0%)  
**Quality:** Poor — scraper needs better detection

---

## Image 1: quote_0001.jpg
- **Source:** https://www.reddit.com/r/HomeImprovement/comments/1r2ui32/
- **Title:** "how much would something like this take to repair?"
- **Classification:** ❌ NOT A QUOTE
- **Actual content:** Product advertisement for "Raccoon One Way Eviction Door" (e-commerce listing image)
- **Why scraped:** Likely because it's an image in a post asking about repair costs

## Image 2: quote_0002.gif
- **Source:** Not recorded in metadata (missing post_url)
- **Classification:** ❌ NOT A QUOTE
- **Actual content:** Educational diagram — "Knee Wall Attic Insulation & Ventilation" from EnergySmartOhio.com
- **Why scraped:** Technical home improvement content, but informational not a quote

## Image 3: quote_0003.jpg  
- **Source:** Not recorded in metadata (missing post_url)
- **Classification:** ❌ NOT A QUOTE
- **Actual content:** Photo of 1950s pink/burgundy bathroom (likely "before" photo for renovation)
- **Why scraped:** Home improvement related, but just a room photo

---

## Analysis

### Problem: Overly Broad Detection
The scraper is collecting ANY image from home improvement posts, not filtering for quote characteristics.

### What Makes a Real Quote?
✅ **Typical characteristics:**
- Document/paper appearance (white background, text-heavy)
- Line items with dollar amounts
- Company letterhead or logo
- Terms like "estimate," "quote," "proposal," "invoice"
- Dates, addresses, project descriptions
- Subtotals, taxes, total amounts
- Signatures or approval sections

❌ **Not quotes:**
- Product photos (Image 1)
- Diagrams/infographics (Image 2)
- Room photos (Image 3)
- Screenshots of websites
- Memes or text-only images

### Scraper Improvements Needed

#### 1. Better Post Title Filtering
Current: Scrapes any post with images  
Better: Filter for posts with keywords:
- "quote"
- "estimate"
- "bid"
- "proposal"
- "contractor gave me"
- "is this a fair price"
- "how much should"
- Numbers like "$10K", "$5,000", etc.

#### 2. Image Content Pre-screening
Before downloading, check if image URL suggests:
- Document formats (PDF screenshot, document scan)
- Avoid obvious product photos (amazon-images, media-library-service)
- Avoid diagram/infographic patterns (logos from educational sites)

#### 3. OCR-Based Validation
After download, run quick OCR and look for:
- Dollar signs + numbers
- Quote-related terms (estimate, total, subtotal, labor, materials)
- Company/contractor names
- If <2 matches → classify as "not_quote" and skip

#### 4. Computer Vision Pre-filter
Use lightweight vision model to classify BEFORE expensive Claude analysis:
- Document layout vs photo vs diagram
- Text density (quotes are text-heavy)
- Presence of tables/line items

---

## Recommendations

### Short-Term (Next Run)
1. **Add post title filtering:** Only scrape posts with pricing-related keywords
2. **Expand metadata capture:** Save post_url for all images (currently missing for 2/3)
3. **Add OCR pre-screen:** Reject images without dollar signs or quote keywords

### Medium-Term
1. **Build lightweight classifier:** Train on our collected dataset (quote vs not-quote)
2. **Multi-stage pipeline:**
   - Stage 1: Post title filter (cheap)
   - Stage 2: Image URL patterns (cheap)
   - Stage 3: OCR keyword detection (moderate cost)
   - Stage 4: Claude vision full analysis (expensive, only for high-confidence candidates)

### Long-Term
1. **User submissions:** Let users upload quotes directly (guaranteed quality)
2. **Contractor partnerships:** Get sample quotes from real contractors
3. **Synthetic generation:** Create fake but realistic quotes for training data

---

## Status Files Update Needed

The scraper's `image_scraper_status.json` showed:
```json
"total_files_downloaded": 0
```

But we actually downloaded 3 files. The status tracking is broken — investigate count increment logic.

---

**Reviewed by:** Ish  
**Date:** 2026-02-13 1:50 AM  
**Next action:** Debug scraper, improve detection logic before next run
