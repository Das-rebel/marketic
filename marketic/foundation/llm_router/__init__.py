"""
Marketic LLM Router - Parallel Multi-Model Marketing Intelligence

Based on a3m-style parallel execution with confidence-weighted voting.
Optimized for marketing tasks: copy, analysis, optimization, strategy.

Uses a3m-router at localhost:8787 as the OpenAI-compatible proxy.
"""

import asyncio
import json
import os
import time
from typing import Optional
from dataclasses import dataclass
from enum import Enum

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# a3m-router base URL
a3M_BASE_URL = os.environ.get('A3M_BASE_URL', 'http://localhost:8787/v1')

# Provider mapping
LLM_PROVIDERS = {
    "openrouter": "openai",
    "groq": "groq",
    "cerebras": "cerebras",
    "minimax": "minimax",
}

# Marketing-specific model routing (using Groq via a3m-router - fast & free)
# Only Groq models confirmed working in current a3m-router setup
MARKETING_MODEL_ROUTING = {
    "copy_generation": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": "groq/llama-3.1-8b-instant",
        "parallel": ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant"],
    },
    "social_media": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": "groq/llama-3.3-70b-versatile",
        "parallel": ["groq/llama-3.1-8b-instant", "groq/llama-3.3-70b-versatile"],
    },
    "seo_content": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": "groq/llama-3.1-8b-instant",
        "parallel": ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant"],
    },
    "analytics": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": "groq/llama-3.1-8b-instant",
        "parallel": ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant"],
    },
    "strategy": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": "groq/llama-3.1-8b-instant",
        "parallel": ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant"],
    },
    "optimization": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": "groq/llama-3.3-70b-versatile",
        "parallel": ["groq/llama-3.1-8b-instant", "groq/llama-3.3-70b-versatile"],
    },
    "general": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": "groq/llama-3.3-70b-versatile",
        "parallel": ["groq/llama-3.1-8b-instant", "groq/llama-3.3-70b-versatile"],
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
        """Generate response from a single model via a3m-router."""
        start = time.time()

        # Skip simulation - use real a3m-router API
        if OpenAI is None:
            await asyncio.sleep(0.05)
            return LLMResponse(
                model=model,
                content=f"[Simulated response from {model}]",
                latency_ms=50,
                cost=0.0001,
                confidence=0.85,
            )

        try:
            # a3m-router model names are already in the correct format
            actual_model = model  # e.g., "gpt-4o-mini", "claude-3.5-sonnet", etc.


            client = OpenAI(
                api_key="dummy",  # a3m-router doesn't need real key with Groq
                base_url=a3M_BASE_URL,
            )
            response = client.chat.completions.create(
                model=actual_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency_ms = (time.time() - start) * 1000
            content = response.choices[0].message.content or ""

            # Estimate cost based on token usage
            usage = response.usage
            total_tokens = (usage.prompt_tokens or 0) + (usage.completion_tokens or 0)
            cost = total_tokens * 0.00001  # Rough estimate

            return LLMResponse(
                model=model,
                content=content,
                latency_ms=latency_ms,
                cost=cost,
                confidence=0.85,
            )
        except Exception as e:
            # Fallback to simulation on error
            latency_ms = (time.time() - start) * 1000
            return LLMResponse(
                model=model,
                content=f"[Simulated response from {model}] (error: {str(e)[:50]})",
                latency_ms=latency_ms,
                cost=0,
                confidence=0.5,
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
