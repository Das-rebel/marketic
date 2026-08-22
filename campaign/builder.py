"""
Campaign Builder — Complete multi-channel campaign generation.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class CampaignObjective(str, Enum):
    AWARENESS = "awareness"
    TRAFFIC = "traffic"
    LEAD_GENERATION = "lead_generation"
    APP_INSTALLS = "app_installs"
    PURCHASES = "purchases"
    BRAND_LOYALTY = "brand_loyalty"


class Channel(str, Enum):
    EMAIL = "email"
    SOCIAL = "social"
    PAID_SEARCH = "paid_search"
    PAID_DISPLAY = "paid_display"
    CONTENT = "content"
    SEO = "seo"
    SMS = "sms"
    PUSH = "push"


@dataclass
class ChannelTactic:
    channel: str
    tactic_name: str
    description: str
    budget_percentage: float
    timeline: str
    kpis: List[str]
    creative_recommendations: List[str]


@dataclass
class CampaignTimeline:
    phase: str
    duration_weeks: int
    activities: List[str]
    milestones: List[str]


@dataclass
class CampaignBudget:
    total_budget: float
    channel_allocations: Dict[str, float]
    daily_spend_limits: Dict[str, float]


@dataclass
class Campaign:
    campaign_id: str
    name: str
    objective: str
    target_audience: str
    channels: List[str]
    timeline: List[CampaignTimeline]
    budget: CampaignBudget
    tactics: List[ChannelTactic]
    estimated_reach: int = 0
    estimated_conversions: int = 0
    estimated_roas: float = 0.0


class CampaignBuilder:
    """Build complete multi-channel marketing campaigns."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def build(
        self,
        name: str,
        objective: CampaignObjective,
        target_audience: str,
        channels: List[str],
        timeline_weeks: int = 4,
        total_budget: float = 10000,
    ) -> Campaign:
        """Build a complete campaign."""

        # Generate campaign components
        timeline = self._build_timeline(timeline_weeks, objective)
        budget = self._allocate_budget(total_budget, channels, objective)
        tactics = self._generate_tactics(channels, objective, target_audience)

        # Calculate estimates
        reach = self._estimate_reach(total_budget, channels, objective)
        conversions = self._estimate_conversions(reach, objective)
        roas = self._estimate_roas(conversions, total_budget, objective)

        return Campaign(
            campaign_id=str(uuid.uuid4())[:12],
            name=name,
            objective=objective.value,
            target_audience=target_audience,
            channels=channels,
            timeline=timeline,
            budget=budget,
            tactics=tactics,
            estimated_reach=reach,
            estimated_conversions=conversions,
            estimated_roas=roas,
        )

    def _build_timeline(
        self, weeks: int, objective: CampaignObjective
    ) -> List[CampaignTimeline]:
        """Build campaign timeline phases."""
        
        if weeks <= 2:
            return [
                CampaignTimeline(
                    phase="Launch",
                    duration_weeks=weeks,
                    activities=["Final creative production", "Audience targeting setup", "Campaign launch"],
                    milestones=["Creative approved", "Campaign live", "Initial metrics reviewed"]
                )
            ]
        
        phases = []
        
        if weeks >= 4:
            phases = [
                CampaignTimeline(
                    phase="Setup & Launch",
                    duration_weeks=1,
                    activities=[
                        "Finalize creative assets",
                        "Set up tracking pixels",
                        "Configure audience targeting",
                        "Launch campaign",
                    ],
                    milestones=["Creative sign-off", "Pixels installed", "Campaign live"]
                ),
                CampaignTimeline(
                    phase="Optimization",
                    duration_weeks=min(weeks - 2, 3),
                    activities=[
                        "Monitor initial performance",
                        "A/B test ad creative",
                        "Refine audience targeting",
                        "Adjust budget based on early ROAS",
                    ],
                    milestones=["First 100 conversions", "CTR > 2%", "CPA within target"]
                ),
                CampaignTimeline(
                    phase="Scale",
                    duration_weeks=1,
                    activities=[
                        "Scale winning ad sets",
                        "Expand to lookalike audiences",
                        "Launch retargeting",
                    ],
                    milestones=["ROAS target achieved", "Scale 50%", "Retargeting active"]
                ),
            ]
        else:
            phases = [
                CampaignTimeline(
                    phase="Launch & Optimize",
                    duration_weeks=weeks,
                    activities=["Launch", "Monitor", "Optimize"],
                    milestones=["Live", "First metrics", "Optimized"]
                )
            ]
        
        return phases

    def _allocate_budget(
        self, total: float, channels: List[str], objective: CampaignObjective
    ) -> CampaignBudget:
        """Allocate budget across channels."""
        
        # Default allocations by channel
        base_allocations = {
            "email": 0.10,
            "social": 0.30,
            "paid_search": 0.20,
            "paid_display": 0.15,
            "content": 0.10,
            "seo": 0.05,
            "sms": 0.05,
            "push": 0.05,
        }
        
        # Adjust for objective
        if objective == CampaignObjective.AWARENESS:
            base_allocations = {
                "email": 0.05,
                "social": 0.40,
                "paid_search": 0.05,
                "paid_display": 0.30,
                "content": 0.15,
                "seo": 0.05,
                "sms": 0.0,
                "push": 0.0,
            }
        elif objective == CampaignObjective.PURCHASES:
            base_allocations = {
                "email": 0.15,
                "social": 0.25,
                "paid_search": 0.25,
                "paid_display": 0.10,
                "content": 0.10,
                "seo": 0.05,
                "sms": 0.05,
                "push": 0.05,
            }
        
        # Filter to requested channels
        filtered = {k: v for k, v in base_allocations.items() if k in channels}
        
        # Renormalize
        total_pct = sum(filtered.values())
        if total_pct > 0:
            filtered = {k: v / total_pct for k, v in filtered.items()}
        
        # Apply to total budget
        allocations = {k: round(v * total, 2) for k, v in filtered.items()}
        
        # Daily limits (assuming 7 days/week)
        daily_limits = {k: round(v / 30, 2) for k, v in allocations.items()}
        
        return CampaignBudget(
            total_budget=total,
            channel_allocations=allocations,
            daily_spend_limits=daily_limits,
        )

    def _generate_tactics(
        self, channels: List[str], objective: CampaignObjective, target_audience: str
    ) -> List[ChannelTactic]:
        """Generate specific tactics for each channel."""
        
        tactics = []
        
        tactic_templates = {
            "email": [
                ChannelTactic(
                    channel="email",
                    tactic_name="Welcome Series",
                    description="3-email sequence for new subscribers",
                    budget_percentage=0.15,
                    timeline="Week 1-2",
                    kpis=["Open rate > 25%", "Click rate > 5%", "List growth"],
                    creative_recommendations=["Personalized subject lines", "Value-first content", "Clear CTAs"]
                ),
                ChannelTactic(
                    channel="email",
                    tactic_name="Promotional Blast",
                    description="Targeted offer campaign to engaged segments",
                    budget_percentage=0.10,
                    timeline="Week 2-3",
                    kpis=["Conversion rate > 3%", "Revenue per email > $0.50"],
                    creative_recommendations=["Urgency-driven subject", "Benefit-focused preview", "Single CTA"]
                ),
            ],
            "social": [
                ChannelTactic(
                    channel="social",
                    tactic_name="Content Calendar",
                    description="Daily organic + paid social mix",
                    budget_percentage=0.40,
                    timeline="All weeks",
                    kpis=["Engagement rate > 3%", "Reach growth > 10%/week", "Follower growth"],
                    creative_recommendations=["Video content (60%)", "Carousels (25%)", "Static images (15%)"]
                ),
                ChannelTactic(
                    channel="social",
                    tactic_name="Retargeting Ads",
                    description="Website visitor retargeting on Meta/LinkedIn",
                    budget_percentage=0.35,
                    timeline="Week 2+",
                    kpis=["CTR > 1%", "Conversion rate > 2%", "ROAS > 3x"],
                    creative_recommendations=["Dynamic product ads", "Testimonial creative", "Limited offers"]
                ),
            ],
            "paid_search": [
                ChannelTactic(
                    channel="paid_search",
                    tactic_name="Branded Keywords",
                    description="Protect brand terms and capture high-intent traffic",
                    budget_percentage=0.30,
                    timeline="All weeks",
                    kpis=["Impression share > 80%", "CPC < $2.50", "Conversion rate > 5%"],
                    creative_recommendations=["Specific CTAs", "Social proof", "Unique offers"]
                ),
                ChannelTactic(
                    channel="paid_search",
                    tactic_name="Non-Branded Campaigns",
                    description="Category/product keyword campaigns",
                    budget_percentage=0.45,
                    timeline="Week 1+",
                    kpis=["Keyword rankings", "Quality Score > 7", "CPA < $25"],
                    creative_recommendations=["Keyword-triggered ad copy", "Compelling extensions", "Negative keyword management"]
                ),
            ],
            "paid_display": [
                ChannelTactic(
                    channel="paid_display",
                    tactic_name="Prospecting Campaigns",
                    description="Reach new audiences via display/programmatic",
                    budget_percentage=0.50,
                    timeline="Week 1+",
                    kpis=["CPM < $5", "View-through rate > 0.5%", "Brand lift > 10%"],
                    creative_recommendations=["Awareness-focused creative", "Short video ads (15s)", "Native formats"]
                ),
            ],
            "content": [
                ChannelTactic(
                    channel="content",
                    tactic_name="SEO Content Hub",
                    description="Long-form articles and guides for organic traffic",
                    budget_percentage=0.40,
                    timeline="Week 1-4",
                    kpis=["Organic traffic growth > 15%", "Keyword rankings", "Time on page > 3min"],
                    creative_recommendations=["Expert roundups", "How-to guides", "Industry insights"]
                ),
            ],
            "seo": [
                ChannelTactic(
                    channel="seo",
                    tactic_name="Technical SEO Audit",
                    description="Fix site issues affecting search visibility",
                    budget_percentage=0.30,
                    timeline="Week 1-2",
                    kpis=["Core Web Vitals pass", "Crawl errors < 10", "Index coverage > 95%"],
                    creative_recommendations=["Site speed optimization", "Mobile audit", "Schema markup"]
                ),
            ],
            "sms": [
                ChannelTactic(
                    channel="sms",
                    tactic_name="Transactional Messages",
                    description="Order confirmations and shipping updates",
                    budget_percentage=0.20,
                    timeline="All weeks",
                    kpis=["Delivery rate > 95%", "Opt-out rate < 1%", "Revenue per message"],
                    creative_recommendations=["Short and clear", "Emoji use (where appropriate)", "Timing optimization"]
                ),
            ],
            "push": [
                ChannelTactic(
                    channel="push",
                    tactic_name="Re-engagement Campaign",
                    description="Win back lapsed users with incentives",
                    budget_percentage=0.30,
                    timeline="Week 3-4",
                    kpis=["Open rate > 15%", "Click rate > 5%", "Reactivation rate > 10%"],
                    creative_recommendations=["Time-sensitive offers", "New feature announcements", "Personalized content"]
                ),
            ],
        }
        
        for channel in channels:
            channel_tactics = tactic_templates.get(channel, [])
            tactics.extend(channel_tactics)
        
        return tactics

    def _estimate_reach(self, budget: float, channels: List[str], objective: CampaignObjective) -> int:
        """Estimate total campaign reach."""
        
        # CPM estimates by channel
        cpm_rates = {
            "email": 0.5,      # Very cheap, high volume
            "social": 8.0,
            "paid_search": 15.0,
            "paid_display": 4.0,
            "content": 2.0,
            "seo": 0.0,        # Organic, no media cost
            "sms": 0.05,       # Per message
            "push": 0.02,
        }
        
        # Weight by channel allocation
        weights = {
            "email": 0.25,
            "social": 0.30,
            "paid_search": 0.20,
            "paid_display": 0.15,
            "content": 0.05,
            "seo": 0.0,
            "sms": 0.03,
            "push": 0.02,
        }
        
        weighted_cpm = sum(cpm_rates.get(ch, 5.0) * weights.get(ch, 0.1) for ch in channels)
        
        if weighted_cpm > 0:
            impressions = (budget / weighted_cpm) * 1000
        else:
            impressions = budget * 100  # Fallback
        
        return int(impressions)

    def _estimate_conversions(self, reach: int, objective: CampaignObjective) -> int:
        """Estimate conversions from reach."""
        
        # Conversion rate estimates by objective
        conversion_rates = {
            CampaignObjective.AWARENESS: 0.001,      # 0.1%
            CampaignObjective.TRAFFIC: 0.01,          # 1%
            CampaignObjective.LEAD_GENERATION: 0.02,  # 2%
            CampaignObjective.APP_INSTALLS: 0.03,     # 3%
            CampaignObjective.PURCHASES: 0.015,       # 1.5%
            CampaignObjective.BRAND_LOYALTY: 0.05,     # 5%
        }
        
        rate = conversion_rates.get(objective, 0.01)
        return int(reach * rate)

    def _estimate_roas(self, conversions: int, budget: float, objective: CampaignObjective) -> float:
        """Estimate ROAS from conversions."""
        
        if conversions == 0 or budget == 0:
            return 0.0
        
        # Average order value estimates
        aov_by_objective = {
            CampaignObjective.AWARENESS: 0,
            CampaignObjective.TRAFFIC: 5,
            CampaignObjective.LEAD_GENERATION: 50,
            CampaignObjective.APP_INSTALLS: 3,
            CampaignObjective.PURCHASES: 75,
            CampaignObjective.BRAND_LOYALTY: 100,
        }
        
        aov = aov_by_objective.get(objective, 50)
        revenue = conversions * aov
        
        return round(revenue / budget, 2)
