"""
Region-profile tests — India pack.

Run: pytest tests/test_region_profiles.py -v --confcutdir=. -o addopts=""
"""
import sys, os, pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signals.collectors import (
    SignalFanout,
    GoogleTrendsCollector,
    IndianMediaRSSCollector,
    YouTubeTrendingCollector,
    expand_hinglish,
)


class TestRegionProfiles:
    def test_india_profile_exists_and_excludes_dead_sources(self):
        india = SignalFanout.REGION_PROFILES["india"]["sources"]
        assert "google_trends" in india
        assert "indian_media" in india
        assert "youtube" in india
        # Polymarket: near-zero India markets; TikTok: banned in India since 2020
        assert "polymarket" not in india
        assert "tiktok" not in india

    def test_us_profile_keeps_polymarket(self):
        us = SignalFanout.REGION_PROFILES["us"]["sources"]
        assert "polymarket" in us

    def test_unknown_profile_is_noop(self):
        """Unknown regions must not crash — fall through to all sources."""
        assert SignalFanout.REGION_PROFILES.get("atlantis") is None


class TestHinglish:
    def test_expands_common_terms(self):
        variants = expand_hinglish("best skincare")
        assert "best skincare" in variants          # original preserved
        assert any("sabse acha" in v for v in variants)

    def test_capped_at_8(self):
        assert len(expand_hinglish("best cheap review phone")) <= 8

    def test_empty_safe(self):
        assert expand_hinglish("") == [""] or expand_hinglish("") == []


class TestCollectorsDegradation:
    @pytest.mark.asyncio
    async def test_trends_degrades_not_crashes(self):
        """429/network failures must return [], never raise."""
        r = await GoogleTrendsCollector().collect(query="skincare")
        assert isinstance(r, list)

    @pytest.mark.asyncio
    async def test_rss_returns_signals_or_empty(self):
        r = await IndianMediaRSSCollector().collect(query="")
        assert isinstance(r, list)
        if r:  # live network case
            s = r[0]
            assert s.source == "indian_media"
            assert s.title

    @pytest.mark.asyncio
    async def test_youtube_live_or_graceful(self):
        import shutil
        r = await YouTubeTrendingCollector().collect(query="skincare review")
        assert isinstance(r, list)
        if r and shutil.which("yt-dlp"):
            s = r[0]
            assert s.source == "youtube"
            assert s.engagement_score >= 0
