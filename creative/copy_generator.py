"""
Copy Generator — Multi-channel ad copy with variant scoring.
"""

import os
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import re


class AdChannel(str, Enum):
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"
    META_FEED = "meta_feed"
    LINKEDIN_SPONSORED = "linkedin_sponsored"
    EMAIL = "email"


class AdObjective(str, Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"


class ToneStyle(str, Enum):
    PERSUASIVE = "persuasive"
    EMOTIONAL = "emotional"
    LOGICAL = "logical"
    URGENT = "urgent"
    FRIENDLY = "friendly"


@dataclass
class AdVariant:
    variant_id: str
    channel: str
    headline: str
    description: str
    primary_text: str = ""
    cta: str
    hooks: List[str] = field(default_factory=list)
    confidence: float = 0.0
    performance_prediction: Dict[str, float] = field(default_factory=dict)
    character_count: int = 0
    keyword_density: float = 0.0


@dataclass
class AdCopyRequest:
    product_name: str
    product_description: str
    channel: AdChannel = AdChannel.META_FEED
    objective: AdObjective = AdObjective.CONVERSION
    target_audience: str = ""
    key_benefits: List[str] = field(default_factory=list)
    num_variants: int = 5
    tone: str = "persuasive"


# Model routing for copy
COPY_MODEL_TIER = {
    AdChannel.META_FEED: ["deepseek/deepseek-v4-flash", "google/gemini-3.6-flash"],
    AdChannel.GOOGLE_SEARCH: ["qwen/qwen3.7-max"],
    AdChannel.LINKEDIN_SPONSORED: ["stealth/ox-alpha", "qwen/qwen3.7-max"],
    AdChannel.EMAIL: ["google/gemini-3.6-flash"],
    AdChannel.GOOGLE_DISPLAY: ["deepseek/deepseek-v4-flash"],
}


class CopyGenerator:
    """Generate ad copy variants with confidence scoring."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def generate_variants(self, request: AdCopyRequest) -> List[AdVariant]:
        """Generate ad copy variants for the specified channel."""
        
        # Build the generation prompt
        prompt = self._build_prompt(request)
        
        # Get appropriate model
        models = COPY_MODEL_TIER.get(request.channel, ["google/gemini-3.6-flash"])
        primary_model = models[0]
        
        # Generate copy
        copy_text = await self._call_model(primary_model, prompt)
        
        # Parse into structured variants
        variants = self._parse_variants(copy_text, request)
        
        # Score and rank
        for variant in variants:
            self._score_variant(variant, request)
        
        # Sort by confidence
        variants.sort(key=lambda v: v.confidence, reverse=True)
        
        return variants[:request.num_variants]

    def _build_prompt(self, request: AdCopyRequest) -> str:
        """Build generation prompt for the ad copy."""
        
        channel_specs = {
            AdChannel.GOOGLE_SEARCH: {
                "headline_len": "30 chars",
                "desc_len": "90 chars",
                "format": "Headline 1 | Headline 2 | Headline 3 || Description"
            },
            AdChannel.META_FEED: {
                "primary_len": "125 chars",
                "headline_len": "40 chars", 
                "format": "Primary Text (hook + value prop) || Headline || Description"
            },
            AdChannel.LINKEDIN_SPONSORED: {
                "intro_len": "150 chars",
                "body_len": "70 chars",
                "format": "Intro line (attention-grabbing) || Body (value prop) || CTA"
            },
            AdChannel.EMAIL: {
                "subject_len": "50 chars",
                "body_len": "200 chars",
                "format": "Subject Line || Preview Text || Body"
            },
        }
        
        specs = channel_specs.get(request.channel, channel_specs[AdChannel.META_FEED])
        
        tone_map = {
            "persuasive": "compelling, benefit-focused, drives action",
            "emotional": "story-driven, creates connection, evokes feeling",
            "logical": "fact-based, data-driven, rational arguments",
            "urgent": "time-sensitive, creates FOMO, limited-time emphasis",
            "friendly": "conversational, approachable, relatable"
        }
        tone = tone_map.get(request.tone, tone_map["persuasive"])
        
        benefits = ", ".join(request.key_benefits) if request.key_benefits else "key benefits of the product"
        
        prompt = f"""You are an expert direct-response copywriter. Generate {request.num_variants} unique ad copy variants.

PRODUCT: {request.product_name}
DESCRIPTION: {request.product_description}
TARGET AUDIENCE: {request.target_audience or "General consumers"}
CHANNEL: {request.channel.value}
OBJECTIVE: {request.objective.value}
TONE: {tone}

KEY BENEFITS: {benefits}

FORMAT SPECS:
{chr(10).join(f"- {k}: {v}" for k, v in specs.items())}

Generate {request.num_variants} variants. For each provide:
1. A unique hook/angle (different from other variants)
2. Headline (within char limit)
3. Description/primary text (within char limit)  
4. Clear CTA button text

Vary your approaches:
- Variant 1: Lead with a surprising statistic or social proof
- Variant 2: Ask a provocative question
- Variant 3: Use a bold claim or exaggeration
- Variant 4: Focus on fear of missing out
- Variant 5: Highlight the transformation/outcome
- (more variants with different angles)

Format each variant clearly separated."""
        
        return prompt

    async def _call_model(self, model: str, prompt: str) -> str:
        """Call AI model for copy generation."""
        
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
                        "max_tokens": 2000
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
                        "max_tokens": 2000
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
            return self._generate_fallback_copy(prompt)
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self._openai_key)
            
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return resp.choices[0].message.content
        except Exception as e:
            print(f"OpenAI fallback error: {e}")
            return self._generate_fallback_copy(prompt)

    def _parse_variants(self, text: str, request: AdCopyRequest) -> List[AdVariant]:
        """Parse raw model output into structured AdVariant objects."""
        import uuid
        
        variants = []
        
        # Simple parsing: look for numbered sections or clear分隔
        sections = re.split(r'(?:variant\s+\d+|\n\s*\d+[).:]\s*)', text, flags=re.IGNORECASE)
        
        variant_num = 1
        for section in sections:
            if len(section.strip()) < 30:
                continue
            
            # Extract components
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # Try to identify headline, description, CTA
            headline = ""
            description = ""
            primary_text = ""
            cta = ""
            hooks = []
            
            for i, line in enumerate(lines):
                # Skip very short lines
                if len(line) < 5:
                    continue
                    
                # CTA patterns
                if any(cta_word in line.lower() for cta_word in ['click', 'sign up', 'get', 'try', 'start', 'learn more', 'book', 'download']):
                    if not cta:
                        cta = line.strip()
                    continue
                
                # Headline: usually short and punchy
                if len(line) < 60 and not headline:
                    headline = line.strip()
                elif len(line) < 100 and not description:
                    description = line.strip()
                else:
                    primary_text += " " + line.strip()
            
            # Fallbacks
            if not headline and lines:
                headline = lines[0][:60]
            if not description and len(lines) > 1:
                description = lines[1][:100] if len(lines) > 1 else ""
            if not cta:
                cta_map = {
                    AdChannel.META_FEED: "Shop Now",
                    AdChannel.GOOGLE_SEARCH: "Learn More",
                    AdChannel.LINKEDIN_SPONSORED: "Get Started",
                    AdChannel.EMAIL: "Subscribe",
                    AdChannel.GOOGLE_DISPLAY: "Learn More",
                }
                cta = cta_map.get(request.channel, "Learn More")
            
            if primary_text:
                primary_text = primary_text.strip()
            
            variants.append(AdVariant(
                variant_id=str(uuid.uuid4())[:8],
                channel=request.channel.value,
                headline=headline,
                description=description,
                primary_text=primary_text,
                cta=cta,
                hooks=hooks[:3],
                character_count=len(headline) + len(description) + len(primary_text),
            ))
            
            variant_num += 1
            if variant_num > request.num_variants:
                break
        
        # If parsing failed, create at least one variant from the full text
        if not variants and text:
            variants.append(AdVariant(
                variant_id=str(uuid.uuid4())[:8],
                channel=request.channel.value,
                headline=text[:60],
                description=text[60:150] if len(text) > 60 else "",
                cta="Learn More",
            ))
        
        return variants

    def _score_variant(self, variant: AdVariant, request: AdCopyRequest):
        """Score variant confidence based on multiple factors."""
        score = 0.5  # Base score
        
        # Length scoring (within spec = good)
        total_len = variant.character_count
        if request.channel == AdChannel.GOOGLE_SEARCH:
            if len(variant.headline) <= 30:
                score += 0.1
            if len(variant.description) <= 90:
                score += 0.1
        elif request.channel == AdChannel.META_FEED:
            if 80 <= len(variant.primary_text) <= 125:
                score += 0.15
        
        # CTA present
        if variant.cta and len(variant.cta) > 0:
            score += 0.1
        
        # Hooks present
        if variant.hooks:
            score += 0.1
        
        # Keyword density in benefits
        if request.key_benefits:
            text_lower = (variant.headline + " " + variant.description + " " + variant.primary_text).lower()
            keyword_matches = sum(1 for kw in request.key_benefits if kw.lower() in text_lower)
            variant.keyword_density = keyword_matches / len(request.key_benefits)
            score += variant.keyword_density * 0.15
        
        # Objective alignment
        if request.objective == AdObjective.CONVERSION:
            if any(word in (variant.headline + variant.cta).lower() for word in ['buy', 'get', 'start', 'try', 'sign']):
                score += 0.1
        elif request.objective == AdObjective.AWARENESS:
            if any(word in variant.headline.lower() for word in ['introducing', 'new', 'now', 'finally']):
                score += 0.1
        
        # Cap at 0.99
        variant.confidence = min(score, 0.99)
        
        # Performance prediction (simplified model)
        variant.performance_prediction = {
            "ctr": round(0.01 + variant.confidence * 0.04, 4),
            "conversion_rate": round(0.02 + variant.confidence * 0.08, 4),
            "estimated_roas": round(1.5 + variant.confidence * 2.5, 2),
        }

    def _generate_fallback_copy(self, prompt: str) -> str:
        """Generate basic copy without AI (fallback)."""
        # Extract product name from prompt if possible
        product_match = re.search(r'PRODUCT:\s*(.+?)(?:\n|$)', prompt)
        product = product_match.group(1).strip() if product_match else "This Product"
        
        fallback = f"""Variant 1:
Headline: Transform Your {product} Experience Today
Description: Discover how {product} can help you achieve better results faster.
CTA: Get Started

Variant 2:
Headline: Why {product} Changes Everything
Description: Join thousands who've already made the switch.
CTA: Learn More

Variant 3:
Headline: {product} — Built for Results
Description: Everything you need, nothing you don't.
CTA: Try Free

Variant 4:
Headline: Don't Miss Out on {product}
Description: Limited time offer for new customers.
CTA: Claim Offer

Variant 5:
Headline: {product} — The Smart Choice
Description: Quality meets affordability in one powerful solution.
CTA: Shop Now"""
        
        return fallback


# Standalone test
if __name__ == "__main__":
    async def test():
        gen = CopyGenerator()
        request = AdCopyRequest(
            product_name="TaskFlow Pro",
            product_description="AI-powered project management tool that automates workflows and boosts team productivity by 40%",
            channel=AdChannel.META_FEED,
            objective=AdObjective.CONVERSION,
            target_audience="Remote team managers and startup founders",
            key_benefits=["40% productivity boost", "Automated workflows", "Real-time collaboration"],
            num_variants=5,
            tone="persuasive"
        )
        
        variants = await gen.generate_variants(request)
        
        print(f"\nGenerated {len(variants)} variants:\n")
        for i, v in enumerate(variants, 1):
            print(f"--- Variant {i} (confidence: {v.confidence:.0%}) ---")
            print(f"Headline: {v.headline}")
            print(f"Description: {v.description}")
            print(f"Primary Text: {v.primary_text}")
            print(f"CTA: {v.cta}")
            print(f"Predicted CTR: {v.performance_prediction['ctr']:.2%}")
            print()
    
    asyncio.run(test())
