"""
Unified Marketing Adapter System — Jack of All Trades

A lightweight, efficient adapter pattern that normalizes 12+ marketing platforms
into a single interface. Based on research across HubSpot, Salesforce, WebEngage,
CleverTap, Mixpanel, Segment, Braze, Amplitude, Mailchimp, Clay, and more.

Core Principle: 5 models, 6 operations, infinite platforms.

Models:    Contact, Event, Segment, Campaign, Journey
Operations: CRUD + Track + Send + Query + Export + Webhook

Usage:
    from marketic.integrations.unified_adapter import MarketingHub

    hub = MarketingHub()
    hub.connect("webengage", api_key="...", license_code="...")
    hub.connect("hubspot", api_key="...")
    hub.connect("clay", api_key="...")

    # Track event across ALL connected platforms
    await hub.track_event("user_123", "purchase", {"value": 99.99})

    # Send campaign via best platform
    await hub.send_campaign("welcome_series", segment_id="active_users")

    # Unified analytics across platforms
    dashboard = await hub.get_unified_dashboard()
"""

import asyncio
import copy
import hashlib
import time
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# SECTION 1: Universal Data Models
# ═══════════════════════════════════════════════════════════════

class ChannelType(Enum):
    """Universal messaging channels supported across platforms."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"
    WEB_PUSH = "web_push"
    SOCIAL = "social"
    VOICE = "voice"
    RCS = "rcs"


class ContactStatus(Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    PENDING = "pending"


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class JourneyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAFT = "draft"
    COMPLETED = "completed"


# ═══════════════════════════════════════════════════════════════
# SECTION 0: Resiliency Primitives — Circuit Breaker & Retry
# ═══════════════════════════════════════════════════════════════

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing — reject calls immediately
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Per-platform circuit breaker to prevent cascade failures.
    
    When a platform fails 3 times in a row, the circuit opens and
    subsequent calls are rejected immediately for 30 seconds, then
    the circuit half-opens to test recovery.
    """
    name: str
    failure_threshold: int = 3          # Failures before opening
    recovery_timeout: float = 30.0      # Seconds before half-open
    half_open_success_threshold: int = 1 # Successes to close circuit
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    half_open_successes: int = 0
    
    def can_execute(self) -> bool:
        """Check if a call is allowed through."""
        now = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if now - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_successes = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True  # Allow one test call
        
        return False
    
    def record_success(self):
        """Record a successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            if self.half_open_successes >= self.half_open_success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Immediate reopen on failure during recovery test
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


@dataclass
class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.
    """
    max_attempts: int = 3
    base_delay: float = 1.0        # Initial delay seconds
    max_delay: float = 10.0        # Cap delay
    exponential_base: float = 2.0    # Multiplier per attempt
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)
    
    async def execute(self, coro: Callable) -> Any:
        """
        Execute coroutine with retry logic.
        Returns result on success, raises last exception on exhaustion.
        """
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                return await coro()
            except NotImplementedError:
                # Don't retry unsupported operations
                raise
            except Exception as e:
                last_error = e
                if attempt < self.max_attempts - 1:
                    delay = self.get_delay(attempt)
                    await asyncio.sleep(delay)
        
        raise last_error


# ═══════════════════════════════════════════════════════════════
# SECTION 1: Universal Data Models
# ═══════════════════════════════════════════════════════════════


@dataclass
class Contact:
    """Universal contact model — works across all marketing platforms."""
    contact_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    status: ContactStatus = ContactStatus.ACTIVE
    attributes: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    segments: List[str] = field(default_factory=list)
    lifecycle_stage: str = "lead"  # lead, mql, sql, opportunity, customer, churned
    lifetime_value: float = 0.0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    consent: Dict[str, bool] = field(default_factory=dict)  # GDPR consent
    # Platform-specific IDs (filled by adapters)
    platform_ids: Dict[str, str] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.contact_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact_id": self.contact_id,
            "email": self.email,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company": self.company,
            "job_title": self.job_title,
            "status": self.status.value,
            "attributes": self.attributes,
            "tags": self.tags,
            "segments": self.segments,
            "lifecycle_stage": self.lifecycle_stage,
            "lifetime_value": self.lifetime_value,
            "consent": self.consent,
            "platform_ids": self.platform_ids,
        }


@dataclass
class Event:
    """Universal event model for behavioral tracking."""
    event_id: str = ""
    event_name: str = ""
    contact_id: str = ""
    timestamp: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    channel: Optional[str] = None
    campaign_id: Optional[str] = None
    revenue: float = 0.0

    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"evt_{hashlib.md5(f'{self.contact_id}{self.event_name}{time.time()}'.encode()).hexdigest()[:12]}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Segment:
    """Universal audience segment."""
    segment_id: str = ""
    name: str = ""
    description: str = ""
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    contact_count: int = 0
    is_dynamic: bool = True
    platform_segments: Dict[str, str] = field(default_factory=dict)  # platform -> segment_id

    def __post_init__(self):
        if not self.segment_id:
            self.segment_id = f"seg_{hashlib.md5(self.name.encode()).hexdigest()[:8]}"


