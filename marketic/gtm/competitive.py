"""
Competitive Intelligence

Monitor and analyze competitors.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from ..foundation.llm_router import generate_parallel, TaskType


class CompetitiveIntelligence:
    """
    Competitive intelligence gathering and analysis.
    
    Usage:
        ci = CompetitiveIntelligence()
        analysis = await ci.analyze_competitor("hubspot")
    """
    
    async def analyze_competitor(
        self,
        competitor_name: str,
        category: str = "",
    ) -> Dict:
        """Analyze a competitor's positioning and strategy."""
        
        prompt = f"""Conduct a competitive analysis of {competitor_name}:

{f"Category: {category}" if category else ""}

Provide:
1. Company overview and positioning
2. Key products/services
3. Target customer segments
4. Pricing strategy
5. Marketing approach
6. Strengths (what they do well)
7. Weaknesses (vulnerabilities to exploit)
8. Recent moves (new products, campaigns, pivots)

Be objective and factual. Use publicly known information."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.5,
            max_tokens=2048,
        )
        
        return {
            "competitor": competitor_name,
            "analysis": responses[0].content if responses else "",
            "confidence": responses[0].confidence if responses else 0,
            "analyzed_at": datetime.now().isoformat(),
        }
    
    async def compare_with_competitors(
        self,
        your_product: str,
        competitors: List[str],
    ) -> Dict:
        """Compare your product against competitors."""
        
        competitors_str = ", ".join(competitors)
        
        prompt = f"""Compare positioning and differentiation:

Your Product: {your_product}
Competitors: {competitors_str}

Provide a comparison covering:
1. Feature comparison matrix
2. Price comparison
3. Positioning differences
4. Your unique advantages
5. Your vulnerabilities vs competitors
6. Strategic recommendations

Format as structured comparison with clear tables where helpful."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.6,
            max_tokens=2560,
        )
        
        return {
            "your_product": your_product,
            "competitors": competitors,
            "comparison": responses[0].content if responses else "",
            "confidence": responses[0].confidence if responses else 0,
        }
    
    async def generate_competitive_messaging(
        self,
        competitor: str,
        your_differentiators: List[str],
    ) -> Dict[str, str]:
        """Generate messaging that positions against a competitor."""
        
        diff_str = "\n".join([f"- {d}" for d in your_differentiators])
        
        prompt = f"""Generate competitive messaging against {competitor}:

Your Differentiators:
{diff_str}

Create:
1. Attack messaging (direct comparisons)
2. Displacement messaging (why to switch)
3. Differentiation messaging (unique value)

For each, provide:
- Key headline/tagline
- Supporting points
- Tone guidance

Format as structured messaging guide."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.COPY_GENERATION,
            temperature=0.7,
            max_tokens=2048,
        )
        
        return {
            "competitor": competitor,
            "messaging": responses[0].content if responses else "",
            "differentiators": your_differentiators,
        }


async def demo():
    """Demo competitive intelligence."""
    print("=" * 60)
    print("MARKETIC COMPETITIVE INTELLIGENCE DEMO")
    print("=" * 60)
    
    ci = CompetitiveIntelligence()
    
    # Analyze competitor
    print("\n🔍 Analyzing HubSpot...")
    analysis = await ci.analyze_competitor("HubSpot", "Marketing Automation")
    
    print(f"\nAnalysis (confidence: {analysis['confidence']:.0%}):")
    print("-" * 40)
    print(analysis["analysis"][:600] + "...")
    
    # Compare with competitors
    print("\n\n⚔️ Competitive Comparison:")
    comparison = await ci.compare_with_competitors(
        your_product="MarketIQ",
        competitors=["HubSpot", "Marketo", "Pardot"]
    )
    
    print(f"\nComparison Preview:")
    print(comparison["comparison"][:500] + "...")
    
    return analysis, comparison


if __name__ == "__main__":
    asyncio.run(demo())
