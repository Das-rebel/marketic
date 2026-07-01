"""
Signal Collectors

Collect market signals from various sources.
Each collector returns structured signal data.
"""

import asyncio
import feedparser
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json

try:
    import httpx
except ImportError:
    httpx = None


@dataclass
class Signal:
    """Represents a market signal."""
    signal_id: str
    source: str
    source_type: str  # reddit, twitter, trends, producthunt, rss
    title: str
    content: str
    url: str
    author: Optional[str] = None
    score: Optional[int] = None
    num_comments: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    sentiment: str = "neutral"  # positive, negative, neutral
    priority: int = 5  # 1 = highest, 5 = lowest
    engagement: int = 0
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "signal_id": self.signal_id,
            "source": self.source,
            "source_type": self.source_type,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "author": self.author,
            "score": self.score,
            "num_comments": self.num_comments,
            "tags": self.tags,
            "sentiment": self.sentiment,
            "priority": self.priority,
            "engagement": self.engagement,
            "created_at": self.created_at,
        }


class BaseCollector:
    """Base class for signal collectors."""
    
    def __init__(self, name: str):
        self.name = name
        
    async def collect(self, **kwargs) -> List[Signal]:
        raise NotImplementedError
    
    def _generate_id(self, title: str) -> str:
        """Generate a unique ID from title."""
        clean = re.sub(r'\W+', '', title.lower())[:50]
        return f"{self.name}_{clean}_{int(time.time())}"


class RedditCollector(BaseCollector):
    """
    Collect signals from Reddit communities.
    
    Usage:
        collector = RedditCollector()
        signals = await collector.collect(
            subreddits=["marketing", "growthhacking", "fintech"],
            sort="hot",  # hot, new, top
            limit=25
        )
    """
    
    def __init__(self):
        super().__init__("reddit")
        self.base_url = "https://www.reddit.com"
        
    async def collect(
        self,
        subreddits: List[str] = None,
        sort: str = "hot",
        limit: int = 25,
    ) -> List[Signal]:
        """Collect posts from specified subreddits."""
        if subreddits is None:
            subreddits = ["marketing", "growthhacking", "startups"]
        
        signals = []
        
        for subreddit in subreddits:
            try:
                url = f"{self.base_url}/r/{subreddit}/{sort}.json?limit={limit}"
                
                # Simulated collection (in production, use actual Reddit API)
                # Reddit requires authentication; use their API or scrape
                await asyncio.sleep(0.1)  # Rate limiting
                
                # For demo, create sample signals
                sample_signals = self._create_sample_signals(subreddit)
                signals.extend(sample_signals)
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit}: {e}")
        
        return signals
    
    def _create_sample_signals(self, subreddit: str) -> List[Signal]:
        """Create sample signals for demo purposes."""
        sample_data = {
            "marketing": [
                {"title": "How we scaled our ad spend 10x while cutting CPA by 60%", "content": "Detailed breakdown of our Meta ads optimization strategy", "engagement": 847},
                {"title": "The death of third-party cookies and what it means for targeting", "content": "Privacy changes are reshaping digital marketing", "engagement": 623},
                {"title": "Our AI-powered content pipeline that generates 100 posts/month", "content": "How we use GPT-4 and automation for content at scale", "engagement": 1203},
            ],
            "growthhacking": [
                {"title": "TikTok organic growth playbook: 0 to 100k followers in 60 days", "content": "Step-by-step viral content strategy that actually works", "engagement": 956},
                {"title": "Cold email playbook that books 15 demos/week", "content": "My exact templates and sequence for outbound", "engagement": 782},
            ],
        }
        
        signals = []
        for data in sample_data.get(subreddit, []):
            signal = Signal(
                signal_id=self._generate_id(data["title"]),
                source=f"r/{subreddit}",
                source_type="reddit",
                title=data["title"],
                content=data["content"],
                url=f"https://reddit.com/r/{subreddit}/placeholder",
                score=data["engagement"],
                engagement=data["engagement"],
                priority=self._calculate_priority(data["engagement"]),
                created_at=datetime.now().isoformat(),
            )
            signals.append(signal)
        
        return signals
    
    def _calculate_priority(self, engagement: int) -> int:
        """Calculate priority based on engagement."""
        if engagement > 1000:
            return 1
        elif engagement > 500:
            return 2
        elif engagement > 200:
            return 3
        elif engagement > 50:
            return 4
        return 5


