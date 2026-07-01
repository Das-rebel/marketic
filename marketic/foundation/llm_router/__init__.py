"""
Marketic LLM Router - Parallel Multi-Model Marketing Intelligence

Based on a3m-style parallel execution with confidence-weighted voting.
Optimized for marketing tasks: copy, analysis, optimization, strategy.
"""

import asyncio
import json
import time
from typing import Optional
from dataclasses import dataclass
from enum import Enum

# Provider mapping
LLM_PROVIDERS = {
    "openrouter": "openai",
    "groq": "groq",
    "cerebras": "cerebras",
    "minimax": "minimax",
}

# Marketing-specific model routing
MARKETING_MODEL_ROUTING = {
    "copy_generation": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallback": "openai/gpt-4o-mini",
        "parallel": ["anthropic/claude-sonnet-4-20250514", "openai/gpt-4o-mini"],
    },
    "social_media": {
        "primary": "openai/gpt-4o-mini",
        "fallback": "anthropic/claude-haiku-4-20250514",
        "parallel": ["openai/gpt-4o-mini", "anthropic/claude-haiku-4-20250514"],
    },
    "seo_content": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallback": "openai/gpt-4o",
        "parallel": ["anthropic/claude-sonnet-4-20250514", "openai/gpt-4o"],
    },
    "analytics": {
        "primary": "openai/gpt-4o",
        "fallback": "anthropic/claude-sonnet-4-20250514",
        "parallel": ["openai/gpt-4o", "google/gemini-2.0-flash-001"],
    },
    "strategy": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallback": "openai/gpt-4o",
        "parallel": ["anthropic/claude-sonnet-4-20250514", "openai/gpt-4o", "google/gemini-2.0-flash-001"],
    },
    "optimization": {
        "primary": "openai/gpt-4o-mini",
        "fallback": "groq/llama-3.1-8b-instant",
        "parallel": ["openai/gpt-4o-mini", "groq/llama-3.1-8b-instant"],
    },
    "general": {
        "primary": "minimax/minimax-text-01",
        "fallback": "openai/gpt-4o-mini",
        "parallel": ["minimax/minimax-text-01", "openai/gpt-4o-mini"],
    },
}


class TaskType(Enum):
    COPY_GENERATION = "copy_generation"
    SOCIAL_MEDIA = "social_media"
    SEO_CONTENT = "seo_content"
    ANALYTICS = "analytics"
    STRATEGY = "strategy"
    OPTIMIZATION = "optimization"
    GENERAL = "general"


@dataclass
class LLMResponse:
    model: str
    content: str
    latency_ms: float
    cost: float
    confidence: float = 0.0


