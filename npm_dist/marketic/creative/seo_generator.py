"""
SEO & GEO Content Generator

Generates SEO-optimized blog posts and articles.
Also handles GEO (Generative Engine Optimization) for AI search.

Features:
- Keyword-optimized blog posts
- Meta descriptions
- Header structure (H1, H2, H3)
- Internal/external linking suggestions
- GEO-optimized content for ChatGPT, Perplexity, Gemini
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

from ..foundation.llm_router import generate_parallel, TaskType


@dataclass
class SEOContentRequest:
    """Request for SEO content generation."""
    keyword: str
    title: str = ""
    target_length: int = 2000  # words
    target_audience: str = ""
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    competitor_urls: List[str] = field(default_factory=list)
    include_geo_optimization: bool = True  # Optimize for AI search engines
    include_faq: bool = True
    tone: str = "informative"  # informative, conversational, professional
    content_type: str = "blog_post"  # blog_post, landing_page, guide, comparison


@dataclass
class SEOContent:
    """Generated SEO content with metadata."""
    content_id: str
    title: str
    meta_title: str
    meta_description: str
    keywords: List[str]
    content: str  # Full HTML or Markdown
    headings: Dict[str, str]  # H1, H2, H3 structure
    word_count: int
    readability_score: str  # easy, medium, hard
    geo_optimized: bool
    faq_section: List[Dict[str, str]] = field(default_factory=list)
    linking_suggestions: Dict[str, List[str]] = field(default_factory=dict)
    confidence: float = 0.0


class SEOGenerator:
    """
    Generates SEO-optimized content for blog posts and articles.
    Includes GEO optimization for AI search engines.
    
    Usage:
        generator = SEOGenerator()
        content = await generator.generate(
            keyword="marketing automation",
            target_length=2500,
            include_geo_optimization=True
        )
    """
    
    def _build_prompt(self, request: SEOContentRequest) -> str:
        """Build prompt for SEO content generation."""
        
        content_type_guidance = {
            "blog_post": "Write as a comprehensive blog post with introduction, body sections, and conclusion",
            "landing_page": "Write as a high-converting landing page with strong CTA sections",
            "guide": "Write as an in-depth how-to guide with step-by-step instructions",
            "comparison": "Write as a comparison article analyzing multiple options",
        }.get(request.content_type, "Write as a blog post")
        
        geo_guidance = ""
        if request.include_geo_optimization:
            geo_guidance = """
GEO (Generative Engine Optimization) Requirements:
- Answer common questions directly and concisely (AI bots extract these)
- Use clear, factual statements (avoid hedging)
- Include specific numbers, statistics, and named examples
- Structure content so AI can easily cite key facts
- Add a FAQ section at the end
- Use headers that match search intent"""
        
        primary_kw = ", ".join(request.primary_keywords) if request.primary_keywords else request.keyword
        secondary_kw = ", ".join(request.secondary_keywords) if request.secondary_keywords else ""
        
        prompt = f"""You are an expert SEO content writer creating {request.content_type.replace('_', ' ')} content.

Create comprehensive SEO-optimized content for:
- Primary Keyword: {request.keyword}
- {f"Secondary Keywords: {secondary_kw}" if secondary_kw else ""}
- Target Length: ~{request.target_length} words
- Target Audience: {request.target_audience or 'General readers'}
- Tone: {request.tone}

{content_type_guidance}
{geo_guidance}

Structure your response as JSON with these exact fields:
{{
    "title": "SEO-optimized H1 title",
    "meta_title": "50-60 char meta title with keyword",
    "meta_description": "150-160 char meta description with CTA",
    "keywords": ["list of 5-10 relevant keywords"],
    "content": "Full article content in Markdown format",
    "headings": {{"H1": "title", "H2": ["section1", "section2"], "H3": ["subsection1"]}},
    "word_count": estimated_words,
    "readability_score": "easy/medium/hard",
    "faq_section": [{{"question": "q", "answer": "a"}}],
    "linking_suggestions": {{"internal": ["url1"], "external": ["source1"]}}
}}

