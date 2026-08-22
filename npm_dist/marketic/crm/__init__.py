"""
Marketic CRM — Lightweight Jack-of-All-Trades CRM

A unified CRM layer that works across all marketing platforms.
Provides: Lead management, pipeline tracking, contact enrichment, activity logging.

Based on research from Frappe CRM, Chatwoot, HubSpot, and Pipedrive.

Usage:
    from marketic.crm import CRMMaster, Lead, Deal, Pipeline, Activity

    crm = CRMMaster()
    lead = crm.create_lead(email="john@acme.com", company="Acme Corp")
    deal = crm.create_deal(lead_id=lead.id, value=50000, stage="proposal")
    crm.log_activity(deal.id, "sent_proposal", notes="Sent proposal v2")
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable


# ═══════════════════════════════════════════════════════════════
# Core Enums
# ═══════════════════════════════════════════════════════════════

class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    LOST = "lost"


class DealStage(Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"
    CAMPAIGN = "campaign"
    WEBINAR = "webinar"
    DEMO = "demo"
    PROPOSAL_SENT = "proposal_sent"
    CONTRACT_SENT = "contract_sent"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ═══════════════════════════════════════════════════════════════
# Core Data Models
# ═══════════════════════════════════════════════════════════════

@dataclass
class Lead:
    """A marketing/sales lead."""
    lead_id: str = ""
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    company: str = ""
    job_title: str = ""
    source: str = ""  # organic, paid, referral, social, cold_outreach
    status: LeadStatus = LeadStatus.NEW
    score: int = 0  # 0-100 lead quality score
    lifecycle_stage: str = "lead"
    tags: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    owner_id: str = ""  # sales rep
    created_at: str = ""
    updated_at: str = ""
    converted_at: Optional[str] = None
    converted_deal_id: Optional[str] = None

    def __post_init__(self):
        if not self.lead_id:
            self.lead_id = f"lead_{hashlib.md5(f'{self.email}{time.time()}'.encode()).hexdigest()[:10]}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def display_name(self) -> str:
        return self.full_name or self.company or self.email


@dataclass
class Company:
    """Company/Account record."""
    company_id: str = ""
    name: str = ""
    domain: str = ""
    industry: str = ""
    size: str = ""  # startup, smb, mid-market, enterprise
    revenue: float = 0.0
    address: str = ""
    city: str = ""
    country: str = ""
    linkedin_url: str = ""
    twitter_handle: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    lead_ids: List[str] = field(default_factory=list)
    deal_ids: List[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.company_id:
            self.company_id = f"co_{hashlib.md5(f'{self.name}{self.domain}'.encode()).hexdigest()[:10]}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class Deal:
    """A sales opportunity/deal."""
    deal_id: str = ""
    name: str = ""
    value: float = 0.0
    currency: str = "USD"
    stage: DealStage = DealStage.LEAD
    probability: int = 10  # 0-100
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    owner_id: str = ""
    expected_close_date: Optional[str] = None
    actual_close_date: Optional[str] = None
    lost_reason: str = ""
    tags: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    stage_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.deal_id:
            self.deal_id = f"deal_{hashlib.md5(f'{self.name}{time.time()}'.encode()).hexdigest()[:10]}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
            self.stage_history = [{"stage": self.stage.value, "timestamp": self.created_at}]
        self.updated_at = datetime.utcnow().isoformat()


@dataclass
class Activity:
    """An activity log entry (call, email, meeting, note, task)."""
    activity_id: str = ""
    activity_type: ActivityType = ActivityType.NOTE
    entity_type: str = ""  # lead, deal, company, contact
    entity_id: str = ""
    subject: str = ""
    notes: str = ""
    duration_minutes: int = 0
    priority: Priority = Priority.MEDIUM
    due_date: Optional[str] = None
    completed: bool = False
    completed_at: Optional[str] = None
    owner_id: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    created_by: str = ""

    def __post_init__(self):
        if not self.activity_id:
            self.activity_id = f"act_{hashlib.md5(f'{self.entity_id}{self.activity_type.value}{time.time()}'.encode()).hexdigest()[:10]}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class Task:
    """A to-do task."""
    task_id: str = ""
    title: str = ""
    description: str = ""
    entity_type: str = ""  # lead, deal, company
    entity_id: str = ""
    priority: Priority = Priority.MEDIUM
    due_date: Optional[str] = None
    assigned_to: str = ""
    completed: bool = False
    completed_at: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.task_id:
            self.task_id = f"task_{hashlib.md5(f'{self.title}{time.time()}'.encode()).hexdigest()[:10]}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class Pipeline:
    """A sales pipeline with stages."""
    pipeline_id: str = ""
    name: str = ""
    stages: List[DealStage] = field(default_factory=list)
    stage_probabilities: Dict[str, int] = field(default_factory=dict)
    is_default: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.pipeline_id:
            self.pipeline_id = f"pipe_{hashlib.md5(f'{self.name}'.encode()).hexdigest()[:8]}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        # Default probabilities if not set
        if not self.stage_probabilities:
            self.stage_probabilities = {
                "lead": 10,
                "qualified": 25,
                "proposal": 50,
                "negotiation": 75,
                "closed_won": 100,
                "closed_lost": 0,
            }


# ═══════════════════════════════════════════════════════════════
# CRM Master — Jack of All Trades
# ═══════════════════════════════════════════════════════════════

class CRMMaster:
    """
    Lightweight unified CRM — works with any marketing platform.

    Provides a single interface for leads, deals, contacts, activities, tasks.
    Automatically syncs with connected marketing platforms.

    Usage:
        crm = CRMMaster()
        lead = crm.create_lead(email="john@acme.com")
        deal = crm.create_deal(lead_id=lead.lead_id, value=50000)
        crm.log_call(deal.deal_id, duration=30, notes="Discussed pricing")
    """

    def __init__(self):
        # In-memory stores (replace with DB in production)
        self._leads: Dict[str, Lead] = {}
        self._companies: Dict[str, Company] = {}
        self._deals: Dict[str, Deal] = {}
        self._activities: Dict[str, Activity] = {}
        self._tasks: Dict[str, Task] = {}
        self._pipelines: Dict[str, Pipeline] = {}

        # Initialize default pipeline
        self._init_default_pipeline()

    def _init_default_pipeline(self):
        """Initialize the default sales pipeline."""
        pipeline = Pipeline(
            name="Sales Pipeline",
            stages=[
                DealStage.LEAD,
                DealStage.QUALIFIED,
                DealStage.PROPOSAL,
                DealStage.NEGOTIATION,
                DealStage.CLOSED_WON,
                DealStage.CLOSED_LOST,
            ],
            is_default=True,
        )
        self._pipelines["default"] = pipeline

    # ── Lead Operations ──

    def create_lead(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        company: str = "",
        job_title: str = "",
        source: str = "",
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        owner_id: str = "",
    ) -> Lead:
        """Create a new lead."""
        lead = Lead(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company,
            job_title=job_title,
            source=source,
            tags=tags or [],
            attributes=attributes or {},
            owner_id=owner_id,
        )
        self._leads[lead.lead_id] = lead
        return lead

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        return self._leads.get(lead_id)

    def update_lead(self, lead_id: str, **kwargs) -> Optional[Lead]:
        lead = self._leads.get(lead_id)
        if not lead:
            return None
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        lead.updated_at = datetime.utcnow().isoformat()
        return lead

    def score_lead(self, lead_id: str) -> int:
        """Calculate lead score based on attributes."""
        lead = self._leads.get(lead_id)
        if not lead:
            return 0

        score = 0
        # Email provided: +10
        if lead.email:
            score += 10
        # Company provided: +15
        if lead.company:
            score += 15
        # Job title provided: +10
        if lead.job_title:
            score += 10
        # Has phone: +10
        if lead.phone:
            score += 10
        # Source scoring
        source_scores = {"organic": 20, "paid": 15, "referral": 25, "social": 10, "cold_outreach": 5}
        score += source_scores.get(lead.source, 5)
        # Attribute-based scoring
        score += lead.attributes.get("engagement_score", 0)

        lead.score = min(score, 100)
        return lead.score

    def qualify_lead(self, lead_id: str) -> Optional[Lead]:
        """Mark lead as qualified (MQL)."""
        return self.update_lead(lead_id, status=LeadStatus.QUALIFIED, lifecycle_stage="mql")

    def convert_lead(self, lead_id: str, deal_value: float = 0) -> Optional[Deal]:
        """Convert a lead into a deal."""
        lead = self._leads.get(lead_id)
        if not lead or lead.status == LeadStatus.CONVERTED:
            return None

        # Create deal from lead
        deal = Deal(
            name=f"{lead.full_name} - {lead.company}",
            value=deal_value,
            lead_id=lead_id,
            company_id=self._find_or_create_company(lead),
            owner_id=lead.owner_id,
            stage=DealStage.LEAD,
            probability=10,
        )
        self._deals[deal.deal_id] = deal

        # Update lead
        lead.status = LeadStatus.CONVERTED
        lead.lifecycle_stage = "sql"
        lead.converted_at = datetime.utcnow().isoformat()
        lead.converted_deal_id = deal.deal_id
        lead.updated_at = datetime.utcnow().isoformat()

        return deal

    def search_leads(self, query: str, limit: int = 50) -> List[Lead]:
        """Search leads by name, email, company."""
        results = []
        q = query.lower()
        for lead in self._leads.values():
            if (q in lead.email.lower() or q in lead.first_name.lower() or
                q in lead.last_name.lower() or q in lead.company.lower()):
                results.append(lead)
        return results[:limit]

    # ── Deal Operations ──

    def create_deal(
        self,
        name: str,
        value: float = 0,
        stage: DealStage = DealStage.LEAD,
        lead_id: Optional[str] = None,
        company_id: Optional[str] = None,
        owner_id: str = "",
        expected_close_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Deal:
        """Create a new deal."""
        deal = Deal(
            name=name,
            value=value,
            stage=stage,
            lead_id=lead_id,
            company_id=company_id,
            owner_id=owner_id,
            expected_close_date=expected_close_date,
            tags=tags or [],
            attributes=attributes or {},
            probability=self._get_stage_probability(stage),
        )
        self._deals[deal.deal_id] = deal
        return deal

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        return self._deals.get(deal_id)

    def update_deal(self, deal_id: str, **kwargs) -> Optional[Deal]:
        deal = self._deals.get(deal_id)
        if not deal:
            return None
        for key, value in kwargs.items():
            if hasattr(deal, key):
                setattr(deal, key, value)
        deal.updated_at = datetime.utcnow().isoformat()
        return deal

    def move_deal(self, deal_id: str, new_stage: DealStage) -> Optional[Deal]:
        """Move deal to a new pipeline stage."""
        deal = self._deals.get(deal_id)
        if not deal:
            return None

        old_stage = deal.stage
        deal.stage = new_stage
        deal.probability = self._get_stage_probability(new_stage)
        deal.stage_history.append({
            "from": old_stage.value,
            "to": new_stage.value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        deal.updated_at = datetime.utcnow().isoformat()

        # Handle closed states
        if new_stage == DealStage.CLOSED_WON:
            deal.actual_close_date = datetime.utcnow().isoformat()
        elif new_stage == DealStage.CLOSED_LOST:
            deal.actual_close_date = datetime.utcnow().isoformat()

        return deal

    def _get_stage_probability(self, stage: DealStage) -> int:
        """Get probability for a stage."""
        probs = {
            DealStage.LEAD: 10,
            DealStage.QUALIFIED: 25,
            DealStage.PROPOSAL: 50,
            DealStage.NEGOTIATION: 75,
            DealStage.CLOSED_WON: 100,
            DealStage.CLOSED_LOST: 0,
        }
        return probs.get(stage, 10)

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get pipeline summary with values per stage."""
        summary = {}
        total_value = 0
        total_count = 0

        for deal in self._deals.values():
            stage_key = deal.stage.value
            if stage_key not in summary:
                summary[stage_key] = {"count": 0, "value": 0.0, "deals": []}

            summary[stage_key]["count"] += 1
            summary[stage_key]["value"] += deal.value
            summary[stage_key]["deals"].append({
                "deal_id": deal.deal_id,
                "name": deal.name,
                "value": deal.value,
                "probability": deal.probability,
            })
            total_value += deal.value
            total_count += 1

        return {
            "total_deals": total_count,
            "total_value": total_value,
            "stages": summary,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ── Activity Operations ──

    def log_activity(
        self,
        entity_id: str,
        activity_type: ActivityType,
        subject: str = "",
        notes: str = "",
        duration_minutes: int = 0,
        priority: Priority = Priority.MEDIUM,
        attributes: Optional[Dict[str, Any]] = None,
        owner_id: str = "",
    ) -> Activity:
        """Log an activity against a lead or deal."""
        activity = Activity(
            activity_type=activity_type,
            entity_type="deal" if entity_id.startswith("deal_") else "lead",
            entity_id=entity_id,
            subject=subject,
            notes=notes,
            duration_minutes=duration_minutes,
            priority=priority,
            attributes=attributes or {},
            owner_id=owner_id,
        )
        self._activities[activity.activity_id] = activity
        return activity

    def log_call(
        self,
        entity_id: str,
        duration_minutes: int,
        notes: str = "",
        outcome: str = "",
    ) -> Activity:
        """Log a phone call."""
        return self.log_activity(
            entity_id=entity_id,
            activity_type=ActivityType.CALL,
            subject=f"Call ({duration_minutes} min)",
            notes=notes,
            duration_minutes=duration_minutes,
            attributes={"outcome": outcome},
        )

    def log_email(self, entity_id: str, subject: str, notes: str = "") -> Activity:
        """Log an email."""
        return self.log_activity(
            entity_id=entity_id,
            activity_type=ActivityType.EMAIL,
            subject=subject,
            notes=notes,
        )

    def log_meeting(self, entity_id: str, duration_minutes: int, notes: str = "") -> Activity:
        """Log a meeting."""
        return self.log_activity(
            entity_id=entity_id,
            activity_type=ActivityType.MEETING,
            subject=f"Meeting ({duration_minutes} min)",
            notes=notes,
            duration_minutes=duration_minutes,
        )

    def log_note(self, entity_id: str, notes: str) -> Activity:
        """Log a note."""
        return self.log_activity(
            entity_id=entity_id,
            activity_type=ActivityType.NOTE,
            notes=notes,
        )

    def get_activities(self, entity_id: str, limit: int = 50) -> List[Activity]:
        """Get activities for a lead or deal."""
        return [
            a for a in self._activities.values()
            if a.entity_id == entity_id
        ][-limit:]

    # ── Task Operations ──

    def create_task(
        self,
        title: str,
        entity_id: str = "",
        entity_type: str = "",
        assigned_to: str = "",
        due_date: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
    ) -> Task:
        """Create a task."""
        task = Task(
            title=title,
            entity_id=entity_id,
            entity_type=entity_type,
            assigned_to=assigned_to,
            due_date=due_date,
            priority=priority,
        )
        self._tasks[task.task_id] = task
        return task

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed."""
        task = self._tasks.get(task_id)
        if task:
            task.completed = True
            task.completed_at = datetime.utcnow().isoformat()
        return task

    def get_pending_tasks(self, assigned_to: str = "") -> List[Task]:
        """Get uncompleted tasks, optionally filtered by assignee."""
        tasks = [t for t in self._tasks.values() if not t.completed]
        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        return sorted(tasks, key=lambda t: (t.priority.value, t.due_date or ""))

    # ── Company Operations ──

    def _find_or_create_company(self, lead: Lead) -> Optional[str]:
        """Find or create company from lead data."""
        if not lead.company:
            return None

        # Search existing
        for company in self._companies.values():
            if company.name.lower() == lead.company.lower():
                if lead.lead_id not in company.lead_ids:
                    company.lead_ids.append(lead.lead_id)
                return company.company_id

        # Create new
        company = Company(name=lead.company)
        company.lead_ids.append(lead.lead_id)
        self._companies[company.company_id] = company
        return company.company_id

    # ── Dashboard / Analytics ──

    def get_crm_dashboard(self) -> Dict[str, Any]:
        """Get CRM dashboard metrics."""
        total_leads = len(self._leads)
        new_leads = sum(1 for l in self._leads.values() if l.status == LeadStatus.NEW)
        qualified_leads = sum(1 for l in self._leads.values() if l.status == LeadStatus.QUALIFIED)

        total_deals = len(self._deals)
        open_deals = sum(1 for d in self._deals.values() if d.stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
        won_deals = sum(1 for d in self._deals.values() if d.stage == DealStage.CLOSED_WON)
        lost_deals = sum(1 for d in self._deals.values() if d.stage == DealStage.CLOSED_LOST)

        total_revenue = sum(d.value for d in self._deals.values() if d.stage == DealStage.CLOSED_WON)
        pipeline_value = sum(d.value * d.probability / 100 for d in self._deals.values() if d.stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST])

        avg_deal_size = total_revenue / won_deals if won_deals > 0 else 0
        win_rate = (won_deals / (won_deals + lost_deals) * 100) if (won_deals + lost_deals) > 0 else 0

        pending_tasks = len([t for t in self._tasks.values() if not t.completed])

        return {
            "leads": {
                "total": total_leads,
                "new": new_leads,
                "qualified": qualified_leads,
                "conversion_rate": f"{(qualified_leads/total_leads*100):.1f}%" if total_leads > 0 else "0%",
            },
            "deals": {
                "total": total_deals,
                "open": open_deals,
                "won": won_deals,
                "lost": lost_deals,
                "total_revenue": total_revenue,
                "pipeline_value": pipeline_value,
                "avg_deal_size": avg_deal_size,
                "win_rate": f"{win_rate:.1f}%",
            },
            "tasks": {
                "pending": pending_tasks,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get a combined timeline of activities and stage changes for an entity."""
        events = []

        # Add activities
        for activity in self.get_activities(entity_id):
            events.append({
                "type": activity.activity_type.value,
                "timestamp": activity.created_at,
                "summary": activity.subject or activity.notes[:100],
                "details": {
                    "notes": activity.notes,
                    "duration_minutes": activity.duration_minutes,
                },
            })

        # Add deal stage changes
        if entity_id.startswith("deal_"):
            deal = self._deals.get(entity_id)
            if deal:
                for change in deal.stage_history:
                    events.append({
                        "type": "stage_change",
                        "timestamp": change["timestamp"],
                        "summary": f"Moved to {change['to']}",
                        "details": change,
                    })

        # Sort by timestamp
        events.sort(key=lambda e: e["timestamp"], reverse=True)
        return events
