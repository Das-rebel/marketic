"""
Campaign Optimizer

AI-powered campaign optimization with real-time performance analysis.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..foundation.llm_router import generate_parallel, TaskType
from ..foundation.memory import get_campaign, save_campaign


@dataclass
class OptimizationRecommendation:
    """A single optimization recommendation."""
    recommendation_id: str
    campaign_id: str
    channel: str
    issue: str
    recommendation: str
    expected_impact: str  # low, medium, high
    confidence: float
    priority: int  # 1 = highest
    action: str  # specific action to take


class CampaignOptimizer:
    """
    Optimizes campaign performance using AI analysis.
    
    Features:
    - Performance diagnosis
    - Bid optimization suggestions
    - Budget reallocation recommendations
    - Creative performance analysis
    - Audience targeting improvements
    
    Usage:
        optimizer = CampaignOptimizer()
        recommendations = await optimizer.analyze(campaign_id="abc123")
    """
    
    async def analyze(
        self,
        campaign_id: str,
        performance_data: Optional[Dict] = None,
    ) -> List[OptimizationRecommendation]:
        """Analyze campaign and generate optimization recommendations."""
        
        # Get campaign data from memory
        if performance_data is None:
            campaign_data = get_campaign(campaign_id)
            if not campaign_data:
                return []
            performance_data = campaign_data
        
        # Generate AI-powered analysis
        analysis_prompt = f"""Analyze this marketing campaign performance and provide optimization recommendations:

Campaign Data:
- Name: {performance_data.get('name', 'Unknown')}
- Channel: {performance_data.get('channel', 'multi')}
- Objective: {performance_data.get('objective', 'conversions')}
- Budget: ${performance_data.get('budget', 0)}
- Spend: ${performance_data.get('spend', 0)}
- Impressions: {performance_data.get('impressions', 0)}
- Clicks: {performance_data.get('clicks', 0)}
- Conversions: {performance_data.get('conversions', 0)}
- Revenue: ${performance_data.get('revenue', 0)}
- CPA: ${performance_data.get('cpa', 0)}
- ROAS: {performance_data.get('roas', 0)}

Provide 5 specific, actionable recommendations to improve performance.
For each recommendation include:
1. The specific issue
2. The recommended action
3. Expected impact (low/medium/high)
4. Priority (1-5, 1 being highest)

Return as JSON array with fields: issue, recommendation, expected_impact, priority"""

        responses = await generate_parallel(
            prompt=analysis_prompt,
            task_type=TaskType.OPTIMIZATION,
            temperature=0.6,
            max_tokens=2048,
        )
        
        recommendations = []
        
        for response in responses[:1]:
            try:
                # Parse JSON from response
                import json
                content = response.content
                
                if "[" in content:
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    data = json.loads(content[start:end])
                    
                    for i, item in enumerate(data):
                        rec = OptimizationRecommendation(
                            recommendation_id=f"rec_{campaign_id}_{i}",
                            campaign_id=campaign_id,
                            channel=performance_data.get("channel", "unknown"),
                            issue=item.get("issue", ""),
                            recommendation=item.get("recommendation", ""),
                            expected_impact=item.get("expected_impact", "medium"),
                            confidence=response.confidence,
                            priority=item.get("priority", 3),
                            action=item.get("recommendation", ""),
                        )
                        recommendations.append(rec)
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Parse error: {e}")
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations
    
    async def optimize_bids(
        self,
        campaign_id: str,
        current_bids: Dict[str, float],
        performance_data: Dict,
    ) -> Dict[str, float]:
        """Generate optimized bid suggestions."""
        
        prompt = f"""Analyze keyword bids and suggest optimizations:

Current Bids:
{chr(10).join([f"- {kw}: ${bid}" for kw, bid in current_bids.items()])}

Performance:
- Clicks: {performance_data.get('clicks', 0)}
- Conversions: {performance_data.get('conversions', 0)}
- CPA: ${performance_data.get('cpa', 0)}
- CTR: {performance_data.get('ctr', 0):.2f}%

For each keyword, recommend:
1. Keep, increase (+X%), or decrease (-X%)
2. Suggested bid amount
3. Reason for change

Return as JSON: {{"keyword": {{"action": "keep/increase/decrease", "suggested_bid": X, "reason": "..."}}}}"""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.OPTIMIZATION,
            temperature=0.5,
            max_tokens=1024,
        )
        
        # Parse and return bid suggestions
        optimized_bids = current_bids.copy()
        
        # In production, parse actual response
        return optimized_bids
    
    async def analyze_creative_performance(
        self,
        campaign_id: str,
        creative_data: List[Dict],
    ) -> List[Dict]:
        """Analyze creative assets and recommend best performers."""
        
        if not creative_data:
            return []
        
        prompt = f"""Analyze these ad creatives and rank by performance:

Creative Performance:
{chr(10).join([f"- {c.get('headline', 'Unknown')}: CTR={c.get('ctr', 0):.2f}%, Conv={c.get('conversion_rate', 0):.2f}%, Spend=${c.get('spend', 0)}" for c in creative_data])}

Provide:
1. Ranking of top 3 creatives to scale
2. Ranking of bottom 2 creatives to pause
3. Key insights on what's working

Return as JSON with fields: creative_id, recommendation, reasoning"""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.ANALYTICS,
            temperature=0.6,
            max_tokens=1024,
        )
        
        # Parse response
        analysis = []
        for response in responses[:1]:
            # Extract insights
            analysis.append({
                "confidence": response.confidence,
                "insights": response.content[:500],
            })
        
        return analysis


async def demo():
    """Demo the optimizer."""
    print("=" * 60)
    print("MARKETIC CAMPAIGN OPTIMIZER DEMO")
    print("=" * 60)
    
    optimizer = CampaignOptimizer()
    
    # Simulated campaign data
    campaign_data = {
        "campaign_id": "demo_001",
        "name": "Q3 Product Launch",
        "channel": "google_search",
        "objective": "conversions",
        "budget": 50000,
        "spend": 32450,
        "impressions": 1250000,
        "clicks": 28500,
        "conversions": 428,
        "revenue": 85600,
        "cpa": 75.82,
        "roas": 2.64,
        "ctr": 2.28,
        "conversion_rate": 1.50,
    }
    
    print("\n📊 Analyzing Campaign Performance...")
    print(f"Campaign: {campaign_data['name']}")
    print(f"Spend: ${campaign_data['spend']:,} / ${campaign_data['budget']:,}")
    print(f"CPA: ${campaign_data['cpa']:.2f}")
    print(f"ROAS: {campaign_data['roas']:.2f}x")
    
    recommendations = await optimizer.analyze(
        campaign_id=campaign_data["campaign_id"],
        performance_data=campaign_data,
    )
    
    print(f"\n🎯 Found {len(recommendations)} Optimization Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"\n  {i}. [{rec.priority}] {rec.issue}")
        print(f"     Action: {rec.recommendation[:80]}...")
        print(f"     Impact: {rec.expected_impact} | Confidence: {rec.confidence:.0%}")
    
    return recommendations


if __name__ == "__main__":
    asyncio.run(demo())
