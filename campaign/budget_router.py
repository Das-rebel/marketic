"""
Budget Router — AI-powered budget allocation optimization.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BudgetAllocation:
    channel: str
    current_spend: float
    recommended_spend: float
    change_percentage: float
    reasoning: str
    expected_impact: Dict[str, float]


@dataclass
class ChannelPerformance:
    channel: str
    spend: float
    roas: float
    conversions: int
    cpa: float
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    # Margin-aware metrics (S-tier per vault eComm metrics research)
    contribution_margin: float = 1.0   # gross margin after COGS + variable costs (0-1)
    new_customer_ratio: float = 0.5    # new vs returning split

    @property
    def margin_adjusted_roas(self) -> float:
        """ROAS weighted by contribution margin — the number that actually matters.
        A 5x ROAS at 20% margin is worth less than a 2x ROAS at 80% margin."""
        return self.roas * self.contribution_margin


class BudgetRouter:
    """Optimize budget allocation based on historical channel performance."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def rebalance(
        self,
        total_budget: float,
        channel_data: Dict[str, Dict[str, Any]],
        strategy: str = "roas_optimized",
    ) -> List[BudgetAllocation]:
        """Rebalance budget across channels based on performance."""

        # Parse channel data into structured format
        performances = []
        for channel, data in channel_data.items():
            perf = ChannelPerformance(
                channel=channel,
                spend=data.get("spend", 0),
                roas=data.get("roas", 0),
                conversions=data.get("conversions", 0),
                cpa=data.get("cpa", 0),
                impressions=data.get("impressions", 0),
                clicks=data.get("clicks", 0),
                ctr=data.get("ctr", 0),
                contribution_margin=data.get("contribution_margin", 1.0),
                new_customer_ratio=data.get("new_customer_ratio", 0.5),
            )
            performances.append(perf)

        # Calculate optimal allocations
        if strategy == "roas_optimized":
            return await self._optimize_for_roas(total_budget, performances)
        elif strategy == "conversion_focused":
            return await self._optimize_for_conversions(total_budget, performances)
        elif strategy == "awareness_focused":
            return await self._optimize_for_reach(total_budget, performances)
        elif strategy == "balanced":
            return await self._optimize_balanced(total_budget, performances)
        else:
            return await self._optimize_for_roas(total_budget, performances)

    async def _optimize_for_roas(
        self, total: float, performances: List[ChannelPerformance]
    ) -> List[BudgetAllocation]:
        """Optimize for highest ROAS."""
        
        if not performances:
            return []
        
        # Score each channel by ROAS efficiency
        scored = []
        total_spend = sum(p.spend for p in performances)
        
        for perf in performances:
            # Margin-adjusted ROAS: raw ROAS is vanity when margins vary by channel.
            roas_score = perf.margin_adjusted_roas if perf.roas > 0 else 0.5 * perf.contribution_margin
            
            # Efficiency: conversions per dollar
            efficiency = perf.conversions / perf.spend if perf.spend > 0 else 0
            
            # Combined score (weighted)
            combined_score = (roas_score * 0.6) + (efficiency * 100 * 0.4)
            
            scored.append((combined_score, perf))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Allocate budget based on score weights
        total_score = sum(s[0] for s in scored)
        allocations = []
        
        for score, perf in scored:
            weight = score / total_score if total_score > 0 else 1 / len(scored)
            
            # Allocate based on weight
            recommended = total * weight
            
            # Apply limits: min 10% of current if channel is performing, max 50%
            min_spend = max(perf.spend * 0.5, total * 0.05)
            max_spend = max(perf.spend * 2, total * 0.4)
            
            recommended = max(min_spend, min(recommended, max_spend))
            
            change_pct = ((recommended - perf.spend) / perf.spend * 100) if perf.spend > 0 else 100
            
            # Generate reasoning
            reasoning = self._generate_reasoning(perf, recommended, "roas")
            
            allocations.append(BudgetAllocation(
                channel=perf.channel,
                current_spend=perf.spend,
                recommended_spend=round(recommended, 2),
                change_percentage=round(change_pct, 1),
                reasoning=reasoning,
                expected_impact={
                    "roas_change": round((recommended / perf.spend * perf.roas - perf.roas) if perf.spend > 0 else 0, 2),
                    "conversion_change": round((recommended / perf.spend * perf.conversions - perf.conversions) if perf.spend > 0 else 0, 1),
                }
            ))
        
        # Normalize to match total budget
        total_allocated = sum(a.recommended_spend for a in allocations)
        if total_allocated > 0:
            scale = total / total_allocated
            for a in allocations:
                a.recommended_spend = round(a.recommended_spend * scale, 2)
                a.change_percentage = round(((a.recommended_spend - a.current_spend) / a.current_spend * 100) if a.current_spend > 0 else 100, 1)
        
        return allocations

    async def _optimize_for_conversions(
        self, total: float, performances: List[ChannelPerformance]
    ) -> List[BudgetAllocation]:
        """Optimize for highest conversions at lowest CPA."""
        
        if not performances:
            return []
        
        # Score by CPA efficiency (lower CPA is better)
        scored = []
        
        for perf in performances:
            # CPA score (inverse - lower CPA = higher score)
            cpa_score = 100 / perf.cpa if perf.cpa > 0 else 1
            
            # Conversion volume weight
            volume_score = min(perf.conversions / 100, 5)  # Cap at 5
            
            combined_score = cpa_score * 0.7 + volume_score * 0.3
            scored.append((combined_score, perf))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        total_score = sum(s[0] for s in scored)
        allocations = []
        
        for score, perf in scored:
            weight = score / total_score if total_score > 0 else 1 / len(scored)
            recommended = total * weight
            
            min_spend = max(perf.spend * 0.5, total * 0.05)
            max_spend = max(perf.spend * 2, total * 0.4)
            recommended = max(min_spend, min(recommended, max_spend))
            
            change_pct = ((recommended - perf.spend) / perf.spend * 100) if perf.spend > 0 else 100
            
            reasoning = self._generate_reasoning(perf, recommended, "conversions")
            
            allocations.append(BudgetAllocation(
                channel=perf.channel,
                current_spend=perf.spend,
                recommended_spend=round(recommended, 2),
                change_percentage=round(change_pct, 1),
                reasoning=reasoning,
                expected_impact={
                    "cpa_change": round((perf.cpa * perf.spend / recommended - perf.cpa) if recommended > 0 else 0, 2),
                    "conversion_change": round((recommended / perf.spend * perf.conversions - perf.conversions) if perf.spend > 0 else 0, 1),
                }
            ))
        
        # Normalize
        total_allocated = sum(a.recommended_spend for a in allocations)
        if total_allocated > 0:
            scale = total / total_allocated
            for a in allocations:
                a.recommended_spend = round(a.recommended_spend * scale, 2)
                a.change_percentage = round(((a.recommended_spend - a.current_spend) / a.current_spend * 100) if a.current_spend > 0 else 100, 1)
        
        return allocations

    async def _optimize_for_reach(
        self, total: float, performances: List[ChannelPerformance]
    ) -> List[BudgetAllocation]:
        """Optimize for maximum reach/impressions."""
        
        if not performances:
            return []
        
        # Score by CPM efficiency (lower CPM = more reach per dollar)
        scored = []
        
        for perf in performances:
            if perf.impressions > 0 and perf.spend > 0:
                cpm = (perf.spend / perf.impressions) * 1000
                reach_score = 100 / cpm if cpm > 0 else 0
            else:
                reach_score = 0.5
            
            scored.append((reach_score, perf))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        total_score = sum(s[0] for s in scored)
        allocations = []
        
        for score, perf in scored:
            weight = score / total_score if total_score > 0 else 1 / len(scored)
            recommended = total * weight
            
            min_spend = max(perf.spend * 0.5, total * 0.05)
            max_spend = max(perf.spend * 2, total * 0.4)
            recommended = max(min_spend, min(recommended, max_spend))
            
            change_pct = ((recommended - perf.spend) / perf.spend * 100) if perf.spend > 0 else 100
            
            reasoning = self._generate_reasoning(perf, recommended, "reach")
            
            allocations.append(BudgetAllocation(
                channel=perf.channel,
                current_spend=perf.spend,
                recommended_spend=round(recommended, 2),
                change_percentage=round(change_pct, 1),
                reasoning=reasoning,
                expected_impact={
                    "impression_change": round((recommended / perf.spend * perf.impressions - perf.impressions) if perf.spend > 0 else 0, 0),
                }
            ))
        
        # Normalize
        total_allocated = sum(a.recommended_spend for a in allocations)
        if total_allocated > 0:
            scale = total / total_allocated
            for a in allocations:
                a.recommended_spend = round(a.recommended_spend * scale, 2)
                a.change_percentage = round(((a.recommended_spend - a.current_spend) / a.current_spend * 100) if a.current_spend > 0 else 100, 1)
        
        return allocations

    async def _optimize_balanced(
        self, total: float, performances: List[ChannelPerformance]
    ) -> List[BudgetAllocation]:
        """Balanced approach across multiple metrics."""
        
        if not performances:
            return []
        
        scored = []
        
        for perf in performances:
            roas_score = perf.roas if perf.roas > 0 else 0.5
            cpa_score = 100 / perf.cpa if perf.cpa > 0 else 1
            
            # Balanced weighting
            combined_score = (roas_score * 0.33) + (cpa_score * 0.33) + (perf.conversions * 0.34 / 10)
            scored.append((combined_score, perf))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        total_score = sum(s[0] for s in scored)
        allocations = []
        
        for score, perf in scored:
            weight = score / total_score if total_score > 0 else 1 / len(scored)
            recommended = total * weight
            
            min_spend = max(perf.spend * 0.5, total * 0.05)
            max_spend = max(perf.spend * 2, total * 0.4)
            recommended = max(min_spend, min(recommended, max_spend))
            
            change_pct = ((recommended - perf.spend) / perf.spend * 100) if perf.spend > 0 else 100
            
            reasoning = self._generate_reasoning(perf, recommended, "balanced")
            
            allocations.append(BudgetAllocation(
                channel=perf.channel,
                current_spend=perf.spend,
                recommended_spend=round(recommended, 2),
                change_percentage=round(change_pct, 1),
                reasoning=reasoning,
                expected_impact={}
            ))
        
        # Normalize
        total_allocated = sum(a.recommended_spend for a in allocations)
        if total_allocated > 0:
            scale = total / total_allocated
            for a in allocations:
                a.recommended_spend = round(a.recommended_spend * scale, 2)
                a.change_percentage = round(((a.recommended_spend - a.current_spend) / a.current_spend * 100) if a.current_spend > 0 else 100, 1)
        
        return allocations

    def _generate_reasoning(self, perf: ChannelPerformance, recommended: float, strategy: str) -> str:
        """Generate human-readable reasoning for allocation."""
        
        if recommended > perf.spend * 1.1:
            action = "increase"
        elif recommended < perf.spend * 0.9:
            action = "decrease"
        else:
            action = "maintain"
        
        if strategy == "roas":
            if action == "increase":
                return f"Strong ROAS ({perf.roas}x) indicates efficient spend. Increase to capture more high-performing inventory."
            elif action == "decrease":
                return f"ROAS ({perf.roas}x) below target. Reduce to reallocate to higher-performing channels."
            else:
                return f"ROAS ({perf.roas}x) is on target. Maintain current spend level."
        
        elif strategy == "conversions":
            if action == "increase":
                return f"Low CPA (${perf.cpa:.2f}) and good conversion volume. Increase budget for more conversions."
            elif action == "decrease":
                return f"CPA (${perf.cpa:.2f}) too high relative to returns. Reduce to optimize spend efficiency."
            else:
                return f"CPA (${perf.cpa:.2f}) is acceptable. Maintain current allocation."
        
        elif strategy == "reach":
            if action == "increase":
                return f"Strong CPM efficiency. Increase budget to maximize audience reach."
            elif action == "decrease":
                return f"CPM higher than alternatives. Reduce to reallocate to more efficient reach channels."
            else:
                return f"Current reach efficiency is acceptable."
        
        else:
            return f"Balanced optimization suggests {action} in this channel based on multi-metric performance."
