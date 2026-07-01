"""
Narrative Generator

Market narrative and storytelling for brands.
"""

import asyncio
from typing import Dict, List

from ..foundation.llm_router import generate_parallel, TaskType


class NarrativeGenerator:
    """
    Generate market narratives, brand stories, and thought leadership content.
    
    Usage:
        narrative = NarrativeGenerator()
        story = await narrative.generate_brand_story(
            company="MarketIQ",
            mission="Make AI marketing accessible"
        )
    """
    
    async def generate_brand_story(
        self,
        company_name: str,
        mission: str,
        founder_story: str = "",
        values: List[str] = None,
    ) -> str:
        """Generate a compelling brand story."""
        
        values_str = "\n".join([f"- {v}" for v in values]) if values else "Innovation, Customer Focus, Integrity"
        
        prompt = f"""Write a compelling brand story for {company_name}:

Mission: {mission}
{f"Founder Story: {founder_story}" if founder_story else ""}
Values:
{values_str}

Structure the story with:
1. Opening hook (the problem/challenge)
2. Founding moment
3. The journey (challenges overcome)
4. What makes them different
5. Mission fulfillment
6. Vision for the future

Make it authentic, inspiring, and memorable.
Format as flowing narrative, not bullet points."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.COPY_GENERATION,
            temperature=0.8,
            max_tokens=2048,
        )
        
        return responses[0].content if responses else ""
    
    async def generate_thought_leadership(
        self,
        topic: str,
        angle: str = "",
        target_audience: str = "",
    ) -> Dict:
        """Generate thought leadership content."""
        
        prompt = f"""Create thought leadership content on:

Topic: {topic}
{f"Angle/Perspective: {angle}" if angle else ""}
{f"Target Audience: {target_audience}" if target_audience else ""}

Generate:
1. A contrarian or unique take (the "hot take")
2. Supporting arguments with examples
3. Evidence and data points
4. Implications for the industry
5. Call to action or next steps

Make it insightful, debatable, and valuable.
Be bold in your perspectives while remaining credible."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.75,
            max_tokens=2560,
        )
        
        return {
            "topic": topic,
            "content": responses[0].content if responses else "",
            "confidence": responses[0].confidence if responses else 0,
        }
    
    async def generate_industry_analysis(
        self,
        industry: str,
        time_horizon: str = "3 years",
    ) -> str:
        """Generate industry analysis and predictions."""
        
        prompt = f"""Write an industry analysis for {industry}:

Time Horizon: {time_horizon}

Cover:
1. Current state of the industry
2. Major trends shaping the future
3. Disruption forces (technology, regulation, behavior)
4. Emerging opportunities
5. Threats and challenges
6. Strategic implications for players in this space

Be specific with examples and data where possible.
Make bold but credible predictions."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.STRATEGY,
            temperature=0.6,
            max_tokens=3072,
        )
        
        return responses[0].content if responses else ""


async def demo():
    """Demo narrative generation."""
    print("=" * 60)
    print("MARKETIC NARRATIVE GENERATOR DEMO")
    print("=" * 60)
    
    narrative = NarrativeGenerator()
    
    # Generate brand story
    print("\n📖 Generating Brand Story...")
    story = await narrative.generate_brand_story(
        company_name="MarketIQ",
        mission="To make AI-powered marketing accessible to every business, not just enterprises",
        founder_story="Built by a growth marketer who spent too many nights manually adjusting bids",
        values=["Democratize AI marketing", "Customer success first", "Transparent & honest", "Ship fast"],
    )
    
    print(f"\nBrand Story Preview:")
    print("-" * 40)
    print(story[:700] + "...")
    
    # Generate thought leadership
    print("\n\n💡 Generating Thought Leadership...")
    leadership = await narrative.generate_thought_leadership(
        topic="The future of performance marketing",
        angle="AI will replace intuition-driven optimization within 3 years",
        target_audience="Growth marketers and CMOs",
    )
    
    print(f"\nThought Leadership Preview:")
    print(leadership["content"][:500] + "...")
    
    return story, leadership


if __name__ == "__main__":
    asyncio.run(demo())
