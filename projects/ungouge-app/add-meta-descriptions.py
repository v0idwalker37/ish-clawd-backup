#!/usr/bin/env python3
"""Add meta descriptions to blog posts missing them"""

import os
import re

BLOG_DIR = "/home/ungouge/clawd/projects/ungouge-app/frontend/content/blog"

# Meta descriptions to add
META_DESCRIPTIONS = {
    "basement-finishing-cost-breakdown.md": "Complete basement finishing cost breakdown with actual material prices, labor rates, and contractor red flags. Budget from $10K to $50K+ based on square footage and finishes.",
    "driveway-paving-cost-breakdown.md": "Complete driveway paving cost breakdown with actual prices for asphalt, concrete, gravel, and pavers. Includes labor rates, regional pricing, and contractor red flags.",
    "fence-installation-cost-breakdown.md": "Complete fence installation cost breakdown with actual prices for wood, vinyl, chain link, and metal fencing. Includes labor rates, material costs, and contractor red flags.",
    "flooring-installation-cost-breakdown.md": "Complete flooring installation cost breakdown with actual prices for hardwood, laminate, tile, vinyl, and carpet. Includes labor rates and contractor red flags.",
    "how-to-read-contractor-quote.md": "Learn to decode every line item in a contractor quote. Understand markup percentages, labor rates, material costs, and spot inflated pricing before you sign.",
    "how-to-spot-contractor-quote-padding.md": "Learn the specific tactics contractors use to pad quotes—from inflated labor hours to phantom expenses—and how to spot them line by line.",
    "hvac-quote-too-high-fair-pricing-2026.md": "Think your HVAC quote is too high? Compare your estimate against real 2026 market data for equipment, labor, and installation. Know what's fair before you pay.",
    "landscaping-cost-breakdown.md": "Complete landscaping cost breakdown with actual prices for design, installation, hardscaping, plantings, and maintenance. Includes labor rates and contractor red flags.",
    "painting-cost-breakdown.md": "Complete painting cost breakdown with actual prices for interior and exterior projects. Includes labor rates, material costs per square foot, and contractor red flags.",
    "why-free-quote-tools-cost-more.md": "Free contractor quote comparison tools seem helpful—but they're lead generation funnels that drive up your final costs. Here's how they work and what to use instead.",
    "window-replacement-cost-breakdown.md": "Complete window replacement cost breakdown with actual prices for vinyl, wood, and fiberglass windows. Includes installation labor rates and contractor red flags.",
}


def add_meta_description(filename, description):
    """Add or update meta description in frontmatter"""
    filepath = os.path.join(BLOG_DIR, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it already has a description
    if re.search(r'^description:\s*["\']', content, re.MULTILINE):
        return f"SKIP {filename} - already has description"
    
    # Check if it has frontmatter (starts with ---)
    if content.startswith('---'):
        # Has frontmatter - add description to it
        # Find the closing ---
        match = re.search(r'^---\n(.+?)\n---', content, re.DOTALL)
        if match:
            frontmatter = match.group(1)
            # Add description at the end of frontmatter
            new_frontmatter = frontmatter.rstrip() + f'\ndescription: "{description}"'
            new_content = content.replace(
                f"---\n{frontmatter}\n---",
                f"---\n{new_frontmatter}\n---"
            )
        else:
            return f"ERROR {filename} - malformed frontmatter"
    else:
        # No frontmatter - extract title and create frontmatter
        # Look for first # heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = filename.replace('.md', '').replace('-', ' ').title()
        
        # Create new frontmatter
        frontmatter = f'''---
title: "{title}"
description: "{description}"
date: 2026-02-01
author: Ungouge Team
keywords: []
---

'''
        new_content = frontmatter + content
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return f"✅ {filename} - added meta description"


def main():
    print("Adding meta descriptions to blog posts...\n")
    
    for filename, description in sorted(META_DESCRIPTIONS.items()):
        result = add_meta_description(filename, description)
        print(result)
    
    print(f"\nProcessed {len(META_DESCRIPTIONS)} posts.")


if __name__ == "__main__":
    main()
