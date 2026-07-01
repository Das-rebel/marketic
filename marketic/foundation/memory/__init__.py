"""
Marketic Memory Layer - Persistent Marketing Intelligence

SQLite-backed memory for campaign performance, creative assets,
audience insights, and market thesis tracking.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path


class MarketicMemory:
    """
    Persistent memory layer for marketing intelligence.
    
    Stores:
    - Campaign performance history
    - Creative asset library
    - Audience insights
    - Market theses and predictions
    - Signal history
    """

    def __init__(self, db_path: str = "marketic_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Campaign performance memory
        c.execute("""
            CREATE TABLE IF NOT EXISTS campaign_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT UNIQUE,
                name TEXT,
                channel TEXT,
                objective TEXT,
                budget REAL,
                spend REAL,
                impressions INTEGER,
                clicks INTEGER,
                conversions INTEGER,
                revenue REAL,
                cpa REAL,
                roas REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Creative assets library
        c.execute("""
            CREATE TABLE IF NOT EXISTS creative_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT UNIQUE,
                type TEXT,  -- ad_copy, social_post, email, blog, video_script
                channel TEXT,
                headline TEXT,
                body TEXT,
                cta TEXT,
                tags TEXT,  -- JSON array
                performance_data TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                used_in_campaign TEXT
            )
        """)
        
        # Audience segments
        c.execute("""
            CREATE TABLE IF NOT EXISTS audience_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                segment_id TEXT UNIQUE,
                name TEXT,
                description TEXT,
                size INTEGER,
                criteria TEXT,  -- JSON
                avg_ltv REAL,
                conversion_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Market theses
        c.execute("""
            CREATE TABLE IF NOT EXISTS market_theses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thesis_id TEXT UNIQUE,
                category TEXT,  -- trend, competitor, technology, regulatory
                title TEXT,
                thesis TEXT,
                evidence TEXT,
                confidence REAL,
                status TEXT,  -- active, confirmed, disproven, stale
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Signal history
        c.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE,
                source TEXT,
                type TEXT,
                title TEXT,
                content TEXT,
                url TEXT,
                sentiment TEXT,
                priority INTEGER,
                processed BOOLEAN DEFAULT 0,
                insights TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # A/B test results
        c.execute("""
            CREATE TABLE IF NOT EXISTS ab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE,
                campaign_id TEXT,
                variant_a TEXT,
                variant_b TEXT,
                metric TEXT,
                result_a REAL,
                result_b REAL,
                winner TEXT,
                confidence REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    # ============ Campaign Performance ============
    
    def save_campaign_performance(self, campaign: Dict[str, Any]) -> bool:
        """Save or update campaign performance data."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT OR REPLACE INTO campaign_performance 
                (campaign_id, name, channel, objective, budget, spend, impressions, 
                 clicks, conversions, revenue, cpa, roas, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                campaign.get("campaign_id"),
                campaign.get("name"),
                campaign.get("channel"),
                campaign.get("objective"),
                campaign.get("budget", 0),
                campaign.get("spend", 0),
                campaign.get("impressions", 0),
                campaign.get("clicks", 0),
                campaign.get("conversions", 0),
                campaign.get("revenue", 0),
                campaign.get("cpa", 0),
                campaign.get("roas", 0),
                campaign.get("status", "active"),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving campaign: {e}")
            return False
        finally:
            conn.close()

    def get_campaign_performance(self, campaign_id: str) -> Optional[Dict]:
        """Get performance for a specific campaign."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM campaign_performance WHERE campaign_id = ?", (campaign_id,))
        row = c.fetchone()
        conn.close()
        
        return dict(row) if row else None

    def get_top_performing_creatives(self, channel: str, limit: int = 10) -> List[Dict]:
        """Get top performing creative assets by ROAS."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM creative_assets 
            WHERE channel = ? AND performance_data IS NOT NULL
            ORDER BY json_extract(performance_data, '$.roas') DESC
            LIMIT ?
        """, (channel, limit))
        
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    # ============ Creative Assets ============
    
    def save_creative_asset(self, asset: Dict[str, Any]) -> bool:
        """Save a creative asset to the library."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT OR REPLACE INTO creative_assets 
                (asset_id, type, channel, headline, body, cta, tags, performance_data, used_at, used_in_campaign)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset.get("asset_id"),
                asset.get("type"),
                asset.get("channel"),
                asset.get("headline", ""),
                asset.get("body", ""),
                asset.get("cta", ""),
                json.dumps(asset.get("tags", [])),
                json.dumps(asset.get("performance_data", {})),
                datetime.now().isoformat() if asset.get("used") else None,
                asset.get("used_in_campaign"),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving creative: {e}")
            return False
        finally:
            conn.close()

    def search_creatives(
        self,
        channel: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """Search creative assets by criteria."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        query = "SELECT * FROM creative_assets WHERE 1=1"
        params = []
        
        if channel:
            query += " AND channel = ?"
            params.append(channel)
        if type:
            query += " AND type = ?"
            params.append(type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        c.execute(query, params)
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        
        # Filter by tags in Python (SQLite JSON support is limited)
        if tags:
            rows = [
                r for r in rows 
                if any(tag in json.loads(r.get("tags", "[]")) for tag in tags)
            ]
        
        return rows

    # ============ Market Theses ============
    
    def save_thesis(self, thesis: Dict[str, Any]) -> bool:
        """Save a market thesis."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT OR REPLACE INTO market_theses 
                (thesis_id, category, title, thesis, evidence, confidence, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                thesis.get("thesis_id"),
                thesis.get("category"),
                thesis.get("title"),
                thesis.get("thesis"),
                thesis.get("evidence", ""),
                thesis.get("confidence", 0.5),
                thesis.get("status", "active"),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving thesis: {e}")
            return False
        finally:
            conn.close()

    def get_active_theses(self, category: Optional[str] = None) -> List[Dict]:
        """Get all active market theses."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        query = "SELECT * FROM market_theses WHERE status = 'active'"
        if category:
            query += " AND category = ?"
            c.execute(query, (category,))
        else:
            c.execute(query)
        
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    # ============ Signals ============
    
    def save_signal(self, signal: Dict[str, Any]) -> bool:
        """Save a market signal."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT OR REPLACE INTO signals 
                (signal_id, source, type, title, content, url, sentiment, priority, insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.get("signal_id", f"sig_{int(time.time())}"),
                signal.get("source"),
                signal.get("type"),
                signal.get("title"),
                signal.get("content", ""),
                signal.get("url"),
                signal.get("sentiment", "neutral"),
                signal.get("priority", 5),
                json.dumps(signal.get("insights", {})),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving signal: {e}")
            return False
        finally:
            conn.close()

    def get_recent_signals(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent signals from the last N hours."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        c.execute("""
            SELECT * FROM signals 
            WHERE created_at > ? 
            ORDER BY priority ASC, created_at DESC
            LIMIT ?
        """, (cutoff.isoformat(), limit))
        
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    # ============ A/B Tests ============
    
    def save_ab_test(self, test: Dict[str, Any]) -> bool:
        """Save A/B test results."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT OR REPLACE INTO ab_tests 
                (test_id, campaign_id, variant_a, variant_b, metric, result_a, result_b, winner, confidence, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test.get("test_id"),
                test.get("campaign_id"),
                test.get("variant_a"),
                test.get("variant_b"),
                test.get("metric"),
                test.get("result_a", 0),
                test.get("result_b", 0),
                test.get("winner"),
                test.get("confidence", 0),
                test.get("status", "running"),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving A/B test: {e}")
            return False
        finally:
            conn.close()

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all A/B tests."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT status, COUNT(*) as count 
            FROM ab_tests 
            GROUP BY status
        """)
        status_counts = dict(c.fetchall())
        
        c.execute("SELECT COUNT(*) as total FROM ab_tests")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) as winners FROM ab_tests WHERE winner IS NOT NULL")
        winners = c.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "winners": winners,
            "win_rate": winners / total if total > 0 else 0,
            "by_status": status_counts,
        }


# Global memory instance
memory = MarketicMemory()


# Convenience functions
def save_campaign(campaign: Dict[str, Any]) -> bool:
    return memory.save_campaign_performance(campaign)

def get_campaign(campaign_id: str) -> Optional[Dict]:
    return memory.get_campaign_performance(campaign_id)

def save_creative(asset: Dict[str, Any]) -> bool:
    return memory.save_creative_asset(asset)

def search_creatives(**kwargs) -> List[Dict]:
    return memory.search_creatives(**kwargs)

def save_signal(signal: Dict[str, Any]) -> bool:
    return memory.save_signal(signal)

def get_signals(hours: int = 24) -> List[Dict]:
    return memory.get_recent_signals(hours)

def save_thesis(thesis: Dict[str, Any]) -> bool:
    return memory.save_thesis(thesis)

def get_theses(category: Optional[str] = None) -> List[Dict]:
    return memory.get_active_theses(category)


if __name__ == "__main__":
    print("Testing Marketic Memory...")
    
    # Test campaign save
    campaign = {
        "campaign_id": "test_001",
        "name": "AI Tool Launch",
        "channel": "google_ads",
        "objective": "app_installs",
        "budget": 10000,
        "spend": 5234,
        "impressions": 450000,
        "clicks": 8900,
        "conversions": 234,
        "revenue": 11700,
        "cpa": 22.37,
        "roas": 2.23,
        "status": "active",
    }
    save_campaign(campaign)
    print(f"Campaign saved: {campaign['name']}")
    
    # Test creative save
    creative = {
        "asset_id": "copy_001",
        "type": "ad_copy",
        "channel": "google_ads",
        "headline": "AI Marketing That Actually Works",
        "body": "Stop wasting budget on ads that don't convert. Our AI does the optimization for you.",
        "cta": "Start Free Trial",
        "tags": ["ai", "marketing", "saas"],
        "performance_data": {"impressions": 120000, "clicks": 3400, "conversions": 89, "roas": 3.2},
    }
    save_creative(creative)
    print(f"Creative saved: {creative['headline']}")
    
    # Test thesis save
    thesis = {
        "thesis_id": "geo_2025",
        "category": "technology",
        "title": "GEO will replace SEO for B2B",
        "thesis": "Generative Engine Optimization is becoming more important than traditional SEO for B2B SaaS",
        "evidence": "a16z research on search behavior shift",
        "confidence": 0.75,
        "status": "active",
    }
    save_thesis(thesis)
    print(f"Thesis saved: {thesis['title']}")
    
    # Test signal save
    signal = {
        "source": "twitter",
        "type": "trend",
        "title": "New AI marketing tool goes viral",
        "content": "A new competitor launched with aggressive pricing",
        "priority": 3,
        "sentiment": "competitive_threat",
    }
    save_signal(signal)
    print(f"Signal saved: {signal['title']}")
    
    print("\nMemory layer test complete!")
