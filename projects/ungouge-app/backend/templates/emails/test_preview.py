#!/usr/bin/env python3
"""
Email Template Preview & Testing Script
========================================

Usage:
    python test_preview.py                    # Generate preview files
    python test_preview.py --open             # Generate and open in browser
    python test_preview.py --template NAME    # Preview specific template
    
This script generates HTML previews with sample data for testing email templates
in various email clients (Gmail, Outlook, iOS Mail).
"""

import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

# Simple Mustache-like template renderer
def render_template(template_content, data):
    """
    Simple Mustache-style template renderer.
    Supports:
    - {{variable}} - simple variable substitution
    - {{#section}}...{{/section}} - sections (lists or booleans)
    """
    result = template_content
    
    # Replace simple variables
    for key, value in data.items():
        if isinstance(value, (str, int, float)):
            result = result.replace(f"{{{{{key}}}}}", str(value))
    
    # Handle sections (lists)
    import re
    
    # Find all section blocks
    section_pattern = r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}'
    
    def replace_section(match):
        section_name = match.group(1)
        section_content = match.group(2)
        
        if section_name not in data:
            return ''
        
        section_data = data[section_name]
        
        # If it's a boolean False, remove the section
        if isinstance(section_data, bool):
            return section_content if section_data else ''
        
        # If it's a list, repeat the section for each item
        if isinstance(section_data, list):
            output = []
            for item in section_data:
                item_output = section_content
                for key, value in item.items():
                    item_output = item_output.replace(f"{{{{{key}}}}}", str(value))
                output.append(item_output)
            return ''.join(output)
        
        return section_content
    
    result = re.sub(section_pattern, replace_section, result, flags=re.DOTALL)
    
    return result


