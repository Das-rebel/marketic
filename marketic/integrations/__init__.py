"""
Marketic Integrations

Connect to marketing platforms via Composio MCP, Apify, and native APIs.

Based on vault research:
- Composio: HubSpot, Salesforce, Meta Ads, LinkedIn, Slack, Notion
- Apify: Web scraping for competitor intelligence
- Firecrawl: AI-powered web scraping
- n8n: Workflow automation
- WebEngage: Push, email, SMS, WhatsApp, in-app messaging
- CleverTap: User engagement & retention
- HubSpot: CRM + marketing automation
- Clay: Data enrichment & outbound prospecting
- Mixpanel: Product analytics
- Segment: Customer data platform (CDP)
- Braze: Multi-channel lifecycle marketing
- Amplitude: Behavioral analytics
- Mailchimp: Email marketing
- Salesforce MC: Enterprise marketing cloud
- Intercom: Customer messaging
- Customer.io: Behavioral messaging
"""

from .apify_integration import ApifyIntegration
from .composio_integration import ComposioIntegration
from .marketing_platforms import (
    BaseMarketingIntegration,
    WebEngageIntegration,
    CleverTapIntegration,
    MixpanelIntegration,
    SegmentIntegration,
    BrazeIntegration,
    AmplitudeIntegration,
    get_marketing_platform,
    UserProfile,
    CampaignMetrics,
    MarketingPlatform,
    EventType,
)
from .unified_adapter import (
    MarketingHub,
    MarketingAdapter,
    Contact,
    ContactStatus,
    Event,
    Segment,
    Campaign,
    CampaignStatus,
    Journey,
    JourneyStep,
    JourneyStatus,
    ChannelType,
    CampaignMetrics as UnifiedCampaignMetrics,
    create_hub,
    list_supported_platforms,
    ADAPTER_REGISTRY,
    # Platform adapters
    WebEngageAdapter,
    CleverTapAdapter,
    HubSpotAdapter,
    ClayAdapter,
    MixpanelAdapter,
    SegmentAdapter,
    BrazeAdapter,
    AmplitudeAdapter,
    MailchimpAdapter,
    SalesforceMCAdapter,
    IntercomAdapter,
    CustomerIOAdapter,
)

__all__ = [
    # Legacy
    "ApifyIntegration",
    "ComposioIntegration",
    # Platform integrations
    "BaseMarketingIntegration",
    "WebEngageIntegration",
    "CleverTapIntegration",
    "MixpanelIntegration",
    "SegmentIntegration",
    "BrazeIntegration",
    "AmplitudeIntegration",
    "get_marketing_platform",
    # Data models
    "UserProfile",
    "CampaignMetrics",
    "MarketingPlatform",
    "EventType",
    # Unified adapter
    "MarketingHub",
    "MarketingAdapter",
    "Contact",
    "ContactStatus",
    "Event",
    "Segment",
    "Campaign",
    "CampaignStatus",
    "Journey",
    "JourneyStep",
    "JourneyStatus",
    "ChannelType",
    "UnifiedCampaignMetrics",
    "create_hub",
    "list_supported_platforms",
    "ADAPTER_REGISTRY",
    # Adapters
    "WebEngageAdapter",
    "CleverTapAdapter",
    "HubSpotAdapter",
    "ClayAdapter",
    "MixpanelAdapter",
    "SegmentAdapter",
    "BrazeAdapter",
    "AmplitudeAdapter",
    "MailchimpAdapter",
    "SalesforceMCAdapter",
    "IntercomAdapter",
    "CustomerIOAdapter",
]
