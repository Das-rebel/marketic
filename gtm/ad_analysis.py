"""
Ad Analysis — Competitor ad deconstruction via VLM.

Vault-sourced: Gemma4 "watches" video ads frame-by-frame (hooks, pacing,
psychological triggers). This module feeds that intel into generate_creatives
so counter-variants know what they're countering.

Backend ladder:
  1. Local Ollama vision model (llava / qwen2.5-vl) — free, private, bulk
  2. OpenRouter/OpenAI vision — paid fallback
  3. Metadata-only heuristic — no VLM required, still useful structure
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

import httpx

OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://127.0.0.1:11434")
VISION_MODEL_ENV = os.environ.get("MARKETIC_VISION_MODEL", "")


@dataclass
class AdBreakdown:
    """Structured deconstruction of one competitor ad."""
    source_url: str
    ad_type: str                          # video / image / copy-only
    hook: str = ""                        # first-3-second scroll-stopper
    pacing: str = ""                      # cuts/sec, rhythm notes
    psychological_triggers: List[str] = field(default_factory=list)
    value_prop: str = ""
    cta: str = ""
    tone: str = ""
    visual_style: str = ""
    counter_angles: List[str] = field(default_factory=list)  # what WE attack
    confidence: float = 0.0               # 0 = metadata-only guess
    backend: str = ""                     # which VLM produced this


def _detect_ollama_vision_model() -> Optional[str]:
    """Find an installed vision-capable ollama model."""
    if VISION_MODEL_ENV:
        return VISION_MODEL_ENV
    candidates = ["llava", "qwen2.5vl", "qwen2.5-vl", "llama3.2-vision", "moondream"]
    try:
        resp = httpx.get(f"{OLLAMA_BASE}/api/tags", timeout=5.0)
        installed = {m["name"].split(":")[0] for m in resp.json().get("models", [])}
        for c in candidates:
            if c in installed:
                return c
    except Exception:
        pass
    return None


_BREAKDOWN_PROMPT = """You are a performance-marketing creative analyst.
Deconstruct this competitor ad. Respond with STRICT JSON only:

{"hook": "the opening attention-grabber, quoted or described",
 "pacing": "cut rhythm / scene duration notes",
 "psychological_triggers": ["fomo", "social_proof", ...],
 "value_prop": "core promise in one line",
 "cta": "call to action text",
 "tone": "e.g. urgent / playful / authoritative",
 "visual_style": "color mood, typography feel, production quality",
 "counter_angles": ["2-3 specific weaknesses or gaps OUR ad can attack"]}

