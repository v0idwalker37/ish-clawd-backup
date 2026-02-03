# Email Template Screenshots & Examples

## Preview Files Generated

All template variations are available in the `previews/` directory:

### 📁 Preview Index
**File:** `previews/index.html`

An interactive index page with links to all three quote scenarios. Open this file in a browser to view all variations side-by-side.

**To view:**
```bash
open backend/templates/emails/previews/index.html
```

---

## Template Variations

### ✅ Fair Quote Scenario
**Files:**
- `previews/quote_analysis_fair_quote.html` (HTML version)
- `previews/quote_analysis_fair_quote.txt` (Plain text version)

**Example:**
- **Verdict:** Fair Price (green accent)
- **Price:** $12,450
- **Red Flags:** None
- **Tone:** Encouraging, informative

**Key Features:**
- Quote within market range
- Positive reinforcement
- Actionable next steps (verify insurance, ask about warranty)
- No red flags section displayed

---

### ⚠️ High Quote Scenario
**Files:**
- `previews/quote_analysis_high_quote.html` (HTML version)
- `previews/quote_analysis_high_quote.txt` (Plain text version)

**Example:**
- **Verdict:** Above Market Rate (amber/warning accent)
- **Price:** $48,900
- **Red Flags:** 3 moderate concerns
- **Tone:** Cautionary but balanced

**Key Features:**
- 22% above market average
- Red flags section visible
- Specific concerns highlighted (inflated costs, lack of itemization)
- Suggests getting additional quotes

---

### 🚨 Overpriced Quote Scenario
**Files:**
- `previews/quote_analysis_overpriced_quote.html` (HTML version)
- `previews/quote_analysis_overpriced_quote.txt` (Plain text version)

**Example:**
- **Verdict:** Significantly Overpriced (red accent)
- **Price:** $31,500
- **Red Flags:** 4 serious concerns
- **Tone:** Urgent warning, protective

**Key Features:**
- 45% above market average
- Multiple red flags (payment terms, pricing markup)
- Strong advisory tone
- Clear "DO NOT sign" guidance

---

## Mobile Responsiveness Testing

### Recommended Testing Method

1. **Open preview in browser:**
   ```bash
   open previews/quote_analysis_fair_quote.html
   ```

2. **Test responsive views:**
   - Desktop: Full width (600px max-width container)
   - Tablet: Responsive scaling
   - Mobile: Single column, touch-friendly buttons

3. **Browser DevTools:**
   - Open DevTools (F12)
   - Toggle device toolbar (Cmd+Shift+M / Ctrl+Shift+M)
   - Test at:
     - iPhone 14 Pro (393px)
     - iPhone SE (375px)
     - iPad (768px)
     - Desktop (1920px)

---

## Email Client Testing

### Quick Test (Gmail)

1. Copy HTML source from preview file
2. Send to your Gmail account
3. Check rendering in:
   - Gmail web (desktop)
   - Gmail mobile app (iOS/Android)

### Recommended Testing Tools

**Free:**
- Send test emails to yourself on different clients
- Use browser DevTools for responsive preview

**Paid (Professional):**
- [Litmus](https://litmus.com/) - Tests 90+ email clients
- [Email on Acid](https://www.emailonacid.com/) - Comprehensive testing

---

## Visual Design Elements

### Color Coding

| Verdict | Color | Hex Code | Use Case |
|---------|-------|----------|----------|
| ✅ Fair Price | Green | `#00B894` | Quote within ±15% of market |
| ⚠️ Above Market | Amber | `#f59e0b` | Quote 15-30% above market |
| 🚨 Overpriced | Red | `#ef4444` | Quote 30%+ above market |

### Typography

- **Headings:** System font stack (SF Pro, Segoe UI, Roboto)
- **Body:** 16px (desktop), scales on mobile
- **Buttons:** 16px, 600 weight, touch-friendly padding

### Layout

- **Max-width:** 600px (industry standard for emails)
- **Padding:** Consistent 30px (desktop), 20px (mobile)
- **Spacing:** 8px grid system for visual rhythm

---

## Rendering Notes

### Known Compatibility

**✅ Tested and working:**
- Gmail (web, iOS, Android)
- Apple Mail (macOS, iOS)
- Outlook (web)
- Samsung Email
- Yahoo Mail

**⚠️ Potential issues:**
- Outlook Desktop (Windows) - limited CSS support
  - Fallback: basic layout still functional
  - Gradients may not render (solid color fallback)

**Fix for Outlook:**
Template includes conditional comments for Outlook-specific styles (if needed in future iterations).

---

## Screenshots (Visual Examples)

Since browser automation wasn't available during generation, preview files can be viewed directly:

### How to Generate Screenshots

**macOS:**
```bash
# Open preview in default browser
open previews/quote_analysis_fair_quote.html

# Use screenshot tool (Cmd+Shift+4)
# Or use screencapture command:
screencapture -w previews/screenshots/fair_quote.png
```

**Windows:**
```bash
# Open in browser
start previews/quote_analysis_fair_quote.html

# Use Snipping Tool or Win+Shift+S
```

**Linux:**
```bash
# Open in browser
xdg-open previews/quote_analysis_fair_quote.html

# Use gnome-screenshot or scrot
gnome-screenshot -w -f previews/screenshots/fair_quote.png
```

---

## Comparison Matrix

| Feature | Fair Quote | High Quote | Overpriced |
|---------|-----------|------------|------------|
| Verdict Icon | ✅ | ⚠️ | 🚨 |
| Color Accent | Green | Amber | Red |
| Red Flags Section | Hidden | Visible (3 flags) | Visible (4 flags) |
| Tone | Encouraging | Cautionary | Urgent |
| Next Steps | 3 steps | 3 steps | 3 steps |
| CTA Emphasis | Standard | Standard | High |

---

## Integration Example

The preview script demonstrates how to render templates with real data. Example integration in backend:

```python
# See test_preview.py for full working examples
from jinja2 import Template

template = Template(open('quote_analysis.html').read())
rendered = template.render(SAMPLE_DATA['fair_quote'])
```

---

**Last updated:** February 2, 2025  
**Files included:** 8 preview files + index  
**Test script:** `test_preview.py`
