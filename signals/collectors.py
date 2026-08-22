"""
Signal Collectors — Marketing signals from Product Hunt, Hacker News, Twitter, Reddit.
"""

import os
import re
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MarketingSignal:
    source: str
    signal_type: str
    title: str
    url: str
    engagement_score: float
    sentiment: str  # positive, neutral, negative
    topics: List[str]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProductHuntCollector:
    """Collect signals from Product Hunt."""

    def __init__(self):
        self._api_key = os.environ.get("PRODUCT_HUNT_API_KEY")

    async def collect(self, limit: int = 50) -> List[MarketingSignal]:
        """Collect trending products on Product Hunt."""
        
        signals = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Product Hunt GraphQL API
                query = """
                query GetTrending {
                    posts(first: %d, order: POPULAR) {
                        edges {
                            node {
                                name
                                tagline
                                url
                                votesCount
                                commentsCount
                                topics {
                                    edges {
                                        node {
                                            name
                                        }
                                    }
                                }
                                createdAt
                            }
                        }
                    }
                }
                """ % limit
                
                if self._api_key:
                    resp = await client.post(
                        "https://api.producthunt.com/v2/api/graphql",
                        headers={
                            "Authorization": f"Bearer {self._api_key}",
                            "Content-Type": "application/json",
                        },
                        json={"query": query}
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        for edge in data.get("data", {}).get("posts", {}).get("edges", []):
                            node = edge["node"]
                            topics = [e["node"]["name"] for e in node.get("topics", {}).get("edges", [])]
                            
                            signals.append(MarketingSignal(
                                source="product_hunt",
                                signal_type="launch",
                                title=f"{node['name']}: {node['tagline']}",
                                url=node["url"],
                                engagement_score=node["votesCount"] + node["commentsCount"] * 2,
                                sentiment="positive",
                                topics=topics,
                                timestamp=node["createdAt"],
                                metadata={
                                    "votes": node["votesCount"],
                                    "comments": node["commentsCount"],
                                }
                            ))
        except Exception as e:
            print(f"Product Hunt error: {e}")
        
        # If no API, return placeholder
        if not signals:
            signals.append(MarketingSignal(
                source="product_hunt",
                signal_type="launch",
                title="[Product Hunt API requires authentication]",
                url="https://producthunt.com",
                engagement_score=0,
                sentiment="neutral",
                topics=["saas", "startup"],
                timestamp=datetime.utcnow().isoformat(),
            ))
        
        return signals


class TrendsCollector:
    """Collect trend signals (simplified Hacker News, tech trends)."""

    async def collect(self, limit: int = 50) -> List[MarketingSignal]:
        """Collect trending topics and discussions."""
        
        signals = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    "https://hacker-news.firebaseio.com/v0/topstories.json"
                )
                
                if resp.status_code == 200:
                    story_ids = resp.json()[:limit]
                    
                    for story_id in story_ids:
                        story_resp = await client.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                        )
                        
                        if story_resp.status_code == 200:
                            story = story_resp.json()
                            
                            if story.get("title"):
                                signals.append(MarketingSignal(
                                    source="hacker_news",
                                    signal_type="discussion",
                                    title=story["title"],
                                    url=f"https://news.ycombinator.com/item?id={story_id}",
                                    engagement_score=story.get("score", 0),
                                    sentiment="neutral",
                                    topics=self._extract_topics(story.get("title", "")),
                                    timestamp=datetime.fromtimestamp(story.get("time", 0)).isoformat() if story.get("time") else "",
                                    metadata={
                                        "score": story.get("score", 0),
                                        "comments": story.get("descendants", 0),
                                    }
                                ))
        except Exception as e:
            print(f"Trends collector error: {e}")
        
        return signals[:limit]

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text."""
        tech_topics = [
            "ai", "ml", "machine learning", "startup", "saas", "crypto", "web3",
            "blockchain", "cloud", "devops", "security", "privacy", "open source",
            "programming", "developer", "api", "database", "frontend", "backend",
        ]
        text_lower = text.lower()
        found = [t for t in tech_topics if t in text_lower]
        return found[:3] if found else ["general"]


class TwitterCollector:
    """Collect signals from Twitter/X."""

    def __init__(self):
        self._api_key = os.environ.get("TWITTER_API_KEY")

    async def collect(self, limit: int = 50) -> List[MarketingSignal]:
        """Collect trending or mentioned brands on Twitter."""
        
        # Would use Twitter API v2 in production
        # For now, return placeholder
        
        return [
            MarketingSignal(
                source="twitter",
                signal_type="mention",
                title="[Twitter API requires OAuth 2.0 authentication]",
                url="https://twitter.com",
                engagement_score=0,
                sentiment="neutral",
                topics=["social media", "branding"],
                timestamp=datetime.utcnow().isoformat(),
            )
        ]


class RedditCollector:
    """Collect signals from Reddit."""

    def __init__(self):
        self._api_key = os.environ.get("REDDIT_API_KEY")

    async def collect(self, limit: int = 50) -> List[MarketingSignal]:
        """Collect trending discussions from Reddit."""
        
        signals = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Popular posts from major marketing subreddits
                subreddits = ["marketing", "entrepreneur", "startups", "smallbusiness"]
                
                for subreddit in subreddits:
                    try:
                        resp = await client.get(
                            f"https://www.reddit.com/r/{subreddit}/hot.json",
                            params={"limit": limit // len(subreddits)},
                            headers={"User-Agent": "Marketic/1.0"},
                        )
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            for post in data.get("data", {}).get("children", []):
                                p = post["data"]
                                
                                signals.append(MarketingSignal(
                                    source="reddit",
                                    signal_type="discussion",
                                    title=p["title"],
                                    url=f"https://reddit.com{p['permalink']}",
                                    engagement_score=p.get("score", 0) + p.get("num_comments", 0),
                                    sentiment="neutral",
                                    topics=[subreddit],
                                    timestamp=datetime.fromtimestamp(p.get("created_utc", 0)).isoformat(),
                                    metadata={
                                        "subreddit": subreddit,
                                        "score": p.get("score", 0),
                                        "comments": p.get("num_comments", 0),
                                    }
                                ))
                    except Exception:
                        continue
        except Exception as e:
            print(f"Reddit error: {e}")
        
        return signals[:limit]


class G2Collector:
    """Collect signals from G2 (review platform)."""

    async def collect(self, limit: int = 50) -> List[MarketingSignal]:
        """Collect product reviews and ratings from G2."""
        
        return [
            MarketingSignal(
                source="g2",
                signal_type="review",
                title="[G2 API requires enterprise authentication]",
                url="https://g2.com",
                engagement_score=0,
                sentiment="neutral",
                topics=["reviews", "saas"],
                timestamp=datetime.utcnow().isoformat(),
            )
        ]


class TrustpilotCollector:
    """Collect signals from Trustpilot."""

    async def collect(self, limit: int = 50) -> List[MarketingSignal]:
        """Collect reviews from Trustpilot."""
        
        return [
            MarketingSignal(
                source="trustpilot",
                signal_type="review",
                title="[Trustpilot API requires business account]",
                url="https://trustpilot.com",
                engagement_score=0,
                sentiment="neutral",
                topics=["reviews", "customer satisfaction"],
                timestamp=datetime.utcnow().isoformat(),
            )
        ]


def aggregate_signals(all_signals: List[MarketingSignal]) -> Dict[str, Any]:
    """Aggregate signals across sources."""
    
    if not all_signals:
        return {
            "total_signals": 0,
            "by_source": {},
            "by_type": {},
            "top_topics": [],
            "avg_sentiment": "neutral",
        }
    
    # Count by source
    by_source = {}
    for s in all_signals:
        by_source[s.source] = by_source.get(s.source, 0) + 1
    
    # Count by type
    by_type = {}
    for s in all_signals:
        by_type[s.signal_type] = by_type.get(s.signal_type, 0) + 1
    
    # Top topics
    topic_counts = {}
    for s in all_signals:
        for topic in s.topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Sentiment distribution
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for s in all_signals:
        sentiment_counts[s.sentiment] = sentiment_counts.get(s.sentiment, 0) + 1
    
    avg_sentiment = "neutral"
    if sentiment_counts["positive"] > sentiment_counts["neutral"] * 1.5:
        avg_sentiment = "positive"
    elif sentiment_counts["negative"] > sentiment_counts["neutral"]:
        avg_sentiment = "negative"
    
    return {
        "total_signals": len(all_signals),
        "by_source": by_source,
        "by_type": by_type,
        "top_topics": top_topics,
        "avg_sentiment": avg_sentiment,
        "sentiment_breakdown": sentiment_counts,
        "top_signals": sorted(all_signals, key=lambda x: x.engagement_score, reverse=True)[:10],
    }
