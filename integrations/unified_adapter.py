"""
Unified Marketing Hub — Connect all marketing platforms via a single interface.
"""

import os
import httpx
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "marketic_memory.db")


def get_connection():
    db_path = os.path.abspath(DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


class ChannelType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    FAILED = "failed"


@dataclass
class Contact:
    contact_id: str
    email: str
    phone: str
    first_name: str
    last_name: str
    company: str
    lifecycle_stage: str
    attributes: Dict[str, Any]
    tags: List[str]
    platform_ids: Dict[str, str] = field(default_factory=dict)  # platform -> external_id


@dataclass
class Campaign:
    campaign_id: str
    name: str
    channel: ChannelType
    subject: str
    content_html: str
    status: CampaignStatus = CampaignStatus.DRAFT
    scheduled_at: str = ""
    sent_at: str = ""


@dataclass
class Event:
    event_name: str
    contact_id: str
    properties: Dict[str, Any]
    revenue: float


@dataclass
class Segment:
    segment_id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    platform_segments: Dict[str, str] = field(default_factory=dict)  # platform -> segment_id


# Platform adapter registry
ADAPTER_REGISTRY = {}


class BaseAdapter:
    """Base class for marketing platform adapters."""
    supported_channels: List[ChannelType] = []
    supports_journeys: bool = False
    supports_analytics: bool = True

    def __init__(self, api_key: str = "", **credentials):
        self.api_key = api_key
        self.credentials = credentials
        self.connected = False

    def connect(self, **credentials) -> bool:
        """Connect to the platform."""
        raise NotImplementedError

    def disconnect(self):
        """Disconnect from the platform."""
        self.connected = False

    def health_check(self) -> Dict[str, Any]:
        """Check platform health."""
        return {"status": "unknown", "connected": self.connected}

    def sync_contact(self, contact: Contact) -> Contact:
        """Sync contact to platform."""
        raise NotImplementedError

    def send_campaign(self, campaign: Campaign, segment_id: str = "") -> Dict[str, Any]:
        """Send campaign via platform."""
        raise NotImplementedError

    def send_transactional(self, contact_id: str, channel: ChannelType, content: Dict) -> Dict[str, Any]:
        """Send transactional message."""
        raise NotImplementedError

    def get_analytics(self) -> Dict[str, Any]:
        """Get platform analytics."""
        return {}


class WebEngageAdapter(BaseAdapter):
    supported_channels = [ChannelType.EMAIL, ChannelType.SMS, ChannelType.PUSH, ChannelType.WHATSAPP]
    supports_journeys = True

    def connect(self, **credentials):
        api_key = credentials.get("api_key") or self.api_key
        license_code = credentials.get("license_code", "")
        self.api_key = api_key
        self.license_code = license_code
        self.connected = bool(api_key and license_code)
        return self.connected

    def health_check(self) -> Dict[str, Any]:
        return {
            "platform": "webengage",
            "status": "connected" if self.connected else "disconnected",
            "connected": self.connected,
            "capabilities": self.supported_channels,
        }

    def sync_contact(self, contact: Contact) -> Contact:
        if not self.connected:
            return contact

        try:
            response = httpx.post(
                f"https://api.webengage.com/v1/accounts/{self.license_code}/users",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "userId": contact.contact_id,
                    "email": contact.email,
                    "phone": contact.phone,
                    "firstName": contact.first_name,
                    "lastName": contact.last_name,
                    "company": contact.company,
                    "attributes": contact.attributes,
                },
                timeout=30.0
            )

            if response.status_code in [200, 201]:
                contact.platform_ids["webengage"] = contact.contact_id
        except Exception as e:
            print(f"WebEngage sync error: {e}")

        return contact

    def send_campaign(self, campaign: Campaign, segment_id: str = "") -> Dict[str, Any]:
        if not self.connected:
            return {"success": False, "error": "Not connected"}

        return {"success": True, "campaign_id": campaign.campaign_id, "platform": "webengage"}


