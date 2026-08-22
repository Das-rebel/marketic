"""
Competitive Intelligence — Deep competitive analysis.
"""

import os
import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CompetitiveAnalysis:
    brand: str
    category: str
    positioning: Dict[str, Any]
    messaging: Dict[str, Any]
    ad_strategy: Dict[str, Any]
    audience_targeting: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    swot_summary: str
    competitive_moves: List[Dict[str, str]]


@dataclass
class CompetitorComparison:
    your_product: str
    competitors: List[str]
    feature_matrix: Dict[str, Dict[str, bool]]
    price_comparison: Dict[str, float]
    positioning_differences: Dict[str, str]
    recommendations: List[str]


class CompetitiveIntelligence:
    """Analyze competitive landscape."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def analyze_competitor(
        self, competitor_name: str, category: str = ""
    ) -> Dict[str, Any]:
        """Deep-dive competitive analysis."""

        # Build analysis prompt
        prompt = f"""Analyze the competitive landscape for {competitor_name} in the {category or "general"} space.

Provide a comprehensive analysis covering:

1. POSITIONING
   - Core value proposition
   - Market position (premium, mid-market, budget)
   - Key differentiators
   - Brand personality and tone

2. MESSAGING STRATEGY
   - Primary messaging themes
   - Taglines and slogans
   - Content marketing approach
   - Emotional vs rational appeals

3. ADVERTISING STRATEGY
   - Primary ad channels
   - Creative approach (visuals, format, tone)
   - Offers and promotions
   - Seasonal campaign patterns

4. AUDIENCE TARGETING
   - Target demographics
   - Psychographics
   - Geographic focus
   - B2B vs B2C focus

5. STRENGTHS (What they do well)
   - Top 3-5 competitive advantages
   - Market perception strengths
   - Product advantages

6. WEAKNESSES (Vulnerabilities)
   - Top 3-5 gaps or vulnerabilities
   - Customer complaints patterns
   - Product limitations
   - Market perception issues

7. OPPORTUNITIES (Market gaps to exploit)
   - Underserved segments
   - Unmet needs
   - Emerging trends to capitalize on

8. THREATS (Risks to monitor)
   - Competitive threats
   - Market disruptions
   - Regulatory risks

9. RECOMMENDED COMPETITIVE MOVES
   - Specific actions to gain advantage
   - Messaging angles to emphasize
   - Channels to target

Format as structured JSON with these exact keys."""

        content = await self._call_model(prompt)

        # Parse response (simplified - would need robust parsing in production)
        return {
            "competitor": competitor_name,
            "category": category,
            "analysis": content,
            "raw_insights": self._extract_insights(content),
        }

    async def compare_with_competitors(
        self, your_product: str, competitors: List[str]
    ) -> Dict[str, Any]:
        """Compare your product against multiple competitors."""

        comp_list = ", ".join(competitors)

        prompt = f"""Compare {your_product} against competitors: {comp_list}

Create a detailed comparison:

1. FEATURE MATRIX
   List key features down the rows, competitors across columns.
   Mark each cell as: Yes (full), Partial, No, or N/A

2. PRICING COMPARISON
   - Subscription tiers
   - Entry-level pricing
   - Enterprise pricing
   - Free tiers or trials

3. POSITIONING DIFFERENCES
   How does each competitor position themselves differently?

4. YOUR ADVANTAGES
   Where do you have clear competitive advantages?

5. THEIR ADVANTAGES  
   Where do competitors have clear advantages?

6. MARKET GAPS
   Underserved needs or segments no one addresses well

7. RECOMMENDATIONS
   - How to compete against each competitor
   - Which competitor to target first
   - Differentiation strategies

Format as structured JSON."""

        content = await self._call_model(prompt)

        return {
            "your_product": your_product,
            "competitors": competitors,
            "comparison": content,
        }

    async def _call_model(self, prompt: str) -> str:
        """Call AI model for analysis."""
        model = "stealth/ox-alpha"  # Best for analysis

        if model.startswith("stealth/"):
            return await self._call_openrouter(model, prompt)
        elif model.startswith(("google/", "qwen/", "deepseek/")):
            return await self._call_openrouter(model, prompt)
        elif model.startswith("minimax/"):
            return await self._call_opencode_go(model, prompt)
        else:
            return await self._call_openai_fallback(prompt)

    async def _call_openrouter(self, model: str, prompt: str) -> str:
        """Call OpenRouter API."""
        if not self._openrouter_key:
            return await self._call_openai_fallback(prompt)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self._openrouter_key}"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 3000
                    }
                )

                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter error: {e}")

        return await self._call_openai_fallback(prompt)

    async def _call_opencode_go(self, model: str, prompt: str) -> str:
        """Call OpenCode Go API."""
        if not self._opencode_key:
            return await self._call_openai_fallback(prompt)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://opencode.ai/zen/go/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self._opencode_key}"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 3000
                    }
                )

                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenCode Go error: {e}")

        return await self._call_openai_fallback(prompt)

    async def _call_openai_fallback(self, prompt: str) -> str:
        """Fallback to OpenAI API."""
        if not self._openai_key:
            return self._fallback_analysis()

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self._openai_key)

            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )

            return resp.choices[0].message.content
        except Exception as e:
            print(f"OpenAI fallback error: {e}")
            return self._fallback_analysis()

    def _extract_insights(self, content: str) -> Dict[str, Any]:
        """Extract key insights from raw content."""
        # Simplified extraction
        return {
            "summary": content[:500] if len(content) > 500 else content,
            "key_themes": [],
            "data_points": [],
        }

    def _fallback_analysis(self) -> str:
        """Fallback analysis when API unavailable."""
        return """{
  "positioning": {
    "core_value_proposition": "Analysis requires live API access",
    "market_position": "Premium",
    "key_differentiators": ["Feature 1", "Feature 2", "Feature 3"]
  },
  "messaging": {
    "primary_themes": ["Theme 1", "Theme 2"],
    "tone": "Professional"
  },
  "swot": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "opportunities": ["Opportunity 1"],
    "threats": ["Threat 1"]
  }
}"""
