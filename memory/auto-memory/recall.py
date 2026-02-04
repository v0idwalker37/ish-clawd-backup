#!/usr/bin/env python3
"""
Auto-Recall Script
Queries relevant memories and formats them for injection into context
"""

import sys
from typing import List, Dict
from database import AutoMemory

class MemoryRecall:
    """Recall relevant memories based on context"""
    
    def __init__(self):
        self.db = AutoMemory()
    
    def recall_for_query(
        self,
        query: str,
        limit: int = 5,
        category: str = None,
        min_confidence: float = 0.6
    ) -> str:
        """
        Recall memories relevant to a query
        Returns formatted text ready for context injection
        """
        results = self.db.search(
            query=query,
            limit=limit,
            category=category,
            min_confidence=min_confidence
        )
        
        if not results:
            return ""
        
        # Format results
        output = ["## Relevant Memories\n"]
        
        for r in results:
            output.append(f"**[{r['category'].title()}]** {r['content']}")
            if r['tags']:
                output.append(f"  *Tags: {', '.join(r['tags'])}*")
            output.append(f"  *Confidence: {r['similarity']:.2%}*\n")
        
        return "\n".join(output)
    
    def recall_credentials(self, service: str = None) -> str:
        """Recall all credentials, optionally filtered by service"""
        if service:
            query = f"{service} credentials password API key"
            results = self.db.search(query, category="credential", limit=10)
        else:
            results = self.db.get_by_category("credential")
        
        if not results:
            return "No credentials found."
        
        output = ["## Stored Credentials\n"]
        for r in results:
            output.append(f"- {r['content']}")
        
        return "\n".join(output)
    
    def recall_preferences(self) -> str:
        """Recall all preferences"""
        results = self.db.get_by_category("preference")
        
        if not results:
            return "No preferences stored."
        
        output = ["## User Preferences\n"]
        for r in results:
            output.append(f"- {r['content']}")
        
        return "\n".join(output)
    
    def recall_decisions(self, topic: str = None) -> str:
        """Recall decisions, optionally filtered by topic"""
        if topic:
            results = self.db.search(topic, category="decision", limit=10)
        else:
            results = self.db.get_by_category("decision")
        
        if not results:
            return "No decisions found."
        
        output = ["## Past Decisions\n"]
        for r in results:
            output.append(f"- {r['content']}")
        
        return "\n".join(output)
    
    def close(self):
        self.db.close()


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 recall.py <query>")
        print("  python3 recall.py --credentials [service]")
        print("  python3 recall.py --preferences")
        print("  python3 recall.py --decisions [topic]")
        sys.exit(1)
    
    recall = MemoryRecall()
    
    if sys.argv[1] == "--credentials":
        service = sys.argv[2] if len(sys.argv) > 2 else None
        print(recall.recall_credentials(service))
        
    elif sys.argv[1] == "--preferences":
        print(recall.recall_preferences())
        
    elif sys.argv[1] == "--decisions":
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        print(recall.recall_decisions(topic))
        
    else:
        query = " ".join(sys.argv[1:])
        print(recall.recall_for_query(query))
    
    recall.close()
