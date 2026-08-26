"""
Signal Collectors — Marketing signals from Product Hunt, Hacker News, Twitter, Reddit.
"""

import os
import re
import json
import shutil
import time as _time
from urllib.parse import quote_plus
import httpx
try:
    import feedparser
except ImportError:  # pragma: no cover - feedparser is a declared dep
    feedparser = None
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


class TikTokCollector:
    """Collect content signals from TikTok via yt-dlp metadata extraction.

    Pragmatic approach (TikTok's search API is unauthenticated/unreliable):
    - If the query looks like a URL or profile, use it directly.
    - Otherwise treat it as a hashtag: https://www.tiktok.com/tag/<query>
    Runs `yt-dlp --skip-download -J <url>` via asyncio subprocess, parses the
    JSON stdout for title/description/upload_date/view_count, and maps into
    MarketingSignal entries with hashtags as topics.

    Degradation paths:
    - yt-dlp binary missing -> [] immediately
    - any subprocess/parse failure -> []
    """

    def __init__(self, timeout_seconds: float = 120.0):
        self._timeout = timeout_seconds

    async def collect(self, limit: int = 50, query: str = "") -> List[MarketingSignal]:
        # Graceful degradation 1: yt-dlp not installed
        if shutil.which("yt-dlp") is None:
            return []
        if not query:
            return []

        try:
            target = self._resolve_target(query)
            proc = await _asyncio.create_subprocess_exec(
                "yt-dlp", "--flat-playlist", "--skip-download", "-J",
                "--playlist-end", str(limit), target,
                stdout=_asyncio.subprocess.PIPE,
                stderr=_asyncio.subprocess.DEVNULL,
            )
            try:
                stdout, _ = await _asyncio.wait_for(proc.communicate(), timeout=self._timeout)
            except _asyncio.TimeoutError:
                proc.kill()
                return []
            if proc.returncode != 0 or not stdout:
                return []
            data = json.loads(stdout.decode("utf-8", errors="replace"))
            return self._map_entries(data, limit)
        except Exception:
            # Graceful degradation 2: any failure (network, parse, tiktok block)
            return []

    @staticmethod
    def _resolve_target(query: str) -> str:
        q = query.strip()
        if q.startswith("http://") or q.startswith("https://"):
            return q
        # bare handle (@user), hashtag (#tag) or plain keyword -> tag page
        tag = q.lstrip("@#")
        return f"https://www.tiktok.com/tag/{tag}"

    def _map_entries(self, data: Dict[str, Any], limit: int) -> List[MarketingSignal]:
        signals: List[MarketingSignal] = []
        entries = data.get("entries") or ([data] if data.get("id") else [])
        for entry in entries[:limit]:
            if not isinstance(entry, dict):
                continue
            title = entry.get("title") or entry.get("description") or "(untitled)"
            description = entry.get("description") or ""
            views = entry.get("view_count") or 0
            timestamp = ""
            upload_date = entry.get("upload_date")  # yyyymmdd
            if upload_date:
                try:
                    timestamp = datetime.strptime(upload_date, "%Y%m%d").isoformat()
                except ValueError:
                    pass
            url = entry.get("url") or entry.get("webpage_url") or ""
            signals.append(MarketingSignal(
                source="tiktok",
                signal_type="content",
                title=title[:200],
                url=url,
                engagement_score=float(views),
                sentiment="neutral",
                topics=self._extract_hashtags(description) or ["tiktok"],
                timestamp=timestamp,
                metadata={
                    "view_count": views,
                    "like_count": entry.get("like_count"),
                    "comment_count": entry.get("comment_count"),
                    "uploader": entry.get("uploader") or entry.get("channel"),
                    "duration": entry.get("duration"),
                },
            ))
        return signals

    @staticmethod
    def _extract_hashtags(text: str) -> List[str]:
        tags = re.findall(r"#([\w\u00c0-\uffff]+)", text or "")
        seen: List[str] = []
        for t in tags:
            t_low = t.lower()
            if t_low not in seen:
                seen.append(t_low)
        return seen[:5]


