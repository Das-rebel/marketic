"""
Social Generator — Platform-specific social media content.
"""

import os
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import re


class SocialPlatform(str, Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


class ContentFormat(str, Enum):
    SINGLE_POST = "single_post"
    THREAD = "thread"
    CAROUSEL = "carousel"
    STORY = "story"


class ToneStyle(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    WITTY = "witty"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"


@dataclass
class SocialPost:
    post_id: str
    platform: str
    content: str
    hashtags: List[str] = field(default_factory=list)
    media_suggestions: List[str] = field(default_factory=list)
    engagement_prediction: Dict[str, float] = field(default_factory=dict)
    best_posting_time: str = ""
    character_count: int = 0


@dataclass
class SocialContentRequest:
    topic: str
    platform: SocialPlatform = SocialPlatform.LINKEDIN
    format: ContentFormat = ContentFormat.SINGLE_POST
    tone: str = "professional"
    num_options: int = 3
    thread_length: int = 5
    include_hashtags: bool = True


# Platform-specific constraints
PLATFORM_LIMITS = {
    SocialPlatform.LINKEDIN: {
        "post_length": 3000,
        "hashtag_limit": 5,
        "ideal_length": (1300, 2100),
    },
    SocialPlatform.TWITTER: {
        "post_length": 280,
        "hashtag_limit": 3,
        "ideal_length": (200, 260),
    },
    SocialPlatform.INSTAGRAM: {
        "post_length": 2200,
        "hashtag_limit": 30,
        "ideal_length": (1250, 2000),
    },
    SocialPlatform.FACEBOOK: {
        "post_length": 63206,
        "hashtag_limit": 3,
        "ideal_length": (500, 1500),
    },
}


class SocialGenerator:
    """Generate platform-specific social media content."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def generate(self, request: SocialContentRequest) -> List[SocialPost]:
        """Generate social media content."""
        
        posts = []
        
        if request.format == ContentFormat.THREAD:
            posts = await self._generate_thread(request)
        elif request.format == ContentFormat.CAROUSEL:
            posts = await self._generate_carousel(request)
        else:
            posts = await self._generate_single(request)
        
        # Score and rank
        for post in posts:
            self._score_post(post, request)
        
        return posts

    async def _generate_single(self, request: SocialContentRequest) -> List[SocialPost]:
        """Generate single posts."""
        import uuid
        
        prompt = self._build_single_prompt(request)
        model = self._select_model(request.platform)
        content = await self._call_model(model, prompt)
        
        posts = []
        
        # Parse into individual posts
        sections = re.split(r'(?:---\s*post\s*---|variant\s*\d+[:\.]|post\s*\d+[:\.])', 
                          content, flags=re.IGNORECASE)
        
        for i, section in enumerate(sections):
            if len(section.strip()) < 20:
                continue
            
            # Extract hashtags
            hashtags = re.findall(r'#\w+', section)
            
            # Extract content (remove hashtags for main content)
            main_content = re.sub(r'#\w+', '', section).strip()
            
            posts.append(SocialPost(
                post_id=str(uuid.uuid4())[:8],
                platform=request.platform.value,
                content=main_content,
                hashtags=hashtags[:PLATFORM_LIMITS[request.platform]["hashtag_limit"]],
                character_count=len(main_content),
            ))
        
        # Ensure we have at least num_options
        while len(posts) < request.num_options:
            posts.append(SocialPost(
                post_id=str(uuid.uuid4())[:8],
                platform=request.platform.value,
                content=self._fallback_post(request),
                hashtags=["#" + request.topic.replace(" ", "")] if request.include_hashtags else [],
                character_count=len(self._fallback_post(request)),
            ))
        
        return posts[:request.num_options]

    async def _generate_thread(self, request: SocialContentRequest) -> List[SocialPost]:
        """Generate a Twitter/LinkedIn thread."""
        import uuid
        
        prompt = self._build_thread_prompt(request)
        model = self._select_model(request.platform)
        content = await self._call_model(model, prompt)
        
        # Parse thread tweets
        lines = content.split('\n')
        thread_posts = []
        
        tweet_num = 0
        current_tweet = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Thread numbering: "1/" "2/" etc or just numbered lines
            thread_match = re.match(r'^(\d+)/\s*(.*)', line)
            if thread_match:
                if current_tweet:
                    thread_posts.append(SocialPost(
                        post_id=str(uuid.uuid4())[:8],
                        platform=request.platform.value,
                        content=current_tweet.strip(),
                        hashtags=[],
                        character_count=len(current_tweet),
                    ))
                tweet_num = int(thread_match.group(1))
                current_tweet = thread_match.group(2)
            elif line.startswith('- ') or line.startswith('• '):
                # Bullet points as tweets
                if current_tweet:
                    thread_posts.append(SocialPost(
                        post_id=str(uuid.uuid4())[:8],
                        platform=request.platform.value,
                        content=current_tweet.strip(),
                        hashtags=[],
                        character_count=len(current_tweet),
                    ))
                current_tweet = line[2:]
            else:
                current_tweet += " " + line
            
            # Check length limit
            if len(current_tweet) > PLATFORM_LIMITS[SocialPlatform.TWITTER]["post_length"]:
                if current_tweet:
                    thread_posts.append(SocialPost(
                        post_id=str(uuid.uuid4())[:8],
                        platform=request.platform.value,
                        content=current_tweet.strip(),
                        hashtags=[],
                        character_count=len(current_tweet),
                    ))
                current_tweet = ""
        
        # Add last tweet
        if current_tweet.strip():
            thread_posts.append(SocialPost(
                post_id=str(uuid.uuid4())[:8],
                platform=request.platform.value,
                content=current_tweet.strip(),
                hashtags=[],
                character_count=len(current_tweet),
            ))
        
        # Ensure minimum thread length
        while len(thread_posts) < request.thread_length:
            thread_posts.append(SocialPost(
                post_id=str(uuid.uuid4())[:8],
                platform=request.platform.value,
                content=f"({len(thread_posts) + 1}/{request.thread_length}) More insights coming soon...",
                hashtags=[],
                character_count=len(thread_posts[-1].content) if thread_posts else 100,
            ))
        
        return thread_posts[:request.thread_length]

    async def _generate_carousel(self, request: SocialContentRequest) -> List[SocialPost]:
        """Generate carousel post (multiple slides as separate posts)."""
        import uuid
        
        prompt = self._build_carousel_prompt(request)
        model = self._select_model(request.platform)
        content = await self._call_model(model, prompt)
        
        # Parse slides
        slides = re.split(r'(?:slide\s*\d+[:\.]|---\s*slide\s*---|===)', content, flags=re.IGNORECASE)
        
        posts = []
        for i, slide in enumerate(slides):
            if len(slide.strip()) < 10:
                continue
            
            hashtags = re.findall(r'#\w+', slide) if request.include_hashtags else []
            main_content = re.sub(r'#\w+', '', slide).strip()
            
            posts.append(SocialPost(
                post_id=str(uuid.uuid4())[:8],
                platform=request.platform.value,
                content=f"Slide {i+1}: {main_content}",
                hashtags=hashtags,
                media_suggestions=[f"Create visual slide {i+1} matching the content"],
                character_count=len(main_content),
            ))
        
        # Default carousel
        if not posts:
            posts = [
                SocialPost(
                    post_id=str(uuid.uuid4())[:8],
                    platform=request.platform.value,
                    content=f"Slide {i+1}: {request.topic}",
                    hashtags=["#" + request.topic.replace(" ", "")] if request.include_hashtags else [],
                    character_count=len(request.topic),
                )
                for i in range(5)
            ]
        
        return posts

    def _build_single_prompt(self, request: SocialContentRequest) -> str:
        """Build prompt for single post generation."""
        limits = PLATFORM_LIMITS[request.platform]
        ideal = limits["ideal_length"]
        
        tone_map = {
            "professional": "insightful, value-driven, authority-building",
            "casual": "conversational, friendly, relatable",
            "witty": "clever, humorous, attention-grabbing",
            "inspirational": "motivating, uplifting, story-driven",
            "educational": "informative, teaching, how-to focused",
        }
        tone = tone_map.get(request.tone, tone_map["professional"])
        
        hashtag_tip = f"Include up to {limits['hashtag_limit']} relevant hashtags" if request.include_hashtags else "Do NOT include hashtags"
        
        prompt = f"""Generate {request.num_options} unique social media posts for {request.platform.value}.

TOPIC: {request.topic}
TONE: {tone}
PLATFORM: {request.platform.value}
{hashtag_tip}

CHARACTER LIMITS:
- Max length: {limits['post_length']} chars
- Ideal length: {ideal[0]}-{ideal[1]} chars

FORMAT: Create each post clearly separated. Include:
1. Main content (within character limit)
2. Hashtags at the end (if enabled)
3. A brief note about what visual would accompany this post

Vary your approaches:
- Post 1: Hook with a bold statement or question
- Post 2: Share a counterintuitive insight
- Post 3: Use a compelling story angle
- (more with different angles)

Make each post scroll-stopping and encourage engagement."""
        
        return prompt

    def _build_thread_prompt(self, request: SocialContentRequest) -> str:
        """Build prompt for thread generation."""
        thread_length = max(request.thread_length, 5)
        
        prompt = f"""Generate a {thread_length}-tweet thread on: {request.topic}

PLATFORM: {request.platform.value}
TONE: {request.tone}

FORMAT:
- Start each tweet with "1/", "2/", etc.
- Each tweet should be self-contained but build on the previous
- Make tweet 1 a HOOK that stops the scroll
- Make the last tweet a CTA or summary

TWEET LENGTH: Max {PLATFORM_LIMITS[SocialPlatform.TWITTER]['post_length']} chars each

Example structure:
1/ The biggest mistake in [topic] isn't what you think...
2/ Most people focus on X, but they should actually...
3/ Here's what the research shows...
...

Generate the full {thread_length}-tweet thread:"""
        
        return prompt

    def _build_carousel_prompt(self, request: SocialContentRequest) -> str:
        """Build prompt for carousel generation."""
        prompt = f"""Generate a carousel post concept for {request.platform.value}.

TOPIC: {request.topic}
IDEAL SLIDES: 5-7 slides

FORMAT:
- Title slide (hook)
- Problem/Context slide
- 2-4 insight slides
- Conclusion/CTA slide

For each slide provide:
- What the VISUAL should show
- The TEXT that goes on the slide
- Keep text minimal (5-10 words per slide)

Generate the carousel concept:"""
        
        return prompt

    def _select_model(self, platform: SocialPlatform) -> str:
        """Select appropriate model for the platform."""
        model_map = {
            SocialPlatform.LINKEDIN: "stealth/ox-alpha",
            SocialPlatform.TWITTER: "deepseek/deepseek-v4-flash",
            SocialPlatform.INSTAGRAM: "google/gemini-3.6-flash",
            SocialPlatform.FACEBOOK: "google/gemini-3.6-flash",
        }
        return model_map.get(platform, "google/gemini-3.6-flash")

    async def _call_model(self, model: str, prompt: str) -> str:
        """Call AI model."""
        if model.startswith("stealth/"):
            return await self._call_openrouter(model, prompt)
        elif model.startswith(("google/", "qwen/", "deepseek/")):
            return await self._call_openrouter(model, prompt)
        elif model.startswith("minimax/"):
            return await self._call_opencode_go(model, prompt)
        else:
            return await self._call_openai_fallback(prompt)

    async def _call_openrouter(self, model: str, prompt: str) -> str:
        """Call OpenRouter API."""
        if not self._openrouter_key:
            return await self._call_openai_fallback(prompt)
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self._openrouter_key}"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2500
                    }
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter error: {e}")
        
        return await self._call_openai_fallback(prompt)

    async def _call_opencode_go(self, model: str, prompt: str) -> str:
        """Call OpenCode Go API."""
        if not self._opencode_key:
            return await self._call_openai_fallback(prompt)
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://opencode.ai/zen/go/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self._opencode_key}"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2500
                    }
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenCode Go error: {e}")
        
        return await self._call_openai_fallback(prompt)

    async def _call_openai_fallback(self, prompt: str) -> str:
        """Fallback to OpenAI API."""
        if not self._openai_key:
            return self._fallback_content()
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self._openai_key)
            
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500
            )
            
            return resp.choices[0].message.content
        except Exception as e:
            print(f"OpenAI fallback error: {e}")
            return self._fallback_content()

    def _score_post(self, post: SocialPost, request: SocialContentRequest):
        """Score post engagement prediction."""
        limits = PLATFORM_LIMITS[request.platform]
        
        # Base engagement score
        base_engagement = 0.05
        
        # Length optimization
        ideal = limits["ideal_length"]
        if ideal[0] <= post.character_count <= ideal[1]:
            base_engagement += 0.02
        
        # Hashtag optimization
        if request.include_hashtags and 1 <= len(post.hashtags) <= limits["hashtag_limit"]:
            base_engagement += 0.01
        
        # Platform-specific adjustments
        if request.platform == SocialPlatform.LINKEDIN:
            if any(word in post.content.lower() for word in ['research', 'study', 'data', 'insight']):
                base_engagement += 0.02
        elif request.platform == SocialPlatform.TWITTER:
            if len(post.content) <= 200:
                base_engagement += 0.015
        
        post.engagement_prediction = {
            "likes": round(base_engagement * 100, 1),
            "comments": round(base_engagement * 10, 1),
            "shares": round(base_engagement * 5, 1),
            "estimated_reach": round(base_engagement * 1000, 0),
        }
        
        # Best posting time (simplified)
        time_map = {
            SocialPlatform.LINKEDIN: "Tuesday-Thursday, 8-10am or 5-6pm",
            SocialPlatform.TWITTER: "Monday-Wednesday, 8-9am or 12-1pm",
            SocialPlatform.INSTAGRAM: "Tuesday, 11am-1pm or 7-9pm",
            SocialPlatform.FACEBOOK: "Wednesday, 1-4pm",
        }
        post.best_posting_time = time_map.get(request.platform, "Weekdays, 10am-2pm")

    def _fallback_post(self, request: SocialContentRequest) -> str:
        """Generate fallback post content."""
        return f"Exploring {request.topic}: Here's what every marketer needs to know in 2024."

    def _fallback_content(self) -> str:
        """Fallback content when API is unavailable."""
        return """Post 1:
Hook your audience with a bold statement about the topic.
#Marketing #Growth #Strategy

Post 2:
Share a counterintuitive insight that challenges conventional thinking.
#ThoughtLeadership #Innovation

Post 3:
Tell a story that connects with your audience's struggles and aspirations.
#Storytelling #BrandBuilding"""