class HubSpotAdapter(BaseAdapter):
    supported_channels = [ChannelType.EMAIL, ChannelType.PUSH]
    supports_journeys = True

    def connect(self, **credentials):
        api_key = credentials.get("api_key") or self.api_key
        self.api_key = api_key
        self.connected = bool(api_key)
        return self.connected

    def health_check(self) -> Dict[str, Any]:
        return {
            "platform": "hubspot",
            "status": "connected" if self.connected else "disconnected",
            "connected": self.connected,
            "capabilities": self.supported_channels,
        }

    def sync_contact(self, contact: Contact) -> Contact:
        if not self.connected:
            return contact

        try:
            response = httpx.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "properties": {
                        "email": contact.email,
                        "phone": contact.phone,
                        "firstname": contact.first_name,
                        "lastname": contact.last_name,
                        "company": contact.company,
                        "lifecyclestage": contact.lifecycle_stage,
                    }
                },
                timeout=30.0
            )

            if response.status_code in [200, 201]:
                data = response.json()
                contact.platform_ids["hubspot"] = data.get("id", contact.contact_id)
        except Exception as e:
            print(f"HubSpot sync error: {e}")

        return contact

    def send_campaign(self, campaign: Campaign, segment_id: str = "") -> Dict[str, Any]:
        if not self.connected:
            return {"success": False, "error": "Not connected"}

        return {"success": True, "campaign_id": campaign.campaign_id, "platform": "hubspot"}


class ClayAdapter(BaseAdapter):
    """Clay data enrichment adapter."""

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://api.clay.com"

    def connect(self, **credentials):
        api_key = credentials.get("api_key") or self.api_key
        self.api_key = api_key
        self.connected = bool(api_key)
        return self.connected

    async def search_contacts(self, query: str, limit: int = 10) -> List[Contact]:
        """Search and enrich contacts via Clay."""
        if not self.connected:
            return []

        try:
            # Clay GraphQL API
            response = httpx.post(
                f"{self.base_url}/v1/graphql",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "query": query,
                    "limit": limit,
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                contacts = []
                for item in data.get("results", []):
                    contacts.append(Contact(
                        contact_id=item.get("id", ""),
                        email=item.get("email", ""),
                        phone=item.get("phone", ""),
                        first_name=item.get("first_name", ""),
                        last_name=item.get("last_name", ""),
                        company=item.get("company", ""),
                        lifecycle_stage="lead",
                        attributes=item,
                        tags=[],
                    ))
                return contacts
        except Exception as e:
            print(f"Clay search error: {e}")

        return []

    def health_check(self) -> Dict[str, Any]:
        return {
            "platform": "clay",
            "status": "connected" if self.connected else "disconnected",
            "connected": self.connected,
        }


class SerperProspectAdapter(BaseAdapter):
    """
    Vault-sourced cost arbitrage (@fin465): Apollo = $100/5K lookups,
    Serper = $100/100K searches — same output, 92-94% cheaper.
    Used as the FIRST enrichment hop; only escalate to Clay for the
    residual contacts that search can't resolve.
    """

    def connect(self, **credentials):
        self.api_key = credentials.get("api_key") or os.environ.get("SERPER_API_KEY", "")
        self.connected = bool(self.api_key)
        return self.connected

    async def search_contacts(self, query: str, limit: int = 10) -> List[Contact]:
        """Find prospects via Google search (Serper) — names/roles/companies."""
        if not self.connected:
            return []
        try:
            resp = httpx.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": f"{query} site:linkedin.com/in", "num": min(limit, 20)},
                timeout=30.0,
            )
            if resp.status_code == 200:
                contacts = []
                for r in resp.json().get("organic", [])[:limit]:
                    title = r.get("title", "")
                    # "Name - Title at Company | LinkedIn" pattern
                    name_part, _, rest = title.partition(" - ")
                    company = r.get("title", "").split(" at ")[-1].split("|")[0].strip()
                    contacts.append(Contact(
                        contact_id=f"serper_{abs(hash(r.get('link','')))%10**10}",
                        email="",  # enrichment of email happens downstream (Clay/Apollo)
                        phone="",
                        first_name=name_part.split()[0] if name_part else "",
                        last_name=" ".join(name_part.split()[1:]) if name_part else "",
                        company=company,
                        job_title=rest.split("|")[0].replace(f"at {company}", "").strip(),
                        lifecycle_stage="prospect",
                        attributes={"source": "serper", "linkedin_url": r.get("link", "")},
                        tags=["prospecting"],
                    ))
                return contacts
        except Exception as e:
            print(f"Serper search error: {e}")
        return []

    def health_check(self) -> Dict[str, Any]:
        return {"platform": "serper", "status": "connected" if self.connected else "disconnected",
                "connected": self.connected,
                "note": "92-94% cheaper than Apollo per lookup; use before Clay"}


