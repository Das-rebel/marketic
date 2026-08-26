"""
Audit Trail — Transparent logging of every AI decision.
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "marketic_memory.db")


def get_connection():
    """Get SQLite connection."""
    db_path = os.path.abspath(DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_audit_db():
    """Initialize audit log table."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                brand_id TEXT,
                action TEXT NOT NULL,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost REAL,
                confidence REAL,
                reasoning_chain TEXT,
                human_approved INTEGER,
                result_summary TEXT,
                metadata TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_audit_brand ON audit_log(brand_id);
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
        """)
        conn.commit()
    finally:
        conn.close()


@dataclass
class AuditEntry:
    id: str
    timestamp: str
    brand_id: Optional[str]
    action: str
    model: Optional[str]
    input_tokens: int
    output_tokens: int
    cost: float
    confidence: float
    reasoning_chain: List[str]
    human_approved: bool
    result_summary: Optional[str]
    metadata: Optional[Dict]


class AuditLogger:
    """Log every AI decision with full transparency."""
    
    def __init__(self):
        init_audit_db()
    
    def log_action(self, action: str, model: str = None,
                   input_tokens: int = 0, output_tokens: int = 0,
                   cost: float = 0.0, confidence: float = 0.0,
                   reasoning_chain: List[str] = None,
                   result_summary: str = None,
                   human_approved: bool = None,
                   brand_id: str = None,
                   metadata: Dict = None) -> str:
        """Log an AI action."""
        audit_id = str(uuid.uuid4())[:12]
        timestamp = datetime.utcnow().isoformat()
        
        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO audit_log 
                (id, timestamp, brand_id, action, model, input_tokens, output_tokens,
                 cost, confidence, reasoning_chain, human_approved, result_summary, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                timestamp,
                brand_id,
                action,
                model,
                input_tokens,
                output_tokens,
                cost,
                confidence,
                json.dumps(reasoning_chain or []),
                1 if human_approved else 0 if human_approved is not None else None,
                result_summary,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
        finally:
            conn.close()
        
        return audit_id
    
    def get_audit_log(self, brand_id: str = None, 
                      action: str = None,
                      start_date: str = None,
                      end_date: str = None,
                      limit: int = 100) -> List[AuditEntry]:
        """Retrieve audit log entries."""
        conn = get_connection()
        try:
            sql = "SELECT * FROM audit_log WHERE 1=1"
            params = []
            
            if brand_id:
                sql += " AND brand_id = ?"
                params.append(brand_id)
            
            if action:
                sql += " AND action = ?"
                params.append(action)
            
            if start_date:
                sql += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                sql += " AND timestamp <= ?"
                params.append(end_date)
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(sql, params).fetchall()
            
            entries = []
            for row in rows:
                entries.append(AuditEntry(
                    id=row["id"],
                    timestamp=row["timestamp"],
                    brand_id=row["brand_id"],
                    action=row["action"],
                    model=row["model"],
                    input_tokens=row["input_tokens"] or 0,
                    output_tokens=row["output_tokens"] or 0,
                    cost=row["cost"] or 0.0,
                    confidence=row["confidence"] or 0.0,
                    reasoning_chain=json.loads(row["reasoning_chain"] or "[]"),
                    human_approved=bool(row["human_approved"]) if row["human_approved"] is not None else None,
                    result_summary=row["result_summary"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                ))
            
            return entries
        finally:
            conn.close()
    
    def get_cost_summary(self, brand_id: str = None,
                         start_date: str = None,
                         end_date: str = None) -> Dict[str, Any]:
        """Get cost summary by model and action type."""
        conn = get_connection()
        try:
            base_sql = "SELECT model, action, SUM(cost) as total_cost, COUNT(*) as count FROM audit_log WHERE 1=1"
            params = []
            
            if brand_id:
                base_sql += " AND brand_id = ?"
                params.append(brand_id)
            
            if start_date:
                base_sql += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                base_sql += " AND timestamp <= ?"
                params.append(end_date)
            
            base_sql += " GROUP BY model, action ORDER BY total_cost DESC"
            
            rows = conn.execute(base_sql, params).fetchall()
            
            total_cost = 0.0
            by_model = {}
            by_action = {}
            
            for row in rows:
                cost = row["total_cost"] or 0.0
                total_cost += cost
                
                model = row["model"] or "unknown"
                action = row["action"] or "unknown"
                
                by_model[model] = by_model.get(model, 0) + cost
                by_action[action] = by_action.get(action, 0) + cost
            
            return {
                "total_cost": round(total_cost, 4),
                "by_model": {k: round(v, 4) for k, v in by_model.items()},
                "by_action": {k: round(v, 4) for k, v in by_action.items()},
                "total_decisions": sum(row["count"] for row in rows)
            }
        finally:
            conn.close()
    
    def export_csv(self, brand_id: str = None,
                  start_date: str = None,
                  end_date: str = None) -> str:
        """Export audit log to CSV file."""
        import csv
        
        entries = self.get_audit_log(brand_id, None, start_date, end_date, 10000)
        
        csv_path = f"/tmp/audit_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Timestamp", "Brand", "Action", "Model", 
                "Input Tokens", "Output Tokens", "Cost", "Confidence",
                "Human Approved", "Result Summary"
            ])
            
            for e in entries:
                writer.writerow([
                    e.id,
                    e.timestamp,
                    e.brand_id or "",
                    e.action,
                    e.model or "",
                    e.input_tokens,
                    e.output_tokens,
                    f"${e.cost:.4f}",
                    f"{e.confidence:.2f}",
                    "Yes" if e.human_approved else "No" if e.human_approved is not None else "Auto",
                    e.result_summary or ""
                ])
        
        return csv_path
    
    def get_decision_details(self, audit_id: str) -> Optional[AuditEntry]:
        """Get full details of a specific decision."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM audit_log WHERE id = ?", (audit_id,)).fetchone()
            if not row:
                return None
            
            return AuditEntry(
                id=row["id"],
                timestamp=row["timestamp"],
                brand_id=row["brand_id"],
                action=row["action"],
                model=row["model"],
                input_tokens=row["input_tokens"] or 0,
                output_tokens=row["output_tokens"] or 0,
                cost=row["cost"] or 0.0,
                confidence=row["confidence"] or 0.0,
                reasoning_chain=json.loads(row["reasoning_chain"] or "[]"),
                human_approved=bool(row["human_approved"]) if row["human_approved"] is not None else None,
                result_summary=row["result_summary"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None
            )
        finally:
            conn.close()