class TwitterCollector(BaseCollector):
    """
    Collect signals from Twitter/X.
    
    Note: Twitter API is paid; this uses simulated data for demo.
    In production, use Twitter API v2 with proper authentication.
    """
    
    def __init__(self):
        super().__init__("twitter")
        
    async def collect(
        self,
        keywords: List[str] = None,
        users: List[str] = None,
        limit: int = 50,
    ) -> List[Signal]:
        """Collect tweets by keywords or from specific users."""
        if keywords is None:
            keywords = ["marketing", "growth", "startup", "AI"]
        if users is None:
            users = ["boringmarketer", "VibeMarketer_", "jacobrodri_"]
        
        signals = []
        
        # Simulated collection
        for keyword in keywords:
            await asyncio.sleep(0.05)
            sample = Signal(
                signal_id=self._generate_id(f"tweet_{keyword}"),
                source="twitter",
                source_type="twitter",
                title=f"Tweet about: {keyword}",
                content=f"Trending discussion about {keyword} on Twitter",
                url="https://twitter.com/placeholder",
                author="marketing_expert",
                engagement=234,
                priority=3,
                created_at=datetime.now().isoformat(),
            )
            signals.append(sample)
        
        return signals


class TrendsCollector(BaseCollector):
    """
    Collect signals from Google Trends.
    
    Usage:
        collector = TrendsCollector()
        signals = await collector.collect(
            keywords=["AI marketing", "marketing automation"],
            timeframe="today 7-d"  # today 1-m, today 3-m, today 12-m
        )
    """
    
    def __init__(self):
        super().__init__("trends")
        
    async def collect(
        self,
        keywords: List[str] = None,
        timeframe: str = "today 7-d",
        geo: str = "GLOBAL",
    ) -> List[Signal]:
        """Collect trend data for keywords."""
        if keywords is None:
            keywords = ["marketing automation", "AI tools", "fintech"]
        
        signals = []
        
        for keyword in keywords:
            await asyncio.sleep(0.05)
            
            # Simulated trend data
            signal = Signal(
                signal_id=self._generate_id(f"trend_{keyword}"),
                source="google_trends",
                source_type="trends",
                title=f"Rising trend: {keyword}",
                content=f"Search interest for '{keyword}' is rising {30}% week-over-week",
                url=f"https://trends.google.com/trends?q={keyword.replace(' ', '+')}",
                engagement=75,
                priority=2,
                created_at=datetime.now().isoformat(),
            )
            signals.append(signal)
        
        return signals


class ProductHuntCollector(BaseCollector):
    """
    Collect signals from ProductHunt launches.
    
    Usage:
        collector = ProductHuntCollector()
        signals = await collector.collect(category="marketing", days=7)
    """
    
    def __init__(self):
        super().__init__("producthunt")
        self.rss_url = "https://www.producthunt.com/feed"
        
    async def collect(
        self,
        category: str = None,
        days: int = 7,
        limit: int = 20,
    ) -> List[Signal]:
        """Collect recent ProductHunt launches."""
        signals = []
        
        # Simulated collection
        sample_launches = [
            {"name": "MarketIQ", "description": "AI-powered marketing analytics platform", "votes": 847, "category": "marketing"},
            {"name": "CopyFlow", "description": "Generate ad copy with AI in seconds", "votes": 623, "category": "marketing"},
            {"name": "LaunchPad AI", "description": "Automated GTM strategy generator", "votes": 512, "category": "saas"},
        ]
        
        for launch in sample_launches:
            signal = Signal(
                signal_id=self._generate_id(launch["name"]),
                source="producthunt",
                source_type="producthunt",
                title=f"New launch: {launch['name']}",
                content=launch["description"],
                url="https://producthunt.com/placeholder",
                score=launch["votes"],
                engagement=launch["votes"],
                priority=self._calculate_priority(launch["votes"]),
                tags=[launch["category"]],
                created_at=datetime.now().isoformat(),
            )
            signals.append(signal)
        
        return signals
    
    def _calculate_priority(self, votes: int) -> int:
        if votes > 500:
            return 1
        elif votes > 200:
            return 2
        elif votes > 100:
            return 3
        return 4


