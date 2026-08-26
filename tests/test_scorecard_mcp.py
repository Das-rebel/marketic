"""Tests for SignalScorecard MCP handlers wired into mcp_server."""

import uuid
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp_server import HANDLERS


class TestTrackSignal:
    @pytest.mark.asyncio
    async def test_track_signal_returns_id(self):
        result = await HANDLERS["track_signal"]({
            "title": "Fed cuts rates by March",
            "source": "polymarket",
            "signal_type": "prediction_market",
            "url": f"https://polymarket.com/event/fed-cuts-march-{uuid.uuid4().hex[:8]}",
            "engagement_score": 75000.0,
            "topics": ["fed", "rates"],
            "metadata": {"implied_yes_prob": 55},
        })
        assert isinstance(result, dict)
        assert result.get("tracked") is True
        assert "signal_id" in result
        assert result["signal_id"] is not None

    @pytest.mark.asyncio
    async def test_track_signal_invalid_type(self):
        result = await HANDLERS["track_signal"]({"signal_data": "not a dict"})
        assert isinstance(result, dict)
        assert "error" in result or result.get("tracked") is False


class TestGetCalibrationReport:
    @pytest.mark.asyncio
    async def test_get_calibration_report_returns_dict(self):
        result = await HANDLERS["get_calibration_report"]({})
        assert isinstance(result, dict)
        # Should have the standard report keys
        assert "brier_score" in result


class TestResolveSignal:
    @pytest.mark.asyncio
    async def test_resolve_signal_returns_id(self):
        # First track a signal
        tracked = await HANDLERS["track_signal"]({
            "title": "Test signal for resolve",
            "source": "polymarket",
            "signal_type": "test",
            "url": "https://polymarket.com/event/test-resolve-" + str(id(self)),
            "engagement_score": 10000.0,
        })
        signal_id = tracked.get("signal_id")
        assert signal_id is not None, f"track failed: {tracked}"

        # Then resolve it
        result = await HANDLERS["resolve_signal"]({
            "signal_id": signal_id,
            "actual_outcome": "YES",
            "notes": "Test resolution",
        })
        assert isinstance(result, dict)
        assert result.get("resolved") is True
        assert result.get("signal_id") == signal_id
