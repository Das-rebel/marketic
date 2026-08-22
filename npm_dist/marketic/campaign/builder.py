"""
Campaign Builder

Builds marketing campaigns with proper structure across channels.
"""

import uuid
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime, timedelta

from ..foundation.llm_router import generate_parallel, TaskType
from ..foundation.memory import save_campaign, get_campaign


class Channel(Enum):
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"
    GOOGLE_PMAX = "google_pmax"
    META_FEED = "meta_feed"
    META_STORY = "meta_story"
    META_RETARGETING = "meta_retargeting"
    LINKEDIN_SPONSORED = "linkedin_sponsored"
    LINKEDIN_MESSAGE = "linkedin_message"
    TWITTER_PROMOTED = "twitter_promoted"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    EMAIL = "email_marketing"
    SEO_ORGANIC = "seo_organic"


class CampaignObjective(Enum):
    AWARENESS = "awareness"
    TRAFFIC = "traffic"
    LEAD_GENERATION = "lead_generation"
    APP_INSTALLS = "app_installs"
    PURCHASES = "purchases"
    BRAND_LOYALTY = "brand_loyalty"


class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    OPTIMIZING = "optimizing"


@dataclass
class AdGroup:
    """An ad group within a campaign."""
    ad_group_id: str
    name: str
    channel: Channel
    keywords: List[str] = field(default_factory=list)
    targeting: Dict = field(default_factory=dict)
    budget_daily: float = 0
    bid_strategy: str = "auto"
    status: str = "active"


@dataclass
class Campaign:
    """A marketing campaign."""
    campaign_id: str
    name: str
    objective: CampaignObjective
    channels: List[Channel]
    total_budget: float
    daily_budget: float
    start_date: str
    end_date: str
    status: CampaignStatus
    ad_groups: List[AdGroup] = field(default_factory=list)
    creative_strategy: str = ""
    targeting_strategy: str = ""
    success_metrics: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=datetime.now().isoformat)