class GoogleTrendsCollector:
    """Rising Google searches in India via pytrends.

    Graceful degradation:
    - pytrends not installed -> []
    - network / rate-limit (429) / parse failure -> []
    """

    def __init__(self):
        try:
            from pytrends.request import TrendReq  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False

    async def collect(self, limit: int = 50, query: str = "") -> List[MarketingSignal]:
        if not self._available:
            return []
        signals = []
        try:
            # pytrends is blocking — run in a thread so we don't stall the loop
            import asyncio
            def _fetch():
                import time
                # Google rate-limits related_queries hard (429) — retry w/ backoff
                last_exc = None
                for attempt in range(3):
                    try:
                        pt = TrendReq(
                            hl="en-IN", geo="IN", timeout=(5, 15),
                            custom_useragent="marketic/2.0 (signals collector)",
                        )
                        kw = query or "marketing"
                        pt.build_payload([kw], timeframe="now 7-d", geo="IN")
                        return pt.related_queries()[kw].get("rising")
                    except Exception as exc:
                        last_exc = exc
                        if "429" in str(exc) or "TooMany" in type(exc).__name__:
                            time.sleep([8, 20, 40][attempt])
                            continue
                        raise
                raise last_exc
            df = await asyncio.get_event_loop().run_in_executor(None, _fetch)
            if df is None or df.empty:
                return []
            for _, row in df.head(10).iterrows():
                q = str(row.get("query", ""))
                v = float(row.get("value", 0) or 0)
                if not q:
                    continue
                signals.append(MarketingSignal(
                    source="google_trends",
                    signal_type="search_trend",
                    title=f"Rising search: {q}",
                    url=f"https://trends.google.com/trends/explore?q={quote_plus(q)}&geo=IN",
                    engagement_score=min(v, 100) * 10,
                    sentiment="neutral",
                    topics=[q],
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={"rise_value": v},
                ))
        except Exception:
            # rate limits (429), network errors, parse errors -> degrade silently
            return []
        return signals[:10]


class IndianMediaRSSCollector:
    """Indian marketing/business media via RSS feeds (ET Brand Equity, Afaqs,
    YourStory, Inc42, Mint Marketing).

    Dead feeds are skipped silently. Responses cached in-memory class-level
    for 30 minutes so hourly briefings don't re-fetch.
    """

    FEEDS = {
        "ET Brand Equity": "https://brandequity.economictimes.indiatimes.com/rss/topstories",
        "Afaqs": "https://www.afaqs.com/rss/afaqs/news rss",
        "YourStory": "https://yourstory.com/feed",
        "Inc42": "https://inc42.com/feed/",
        "Mint Marketing": "https://www.livemint.com/rss/marketing",
    }

    CACHE_TTL_SECONDS = 30 * 60
    _cache: Dict[str, tuple] = {}  # feed_url -> (fetched_at_monotonic, entries)

    async def collect(self, limit: int = 50, query: str = "") -> List[MarketingSignal]:
        if feedparser is None:
            return []
        import asyncio

        def _parse(url: str):
            return feedparser.parse(url)

        all_entries = []
        alive = []
        for name, url in self.FEEDS.items():
            try:
                cached = self._cache.get(url)
                now = _time.monotonic()
                if cached and (now - cached[0]) < self.CACHE_TTL_SECONDS:
                    entries = cached[1]
                else:
                    parsed = await asyncio.get_event_loop().run_in_executor(
                        None, _parse, url)
                    entries = list(parsed.entries or [])
                    self._cache[url] = (now, entries)
                if entries:
                    alive.append(name)
                    all_entries.extend(entries)
            except Exception:
                continue  # skip dead feeds silently

        if query:
            ql = query.lower()
            filtered = [e for e in all_entries
                        if any(ql in t.lower() for t in self._entry_topics(e))
                        or ql in (e.get("title", "") or "").lower()]
            selected = filtered if filtered else sorted(all_entries, key=self._entry_ts, reverse=True)[:limit]
        else:
            selected = sorted(all_entries, key=self._entry_ts, reverse=True)[:limit]

        signals = []
        for e in selected[:limit]:
            title = (e.get("title") or "").strip()
            if not title:
                continue
            signals.append(MarketingSignal(
                source="indian_media",
                signal_type="news",
                title=title,
                url=e.get("link") or "",
                engagement_score=50.0,  # baseline — RSS has no engagement metric
                sentiment="neutral",
                topics=self._entry_topics(e) or ["india_marketing"],
                timestamp=self._entry_ts(e),
                metadata={},
            ))
        self.last_alive_feeds = alive
        return signals

    @staticmethod
    def _entry_topics(entry) -> List[str]:
        tags = entry.get("tags") or []
        return [t.get("term", "").lower() for t in tags if t.get("term")][:3]

    @staticmethod
    def _entry_ts(entry) -> str:
        for key in ("published", "updated"):
            val = entry.get(key)
            if val:
                return val
        return ""


