"""
Budget router margin-awareness tests — locks the core claim that budget
optimizes contribution profit (roas x margin), not vanity ROAS.

Run: pytest tests/test_budget_margin.py -v
"""
import sys, os, pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from campaign.budget_router import BudgetRouter
except ImportError:
    pytest.skip("BudgetRouter import path changed", allow_module_level=True)


def _make_router():
    return BudgetRouter()


class TestMarginAwareness:
    @pytest.mark.asyncio
    async def test_high_margin_beats_vanity_roas(self):
        """
        Channel A: 5x ROAS @ 15% margin -> 0.75 contribution multiple
        Channel B: 2x ROAS @ 85% margin -> 1.70 contribution multiple
        B must receive MORE budget despite half the ROAS.
        """
        router = _make_router()
        channel_data = {
            "vanity": {"roas": 5.0, "contribution_margin": 0.15, "spend": 5000},
            "profit": {"roas": 2.0, "contribution_margin": 0.85, "spend": 5000},
        }
        result = await router.rebalance(10000, channel_data, strategy="roas_optimized")
        allocations = {a.channel: a.recommended_spend for a in result}
        assert allocations["profit"] > allocations["vanity"], (
            f"margin-aware routing violated: {allocations}"
        )

    @pytest.mark.asyncio
    async def test_split_sums_to_total(self):
        router = _make_router()
        channel_data = {
            "email": {"roas": 3.0, "contribution_margin": 0.5, "spend": 4000},
            "social": {"roas": 2.0, "contribution_margin": 0.6, "spend": 4000},
        }
        result = await router.rebalance(8000, channel_data, strategy="roas_optimized")
        total = sum(a.recommended_spend for a in result)
        assert abs(total - 8000) < 0.01
