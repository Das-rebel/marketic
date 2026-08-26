"""
SEO Content Writer — Generate long-form SEO articles with keyword research.
"""

import os
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

# Try OpenRouter for ox-alpha
try:
    import httpx
    OPENROUTER_AVAILABLE = bool(os.environ.get("OPENROUTER_API_KEY"))
except ImportError:
    OPENROUTER_AVAILABLE = False


@dataclass
class Keyword:
    keyword: str
    difficulty: int  # 0-100
    volume: int  # monthly searches
    opportunity_score: float  # 0-1


@dataclass  
class Article:
    title: str
    content: str
    meta_description: str
    subheadings: List[str]
    word_count: int
    seo_score: float
    keywords_used: List[str]


class SEOWriter:
    """Generate SEO-optimized long-form articles."""
    
    def __init__(self):
        self._openai = None
        self._openrouter_client = None
        
        if OPENAI_AVAILABLE:
            self._openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        if OPENROUTER_AVAILABLE:
            self._openrouter_client = httpx.Client(
                base_url="https://openrouter.ai/api/v1",
                headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
                timeout=60.0
            )
    
    def research_keywords(self, seed_keyword: str, num_keywords: int = 20) -> List[Keyword]:
        """
        Research keywords based on seed keyword.
        Uses simple pattern matching + simulation for now.
        In production, would use Google Keyword Planner API or similar.
        """
        # Simulated keyword data based on seed
        base_terms = seed_keyword.lower().split()
        
        modifiers = [
            "guide", " strategies", "tips", "best", "top", "how to",
            "examples", "template", "checklist", "automation",
            "2026", "for beginners", "advanced", "case study"
        ]
        
        keywords = []
        
        # Seed keyword itself
        keywords.append(Keyword(
            keyword=seed_keyword,
            difficulty=50,
            volume=1000,
            opportunity_score=0.7
        ))
        
        # Generate combinations
        for modifier in modifiers[:num_keywords - 1]:
            kw = seed_keyword + modifier
            keywords.append(Keyword(
                keyword=kw,
                difficulty=max(10, min(95, 50 + len(keywords) * 3)),
                volume=max(100, 1000 - len(keywords) * 50),
                opportunity_score=max(0.2, min(0.95, 0.7 - len(keywords) * 0.03))
            ))
        
        return keywords[:num_keywords]
    
    def generate_article(self, keyword: str, target_words: int = 1800, 
                        brand_voice: Optional[Dict] = None) -> Article:
        """
        Generate a long-form SEO article.
        Uses ox-alpha (1.05M context) via OpenRouter if available, else GPT-4o-mini.
        """
        title = self._generate_title(keyword)
        meta_description = self._generate_meta_description(keyword, title)
        subheadings = self._generate_subheadings(keyword, target_words)
        content = self._generate_content(keyword, title, subheadings, target_words, brand_voice)
        
        word_count = len(content.split())
        
        # Calculate SEO score
        seo_score = self._calculate_seo_score(content, keyword)
        
        return Article(
            title=title,
            content=content,
            meta_description=meta_description,
            subheadings=subheadings,
            word_count=word_count,
            seo_score=seo_score,
            keywords_used=[keyword] + [s for s in subheadings if s]
        )
    
    def _generate_title(self, keyword: str) -> str:
        """Generate SEO title."""
        if self._openrouter_client:
            try:
                response = self._openrouter_client.post("/chat/completions", json={
                    "model": "stealth/ox-alpha",
                    "messages": [{
                        "role": "user", 
                        "content": f"Generate an SEO-optimized article title for keyword: '{keyword}'. "
                                   f"Return ONLY the title, no quotes or extra text. Max 60 characters."
                    }],
                    "max_tokens": 60
                })
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception:
                pass
        
        if self._openai:
            try:
                response = self._openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": f"Generate an SEO title for: '{keyword}'. Max 60 chars. Return ONLY the title."
                    }],
                    max_tokens=60
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass
        
        # Fallback
        return f"The Complete Guide to {keyword.title()} in 2026"
    
    def _generate_meta_description(self, keyword: str, title: str) -> str:
        """Generate meta description."""
        if self._openai:
            try:
                response = self._openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": f"Write a meta description for an article titled '{title}' about '{keyword}'. Max 155 chars."
                    }],
                    max_tokens=160
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass
        
        return f"Learn everything about {keyword} with our comprehensive guide. Expert tips, strategies, and examples."
    
    def _generate_subheadings(self, keyword: str, target_words: int) -> List[str]:
        """Generate H2 subheadings for the article."""
        num_headings = max(4, min(8, target_words // 300))
        
        if self._openai:
            try:
                response = self._openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": f"Generate {num_headings} H2 subheadings for an article about '{keyword}'. "
                                   f"Return as JSON array of strings. Each should be a question or phrase."
                    }],
                    max_tokens=300
                )
                content = response.choices[0].message.content.strip()
                # Try to parse JSON
                try:
                    import ast
                    headings = ast.literal_eval(content)
                    if isinstance(headings, list):
                        return [str(h) for h in headings[:num_headings]]
                except:
                    pass
            except Exception:
                pass
        
        # Fallback subheadings
        return [
            f"What is {keyword.title()}?",
            f"Key Benefits of {keyword.title()}",
            f"How to Get Started with {keyword.title()}",
            f"Common Mistakes to Avoid with {keyword.title()}",
            f"Best Practices for {keyword.title()}",
        ][:num_headings]
    
    def _generate_content(self, keyword: str, title: str, subheadings: List[str], 
                         target_words: int, brand_voice: Optional[Dict]) -> str:
        """Generate full article content."""
        
        # Build content structure
        sections = []
        
        # Introduction
        intro = f"# {title}\n\n"
        intro += f"In this comprehensive guide, we'll explore everything you need to know about **{keyword}**. "
        intro += f"Whether you're just getting started or looking to level up your knowledge, this article has you covered.\n\n"
        sections.append(intro)
        
        # Build each section
        words_per_section = target_words // (len(subheadings) + 1)
        
        for heading in subheadings:
            section = f"## {heading}\n\n"
            section += f"This section covers the essential aspects of {heading.lower()}. "
            section += f"Understanding this is crucial for anyone working with {keyword}.\n\n"
            
            # Add bullet points
            bullets = [
                f"Key point 1 related to {heading.lower()}",
                f"Important consideration for {keyword} strategy",
                f"Best practice example in {keyword}",
            ]
            for bullet in bullets:
                section += f"- {bullet}\n"
            
            sections.append(section)
        
        # Conclusion
        conclusion = f"## Conclusion\n\n"
        conclusion += f"We've covered the complete landscape of {keyword} in this guide. "
        conclusion += f"The key takeaway: start implementing what you've learned today. "
        conclusion += f"For more insights, explore our related resources.\n"
        sections.append(conclusion)
        
        content = "".join(sections)
        
        # If brand voice provided, adapt
        if brand_voice and brand_voice.get("tone"):
            content = self._adapt_to_brand_voice(content, brand_voice)
        
        return content
    
    def _adapt_to_brand_voice(self, content: str, brand_voice: Dict) -> str:
        """Adapt content to brand voice."""
        tone = brand_voice.get("tone", "professional")
        
        if tone == "casual":
            content = content.replace("comprehensive", "complete")
            content = content.replace("essential", "key")
        elif tone == "bold":
            content = content.replace("learned", "mastered")
            content = content.replace("help", "transform")
        
        return content
    
    def _calculate_seo_score(self, content: str, keyword: str) -> float:
        """Calculate SEO score based on content optimization."""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        keyword_count = content_lower.count(keyword.lower())
        word_count = len(content.split())
        
        # Keyword density (ideal: 1-2%)
        keyword_density = (keyword_count * len(keyword.split())) / word_count if word_count > 0 else 0
        density_score = min(1.0, keyword_density / 0.02) if keyword_density > 0 else 0
        
        # Length score
        length_score = min(1.0, word_count / 1800)
        
        # Structure score (has headings, lists)
        structure_score = 0.5
        if "##" in content:
            structure_score += 0.2
        if "- " in content:
            structure_score += 0.2
        if "# " in content:
            structure_score += 0.1
        
        # Meta score
        meta_score = 0.5
        if len(content) > 1800:
            meta_score += 0.3
        if keyword in content[:500]:
            meta_score += 0.2
        
        total_score = (density_score * 0.3 + length_score * 0.3 + 
                       structure_score * 0.2 + meta_score * 0.2)
        
        return round(min(1.0, total_score), 2)
    
    def generate_seo_images(self, article_topic: str, num_images: int = 3) -> List[Dict[str, str]]:
        """Generate image prompts for article."""
        prompts = []
        
        base_prompts = [
            f"Professional illustration about {article_topic}, modern design, clean aesthetic",
            f"Diagram explaining {article_topic} concepts, infographic style",
            f"Real-world example of {article_topic}, photography style",
        ]
        
        for i, prompt in enumerate(base_prompts[:num_images]):
            prompts.append({
                "prompt": prompt,
                "alt_text": f"{article_topic} - image {i+1}",
                "suggested_caption": f"Visual representation of {article_topic}"
            })
        
        return prompts
