"""
Social Media Content Generator

Generates content for Twitter/X, LinkedIn, Instagram, and more.
Features:
- Twitter threads (curated insights style)
- LinkedIn posts (professional storytelling)
- Instagram captions
- Multi-platform adaptation
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

from ..foundation.llm_router import generate_parallel, TaskType


class SocialPlatform(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    THREADS = "threads"


class ContentFormat(Enum):
    SINGLE_POST = "single"
    THREAD = "thread"
    CAROUSEL_IDEA = "carousel"
    STORY_IDEA = "story"
    VIDEO_SCRIPT = "video_script"


@dataclass
class SocialContentRequest:
    """Request for social content generation."""
    topic: str
    platform: SocialPlatform
    format: ContentFormat = ContentFormat.SINGLE_POST
    num_options: int = 3
    target_audience: str = ""
    include_hashtags: bool = True
    include_hooks: bool = True
    tone: str = "professional"  # professional, casual, humorous, inspirational
    thread_length: int = 5  # For threads


@dataclass
class SocialPost:
    """A single social media post."""
    post_id: str
    platform: str
    content: str
    thread_posts: List[str] = field(default_factory=list)  # For threads
    hashtags: List[str] = field(default_factory=list)
    hook: str = ""
    cta: str = ""
    estimated_engagement: str = ""  # low, medium, high, viral
    confidence: float = 0.0


class SocialGenerator:
    """
    Generates social media content for all major platforms.
    
    Usage:
        generator = SocialGenerator()
        
        # Twitter thread
        posts = await generator.generate(
            topic="How AI is changing marketing",
            platform=SocialPlatform.TWITTER,
            format=ContentFormat.THREAD,
            thread_length=8
        )
        
        # LinkedIn post
        posts = await generator.generate(
            topic="My journey building a marketing tool",
            platform=SocialPlatform.LINKEDIN,
            format=ContentFormat.SINGLE_POST
        )
    """
    
    def _build_prompt(self, request: SocialContentRequest) -> str:
        """Build prompt for social content generation."""
        
        platform_context = {
            SocialPlatform.TWITTER: {
                "name": "Twitter/X",
                "style": "concise, punchy, with character limits (280 chars per tweet)",
                "best_for": "quick insights, threads, hot takes, engagement bait",
            },
            SocialPlatform.LINKEDIN: {
                "name": "LinkedIn",
                "style": "professional storytelling, value-driven, longer-form ok (1500-3000 chars)",
                "best_for": "thought leadership, career insights, industry analysis",
            },
            SocialPlatform.INSTAGRAM: {
                "name": "Instagram",
                "style": "visual-first, short captions (150-300 chars), emojis encouraged",
                "best_for": "brand awareness, behind-the-scenes, lifestyle",
            },
            SocialPlatform.FACEBOOK: {
                "name": "Facebook",
                "style": "conversational, community-focused, longer captions ok",
                "best_for": "community building, event promotion, stories",
            },
        }.get(request.platform, {})
        
        format_guidance = ""
        if request.format == ContentFormat.THREAD:
            format_guidance = f"Create a {request.thread_length}-tweet thread with: hook tweet, context, insights, examples, and CTA"
        elif request.format == ContentFormat.SINGLE_POST:
            format_guidance = "Create a single impactful post with hook, content, and optional CTA"
        elif request.format == ContentFormat.CAROUSEL_IDEA:
            format_guidance = "Outline a carousel with 10 slides: title + 8 insights + CTA slide"
        
        tone_guidance = f"Tone: {request.tone}" 
        
        prompt = f"""You are a social media expert creating content for {platform_context.get('name', 'social')}.

Create {request.num_options} content options for:
- Topic: {request.topic}
- Platform: {platform_context.get('name', 'Social Media')}
- Style: {platform_context.get('style', '')}
- Best for: {platform_context.get('best_for', '')}
- Format: {format_guidance}
- Tone: {tone_guidance}

{f"Target Audience: {request.target_audience}" if request.target_audience else ""}

Requirements:
1. Include attention-grabbing hook (first line is crucial)
2. Make it scroll-stopping
3. Include value/information density
4. Include relevant hashtags
5. End with engagement CTA

{f"Hashtags: Include hashtags" if request.include_hashtags else "No hashtags needed"}

