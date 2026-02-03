#!/usr/bin/env python3
"""
Quick test script for Gemini quote parser

Usage:
    python3 test_gemini_parser.py path/to/quote.pdf
    python3 test_gemini_parser.py path/to/quote.jpg
"""
import sys
import os
import json
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.quote_parser_gemini import process_quote_file


async def test_parser(file_path: str):
    """Test the Gemini parser on a sample quote"""
    
    print(f"\n{'='*60}")
    print(f"Testing Gemini Quote Parser")
    print(f"{'='*60}\n")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not found in environment")
        print("Add it to backend/.env or export it:\n")
        print("  export GEMINI_API_KEY='your_key_here'")
        return
    
    print(f"📄 File: {file_path}")
    
    # Check file exists
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found: {file_path}")
        return
    
    # Read file
    print("📖 Reading file...")
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    
    filename = os.path.basename(file_path)
    print(f"✅ Loaded {len(file_bytes)} bytes\n")
    
    # Parse with Gemini
    print("🤖 Parsing with Gemini Vision...")
    try:
        result = await process_quote_file(file_bytes, filename)
        
        print("✅ Parse successful!\n")
        print(f"{'='*60}")
        print("EXTRACTED DATA")
        print(f"{'='*60}\n")
        
        # Pretty print results
        print(f"Project Type: {result.get('project_type', 'N/A')}")
        print(f"Location: {result.get('location', 'N/A')}")
        print(f"Contractor: {result.get('contractor_name', 'N/A')}")
        print(f"Date: {result.get('date', 'N/A')}")
        
        if result.get('notes'):
            print(f"Notes: {result['notes']}")
        
        print(f"\n{'='*60}")
        print(f"LINE ITEMS ({len(result.get('line_items', []))} found)")
        print(f"{'='*60}\n")
        
        total_items = 0
        for i, item in enumerate(result.get('line_items', []), 1):
            print(f"{i}. {item.get('item_name', 'Unknown')}")
            if item.get('description'):
                print(f"   Description: {item['description']}")
            print(f"   Price: ${item.get('quoted_price', 0):.2f}")
            print(f"   Quantity: {item.get('quantity', 1)} {item.get('unit', 'item')}")
            item_total = item.get('quoted_price', 0) * item.get('quantity', 1)
            print(f"   Subtotal: ${item_total:.2f}\n")
            total_items += item_total
        
        print(f"{'='*60}")
        print(f"TOTAL: ${result.get('total', total_items):.2f}")
        print(f"{'='*60}\n")
        
        # Save full JSON for inspection
        output_file = f"{file_path}.gemini_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 Full JSON saved to: {output_file}\n")
        
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_gemini_parser.py <quote_file>")
        print("\nExample:")
        print("  python3 test_gemini_parser.py ~/Desktop/contractor_quote.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    asyncio.run(test_parser(file_path))