class CampaignBuilder:
    """
    Builds structured marketing campaigns across multiple channels.
    
    Usage:
        builder = CampaignBuilder()
        campaign = await builder.build(
            name="Q3 Product Launch",
            objective="lead_generation",
            channels=["google_search", "meta_feed"],
            total_budget=50000,
        )
    """
    
    def __init__(self):
        self.memory = None
    
    async def build(
        self,
        name: str,
        objective: str,
        channels: List[str],
        total_budget: float,
        target_audience: str = "",
        competitors: List[str] = None,
        timeline_weeks: int = 12,
        existing_channels_data: Dict = None,
    ) -> Campaign:
        """Build a complete campaign structure."""
        
        # Convert string channels to enums
        channel_enums = []
        for ch in channels:
            try:
                channel_enums.append(Channel(ch))
            except ValueError:
                print(f"Unknown channel: {ch}")
        
        # Generate campaign structure using AI
        structure_prompt = f"""Create a detailed campaign structure for:

Campaign: {name}
Objective: {objective}
Channels: {', '.join(channels)}
Total Budget: ${total_budget}
Timeline: {timeline_weeks} weeks
{f"Target Audience: {target_audience}" if target_audience else ""}
{f"Competitors: {', '.join(competitors)}" if competitors else ""}

For each channel, provide:
1. Recommended budget allocation (% and $)
2. Ad group structure with keywords/targeting
3. Bidding strategy
4. Key success metrics

Return as JSON with channel details."""

        # Use AI to generate optimized structure
        responses = await generate_parallel(
            prompt=structure_prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.6,
            max_tokens=2048,
        )
        
        # Create campaign
        campaign_id = str(uuid.uuid4())[:8]
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=timeline_weeks)
        
        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            objective=CampaignObjective(objective) if isinstance(objective, str) else objective,
            channels=channel_enums,
            total_budget=total_budget,
            daily_budget=total_budget / (timeline_weeks * 7),
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            status=CampaignStatus.DRAFT,
            ad_groups=[],
        )
        
        # Parse AI response for channel details
        if responses:
            # In production, parse actual response
            pass
        
        # Create default ad groups for each channel
        for channel in channel_enums:
            ad_group = AdGroup(
                ad_group_id=str(uuid.uuid4())[:8],
                name=f"{name} - {channel.value}",
                channel=channel,
                budget_daily=campaign.daily_budget / len(channel_enums),
            )
            campaign.ad_groups.append(ad_group)
        
        # Save to memory
        self._save_campaign(campaign)
        
        return campaign
    
    def _save_campaign(self, campaign: Campaign):
        """Save campaign to memory."""
        campaign_data = {
            "campaign_id": campaign.campaign_id,
            "name": campaign.name,
            "objective": campaign.objective.value,
            "channels": [c.value for c in campaign.channels],
            "total_budget": campaign.total_budget,
            "daily_budget": campaign.daily_budget,
            "budget_spend": 0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "revenue": 0,
            "status": campaign.status.value,
        }
        save_campaign(campaign_data)
    
    async def generate_brief(
        self,
        campaign: Campaign,
        product_description: str = "",
    ) -> str:
        """Generate a creative brief for the campaign."""
        
        brief_prompt = f"""Create a creative brief for this campaign:

Campaign: {campaign.name}
Objective: {campaign.objective.value}
Channels: {', '.join(c.value for c in campaign.channels)}
Budget: ${campaign.total_budget}

{f"Product Description: {product_description}" if product_description else ""}

Include:
1. Campaign concept and theme
2. Key messages for each channel
3. Creative direction and tone
4. Target audience profile
5. Competitive positioning
6. Success metrics and KPIs

Return as a structured brief."""

        responses = await generate_parallel(
            prompt=brief_prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.7,
            max_tokens=2048,
        )
        
        if responses:
            return responses[0].content
        return "Brief generation failed"
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign from memory."""
        data = get_campaign(campaign_id)
        if not data:
            return None
        
        # Reconstruct campaign object
        # (simplified - in production would fully reconstruct)
        return data


async def demo():
    """Demo the campaign builder."""
    print("=" * 60)
    print("MARKETIC CAMPAIGN BUILDER DEMO")
    print("=" * 60)
    
    builder = CampaignBuilder()
    
    # Build a campaign
    print("\n🚀 Building Multi-Channel Campaign...")
    campaign = await builder.build(
        name="Q3 2025 Product Launch - MarketIQ",
        objective="lead_generation",
        channels=["google_search", "meta_feed", "linkedin_sponsored"],
        total_budget=75000,
        target_audience="Growth marketers, CMOs at SaaS companies (500-5000 employees)",
        competitors=["HubSpot", "Marketo", "Pardot"],
        timeline_weeks=12,
    )
    
    print(f"\nCampaign Created:")
    print(f"  ID: {campaign.campaign_id}")
    print(f"  Name: {campaign.name}")
    print(f"  Objective: {campaign.objective.value}")
    print(f"  Channels: {[c.value for c in campaign.channels]}")
    print(f"  Total Budget: ${campaign.total_budget:,}")
    print(f"  Daily Budget: ${campaign.daily_budget:,.2f}")
    print(f"  Start: {campaign.start_date[:10]}")
    print(f"  End: {campaign.end_date[:10]}")
    print(f"  Status: {campaign.status.value}")
    print(f"  Ad Groups: {len(campaign.ad_groups)}")
    
    for ag in campaign.ad_groups:
        print(f"    - {ag.name}: ${ag.budget_daily:,.2f}/day")
    
    # Generate creative brief
    print("\n📋 Generating Creative Brief...")
    brief = await builder.generate_brief(
        campaign,
        product_description="AI-powered marketing analytics platform that automatically optimizes campaigns for maximum ROAS"
    )
    
    print(f"\nBrief Preview:")
    print(brief[:500] + "...")
    
    return campaign


if __name__ == "__main__":
    asyncio.run(demo())
