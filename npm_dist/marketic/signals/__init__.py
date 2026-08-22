"""
Marketic Signals - Market Intelligence Collection

Collects and analyzes market signals from multiple sources.
"""

from .collectors import (
    RedditCollector,
    TwitterCollector,
    TrendsCollector,
    ProductHuntCollector,
    RSSCollector,
    run_full_pipeline,
)

__all__ = [
    "RedditCollector",
    "TwitterCollector",
    "TrendsCollector",
    "ProductHuntCollector",
    "RSSCollector",
    "run_full_pipeline",
]