class MarketingHub:
    """Unified marketing hub that aggregates multiple platforms."""

class MarketingHub:
    """Unified marketing hub that aggregates multiple platforms."""

    def __init__(self):
        self.adapters: Dict[str, BaseAdapter] = {}
        self._init_adapters()

    def _init_adapters(self):
        """Initialize all available adapters."""
        self.adapters["webengage"] = WebEngageAdapter()
        self.adapters["hubspot"] = HubSpotAdapter()
        self.adapters["clay"] = ClayAdapter()
        self.adapters["serper"] = SerperProspectAdapter()

    def connect(self, platform: str, **credentials) -> bool:
        """Connect to a specific platform."""
        adapter = self.adapters.get(platform)
        if not adapter:
            return False
        return adapter.connect(**credentials)

    def get_connected_platforms(self) -> List[str]:
        """Get list of connected platforms."""
        return [name for name, adapter in self.adapters.items() if adapter.connected]

    async def initialize(self):
        """Initialize connections (async)."""
        pass

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all platforms."""
        results = {}
        for name, adapter in self.adapters.items():
            results[name] = adapter.health_check()
        return results

    async def sync_contact(self, contact: Contact) -> Contact:
        """Sync contact to ALL connected platforms."""
        synced_contact = contact

        for name, adapter in self.adapters.items():
            if adapter.connected and hasattr(adapter, 'sync_contact'):
                try:
                    synced_contact = adapter.sync_contact(synced_contact)
                except Exception as e:
                    print(f"Sync error for {name}: {e}")

        return synced_contact

    async def broadcast_event(self, event: Event) -> Dict[str, bool]:
        """Broadcast event to all connected platforms."""
        results = {}

        for name, adapter in self.adapters.items():
            if adapter.connected and hasattr(adapter, 'track_event'):
                try:
                    result = await adapter.track_event(event)
                    results[name] = result
                except Exception as e:
                    print(f"Event broadcast error for {name}: {e}")
                    results[name] = False

        return results

    async def send_campaign(self, campaign: Campaign, preferred: str = "") -> Dict[str, Any]:
        """Send campaign via best available platform."""
        # If preferred platform specified and connected, use it
        if preferred and preferred in self.adapters:
            adapter = self.adapters[preferred]
            if adapter.connected:
                return adapter.send_campaign(campaign)

        # Otherwise, use first connected platform
        for name, adapter in self.adapters.items():
            if adapter.connected:
                return adapter.send_campaign(campaign)

        return {"success": False, "error": "No connected platforms"}

    async def send_transactional(self, contact_id: str, channel: ChannelType, content: Dict) -> Dict[str, Any]:
        """Send transactional message."""
        for name, adapter in self.adapters.items():
            if adapter.connected and channel in adapter.supported_channels:
                return adapter.send_transactional(contact_id, channel, content)

        return {"success": False, "error": "No platform supports this channel"}

    async def create_unified_segment(self, segment: Segment) -> Segment:
        """Create segment across all platforms."""
        created_ids = {}

        for name, adapter in self.adapters.items():
            if adapter.connected and hasattr(adapter, 'create_segment'):
                try:
                    segment_id = adapter.create_segment(segment)
                    created_ids[name] = segment_id
                except Exception as e:
                    print(f"Segment creation error for {name}: {e}")

        segment.platform_segments = created_ids
        return segment

    async def get_unified_dashboard(self) -> Dict[str, Any]:
        """Get unified analytics across platforms."""
        dashboard = {
            "email": {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0},
            "sms": {"sent": 0, "delivered": 0, "clicked": 0},
            "push": {"sent": 0, "delivered": 0, "opened": 0},
            "total_contacts": 0,
        }

        # Aggregate from connected platforms
        for name, adapter in self.adapters.items():
            if adapter.connected and hasattr(adapter, 'get_analytics'):
                try:
                    analytics = adapter.get_analytics()
                    for key in dashboard:
                        if key in analytics:
                            if isinstance(analytics[key], dict):
                                for subkey in dashboard[key]:
                                    dashboard[key][subkey] += analytics[key].get(subkey, 0)
                            else:
                                dashboard[key] += analytics.get(key, 0)
                except Exception:
                    pass

        return dashboard


def list_supported_platforms() -> List[str]:
    """List all supported marketing platforms."""
    return [
        "webengage",
        "hubspot",
        "clevertap",
        "mixpanel",
        "braze",
        "mailchimp",
        "clay",
        "intercom",
    ]


def build_utm_url(base_url: str, source: str, medium: str, campaign: str,
                 content: str = "", term: str = "") -> str:
    """Build a UTM-tagged URL."""
    params = [
        ("utm_source", source),
        ("utm_medium", medium),
        ("utm_campaign", campaign),
    ]
    if content:
        params.append(("utm_content", content))
    if term:
        params.append(("utm_term", term))

    param_str = "&".join(f"{k}={v}" for k, v in params)
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{param_str}"


def parse_utm_params(url: str) -> Dict[str, str]:
    """Parse UTM parameters from URL."""
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        utm_params = {}
        for key in ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]:
            if key in qs:
                utm_params[key.replace("utm_", "")] = qs[key][0]

        return utm_params
    except Exception:
        return {}


class MarketingWorkflow:
    """Multi-step marketing workflow engine."""

    def __init__(self, workflow_id: str, name: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.steps: List[Dict[str, Any]] = []
        self.step_map: Dict[str, Dict[str, Any]] = {}

    def add_step(self, step_id: str, action: str, params: Dict[str, Any],
                 on_success: str = "", on_failure: str = "", is_first: bool = False):
        """Add a step to the workflow."""
        step = {
            "step_id": step_id,
            "action": action,
            "params": params,
            "on_success": on_success,
            "on_failure": on_failure,
            "is_first": is_first,
        }
        self.steps.append(step)
        self.step_map[step_id] = step

    async def execute(self, hub: MarketingHub) -> Dict[str, Any]:
        """Execute the workflow."""
        results = {}

        # Find first step
        first_steps = [s for s in self.steps if s.get("is_first")]
        if not first_steps:
            first_steps = [self.steps[0]] if self.steps else []

        current_step_id = first_steps[0]["step_id"] if first_steps else None

        while current_step_id:
            step = self.step_map.get(current_step_id)
            if not step:
                break

            action = step["action"]
            params = step["params"]

            try:
                # Execute action
                if action == "sync_contact":
                    contact = await hub.sync_contact(Contact(**params))
                    results[current_step_id] = {"success": True, "result": contact}
                    current_step_id = step["on_success"]

                elif action == "create_segment":
                    segment = await hub.create_unified_segment(Segment(**params))
                    results[current_step_id] = {"success": True, "result": segment}
                    current_step_id = step["on_success"]

                elif action == "send_campaign":
                    campaign = Campaign(**params)
                    result = await hub.send_campaign(campaign)
                    results[current_step_id] = {"success": True, "result": result}
                    current_step_id = step["on_success"]

                elif action == "broadcast_event":
                    event = Event(**params)
                    result = await hub.broadcast_event(event)
                    results[current_step_id] = {"success": True, "result": result}
                    current_step_id = step["on_success"]

                else:
                    results[current_step_id] = {"success": False, "error": f"Unknown action: {action}"}
                    current_step_id = step["on_failure"]

            except Exception as e:
                results[current_step_id] = {"success": False, "error": str(e)}
                current_step_id = step["on_failure"]

        return {
            "workflow_id": self.workflow_id,
            "completed": True,
            "step_results": results,
        }
