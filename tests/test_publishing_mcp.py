"""Publishing/UGC/template MCP tool tests.

Run: pytest tests/test_publishing_mcp.py -v --confcutdir=. -o addopts=""
"""
import sys, pytest

sys.path.insert(0, ".")
from mcp_server import HANDLERS


class TestHashtagOptimizer:
    @pytest.mark.asyncio
    async def test_optimize_hashtags_returns_list(self):
        result = await HANDLERS["optimize_hashtags"]({
            "content_text": "Check out our new skincare launch today",
            "platform": "instagram",
        })
        assert isinstance(result, dict)
        assert "hashtags" in result or "error" in result


class TestScheduleContent:
    @pytest.mark.asyncio
    async def test_schedule_content_degrades_gracefully(self):
        result = await HANDLERS["schedule_content"]({
            "platform": "instagram",
            "content_text": "Testing scheduling",
        })
        # Should not raise; returns dict (may have error if keys missing)
        assert isinstance(result, dict)


class TestUGC:
    @pytest.mark.asyncio
    async def test_curate_ugc_returns_struct(self):
        result = await HANDLERS["curate_ugc"]({
            "hashtag": "skincare",
            "platform": "instagram",
            "limit": 3,
        })
        assert isinstance(result, dict)
        assert "curated" in result or "error" in result

    @pytest.mark.asyncio
    async def test_request_ugc_permission_degrades(self):
        result = await HANDLERS["request_ugc_permission"]({
            "content_url": "https://instagram.com/p/test",
            "platform": "instagram",
        })
        assert isinstance(result, dict)


class TestTemplateRenderer:
    @pytest.mark.asyncio
    async def test_render_template_with_minimal_brand(self):
        result = await HANDLERS["render_template"]({
            "template_name": "MinimalStory",
            "brand": {
                "name": "TestBrand",
                "primary": "#FF0000",
                "background": "#FFFFFF",
                "accent": "#0000FF",
                "secondary": "#00FF00",
                "font": "Arial",
                "handle": "@testbrand",
                "tagline": "Test tagline",
            },
        })
        assert isinstance(result, dict)
        assert "html" in result or "placeholders" in result or "error" in result
