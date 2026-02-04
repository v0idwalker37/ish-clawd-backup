#!/usr/bin/env python3
"""
Auto-Capture Script
Extracts important facts from conversation text and stores them
"""

import re
import json
from typing import List, Dict, Optional
from database import AutoMemory
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCn2SYSbVEKaxeDYImC6BTx6O5fUjnF8B0"
genai.configure(api_key=GEMINI_API_KEY)

class FactExtractor:
    """Extract structured facts from conversation text"""
    
    def __init__(self):
        self.db = AutoMemory()
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def extract_facts(self, conversation_text: str) -> List[Dict]:
        """
        Use Gemini to extract important facts from conversation
        Returns list of structured facts
        """
        prompt = f"""Extract important facts from this conversation that should be remembered long-term.

Focus on:
- Credentials (passwords, API keys, emails)
- Preferences (likes/dislikes, how Jason wants things done)
- Decisions (choices made, why we chose X over Y)
- Personal information (family, background, values)
- Technical details (configurations, system info)

Return ONLY a JSON array of facts, each with:
- content: the fact as a complete sentence
- category: "credential" | "preference" | "decision" | "fact" | "personal"
- confidence: 0.0-1.0 (how certain you are this is worth remembering)
- tags: array of 1-3 relevant tags

Conversation:
{conversation_text}

Return ONLY the JSON array, no explanation:"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON from response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            facts = json.loads(text)
            return facts if isinstance(facts, list) else []
            
        except Exception as e:
            print(f"Error extracting facts: {e}")
            return []
    
    def capture_from_text(self, text: str, source: str = "conversation") -> int:
        """
        Extract and store facts from conversation text
        Returns number of facts captured
        """
        facts = self.extract_facts(text)
        captured = 0
        
        for fact in facts:
            # Only capture high-confidence facts
            if fact.get('confidence', 0) >= 0.7:
                try:
                    self.db.add_memory(
                        content=fact['content'],
                        category=fact['category'],
                        tags=fact.get('tags', []),
                        confidence=fact['confidence'],
                        metadata={'source': source}
                    )
                    captured += 1
                except Exception as e:
                    print(f"Error storing fact: {e}")
        
        return captured
    
    def capture_credential(
        self,
        service: str,
        credential_type: str,
        value: str,
        tags: List[str] = None
    ) -> int:
        """Quick helper to capture credentials"""
        content = f"{service} {credential_type}: {value}"
        
        return self.db.add_memory(
            content=content,
            category="credential",
            tags=tags or [service.lower(), credential_type.lower()],
            confidence=1.0,
            metadata={'service': service, 'type': credential_type}
        )
    
    def capture_preference(
        self,
        preference: str,
        tags: List[str] = None
    ) -> int:
        """Quick helper to capture preferences"""
        return self.db.add_memory(
            content=preference,
            category="preference",
            tags=tags or ["preference"],
            confidence=1.0
        )
    
    def close(self):
        self.db.close()


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 capture.py <conversation_text>")
        print("  python3 capture.py --credential <service> <type> <value>")
        print("  python3 capture.py --preference <preference>")
        sys.exit(1)
    
    extractor = FactExtractor()
    
    if sys.argv[1] == "--credential":
        # Quick credential capture
        service = sys.argv[2]
        cred_type = sys.argv[3]
        value = sys.argv[4]
        
        memory_id = extractor.capture_credential(service, cred_type, value)
        print(f"Captured credential (ID: {memory_id})")
        
    elif sys.argv[1] == "--preference":
        # Quick preference capture
        preference = " ".join(sys.argv[2:])
        memory_id = extractor.capture_preference(preference)
        print(f"Captured preference (ID: {memory_id})")
        
    else:
        # Extract facts from conversation
        text = " ".join(sys.argv[1:])
        count = extractor.capture_from_text(text)
        print(f"Captured {count} facts from conversation")
    
    extractor.close()
