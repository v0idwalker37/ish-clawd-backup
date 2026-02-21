#!/usr/bin/env python3
"""
Batch add internal links and Related Guides sections to blog posts
"""

import os
import re

BLOG_DIR = "/home/ungouge/clawd/projects/ungouge-app/frontend/content/blog"

# Define related posts mappings
RELATED_GUIDES = {
    # Educational posts should link to other educational + relevant cost guides
    "how-to-read-contractor-quote.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/signs-your-contractor-is-overcharging", "10 Signs of Overcharging"),
            ("/blog/fair-contractor-markup-2026", "Fair Contractor Markup Guide"),
            ("/blog/how-to-spot-contractor-quote-padding", "Spot Quote Padding"),
        ],
        "cost_guides": [
            ("/blog/kitchen-remodel-cost-2026", "Kitchen Remodel Costs"),
            ("/blog/roof-replacement-cost-guide-2026", "Roof Replacement Costs"),
        ]
    },
    
    "03-contractor-quote-red-flags.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/signs-your-contractor-is-overcharging", "10 Signs of Overcharging"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
            ("/blog/when-to-walk-away-contractor-quote", "When to Walk Away"),
        ],
        "cost_guides": []
    },
    
    "fair-contractor-markup-2026.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/signs-your-contractor-is-overcharging", "10 Signs of Overcharging"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/bathroom-remodel-cost-breakdown", "Bathroom Remodel Costs"),
            ("/blog/deck-building-cost-breakdown", "Deck Building Costs"),
        ]
    },
    
    "how-to-spot-contractor-quote-padding.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/signs-your-contractor-is-overcharging", "10 Signs of Overcharging"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
            ("/blog/fair-contractor-markup-2026", "Fair Markup Percentages"),
        ],
        "cost_guides": []
    },
    
    "when-to-walk-away-contractor-quote.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/contractor-quote-red-flags", "Contractor Quote Red Flags"),
            ("/blog/signs-your-contractor-is-overcharging", "10 Signs of Overcharging"),
        ],
        "cost_guides": []
    },
    
    "how-to-negotiate-contractor-quotes.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
            ("/blog/fair-contractor-markup-2026", "Fair Markup Guide"),
        ],
        "cost_guides": []
    },
    
    "do-i-need-3-contractor-quotes.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": []
    },
    
    "contractor-quote-vs-estimate.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": []
    },
    
    # Cost breakdown posts link to educational + similar cost guides
    "roof-replacement-cost-guide-2026.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/siding-installation-cost-breakdown", "Siding Installation Costs"),
            ("/blog/gutter-installation", "Gutter Installation Costs"),
            ("/blog/window-replacement-cost-breakdown", "Window Replacement Costs"),
        ]
    },
    
    "02-kitchen-remodel-cost-2026.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/bathroom-remodel-cost-breakdown", "Bathroom Remodel Costs"),
            ("/blog/flooring-installation-cost-breakdown", "Flooring Installation Costs"),
            ("/blog/painting-cost-breakdown", "Painting Costs"),
        ]
    },
    
    "bathroom-remodel-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/kitchen-remodel-cost-2026", "Kitchen Remodel Costs"),
            ("/blog/flooring-installation-cost-breakdown", "Flooring Installation Costs"),
            ("/blog/electrical-work-cost-breakdown", "Electrical Work Costs"),
        ]
    },
    
    "hvac-replacement-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/electrical-work-cost-breakdown", "Electrical Work Costs"),
            ("/blog/solar-panel-installation", "Solar Panel Installation"),
        ]
    },
}

# Standard CTA to add if not present
STANDARD_CTA = """
## Get Your Quote Verified

Not sure if your contractor quote is fair? [Submit your quote to UnGouge](/analyze) for a detailed, data-backed analysis in 24 hours. We'll tell you if you're getting a fair price—or if you should negotiate.
""".strip()


def build_related_section(educational_links, cost_guide_links):
    """Build a Related Guides section"""
    lines = ["## Related Guides\n"]
    
    if educational_links:
        lines.append("**Learn more about contractor quotes:**")
        for url, title in educational_links:
            lines.append(f"- [{title}]({url})")
        lines.append("")
    
    if cost_guide_links:
        lines.append("**Project-specific cost guides:**")
        for url, title in cost_guide_links:
            lines.append(f"- [{title}]({url})")
        lines.append("")
    
    return "\n".join(lines)


def process_post(filename):
    """Add Related Guides section and CTA to a blog post if not already present"""
    filepath = os.path.join(BLOG_DIR, filename)
    
    if filename not in RELATED_GUIDES:
        return f"SKIP {filename} - no mapping defined"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has "Related Guides"
    if "## Related Guides" in content:
        return f"SKIP {filename} - already has Related Guides"
    
    # Get the related links
    mapping = RELATED_GUIDES[filename]
    educational = mapping.get("educational", [])
    cost_guides = mapping.get("cost_guides", [])
    
    # Build the Related section
    related_section = build_related_section(educational, cost_guides)
    
    # Find where to insert (before last heading or at end)
    # Look for common ending patterns
    patterns = [
        r'\n## Final Thoughts',
        r'\n## Bottom Line',
        r'\n## Conclusion',
        r'\n---\n\*Last updated:',
        r'\n---\n\n\*Last updated:',
    ]
    
    insert_pos = None
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            insert_pos = match.start()
            break
    
    if insert_pos:
        # Insert before the final section
        new_content = content[:insert_pos] + "\n---\n\n" + related_section + "\n" + content[insert_pos:]
    else:
        # Append at end
        new_content = content.rstrip() + "\n\n---\n\n" + related_section + "\n"
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return f"✅ {filename} - added {len(educational) + len(cost_guides)} links"