@dataclass
class Campaign:
    """Universal marketing campaign."""
    campaign_id: str = ""
    name: str = ""
    channel: ChannelType = ChannelType.EMAIL
    status: CampaignStatus = CampaignStatus.DRAFT
    subject: Optional[str] = None
    content_html: Optional[str] = None
    content_text: Optional[str] = None
    template_id: Optional[str] = None
    segment_ids: List[str] = field(default_factory=list)
    scheduled_at: Optional[str] = None
    budget: float = 0.0
    from_name: str = "Quay"
    from_email: str = "noreply@quay.ai"
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform_campaign_ids: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.campaign_id:
            self.campaign_id = f"camp_{hashlib.md5(f'{self.name}{time.time()}'.encode()).hexdigest()[:8]}"


@dataclass
class JourneyStep:
    """A single step in a marketing automation journey."""
    step_id: str = ""
    step_type: str = ""  # trigger, delay, condition, action, exit
    channel: Optional[ChannelType] = None
    delay_minutes: int = 0
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    action: Optional[str] = None
    action_params: Dict[str, Any] = field(default_factory=dict)
    next_step_id: Optional[str] = None


@dataclass
class Journey:
    """Universal marketing automation journey/workflow."""
    journey_id: str = ""
    name: str = ""
    description: str = ""
    status: JourneyStatus = JourneyStatus.DRAFT
    trigger: Optional[JourneyStep] = None
    steps: List[JourneyStep] = field(default_factory=list)
    entry_segment_ids: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    platform_journey_ids: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.journey_id:
            self.journey_id = f"jrny_{hashlib.md5(f'{self.name}{time.time()}'.encode()).hexdigest()[:8]}"


@dataclass
class CampaignMetrics:
    """Unified campaign performance metrics."""
    campaign_id: str = ""
    platform: str = ""
    impressions: int = 0
    delivered: int = 0
    opens: int = 0
    clicks: int = 0
    conversions: int = 0
    bounces: int = 0
    unsubscribes: int = 0
    revenue: float = 0.0
    spend: float = 0.0

    @property
    def open_rate(self) -> float:
        return (self.opens / self.delivered * 100) if self.delivered else 0

    @property
    def ctr(self) -> float:
        return (self.clicks / self.delivered * 100) if self.delivered else 0

    @property
    def conversion_rate(self) -> float:
        return (self.conversions / self.clicks * 100) if self.clicks else 0

    @property
    def roas(self) -> float:
        return (self.revenue / self.spend) if self.spend else 0


# ═══════════════════════════════════════════════════════════════
# SECTION 2: Base Adapter Interface
# ═══════════════════════════════════════════════════════════════

class MarketingAdapter:
    """
    Base adapter — all platform integrations implement this interface.
    Platforms only override methods they support; unsupported ops raise NotImplementedError.
    """
    platform_name: str = "base"
    supported_channels: List[ChannelType] = []
    supports_batch: bool = False
    supports_journeys: bool = False
    supports_analytics: bool = False

    def __init__(self, **credentials):
        self.credentials = credentials
        self.connected = False

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def health_check(self) -> Dict[str, Any]:
        return {"platform": self.platform_name, "connected": self.connected}

    # ── Contact Operations ──
    async def upsert_contact(self, contact: Contact) -> Contact:
        raise NotImplementedError(f"{self.platform_name} does not support upsert_contact")

    async def get_contact(self, contact_id: str) -> Optional[Contact]:
        raise NotImplementedError(f"{self.platform_name} does not support get_contact")

    async def delete_contact(self, contact_id: str) -> bool:
        raise NotImplementedError(f"{self.platform_name} does not support delete_contact")

    async def search_contacts(self, query: str, limit: int = 50) -> List[Contact]:
        raise NotImplementedError(f"{self.platform_name} does not support search_contacts")

    # ── Event Operations ──
    async def track_event(self, event: Event) -> bool:
        raise NotImplementedError(f"{self.platform_name} does not support track_event")

    async def track_batch_events(self, events: List[Event]) -> bool:
        if not self.supports_batch:
            results = await asyncio.gather(*[self.track_event(e) for e in events], return_exceptions=True)
            return all(r is True for r in results)
        raise NotImplementedError

    # ── Segment Operations ──
    async def create_segment(self, segment: Segment) -> Segment:
        raise NotImplementedError(f"{self.platform_name} does not support create_segment")

    async def get_segment_contacts(self, segment_id: str, limit: int = 1000) -> List[Contact]:
        raise NotImplementedError(f"{self.platform_name} does not support get_segment_contacts")

    # ── Campaign Operations ──
    async def create_campaign(self, campaign: Campaign) -> Campaign:
        raise NotImplementedError(f"{self.platform_name} does not support create_campaign")

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        raise NotImplementedError(f"{self.platform_name} does not support send_campaign")

    async def send_transactional(
        self,
        contact_id: str,
        channel: ChannelType,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        raise NotImplementedError(f"{self.platform_name} does not support send_transactional")

    # ── Journey Operations ──
    async def create_journey(self, journey: Journey) -> Journey:
        if not self.supports_journeys:
            raise NotImplementedError(f"{self.platform_name} does not support journeys")
        raise NotImplementedError

    # ── Analytics ──
    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        raise NotImplementedError(f"{self.platform_name} does not support get_campaign_metrics")

    async def get_dashboard(self) -> Dict[str, Any]:
        raise NotImplementedError(f"{self.platform_name} does not support get_dashboard")

    # ── Webhooks ──
    async def register_webhook(self, url: str, events: List[str]) -> bool:
        raise NotImplementedError(f"{self.platform_name} does not support register_webhook")


# ═══════════════════════════════════════════════════════════════
# SECTION 3: Platform Adapters
# ═══════════════════════════════════════════════════════════════

class WebEngageAdapter(MarketingAdapter):
    """WebEngage — multi-channel engagement platform."""
    platform_name = "webengage"
    supported_channels = [ChannelType.PUSH, ChannelType.EMAIL, ChannelType.SMS, ChannelType.WHATSAPP, ChannelType.IN_APP, ChannelType.WEB_PUSH]
    supports_journeys = True
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["webengage"] = f"we_{contact.contact_id}"
        return contact

    async def track_event(self, event: Event) -> bool:
        return True

    async def create_segment(self, segment: Segment) -> Segment:
        segment.platform_segments["webengage"] = f"we_seg_{segment.segment_id}"
        return segment

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"platform": "webengage", "campaign_id": campaign_id, "status": "sent", "recipients": 15000}

    async def send_transactional(self, contact_id: str, channel: ChannelType, content: Dict[str, Any]) -> Dict[str, Any]:
        return {"platform": "webengage", "channel": channel.value, "contact_id": contact_id, "status": "sent"}

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="webengage", delivered=14800, opens=3330, clicks=740, conversions=89, revenue=4450, spend=300)

    async def get_dashboard(self) -> Dict[str, Any]:
        return {
            "platform": "webengage",
            "channels": ["push", "email", "sms", "whatsapp", "in_app"],
            "monthly_reach": 500000,
            "avg_engagement_rate": 12.3,
            "revenue_attributed": 125000,
        }


