"""
Budget Router

AI-powered budget allocation and rebalancing across channels.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

from ..foundation.llm_router import generate_parallel, TaskType


@dataclass
class BudgetAllocation:
    """Budget allocation for a single channel."""
    channel: str
    current_budget: float
    recommended_budget: float
    change_percent: float
    reason: str
    expected_impact: str


class BudgetRouter:
    """
    Automatically routes and rebalances marketing budget across channels
    based on real-time performance data.
    
    Usage:
        router = BudgetRouter()
        allocations = await router.rebalance(
            total_budget=100000,
            channel_data={
                "google_search": {"spend": 40000, "roas": 3.5, "conversions": 450},
                "meta_feed": {"spend": 35000, "roas": 2.1, "conversions": 320},
                "linkedin": {"spend": 25000, "roas": 1.8, "conversions": 89},
            }
        )
    """
    
    async def rebalance(
        self,
        total_budget: float,
        channel_data: Dict[str, Dict],
        strategy: str = "roas_optimized",  # roas_optimized, conversion_focused, brand_building
    ) -> List[BudgetAllocation]:
        """
        Rebalance budget across channels based on performance.
        
        Strategies:
        - roas_optimized: Maximize ROAS, shift budget to best performers
        - conversion_focused: Minimize CPA, shift to best converters
        - brand_building: Balance efficiency with awareness channels
        """
        
        prompt = f"""Analyze this marketing channel performance and rebalance ${total_budget:,} budget:

Current Allocations and Performance:
{chr(10).join([f"- {ch}: Spend=${data.get('spend', 0):,.0f}, ROAS={data.get('roas', 0):.2f}x, CPA=${data.get('cpa', 0):.2f}, Conversions={data.get('conversions', 0)}" for ch, data in channel_data.items()])}

Strategy: {strategy}

Provide new budget allocation for each channel that optimizes for this strategy.
For each channel include:
1. Recommended budget amount
2. % change from current
3. Brief reason for the change
4. Expected performance impact

Return as JSON array with fields: channel, current_budget, recommended_budget, change_percent, reason, expected_impact"""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.OPTIMIZATION,
            temperature=0.5,
            max_tokens=2048,
        )
        
        allocations = []
        
        for response in responses[:1]:
            try:
                import json
                content = response.content
                
                if "[" in content:
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    data = json.loads(content[start:end])
                    
                    for item in data:
                        allocation = BudgetAllocation(
                            channel=item.get("channel", ""),
                            current_budget=item.get("current_budget", 0),
                            recommended_budget=item.get("recommended_budget", 0),
                            change_percent=item.get("change_percent", 0),
                            reason=item.get("reason", ""),
                            expected_impact=item.get("expected_impact", ""),
                        )
                        allocations.append(allocation)
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Parse error: {e}")
        
        return allocations
    
    async def suggest_daily_budget(
        self,
        channel: str,
        performance_data: Dict,
        target_cpa: float = None,
        target_roas: float = None,
    ) -> float:
        """Suggest optimal daily budget for a channel."""
        
        current_spend = performance_data.get("spend", 0)
        current_cpa = performance_data.get("cpa", 0)
        current_roas = performance_data.get("roas", 0)
        daily_spend = performance_data.get("daily_spend", current_spend / 30)
        days_remaining = performance_data.get("days_remaining", 30)
        budget_remaining = performance_data.get("budget_remaining", 0)
        
        # Calculate suggested daily budget
        if target_cpa and current_cpa > 0:
            # Need to spend less per conversion
            recent_conversions = performance_data.get("conversions", 100)
            daily_conversions = recent_conversions / 30
            
            if daily_conversions > 0:
                suggested_daily = daily_conversions * target_cpa
            else:
                suggested_daily = daily_spend * 0.9  # Conservative 10% reduction
                
        elif target_roas and current_roas > 0:
            # Optimize for ROAS
            daily_revenue = daily_spend * current_roas
            suggested_daily = daily_revenue / target_roas if target_roas > 0 else daily_spend
            
        else:
            # Default: maintain current pace with slight optimization
            suggested_daily = daily_spend * 0.95
        
        # Cap at remaining budget divided by days
        max_daily = budget_remaining / days_remaining if days_remaining > 0 else suggested_daily
        suggested_daily = min(suggested_daily, max_daily * 1.2)  # Allow 20% over if performing well
        
        return round(suggested_daily, 2)
    
    def calculate_efficiency_score(self, channel_data: Dict) -> Dict[str, float]:
        """Calculate efficiency scores for channels."""
        scores = {}
        
        for channel, data in channel_data.items():
            roas = data.get("roas", 0)
            cpa = data.get("cpa", 0)
            conversions = data.get("conversions", 0)
            spend = data.get("spend", 1)
            
            # Composite efficiency score
            roas_score = min(roas / 3.0, 1.0) * 40  # ROAS normalized (target 3x)
            volume_score = min(conversions / 100, 1.0) * 30  # Volume normalized
            efficiency_score = min(spend / 10000, 1.0) * 30  # Investment level
            
            total_score = roas_score + volume_score + efficiency_score
            scores[channel] = round(total_score, 2)
        
        return scores


async def demo():
    """Demo the budget router."""
    print("=" * 60)
    print("MARKETIC BUDGET ROUTER DEMO")
    print("=" * 60)
    
    router = BudgetRouter()
    
    # Channel performance data
    channel_data = {
        "google_search": {
            "spend": 40000,
            "roas": 3.5,
            "cpa": 45.23,
            "conversions": 885,
        },
        "meta_feed": {
            "spend": 35000,
            "roas": 2.1,
            "cpa": 78.50,
            "conversions": 446,
        },
        "linkedin_sponsored": {
            "spend": 20000,
            "roas": 1.5,
            "cpa": 125.00,
            "conversions": 160,
        },
        "youtube": {
            "spend": 5000,
            "roas": 1.2,
            "cpa": 95.00,
            "conversions": 53,
        },
    }
    
    total_budget = 100000
    
    print(f"\n💰 Total Budget: ${total_budget:,}")
    print("\nCurrent Channel Performance:")
    for ch, data in channel_data.items():
        print(f"  {ch}: ${data['spend']:,} | ROAS: {data['roas']}x | CPA: ${data['cpa']}")
    
    # Rebalance
    print("\n🔄 Rebalancing Budget (ROAS Optimized)...")
    allocations = await router.rebalance(
        total_budget=total_budget,
        channel_data=channel_data,
        strategy="roas_optimized",
    )
    
    print("\nRecommended Allocations:")
    for alloc in allocations:
        change = f"+{alloc.change_percent:.1f}%" if alloc.change_percent > 0 else f"{alloc.change_percent:.1f}%"
        print(f"\n  {alloc.channel}:")
        print(f"    Current: ${alloc.current_budget:,.0f}")
        print(f"    Recommended: ${alloc.recommended_budget:,.0f} ({change})")
        print(f"    Reason: {alloc.reason[:60]}...")
    
    # Efficiency scores
    print("\n📊 Channel Efficiency Scores:")
    scores = router.calculate_efficiency_score(channel_data)
    for ch, score in sorted(scores.items(), key=lambda x: -x[1]):
        print(f"  {ch}: {score:.1f}/100")
    
    return allocations


if __name__ == "__main__":
    asyncio.run(demo())
