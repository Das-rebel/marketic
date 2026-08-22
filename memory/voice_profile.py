"""
Brand Voice Profile — Extract, score, and adapt content to brand voice.
"""

import os
import re
from typing import Dict, List, Optional, Any

# Try to import sentence-transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class VoiceProfile:
    tone: str
    vocabulary: List[str]
    banned_words: List[str]
    style_attributes: Dict[str, Any]
    sample_size: int


class VoiceAnalyzer:
    """Analyzes brand content to extract voice profile."""
    
    def __init__(self):
        self._embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                pass
        
        if OPENAI_AVAILABLE:
            self._openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def analyze_text_samples(self, texts: List[str]) -> VoiceProfile:
        """
        Analyze a list of text samples to extract voice profile.
        Falls back to simple keyword analysis if no APIs available.
        """
        if not texts:
            return VoiceProfile(
                tone="professional",
                vocabulary=[],
                banned_words=[],
                style_attributes={},
                sample_size=0
            )
        
        # Simple analysis: extract common words, detect tone markers
        all_text = " ".join(texts).lower()
        
        # Extract tone signals
        tone_indicators = {
            "casual": ["hey", "yo", "cool", "awesome", "fun", "love"],
            "professional": ["therefore", "furthermore", "however", "consequently", "regarding"],
            "friendly": ["great", "amazing", "thank", "please", "happy"],
            "technical": ["api", "integration", "platform", "framework", "architecture"],
            "bold": ["revolutionary", "game-changing", "unprecedented", "breakthrough"],
        }
        
        tone_scores = {}
        for tone, markers in tone_indicators.items():
            score = sum(1 for m in markers if m in all_text)
            tone_scores[tone] = score
        
        dominant_tone = max(tone_scores, key=tone_scores.get) if any(tone_scores.values()) else "professional"
        
        # Extract vocabulary (most common content words)
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they', 'their', 'what', 'when', 'where', 'which', 'about', 'would', 'could', 'should', 'there', 'here', 'into', 'your', 'more', 'some', 'into'}
        content_words = [w for w in words if w not in stopwords]
        word_freq = {}
        for w in content_words:
            word_freq[w] = word_freq.get(w, 0) + 1
        
        top_vocabulary = sorted(word_freq.items(), key=lambda x: -x[1])[:50]
        vocabulary = [w for w, _ in top_vocabulary]
        
        # Detect banned words (simple heuristic)
        banned = ["spam", "fake", "scam", "clickbait", "viagra", "nigeria"]
        banned_words = [w for w in banned if w in all_text]
        
        # Style attributes
        avg_word_count = sum(len(t.split()) for t in texts) / len(texts)
        avg_sentence_count = sum(len(re.split(r'[.!?]+', t)) for t in texts) / len(texts)
        
        style_attributes = {
            "avg_word_count": round(avg_word_count, 1),
            "avg_sentence_length": round(avg_word_count / max(avg_sentence_count, 1), 1),
            "has_emoji": any(c in all_text for c in "😀🚀💡⭐❤️"),
            "has_hashtags": any("#" in t for t in texts),
            "exclamation_usage": all_text.count("!"),
            "question_usage": all_text.count("?"),
        }
        
        return VoiceProfile(
            tone=dominant_tone,
            vocabulary=vocabulary[:50],
            banned_words=banned_words,
            style_attributes=style_attributes,
            sample_size=len(texts)
        )
    
    def score_content(self, content: str, profile: VoiceProfile) -> float:
        """
        Score how well content matches a brand voice profile.
        Returns score 0.0-1.0.
        """
        if not content or profile.sample_size == 0:
            return 0.5
        
        content_lower = content.lower()
        
        # Tone match
        tone_indicators = {
            "casual": ["hey", "yo", "cool", "awesome", "fun", "love"],
            "professional": ["therefore", "furthermore", "however", "consequently", "regarding"],
            "friendly": ["great", "amazing", "thank", "please", "happy"],
            "technical": ["api", "integration", "platform", "framework", "architecture"],
            "bold": ["revolutionary", "game-changing", "unprecedented", "breakthrough"],
        }
        
        tone_markers = tone_indicators.get(profile.tone, [])
        tone_score = sum(1 for m in tone_markers if m in content_lower) / max(len(tone_markers), 1)
        
        # Vocabulary match
        content_words = set(re.findall(r'\b[a-z]{4,}\b', content_lower))
        profile_vocab = set(profile.vocabulary[:30])
        vocab_overlap = len(content_words & profile_vocab)
        vocab_score = vocab_overlap / max(len(profile_vocab), 1)
        
        # Banned word penalty
        banned_penalty = 0
        for word in profile.banned_words:
            if word in content_lower:
                banned_penalty += 0.2
        
        # Style check
        style_score = 1.0
        if profile.style_attributes.get("has_emoji") and "😀" not in content and "🚀" not in content:
            style_score *= 0.9
        if profile.style_attributes.get("has_hashtags") and "#" not in content:
            style_score *= 0.9
        
        score = (tone_score * 0.3 + vocab_score * 0.4 + style_score * 0.3) - banned_penalty
        return max(0.0, min(1.0, score))
    
    def adapt_content(self, content: str, profile: VoiceProfile, target_words: int = None) -> str:
        """
        Adapt content to match a brand voice profile.
        If OpenAI available, uses GPT to rewrite. Otherwise does simple adaptation.
        """
        if not profile or profile.sample_size == 0:
            return content
        
        if OPENAI_AVAILABLE and self._openai:
            # Use GPT to rewrite in brand voice
            tone_guidance = f"The brand voice is {profile.tone}."
            vocab_guidance = f"Use these words naturally: {', '.join(profile.vocabulary[:20])}"
            banned_guidance = f"Avoid these words: {', '.join(profile.banned_words)}" if profile.banned_words else "No banned words."
            
            prompt = f"""Rewrite the following content to match this brand voice:
            
Tone: {profile.tone}
Vocabulary: {vocab_guidance}
Banned: {banned_guidance}

Original content:
{content}

Rewritten content (preserve the meaning, just adapt the voice):"""
            
            try:
                response = self._openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                adapted = response.choices[0].message.content.strip()
                if target_words:
                    # Trim to target word count
                    words = adapted.split()
                    if len(words) > target_words:
                        adapted = " ".join(words[:target_words]) + "..."
                return adapted
            except Exception:
                pass
        
        # Fallback: simple voice adaptation
        adapted = content
        
        # Apply tone markers
        tone_markers = {
            "casual": [("implement", "set up"), ("utilize", "use"), ("facilitate", "help")],
            "professional": [("get", "obtain"), ("buy", "purchase"), ("help", "assist")],
            "friendly": [("purchase", "grab"), ("contact", "reach out")],
        }
        
        for tone, replacements in tone_markers.items():
            if profile.tone == tone:
                for formal, informal in replacements:
                    adapted = adapted.replace(formal, informal)
        
        # Add banned word warning if content contains banned words
        for word in profile.banned_words:
            if word in adapted.lower():
                # Remove/replace banned word
                adapted = re.sub(rf'\b{word}\b', "[removed]", adapted, flags=re.IGNORECASE)
        
        if target_words:
            words = adapted.split()
            if len(words) > target_words:
                adapted = " ".join(words[:target_words]) + "..."
        
        return adapted