class YouTubeTrendingCollector:
    """Top-viewed YouTube videos this week matching a query, via yt-dlp.

    Degradation paths:
    - yt-dlp binary missing -> [] immediately
    - subprocess/network/parse failure -> []
    """

    TIMEOUT_SECONDS = 120.0

    async def collect(self, limit: int = 50, query: str = "") -> List[MarketingSignal]:
        if shutil.which("yt-dlp") is None:
            return []
        if not query:
            return []
        search_url = ("https://www.youtube.com/results?search_query="
                      f"{quote_plus(query)}&sp=CAMSAhAB")  # this week + view sort
        try:
            proc = await _asyncio.create_subprocess_exec(
                "yt-dlp", "--flat-playlist", "--dump-json",
                "--playlist-end", "40", search_url,
                stdout=_asyncio.subprocess.PIPE,
                stderr=_asyncio.subprocess.DEVNULL,
            )
            try:
                stdout, _ = await _asyncio.wait_for(
                    proc.communicate(), timeout=self.TIMEOUT_SECONDS)
            except _asyncio.TimeoutError:
                proc.kill()
                return []
            if proc.returncode != 0 or not stdout:
                return []
            entries = []
            for line in stdout.decode("utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            entries.sort(key=lambda e: e.get("view_count") or 0, reverse=True)
            signals = []
            for e in entries[:8]:
                views = e.get("view_count") or 0
                desc = e.get("description") or ""
                hashtags = [t.lower() for t in re.findall(r"#(\w+)", desc)][:5]
                signals.append(MarketingSignal(
                    source="youtube",
                    signal_type="video",
                    title=(e.get("title") or "(untitled)")[:200],
                    url=e.get("url") or e.get("webpage_url") or "",
                    engagement_score=min(views / 1000, 5000),
                    sentiment="neutral",
                    topics=hashtags or ["youtube"],
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={"view_count": views,
                              "uploader": e.get("uploader")},
                ))
            return signals
        except Exception:
            return []


# ─── Hinglish query expansion ──────────────────────────────────────────────────

HINGLISH_MAP = {
    "best": ["sabse acha", "top"],
    "cheap": ["sasta"],
    "affordable": ["budget", "sasta"],
    "review": ["honest review"],
    "skincare": ["skin care hindi"],
    "haircare": ["hair care hindi"],
    "makeup": ["makeup hindi", "shaadi makeup"],
    "fitness": ["gym hindi", "weight loss desi"],
    "diet": ["diet plan indian"],
    "phone": ["mobile", "smartphone under budget"],
    "laptop": ["laptop under budget"],
    "car": ["gaadi", "car mileage"],
    "bike": ["bike mileage"],
    "loan": ["loan bina documents", "emi"],
    "insurance": ["insurance hindi", "policy kaise"],
    "invest": ["paisa invest", "mutual fund hindi"],
    "save money": ["paisa bachao", "bachat"],
    "shopping": ["online shopping offer", "sale india"],
    "recipe": ["recipe hindi", "ghar ka khana"],
    "travel": ["ghumne", "budget trip india"],
    "education": ["padhai", "coaching"],
    "job": ["naukri", "sarkari naukri"],
    "startup": ["business idea hindi"],
    "marketing": ["digital marketing hindi"],
}


def expand_hinglish(query: str) -> List[str]:
    """Broaden an English marketing query with common Hinglish variants.

    Returns [query] + mapped variants + generic India suffixes, capped at 8.
    Used by callers to broaden X/YouTube searches for Indian audiences.
    """
    q = (query or "").strip()
    variants = [q] if q else []
    ql = q.lower()
    for term, alts in HINGLISH_MAP.items():
        if re.search(rf"\b{re.escape(term)}\b", ql):
            variants.extend(alts)
    suffixes = [f"{q} in india", f"{q} india"] if q else []
    variants.extend(suffixes)
    seen, out = set(), []
    for v in variants:
        vl = v.lower()
        if vl not in seen:
            seen.add(vl)
            out.append(v)
    return out[:8]


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


# ─── Parallel Fan-Out (last30days-skill pattern) ──────────────────────────────
# Vault-sourced: github.com/mvanhorn/last30days-skill — search all sources in
# parallel, score by REAL engagement, synthesize into ONE brief.

import asyncio as _asyncio


class PolymarketCollector:
    """Prediction-market implied demand. Unique signal: real money on real outcomes.

    Vault-sourced calibration (@sterlingcrispin 'Nothing Ever Happens' bot):
    ~73.4% of ALL Polymarket markets resolve "No" — raw volume massively
    overweights long-shot sensationalism. We therefore score:
        effective_volume = volume x implied_probability_of_YES
    so a $1M market at 8% Yes ranks below a $200K market at 70% Yes.
    """

    async def collect(self, limit: int = 50, query: str = "") -> List[MarketingSignal]:
        signals = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Gamma API — public markets data
                resp = await client.get(
                    "https://gamma-api.polymarket.com/events",
                    params={"limit": limit, "active": "true", "closed": "false",
                            **({"search": query} if query else {})},
                )
                if resp.status_code == 200:
                    for ev in resp.json()[:limit]:
                        volume = float(ev.get("volume", 0) or 0)
                        markets = ev.get("markets") or []
                        yes_prob = self._implied_yes_probability(markets)
                        effective = volume * yes_prob
                        signals.append(MarketingSignal(
                            source="polymarket",
                            signal_type="prediction_market",
                            title=ev.get("title", ""),
                            url=ev.get("slug") and f"https://polymarket.com/event/{ev['slug']}" or "",
                            # probability-adjusted: real money ON REAL OUTCOMES
                            engagement_score=round(effective, 2),
                            sentiment="neutral",
                            topics=[t.get("label", "").lower() for t in ev.get("tags", [])[:3]],
                            timestamp=ev.get("startDate", ""),
                            metadata={
                                "volume_usd": volume,
                                "liquidity": ev.get("liquidity"),
                                "implied_yes_prob": round(yes_prob, 3),
                            },
                        ))
        except Exception as e:
            print(f"Polymarket error: {e}")
        return signals

    @staticmethod
    def _implied_yes_probability(markets: List[Dict]) -> float:
        """
        Extract implied P(YES) from Gamma market outcome prices.
        Falls back to base rate (~0.266, i.e. 73.4% resolve No) when
        prices are unavailable — deliberately conservative.
        """
        BASE_RATE_NO_RESOLVES = 0.266
        probs = []
        for m in markets[:5]:
            try:
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    prices = json.loads(prices)
                if prices and len(prices) >= 1:
                    p = float(prices[0])
                    if 0 < p < 1:
                        probs.append(p)
            except Exception:
                continue
        if not probs:
            return BASE_RATE_NO_RESOLVES
        # Event YES = best (max) market probability among its markets
        return max(probs)


# Engagement-score normalization: raw scores across sources are incomparable
# (HN points ≠ Reddit karma ≠ USD volume). Normalize per-source to 0-1, then weight.
SOURCE_WEIGHTS = {
    "polymarket": 1.0,   # real money — strongest
    "hacker_news": 0.8,  # technical early-adopter density
    "reddit": 0.7,       # community depth, slower
    "product_hunt": 0.6, # launch-day spike bias
    "twitter": 0.5,      # highest noise floor
    "tiktok": 0.5,       # viral reach, weak purchase intent
}


def _normalize_scores(signals: List[MarketingSignal]) -> List[MarketingSignal]:
    """Min-max normalize engagement within each source, apply source weight."""
    by_source: Dict[str, List[MarketingSignal]] = {}
    for s in signals:
        by_source.setdefault(s.source, []).append(s)

    for source, group in by_source.items():
        scores = [s.engagement_score for s in group]
        lo, hi = min(scores), max(scores)
        span = (hi - lo) or 1.0
        w = SOURCE_WEIGHTS.get(source, 0.5)
        for s in group:
            s.metadata["normalized_score"] = round(
                ((s.engagement_score - lo) / span) * w, 4
            )
    return signals


class SignalFanout:
    """
    Parallel fan-out across all sources → cross-source normalized scoring →
    one synthesized brief.

    Usage:
        fanout = SignalFanout()
        brief = await fanout.run(query="ai agents", limit_per_source=25)
    """

    REGION_PROFILES = {
        "global": {"sources": None},  # all
        "india": {"sources": ["twitter", "reddit", "google_trends",
                              "indian_media", "youtube", "facebook_ads"]},
        "us": {"sources": ["polymarket", "hacker_news", "reddit",
                           "product_hunt", "twitter"]},
    }

    def __init__(self):
        self.collectors = {
            "product_hunt": ProductHuntCollector(),
            "hacker_news": TrendsCollector(),
            "twitter": TwitterCollector(),
            "reddit": RedditCollector(),
            "polymarket": PolymarketCollector(),
            "tiktok": TikTokCollector(),
            "google_trends": GoogleTrendsCollector(),
            "indian_media": IndianMediaRSSCollector(),
            "youtube": YouTubeTrendingCollector(),
        }

    async def run(self, query: str = "", sources: Optional[List[str]] = None,
                  limit_per_source: int = 25,
                  region: Optional[str] = None) -> Dict[str, Any]:
        """Fan out, gather, normalize, synthesize.

        region: optional key into REGION_PROFILES ("global"|"india"|"us").
        If given and the caller didn't pass explicit `sources`, the region's
        source list is used. For region="india", polymarket / tiktok /
        product_hunt are deliberately excluded: polymarket has near-zero India
        markets, tiktok is banned in India, and product_hunt skews US launch
        culture.
        """
        if region and sources is None:
            profile = self.REGION_PROFILES.get(region)
            if profile:
                sources = profile.get("sources")
        active = {k: v for k, v in self.collectors.items()
                  if not sources or k in sources}

        # Parallel fan-out — failures isolated per source
        results = await _asyncio.gather(
            *(c.collect(limit=limit_per_source) for c in active.values()),
            return_exceptions=True,
        )

        all_signals: List[MarketingSignal] = []
        errors = {}
        for name, result in zip(active.keys(), results):
            if isinstance(result, Exception):
                errors[name] = str(result)
            elif isinstance(result, list):
                # Filter by query relevance if given
                if query:
                    q = query.lower()
                    matched = [s for s in result
                               if q in s.title.lower() or any(q in t for t in s.topics)]
                    all_signals.extend(matched if matched else result[:5])
                else:
                    all_signals.extend(result)

        if not all_signals:
            return {"query": query, "total": 0, "brief": None,
                    "errors": errors}

        all_signals = _normalize_scores(all_signals)

        # Calibration data collection: snapshot prediction-market signals so
        # the scorecard can later measure volume x P(YES) against real
        # resolutions. Never let scorecard failures break the fan-out.
        snapshotted = 0
        try:
            from analytics.scorecard import SignalScorecard
            snapshotted = SignalScorecard().snapshot(all_signals)
        except Exception as exc:  # noqa: BLE001
            errors.setdefault("scorecard", str(exc))

        return {"query": query, "total": len(all_signals),
                "calibration_snapshot": snapshotted,
                "errors": errors, **self.synthesize(all_signals)}

    def synthesize(self, signals: List[MarketingSignal]) -> Dict[str, Any]:
        """One brief from N sources: consensus themes, outliers, momentum."""
        ranked = sorted(signals,
                        key=lambda s: s.metadata.get("normalized_score", 0),
                        reverse=True)

        # Cross-source consensus: same topic appearing in ≥2 sources = stronger
        topic_sources: Dict[str, set] = {}
        for s in signals:
            for t in s.topics:
                if t:
                    topic_sources.setdefault(t, set()).add(s.source)
        consensus_themes = sorted(
            [(t, len(srcs)) for t, srcs in topic_sources.items() if len(srcs) >= 2],
            key=lambda x: (-x[1], x[0]),
        )[:8]

        # Money outlier: polymarket item ranking above social chatter
        money_outliers = [s for s in ranked[:15] if s.source == "polymarket"][:3]

        base = aggregate_signals(signals)
        base.pop("top_signals", None)
        base.update({
            "brief_top_10": [
                {"source": s.source, "title": s.title[:120], "url": s.url,
                 "score": s.metadata.get("normalized_score"), "engagement_raw": s.engagement_score}
                for s in ranked[:10]
            ],
            "consensus_themes": [f"{t} ({n} sources)" for t, n in consensus_themes],
            "money_outliers": [
                {"title": s.title[:100], "volume_usd": s.metadata.get("volume_usd"), "url": s.url}
                for s in money_outliers
            ],
        })
        return base
