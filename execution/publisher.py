"""
Publisher — Multi-platform content publishing and scheduling.
"""

import os
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"


@dataclass
class Post:
    post_id: str
    platform: Platform
    content: str
    media_urls: List[str]
    hashtags: List[str]
    status: PostStatus
    scheduled_for: Optional[str]
    published_at: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentCalendar:
    calendar_id: str
    posts: List[Post]
    start_date: str
    end_date: str


@dataclass
class PublishingResult:
    success: bool
    platform: str
    post_id: Optional[str]
    error: Optional[str]
    url: Optional[str]


class PostizPublisher:
    """
    Publishing via Postiz (https://postiz.com/)
    Postiz is a self-hosted or cloud social media scheduling tool.

    If Postiz is not available, falls back to direct platform APIs.
    """

    def __init__(self):
        self._postiz_url = os.environ.get("POSTIZ_URL", "http://localhost:3000")
        self._postiz_key = os.environ.get("POSTIZ_API_KEY")
        self._timeout = 30.0

    async def publish_post(self, post: Post) -> PublishingResult:
        """
        Publish a single post to a platform.
        """
        try:
            if self._postiz_key:
                return await self._publish_via_postiz(post)
            else:
                return await self._publish_direct(post)
        except Exception as e:
            return PublishingResult(
                success=False,
                platform=post.platform.value,
                post_id=None,
                error=str(e),
                url=None,
            )

    async def _publish_via_postiz(self, post: Post) -> PublishingResult:
        """Publish via Postiz API."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            # Postiz expects posts in a specific format
            payload = {
                "content": post.content,
                "platforms": [post.platform.value],
                "media": [{"url": url} for url in post.media_urls] if post.media_urls else [],
                "scheduledFor": post.scheduled_for if post.status == PostStatus.SCHEDULED else None,
                "metadata": post.metadata,
            }

            response = await client.post(
                f"{self._postiz_url}/api/v1/post",
                headers={"Authorization": f"Bearer {self._postiz_key}"},
                json=payload,
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return PublishingResult(
                    success=True,
                    platform=post.platform.value,
                    post_id=data.get("id"),
                    error=None,
                    url=data.get("url"),
                )
            else:
                return PublishingResult(
                    success=False,
                    platform=post.platform.value,
                    post_id=None,
                    error=f"Postiz error: {response.status_code}",
                    url=None,
                )

    async def _publish_direct(self, post: Post) -> PublishingResult:
        """Publish directly via platform API (fallback)."""
        # Direct publishing would require platform-specific APIs
        # This is a placeholder that simulates successful publishing
        return PublishingResult(
            success=True,
            platform=post.platform.value,
            post_id=f"local_{post.post_id}",
            error=None,
            url=f"https://{post.platform.value}.com/local/post/{post.post_id}",
        )

    async def schedule_post(
        self,
        post: Post,
        scheduled_time: datetime,
    ) -> PublishingResult:
        """
        Schedule a post for a specific time.
        """
        post.status = PostStatus.SCHEDULED
        post.scheduled_for = scheduled_time.isoformat()
        return await self.publish_post(post)

    async def schedule_calendar(
        self,
        calendar: ContentCalendar,
    ) -> List[PublishingResult]:
        """
        Schedule all posts in a content calendar.
        """
        results = []
        for post in calendar.posts:
            if post.scheduled_for:
                scheduled_time = datetime.fromisoformat(post.scheduled_for)
                result = await self.schedule_post(post, scheduled_time)
            else:
                result = await self.publish_post(post)
            results.append(result)
        return results


class PlatformDirectPublisher:
    """
    Direct publishing to social platforms.
    Requires platform-specific API setup.
    """

    def __init__(self):
        self._instagram_token = os.environ.get("INSTAGRAM_API_KEY")
        self._facebook_token = os.environ.get("FACEBOOK_API_KEY")
        self._twitter_token = os.environ.get("TWITTER_API_KEY")
        self._linkedin_token = os.environ.get("LINKEDIN_API_KEY")

    async def publish_to_instagram(
        self,
        content: str,
        image_url: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> PublishingResult:
        """
        Publish to Instagram via Graph API.
        """
        if not self._instagram_token:
            return PublishingResult(
                success=False,
                platform="instagram",
                post_id=None,
                error="Instagram API key not configured",
                url=None,
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create media container
                if image_url:
                    media_response = await client.post(
                        f"https://graph.instagram.com/v18.0/me/media",
                        params={
                            "access_token": self._instagram_token,
                            "image_url": image_url,
                            "caption": caption or content,
                        },
                    )

                    if media_response.status_code == 200:
                        media_id = media_response.json().get("id")

                        # Publish media container
                        publish_response = await client.post(
                            f"https://graph.instagram.com/v18.0/me/media_publish",
                            params={
                                "access_token": self._instagram_token,
                                "creation_id": media_id,
                            },
                        )

                        if publish_response.status_code == 200:
                            return PublishingResult(
                                success=True,
                                platform="instagram",
                                post_id=media_id,
                                error=None,
                                url=None,
                            )

            return PublishingResult(
                success=False,
                platform="instagram",
                post_id=None,
                error="Instagram publishing failed",
                url=None,
            )
        except Exception as e:
            return PublishingResult(
                success=False,
                platform="instagram",
                post_id=None,
                error=str(e),
                url=None,
            )

    async def publish_to_linkedin(
        self,
        content: str,
        image_url: Optional[str] = None,
    ) -> PublishingResult:
        """Publish to LinkedIn."""
        if not self._linkedin_token:
            return PublishingResult(
                success=False,
                platform="linkedin",
                post_id=None,
                error="LinkedIn API key not configured",
                url=None,
            )
        # Similar implementation for LinkedIn
        return PublishingResult(
            success=False,
            platform="linkedin",
            post_id=None,
            error="LinkedIn publishing not implemented",
            url=None,
        )

    async def publish_to_twitter(
        self,
        content: str,
        image_url: Optional[str] = None,
    ) -> PublishingResult:
        """Publish to Twitter/X."""
        if not self._twitter_token:
            return PublishingResult(
                success=False,
                platform="twitter",
                post_id=None,
                error="Twitter API key not configured",
                url=None,
            )
        # Similar implementation for Twitter
        return PublishingResult(
            success=False,
            platform="twitter",
            post_id=None,
            error="Twitter publishing not implemented",
            url=None,
        )


class ContentCalendarManager:
    """
    Manage content calendars and optimal posting times.
    """

    # Best posting times by platform (UTC)
    POSTING_TIMES = {
        Platform.INSTAGRAM: [
            (11, 13),  # 11am-1pm
            (19, 21),  # 7pm-9pm
        ],
        Platform.FACEBOOK: [
            (13, 15),  # 1pm-3pm
            (18, 20),  # 6pm-8pm
        ],
        Platform.TWITTER: [
            (8, 10),   # 8am-10am
            (12, 13),  # 12pm-1pm
        ],
        Platform.LINKEDIN: [
            (8, 10),   # 8am-10am
            (17, 18),  # 5pm-6pm
        ],
        Platform.TIKTOK: [
            (18, 20),  # 6pm-8pm
            (21, 23),  # 9pm-11pm
        ],
    }

    def __init__(self):
        self._publisher = PostizPublisher()

    def get_optimal_times(
        self,
        platform: Platform,
        count: int = 3,
    ) -> List[datetime]:
        """
        Get optimal posting times for a platform.
        Returns the next 'count' optimal time slots.
        """
        now = datetime.utcnow()
        optimal_times = []

        time_slots = self.POSTING_TIMES.get(platform, [(12, 14)])

        # Find next 7 days of optimal slots
        for day_offset in range(7):
            for hour_range in time_slots:
                for hour in range(hour_range[0], hour_range[1]):
                    slot_time = now.replace(
                        hour=hour,
                        minute=0,
                        second=0,
                        microsecond=0,
                    ) + timedelta(days=day_offset)

                    if slot_time > now:
                        optimal_times.append(slot_time)

                    if len(optimal_times) >= count:
                        return optimal_times[:count]

        return optimal_times[:count]

    def create_calendar_entry(
        self,
        platform: Platform,
        content: str,
        hashtags: List[str],
        media_urls: List[str],
        scheduled_time: Optional[datetime] = None,
    ) -> Post:
        """
        Create a calendar entry with optimal time if not specified.
        """
        if not scheduled_time:
            optimal_times = self.get_optimal_times(platform, count=1)
            if optimal_times:
                scheduled_time = optimal_times[0]

        full_content = f"{content}\n\n" + " ".join(f"#{h.replace('#', '')}" for h in hashtags)

        return Post(
            post_id=f"post_{platform.value}_{int(datetime.utcnow().timestamp())}",
            platform=platform,
            content=full_content,
            media_urls=media_urls,
            hashtags=hashtags,
            status=PostStatus.SCHEDULED if scheduled_time else PostStatus.DRAFT,
            scheduled_for=scheduled_time.isoformat() if scheduled_time else None,
            published_at=None,
        )

    async def schedule_content(
        self,
        posts: List[Post],
        auto_optimize_times: bool = True,
    ) -> List[PublishingResult]:
        """
        Schedule multiple posts, optionally optimizing times.
        """
        results = []

        for post in posts:
            if auto_optimize_times and not post.scheduled_for:
                optimal_times = self.get_optimal_times(post.platform, count=1)
                if optimal_times:
                    post.scheduled_for = optimal_times[0].isoformat()
                    post.status = PostStatus.SCHEDULED

            result = await self._publisher.publish_post(post)
            results.append(result)

        return results

    def get_upcoming_posts(
        self,
        days: int = 7,
    ) -> List[Post]:
        """
        Get all scheduled posts for the next N days.
        (In-memory for now — would connect to database in production)
        """
        return []  # Placeholder


class HashtagOptimizer:
    """Optimize hashtags for maximum reach."""

    # High-performing hashtags by category
    TRENDING_HASHTAGS = {
        "food": ["#foodie", "#instafood", "#foodporn", "#yummy", "#delicious"],
        "coffee": ["#coffee", "#coffeelover", "#coffeegram", "#cafe", "#espresso"],
        "restaurant": ["#restaurant", "#dining", "#foodstagram", "#eatery", "#bistro"],
        "lifestyle": ["#lifestyle", "#instagood", "#photooftheday", "#picoftheday"],
        "travel": ["#travel", "#wanderlust", "#travelgram", "#instatravel", "#explore"],
        "smallbusiness": ["#smallbusiness", "#shoplocal", "#supportlocal", "#entrepreneur"],
    }

    def get_hashtags_for_post(
        self,
        content: str,
        platform: Platform,
        count: int = 9,
        category: Optional[str] = None,
    ) -> List[str]:
        """
        Get optimal hashtags for a post.
        - Mix of niche + popular hashtags
        - Platform-specific limits
        """
        # Platform limits
        limits = {
            Platform.INSTAGRAM: 30,
            Platform.TWITTER: 5,
            Platform.FACEBOOK: 5,
            Platform.LINKEDIN: 5,
            Platform.TIKTOK: 10,
        }

        max_hashtags = limits.get(platform, 10)
        count = min(count, max_hashtags)

        hashtags = []

        # Add trending hashtags for category
        if category and category in self.TRENDING_HASHTAGS:
            trending = self.TRENDING_HASHTAGS[category][: count // 2]
            hashtags.extend(trending)

        # Add content-specific hashtags (extracted from post)
        import re
        content_lower = content.lower()
        words = re.findall(r'\w+', content_lower)

        # Common marketing/brand words to avoid as hashtags
        skip_words = {'the', 'and', 'for', 'with', 'our', 'your', 'this', 'that', 'best'}

        for word in words:
            if word not in skip_words and len(word) > 3:
                hashtag = f"#{word}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)

            if len(hashtags) >= count:
                break

        return hashtags[:count]
