"""Tests for discover_prospects MCP tool.

Run: pytest tests/test_scout_mcp.py -v --confcutdir=. -o addopts=""
"""
import sys, pytest

sys.path.insert(0, ".")
from mcp_server import HANDLERS


class TestDiscoverProspects:
    @pytest.mark.asyncio
    async def test_requires_icp(self):
        result = await HANDLERS["discover_prospects"]({})
        assert "error" in result

    @pytest.mark.asyncio
    async def test_returns_prospects_list(self):
        """With no SERPER_API_KEY it returns empty prospects but no crash."""
        result = await HANDLERS["discover_prospects"]({
            "icp_description": "D2C vitamin brand India",
            "limit": 5,
        })
        assert isinstance(result, dict)
        assert "prospects" in result
        assert "count" in result
        assert "serper_key_set" in result
        # With no key, count should be 0 but structure should be valid
        assert isinstance(result["prospects"], list)
