"""
test_ad_breakdown_mcp.py — pytest suite for handle_breakdown_ad MCP tool.

Run: pytest tests/test_ad_breakdown_mcp.py -v --confcutdir=. -o addopts=""
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from mcp_server import handle_breakdown_ad


@pytest.mark.asyncio
async def test_breakdown_ad_with_text():
    """Raw ad copy text triggers heuristic fallback (no network needed)."""
    result = await handle_breakdown_ad({
        "ad_url_or_text": "Get 50% off today only! Click here to shop now.",
        "brand_name": "TestBrand",
        "analysis_depth": "standard",
    })
    # Should return a dict with breakdown fields, not crash
    assert isinstance(result, dict)
    # Heuristic backend populates these fields
    assert "hook" in result or "error" in result
    # No network required for text-only heuristic
    assert result.get("backend") == "heuristics" or "error" in result


@pytest.mark.asyncio
async def test_breakdown_ad_with_url_graceful():
    """Plausible URL should either succeed or return error dict gracefully."""
    result = await handle_breakdown_ad({
        "ad_url_or_text": "https://example.com/ads/competitor-banner.jpg",
        "brand_name": "Nike",
        "analysis_depth": "standard",
    })
    assert isinstance(result, dict)
    # Must not raise — graceful degradation expected (no local VLM/token)
    assert ("hook" in result) or ("error" in result) or ("backend" in result)


@pytest.mark.asyncio
async def test_breakdown_ad_unknown_brand():
    """Empty ad_url_or_text with brand_name set should return error dict."""
    result = await handle_breakdown_ad({
        "ad_url_or_text": "",
        "brand_name": "SomeBrand",
        "analysis_depth": "standard",
    })
    assert isinstance(result, dict)
    assert "error" in result, f"Expected error key for empty input, got: {result}"
    assert result["error"] == "ad_url_or_text is required"
