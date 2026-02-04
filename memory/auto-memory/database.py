#!/usr/bin/env python3
"""
Auto-Memory Database
Uses SQLite + Gemini embeddings for semantic memory
"""

import sqlite3
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
import google.generativeai as genai

# Database path
DB_PATH = Path(__file__).parent / "auto-memory.db"
GEMINI_API_KEY = "AIzaSyCn2SYSbVEKaxeDYImC6BTx6O5fUjnF8B0"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class AutoMemory:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript("""
            -- Memory entries with embeddings
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL,
                category TEXT NOT NULL,  -- credential, preference, decision, fact
                confidence REAL DEFAULT 1.0,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                metadata TEXT  -- JSON blob for extra data
            );
            
            -- Tags for memories
            CREATE TABLE IF NOT EXISTS tags (
                memory_id INTEGER,
                tag TEXT NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
            );
            
            -- Superseded facts (timeline tracking)
            CREATE TABLE IF NOT EXISTS supersedes (
                memory_id INTEGER,
                superseded_id INTEGER,
                reason TEXT,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (superseded_id) REFERENCES memories(id) ON DELETE CASCADE
            );
            
            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
            CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
            CREATE INDEX IF NOT EXISTS idx_tags_memory ON tags(memory_id);
            CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
        """)
        self.conn.commit()
    
    def get_embedding(self, text: str) -> List[float]:
        """Get Gemini embedding for text"""
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def add_memory(
        self,
        content: str,
        category: str,
        tags: List[str] = None,
        confidence: float = 1.0,
        metadata: Dict = None,
        supersedes_id: Optional[int] = None
    ) -> int:
        """Add a new memory"""
        embedding = self.get_embedding(content)
        embedding_blob = json.dumps(embedding).encode()
        
        now = int(time.time())
        
        cursor = self.conn.execute(
            """INSERT INTO memories 
               (content, embedding, category, confidence, created_at, updated_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (content, embedding_blob, category, confidence, now, now,
             json.dumps(metadata) if metadata else None)
        )
        memory_id = cursor.lastrowid
        
        # Add tags
        if tags:
            for tag in tags:
                self.conn.execute(
                    "INSERT INTO tags (memory_id, tag) VALUES (?, ?)",
                    (memory_id, tag)
                )
        
        # Track superseding
        if supersedes_id:
            self.conn.execute(
                "INSERT INTO supersedes (memory_id, superseded_id) VALUES (?, ?)",
                (memory_id, supersedes_id)
            )
        
        self.conn.commit()
        return memory_id
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x * x for x in a) ** 0.5
        mag_b = sum(x * x for x in b) ** 0.5
        return dot_product / (mag_a * mag_b) if mag_a and mag_b else 0.0
    
    def search(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> List[Dict]:
        """Search memories semantically"""
        query_embedding = self.get_embedding(query)
        
        # Get all memories (filtered by category if specified)
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        cursor = self.conn.execute(sql, params)
        results = []
        
        for row in cursor:
            memory_embedding = json.loads(row['embedding'].decode())
            similarity = self.cosine_similarity(query_embedding, memory_embedding)
            
            if similarity >= min_confidence:
                # Get tags
                tag_cursor = self.conn.execute(
                    "SELECT tag FROM tags WHERE memory_id = ?",
                    (row['id'],)
                )
                tags = [t['tag'] for t in tag_cursor]
                
                results.append({
                    'id': row['id'],
                    'content': row['content'],
                    'category': row['category'],
                    'confidence': row['confidence'],
                    'similarity': similarity,
                    'tags': tags,
                    'created_at': row['created_at'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all memories in a category"""
        cursor = self.conn.execute(
            "SELECT * FROM memories WHERE category = ? ORDER BY created_at DESC",
            (category,)
        )
        return [dict(row) for row in cursor]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Test
    db = AutoMemory()
    
    # Add test memory
    memory_id = db.add_memory(
        content="Jason's iCloud email is jasontrask@icloud.com",
        category="credential",
        tags=["email", "icloud"],
        confidence=1.0,
        metadata={"source": "conversation", "date": "2026-02-04"}
    )
    
    print(f"Added memory ID: {memory_id}")
    
    # Search
    results = db.search("what is Jason's iCloud email?")
    print(f"\nSearch results: {len(results)}")
    for r in results:
        print(f"  [{r['similarity']:.3f}] {r['content']}")
    
    db.close()