Return as JSON with fields: content, hashtags, hook, cta, estimated_engagement"""
        
        return prompt
    
    async def generate(self, request: SocialContentRequest) -> List[SocialPost]:
        """Generate social content."""
        
        prompt = self._build_prompt(request)
        
        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.SOCIAL_MEDIA,
            temperature=0.75,
            max_tokens=2048,
        )
        
        posts = []
        
        for response in responses[:1]:
            try:
                if "[" in response.content:
                    start = response.content.find("[")
                    end = response.content.rfind("]") + 1
                    data = json.loads(response.content[start:end])
                    
                    for item in data[:request.num_options]:
                        post = SocialPost(
                            post_id=str(uuid.uuid4())[:8],
                            platform=request.platform.value,
                            content=item.get("content", ""),
                            hashtags=item.get("hashtags", []),
                            hook=item.get("hook", ""),
                            cta=item.get("cta", ""),
                            estimated_engagement=item.get("estimated_engagement", "medium"),
                            confidence=response.confidence,
                        )
                        
                        # For threads, parse out individual tweets
                        if request.format == ContentFormat.THREAD:
                            post.thread_posts = self._parse_thread(post.content, request.thread_length)
                        
                        posts.append(post)
                else:
                    posts = self._parse_text_response(response.content, request)
                    
            except json.JSONDecodeError:
                posts = self._parse_text_response(response.content, request)
        
        if not posts:
            posts = [self._create_fallback_post(request)]
        
        return posts[:request.num_options]
    
    def _parse_thread(self, content: str, length: int) -> List[str]:
        """Parse thread content into individual tweets."""
        tweets = []
        
        # Split by common delimiters
        parts = content.split("\n\n")
        
        for part in parts[:length]:
            tweet = part.strip()
            if tweet and len(tweet) <= 280:
                tweets.append(tweet)
            elif len(tweet) > 280:
                # Truncate with ellipsis
                tweets.append(tweet[:277] + "...")
        
        return tweets
    
    def _parse_text_response(self, content: str, request: SocialContentRequest) -> List[SocialPost]:
        """Parse text response into posts."""
        posts = []
        blocks = content.split("\n\n")
        
        for block in blocks[:request.num_options]:
            post = SocialPost(
                post_id=str(uuid.uuid4())[:8],
                platform=request.platform.value,
                content=block.strip(),
                hashtags=[],
                confidence=0.7,
            )
            
            if request.format == ContentFormat.THREAD:
                post.thread_posts = self._parse_thread(block, request.thread_length)
            
            posts.append(post)
        
        return posts
    
    def _create_fallback_post(self, request: SocialContentRequest) -> SocialPost:
        """Create fallback post."""
        return SocialPost(
            post_id=str(uuid.uuid4())[:8],
            platform=request.platform.value,
            content=f"Here's what I learned about {request.topic}...",
            hashtags=[f"{request.topic.replace(' ', '')}", "Marketing", "Growth"],
            hook="The biggest mistake marketers make...",
            estimated_engagement="medium",
            confidence=0.5,
        )
    
    async def generate_twitter_thread(
        self,
        topic: str,
        length: int = 8,
        **kwargs
    ) -> SocialPost:
        """Convenience method for Twitter threads."""
        request = SocialContentRequest(
            topic=topic,
            platform=SocialPlatform.TWITTER,
            format=ContentFormat.THREAD,
            thread_length=length,
            **kwargs
        )
        posts = await self.generate(request)
        return posts[0] if posts else None
    
    async def generate_linkedin_post(
        self,
        topic: str,
        **kwargs
    ) -> SocialPost:
        """Convenience method for LinkedIn posts."""
        request = SocialContentRequest(
            topic=topic,
            platform=SocialPlatform.LINKEDIN,
            format=ContentFormat.SINGLE_POST,
            **kwargs
        )
        posts = await self.generate(request)
        return posts[0] if posts else None


async def demo():
    """Demo the social generator."""
    print("=" * 60)
    print("MARKETIC SOCIAL CONTENT GENERATOR DEMO")
    print("=" * 60)
    
    generator = SocialGenerator()
    
    # Twitter thread
    print("\n🐦 Generating Twitter Thread...")
    thread = await generator.generate_twitter_thread(
        topic="Why most marketing automation fails",
        length=6,
        tone="provocative"
    )
    
    if thread:
        print(f"\nThread ({len(thread.thread_posts)} tweets):")
        for i, tweet in enumerate(thread.thread_posts, 1):
            print(f"\n  Tweet {i}:")
            print(f"    {tweet[:100]}...")
    
    # LinkedIn post
    print("\n\n📄 Generating LinkedIn Post...")
    post = await generator.generate_linkedin_post(
        topic="The future of performance marketing in the AI era",
        tone="professional",
        num_options=2
    )
    
    if post:
        print(f"\nLinkedIn Post:")
        print(f"  {post.content[:200]}...")
        print(f"  Hashtags: {', '.join(post.hashtags)}")
        print(f"  Hook: {post.hook}")
        print(f"  Engagement: {post.estimated_engagement}")
    
    return thread, post


if __name__ == "__main__":
    asyncio.run(demo())
