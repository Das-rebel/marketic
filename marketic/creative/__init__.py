"""
Marketic Creative Generation

AI-powered content creation across all marketing channels:
- Ad copy (Google, Meta, LinkedIn, TikTok)
- Social media (Twitter threads, LinkedIn posts)
- SEO content (blog posts, articles)
- Email sequences
- Video scripts
"""

from .copy_generator import CopyGenerator, AdCopyRequest
from .social_generator import SocialGenerator, SocialContentRequest
from .seo_generator import SEOGenerator, SEOContentRequest

__all__ = [
    "CopyGenerator",
    "AdCopyRequest",
    "SocialGenerator", 
    "SocialContentRequest",
    "SEOGenerator",
    "SEOContentRequest",
]