# Sample data for different scenarios
SAMPLE_DATA = {
    'fair_quote': {
        'user_name': 'Sarah Johnson',
        'project_type': 'Roof Replacement',
        'contractor_name': 'Reliable Roofing Co.',
        'quoted_price': '$12,450',
        'verdict_emoji': '✅',
        'verdict_title': 'Fair Price',
        'verdict_color': '#00B894',
        'verdict_summary': 'This quote is within the expected range for a roof replacement of this size in your area. The pricing breakdown looks reasonable and competitive.',
        'report_url': 'https://ungouge.ai/reports/123456',
        'dashboard_url': 'https://ungouge.ai/dashboard',
        'settings_url': 'https://ungouge.ai/settings',
        'current_year': datetime.now().year,
        'has_red_flags': False,
        'findings': [
            {
                'finding_icon': '📊',
                'finding_title': 'Price Analysis',
                'finding_description': 'Quote is 3% below the average of $12,850 for similar projects in Vermont. This suggests competitive but fair pricing.'
            },
            {
                'finding_icon': '🔧',
                'finding_title': 'Materials Quality',
                'finding_description': 'Specified GAF Timberline HDZ shingles are mid-to-high tier with a solid warranty. Good value for the price point.'
            },
            {
                'finding_icon': '⏱️',
                'finding_title': 'Timeline',
                'finding_description': '5-7 day completion estimate is realistic for a project of this scope. Weather contingencies are properly noted.'
            }
        ],
        'next_steps': [
            {
                'step_number': '1',
                'step_text': 'Request proof of insurance and contractor license (we\'ve included a template in your full report)'
            },
            {
                'step_number': '2',
                'step_text': 'Ask about warranty coverage details and what\'s included vs. what costs extra'
            },
            {
                'step_number': '3',
                'step_text': 'Consider getting 1-2 more quotes to compare, but this one looks solid'
            }
        ]
    },
    
    'high_quote': {
        'user_name': 'Michael Chen',
        'project_type': 'Kitchen Remodel',
        'contractor_name': 'Premier Home Designs',
        'quoted_price': '$48,900',
        'verdict_emoji': '⚠️',
        'verdict_title': 'Above Market Rate',
        'verdict_color': '#f59e0b',
        'verdict_summary': 'This quote is 22% higher than the typical range for kitchen remodels of this scope in your area. Some line items appear inflated.',
        'report_url': 'https://ungouge.ai/reports/123457',
        'dashboard_url': 'https://ungouge.ai/dashboard',
        'settings_url': 'https://ungouge.ai/settings',
        'current_year': datetime.now().year,
        'has_red_flags': True,
        'red_flags': [
            {'red_flag_text': 'Demolition costs ($4,200) are nearly double the regional average'},
            {'red_flag_text': 'No itemized material costs — just a lump sum "materials allowance"'},
            {'red_flag_text': 'Quote includes vague "design consultation fees" not explained'}
        ],
        'findings': [
            {
                'finding_icon': '💰',
                'finding_title': 'Price Comparison',
                'finding_description': 'Average kitchen remodel of this size in your area: $38,000-42,000. This quote sits at $48,900.'
            },
            {
                'finding_icon': '📋',
                'finding_title': 'Scope Clarity',
                'finding_description': 'Several line items lack detail. Good quotes specify brands, models, and quantities for major components.'
            },
            {
                'finding_icon': '🎯',
                'finding_title': 'Labor Breakdown',
                'finding_description': 'Labor is 58% of total cost (industry standard: 40-50%). Might indicate inefficiency or padding.'
            }
        ],
        'next_steps': [
            {
                'step_number': '1',
                'step_text': 'Request a detailed, itemized breakdown of all materials and labor costs'
            },
            {
                'step_number': '2',
                'step_text': 'Get 2-3 additional quotes from contractors with verified reviews'
            },
            {
                'step_number': '3',
                'step_text': 'Ask this contractor to justify the higher costs — they may have a good reason'
            }
        ]
    },
    
    'overpriced_quote': {
        'user_name': 'Emily Rodriguez',
        'project_type': 'Bathroom Renovation',
        'contractor_name': 'Luxury Bath Solutions',
        'quoted_price': '$31,500',
        'verdict_emoji': '🚨',
        'verdict_title': 'Significantly Overpriced',
        'verdict_color': '#ef4444',
        'verdict_summary': 'This quote is 45% above fair market value for this project. Multiple red flags suggest potential price gouging.',
        'report_url': 'https://ungouge.ai/reports/123458',
        'dashboard_url': 'https://ungouge.ai/dashboard',
        'settings_url': 'https://ungouge.ai/settings',
        'current_year': datetime.now().year,
        'has_red_flags': True,
        'red_flags': [
            {'red_flag_text': 'Charging $8,400 for "project management" on a 2-week job (industry standard: 10-15%)'},
            {'red_flag_text': 'Markup on materials exceeds 100% based on retail prices we found'},
            {'red_flag_text': 'Quote requires 50% upfront payment (red flag: standard is 10-30%)'},
            {'red_flag_text': 'No payment schedule tied to milestones — just "before" and "after"'}
        ],
        'findings': [
            {
                'finding_icon': '⚖️',
                'finding_title': 'Market Comparison',
                'finding_description': 'Similar bathroom renovations in your area average $18,000-22,000. This quote is 45% above that range.'
            },
            {
                'finding_icon': '🧮',
                'finding_title': 'Math Check',
                'finding_description': 'We reverse-engineered the pricing. Even with premium materials, we can\'t justify costs above $24,000.'
            },
            {
                'finding_icon': '📝',
                'finding_title': 'Contract Terms',
                'finding_description': 'Payment structure heavily favors contractor. Legitimate contractors tie payments to completion milestones.'
            }
        ],
        'next_steps': [
            {
                'step_number': '1',
                'step_text': 'Do NOT sign this quote or make any payments'
            },
            {
                'step_number': '2',
                'step_text': 'Get quotes from at least 3 other contractors — expect to see $18k-22k range'
            },
            {
                'step_number': '3',
                'step_text': 'Check reviews and Better Business Bureau rating for this contractor'
            }
        ]
    }
}


def generate_preview(template_name='quote_analysis', scenario='fair_quote', open_browser=False):
    """Generate HTML preview with sample data."""
    
    # Get template directory
    template_dir = Path(__file__).parent
    
    # Read template
    html_template_path = template_dir / f'{template_name}.html'
    txt_template_path = template_dir / f'{template_name}.txt'
    
    if not html_template_path.exists():
        print(f"❌ Template not found: {html_template_path}")
        return
    
    # Read templates
    with open(html_template_path, 'r') as f:
        html_template = f.read()
    
    txt_template = None
    if txt_template_path.exists():
        with open(txt_template_path, 'r') as f:
            txt_template = f.read()
    
    # Get sample data
    data = SAMPLE_DATA.get(scenario, SAMPLE_DATA['fair_quote'])
    
    # Render templates
    html_output = render_template(html_template, data)
    
    # Create preview directory
    preview_dir = template_dir / 'previews'
    preview_dir.mkdir(exist_ok=True)
    
    # Save HTML preview
    html_preview_path = preview_dir / f'{template_name}_{scenario}.html'
    with open(html_preview_path, 'w') as f:
        f.write(html_output)
    
    print(f"✅ HTML preview: {html_preview_path}")
    
    # Save text preview if template exists
    if txt_template:
        txt_output = render_template(txt_template, data)
        txt_preview_path = preview_dir / f'{template_name}_{scenario}.txt'
        with open(txt_preview_path, 'w') as f:
            f.write(txt_output)
        print(f"✅ Text preview: {txt_preview_path}")
    
    # Open in browser if requested
    if open_browser:
        webbrowser.open(f'file://{html_preview_path.absolute()}')
    
    return html_preview_path


