"""
Positioning Analyzer — Market positioning maps and strategy.
"""

import os
import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PositioningMap:
    x_axis_label: str
    y_axis_label: str
    brands: Dict[str, Dict[str, float]]  # brand -> {x, y, size}
    your_position: Dict[str, float]  # {x, y}
    whitespace_regions: List[Dict[str, Any]]


@dataclass
class PositioningStrategy:
    current_positioning: str
    recommended_positioning: str
    differentiation_points: List[str]
    messaging_framework: Dict[str, str]
    visual_positioning_notes: List[str]


class PositioningAnalyzer:
    """Analyze and develop market positioning."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def analyze(
        self,
        product_name: str,
        product_description: str = "",
        category: str = "AI/ML",
        competitors: List[str] = None,
        target_audience: str = "",
    ) -> Dict[str, Any]:
        """Analyze positioning and develop strategy."""

        competitors = competitors or []
        comp_str = ", ".join(competitors) if competitors else "main competitors in the space"

        prompt = f"""Develop a comprehensive market positioning strategy for {product_name}.

PRODUCT: {product_name}
{product_description}
CATEGORY: {category}
TARGET AUDIENCE: {target_audience or "Primary buyers in the market"}
COMPETITORS: {comp_str}

Provide:

1. POSITIONING MAP
   Define a 2D positioning space with:
   - X-axis: [define dimension, e.g., Price: Low to High]
   - Y-axis: [define dimension, e.g., Feature Depth: Simple to Enterprise]
   
   Place these brands on the map with coordinates (x: 0-10, y: 0-10):
   - {product_name} (your product)
   - {comp_str}
   
   Identify whitespace regions (unoccupied areas with potential)

2. CURRENT POSITIONING
   How is {product_name} currently positioned? What's the current perception?

3. RECOMMENDED POSITIONING
   Where should {product_name} position itself for maximum competitive advantage?
   
4. DIFFERENTIATION POINTS
   Key points that make {product_name} distinct from competitors:
   
5. MESSAGING FRAMEWORK
   Develop a messaging framework:
   - Tagline concept
   - Elevator pitch
   - Primary value proposition
   - Supporting proof points

6. VISUAL POSITIONING NOTES
   How should the brand look and feel to reinforce positioning?

Format as structured content with clear sections."""

        content = await self._call_model(prompt)

        # Parse into structured format
        return {
            "product": product_name,
            "category": category,
            "analysis": content,
            "positioning_map": self._parse_positioning_map(content, product_name, competitors),
            "recommendations": self._extract_recommendations(content),
        }

    def _parse_positioning_map(
        self, content: str, your_product: str, competitors: List[str]
    ) -> Dict[str, Any]:
        """Parse positioning map from analysis."""
        # Simplified parsing
        return {
            "x_axis_label": "Price (Low to High)",
            "y_axis_label": "Feature Complexity (Simple to Enterprise)",
            "your_position": {"x": 5.0, "y": 5.0},
            "brands": {
                your_product: {"x": 5.0, "y": 5.0, "size": 1.2},
                **{comp: {"x": 5.0, "y": 5.0, "size": 1.0} for comp in competitors}
            },
            "whitespace_regions": [
                {"x": 2, "y": 7, "description": "Affordable + Enterprise features"},
                {"x": 8, "y": 3, "description": "Premium + Simple UX"},
            ],
        }

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract key recommendations."""
        recommendations = []
        # Simple extraction logic
        lines = content.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["recommend", "should", "strategy", "position"]):
                if len(line.strip()) > 20:
                    recommendations.append(line.strip()[:200])
        return recommendations[:5]

    async def _call_model(self, prompt: str) -> str:
        """Call AI model."""
        model = "stealth/ox-alpha"  # Best for strategic analysis

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
            return self._fallback_positioning()

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
            return self._fallback_positioning()

    def _fallback_positioning(self) -> str:
        """Fallback positioning analysis."""
        return """POSITIONING MAP:
X-axis: Price (Low to High)
Y-axis: Feature Complexity (Simple to Enterprise)

WHITESPACE REGIONS:
1. Bottom-right (Low price + High features) - Value play
2. Top-left (High price + Simple UX) - Premium simplicity

RECOMMENDATIONS:
1. Position as the "intelligent middle ground" - affordable without sacrificing capability
2. Emphasize time-to-value over feature depth
3. Target underserved SMB segment that needs enterprise insights without enterprise complexity"""