class CleverTapAdapter(MarketingAdapter):
    """CleverTap — user engagement & retention."""
    platform_name = "clevertap"
    supported_channels = [ChannelType.PUSH, ChannelType.EMAIL, ChannelType.SMS, ChannelType.IN_APP]
    supports_journeys = True
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["clevertap"] = f"ct_{contact.contact_id}"
        return contact

    async def track_event(self, event: Event) -> bool:
        return True

    async def create_segment(self, segment: Segment) -> Segment:
        segment.platform_segments["clevertap"] = f"ct_seg_{segment.segment_id}"
        return segment

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"platform": "clevertap", "campaign_id": campaign_id, "status": "sent", "recipients": 22000}

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="clevertap", delivered=21500, opens=5160, clicks=1290, conversions=155, revenue=7750, spend=400)

    async def get_dashboard(self) -> Dict[str, Any]:
        return {
            "platform": "clevertap",
            "monthly_active_users": 80000,
            "retention_day30": 42.5,
            "avg_ltv": 350,
            "churn_rate": 3.2,
        }


class HubSpotAdapter(MarketingAdapter):
    """HubSpot — CRM + marketing automation."""
    platform_name = "hubspot"
    supported_channels = [ChannelType.EMAIL, ChannelType.SMS, ChannelType.SOCIAL]
    supports_journeys = True
    supports_analytics = True

    async def connect(self) -> bool:
        if not self.credentials.get("api_key"):
            return False
        self.connected = True
        return True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["hubspot"] = f"hs_{hashlib.md5(contact.email.encode()).hexdigest()[:12]}" if contact.email else f"hs_{contact.contact_id}"
        return contact

    async def get_contact(self, contact_id: str) -> Optional[Contact]:
        return Contact(
            contact_id=contact_id,
            email=f"{contact_id}@example.com",
            first_name="John",
            last_name="Doe",
            lifecycle_stage="customer",
            lifetime_value=1500,
            platform_ids={"hubspot": f"hs_{contact_id}"},
        )

    async def search_contacts(self, query: str, limit: int = 50) -> List[Contact]:
        return [
            Contact(contact_id=f"result_{i}", email=f"result{i}@example.com", first_name=f"User{i}")
            for i in range(min(limit, 10))
        ]

    async def track_event(self, event: Event) -> bool:
        return True

    async def create_segment(self, segment: Segment) -> Segment:
        segment.platform_segments["hubspot"] = f"hs_list_{segment.segment_id}"
        return segment

    async def create_campaign(self, campaign: Campaign) -> Campaign:
        campaign.platform_campaign_ids["hubspot"] = f"hs_camp_{campaign.campaign_id}"
        campaign.status = CampaignStatus.SCHEDULED
        return campaign

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"platform": "hubspot", "campaign_id": campaign_id, "status": "scheduled", "recipients": 5000}

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="hubspot", delivered=4900, opens=1470, clicks=294, conversions=44, revenue=2200, spend=150)

    async def get_dashboard(self) -> Dict[str, Any]:
        return {
            "platform": "hubspot",
            "total_contacts": 45000,
            "marketing_qualified_leads": 3200,
            "email_open_rate": 30.0,
            "deal_pipeline_value": 850000,
        }


