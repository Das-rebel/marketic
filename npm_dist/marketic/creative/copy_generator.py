"""
Ad Copy Generator

Generates high-converting ad copy for multiple platforms.
Uses parallel multi-LLM generation for best results.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from enum import Enum

from ..foundation.llm_router import generate_parallel, TaskType
from ..foundation.memory import save_creative


class AdChannel(Enum):
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"
    META_FEED = "meta_feed"
    META_STORY = "meta_story"
    LINKEDIN_SPONSORED = "linkedin_sponsored"
    TIKTOK = "tiktok"
    TWITTER_PROMOTED = "twitter_promoted"
    YOUTUBE = "youtube"
    EMAIL = "email"


class AdObjective(Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"


@dataclass
class AdCopyRequest:
    """Request for ad copy generation."""
    product_name: str
    product_description: str
    channel: AdChannel
    objective: AdObjective = AdObjective.CONVERSION
    target_audience: str = ""
    key_benefits: List[str] = field(default_factory=list)
    competitor: str = ""
    unique_angle: str = ""
    num_variants: int = 5
    tone: str = "persuasive"  # persuasive, emotional, logical, urgent, friendly


@dataclass
class AdVariant:
    """A single ad copy variant."""
    variant_id: str
    channel: str
    headline: str
    description: str
    cta: str
    primary_keyword: str
    hooks: List[str] = field(default_factory=list)
    confidence: float = 0.0
    performance_prediction: str = ""


class CopyGenerator:
    """
    Generates high-converting ad copy across all channels.
    
    Usage:
        generator = CopyGenerator()
        variants = await generator.generate_variants(
            product_name="AI Marketing Tool",
            product_description="Automated campaign optimization",
            channel=AdChannel.GOOGLE_SEARCH,
            num_variants=5
        )
    """
    
    def __init__(self):
        self.memory = None  # Lazy load to avoid circular imports
        
    def _build_prompt(self, request: AdCopyRequest) -> str:
        """Build prompt for copy generation."""
        
        channel_context = {
            AdChannel.GOOGLE_SEARCH: "Google Search ads - 30 char headline, 90 char description, use keywords naturally",
            AdChannel.GOOGLE_DISPLAY: "Google Display - 90 char headline, 90 char description, visual-friendly language",
            AdChannel.META_FEED: "Meta News Feed - 40 char headline, 125 char description, scroll-stopping hook",
            AdChannel.META_STORY: "Meta Stories - 22 char headline, punchy, action-oriented",
            AdChannel.LINKEDIN_SPONSORED: "LinkedIn Sponsored - professional tone, value-driven, B2B focus",
            AdChannel.TIKTOK: "TikTok - conversational, trendy, Gen-Z friendly, short and snappy",
            AdChannel.TWITTER_PROMOTED: "Twitter Promoted - 280 char limit, thread-friendly, punchy",
            AdChannel.YOUTUBE: "YouTube Ads - 15 sec hook, story arc, clear CTA",
            AdChannel.EMAIL: "Email subject line + preview - urgency, personalization tokens",
        }.get(request.channel, "")
        
        objective_context = {
            AdObjective.AWARENESS: "Focus on brand story, emotion, and memorability",
            AdObjective.CONSIDERATION: "Highlight benefits, social proof, and unique value",
            AdObjective.CONVERSION: "Strong CTA, urgency, risk reversal, offer clarity",
        }.get(request.objective, "")
        
        benefits = ", ".join(request.key_benefits) if request.key_benefits else "key value proposition"
        
        prompt = f"""You are an expert copywriter specializing in high-converting advertising.

Generate {request.num_variants} ad copy variants for:
- Product: {request.product_name}
- Description: {request.product_description}
- Target Audience: {request.target_audience or 'General audience'}
- Key Benefits: {benefits}

Channel: {channel_context}
Objective: {objective_context}
Tone: {request.tone}

{f"Competitor to differentiate from: {request.competitor}" if request.competitor else ""}
{f"Unique Angle: {request.unique_angle}" if request.unique_angle else ""}

For each variant, provide:
1. Headline (within channel character limits)
2. Description/body copy
3. CTA (call-to-action)
4. Primary keyword to include
5. 2-3 attention-grabbing hooks