class RSSCollector(BaseCollector):
    """
    Collect signals from RSS feeds.
    
    Usage:
        collector = RSSCollector()
        signals = await collector.collect(feeds=[
            "https://marketingweek.com/feed/",
            "https://www.entrepreneur.com/latest/feed",
        ])
    """
    
    def __init__(self):
        super().__init__("rss")
        
    async def collect(
        self,
        feeds: List[str] = None,
        limit_per_feed: int = 10,
    ) -> List[Signal]:
        """Collect articles from RSS feeds."""
        if feeds is None:
            feeds = [
                "https://marketingweek.com/feed/",
                "https://www.entrepreneur.com/latest/feed",
                "https://feeds.feedburner.com/retailmenot",
            ]
        
        signals = []
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:limit_per_feed]:
                    signal = Signal(
                        signal_id=self._generate_id(entry.get("title", "")),
                        source=feed.feed.get("title", feed_url),
                        source_type="rss",
                        title=entry.get("title", ""),
                        content=entry.get("summary", "")[:500],
                        url=entry.get("link", ""),
                        author=entry.get("author", ""),
                        priority=4,
                        created_at=self._parse_date(entry),
                    )
                    signals.append(signal)
                    
            except Exception as e:
                print(f"Error parsing feed {feed_url}: {e}")
        
        return signals
    
    def _parse_date(self, entry) -> str:
        """Parse date from RSS entry."""
        if hasattr(entry, "published"):
            return entry.published
        elif hasattr(entry, "updated"):
            return entry.updated
        return datetime.now().isoformat()


async def run_full_pipeline(
    subreddits: List[str] = None,
    twitter_keywords: List[str] = None,
    trend_keywords: List[str] = None,
    rss_feeds: List[str] = None,
) -> List[Signal]:
    """Run the full signal collection pipeline."""
    
    collectors = [
        RedditCollector(),
        TwitterCollector(),
        TrendsCollector(),
        RSSCollector(),
    ]
    
    all_signals = []
    
    # Run all collectors in parallel
    tasks = [
        collectors[0].collect(subreddits=subreddits or ["marketing", "growthhacking"]),
        collectors[1].collect(keywords=twitter_keywords or ["marketing AI"]),
        collectors[2].collect(keywords=trend_keywords or ["marketing automation"]),
        collectors[3].collect(feeds=rss_feeds),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            print(f"Collector error: {result}")
        else:
            all_signals.extend(result)
    
    # Sort by priority (1 = highest)
    all_signals.sort(key=lambda s: s.priority)
    
    return all_signals


if __name__ == "__main__":
    async def test():
        print("Testing Signal Collectors...")
        
        # Test individual collectors
        print("\n1. Reddit Collector:")
        reddit = RedditCollector()
        signals = await reddit.collect(subreddits=["marketing"])
        print(f"   Collected {len(signals)} signals")
        
        print("\n2. Twitter Collector:")
        twitter = TwitterCollector()
        signals = await twitter.collect(keywords=["marketing automation"])
        print(f"   Collected {len(signals)} signals")
        
        print("\n3. Trends Collector:")
        trends = TrendsCollector()
        signals = await trends.collect(keywords=["AI marketing"])
        print(f"   Collected {len(signals)} signals")
        
        print("\n4. RSS Collector:")
        rss = RSSCollector()
        signals = await rss.collect()
        print(f"   Collected {len(signals)} signals")
        
        print("\n5. Full Pipeline:")
        all_signals = await run_full_pipeline()
        print(f"   Total signals collected: {len(all_signals)}")
        
        # Show top signals
        print("\nTop 5 Priority Signals:")
        for signal in all_signals[:5]:
            print(f"   [{signal.priority}] {signal.source}: {signal.title[:50]}...")
    
    asyncio.run(test())
