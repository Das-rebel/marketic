"""
Prospect Scout — top-of-funnel discovery.

Finds companies/people matching an ICP before they enter the enrichment pipeline.
Complements run_prospect_loop (which enriches known leads); this finds NEW targets.

Sources checked in parallel:
  1. Serper API — Google search for ICP-matching companies/news
  2. Twitter/X — operator accounts in the target niche
  3. Reddit — discussions from companies matching the ICP
  4. Product Hunt — new launches in target category
"""
from __future__ import annotations

import os
import re
import asyncio
from typing import Optional
from dataclasses import dataclass, field
from urllib.parse import quote_plus

import httpx

SERPER_BASE = "https://google.serper.dev/search"
SERPER_TYPES = {
    "news": "https://google.serper.dev/news",
    "images": "https://google.serper.dev/images",
}


@dataclass
class ScoutResult:
    """A discovered prospect entity."""
    name: str
    domain: Optional[str] = None
    source: str = ""
    source_url: str = ""
    headline: str = ""
    relevance_score: float = 0.0  # 0-100
    signal: str = ""  # why this matches ICP
    matched_on: list[str] = field(default_factory=list)  # which keywords matched


class ProspectScout:
    """Discover new prospects matching an ICP.

    Usage:
        scout = ProspectScout()
        results = await scout.discover(
            icp_description="D2C skincare brands in India with 10k+ Instagram followers",
            limit=20,
        )
    """

    def __init__(self, *, serper_api_key: Optional[str] = None):
        self.serper_key = serper_api_key or os.getenv("SERPER_API_KEY")

    async def discover(
        self,
        icp_description: str,
        limit: int = 20,
        sources: Optional[list[str]] = None,
    ) -> list[ScoutResult]:
        """Run all source scouts in parallel, merge and rank results.

        Args:
            icp_description: Natural-language description of the ICP.
            limit: Maximum results to return.
            sources: Which sources to check. Defaults to all available.
        """
        sources = sources or ["serper", "twitter", "reddit", "product_hunt"]
        queries = self._build_queries(icp_description)

        tasks = []
        if "serper" in sources:
            tasks.append(self._serper_search(queries["serper"]))
        if "twitter" in sources:
            tasks.append(self._twitter_search(queries["twitter"]))
        if "reddit" in sources:
            tasks.append(self._reddit_search(queries["reddit"]))
        if "product_hunt" in sources:
            tasks.append(self._product_hunt_search(queries["product_hunt"]))

        batches = await asyncio.gather(*tasks, return_exceptions=True)
        seen: set[str] = set()
        results: list[ScoutResult] = []

        for batch in batches:
            for r in batch:
                key = r.domain or r.name
                if key and key not in seen:
                    seen.add(key)
                    results.append(r)

        # Sort by relevance descending
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    # ------------------------------------------------------------------ //
    # Source implementations
    # ------------------------------------------------------------------ //

    async def _serper_search(self, query: str) -> list[ScoutResult]:
        """Google search via Serper — finds companies in the news/serps."""
        if not self.serper_key:
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    SERPER_BASE,
                    headers={"X-API-KEY": self.serper_key},
                    json={"q": query, "num": 10},
                )
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = []
            for item in data.get("organic", [])[:8]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                url = item.get("link", "")
                domain = self._extract_domain(url)
                score = self._score_text(f"{title} {snippet}", query)
                results.append(ScoutResult(
                    name=title,
                    domain=domain,
                    source="serper",
                    source_url=url,
                    headline=snippet[:120],
                    relevance_score=score,
                    signal=f"Ranked #{item.get('position', '?')} in Google results for: {query}",
                    matched_on=self._matched_keywords(f"{title} {snippet}", query),
                ))
            return results
        except Exception:
            return []

    async def _twitter_search(self, query: str) -> list[ScoutResult]:
        """Find operator/company accounts on X via Serper Twitter results."""
        if not self.serper_key:
            return []

        twitter_query = f"{query} site:twitter.com OR site:x.com"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    SERPER_BASE,
                    headers={"X-API-KEY": self.serper_key},
                    json={"q": twitter_query, "num": 8},
                )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("organic", [])[:6]:
                url = item.get("link", "")
                domain = self._extract_domain(url)
                score = self._score_text(item.get("title", ""), query) * 0.9
                results.append(ScoutResult(
                    name=item.get("title", "").replace(" on X", "").replace(" (@", " (@"),
                    domain=domain,
                    source="twitter",
                    source_url=url,
                    headline=item.get("snippet", "")[:100],
                    relevance_score=score,
                    signal="X/Twitter operator account matching ICP",
                    matched_on=self._matched_keywords(item.get("title", ""), query),
                ))
            return results
        except Exception:
            return []

    async def _reddit_search(self, query: str) -> list[ScoutResult]:
        """Find relevant discussions on Reddit (companies being discussed)."""
        if not self.serper_key:
            return []

        reddit_query = f"{query} site:reddit.com"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    SERPER_BASE,
                    headers={"X-API-KEY": self.serper_key},
                    json={"q": reddit_query, "num": 8},
                )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("organic", [])[:6]:
                url = item.get("link", "")
                # Try to extract a company/project name from the Reddit title
                title = item.get("title", "")
                domain = self._extract_domain(url)
                score = self._score_text(title, query) * 0.8
                results.append(ScoutResult(
                    name=title[:80],
                    domain=domain,
                    source="reddit",
                    source_url=url,
                    headline=f"Reddit discussion · {item.get('snippet', '')[:80]}",
                    relevance_score=score,
                    signal="Active Reddit discussion in target category",
                    matched_on=self._matched_keywords(title, query),
                ))
            return results
        except Exception:
            return []

    async def _product_hunt_search(self, query: str) -> list[ScoutResult]:
        """Find recently launched products matching the ICP via Serper."""
        if not self.serper_key:
            return []

        ph_query = f"{query} site:producthunt.com"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    SERPER_BASE,
                    headers={"X-API-KEY": self.serper_key},
                    json={"q": ph_query, "num": 6},
                )
            if resp.status_code != 200:
                return []
            results = []
            for item in resp.json().get("organic", [])[:5]:
                url = item.get("link", "")
                domain = self._extract_domain(url)
                score = self._score_text(item.get("title", ""), query) * 1.1
                results.append(ScoutResult(
                    name=item.get("title", ""),
                    domain=domain,
                    source="product_hunt",
                    source_url=url,
                    headline=f"Product Hunt launch · {item.get('snippet', '')[:80]}",
                    relevance_score=score,
                    signal="Recent Product Hunt launch matching ICP",
                    matched_on=self._matched_keywords(item.get("title", ""), query),
                ))
            return results
        except Exception:
            return []

    # ------------------------------------------------------------------ //
    # Helpers
    # ------------------------------------------------------------------ //

    def _build_queries(self, icp: str) -> dict[str, str]:
        """Expand one ICP description into queries for each source."""
        base = icp.strip().rstrip(".")
        return {
            "serper": base,
            "twitter": f"{base} founder OR {base} brand OR {base} startup",
            "reddit": f"{base} India OR {base} D2C OR {base} startup India",
            "product_hunt": base,
        }

    def _extract_domain(self, url: str) -> Optional[str]:
        if not url:
            return None
        m = re.match(r"https?://([^/]+)", url)
        if m:
            d = m.group(1)
            return d.replace("www.", "")
        return None

    def _score_text(self, text: str, query: str) -> float:
        """Simple keyword overlap score 0-100."""
        text_l = text.lower()
        query_l = query.lower()
        # Count how many query words appear in text
        words = [w for w in query_l.split() if len(w) > 2]
        if not words:
            return 50.0
        matches = sum(1 for w in words if w in text_l)
        return min(matches / len(words) * 100, 100.0)

    def _matched_keywords(self, text: str, query: str) -> list[str]:
        text_l, query_l = text.lower(), query.lower()
        return [w for w in query_l.split() if len(w) > 2 and w in text_l]


# -------------------------------------------------------------------------- //
# Smoke test
# -------------------------------------------------------------------------- //

if __name__ == "__main__":
    import sys

    async def main():
        scout = ProspectScout()
        if not scout.serper_key:
            print("SERPER_API_KEY not set — test with mock only")
            sys.exit(0)

        results = await scout.discover(
            icp_description="D2C skincare brand India selling serums and moisturizers",
            limit=10,
        )
        print(f"\nDiscovered {len(results)} prospects:\n")
        for r in results:
            print(f"  [{r.source.upper():12}] {r.name[:60]}")
            print(f"   domain: {r.domain or 'n/a'} | score: {r.relevance_score:.0f}/100")
            print(f"   why: {r.signal}")
            print()

    asyncio.run(main())
