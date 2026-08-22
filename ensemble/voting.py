"""
Ensemble Voting — Multi-model confidence-weighted decision making.
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

import httpx


@dataclass
class ModelResponse:
    model: str
    response: str
    cost: float
    latency_ms: int
    tokens_used: int


@dataclass
class EnsembleVote:
    decision: str
    confidence: float  # 0.0-1.0
    models_used: List[str]
    reasoning_chain: List[str]
    cost: float
    consensus: bool


# Model pricing (per 1M tokens, approximate)
MODEL_PRICING = {
    "stealth/ox-alpha": {"input": 0, "output": 0},  # FREE
    "qwen/qwen3.7-max": {"input": 0.50, "output": 1.50},
    "google/gemini-3.6-flash": {"input": 0.10, "output": 0.40},
    "deepseek/deepseek-v4-flash": {"input": 0.22, "output": 0.66},
    "minimax/m3": {"input": 0.30, "output": 1.20},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

# Model tiers
TIER_CHEAP = ["qwen/qwen3.7-flash", "deepseek/deepseek-v4-flash"]
TIER_MID = ["google/gemini-3.6-flash", "minimax/m3", "qwen/qwen3.7-max"]
TIER_PREMIUM = ["stealth/ox-alpha", "openai/gpt-4o-mini"]


class EnsembleVoter:
    """
    Multi-model voting with confidence scoring.
    Simple tasks use 1 model. Complex tasks use multiple models + voting.
    """
    
    def __init__(self):
        self._openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self._openai_key = os.environ.get("OPENAI_API_KEY")
        self._opencode_key = os.environ.get("OPENCODE_GO_TOKEN")
    
    def vote(self, task_type: str, prompt: str, context: Dict = None,
            models: List[str] = None) -> EnsembleVote:
        """
        Run ensemble vote on a task.
        
        task_type: simple (1 cheap model), moderate (1 mid model), 
                  complex (3 models parallel), critical (5 models + deep reasoning)
        """
        context = context or {}
        
        # Route to appropriate models
        if models:
            selected_models = models
        else:
            selected_models = self._route_task(task_type)
        
        # Run all models in parallel
        responses = self._run_parallel(prompt, selected_models, context)
        
        # Calculate consensus and confidence
        decision, confidence, consensus = self._calculate_consensus(responses)
        
        # Build reasoning chain
        reasoning_chain = [f"[{r.model}] {r.response[:200]}" for r in responses]
        
        # Total cost
        total_cost = sum(r.cost for r in responses)
        
        return EnsembleVote(
            decision=decision,
            confidence=confidence,
            models_used=[r.model for r in responses],
            reasoning_chain=reasoning_chain,
            cost=total_cost,
            consensus=consensus
        )
    
    def _route_task(self, task_type: str) -> List[str]:
        """Route task to appropriate model tier."""
        routing = {
            "ad_copy": ["deepseek/deepseek-v4-flash"],  # 1 cheap
            "social_post": ["google/gemini-3.6-flash"],  # 1 mid
            "keyword_research": ["qwen/qwen3.7-max"],  # 1 mid
            "competitor_analysis": ["stealth/ox-alpha", "qwen/qwen3.7-max", "google/gemini-3.6-flash"],  # 3 premium
            "campaign_strategy": ["stealth/ox-alpha", "qwen/qwen3.7-max", "openai/gpt-4o-mini"],  # 3 premium
            "brand_voice_analysis": ["stealth/ox-alpha", "qwen/qwen3.7-max"],  # 2 mid
            "briefing_generation": ["stealth/ox-alpha"],  # 1 premium (long context)
            "default": ["google/gemini-3.6-flash"],
        }
        return routing.get(task_type, routing["default"])
    
    def _run_parallel(self, prompt: str, models: List[str], 
                     context: Dict) -> List[ModelResponse]:
        """Run multiple models and return responses."""
        responses = []
        
        for model in models:
            try:
                resp = self._call_model(model, prompt, context)
                responses.append(resp)
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        return responses
    
    def _call_model(self, model: str, prompt: str, context: Dict) -> ModelResponse:
        """Call a single model and return response with cost."""
        start = time.time()
        
        # Determine provider
        if model.startswith("stealth/"):
            return self._call_openrouter(model, prompt)
        elif model.startswith(("google/", "qwen/", "deepseek/")):
            return self._call_openrouter(model, prompt)
        elif model.startswith("openai/"):
            return self._call_openai(model, prompt)
        elif model.startswith("minimax/"):
            return self._call_opencode_go(model, prompt)
        else:
            return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
    
    def _call_openrouter(self, model: str, prompt: str) -> ModelResponse:
        """Call OpenRouter API."""
        if not self._openrouter_key:
            return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
        
        try:
            client = httpx.Client(
                base_url="https://openrouter.ai/api/v1",
                headers={"Authorization": f"Bearer {self._openrouter_key}"},
                timeout=120.0
            )
            
            start = time.time()
            response = client.post("/chat/completions", json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            })
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                # Calculate cost
                pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
                input_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * pricing["input"]
                output_cost = (usage.get("completion_tokens", 0) / 1_000_000) * pricing["output"]
                total_cost = input_cost + output_cost
                
                return ModelResponse(
                    model=model,
                    response=content,
                    cost=total_cost,
                    latency_ms=latency,
                    tokens_used=usage.get("completion_tokens", 0)
                )
        except Exception as e:
            print(f"OpenRouter error: {e}")
        
        return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
    
    def _call_openai(self, model: str, prompt: str) -> ModelResponse:
        """Call OpenAI API."""
        if not self._openai_key:
            return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._openai_key)
            
            start = time.time()
            resp = client.chat.completions.create(
                model=model.replace("openai/", ""),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            latency = int((time.time() - start) * 1000)
            
            content = resp.choices[0].message.content
            usage = resp.usage
            
            pricing = MODEL_PRICING.get(model, {"input": 0.15, "output": 0.60})
            total_cost = (usage.prompt_tokens / 1_000_000 * pricing["input"] + 
                         usage.completion_tokens / 1_000_000 * pricing["output"])
            
            return ModelResponse(
                model=model,
                response=content,
                cost=total_cost,
                latency_ms=latency,
                tokens_used=usage.completion_tokens
            )
        except Exception as e:
            print(f"OpenAI error: {e}")
        
        return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
    
    def _call_opencode_go(self, model: str, prompt: str) -> ModelResponse:
        """Call OpenCode Go API (uses same format as OpenAI)."""
        if not self._opencode_key:
            return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
        
        try:
            client = httpx.Client(
                base_url="https://opencode.ai/zen/go/v1",
                headers={"Authorization": f"Bearer {self._opencode_key}"},
                timeout=120.0
            )
            
            start = time.time()
            response = client.post("/chat/completions", json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            })
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                # OpenCode Go is free
                return ModelResponse(
                    model=model,
                    response=content,
                    cost=0,
                    latency_ms=latency,
                    tokens_used=usage.get("completion_tokens", 0)
                )
        except Exception as e:
            print(f"OpenCode Go error: {e}")
        
        return ModelResponse(model=model, response="", cost=0, latency_ms=0, tokens_used=0)
    
    def _calculate_consensus(self, responses: List[ModelResponse]) -> Tuple[str, float, bool]:
        """
        Calculate consensus from multiple model responses.
        Returns (best_response, confidence, is_consensus).
        """
        if not responses:
            return "", 0.0, False
        
        if len(responses) == 1:
            return responses[0].response, 0.7, True
        
        # Simple consensus: use longest response (more detail = higher confidence)
        # In production would use semantic similarity
        sorted_responses = sorted(responses, key=lambda r: len(r.response), reverse=True)
        
        best = sorted_responses[0]
        
        # Calculate confidence based on agreement
        # If all responses are similar length, higher confidence
        avg_len = sum(len(r.response) for r in responses) / len(responses)
        length_variance = sum(abs(len(r.response) - avg_len) for r in responses) / len(responses)
        
        # Low variance = high confidence
        confidence = max(0.3, min(0.95, 1.0 - (length_variance / avg_len if avg_len > 0 else 0)))
        
        # Consensus if top 2 responses are similar length
        consensus = len(sorted_responses) < 2 or \
                   abs(len(sorted_responses[0].response) - len(sorted_responses[1].response)) < 100
        
        return best.response, confidence, consensus
