"""
SEO Generator — SEO-optimized content with meta tags, headers, and FAQs.
"""

import os
import httpx
import asyncio
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ContentType(str, Enum):
    LANDING_PAGE = "landing_page"
    BLOG_POST = "blog_post"
    PRODUCT_PAGE = "product_page"
    FAQ = "faq"


@dataclass
class SEOContent:
    meta_title: str
    meta_description: str
    h1: str
    h2_headers: List[str] = field(default_factory=list)
    h3_headers: List[str] = field(default_factory=list)
    body_content: str = ""
    faq_section: List[Dict[str, str]] = field(default_factory=list)
    internal_link_suggestions: List[str] = field(default_factory=list)
    keyword_density: float = 0.0
    readability_score: float = 0.0
    estimated_read_time_minutes: int = 0
    word_count: int = 0


@dataclass
class SEOContentRequest:
    keyword: str
    content_type: ContentType = ContentType.BLOG_POST
    target_length: int = 1500
    competitor_url: str = ""


class SEOGenerator:
    """Generate SEO-optimized content."""

    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
        self._openai_key = os.environ.get("OPENAI_API_KEY")

    async def generate(self, request: SEOContentRequest) -> SEOContent:
        """Generate SEO content."""
        
        # Build generation prompt
        prompt = self._build_prompt(request)
        
        # Select model
        model = "qwen/qwen3.7-max"  # Good for structured content
        
        # Generate content
        content = await self._call_model(model, prompt)
        
        # Parse into SEO structure
        seo_content = self._parse_content(content, request)
        
        # Score SEO quality
        self._score_seo(seo_content, request)
        
        return seo_content

    def _build_prompt(self, request: SEOContentRequest) -> str:
        """Build SEO content generation prompt."""
        
        type_specs = {
            ContentType.BLOG_POST: {
                "sections": "1. Hook/intro (compelling opening)\n2. Key points (H2 headers)\n3. Supporting content under each H2\n4. FAQ section (5 questions)\n5. Conclusion with CTA",
                "length_note": f"Target {request.target_length} words",
            },
            ContentType.LANDING_PAGE: {
                "sections": "1. Hero section with H1\n2. Value proposition (H2)\n3. Features/benefits (H2/H3)\n4. Social proof\n5. FAQ\n6. Final CTA",
                "length_note": "Keep concise, conversion-focused",
            },
            ContentType.PRODUCT_PAGE: {
                "sections": "1. Product name (H1)\n2. Tagline\n3. Features (H2/H3)\n4. Specifications\n5. FAQ\n6. Purchase CTA",
                "length_note": "Clear, scannable, benefit-focused",
            },
            ContentType.FAQ: {
                "sections": "1. Intro paragraph\n2. 8-10 FAQ items (Question in bold, answer below)\n3. CTA to contact or learn more",
                "length_note": f"Target {request.target_length} words total",
            },
        }
        
        specs = type_specs.get(request.content_type, type_specs[ContentType.BLOG_POST])
        
        prompt = f"""You are an expert SEO content writer. Generate optimized content for the keyword: "{request.keyword}"

CONTENT TYPE: {request.content_type.value}
{stype_specs["length_note"]}

SECTIONS TO INCLUDE:
{type_specs["sections"]}

REQUIREMENTS:
1. Meta title: Under 60 characters, includes main keyword
2. Meta description: Under 160 characters, compelling, includes keyword
3. Use keyword naturally throughout (1-2% density)
4. H1 should be catchy, includes keyword
5. H2 headers should be descriptive, benefit-driven
6. FAQ: Answer common questions concisely
7. Write for humans first, search engines second
8. Include a clear CTA

COMPETITOR REFERENCE: {request.competitor_url if request.competitor_url else "None provided"}

Generate the full SEO content with all sections clearly labeled:"""
        
        return prompt

    async def _call_model(self, model: str, prompt: str) -> str:
        """Call AI model."""
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
            return self._fallback_content()
        
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
            return self._fallback_content()

    def _parse_content(self, text: str, request: SEOContentRequest) -> SEOContent:
        """Parse raw content into SEO structure."""
        
        lines = text.split('\n')
        
        meta_title = ""
        meta_description = ""
        h1 = ""
        h2_headers = []
        h3_headers = []
        faq_items = []
        body_sections = []
        in_faq = False
        current_faq_q = ""
        current_faq_a = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Meta title
            if line.lower().startswith("meta title:") or line.lower().startswith("title:"):
                meta_title = re.sub(r'^(?:meta\s+)?title:\s*', '', line, flags=re.IGNORECASE).strip('"').strip()
                continue
            
            # Meta description
            if line.lower().startswith("meta description:") or line.lower().startswith("description:"):
                meta_description = re.sub(r'^(?:meta\s+)?description:\s*', '', line, flags=re.IGNORECASE).strip('"').strip()
                continue
            
            # H1
            if line.startswith("# ") and not h1:
                h1 = line[2:].strip()
                continue
            
            # H2
            if line.startswith("## "):
                h2_text = line[3:].strip()
                if h2_text.lower().startswith("faq"):
                    in_faq = True
                    continue
                h2_headers.append(h2_text)
                in_faq = False
                continue
            
            # H3
            if line.startswith("### "):
                h3_headers.append(line[4:].strip())
                continue
            
            # FAQ items
            if in_faq:
                if line.startswith("**") or line.startswith("Q:"):
                    # Save previous FAQ if exists
                    if current_faq_q:
                        faq_items.append({"question": current_faq_q, "answer": current_faq_a.strip()})
                    
                    # Start new FAQ
                    current_faq_q = re.sub(r'^\*\*|\*\*$|:$|^Q:\s*', '', line).strip()
                    current_faq_a = ""
                elif current_faq_q:
                    current_faq_a += " " + line
                continue
            
            # Body content
            if line and not line.startswith("---"):
                body_sections.append(line)
        
        # Save last FAQ
        if current_faq_q:
            faq_items.append({"question": current_faq_q, "answer": current_faq_a.strip()})
        
        # Calculate metrics
        all_text = " ".join(body_sections)
        word_count = len(all_text.split())
        estimated_read_time = max(1, round(word_count / 200))
        
        # Build body content string
        body_content = "\n\n".join(body_sections)
        
        return SEOContent(
            meta_title=meta_title or f"Best {request.keyword} - Complete Guide",
            meta_description=meta_description or f"Learn everything about {request.keyword}. Expert tips, strategies, and insights to help you succeed.",
            h1=h1 or f"The Ultimate Guide to {request.keyword}",
            h2_headers=h2_headers,
            h3_headers=h3_headers,
            body_content=body_content,
            faq_section=faq_items,
            word_count=word_count,
            estimated_read_time_minutes=estimated_read_time,
        )

    def _score_seo(self, content: SEOContent, request: SEOContentRequest):
        """Score SEO quality."""
        keyword = request.keyword.lower()
        all_text = (content.h1 + " " + content.meta_title + " " + content.meta_description + " " + content.body_content).lower()
        word_count = max(1, len(all_text.split()))
        
        # Keyword density
        keyword_count = all_text.count(keyword)
        content.keyword_density = round(keyword_count / word_count * 100, 2)
        
        # Meta title scoring
        meta_title_score = 0.0
        if keyword in content.meta_title.lower():
            meta_title_score += 0.3
        if len(content.meta_title) <= 60:
            meta_title_score += 0.2
        if content.meta_title.startswith(keyword):
            meta_title_score += 0.1
        
        # Meta description scoring
        meta_desc_score = 0.0
        if keyword in content.meta_description.lower():
            meta_desc_score += 0.3
        if len(content.meta_description) <= 160:
            meta_desc_score += 0.2
        
        # Content length scoring
        length_score = 0.0
        if 1000 <= content.word_count <= 3000:
            length_score += 0.3
        elif content.word_count >= 500:
            length_score += 0.1
        
        # Structure scoring
        structure_score = 0.0
        if content.h1:
            structure_score += 0.1
        if len(content.h2_headers) >= 3:
            structure_score += 0.15
        if len(content.faq_section) >= 3:
            structure_score += 0.1
        
        # Keyword density scoring
        density_score = 0.0
        if 1.0 <= content.keyword_density <= 2.5:
            density_score += 0.25
        elif content.keyword_density > 0:
            density_score += 0.1
        
        # Readability (simplified)
        content.readability_score = round(
            min(1.0, (meta_title_score + meta_desc_score + length_score + structure_score + density_score) / 1.8),
            2
        )
        
        # Internal link suggestions
        content.internal_link_suggestions = [
            f"Related guide on {request.keyword} best practices",
            f"How to get started with {request.keyword}",
            f"Common {request.keyword} mistakes to avoid",
        ]

    def _fallback_content(self) -> str:
        """Fallback content when API is unavailable."""
        return f"""Meta Title: Best Practices for SEO Success
Meta Description: Learn the top SEO strategies to improve your search rankings and drive more traffic to your website.

# The Complete SEO Guide

## Why SEO Matters

Search engine optimization is critical for any business looking to establish a strong online presence. When done correctly, SEO can drive consistent, high-quality traffic to your website without paying for advertisements.

## Key SEO Strategies

### 1. Keyword Research

Start with thorough keyword research to understand what your audience is searching for. Use tools like Google Keyword Planner, SEMrush, or Ahrefs to find relevant keywords with good search volume and reasonable competition.

### 2. On-Page Optimization

Ensure each page is optimized for your target keywords. This includes:
- Unique, compelling meta titles
- Descriptive meta descriptions
- Proper header structure (H1, H2, H3)
- Optimized content with natural keyword usage

### 3. Technical SEO

Technical SEO ensures search engines can crawl and index your site effectively:
- Fast page load speeds
- Mobile-responsive design
- Clean URL structures
- XML sitemaps

### 4. Content Marketing

Create high-quality, valuable content that answers your audience's questions. Regular blog posts, guides, and resources build authority and attract backlinks.

## FAQ

**Q: How long does SEO take to show results?**
A: Typically 3-6 months to see significant improvements, though some changes can show impact within weeks.

**Q: What's more important, on-page or off-page SEO?**
A: Both are essential. On-page SEO establishes relevance; off-page SEO builds authority.

**Q: How often should I update my content?**
A: Review and update key pages quarterly, and refresh blog posts when information becomes outdated.

## Conclusion

SEO is a long-term investment. Focus on creating valuable content, optimizing for users, and building genuine authority. Avoid shortcuts and black-hat techniques that can result in penalties."""
