"""
Marketic - Marketing Intelligence OS

AI-native full-stack marketing operating system.

Built on:
- a3m-style parallel multi-LLM routing
- growth-workflow-os signal intelligence  
- omniclaw-style orchestration

Usage:
    from marketic import CopyGenerator, CampaignBuilder, Analytics
    
    # Generate ad copy
    generator = CopyGenerator()
    variants = await generator.generate_variants(request)
"""

__version__ = "0.1.0"
__author__ = "Subhajit"

# Core modules
from .foundation.llm_router import MarketicLLMRouter, TaskType
from .foundation.memory import MarketicMemory
from .foundation.orchestration import OrchestrationLayer
from .foundation.alerts import AlertLayer

# Creative generation
from .creative import CopyGenerator, SocialGenerator, SEOGenerator

# Campaign management
from .campaign import CampaignBuilder, CampaignOptimizer, BudgetRouter

# Analytics
from .analytics import AttributionModel, MultiTouchAttribution, AnalyticsDashboard, ReportGenerator

# GTM Intelligence
from .gtm import PositioningAnalyzer, CompetitiveIntelligence, NarrativeGenerator

# Signal intelligence
from .signals.collectors import RedditCollector, TwitterCollector, TrendsCollector, RSSCollector

__all__ = [
    # Version
    "__version__",
    
    # Foundation
    "MarketicLLMRouter",
    "TaskType",
    "MarketicMemory",
    "OrchestrationLayer",
    "AlertLayer",
    
    # Creative
    "CopyGenerator",
    "SocialGenerator",
    "SEOGenerator",
    
    # Campaign
    "CampaignBuilder",
    "CampaignOptimizer",
    "BudgetRouter",
    
    # Analytics
    "AttributionModel",
    "MultiTouchAttribution",
    "AnalyticsDashboard",
    "ReportGenerator",
    
    # GTM
    "PositioningAnalyzer",
    "CompetitiveIntelligence",
    "NarrativeGenerator",
    
    # Signals
    "RedditCollector",
    "TwitterCollector",
    "TrendsCollector",
    "RSSCollector",
]