def main():
    """Process all posts with mappings"""
    print("Adding internal links to blog posts...\n")
    
    for filename in sorted(RELATED_GUIDES.keys()):
        result = process_post(filename)
        print(result)
    
    print(f"\nProcessed {len(RELATED_GUIDES)} posts.")


if __name__ == "__main__":
    main()

# Add more cost breakdown mappings
RELATED_GUIDES.update({
    "deck-building-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/fence-installation-cost-breakdown", "Fence Installation Costs"),
            ("/blog/landscaping-cost-breakdown", "Landscaping Costs"),
            ("/blog/painting-cost-breakdown", "Painting Costs"),
        ]
    },
    
    "fence-installation-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/deck-building-cost-breakdown", "Deck Building Costs"),
            ("/blog/landscaping-cost-breakdown", "Landscaping Costs"),
        ]
    },
    
    "flooring-installation-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/kitchen-remodel-cost-2026", "Kitchen Remodel Costs"),
            ("/blog/bathroom-remodel-cost-breakdown", "Bathroom Remodel Costs"),
            ("/blog/painting-cost-breakdown", "Painting Costs"),
        ]
    },
    
    "painting-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/siding-installation-cost-breakdown", "Siding Installation Costs"),
            ("/blog/driveway-paving-cost-breakdown", "Driveway Paving Costs"),
        ]
    },
    
    "siding-installation-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/roof-replacement-cost-guide-2026", "Roof Replacement Costs"),
            ("/blog/window-replacement-cost-breakdown", "Window Replacement Costs"),
            ("/blog/painting-cost-breakdown", "Painting Costs"),
        ]
    },
    
    "window-replacement-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/siding-installation-cost-breakdown", "Siding Installation Costs"),
            ("/blog/roof-replacement-cost-guide-2026", "Roof Replacement Costs"),
        ]
    },
    
    "driveway-paving-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/concrete-foundation", "Concrete Foundation Costs"),
            ("/blog/landscaping-cost-breakdown", "Landscaping Costs"),
        ]
    },
    
    "electrical-work-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/hvac-replacement-cost-breakdown", "HVAC Replacement Costs"),
            ("/blog/solar-panel-installation", "Solar Panel Installation"),
        ]
    },
    
    "basement-finishing-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/flooring-installation-cost-breakdown", "Flooring Installation Costs"),
            ("/blog/electrical-work-cost-breakdown", "Electrical Work Costs"),
            ("/blog/painting-cost-breakdown", "Painting Costs"),
        ]
    },
    
    "gutter-installation.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/roof-replacement-cost-guide-2026", "Roof Replacement Costs"),
            ("/blog/siding-installation-cost-breakdown", "Siding Installation Costs"),
        ]
    },
    
    "landscaping-cost-breakdown.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/deck-building-cost-breakdown", "Deck Building Costs"),
            ("/blog/fence-installation-cost-breakdown", "Fence Installation Costs"),
            ("/blog/tree-removal", "Tree Removal Costs"),
        ]
    },
    
    "pool-installation.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/deck-building-cost-breakdown", "Deck Building Costs"),
            ("/blog/landscaping-cost-breakdown", "Landscaping Costs"),
            ("/blog/electrical-work-cost-breakdown", "Electrical Work Costs"),
        ]
    },
    
    "solar-panel-installation.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/electrical-work-cost-breakdown", "Electrical Work Costs"),
            ("/blog/roof-replacement-cost-guide-2026", "Roof Replacement Costs"),
        ]
    },
    
    "tree-removal.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/landscaping-cost-breakdown", "Landscaping Costs"),
        ]
    },
    
    "concrete-foundation.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/driveway-paving-cost-breakdown", "Driveway Paving Costs"),
            ("/blog/basement-finishing-cost-breakdown", "Basement Finishing Costs"),
        ]
    },
    
    "home-inspection-costs.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": []
    },
    
    "hvac-quote-too-high-fair-pricing-2026.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
            ("/blog/signs-your-contractor-is-overcharging", "10 Signs of Overcharging"),
        ],
        "cost_guides": [
            ("/blog/hvac-replacement-cost-breakdown", "HVAC Replacement Costs"),
            ("/blog/electrical-work-cost-breakdown", "Electrical Work Costs"),
        ]
    },
    
    "how-much-should-roof-replacement-cost.md": {
        "educational": [
            ("/blog/01-is-contractor-quote-too-high", "How to Tell If Your Quote Is Too High"),
            ("/blog/how-to-read-contractor-quote", "How to Read a Quote"),
        ],
        "cost_guides": [
            ("/blog/roof-replacement-cost-guide-2026", "Roof Replacement Cost Guide"),
            ("/blog/siding-installation-cost-breakdown", "Siding Installation Costs"),
        ]
    },
})