Return as JSON array with fields: headline, description, cta, primary_keyword, hooks"""
        
        return prompt
    
    async def generate_variants(self, request: AdCopyRequest) -> List[AdVariant]:
        """Generate ad copy variants using parallel LLM execution."""
        
        prompt = self._build_prompt(request)
        
        # Use parallel generation for best results
        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.COPY_GENERATION,
            temperature=0.8,
            max_tokens=2048,
        )
        
        variants = []
        
        # Parse the best response
        for response in responses[:1]:  # Take first (best) response
            try:
                # Try to parse as JSON
                if "[" in response.content:
                    start = response.content.find("[")
                    end = response.content.rfind("]") + 1
                    data = json.loads(response.content[start:end])
                    
                    for item in data[:request.num_variants]:
                        variant = AdVariant(
                            variant_id=str(uuid.uuid4())[:8],
                            channel=request.channel.value,
                            headline=item.get("headline", ""),
                            description=item.get("description", ""),
                            cta=item.get("cta", "Learn More"),
                            primary_keyword=item.get("primary_keyword", ""),
                            hooks=item.get("hooks", []),
                            confidence=response.confidence,
                        )
                        variants.append(variant)
                else:
                    # Fallback to structured text parsing
                    variants = self._parse_text_response(response.content, request)
                    
            except json.JSONDecodeError:
                # Fallback to text parsing
                variants = self._parse_text_response(response.content, request)
        
        # Ensure we have at least one variant
        if not variants:
            variants = [self._create_fallback_variant(request)]
        
        return variants[:request.num_variants]
    
    def _parse_text_response(self, content: str, request: AdCopyRequest) -> List[AdVariant]:
        """Parse text response into variants."""
        variants = []
        lines = content.split("\n")
        
        current_variant = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "Variant", "Headline")):
                if current_variant:
                    variants.append(current_variant)
                current_variant = AdVariant(
                    variant_id=str(uuid.uuid4())[:8],
                    channel=request.channel.value,
                    headline="",
                    description="",
                    cta="Learn More",
                    primary_keyword="",
                )
            
            if current_variant:
                if "headline" in line.lower():
                    current_variant.headline = line.split(":", 1)[-1].strip()
                elif "description" in line.lower() or "body" in line.lower():
                    current_variant.description = line.split(":", 1)[-1].strip()
                elif "cta" in line.lower():
                    current_variant.cta = line.split(":", 1)[-1].strip()
        
        if current_variant:
            variants.append(current_variant)
        
        return variants
    
    def _create_fallback_variant(self, request: AdCopyRequest) -> AdVariant:
        """Create a fallback variant when generation fails."""
        return AdVariant(
            variant_id=str(uuid.uuid4())[:8],
            channel=request.channel.value,
            headline=f"{request.product_name} - Transform Your Marketing",
            description=request.product_description[:100],
            cta="Start Free Trial",
            primary_keyword=request.product_name.split()[0].lower(),
            hooks=["Limited time offer", "Join thousands of marketers"],
            confidence=0.5,
        )
    
    async def generate_for_channel(
        self,
        product_name: str,
        product_description: str,
        channel: str,
        **kwargs
    ) -> List[AdVariant]:
        """Convenience method for single-channel generation."""
        try:
            channel_enum = AdChannel(channel)
        except ValueError:
            channel_enum = AdChannel.GOOGLE_SEARCH
        
        request = AdCopyRequest(
            product_name=product_name,
            product_description=product_description,
            channel=channel_enum,
            **kwargs
        )
        
        return await self.generate_variants(request)
    
    def save_to_library(self, variants: List[AdVariant], campaign_id: str = "") -> int:
        """Save generated variants to creative library."""
        saved = 0
        for variant in variants:
            asset = {
                "asset_id": f"copy_{variant.variant_id}",
                "type": "ad_copy",
                "channel": variant.channel,
                "headline": variant.headline,
                "body": variant.description,
                "cta": variant.cta,
                "tags": [variant.primary_keyword],
                "performance_data": {},
                "used": False,
                "used_in_campaign": campaign_id,
            }
            if save_creative(asset):
                saved += 1
        return saved


async def demo():
    """Demo the copy generator."""
    print("=" * 60)
    print("MARKETIC AD COPY GENERATOR DEMO")
    print("=" * 60)
    
    generator = CopyGenerator()
    
    # Generate Google Search ads
    print("\n📱 Generating Google Search Ad Variants...")
    request = AdCopyRequest(
        product_name="MarketIQ",
        product_description="AI-powered marketing analytics that automatically optimizes your campaigns for maximum ROAS",
        channel=AdChannel.GOOGLE_SEARCH,
        objective=AdObjective.CONVERSION,
        target_audience="Growth marketers, CMOs at SaaS companies",
        key_benefits=["50% lower CPA", "Automated optimization", "Real-time insights"],
        competitor="HubSpot",
        num_variants=5,
    )
    
    variants = await generator.generate_variants(request)
    
    print(f"\nGenerated {len(variants)} variants:")
    for i, v in enumerate(variants, 1):
        print(f"\n  Variant {i} (confidence: {v.confidence:.2f}):")
        print(f"    Headline: {v.headline}")
        print(f"    Description: {v.description[:60]}...")
        print(f"    CTA: {v.cta}")
        print(f"    Keyword: {v.primary_keyword}")
    
    # Save to library
    saved = generator.save_to_library(variants)
    print(f"\n✅ Saved {saved} variants to creative library")
    
    # Generate Meta Feed ads
    print("\n\n📱 Generating Meta Feed Ad Variants...")
    request2 = AdCopyRequest(
        product_name="CopyFlow",
        product_description="Generate high-converting ad copy in seconds using AI",
        channel=AdChannel.META_FEED,
        objective=AdObjective.CONVERSION,
        target_audeness="E-commerce brands, DTC companies",
        key_benefits=["10x faster copy", "A/B tested angles", "All platforms"],
        num_variants=3,
        tone="friendly",
    )
    
    variants2 = await generator.generate_variants(request2)
    print(f"Generated {len(variants2)} Meta variants")
    
    return variants, variants2


if __name__ == "__main__":
    asyncio.run(demo())
