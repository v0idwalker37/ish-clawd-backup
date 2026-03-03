# Email Templates - GougeAlert

Professional, mobile-responsive email templates for quote analysis delivery.

## 📧 Templates

### `quote_analysis.html`
Main HTML template for delivering quote analysis reports to users.

**Tone:** Data-driven but human. "Here's what we found" not "Our analysis indicates."

**Includes:**
- Quote summary with verdict (Fair/High/Overpriced)
- Key findings (price analysis, materials, timeline, etc.)
- Red flags section (conditional, only when present)
- Next steps / actionable recommendations
- Clear CTA to view full report

**Mobile-responsive:** Uses table-based layout for maximum email client compatibility.

### `quote_analysis.txt`
Plain-text fallback version for email clients that don't support HTML.

---

## 🎨 Design Philosophy

- **Professional but approachable** — not corporate
- **Visual hierarchy** — emoji icons for quick scanning
- **Color-coded verdicts:**
  - ✅ Fair Price: `#00B894` (green)
  - ⚠️ Above Market: `#f59e0b` (amber)
  - 🚨 Overpriced: `#ef4444` (red)
- **Data-first** — lead with numbers and facts
- **Actionable** — always include next steps

---

## 🔧 Template Variables

### Required Variables

```python
{
    'user_name': str,              # User's first name
    'project_type': str,           # e.g., "Roof Replacement"
    'contractor_name': str,        # Contractor business name
    'quoted_price': str,           # Formatted price, e.g., "$12,450"
    'verdict_emoji': str,          # ✅, ⚠️, or 🚨
    'verdict_title': str,          # "Fair Price", "Above Market Rate", etc.
    'verdict_color': str,          # Hex color for verdict accent
    'verdict_summary': str,        # 1-2 sentence verdict explanation
    'report_url': str,             # Link to full report
    'dashboard_url': str,          # Link to user dashboard
    'settings_url': str,           # Link to settings
    'current_year': int,           # For footer copyright
}
```

### Optional Variables

```python
{
    'has_red_flags': bool,         # Show/hide red flags section
    'red_flags': [                 # List of red flag items
        {'red_flag_text': str},
        ...
    ],
    'findings': [                  # List of key findings
        {
            'finding_icon': str,   # Emoji icon
            'finding_title': str,  # Finding headline
            'finding_description': str
        },
        ...
    ],
    'next_steps': [                # Recommended actions
        {
            'step_number': str,    # "1", "2", "3"
            'step_text': str       # Action description
        },
        ...
    ]
}
```

---

## 🧪 Testing & Preview

### Generate Previews

```bash
# Generate all scenarios (fair, high, overpriced)
python test_preview.py --all

# Generate specific scenario
python test_preview.py --scenario fair_quote

# Generate and open in browser
python test_preview.py --all --open
```

Preview files are saved to `previews/` directory with an index page for easy viewing.

### Test Scenarios

The test script includes three realistic scenarios:

1. **Fair Quote** — within market range, no red flags
2. **High Quote** — 22% above market with some red flags
3. **Overpriced Quote** — 45% above market with multiple red flags

### Email Client Testing

**Gmail:**
- Copy HTML source from preview
- Send to yourself as test email
- Check mobile Gmail app on iOS/Android

**Outlook (Desktop/Web):**
- Use Outlook's Developer Tools
- Or send test email to Outlook account

**iOS Mail:**
- Send test email to iPhone
- Verify rendering on actual device