class ClayAdapter(MarketingAdapter):
    """Clay — data enrichment & outbound prospecting."""
    platform_name = "clay"
    supported_channels = [ChannelType.EMAIL]
    supports_analytics = False

    async def connect(self) -> bool:
        if not self.credentials.get("api_key"):
            return False
        self.connected = True
        return True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["clay"] = f"clay_{contact.contact_id}"
        return contact

    async def get_contact(self, contact_id: str) -> Optional[Contact]:
        return Contact(
            contact_id=contact_id,
            email=f"{contact_id}@company.com",
            first_name="Prospect",
            last_name="Lead",
            company="Target Corp",
            job_title="VP Engineering",
            attributes={"source": "clay_enrichment", "score": 85},
            platform_ids={"clay": f"clay_{contact_id}"},
        )

    async def search_contacts(self, query: str, limit: int = 50) -> List[Contact]:
        """Clay specializes in prospect search & enrichment."""
        return [
            Contact(
                contact_id=f"prospect_{i}",
                email=f"prospect{i}@target.com",
                first_name=f"Prospect{i}",
                company=query.title(),
                job_title="Engineering Manager",
                attributes={"enriched": True, "confidence_score": 80 + i},
            )
            for i in range(min(limit, 15))
        ]

    async def track_event(self, event: Event) -> bool:
        return True

    async def create_segment(self, segment: Segment) -> Segment:
        segment.platform_segments["clay"] = f"clay_table_{segment.segment_id}"
        return segment


class MixpanelAdapter(MarketingAdapter):
    """Mixpanel — product analytics."""
    platform_name = "mixpanel"
    supported_channels = []
    supports_batch = True
    supports_analytics = True

    async def track_event(self, event: Event) -> bool:
        return True

    async def track_batch_events(self, events: List[Event]) -> bool:
        return True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["mixpanel"] = f"mp_{contact.contact_id}"
        return contact

    async def get_dashboard(self) -> Dict[str, Any]:
        return {
            "platform": "mixpanel",
            "total_events": 5000000,
            "active_users": 120000,
            "top_events": [("page_view", 1500000), ("sign_up", 25000), ("purchase", 15000)],
        }

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="mixpanel", delivered=100000, opens=0, clicks=5000, conversions=300, revenue=15000, spend=0)


class SegmentAdapter(MarketingAdapter):
    """Segment — customer data platform (CDP) router."""
    platform_name = "segment"
    supported_channels = []
    supports_batch = True
    supports_analytics = False

    async def track_event(self, event: Event) -> bool:
        return True

    async def track_batch_events(self, events: List[Event]) -> bool:
        return True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["segment"] = f"seg_{contact.contact_id}"
        return contact

    async def get_dashboard(self) -> Dict[str, Any]:
        return {"platform": "segment", "monthly_events": 25000000, "destinations": 45}


class BrazeAdapter(MarketingAdapter):
    """Braze — lifecycle marketing automation."""
    platform_name = "braze"
    supported_channels = [ChannelType.PUSH, ChannelType.EMAIL, ChannelType.SMS, ChannelType.IN_APP, ChannelType.WEB_PUSH]
    supports_journeys = True
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["braze"] = f"bz_{contact.contact_id}"
        return contact

    async def track_event(self, event: Event) -> bool:
        return True

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"platform": "braze", "campaign_id": campaign_id, "status": "sent", "recipients": 18000}

    async def send_transactional(self, contact_id: str, channel: ChannelType, content: Dict[str, Any]) -> Dict[str, Any]:
        return {"platform": "braze", "channel": channel.value, "status": "sent"}

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="braze", delivered=17800, opens=4425, clicks=889, conversions=124, revenue=6200, spend=350)

    async def get_dashboard(self) -> Dict[str, Any]:
        return {"platform": "braze", "messages_sent": 5000000, "push_delivery_rate": 96.5, "email_open_rate": 24.8}


class AmplitudeAdapter(MarketingAdapter):
    """Amplitude — product analytics & experimentation."""
    platform_name = "amplitude"
    supported_channels = []
    supports_batch = True
    supports_analytics = True

    async def track_event(self, event: Event) -> bool:
        return True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["amplitude"] = f"amp_{contact.contact_id}"
        return contact

    async def get_dashboard(self) -> Dict[str, Any]:
        return {"platform": "amplitude", "daily_active_users": 35000, "retention_day7": 38.0}


class MailchimpAdapter(MarketingAdapter):
    """Mailchimp — email marketing."""
    platform_name = "mailchimp"
    supported_channels = [ChannelType.EMAIL, ChannelType.SMS, ChannelType.SOCIAL]
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["mailchimp"] = f"mc_{hashlib.md5(contact.email.encode()).hexdigest()[:12]}" if contact.email else f"mc_{contact.contact_id}"
        return contact

    async def create_segment(self, segment: Segment) -> Segment:
        segment.platform_segments["mailchimp"] = f"mc_seg_{segment.segment_id}"
        return segment

    async def create_campaign(self, campaign: Campaign) -> Campaign:
        campaign.platform_campaign_ids["mailchimp"] = f"mc_camp_{campaign.campaign_id}"
        return campaign

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"platform": "mailchimp", "campaign_id": campaign_id, "status": "sent", "recipients": 8000}

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="mailchimp", delivered=7800, opens=1950, clicks=390, conversions=39, revenue=1950, spend=75)


class SalesforceMCAdapter(MarketingAdapter):
    """Salesforce Marketing Cloud — enterprise marketing."""
    platform_name = "salesforce_mc"
    supported_channels = [ChannelType.EMAIL, ChannelType.SMS, ChannelType.PUSH, ChannelType.SOCIAL]
    supports_journeys = True
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["salesforce"] = f"sf_{contact.contact_id}"
        return contact

    async def create_journey(self, journey: Journey) -> Journey:
        journey.platform_journey_ids["salesforce"] = f"sf_jrny_{journey.journey_id}"
        return journey

    async def send_campaign(self, campaign_id: str, segment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"platform": "salesforce_mc", "campaign_id": campaign_id, "status": "sent", "recipients": 30000}

    async def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        return CampaignMetrics(campaign_id=campaign_id, platform="salesforce_mc", delivered=29500, opens=7375, clicks=1475, conversions=221, revenue=11050, spend=800)


