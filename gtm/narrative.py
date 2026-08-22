"""
Narrative Generator — Brand stories and messaging frameworks.
"""

import os
import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BrandStory:
    company_name: str
    narrative_type: str
    story_text: str
    key_messages: List[str]
    supporting_elements: List[str]
    cta: str


class NarrativeGenerator:
    """Generate brand narratives and stories."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def generate_brand_story(
        self,
        company_name: str,
        mission: str = "",
        founder_story: str = "",
        values: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate brand story narrative."""

        values_str = ", ".join(values) if values else "innovation, customer focus, integrity"

        prompt = f"""Create a compelling brand story for {company_name}.

MISSION/VISION: {mission or "Building the future with AI"}
FOUNDER STORY: {founder_story or "No specific founder story provided"}
COMPANY VALUES: {values_str}

Develop:

1. BRAND ORIGIN STORY
   A compelling narrative about how {company_name} came to be. Include:
   - The problem that existed
   - The insight or breakthrough
   - Why this matters now

2. THE TRANSFORMATION
   What change does {company_name} create for customers?
   - Before state
   - The journey
   - After state

3. KEY BRAND MESSAGES (3-5)
   Core messages that should appear across all communications:
   
4. SUPPORTING STORY ELEMENTS
   - Customer success themes
   - Company culture highlights
   - Industry context

5. BRAND VOICE NOTES
   How should {company_name} sound in communications?

6. RECOMMENDED CTA
   Call to action that aligns with brand story

Keep tone: Authentic, inspiring, customer-centric (not company glorifying)"""

        content = await self._call_model(prompt)

        # Parse into structured format
        return {
            "company": company_name,
            "story": content,
            "key_messages": self._extract_messages(content),
            "story_type": "brand_origin",
        }

    async def generate_thought_leadership(
        self,
        brand: str,
        industry: str,
        topic: str,
    ) -> Dict[str, Any]:
        """Generate thought leadership content."""

        prompt = f"""Create thought leadership content for {brand} on: {topic}

INDUSTRY: {industry}

Develop:

1. CONTRARIAN INSIGHT
   A counterintuitive take on {topic} that challenges conventional thinking

2. SUPPORTING ARGUMENTS
   3-4 points that support this contrarian view
   Include specific examples or data points

3. IMPLICATIONS
   What this means for the industry and practitioners

4. BRAND CONNECTION
   How does {brand} embody this insight?

5. ENGAGEMENT HOOK
   A provocative question or statement to start the piece

Tone: Authoritative but accessible, challenging but respectful"""

        content = await self._call_model(prompt)

        return {
            "brand": brand,
            "topic": topic,
            "content": content,
            "content_type": "thought_leadership",
        }

    async def generate_industry_analysis(
        self,
        brand: str,
        industry: str,
    ) -> Dict[str, Any]:
        """Generate industry analysis narrative."""

        prompt = f"""Create an industry analysis narrative for {brand} operating in {industry}.

Cover:

1. INDUSTRY CONTEXT
   The major shifts happening in {industry} right now

2. PAIN POINTS
   The biggest challenges practitioners face today

3. EMERGING TRENDS
   3-5 trends shaping the future of {industry}

4. OPPORTUNITIES
   Where is growth happening? What opportunities exist?

5. BRAND POSITIONING
   How should {brand} position itself to capitalize on these trends?

6. KEY TALKING POINTS
   For sales and marketing to use

Format as a comprehensive industry brief."""

        content = await self._call_model(prompt)

        return {
            "brand": brand,
            "industry": industry,
            "analysis": content,
            "content_type": "industry_analysis",
        }

    async def _call_model(self, prompt: str) -> str:
        """Call AI model."""
        model = "stealth/ox-alpha"  # Best for narrative

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
                        "max_tokens": 2500
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
                        "max_tokens": 2500
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
            return self._fallback_narrative()

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self._openai_key)

            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500
            )

            return resp.choices[0].message.content
        except Exception as e:
            print(f"OpenAI fallback error: {e}")
            return self._fallback_narrative()

    def _extract_messages(self, content: str) -> List[str]:
        """Extract key messages from narrative."""
        messages = []
        lines = content.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["message", "key point", "core", "central"]):
                if len(line.strip()) > 15:
                    messages.append(line.strip()[:150])
        return messages[:5]

    def _fallback_narrative(self) -> str:
        """Fallback narrative."""
        return """BRAND STORY:

Every great company starts with a simple observation: the way things are done isn't the way they have to be.

[Company Name] was founded on the belief that technology should work for people, not the other way around. We saw businesses struggling with complexity, drowning in data, and spending more time managing tools than actually succeeding.

That's why we built something different. Not another feature-heavy platform that adds to the noise—but a solution that cuts through it. Something that understands what you actually need and delivers it without friction.

Today, we're helping businesses of all sizes transform how they work. From startups to enterprises, teams are discovering that success doesn't have to be complicated.

The story continues with every customer who chooses to work differently. With every team that discovers a better way. With every business that realizes: the future isn't about more tools. It's about smarter decisions.

[Company Name]. Work smarter.

---

KEY MESSAGES:
1. We simplify complexity
2. Technology should enhance, not distract
3. Every customer is a partner in our journey
4. Better decisions, not more effort

CTA: Join the businesses already working smarter."""