Ensure:
1. Title includes primary keyword naturally
2. First 100 words contain keyword and provide value
3. Headers are keyword-rich but readable
4. Content answers search intent fully
5. Include relevant examples and actionable advice
6. End with clear CTA or next steps"""
        
        return prompt
    
    async def generate(self, request: SEOContentRequest) -> SEOContent:
        """Generate SEO content."""
        
        prompt = self._build_prompt(request)
        
        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.SEO_CONTENT,
            temperature=0.7,
            max_tokens=4096,
        )
        
        for response in responses[:1]:
            try:
                # Extract JSON from response
                content = response.content
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    content = content[start:end]
                elif "```" in content:
                    start = content.find("```") + 3
                    end = content.rfind("```")
                    content = content[start:end]
                
                if "{" in content and "}" in content:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    data = json.loads(content[start:end])
                    
                    return SEOContent(
                        content_id=str(uuid.uuid4())[:8],
                        title=data.get("title", request.title or request.keyword),
                        meta_title=data.get("meta_title", "")[:60],
                        meta_description=data.get("meta_description", "")[:160],
                        keywords=data.get("keywords", []),
                        content=data.get("content", ""),
                        headings=data.get("headings", {}),
                        word_count=data.get("word_count", 0),
                        readability_score=data.get("readability_score", "medium"),
                        geo_optimized=request.include_geo_optimization,
                        faq_section=data.get("faq_section", []),
                        linking_suggestions=data.get("linking_suggestions", {}),
                        confidence=response.confidence,
                    )
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Parse error: {e}")
        
        # Fallback
        return self._create_fallback_content(request)
    
    def _create_fallback_content(self, request: SEOContentRequest) -> SEOContent:
        """Create fallback content when generation fails."""
        return SEOContent(
            content_id=str(uuid.uuid4())[:8],
            title=request.title or f"Ultimate Guide to {request.keyword}",
            meta_title=f"{request.keyword.title()} - Complete Guide"[:60],
            meta_description=f"Learn everything about {request.keyword} and how it can help your business. Expert insights and practical strategies."[:160],
            keywords=[request.keyword] + request.primary_keywords[:5],
            content=f"# {request.title or request.keyword.title()}\n\nContent coming soon...",
            headings={"H1": request.keyword, "H2": ["Introduction", "Key Concepts", "Best Practices", "Conclusion"]},
            word_count=0,
            readability_score="medium",
            geo_optimized=request.include_geo_optimization,
            confidence=0.3,
        )
    
    async def generate_blog_post(
        self,
        keyword: str,
        title: str = "",
        **kwargs
    ) -> SEOContent:
        """Convenience method for blog posts."""
        request = SEOContentRequest(
            keyword=keyword,
            title=title,
            content_type="blog_post",
            **kwargs
        )
        return await self.generate(request)
    
    async def generate_llm_txt(self, product_name: str, description: str) -> str:
        """
        Generate an LLM.txt file for Generative Engine Optimization.
        This helps AI systems like ChatGPT, Perplexity, and Gemini
        accurately represent your product/service.
        
        This is a key GEO tactic mentioned in your vault research.
        """
        prompt = f"""Create an LLM.TXT file for {product_name}.

An LLM.TXT file is a text file that helps AI systems understand your brand/product
so they can describe it accurately in responses.

Include:
1. Product/service name and tagline
2. What it does (in 2-3 sentences)
3. Key features and capabilities (bullet points)
4. Target audience/use cases
5. Pricing model (if applicable)
6. What makes it different from competitors
7. Trust indicators (awards, customers, metrics)
8. Contact/support information

Format as a clean text file with clear sections.
Keep descriptions factual and concise (AI systems prefer direct statements over marketing copy).
Include specific numbers and named examples where possible."""

        responses = await generate_parallel(
            prompt=prompt,
            task_type=TaskType.SEO_CONTENT,
            temperature=0.5,
            max_tokens=2048,
        )
        
        if responses:
            # Extract clean text
            content = responses[0].content
            if "```" in content:
                start = content.find("```") + 3
                end = content.rfind("```")
                content = content[start:end].strip()
            return content
        
        return f"# {product_name}\n\n{description}"


async def demo():
    """Demo the SEO generator."""
    print("=" * 60)
    print("MARKETIC SEO CONTENT GENERATOR DEMO")
    print("=" * 60)
    
    generator = SEOGenerator()
    
    # Generate blog post
    print("\n📝 Generating SEO Blog Post...")
    content = await generator.generate_blog_post(
        keyword="marketing automation",
        title="Marketing Automation: The Complete Guide for 2025",
        target_length=2500,
        target_audience="Growth marketers and CMOs",
        primary_keywords=["marketing automation", "marketing software", "automation tools"],
        include_geo_optimization=True,
        include_faq=True,
    )
    
    print(f"\nGenerated Content:")
    print(f"  Title: {content.title}")
    print(f"  Meta Title: {content.meta_title}")
    print(f"  Meta Description: {content.meta_description[:80]}...")
    print(f"  Keywords: {', '.join(content.keywords[:5])}")
    print(f"  Word Count: {content.word_count}")
    print(f"  Readability: {content.readability_score}")
    print(f"  GEO Optimized: {content.geo_optimized}")
    print(f"  FAQ Items: {len(content.faq_section)}")
    
    if content.faq_section:
        print(f"\n  Sample FAQ:")
        for faq in content.faq_section[:2]:
            print(f"    Q: {faq.get('question', '')[:50]}...")
    
    print(f"\n  Content Preview:")
    print(f"  {content.content[:200]}...")
    
    # Generate LLM.txt
    print("\n\n📄 Generating LLM.txt for GEO...")
    llm_txt = await generator.generate_llm_txt(
        product_name="MarketIQ",
        description="AI-powered marketing analytics and campaign optimization platform"
    )
    
    print(f"\nLLM.txt Content:")
    print(llm_txt[:500] + "...")
    
    return content, llm_txt


if __name__ == "__main__":
    asyncio.run(demo())
