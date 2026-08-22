#!/usr/bin/env python3
"""
Initialize Marketic memory database with all required tables.
Run this once to set up the SQLite database.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "marketic_memory.db")


def get_connection():
    db_path = os.path.abspath(DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_all():
    """Initialize all database tables."""
    
    conn = get_connection()
    
    print(f"Initializing Marketic database at {DB_PATH}...")
    
    # Brand Memory table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_memory (
            brand_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            industry TEXT,
            positioning TEXT,
            messaging TEXT,
            voice_tone TEXT,
            competitors TEXT DEFAULT '[]',
            target_audience TEXT DEFAULT '[]',
            key_messages TEXT DEFAULT '[]',
            brand_values TEXT DEFAULT '[]',
            story TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Creative variants table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS creative_variants (
            variant_id TEXT PRIMARY KEY,
            brand_id TEXT,
            campaign_id TEXT,
            channel TEXT NOT NULL,
            objective TEXT,
            headline TEXT,
            description TEXT,
            primary_text TEXT,
            cta TEXT,
            confidence REAL DEFAULT 0.5,
            performance_prediction TEXT DEFAULT '{}',
            status TEXT DEFAULT 'draft',
            approved INTEGER DEFAULT 0,
            used_in_campaign TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Campaign table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brand_id TEXT,
            objective TEXT,
            status TEXT DEFAULT 'planning',
            channels TEXT DEFAULT '[]',
            timeline TEXT DEFAULT '{}',
            budget TEXT DEFAULT '{}',
            tactics TEXT DEFAULT '[]',
            estimated_reach INTEGER DEFAULT 0,
            estimated_conversions INTEGER DEFAULT 0,
            estimated_roas REAL DEFAULT 0.0,
            actual_results TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Audit Log table (for ensemble decisions)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            brand_id TEXT,
            action TEXT NOT NULL,
            model TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cost REAL DEFAULT 0.0,
            confidence REAL DEFAULT 0.0,
            reasoning_chain TEXT DEFAULT '[]',
            human_approved INTEGER,
            result_summary TEXT,
            metadata TEXT
        )
    """)
    
    # Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_brand ON audit_log(brand_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_brand_name ON brand_memory(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_creative_brand ON creative_variants(brand_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_brand ON campaigns(brand_id)")
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    print(f"Database location: {DB_PATH}")


def reset():
    """Reset database (delete and recreate)."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")
    init_all()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset()
    else:
        init_all()
