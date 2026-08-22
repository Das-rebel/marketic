"""
CRM — Lead and Deal management with simple scoring.
"""

import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "marketic_memory.db")


def get_connection():
    """Get SQLite connection."""
    db_path = os.path.abspath(DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_crm_db():
    """Initialize CRM tables."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS crm_leads (
                lead_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                company TEXT,
                job_title TEXT,
                source TEXT DEFAULT 'organic',
                status TEXT DEFAULT 'new',
                score REAL DEFAULT 50.0,
                lifecycle_stage TEXT DEFAULT 'lead',
                tags TEXT DEFAULT '[]',
                attributes TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS crm_deals (
                deal_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                value REAL DEFAULT 0,
                stage TEXT DEFAULT 'lead',
                probability REAL DEFAULT 0.1,
                lead_id TEXT,
                owner_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT,
                FOREIGN KEY (lead_id) REFERENCES crm_leads(lead_id)
            );
            
            CREATE TABLE IF NOT EXISTS crm_activities (
                activity_id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                subject TEXT,
                notes TEXT,
                duration_minutes INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES crm_leads(lead_id)
            );
            
            CREATE TABLE IF NOT EXISTS crm_stage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT,
                lead_id TEXT,
                from_stage TEXT,
                to_stage TEXT,
                changed_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_leads_email ON crm_leads(email);
            CREATE INDEX IF NOT EXISTS idx_leads_status ON crm_leads(status);
            CREATE INDEX IF NOT EXISTS idx_deals_stage ON crm_deals(stage);
            CREATE INDEX IF NOT EXISTS idx_activities_entity ON crm_activities(entity_id);
        """)
        conn.commit()
    finally:
        conn.close()


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class DealStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"
    CAMPAIGN = "campaign"


@dataclass
class Lead:
    lead_id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    company: str
    job_title: str
    source: str
    status: LeadStatus
    score: float
    lifecycle_stage: str
    tags: List[str]
    attributes: Dict[str, Any]
    created_at: str
    updated_at: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email


@dataclass
class Deal:
    deal_id: str
    name: str
    value: float
    stage: DealStage
    probability: float
    lead_id: Optional[str]
    owner_id: str
    created_at: str
    updated_at: str
    closed_at: Optional[str]


@dataclass
class Activity:
    activity_id: str
    entity_id: str
    entity_type: str
    activity_type: ActivityType
    subject: str
    notes: str
    duration_minutes: int
    created_at: str