class MarketicLLMRouter:
    """
    Parallel multi-LLM router optimized for marketing tasks.
    
    Features:
    - Task-type based routing
    - Parallel execution with result merging
    - Confidence-weighted voting
    - Cost-performance optimization
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._results_cache = {}
        
    def classify_task(self, prompt: str) -> TaskType:
        """Classify the task type based on prompt content."""
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ["ad copy", "advertisement", "landing page", "email copy", "cta"]):
            return TaskType.COPY_GENERATION
        elif any(kw in prompt_lower for kw in ["twitter", "linkedin", "instagram", "facebook", "social media", "post"]):
            return TaskType.SOCIAL_MEDIA
        elif any(kw in prompt_lower for kw in ["seo", "blog", "article", "content", "keyword"]):
            return TaskType.SEO_CONTENT
        elif any(kw in prompt_lower for kw in ["analytics", "metrics", "attribution", "performance", "report"]):
            return TaskType.ANALYTICS
        elif any(kw in prompt_lower for kw in ["strategy", "positioning", "gtm", "launch", "competitive"]):
            return TaskType.STRATEGY
        elif any(kw in prompt_lower for kw in ["optimize", "improve", "ab test", "budget", "bid"]):
            return TaskType.OPTIMIZATION
        else:
            return TaskType.GENERAL

    def get_routing(self, task_type: TaskType) -> dict:
        """Get model routing for a task type."""
        routing = MARKETING_MODEL_ROUTING.get(task_type.value, MARKETING_MODEL_ROUTING["general"])
        return routing

    async def generate_parallel(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        models: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> list[LLMResponse]:
        """
        Generate responses in parallel from multiple models.
        
        This is the key differentiator from sequential routing:
        We run ALL models simultaneously and merge results.
        """
        if task_type is None:
            task_type = self.classify_task(prompt)
        
        if models is None:
            routing = self.get_routing(task_type)
            models = routing["parallel"]
        
        # Simulated parallel generation
        # In production, this would call actual APIs
        tasks = []
        for model in models:
            tasks.append(self._generate_single(prompt, model, temperature, max_tokens))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Model {models[i]} failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results

    async def _generate_single(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Generate response from a single model."""
        start = time.time()
        
        # Simulate API call
        # In production, use litellm or direct API calls
        await asyncio.sleep(0.1)  # Simulated latency
        
        latency_ms = (time.time() - start) * 1000
        
        # Estimate cost (simplified)
        cost = (max_tokens / 1000) * 0.0001
        
        return LLMResponse(
            model=model,
            content=f"[Simulated response from {model}]",
            latency_ms=latency_ms,
            cost=cost,
            confidence=0.85,
        )

    def merge_results(self, responses: list[LLMResponse], method: str = "confidence_weighted") -> LLMResponse:
        """
        Merge multiple responses using specified method.
        
        Methods:
        - confidence_weighted: Weighted average by confidence
        - first_wins: Return highest confidence
        - ensemble: Return all as list
        """
        if not responses:
            raise ValueError("No responses to merge")
        
        if method == "first_wins":
            return max(responses, key=lambda r: r.confidence)
        
        elif method == "confidence_weighted":
            total_confidence = sum(r.confidence for r in responses)
            if total_confidence == 0:
                return responses[0]
            
            weighted_content = []
            for r in responses:
                weight = r.confidence / total_confidence
                weighted_content.append(f"[{r.model}] (weight: {weight:.2f}) {r.content}")
            
            return LLMResponse(
                model="ensemble",
                content="\n".join(weighted_content),
                latency_ms=sum(r.latency_ms for r in responses) / len(responses),
                cost=sum(r.cost for r in responses),
                confidence=sum(r.confidence for r in responses) / len(responses),
            )
        
        elif method == "ensemble":
            # Return ensemble response with all options
            return LLMResponse(
                model="ensemble",
                content=json.dumps([
                    {"model": r.model, "content": r.content, "confidence": r.confidence}
                    for r in responses
                ]),
                latency_ms=sum(r.latency_ms for r in responses),
                cost=sum(r.cost for r in responses),
                confidence=max(r.confidence for r in responses),
            )
        
        return responses[0]


# Convenience functions
router = MarketicLLMRouter()


def classify_task(prompt: str) -> TaskType:
    """Classify a task type."""
    return router.classify_task(prompt)


async def generate_parallel(prompt: str, task_type: Optional[TaskType] = None, **kwargs) -> list[LLMResponse]:
    """Generate parallel responses."""
    return await router.generate_parallel(prompt, task_type, **kwargs)


async def generate(prompt: str, task_type: Optional[TaskType] = None, **kwargs) -> LLMResponse:
    """Generate and merge results."""
    responses = await generate_parallel(prompt, task_type, **kwargs)
    return router.merge_results(responses)


if __name__ == "__main__":
    async def test():
        print("Testing Marketic LLM Router...")
        
        # Test task classification
        tasks = [
            "Generate 5 ad copy options for an AI marketing tool",
            "Write a Twitter thread about fintech growth",
            "Analyze campaign performance data",
            "Create SEO-optimized blog post about marketing automation",
        ]
        
        for task in tasks:
            task_type = classify_task(task)
            print(f"\nTask: {task[:50]}...")
            print(f"Type: {task_type.value}")
            
            responses = await generate_parallel(task, task_type)
            print(f"Parallel models: {[r.model for r in responses]}")
            
            result = router.merge_results(responses)
            print(f"Merged result confidence: {result.confidence:.2f}")
    
    asyncio.run(test())