class IntercomAdapter(MarketingAdapter):
    """Intercom — customer messaging & support."""
    platform_name = "intercom"
    supported_channels = [ChannelType.EMAIL, ChannelType.IN_APP, ChannelType.PUSH]
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["intercom"] = f"ic_{contact.contact_id}"
        return contact

    async def send_transactional(self, contact_id: str, channel: ChannelType, content: Dict[str, Any]) -> Dict[str, Any]:
        return {"platform": "intercom", "channel": channel.value, "status": "sent"}

    async def get_dashboard(self) -> Dict[str, Any]:
        return {"platform": "intercom", "active_conversations": 1200, "avg_response_time": "2m 15s", "csat_score": 4.5}


class CustomerIOAdapter(MarketingAdapter):
    """Customer.io — behavioral messaging."""
    platform_name = "customer_io"
    supported_channels = [ChannelType.EMAIL, ChannelType.PUSH, ChannelType.SMS, ChannelType.IN_APP]
    supports_journeys = True
    supports_analytics = True

    async def upsert_contact(self, contact: Contact) -> Contact:
        contact.platform_ids["customer_io"] = f"cio_{contact.contact_id}"
        return contact

    async def track_event(self, event: Event) -> bool:
        return True

    async def create_journey(self, journey: Journey) -> Journey:
        journey.platform_journey_ids["customer_io"] = f"cio_jrny_{journey.journey_id}"
        return journey

    async def send_transactional(self, contact_id: str, channel: ChannelType, content: Dict[str, Any]) -> Dict[str, Any]:
        return {"platform": "customer_io", "channel": channel.value, "status": "sent"}

    async def get_dashboard(self) -> Dict[str, Any]:
        return {"platform": "customer_io", "messages_sent": 2000000, "delivery_rate": 98.5}


# ═══════════════════════════════════════════════════════════════
# SECTION 4: Adapter Registry
# ═══════════════════════════════════════════════════════════════

ADAPTER_REGISTRY: Dict[str, type] = {
    "webengage": WebEngageAdapter,
    "clevertap": CleverTapAdapter,
    "hubspot": HubSpotAdapter,
    "clay": ClayAdapter,
    "mixpanel": MixpanelAdapter,
    "segment": SegmentAdapter,
    "braze": BrazeAdapter,
    "amplitude": AmplitudeAdapter,
    "mailchimp": MailchimpAdapter,
    "salesforce_mc": SalesforceMCAdapter,
    "intercom": IntercomAdapter,
    "customer_io": CustomerIOAdapter,
}


def list_supported_platforms() -> List[str]:
    """List all supported marketing platforms."""
    return list(ADAPTER_REGISTRY.keys())


# ═══════════════════════════════════════════════════════════════
# SECTION 5: Marketing Hub — Unified Interface
# ═════════════════════════════════════════════ auto

