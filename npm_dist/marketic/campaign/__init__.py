"""
Marketic Campaign Orchestration

End-to-end campaign management with AI optimization:
- Campaign building and structure
- Budget allocation and routing
- A/B testing automation
- Performance optimization
"""

from .builder import CampaignBuilder, Campaign, Channel
from .optimizer import CampaignOptimizer
from .budget_router import BudgetRouter

__all__ = [
    "CampaignBuilder",
    "Campaign",
    "Channel",
    "CampaignOptimizer",
    "BudgetRouter",
]