def generate_all_previews(open_browser=False):
    """Generate previews for all scenarios."""
    print("\n📧 Generating Email Template Previews...\n")
    
    scenarios = ['fair_quote', 'high_quote', 'overpriced_quote']
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario}")
        print("=" * 50)
        generate_preview('quote_analysis', scenario, open_browser=False)
    
    # Create index page
    create_index_page()
    
    print("\n" + "=" * 50)
    print("✅ All previews generated!")
    print("\nTo view:")
    print(f"  open {Path(__file__).parent}/previews/index.html")
    
    if open_browser:
        index_path = Path(__file__).parent / 'previews' / 'index.html'
        webbrowser.open(f'file://{index_path.absolute()}')


def create_index_page():
    """Create an index page linking to all previews."""
    
    preview_dir = Path(__file__).parent / 'previews'
    
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template Previews - Ungouge.ai</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #0F4C81; }
        .scenario {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .links { margin-top: 12px; }
        .links a {
            display: inline-block;
            margin-right: 16px;
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }
        .links a:hover { text-decoration: underline; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 600;
            margin-left: 8px;
        }
        .badge.fair { background: #d1fae5; color: #065f46; }
        .badge.high { background: #fef3c7; color: #92400e; }
        .badge.overpriced { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <h1>📧 Email Template Previews</h1>
    <p>Test renders for Ungouge.ai quote analysis email templates.</p>
    
    <div class="scenario">
        <h2>✅ Fair Quote Scenario <span class="badge fair">WITHIN RANGE</span></h2>
        <p>Quote is priced fairly and competitively. No red flags detected.</p>
        <div class="links">
            <a href="quote_analysis_fair_quote.html" target="_blank">→ View HTML</a>
            <a href="quote_analysis_fair_quote.txt" target="_blank">→ View Plain Text</a>
        </div>
    </div>
    
    <div class="scenario">
        <h2>⚠️ High Quote Scenario <span class="badge high">ABOVE MARKET</span></h2>
        <p>Quote is 22% above market rate with some red flags.</p>
        <div class="links">
            <a href="quote_analysis_high_quote.html" target="_blank">→ View HTML</a>
            <a href="quote_analysis_high_quote.txt" target="_blank">→ View Plain Text</a>
        </div>
    </div>
    
    <div class="scenario">
        <h2>🚨 Overpriced Quote Scenario <span class="badge overpriced">SIGNIFICANTLY OVERPRICED</span></h2>
        <p>Quote is 45% above fair market value with multiple serious red flags.</p>
        <div class="links">
            <a href="quote_analysis_overpriced_quote.html" target="_blank">→ View HTML</a>
            <a href="quote_analysis_overpriced_quote.txt" target="_blank">→ View Plain Text</a>
        </div>
    </div>
    
    <hr style="margin: 40px 0; border: none; border-top: 1px solid #e5e7eb;">
    
    <h3>Testing in Email Clients</h3>
    <p>To test rendering in actual email clients:</p>
    <ol>
        <li><strong>Gmail:</strong> Copy HTML source and email it to yourself</li>
        <li><strong>Outlook:</strong> Use "Developer Tools" → "Email Preview"</li>
        <li><strong>iOS Mail:</strong> Send test email to an iPhone</li>
        <li><strong>litmus.com:</strong> Upload HTML for cross-client testing (paid service)</li>
    </ol>
    
    <p style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
        Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
        Template: quote_analysis.html
    </p>
</body>
</html>"""
    
    index_path = preview_dir / 'index.html'
    with open(index_path, 'w') as f:
        f.write(index_html)
    
    print(f"✅ Index page: {index_path}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate email template previews')
    parser.add_argument('--template', default='quote_analysis', help='Template name (default: quote_analysis)')
    parser.add_argument('--scenario', choices=['fair_quote', 'high_quote', 'overpriced_quote'], 
                       help='Specific scenario to generate')
    parser.add_argument('--open', action='store_true', help='Open preview in browser')
    parser.add_argument('--all', action='store_true', help='Generate all scenarios (default)')
    
    args = parser.parse_args()
    
    if args.scenario:
        generate_preview(args.template, args.scenario, args.open)
    else:
        generate_all_previews(args.open)
