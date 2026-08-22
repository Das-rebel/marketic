"""
Brand Memory Store — Persistent brand memory with SQLite + semantic search.
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "marketic_memory.db")


@dataclass
class Brand:
    id: str
    name: str
    website: str
    industry: str
    created_at: str


@dataclass
class Memory:
    id: str
    brand_id: str
    memory_type: str  # voice, competitor_intel, performance_baseline, preferences, learning
    content: str
    metadata: Optional[str]  # JSON string for additional data
    created_at: str


def get_connection():
    """Get SQLite connection."""
    db_path = os.path.abspath(DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                website TEXT,
                industry TEXT,
                created_at TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                brand_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_memories_brand ON memories(brand_id);
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
        """)
        conn.commit()
    finally:
        conn.close()


class BrandMemoryStore:
    """Persistent memory store for brands."""
    
    def __init__(self):
        init_db()
    
    def create_brand(self, name: str, website: str = "", industry: str = "") -> Brand:
        """Create a new brand."""
        brand_id = str(uuid.uuid4())[:8]
        created_at = datetime.utcnow().isoformat()
        
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO brands (id, name, website, industry, created_at) VALUES (?, ?, ?, ?, ?)",
                (brand_id, name, website, industry, created_at)
            )
            conn.commit()
        finally:
            conn.close()
        
        return Brand(id=brand_id, name=name, website=website, industry=industry, created_at=created_at)
    
    def get_brand(self, brand_id: str) -> Optional[Brand]:
        """Get brand by ID."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM brands WHERE id = ?", (brand_id,)).fetchone()
            if row:
                return Brand(**dict(row))
            return None
        finally:
            conn.close()
    
    def update_brand(self, brand_id: str, data: Dict[str, str]) -> bool:
        """Update brand fields."""
        allowed = {"name", "website", "industry"}
        updates = {k: v for k, v in data.items() if k in allowed}
        if not updates:
            return False
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [brand_id]
        
        conn = get_connection()
        try:
            conn.execute(f"UPDATE brands SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
    
    def add_memory(self, brand_id: str, memory_type: str, content: str, metadata: Optional[Dict] = None) -> Memory:
        """Add a memory to a brand."""
        memory_id = str(uuid.uuid4())[:12]
        created_at = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO memories (id, brand_id, memory_type, content, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (memory_id, brand_id, memory_type, content, metadata_json, created_at)
            )
            conn.commit()
        finally:
            conn.close()
        
        return Memory(id=memory_id, brand_id=brand_id, memory_type=memory_type, 
                     content=content, metadata=metadata_json, created_at=created_at)
    
    def get_memories(self, brand_id: str, memory_type: Optional[str] = None, query: Optional[str] = None) -> List[Memory]:
        """Get memories for a brand, optionally filtered by type or keyword search."""
        conn = get_connection()
        try:
            sql = "SELECT * FROM memories WHERE brand_id = ?"
            params: List[str] = [brand_id]
            
            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type)
            
            if query:
                sql += " AND content LIKE ?"
                params.append(f"%{query}%")
            
            sql += " ORDER BY created_at DESC"
            
            rows = conn.execute(sql, params).fetchall()
            return [Memory(**dict(row)) for row in rows]
        finally:
            conn.close()
    
    def get_all_memory_types(self, brand_id: str) -> List[str]:
        """Get all unique memory types for a brand."""
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT DISTINCT memory_type FROM memories WHERE brand_id = ? ORDER BY memory_type",
                (brand_id,)
            ).fetchall()
            return [row["memory_type"] for row in rows]
        finally:
            conn.close()
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory."""
        conn = get_connection()
        try:
            conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
    
    def get_brand_by_name(self, name: str) -> Optional[Brand]:
        """Get brand by name (case-insensitive)."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM brands WHERE LOWER(name) = LOWER(?)", (name,)
            ).fetchone()
            if row:
                return Brand(**dict(row))
            return None
        finally:
            conn.close()
    
    def list_brands(self) -> List[Brand]:
        """List all brands."""
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM brands ORDER BY created_at DESC").fetchall()
            return [Brand(**dict(row)) for row in rows]
        finally:
            conn.close()
