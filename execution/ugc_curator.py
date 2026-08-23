"""
UGC Curation — User-generated content collection and permission workflow.
"""

import os
import httpx
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class PermissionStatus(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class UGCContent:
    content_id: str
    platform: str
    username: str
    caption: str
    hashtags: List[str]
    image_url: str
    video_url: Optional[str]
    likes: int
    comments: int
    posted_at: str
    relevance_score: float
    aesthetic_score: float
    permission_status: PermissionStatus
    permission_requested_at: Optional[str]
    permission_granted_at: Optional[str]


@dataclass
class PermissionRequest:
    request_id: str
    content_id: str
    username: str
    platform: str
    message_template: str
    status: PermissionStatus
    created_at: str
    responded_at: Optional[str]


@dataclass
class UGCRepost:
    repost_id: str
    original_content: UGCContent
    branded_caption: str
    hashtags: List[str]
    scheduled_for: Optional[str]
    posted_to: List[str]
    status: str


class HashtagMonitor:
    """Monitor hashtags across platforms."""

    # Default hashtags to monitor
    DEFAULT_HASHTAGS = [
        "brand_mentions",  # Primary brand hashtag
        "brand_location",   # Location-specific
        "tagline",         # Tagline hashtag
        "location",        # City/area
        "industry_specific",  # Industry crossover
    ]

    def __init__(self):
        self._instagram_key = os.environ.get("INSTAGRAM_API_KEY")
        self._tiktok_key = os.environ.get("TIKTOK_API_KEY")

    async def monitor_hashtag(self, hashtag: str, platform: str = "instagram") -> List[Dict]:
        """
        Monitor a hashtag and return recent posts.
        Note: Requires proper API access (Meta Graph API, TikTok API, etc.)
        """
        # Placeholder - real implementation would use platform APIs
        return []

    async def search_mentions(self, query: str, platform: str = "instagram") -> List[Dict]:
        """Search for brand/product mentions."""
        return []


class UGCCurator:
    """
    UGC Curation workflow:
    1. Discover content via hashtag monitoring
    2. Score and filter based on aesthetics + relevance
    3. Request permissions via DM templates
    4. Create branded repost
    5. Track and measure performance
    """

    def __init__(self):
        self.monitor = HashtagMonitor()
        self._api_key = os.environ.get("OPENROUTER_API_KEY")

    async def discover_content(
        self,
        hashtags: List[str],
        platforms: List[str] = None,
        min_likes: int = 10,
        limit: int = 50,
    ) -> List[UGCContent]:
        """
        Discover UGC from monitored hashtags.
        """
        platforms = platforms or ["instagram"]
        discovered = []

        for hashtag in hashtags:
            for platform in platforms:
                posts = await self.monitor.monitor_hashtag(hashtag, platform)
                for post in posts[:limit]:
                    if post.get("likes", 0) >= min_likes:
                        content = self._parse_post(post, platform)
                        if content:
                            content.relevance_score = self._calculate_relevance(content, hashtag)
                            content.aesthetic_score = self._calculate_aesthetic_score(content)
                            discovered.append(content)

        # Sort by combined score
        discovered.sort(
            key=lambda x: x.relevance_score * 0.4 + x.aesthetic_score * 0.6,
            reverse=True,
        )

        return discovered[:limit]

    def _parse_post(self, post: Dict, platform: str) -> Optional[UGCContent]:
        """Parse raw post data into UGCContent."""
        try:
            return UGCContent(
                content_id=post.get("id", ""),
                platform=platform,
                username=post.get("username", post.get("user", {}).get("username", "unknown")),
                caption=post.get("caption", post.get("text", "")),
                hashtags=self._extract_hashtags(post.get("caption", "")),
                image_url=post.get("image_url", post.get("media_url", "")),
                video_url=post.get("video_url"),
                likes=post.get("likes", 0),
                comments=post.get("comments", 0),
                posted_at=post.get("posted_at", post.get("timestamp", "")),
                relevance_score=0.0,
                aesthetic_score=0.0,
                permission_status=PermissionStatus.PENDING,
                permission_requested_at=None,
                permission_granted_at=None,
            )
        except Exception:
            return None

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        import re
        return re.findall(r"#\w+", text.lower())

    def _calculate_relevance(self, content: UGCContent, target_hashtag: str) -> float:
        """
        Calculate relevance score (0-1) based on:
        - Hashtag match
        - Caption relevance
        - Engagement rate
        """
        score = 0.0

        # Hashtag match
        target = target_hashtag.lower().replace("#", "")
        matching_hashtags = [h for h in content.hashtags if target in h]
        score += min(len(matching_hashtags) / 3, 1.0) * 0.3

        # Engagement rate (normalized)
        total_engagement = content.likes + content.comments * 2
        engagement_rate = min(total_engagement / 1000, 1.0)
        score += engagement_rate * 0.4

        # Caption relevance (presence of keywords)
        caption_words = content.caption.lower().split()
        relevant_words = ["love", "amazing", "great", "best", "perfect", "favorite", "recommend"]
        relevance = sum(1 for w in caption_words if w in relevant_words) / max(len(caption_words), 1)
        score += relevance * 0.3

        return min(score, 1.0)

    def _calculate_aesthetic_score(self, content: UGCContent) -> float:
        """
        Calculate aesthetic score (0-1) based on:
        - Image/video quality indicators
        - Brand alignment
        - Content type
        """
        score = 0.5  # Base score

        # Has image (generally better than no image)
        if content.image_url:
            score += 0.2

        # Good engagement ratio (likes vs comments)
        if content.likes > 0:
            comment_ratio = content.comments / content.likes
            if 0.01 < comment_ratio < 0.2:  # Healthy engagement
                score += 0.2

        # Caption length (not too short, not too long)
        caption_len = len(content.caption)
        if 50 < caption_len < 300:
            score += 0.1

        return min(score, 1.0)

    async def request_permission(
        self,
        content: UGCContent,
        language: str = "english",
    ) -> PermissionRequest:
        """
        Send permission request via DM.
        Returns the request object (actual sending requires platform API access).
        """
        templates = {
            "english": "Hey {name}! We love this shot of our place! Would you mind if we share it on our feed? We'll tag you of course. Thanks!",
            "indonesian": "Hai {name}! Kami suka banget foto kami! Boleh nggak kalau kami share di feed kami? Pasti kami tag ya. Makasih!",
        }

        template = templates.get(language, templates["english"])
        message = template.format(name=content.username)

        return PermissionRequest(
            request_id=f"perm_{content.content_id}",
            content_id=content.content_id,
            username=content.username,
            platform=content.platform,
            message_template=message,
            status=PermissionStatus.PENDING,
            created_at="",
            responded_at=None,
        )

    def create_repost_caption(
        self,
        content: UGCContent,
        include_story: bool = True,
    ) -> Tuple[str, List[str]]:
        """
        Create branded caption for UGC repost.
        Returns (caption, hashtags).
        """
        # Credit line
        caption = f"📸 @{content.username}\n\n"

        # Micro-story (short, warm)
        caption += f"{content.caption[:150]}...\n\n"

        # Community CTA
        if include_story:
            caption += "Tag us in your moments — we love seeing your stories\n\n"

        # Hashtags
        hashtags = ["#Repost", "#BrandName"]

        return caption, hashtags

    def filter_content(
        self,
        content: List[UGCContent],
        min_aesthetic: float = 0.5,
        min_relevance: float = 0.4,
    ) -> List[UGCContent]:
        """
        Filter content based on quality thresholds.
        """
        filtered = []

        for c in content:
            combined = c.aesthetic_score * 0.6 + c.relevance_score * 0.4
            if c.aesthetic_score >= min_aesthetic and c.relevance_score >= min_relevance:
                filtered.append(c)

        return filtered

    def select_content_for_repost(
        self,
        content: List[UGCContent],
        target_count: int = 1,
    ) -> List[UGCContent]:
        """
        Select best content for reposting based on combined scoring.
        """
        scored = []

        for c in content:
            if c.permission_status != PermissionStatus.GRANTED:
                continue

            combined = c.aesthetic_score * 0.6 + c.relevance_score * 0.4
            scored.append((combined, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:target_count]]


class UGCAnalytics:
    """Track UGC performance."""

    async def track_repost(self, repost: UGCRepost) -> Dict[str, Any]:
        """
        Track a UGC repost for performance.
        """
        return {
            "repost_id": repost.repost_id,
            "original_content_id": repost.original_content.content_id,
            "platform": repost.original_content.platform,
            "status": repost.status,
            "metrics": {
                "reach": 0,
                "likes": 0,
                "comments": 0,
                "saves": 0,
                "shares": 0,
            },
        }