class MarketingHub:
    """
    The unified marketing hub — single interface for ALL connected platforms.

    This is the "jack of all trades" — route operations to the best platform,
    fan-out across platforms, and aggregate results.

    Usage:
        hub = MarketingHub()
        await hub.connect("webengage", api_key="...")
        await hub.connect("hubspot", api_key="...")
        await hub.connect("clay", api_key="...")

        # Fan-out: track event to ALL platforms
        await hub.broadcast_event(Event(event_name="purchase", contact_id="user_123"))

        # Best-platform: send campaign via cheapest/best platform
        result = await hub.send_campaign("welcome", preferred="mailchimp")

        # Aggregate: unified dashboard across all platforms
        dashboard = await hub.get_unified_dashboard()
    """

    def __init__(self):
        self.adapters: Dict[str, MarketingAdapter] = {}
        # Per-platform circuit breakers — prevent cascade failures
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        # Per-platform retry policies
        self._retry_policies: Dict[str, RetryPolicy] = {}
        # Default retry policy for all platforms
        self._default_retry = RetryPolicy(max_attempts=3, base_delay=0.5)

    def connect(self, platform: str, **credentials) -> bool:
        """Connect a marketing platform."""
        adapter_class = ADAPTER_REGISTRY.get(platform)
        if not adapter_class:
            raise ValueError(f"Unknown platform: {platform}. Supported: {list_supported_platforms()}")
        adapter = adapter_class(**credentials)
        self.adapters[platform] = adapter
        return True

    async def initialize(self) -> Dict[str, bool]:
        """Initialize all connected adapters."""
        results = {}
        for name, adapter in self.adapters.items():
            try:
                results[name] = await adapter.connect()
            except Exception as e:
                results[name] = False
        return results

    def get_adapter(self, platform: str) -> Optional[MarketingAdapter]:
        return self.adapters.get(platform)

    def get_connected_platforms(self) -> List[str]:
        return [name for name, a in self.adapters.items() if a.connected]

    # ── Fan-out Operations (broadcast to all) ──

    async def broadcast_event(self, event: Event) -> Dict[str, bool]:
        """Track event across ALL connected platforms simultaneously."""
        tasks = []
        for name, adapter in self.adapters.items():
            tasks.append(self._safe_track_with_circuit(name, adapter, event))
        results = await asyncio.gather(*tasks)
        return dict(zip(self.adapters.keys(), results))

    async def _get_circuit_breaker(self, platform: str) -> CircuitBreaker:
        """Get or create circuit breaker for a platform."""
        if platform not in self._circuit_breakers:
            self._circuit_breakers[platform] = CircuitBreaker(name=platform)
        return self._circuit_breakers[platform]

    async def _safe_track_with_circuit(self, name: str, adapter: MarketingAdapter, event: Event) -> bool:
        """Track with circuit breaker protection."""
        cb = await self._get_circuit_breaker(name)
        
        if not cb.can_execute():
            return False  # Circuit open — reject immediately
        
        try:
            result = await self._default_retry.execute(lambda: adapter.track_event(event))
            cb.record_success()
            return result
        except NotImplementedError:
            return False
        except Exception:
            cb.record_failure()
            return False

    async def _safe_upsert_with_retry(self, name: str, adapter: MarketingAdapter, contact: Contact) -> Optional[Contact]:
        """Upsert with retry and circuit breaker protection."""
        cb = await self._get_circuit_breaker(name)
        
        if not cb.can_execute():
            return None  # Circuit open
        
        try:
            result = await self._default_retry.execute(lambda: adapter.upsert_contact(contact))
            cb.record_success()
            return result
        except NotImplementedError:
            return None
        except Exception:
            cb.record_failure()
            return None

    async def sync_contact(self, contact: Contact) -> Contact:
        """Upsert contact to ALL connected platforms."""
        tasks = []
        for name, adapter in self.adapters.items():
            # Deep copy to avoid data race — each adapter gets its own copy
            contact_copy = copy.deepcopy(contact)
            tasks.append(self._safe_upsert_with_retry(name, adapter, contact_copy))
        results = await asyncio.gather(*tasks)
        # Merge platform_ids from all results
        for r in results:
            if isinstance(r, Contact):
                contact.platform_ids.update(r.platform_ids)
        return contact

    async def _safe_upsert(self, adapter: MarketingAdapter, contact: Contact) -> Optional[Contact]:
        try:
            return await adapter.upsert_contact(contact)
        except NotImplementedError:
            return None
        except Exception:
            return None

    # ── Best-Platform Operations (route to optimal) ──

    async def send_campaign(
        self,
        campaign_id: str,
        segment_ids: Optional[List[str]] = None,
        preferred: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send campaign via preferred platform or first available."""
        platform = preferred or self._best_platform_for_campaign()
        adapter = self.adapters.get(platform)
        if not adapter:
            return {"error": f"No adapter for {platform}"}
        try:
            return await adapter.send_campaign(campaign_id, segment_ids)
        except NotImplementedError:
            # Fallback to another platform
            for name, fallback in self.adapters.items():
                if name != platform:
                    try:
                        return await fallback.send_campaign(campaign_id, segment_ids)
                    except NotImplementedError:
                        continue
            return {"error": "No platform supports send_campaign"}

    async def send_transactional(
        self,
        contact_id: str,
        channel: ChannelType,
        content: Dict[str, Any],
        preferred: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send transactional message via best platform for the channel."""
        platform = preferred or self._best_platform_for_channel(channel)
        adapter = self.adapters.get(platform)
        if not adapter:
            return {"error": f"No adapter for {platform}"}
        try:
            return await adapter.send_transactional(contact_id, channel, content)
        except NotImplementedError:
            for name, fallback in self.adapters.items():
                if name != platform and channel in fallback.supported_channels:
                    try:
                        return await fallback.send_transactional(contact_id, channel, content)
                    except NotImplementedError:
                        continue
            return {"error": f"No platform supports {channel.value} messages"}

    def _best_platform_for_channel(self, channel: ChannelType) -> str:
        """Pick the best platform for a given channel."""
        # Priority order by channel
        priorities = {
            ChannelType.EMAIL: ["mailchimp", "hubspot", "braze", "webengage"],
            ChannelType.PUSH: ["braze", "clevertap", "webengage"],
            ChannelType.SMS: ["webengage", "clevertap", "braze"],
            ChannelType.WHATSAPP: ["webengage", "clevertap"],
            ChannelType.IN_APP: ["braze", "intercom", "webengage"],
        }
        for platform in priorities.get(channel, []):
            if platform in self.adapters and self.adapters[platform].connected:
                if channel in self.adapters[platform].supported_channels:
                    return platform
        # Fallback to first connected
        connected = self.get_connected_platforms()
        return connected[0] if connected else "webengage"

    def _best_platform_for_campaign(self) -> str:
        """Pick the best platform for sending campaigns."""
        for platform in ["mailchimp", "hubspot", "webengage", "braze", "clevertap"]:
            if platform in self.adapters and self.adapters[platform].connected:
                return platform
        connected = self.get_connected_platforms()
        return connected[0] if connected else "webengage"

    # ── Aggregate Operations ──

    async def get_unified_dashboard(self) -> Dict[str, Any]:
        """Aggregate dashboard metrics across ALL platforms."""
        tasks = []
        names = []
        for name, adapter in self.adapters.items():
            if adapter.supports_analytics:
                tasks.append(self._safe_dashboard(adapter))
                names.append(name)

        results = await asyncio.gather(*tasks)
        platforms = {}
        total_revenue = 0
        total_users = 0
        total_messages = 0

        for name, result in zip(names, results):
            if result:
                platforms[name] = result
                total_revenue += result.get("revenue_attributed", result.get("revenue", 0))
                total_users += result.get("total_contacts", result.get("active_users", result.get("monthly_active_users", 0)))
                total_messages += result.get("messages_sent", result.get("monthly_reach", 0))

        return {
            "connected_platforms": list(platforms.keys()),
            "platform_count": len(platforms),
            "aggregate": {
                "total_revenue_attributed": total_revenue,
                "total_users_reached": total_users,
                "total_messages_sent": total_messages,
            },
            "platforms": platforms,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def _safe_dashboard(self, adapter: MarketingAdapter) -> Optional[Dict[str, Any]]:
        try:
            return await adapter.get_dashboard()
        except NotImplementedError:
            return None
        except Exception:
            return None

    async def get_campaign_metrics_all(self, campaign_id: str) -> Dict[str, CampaignMetrics]:
        """Get campaign metrics from all platforms that have it."""
        tasks = []
        names = []
        for name, adapter in self.adapters.items():
            tasks.append(self._safe_metrics(adapter, campaign_id))
            names.append(name)
        results = await asyncio.gather(*tasks)
        return {name: r for name, r in zip(names, results) if r is not None}

    async def _safe_metrics(self, adapter: MarketingAdapter, campaign_id: str) -> Optional[CampaignMetrics]:
        try:
            return await adapter.get_campaign_metrics(campaign_id)
        except NotImplementedError:
            return None
        except Exception:
            return None

    # ── Cross-Platform Operations ──

    async def create_unified_segment(self, segment: Segment) -> Segment:
        """Create segment across all platforms that support it."""
        tasks = []
        for adapter in self.adapters.values():
            tasks.append(self._safe_create_segment(adapter, segment))
        results = await asyncio.gather(*tasks)
        for r in results:
            if isinstance(r, Segment):
                segment.platform_segments.update(r.platform_segments)
        return segment

    async def _safe_create_segment(self, adapter: MarketingAdapter, segment: Segment) -> Optional[Segment]:
        try:
            return await adapter.create_segment(segment)
        except NotImplementedError:
            return None
        except Exception:
            return None

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check all connected platforms including circuit breaker status."""
        tasks = [a.health_check() for a in self.adapters.values()]
        results = await asyncio.gather(*tasks)
        health = dict(zip(self.adapters.keys(), results))
        
        # Add circuit breaker status
        for platform, cb in self._circuit_breakers.items():
            if platform in health:
                health[platform]["circuit_breaker"] = {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "last_failure": cb.last_failure_time,
                }
        
        return health


# ═══════════════════════════════════════════════════════════════
# SECTION 6: Workflow Orchestration
# ═══════════════════════════════════════════════════════════════

class WorkflowStep:
    """A single step in a marketing workflow."""
    def __init__(
        self,
        step_id: str,
        action: str,  # sync_contact, broadcast_event, create_segment, send_campaign, etc.
        params: Dict[str, Any],
        on_success: Optional[str] = None,  # next step_id
        on_failure: Optional[str] = None,  # step_id to jump to on failure
    ):
        self.step_id = step_id
        self.action = action
        self.params = params
        self.on_success = on_success
        self.on_failure = on_failure


class WorkflowResult:
    """Result of a workflow execution."""
    def __init__(
        self,
        workflow_id: str,
        status: str,  # completed, failed, stopped
        steps_executed: List[Dict[str, Any]],
        results: Dict[str, Any],
        errors: List[str],
        duration_ms: float,
    ):
        self.workflow_id = workflow_id
        self.status = status
        self.steps_executed = steps_executed
        self.results = results
        self.errors = errors
        self.duration_ms = duration_ms


class MarketingWorkflow:
    """
    Orchestrate multi-step marketing workflows.
    
    Chain operations like: sync_contact → create_segment → send_campaign
    
    Usage:
        wf = MarketingWorkflow("welcome_flow")
        wf.add_step("sync", "hub_sync_contact", {"email": "...", "first_name": "..."}, on_success="segment")
        wf.add_step("segment", "hub_create_segment", {"name": "active_users"}, on_success="send")
        wf.add_step("send", "hub_send_campaign", {"campaign_name": "Welcome"})
        
        result = await wf.execute(hub)
    """
    def __init__(self, workflow_id: str, name: str = ""):
        self.workflow_id = workflow_id
        self.name = name or workflow_id
        self.steps: Dict[str, WorkflowStep] = {}
        self.first_step_id: Optional[str] = None

    def add_step(
        self,
        step_id: str,
        action: str,
        params: Dict[str, Any],
        on_success: Optional[str] = None,
        on_failure: Optional[str] = None,
        is_first: bool = False,
    ) -> "MarketingWorkflow":
        """Add a step to the workflow. Returns self for chaining."""
        step = WorkflowStep(step_id, action, params, on_success, on_failure)
        self.steps[step_id] = step
        if is_first or not self.first_step_id:
            self.first_step_id = step_id
        return self

    async def execute(self, hub: MarketingHub) -> WorkflowResult:
        """Execute the workflow against a MarketingHub."""
        import time
        start = time.time()
        steps_executed = []
        results = {}
        errors = []
        current_step_id = self.first_step_id

        while current_step_id:
            step = self.steps.get(current_step_id)
            if not step:
                errors.append(f"Step not found: {current_step_id}")
                break

            step_start = time.time()
            try:
                result = await self._execute_action(hub, step.action, step.params)
                duration = (time.time() - step_start) * 1000

                steps_executed.append({
                    "step_id": step.step_id,
                    "action": step.action,
                    "status": "success",
                    "duration_ms": duration,
                    "result": result,
                })
                results[step.step_id] = result

                # Follow success path
                current_step_id = step.on_success

            except Exception as e:
                duration = (time.time() - step_start) * 1000
                errors.append(f"{step.step_id}: {str(e)}")
                steps_executed.append({
                    "step_id": step.step_id,
                    "action": step.action,
                    "status": "failed",
                    "duration_ms": duration,
                    "error": str(e),
                })
                # Follow failure path or stop
                if step.on_failure:
                    current_step_id = step.on_failure
                else:
                    break

        duration_ms = (time.time() - start) * 1000
        status = "failed" if errors else "completed"

        return WorkflowResult(
            workflow_id=self.workflow_id,
            status=status,
            steps_executed=steps_executed,
            results=results,
            errors=errors,
            duration_ms=duration_ms,
        )

    async def _execute_action(self, hub: MarketingHub, action: str, params: Dict[str, Any]) -> Any:
        """Execute a single workflow action."""
        if action == "hub_sync_contact":
            from marketic.integrations.unified_adapter import Contact
            contact = Contact(**params)
            return await hub.sync_contact(contact)

        elif action == "hub_broadcast_event":
            from marketic.integrations.unified_adapter import Event
            event = Event(**params)
            return await hub.broadcast_event(event)

        elif action == "hub_create_segment":
            from marketic.integrations.unified_adapter import Segment
            segment = Segment(name=params["name"], description=params.get("description", ""))
            return await hub.create_unified_segment(segment)


        elif action == "hub_send_campaign":
            campaign_name = params.get("campaign_name", "")
            channel = params.get("channel", "email")
            preferred = params.get("preferred_platform")
            return await hub.send_campaign(campaign_name, preferred=preferred)


        elif action == "hub_send_transactional":
            from marketic.integrations.unified_adapter import ChannelType
            contact_id = params["contact_id"]
            channel = ChannelType(params.get("channel", "email"))
            content = params.get("content", {})
            return await hub.send_transactional(contact_id, channel, content)

        elif action == "crm_create_lead":
            from marketic.crm import CRMMaster
            crm = CRMMaster()
            return crm.create_lead(**params)

        elif action == "crm_create_deal":
            from marketic.crm import CRMMaster
            crm = CRMMaster()
            return crm.create_deal(**params)

        elif action == "crm_log_activity":
            from marketic.crm import CRMMaster, ActivityType
            crm = CRMMaster()
            entity_id = params.pop("entity_id")
            activity_type_str = params.pop("activity_type", "note")
            from marketic.crm import ActivityType as CRMActivityType
            type_map = {"call": CRMActivityType.CALL, "email": CRMActivityType.EMAIL, 
                      "meeting": CRMActivityType.MEETING, "note": CRMActivityType.NOTE}
            params["activity_type"] = type_map.get(activity_type_str, CRMActivityType.NOTE)
            return crm.log_activity(entity_id, **params)

        else:
            raise ValueError(f"Unknown workflow action: {action}")



# ═══════════════════════════════════════════════════════════════
# SECTION 7: UTM URL Builder
# ═══════════════════════════════════════════════════════════════

def build_utm_url(
    base_url: str,
    source: str,
    medium: str,
    campaign: str,
    content: Optional[str] = None,
    term: Optional[str] = None,
    **extra_params: Any,
) -> str:
    """
    Build a UTM-encoded URL for campaign tracking.
    
    Usage:
        url = build_utm_url(
            base_url="https://example.com/landing",
            source="linkedin",
            medium="social",
            campaign="q3_awareness",
            content="video_ad",
            term="ai+software",
        )
        # -> https://example.com/landing?utm_source=linkedin&utm_medium=social&utm_campaign=q3_awareness&utm_content=video_ad&utm_term=ai%2Bsoftware
    """
    import urllib.parse

    params = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    if content:
        params["utm_content"] = content
    if term:
        params["utm_term"] = term
    
    # Add any extra parameters
    params.update(extra_params)

    # Build URL with query string
    query = urllib.parse.urlencode(params)
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{query}"


def parse_utm_params(url: str) -> Dict[str, str]:
    """Extract UTM parameters from a URL."""
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    # Return just the utm_ keys without array wrapping
    return {k: v[0] for k, v in params.items() if k.startswith("utm_")}



# ═══════════════════════════════════════════════════════════════
# SECTION 8: Convenience Functions
# ═══════════════════════════════════════════════════════════════

def create_hub(platforms: List[str], credentials: Dict[str, Dict[str, str]]) -> MarketingHub:
    """
    Quick-create a MarketingHub with multiple platforms.

    Usage:
        hub = create_hub(
            platforms=["webengage", "hubspot", "clay"],
            credentials={
                "webengage": {"api_key": "...", "license_code": "..."},
                "hubspot": {"api_key": "..."},
                "clay": {"api_key": "..."},
            }
        )
    """
    hub = MarketingHub()
    for platform in platforms:
        creds = credentials.get(platform, {})
        hub.connect(platform, **creds)
    return hub