Be specific to what you actually see/hear. No filler."""


class AdAnalyzer:
    """Deconstruct competitor ads into structured, attackable intelligence."""

    def analyze(
        self,
        image_path_or_url: str = "",
        transcript: str = "",
        caption: str = "",
    ) -> AdBreakdown:
        """
        Analyze one ad from any available input:
        - image/video frame (path or URL) → vision model
        - transcript (video voiceover/subtitles) → text model path
        - caption/copy → metadata heuristics at minimum
        """
        # Ladder 1: local Ollama vision
        if image_path_or_url:
            model = _detect_ollama_vision_model()
            if model:
                result = self._via_ollama_vision(model, image_path_or_url)
                if result:
                    return result

        # Ladder 2: cloud vision
        if image_path_or_url:
            result = self._via_cloud_vision(image_path_or_url)
            if result:
                return result

        # Ladder 3: heuristics on whatever text we have
        return self._heuristic(transcript=transcript, caption=caption,
                               source=image_path_or_url)

    def analyze_batch(self, ads: List[Dict[str, str]]) -> List[AdBreakdown]:
        """Bulk deconstruction — the actual 'watch them in bulk' workflow."""
        return [self.analyze(**{k: v for k, v in ad.items()
                                if k in ("image_path_or_url", "transcript", "caption")})
                for ad in ads]

    def derive_counter_brief(self, breakdowns: List[AdBreakdown]) -> Dict[str, Any]:
        """
        Aggregate N competitor breakdowns into input for generate_creatives:
        saturated triggers (avoid — everyone does it), open angles (attack),
        and tone map of the field.
        """
        trigger_counts: Dict[str, int] = {}
        tones: Dict[str, int] = {}
        open_angles: List[str] = []

        for b in breakdowns:
            for t in b.psychological_triggers:
                trigger_counts[t.lower()] = trigger_counts.get(t.lower(), 0) + 1
            if b.tone:
                tones[b.tone.lower()] = tones.get(b.tone.lower(), 0) + 1
            open_angles.extend(b.counter_angles[:2])

        saturated = sorted(trigger_counts.items(), key=lambda x: -x[1])
        return {
            "saturated_triggers": [t for t, n in saturated if n >= max(2, len(breakdowns) // 2)],
            "rare_triggers": [t for t, n in saturated if n == 1],
            "field_tones": sorted(tones.items(), key=lambda x: -x[1]),
            "open_attack_angles": list(dict.fromkeys(open_angles))[:8],
            "ads_analyzed": len(breakdowns),
        }

    # ── backends ─────────────────────────────────────────────────────────

    def _via_ollama_vision(self, model: str, image_ref: str) -> Optional[AdBreakdown]:
        try:
            if image_ref.startswith("http"):
                img_resp = httpx.get(image_ref, timeout=30.0)
                img_data = base64.b64encode(img_resp.content).decode()
            else:
                with open(image_ref, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()

            resp = httpx.post(
                f"{OLLAMA_BASE}/api/generate",
                json={
                    "model": model,
                    "prompt": _BREAKDOWN_PROMPT,
                    "images": [img_data],
                    "stream": False,
                    "format": "json",
                },
                timeout=120.0,
            )
            if resp.status_code == 200:
                parsed = self._parse_json(resp.json().get("response", ""))
                if parsed:
                    return self._to_breakdown(parsed, image_ref,
                                              backend=f"ollama:{model}", confidence=0.8)
        except Exception as e:
            print(f"[ad_analysis] ollama vision failed: {e}")
        return None

    def _via_cloud_vision(self, image_ref: str) -> Optional[AdBreakdown]:
        key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            return None
        try:
            content: Any = [{"type": "text", "text": _BREAKDOWN_PROMPT}]
            if image_ref.startswith("http"):
                content.append({"type": "image_url", "image_url": {"url": image_ref}})
            else:
                with open(image_ref, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                content.append({"type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"}})

            base = ("https://openrouter.ai/api/v1" if key.startswith("sk-or-")
                    else "https://api.openai.com/v1")
            model = "openai/gpt-4o-mini" if key.startswith("sk-or-") else "gpt-4o-mini"
            resp = httpx.post(f"{base}/chat/completions", headers={"Authorization": f"Bearer {key}"},
                              json={"model": model, "messages": [{"role": "user", "content": content}],
                                    "max_tokens": 500},
                              timeout=90.0)
            if resp.status_code == 200:
                parsed = self._parse_json(resp.json()["choices"][0]["message"]["content"])
                if parsed:
                    return self._to_breakdown(parsed, image_ref,
                                              backend=f"cloud:{model}", confidence=0.85)
        except Exception as e:
            print(f"[ad_analysis] cloud vision failed: {e}")
        return None

    # ── heuristic fallback (no VLM needed) ───────────────────────────────

    _TRIGGER_LEXICON = {
        "limited": "scarcity", "only": "scarcity", "today": "urgency",
        "now": "urgency", "free": "free_offer", "%": "discount",
        "join": "community", "everyone": "social_proof", "loved by": "social_proof",
        "guarantee": "risk_reversal", "proven": "authority", "expert": "authority",
    }

    def _heuristic(self, transcript: str = "", caption: str = "",
                   source: str = "") -> AdBreakdown:
        """Structure + lexicon triggers from copy alone. Honest low confidence."""
        text = f"{caption} {transcript}".lower()
        triggers = sorted({v for k, v in self._TRIGGER_LEXICON.items() if k in text})
        words = text.split()
        return AdBreakdown(
            source_url=source or "(text only)",
            ad_type="copy-only" if not image_needs(source) else "unanalyzed-media",
            hook=(caption or transcript)[:100],
            psychological_triggers=triggers,
            value_prop=" ".join(words[10:30]) if len(words) > 30 else "",
            cta=self._guess_cta(text),
            counter_angles=["full VLM analysis pending — install llava: ollama pull llava"],
            confidence=0.2,
            backend="heuristics",
        )

    @staticmethod
    def _guess_cta(text: str) -> str:
        for phrase in ("shop now", "sign up", "get started", "learn more",
                       "try free", "buy now", "download"):
            if phrase in text:
                return phrase.title()
        return ""

    # ── helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(text: str) -> Optional[Dict]:
        try:
            start, end = text.find("{"), text.rfind("}") + 1
            return json.loads(text[start:end]) if start >= 0 < end else None
        except Exception:
            return None

    @staticmethod
    def _to_breakdown(parsed: Dict, source: str, backend: str,
                      confidence: float) -> AdBreakdown:
        return AdBreakdown(
            source_url=source,
            ad_type=parsed.get("ad_type", "video"),
            hook=str(parsed.get("hook", ""))[:200],
            pacing=str(parsed.get("pacing", ""))[:200],
            psychological_triggers=[str(t).lower() for t in parsed.get("psychological_triggers", [])][:6],
            value_prop=str(parsed.get("value_prop", ""))[:200],
            cta=str(parsed.get("cta", ""))[:60],
            tone=str(parsed.get("tone", ""))[:40],
            visual_style=str(parsed.get("visual_style", ""))[:150],
            counter_angles=[str(a)[:150] for a in parsed.get("counter_angles", [])][:4],
            confidence=confidence,
            backend=backend,
        )


def image_needs(ref: str) -> bool:
    return bool(ref) and ref != "(text only)"