**Cross-client testing (recommended):**
- [Litmus](https://litmus.com/) — paid service, tests 90+ clients
- [Email on Acid](https://www.emailonacid.com/) — alternative

---

## 📱 Mobile Responsiveness

Templates use **hybrid/fluid design**:
- Table-based layout (for Outlook compatibility)
- Max-width 600px container
- Inline styles (email clients strip `<style>` tags)
- Touch-friendly buttons (44px+ hit areas)
- Readable font sizes (16px+ for body text)

**Tested on:**
- iOS Mail (iPhone/iPad)
- Gmail mobile app
- Outlook mobile app
- Samsung Email

---

## 🎯 Usage in Backend

### Example Integration

```python
from jinja2 import Template
import datetime

# Load template
with open('templates/emails/quote_analysis.html') as f:
    template = Template(f.read())

# Prepare data
data = {
    'user_name': 'Sarah',
    'project_type': 'Roof Replacement',
    'contractor_name': 'Reliable Roofing Co.',
    'quoted_price': '$12,450',
    'verdict_emoji': '✅',
    'verdict_title': 'Fair Price',
    'verdict_color': '#00B894',
    'verdict_summary': 'This quote is within expected range...',
    'has_red_flags': False,
    'findings': [
        {
            'finding_icon': '📊',
            'finding_title': 'Price Analysis',
            'finding_description': 'Quote is 3% below average...'
        }
    ],
    'next_steps': [
        {
            'step_number': '1',
            'step_text': 'Request proof of insurance...'
        }
    ],
    'report_url': 'https://gougealert.com/reports/123456',
    'dashboard_url': 'https://gougealert.com/dashboard',
    'settings_url': 'https://gougealert.com/settings',
    'current_year': datetime.datetime.now().year
}

# Render
html_body = template.render(data)

# Send via your email service
send_email(
    to=user.email,
    subject=f'Your {data["project_type"]} Quote Analysis',
    html=html_body,
    text=render_text_version(data)  # Plain-text fallback
)
```

---

## 🚀 Best Practices

### Verdict Assignment

**Fair Price (✅ #00B894):**
- Within ±15% of market average
- No significant red flags
- Reasonable breakdown

**Above Market Rate (⚠️ #f59e0b):**
- 15-30% above market average
- 1-2 moderate red flags
- Some items need clarification

**Significantly Overpriced (🚨 #ef4444):**
- 30%+ above market average
- 3+ red flags
- Payment terms are suspicious
- Lack of transparency

### Red Flag Examples

**Price-related:**
- "Demolition costs are 2x regional average"
- "No itemized material costs — just lump sum"
- "Labor is 60% of total (standard: 40-50%)"

**Contract-related:**
- "Requires 50% upfront (red flag: standard is 10-30%)"
- "No payment schedule tied to milestones"
- "Vague 'contingency fees' not explained"

**Legitimacy-related:**
- "No license/insurance documentation provided"
- "Pressure tactics: 'quote expires in 24 hours'"
- "Company has no verifiable online presence"

### Writing Next Steps

Always be **specific and actionable**:

❌ Bad: "Get more quotes"
✅ Good: "Get 2-3 additional quotes from contractors with verified reviews"

❌ Bad: "Check the contract"
✅ Good: "Request a detailed, itemized breakdown of all materials and labor costs"

❌ Bad: "Be careful"
✅ Good: "Do NOT sign this quote or make any payments until you've compared with other contractors"

---

## 📸 Screenshots

Preview screenshots saved in `previews/screenshots/` (if generated).

To capture screenshots:
```bash
# macOS
screencapture -w previews/screenshots/fair_quote.png

# Or use browser dev tools to export mobile/desktop views
```

---

## 📝 Template Syntax

Templates use Mustache-style syntax:

**Variables:**
```html
{{variable_name}}
```

**Conditional sections:**
```html
{{#has_red_flags}}
  <!-- Only shown if has_red_flags is true -->
{{/has_red_flags}}
```

**Lists (loops):**
```html
{{#findings}}
  <div>{{finding_title}}</div>
{{/findings}}
```

---

## 🔐 Security Notes

- **No user-generated content** should be inserted without sanitization
- **Links** should use HTTPS only
- **Email addresses** should be validated before sending
- **Personal data** (name, address) should comply with privacy policy

---

## 🎨 Maintaining Brand Consistency

All colors, fonts, and spacing align with `BRANDING.md`:

- **Primary blue:** `#0F4C81` (Trust Blue)
- **Accent green:** `#00B894` (Fair Green)
- **Typography:** System font stack for cross-platform consistency
- **Spacing:** 8px grid system

---

## 📚 Resources

- **Email template best practices:** [Really Good Emails](https://reallygoodemails.com/)
- **HTML email guide:** [Campaign Monitor Guide](https://www.campaignmonitor.com/css/)
- **Mobile-first email design:** [Litmus Resources](https://www.litmus.com/resources/)

---

**Last updated:** February 2025  
**Maintainer:** Development Team  
**Questions?** Check the main project README or open an issue.