class CRMMaster:
    """Main CRM interface."""

    def __init__(self):
        init_crm_db()

    def create_lead(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        company: str = "",
        job_title: str = "",
        source: str = "organic",
        tags: List[str] = None,
    ) -> Lead:
        """Create a new lead."""
        tags = tags or []
        lead_id = str(uuid.uuid4())[:12]

        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO crm_leads 
                (lead_id, email, first_name, last_name, phone, company, job_title, source, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (lead_id, email, first_name, last_name, phone, company, job_title, source, json.dumps(tags)))
            conn.commit()
        finally:
            conn.close()

        return Lead(
            lead_id=lead_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company,
            job_title=job_title,
            source=source,
            status=LeadStatus.NEW,
            score=50.0,
            lifecycle_stage="lead",
            tags=tags,
            attributes={},
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM crm_leads WHERE lead_id = ?", (lead_id,)).fetchone()
            if not row:
                return None
            return self._row_to_lead(row)
        finally:
            conn.close()

    def score_lead(self, lead_id: str) -> float:
        """Calculate and update lead score."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM crm_leads WHERE lead_id = ?", (lead_id,)).fetchone()
            if not row:
                return 0.0

            score = 50.0  # Base score

            # Company indicator bonus
            if row["company"]:
                score += 15

            # Job title indicators
            title = (row["job_title"] or "").lower()
            if any(word in title for word in ["ceo", "cto", "cfo", "founder", "vp", "director", "head"]):
                score += 20
            elif any(word in title for word in ["manager", "lead", "senior"]):
                score += 10

            # Contact info completeness
            fields_filled = sum([bool(row["phone"]), bool(row["company"]), bool(row["job_title"])])
            score += fields_filled * 5

            # Activity bonus (would check activities table in production)
            activities_count = conn.execute(
                "SELECT COUNT(*) FROM crm_activities WHERE entity_id = ?", (lead_id,)
            ).fetchone()[0]
            score += min(activities_count * 5, 20)

            # Source scoring
            source_scores = {"organic": 10, "referral": 25, "paid": 15, "cold_outreach": 5}
            score += source_scores.get(row["source"], 10)

            # Cap at 100
            score = min(score, 100.0)

            # Update score
            conn.execute("UPDATE crm_leads SET score = ?, updated_at = CURRENT_TIMESTAMP WHERE lead_id = ?",
                        (score, lead_id))
            conn.commit()

            return score
        finally:
            conn.close()

    def search_leads(self, query: str, limit: int = 10) -> List[Lead]:
        """Search leads by email, name, or company."""
        conn = get_connection()
        try:
            q = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM crm_leads 
                WHERE email LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR company LIKE ?
                LIMIT ?
            """, (q, q, q, q, limit)).fetchall()
            return [self._row_to_lead(row) for row in rows]
        finally:
            conn.close()

    def create_deal(
        self,
        name: str,
        value: float = 0,
        stage: DealStage = DealStage.LEAD,
        lead_id: Optional[str] = None,
        owner_id: str = "",
    ) -> Deal:
        """Create a new deal."""
        deal_id = str(uuid.uuid4())[:12]
        stage_probabilities = {
            DealStage.LEAD: 0.1,
            DealStage.QUALIFIED: 0.25,
            DealStage.PROPOSAL: 0.5,
            DealStage.NEGOTIATION: 0.75,
            DealStage.CLOSED_WON: 1.0,
            DealStage.CLOSED_LOST: 0.0,
        }
        probability = stage_probabilities.get(stage, 0.1)

        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO crm_deals (deal_id, name, value, stage, probability, lead_id, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (deal_id, name, value, stage.value, probability, lead_id, owner_id))
            conn.commit()
        finally:
            conn.close()

        return Deal(
            deal_id=deal_id,
            name=name,
            value=value,
            stage=stage,
            probability=probability,
            lead_id=lead_id,
            owner_id=owner_id,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            closed_at=None,
        )

    def move_deal(self, deal_id: str, new_stage: DealStage) -> Optional[Deal]:
        """Move deal to a new stage."""
        conn = get_connection()
        try:
            # Get current stage
            row = conn.execute("SELECT stage FROM crm_deals WHERE deal_id = ?", (deal_id,)).fetchone()
            if not row:
                return None

            old_stage = row["stage"]

            # Calculate new probability
            stage_probabilities = {
                DealStage.LEAD: 0.1,
                DealStage.QUALIFIED: 0.25,
                DealStage.PROPOSAL: 0.5,
                DealStage.NEGOTIATION: 0.75,
                DealStage.CLOSED_WON: 1.0,
                DealStage.CLOSED_LOST: 0.0,
            }
            probability = stage_probabilities.get(new_stage, 0.1)

            # Update deal
            closed_at = datetime.utcnow().isoformat() if new_stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST] else None

            conn.execute("""
                UPDATE crm_deals 
                SET stage = ?, probability = ?, closed_at = ?, updated_at = CURRENT_TIMESTAMP
                WHERE deal_id = ?
            """, (new_stage.value, probability, closed_at, deal_id))

            # Log stage change
            conn.execute("""
                INSERT INTO crm_stage_history (deal_id, from_stage, to_stage)
                VALUES (?, ?, ?)
            """, (deal_id, old_stage, new_stage.value))

            conn.commit()

            # Return updated deal
            row = conn.execute("SELECT * FROM crm_deals WHERE deal_id = ?", (deal_id,)).fetchone()
            if not row:
                return None

            return Deal(
                deal_id=row["deal_id"],
                name=row["name"],
                value=row["value"],
                stage=DealStage(row["stage"]),
                probability=row["probability"],
                lead_id=row["lead_id"],
                owner_id=row["owner_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                closed_at=row["closed_at"],
            )
        finally:
            conn.close()

    def log_activity(
        self,
        entity_id: str,
        activity_type: ActivityType,
        subject: str = "",
        notes: str = "",
        duration_minutes: int = 0,
    ) -> Activity:
        """Log an activity on a lead or deal."""
        activity_id = str(uuid.uuid4())[:12]

        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO crm_activities (activity_id, entity_id, entity_type, activity_type, subject, notes, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (activity_id, entity_id, "lead", activity_type.value, subject, notes, duration_minutes))
            conn.commit()
        finally:
            conn.close()

        return Activity(
            activity_id=activity_id,
            entity_id=entity_id,
            entity_type="lead",
            activity_type=activity_type,
            subject=subject,
            notes=notes,
            duration_minutes=duration_minutes,
            created_at=datetime.utcnow().isoformat(),
        )

    def get_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get timeline of activities for a lead or deal."""
        conn = get_connection()
        try:
            # Get activities
            activities = conn.execute("""
                SELECT * FROM crm_activities 
                WHERE entity_id = ?
                ORDER BY created_at DESC
            """, (entity_id,)).fetchall()

            timeline = []
            for a in activities:
                timeline.append({
                    "type": a["activity_type"],
                    "subject": a["subject"],
                    "notes": a["notes"],
                    "date": a["created_at"],
                })

            # Get stage changes
            stage_changes = conn.execute("""
                SELECT * FROM crm_stage_history 
                WHERE deal_id = ? OR lead_id = ?
                ORDER BY changed_at DESC
            """, (entity_id, entity_id)).fetchall()

            for sc in stage_changes:
                timeline.append({
                    "type": "stage_change",
                    "from": sc["from_stage"],
                    "to": sc["to_stage"],
                    "date": sc["changed_at"],
                })

            # Sort by date
            timeline.sort(key=lambda x: x["date"], reverse=True)

            return timeline
        finally:
            conn.close()

    def get_crm_dashboard(self) -> Dict[str, Any]:
        """Get CRM dashboard metrics."""
        conn = get_connection()
        try:
            # Lead counts by stage
            lead_counts = {}
            for status in LeadStatus:
                count = conn.execute(
                    "SELECT COUNT(*) FROM crm_leads WHERE status = ?", (status.value,)
                ).fetchone()[0]
                lead_counts[status.value] = count

            # Deal pipeline value by stage
            deal_pipeline = {}
            total_pipeline = 0.0
            for stage in DealStage:
                result = conn.execute("""
                    SELECT SUM(value) as total, COUNT(*) as count 
                    FROM crm_deals 
                    WHERE stage = ? AND closed_at IS NULL
                """, (stage.value,)).fetchone()
                deal_pipeline[stage.value] = {
                    "count": result[1] or 0,
                    "value": result[0] or 0.0,
                }
                if stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]:
                    total_pipeline += result[0] or 0

            # Recent activities
            recent = conn.execute("""
                SELECT * FROM crm_activities 
                ORDER BY created_at DESC LIMIT 10
            """).fetchall()

            return {
                "leads": {
                    "total": sum(lead_counts.values()),
                    "by_status": lead_counts,
                    "avg_score": conn.execute("SELECT AVG(score) FROM crm_leads").fetchone()[0] or 0,
                },
                "deals": {
                    "total_pipeline": round(total_pipeline, 2),
                    "by_stage": deal_pipeline,
                    "total_open": sum(d["count"] for d in deal_pipeline.values()),
                },
                "recent_activities": [
                    {"type": a["activity_type"], "subject": a["subject"], "date": a["created_at"]}
                    for a in recent
                ],
            }
        finally:
            conn.close()

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get deal pipeline summary."""
        conn = get_connection()
        try:
            stages = []
            for stage in DealStage:
                if stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]:
                    continue

                result = conn.execute("""
                    SELECT SUM(value) as total, COUNT(*) as count, AVG(probability) as avg_prob
                    FROM crm_deals 
                    WHERE stage = ?
                """, (stage.value,)).fetchone()

                stages.append({
                    "stage": stage.value,
                    "count": result[1] or 0,
                    "value": result[0] or 0.0,
                    "probability": result[2] or 0.1,
                    "weighted_value": (result[0] or 0.0) * (result[2] or 0.1),
                })

            # Calculate totals
            total_value = sum(s["value"] for s in stages)
            weighted_total = sum(s["weighted_value"] for s in stages)

            return {
                "stages": stages,
                "total_value": round(total_value, 2),
                "weighted_value": round(weighted_total, 2),
                "total_deals": sum(s["count"] for s in stages),
            }
        finally:
            conn.close()

    def _row_to_lead(self, row) -> Lead:
        """Convert database row to Lead object."""
        return Lead(
            lead_id=row["lead_id"],
            email=row["email"],
            first_name=row["first_name"] or "",
            last_name=row["last_name"] or "",
            phone=row["phone"] or "",
            company=row["company"] or "",
            job_title=row["job_title"] or "",
            source=row["source"] or "organic",
            status=LeadStatus(row["status"]),
            score=row["score"] or 50.0,
            lifecycle_stage=row["lifecycle_stage"] or "lead",
            tags=json.loads(row["tags"] or "[]"),
            attributes=json.loads(row["attributes"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
