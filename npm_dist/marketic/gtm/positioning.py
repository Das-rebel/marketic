"""
Positioning Analyzer

Market positioning strategy and analysis.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..foundation.llm_router import generate_parallel, TaskType


@dataclass
class PositioningMap:
    """2D positioning map for competitive analysis."""
    x_axis: str  # e.g., "Price: Low to High"
    y_axis: str  # e.g., "Quality: Low to High"
    competitors: Dict[str, Dict] = None  # {name: {x: val, y: val, size: market_share}}


@dataclass
class PositioningRecommendation:
    """Positioning recommendation."""
    position: str
    tagline: str
    key_differentiators: List[str]
    messaging_framework: str
    visual_positioning_notes: str


class PositioningAnalyzer:
    """
    Analyzes and develops market positioning strategy.
    
    Usage:
        analyzer = PositioningAnalyzer()
        position = await analyzer.analyze(
            product="AI marketing tool",
            category="marketing automation",
            competitors=["hubspot", "marketo", "pardot"]
        )
    """
    
    async def analyze(
        self,
        product_name: str,
        product_description: str,
        category: str,
        competitors: List[str],
        target_audience: str = "",
    ) -> Dict:
        """Analyze positioning options."""
        
        prompt = f"""Analyze market positioning for a new product:

Product: {product_name}
Description: {product_description}
Category: {category}
Competitors: {', '.join(competitors)}
{f"Target Audience: {target_audience}" if target_audience else ""}

Provide:
1. Competitive positioning map (2x2 matrix) with positioning recommendations
2. 3 distinct positioning options (choose different angles)
3. For each option:
   - Unique position/tagline
   - Key differentiators (3-5 points)
   - Messaging framework
   - Target audience fit
4. Recommended positioning with rationale
5. Potential positioning pitfalls to avoid

Format as structured analysis with clear sections."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.7,
            max_tokens=3072,
        )
        
        if responses:
            return {
                "analysis": responses[0].content,
                "confidence": responses[0].confidence,
            }
        
        return {"analysis": "Positioning analysis failed.", "confidence": 0}
    
    async def generate_positioning_statements(
        self,
        product: str,
        differentiators: List[str],
        target: str = "",
    ) -> List[str]:
        """Generate positioning statements."""
        
        diff_str = "\n".join([f"- {d}" for d in differentiators])
        
        prompt = f"""Generate 5 positioning statements for:

Product: {product}
Differentiators:
{diff_str}
{f"Target Audience: {target}" if target else ""}

Positioning statement format: "For [target audience] who [need], [product] is [category] that [key benefit]. Unlike [competitor], we [key differentiator]."

Generate 5 variations with different emphases."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.COPY_GENERATION,
            temperature=0.7,
            max_tokens=1536,
        )
        
        if responses:
            return responses[0].content.split("\n")
        
        return []
    
    async def analyze_category_position(
        self,
        category: str,
        market_trends: List[str] = None,
    ) -> Dict:
        """Analyze optimal category positioning."""
        
        trends_str = "\n".join([f"- {t}" for t in trends]) if trends else "No specific trends noted"
        
        prompt = f"""Analyze optimal positioning within category:

Category: {category}

Market Trends:
{trends_str}

Provide:
1. Category dynamics (growing/shrinking, fragmented/concentrated)
2. Key success factors in this category
3. Blue ocean opportunities (uncontested space)
4. Red ocean threats (intense competition)
5. Strategic recommendations for entering this space

Be specific and actionable."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.6,
            max_tokens=2048,
        )
        
        return {
            "analysis": responses[0].content if responses else "",
            "confidence": responses[0].confidence if responses else 0,
        }


async def demo():
    """Demo positioning analysis."""
    print("=" * 60)
    print("MARKETIC POSITIONING ANALYZER DEMO")
    print("=" * 60)
    
    analyzer = PositioningAnalyzer()
    
    print("\n🎯 Analyzing Market Positioning...")
    result = await analyzer.analyze(
        product_name="MarketIQ",
        product_description="AI-powered marketing analytics platform that automatically optimizes campaigns for maximum ROAS",
        category="Marketing Analytics & Attribution",
        competitors=["HubSpot", "Marketo", "Pardot", "Google Analytics"],
        target_audience="Growth marketers and CMOs at mid-market SaaS companies",
    )
    
    print(f"\nAnalysis Preview (confidence: {result['confidence']:.0%}):")
    print("-" * 40)
    print(result["analysis"][:800] + "...")
    
    # Generate positioning statements
    print("\n\n💡 Positioning Statements:")
    statements = await analyzer.generate_positioning_statements(
        product="MarketIQ",
        differentiators=[
            "AI that learns from your best campaigns",
            "50% lower CPA on average",
            "Real-time optimization (not daily)",
            "Works with existing tools (no rip-and-replace)",
        ],
        target="Growth marketers tired of manual optimization",
    )
    
    for i, stmt in enumerate(statements[:3], 1):
        print(f"\n  {i}. {stmt}")
    
    return result, statements


if __name__ == "__main__":
    asyncio.run(demo())
