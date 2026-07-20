# Marketic — Architecture Redesign
## Based on A3M Router + OmniClaw Architectural Learnings

**Redesigned:** 2026-07-02
**Based on:** A3M Router research + OmniClaw production patterns

---

## Executive Summary

The previous flat module structure had no pipeline, no routing, no ensemble, and no quality feedback. This redesign applies **12 architectural patterns** from A3M Router and OmniClaw to create a production-grade marketing OS.

### Key Changes

| Before | After |
|--------|-------|
| Flat 20+ modules | 4-stage canonical pipeline |
| No routing | Tier-based parallel ensemble |
| No difficulty classification | Intent + difficulty + domain classifiers |
| No middleware | Rate limits, retries, circuit breakers, caching |
| No quality feedback | Dynamic tier adjustment |
| Standalone MCPs | Integrated into routing |
| Flat memory | Session + persistent + semantic |
| No skill bridge | Slash commands |

---

## Part I: Core Pipeline Architecture

### The Canonical Pipeline (OmniClaw Pattern)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE ENGINE                                  │
│         Signal → Plan → Execute → Respond → Learn → Repeat               │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Stage 1: Signal (Trigger + Context)
```python
class SignalStage:
    """
    Signal: What triggered this run?
    - User command (CLI, Slack, WhatsApp)
    - Scheduled event (cron trigger)
    - Webhook (campaign performance alert)
    - Pipeline event (signals collected)
    
    Returns: SignalContext with intent + entities + context
    """
    
    async def process(self, trigger: Trigger) -> SignalContext:
        # 1. Parse trigger type
        # 2. Extract entities (brand, campaign, date_range)
        # 3. Load relevant context from memory
        # 4. Classify intent (what does user want?)
        # 5. Return enriched SignalContext
```

#### Stage 2: Plan (Route + Strategy)
```python
class PlanStage:
    """
    Plan: What's the execution strategy?
    - Classify query difficulty (Easy/Medium/Hard/Expert)
    - Select tier (1 model / 2 parallel / 3 parallel)
    - Choose providers per tier
    - Build execution plan (what to call in what order)
    
    Returns: ExecutionPlan with steps + provider assignments
    """
    
    async def plan(self, context: SignalContext) -> ExecutionPlan:
        # 1. Intent classification (what type of marketing task?)
        # 2. Difficulty scoring (0-100)
        # 3. Tier assignment (1/2/3 based on threshold)
        # 4. Provider selection per tier
        # 5. Build ordered step list
```

#### Stage 3: Execute (Ensemble + Fallback)
```python
class ExecuteStage:
    """
    Execute: Run the plan with parallel ensemble + fallback.
    
    Pattern from A3M: ALL providers run in parallel FIRST
    Then fallback chain if all fail.
    
    Returns: EnsembleResult with responses + quality scores
    """
    
    async def execute(self, plan: ExecutionPlan) -> EnsembleResult:
        # TIER 1: Parallel execution
        tier1_tasks = [self.call_provider(p, plan) for p in plan.tier1]
        tier1_results = await asyncio.gather(*tier1_tasks, return_exceptions=True)
        
        # Check if confidence threshold met
        if self.quality_tracker.get_confidence(tier1_results) >= plan.threshold:
            return EnsembleResult(responses=tier1_results, tier_used=1)
        
        # TIER 2: Parallel execution
        tier2_tasks = [self.call_provider(p, plan) for p in plan.tier2]
        tier2_results = await asyncio.gather(*tier2_tasks, return_exceptions=True)
        
        if self.quality_tracker.get_confidence(tier2_results) >= plan.threshold:
            return EnsembleResult(responses=tier2_results, tier_used=2)
        
        # TIER 3: Expert fallback
        return await self.fallback_chain(plan.tier3)
```

#### Stage 4: Respond (Merge + Format + Deliver)
```python
class RespondStage:
    """
    Respond: Merge ensemble results + format + deliver.
    
    Pattern from A3M: Confidence-weighted voting for merge
    Pattern from OmniClaw: Response synthesized from all providers
    """
    
    async def respond(self, result: EnsembleResult) -> Response:
        # 1. Confidence-weighted merge
        merged = self.merger.merge(result.responses, method="confidence_weighted")
        
        # 2. Format based on delivery channel (CLI/JSON/Slack/WhatsApp)
        formatted = self.formatter.format(merged, context.delivery_channel)
        
        # 3. Send to channel
        await self.delivery.send(formatted, context.channel)
        
        # 4. Learn from quality
        await self.quality_tracker.record(result)
```

#### Stage 5: Learn (Feedback Loop)
```python
class LearnStage:
    """
    Learn: Track quality per provider per task type.
    Adjust thresholds dynamically.
    
    Pattern from A3M: Dynamic threshold optimization
    """
    
    async def learn(self, result: EnsembleResult, context: SignalContext):
        # 1. Record quality score per provider
        for response in result.responses:
            await self.quality_tracker.record(
                provider=response.provider,
                task_type=context.intent,
                quality=response.quality,
                latency=response.latency,
                cost=response.cost
            )
        
        # 2. Adjust thresholds
        await self.threshold_optimizer.adjust(
            task_type=context.intent,
            recent_accuracy=self.quality_tracker.get_recent_accuracy(context.intent)
        )
        
        # 3. Update provider profiles
        await self.provider_registry.update_profiles(
            self.quality_tracker.get_provider_stats()
        )
```

---

## Part II: Routing Architecture

### The Three-Layer Router (A3M Pattern)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROUTER LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 1: Intent Classifier  → What TYPE of marketing task?               │
│  Layer 2: Difficulty Scorer → How COMPLEX is this?                       │
│  Layer 3: Tier Selector    → Which TIER to use?                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Intent Classification
```python
class IntentClassifier:
    """
    Classify what TYPE of marketing task this is.
    
    Based on OmniClaw's hyperagentRoute pattern.
    Uses keyword matching + embedding similarity.
    """
    
    INTENTS = [
        "competitor_research",   # "analyze competitor X"
        "creative_generation",   # "generate ad copy for X"
        "campaign_optimization", # "optimize campaign X ROAS"
        "budget_routing",       # "rebalance budget across channels"
        "performance_review",   # "show campaign performance"
        "attribution_analysis", # "attribute conversions to channels"
        "email_campaign",        # "create email sequence for X"
        "landing_page",          # "build landing page for X"
        "ab_test_analysis",     # "analyze A/B test results"
        "roi_report",           # "generate ROI report"
    ]
    
    async def classify(self, query: str) -> IntentPrediction:
        # 1. Keyword matching
        keywords = self.extract_keywords(query)
        
        # 2. Embed query + compute similarity to intent templates
        embedding = await self.embedding_model.encode(query)
        scores = {
            intent: cosine_similarity(embedding, self.intent_embeddings[intent])
            for intent in self.INTENTS
        }
        
        # 3. Return top intent + confidence
        top_intent = max(scores, key=scores.get)
        return IntentPrediction(
            intent=top_intent,
            confidence=scores[top_intent],
            all_scores=scores
        )
```

### Layer 2: Difficulty Scoring
```python
class DifficultyScorer:
    """
    Score query difficulty 0-100.
    
    Based on A3M's feature-based difficulty scoring.
    Features: length, complexity, multi-step, technical keywords.
    """
    
    async def score(self, query: str, intent: str) -> DifficultyScore:
        features = {
            "word_count": len(query.split()),
            "char_count": len(query),
            "question_marks": query.count("?"),
            "multi_step_keywords": sum(1 for kw in ["and", "then", "also", "plus"] if kw in query),
            "technical_keywords": sum(1 for kw in INTENSITY_KEYWORDS if kw in query.lower()),
            "comparison_keywords": sum(1 for kw in ["vs", "versus", "compare", "difference"] if kw in query),
        }
        
        # Normalize to 0-100
        raw_score = self.feature_weights.dot(features)
        normalized = self.scaler.normalize(raw_score)
        
        return DifficultyScore(
            score=normalized,
            features=features,
            tier=self.score_to_tier(normalized)
        )
    
    def score_to_tier(self, score: float) -> int:
        if score < 30: return 1  # Easy: single provider
        if score < 60: return 2  # Medium: 2 providers parallel
        return 3                    # Hard: 3 providers + expert fallback
```

### Layer 3: Tier-Based Provider Selection
```python
class TierSelector:
    """
    Select providers based on task type + difficulty.
    
    Based on A3M's tier routing with provider profiles.
    """
    
    PROVIDER_PROFILES = {
        "competitor_intel": {
            1: ["gomarble"],           # Single: GoMarble handles Meta Ad Library
            2: ["gomarble", "apify"], # Parallel: GoMarble + Apify scraper
            3: ["gomarble", "apify", "firecrawl"],  # + deep scraping
        },
        "creative_generation": {
            1: ["qwen3:4b"],          # Local: fast turnaround
            2: ["qwen3:4b", "groq:llama-3.1-8b"],  # Parallel ensemble
            3: ["qwen3:4b", "groq:llama-3.1-8b", "claude-sonnet"],  # + expert
        },
        "campaign_optimization": {
            1: ["groq:llama-3.1-8b"],  # Fast: bidding recommendations
            2: ["groq:llama-3.1-8b", "qwen3:4b"],
            3: ["groq:llama-3.1-8b", "qwen3:4b", "claude-sonnet"],
        },
        "seo_content": {
            1: ["qwen3:4b"],
            2: ["qwen3:4b", "groq:llama-3.1-8b"],
            3: ["qwen3:4b", "claude-sonnet", "gemini-2.0-flash"],
        },
    }
    
    def select_tier(self, intent: str, difficulty: int) -> List[str]:
        tier = self.score_to_tier(difficulty)
        return self.PROVIDER_PROFILES.get(intent, {}).get(tier, ["qwen3:4b"])
```

---

## Part III: Ensemble Architecture (A3M Pattern)

### Parallel Ensemble with Confidence Voting
```python
class EnsembleExecutor:
    """
    Execute providers in parallel, merge with confidence-weighted voting.
    
    Pattern from A3M Router:
    1. All tier-1 providers run in parallel
    2. Check if confidence threshold met
    3. If not, add tier-2 in parallel
    4. If still not, use expert fallback
    
    Returns merged result with quality score.
    """
    
    def __init__(self):
        self.provider_registry = ProviderRegistry()
        self.quality_tracker = QualityTracker()
        self.threshold_optimizer = ThresholdOptimizer()
    
    async def execute(self, plan: ExecutionPlan) -> EnsembleResult:
        # Dynamic threshold from optimizer
        threshold = await self.threshold_optimizer.get_threshold(
            plan.intent, 
            self.quality_tracker.get_recent_accuracy(plan.intent)
        )
        
        results = []
        
        # TIER 1: Parallel
        tier1_tasks = [
            self.call_provider(provider, plan)
            for provider in plan.tier1
        ]
        tier1_results = await asyncio.gather(*tier1_tasks, return_exceptions=True)
        valid_tier1 = [r for r in tier1_results if not isinstance(r, Exception)]
        results.extend(valid_tier1)
        
        # Check confidence
        confidence = self.calculate_confidence(valid_tier1)
        if confidence >= threshold:
            return self.merge_and_finalize(results, tier_used=1)
        
        # TIER 2: Parallel (add to existing)
        tier2_tasks = [
            self.call_provider(provider, plan)
            for provider in plan.tier2
        ]
        tier2_results = await asyncio.gather(*tier2_tasks, return_exceptions=True)
        valid_tier2 = [r for r in tier2_results if not isinstance(r, Exception)]
        results.extend(valid_tier2)
        
        confidence = self.calculate_confidence(results)
        if confidence >= threshold:
            return self.merge_and_finalize(results, tier_used=2)
        
        # TIER 3: Expert fallback (sequential)
        expert_result = await self.expert_fallback(plan.tier3, plan)
        results.append(expert_result)
        
        return self.merge_and_finalize(results, tier_used=3)
    
    def calculate_confidence(self, results: List[ProviderResult]) -> float:
        """
        Confidence = weighted average of individual confidence scores.
        Based on A3M's confidence-weighted voting.
        """
        if not results:
            return 0.0
        
        total_confidence = sum(r.confidence * r.quality_weight for r in results)
        total_weight = sum(r.quality_weight for r in results)
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def merge_and_finalize(self, results: List[ProviderResult], tier_used: int):
        """
        Merge results using confidence-weighted voting.
        Based on A3M's ensemble strategy.
        """
        # Sort by confidence
        sorted_results = sorted(results, key=lambda r: r.confidence, reverse=True)
        
        # Merge content
        merged_content = self.merger.merge(
            [r.content for r in sorted_results],
            method="confidence_weighted"
        )
        
        # Build metadata
        metadata = {
            "tier_used": tier_used,
            "providers_called": [r.provider_id for r in sorted_results],
            "avg_confidence": sum(r.confidence for r in sorted_results) / len(sorted_results),
            "total_cost": sum(r.cost for r in sorted_results),
            "total_latency_ms": max(r.latency_ms for r in sorted_results),
        }
        
        return EnsembleResult(
            content=merged_content,
            confidence=metadata["avg_confidence"],
            metadata=metadata,
            results=sorted_results
        )
```

---

## Part IV: Dynamic Threshold Optimizer (A3M Pattern)

### Adaptive Threshold Adjustment
```python
class ThresholdOptimizer:
    """
    Dynamically adjust ensemble thresholds based on recent accuracy.
    
    Based on A3M's DynamicThresholdOptimizer:
    - High recent accuracy → Raise threshold (save cost)
    - Low recent accuracy → Lower threshold (more ensemble)
    - Rate limit pressure → Raise threshold (conserve capacity)
    """
    
    EASY_THRESHOLD = 0.15
    MEDIUM_THRESHOLD = 0.50
    
    async def get_threshold(self, intent: str, recent_accuracy: float) -> float:
        # Base threshold by difficulty
        base = self.difficulty_to_base_threshold(intent)
        
        # Adjust based on recent accuracy
        if recent_accuracy > 0.50:
            # We're doing well → raise threshold (reduce ensemble, save cost)
            adjustment = +0.10 * (recent_accuracy - 0.50)
        elif recent_accuracy < 0.40:
            # We're struggling → lower threshold (more ensemble)
            adjustment = -0.15 * (0.40 - recent_accuracy)
        else:
            adjustment = 0
        
        return max(0.10, min(0.95, base + adjustment))
    
    async def record_outcome(self, intent: str, quality: float, tier_used: int):
        """Record the quality outcome of a routing decision."""
        await self.history.append({
            "intent": intent,
            "quality": quality,
            "tier_used": tier_used,
            "timestamp": time.time()
        })
        
        # Recalculate recent accuracy
        recent = [h for h in self.history[-20:] if h["intent"] == intent]
        if recent:
            avg_quality = sum(h["quality"] for h in recent) / len(recent)
            await self.provider_registry.update_intent_accuracy(intent, avg_quality)
```

---

## Part V: Provider Registry (A3M + OmniClaw Pattern)

### Unified Provider Abstraction
```python
class ProviderRegistry:
    """
    Unified registry for all providers (LLMs, MCPs, external APIs).
    
    Pattern from OmniClaw's skills/providers/registry.py + A3M's provider setup.
    """
    
    def __init__(self):
        self.providers: Dict[str, Provider] = {}
        self.profiles: Dict[str, ProviderProfile] = {}
        self.health: Dict[str, HealthStatus] = {}
    
    def register(self, provider: Provider):
        self.providers[provider.id] = provider
        self.profiles[provider.id] = ProviderProfile(
            id=provider.id,
            name=provider.name,
            capabilities=provider.capabilities,
            strengths=provider.strengths,
            weaknesses=provider.weaknesses,
            cost_per_1k_input=provider.cost_per_1k_input,
            cost_per_1k_output=provider.cost_per_1k_output,
            latency_ms_p50=provider.latency_p50,
            accuracy_by_intent={},  # Updated by quality tracker
        )
        self.health[provider.id] = HealthStatus(available=True, failures=0)
    
    def get_providers_for(self, intent: str, tier: int) -> List[Provider]:
        """Get providers that handle this intent at this tier."""
        candidates = [
            p for p in self.providers.values()
            if intent in p.capabilities
        ]
        
        # Sort by profile accuracy for this intent
        candidates.sort(
            key=lambda p: self.profiles[p.id].accuracy_by_intent.get(intent, 0.5),
            reverse=True
        )
        
        return candidates[:tier]


class Provider(ABC):
    """Abstract base for all providers."""
    
    @abstractmethod
    async def call(self, prompt: str, **kwargs) -> ProviderResult:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass


class LLMProvider(Provider):
    """LLM provider (OpenAI, Anthropic, Groq, Ollama, etc.)."""
    
    def __init__(
        self,
        provider_id: str,
        name: str,
        api_type: str,  # "openai" | "anthropic" | "groq" | "ollama"
        model: str,
        api_key: str = None,
        endpoint: str = None,
        capabilities: List[str] = None,
        strengths: List[str] = None,
        weaknesses: List[str] = None,
    ):
        self.id = provider_id
        self.name = name
        self.api_type = api_type
        self.model = model
        self.api_key = api_key or os.environ.get(f"{provider_id.upper()}_API_KEY")
        self.endpoint = endpoint
        self.capabilities = capabilities or []
        self.strengths = strengths or []
        self.weaknesses = weaknesses or []
        
        # Rate limiting
        self.rate_limiter = TokenBucket(rpm=self.default_rpm)
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )


class MCPProvider(Provider):
    """
    MCP provider (GoMarble, Composio, Apify, Goose Ads, etc.).
    
    MCPs are treated as providers in the routing system.
    """
    
    def __init__(
        self,
        provider_id: str,
        name: str,
        mcp_command: str,  # e.g., "npx @gomarble/mcp"
        capabilities: List[str] = None,
        env: Dict[str, str] = None,
    ):
        super().__init__()
        self.id = provider_id
        self.name = name
        self.mcp_command = mcp_command
        self.capabilities = capabilities or []
        self.env = env or {}
        self.process = None  # MCP server process
    
    async def call(self, prompt: str, **kwargs) -> ProviderResult:
        # Start MCP server if not running
        if not self.process:
            self.process = await self._start_server()
        
        # Send request via JSON-RPC
        response = await self._send_request(
            method=kwargs.get("method", "complete"),
            params={"prompt": prompt, **kwargs}
        )
        
        return ProviderResult(
            provider_id=self.id,
            content=response["content"],
            confidence=response.get("confidence", 0.8),
            latency_ms=response.get("latency_ms", 0),
            cost=0,  # MCP costs are API-key based
        )
    
    async def health_check(self) -> bool:
        try:
            await self._send_request(method="ping")
            return True
        except:
            return False
```

---

## Part VI: Middleware Pipeline (OmniClaw Pattern)

### Composable Middleware Chain
```python
class MiddlewarePipeline:
    """
    Composable middleware for provider calls.
    
    Pattern from OmniClaw's browser MCP middleware:
    guardrails → cost_tracker → semantic_cache → 
    circuit_breaker → retry → rate_limiter
    """
    
    def __init__(self):
        self.middlewares: List[Middleware] = []
    
    def use(self, middleware: Middleware):
        self.middlewares.append(middleware)
    
    async def execute(self, ctx: RequestContext, next_fn):
        # Build chain
        async def chain(index: int):
            if index >= len(self.middlewares):
                return await next_fn()
            mw = self.middlewares[index]
            return await mw.process(ctx, lambda: chain(index + 1))
        
        return await chain(0)


class RateLimitMiddleware:
    """Rate limiting per provider."""
    
    async def process(self, ctx: RequestContext, next_fn):
        provider = ctx.provider
        
        if not await provider.rate_limiter.try_acquire():
            # Backpressure
            wait_time = provider.rate_limiter.wait_time()
            if wait_time > 30:  # Too long to wait
                raise RateLimitExceeded(provider.id, wait_time)
            await asyncio.sleep(wait_time)
        
        return await next_fn()


class CircuitBreakerMiddleware:
    """Circuit breaker pattern for failing providers."""
    
    async def process(self, ctx: RequestContext, next_fn):
        provider = ctx.provider
        
        if provider.circuit_breaker.is_open():
            if provider.circuit_breaker.should_try():
                provider.circuit_breaker.half_open()
            else:
                raise CircuitOpen(provider.id)
        
        try:
            result = await next_fn()
            provider.circuit_breaker.success()
            return result
        except Exception as e:
            provider.circuit_breaker.failure()
            raise


class RetryMiddleware:
    """Exponential backoff retry."""
    
    async def process(self, ctx: RequestContext, next_fn):
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                return await next_fn()
            except (RateLimitError, TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)


class SemanticCacheMiddleware:
    """
    Cache responses by semantic similarity.
    
    Pattern from OmniClaw: 85% cost savings on repeated queries.
    """
    
    def __init__(self, cache_dir: str = ".cache/semantic"):
        self.cache = SemanticCache(cache_dir)
        self.embedding_model = EmbeddingModel()
    
    async def process(self, ctx: RequestContext, next_fn):
        # Check cache
        embedding = await self.embedding_model.encode(ctx.prompt)
        cached = self.cache.get(embedding, threshold=0.95)
        
        if cached:
            return CachedResult(cached, hit=True)
        
        result = await next_fn()
        
        # Store in cache
        await self.cache.set(embedding, result)
        
        return result
```

---

## Part VII: Memory Architecture (OmniClaw Pattern)

### Three-Layer Memory
```python
class MemoryLayer:
    """
    Three-layer memory: Session → Persistent → Semantic.
    
    Pattern from OmniClaw's conversationMemory + persistent memory.
    """
    
    def __init__(self, db_path: str = "marketic_memory.db"):
        self.session: Dict[str, Any] = {}  # In-memory session
        self.persistent = PersistentMemory(db_path)  # SQLite
        self.semantic = SemanticMemory()  # Embeddings
    
    async def store_signal(self, signal: Signal):
        """Store a signal in all layers."""
        # Persistent: raw signal
        await self.persistent.store_signal(signal)
        
        # Semantic: for retrieval
        embedding = await self.embedding_model.encode(signal.content)
        await self.semantic.store(embedding, signal)
    
    async def get_context(self, query: str, limit: int = 10) -> List[Any]:
        """Get relevant context for a query."""
        embedding = await self.embedding_model.encode(query)
        
        # Get from semantic
        semantic_results = await self.semantic.search(embedding, limit=limit)
        
        # Get from persistent (recent)
        recent = await self.persistent.get_recent(limit=5)
        
        return deduplicate_merge(semantic_results, recent)


class PersistentMemory:
    """
    SQLite-backed persistent memory.
    
    Stores: campaigns, creatives, signals, theses, A/B tests.
    Pattern from OmniClaw's GCS-backed context persistence.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_schema()
    
    async def store_signal(self, signal: Signal):
        # Store in signals table
        pass
    
    async def get_campaigns(self, filters: dict) -> List[Campaign]:
        pass
    
    async def get_creative_variants(
        self, 
        campaign_id: str = None,
        channel: str = None,
        sort_by: str = "roas",
        limit: int = 20
    ) -> List[CreativeVariant]:
        """
        Get creative variants with optional filtering.
        Pattern from OmniClaw: enrich query with GCS context.
        """
        pass


class SemanticMemory:
    """
    Embedding-based semantic memory for retrieval.
    
    Uses sentence-transformers for embeddings.
    """
    
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = FAISS.IndexFlatIP(384)
    
    async def store(self, embedding: np.ndarray, data: Any):
        self.index.add(embedding.reshape(1, -1))
        self.data_store.append(data)
    
    async def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 10
    ) -> List[Any]:
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)
        return [self.data_store[i] for i in indices[0]]
```

---

## Part VIII: Skill/Agent Bridge (OmniClaw Pattern)

### Slash Command → Skill Execution
```python
class SkillBridge:
    """
    Bridge CLI slash commands to skill execution.
    
    Pattern from OmniClaw's slash command handling:
    /competitor → CompetitorResearchSkill
    /optimize    → CampaignOptimizerSkill
    /report      → ReportingSkill
    """
    
    SKILL_REGISTRY = {
        # Marketing-specific skills
        "competitor": CompetitorResearchSkill,
        "intel": CompetitorResearchSkill,
        "analyze": CompetitorResearchSkill,
        
        "creative": CreativeGenerationSkill,
        "generate": CreativeGenerationSkill,
        "copy": CreativeGenerationSkill,
        
        "optimize": CampaignOptimizerSkill,
        "roas": CampaignOptimizerSkill,
        "bid": CampaignOptimizerSkill,
        
        "report": ReportingSkill,
        "attribution": AttributionSkill,
        
        "email": EmailSkill,
        "land": LandingPageSkill,
        "ab": ABTestSkill,
        
        # Built-in engineering skills
        "diagnose": DiagnoseSkill,
        "grill": GrillMeSkill,
        "tdd": TDDSkill,
        "triage": TriageSkill,
    }
    
    async def execute(self, command: str, args: List[str]) -> ExecutionResult:
        # Parse command
        skill_name = command.lstrip("/")
        params = self.parse_args(args)
        
        # Get skill class
        skill_cls = self.SKILL_REGISTRY.get(skill_name)
        if not skill_cls:
            raise SkillNotFound(skill_name)
        
        # Create skill instance with dependencies
        skill = skill_cls(
            router=self.router,
            memory=self.memory,
            mcp_registry=self.mcp_registry,
        )
        
        # Execute with middleware
        ctx = ExecutionContext(command=command, params=params)
        
        return await self.middleware_pipeline.execute(
            ctx,
            lambda: skill.execute(params)
        )


class BaseSkill(ABC):
    """Base class for all marketing skills."""
    
    def __init__(
        self,
        router: 'EnsembleExecutor',
        memory: 'MemoryLayer',
        mcp_registry: 'ProviderRegistry',
    ):
        self.router = router
        self.memory = memory
        self.mcp_registry = mcp_registry
    
    @abstractmethod
    async def execute(self, params: dict) -> ExecutionResult:
        pass
    
    async def plan(self, objective: str) -> ExecutionPlan:
        """Plan how to achieve an objective using the router."""
        intent = await self.router.classifier.classify(objective)
        difficulty = await self.router.scorer.score(objective, intent.intent)
        tier = self.router.selector.select_tier(intent.intent, difficulty.tier)
        
        return ExecutionPlan(
            objective=objective,
            intent=intent,
            difficulty=difficulty,
            tier=tier,
            providers=self.router.provider_registry.get_providers_for(intent.intent, tier),
        )
```

---

## Part IX: MCP Integration (OmniClaw Pattern)

### MCPs as Routing-Aware Providers
```python
class MCPRouter:
    """
    Integrate MCPs into the routing system.
    
    MCPs are treated as specialized providers.
    The router decides WHEN to use which MCP.
    
    Pattern from OmniClaw: MCPs are providers, not standalone tools.
    """
    
    def __init__(self):
        self.mcp_servers: Dict[str, MCPProcess] = {}
        self.capability_map = {
            # Which MCP handles which capability
            "competitor_ads": ["gomarble", "goose_ads"],
            "web_scraping": ["apify", "firecrawl"],
            "tiktok_video": ["revid"],
            "google_ads": ["higgsfield"],
            "social_media": ["apify"],
        }
    
    async def call_mcp(
        self,
        capability: str,
        method: str,
        params: dict
    ) -> ProviderResult:
        """Route to the best MCP for this capability."""
        candidates = self.capability_map.get(capability, [])
        
        # Try each candidate until one succeeds
        for mcp_id in candidates:
            mcp = self.mcp_servers.get(mcp_id)
            if not mcp or not await mcp.health_check():
                continue
            
            try:
                result = await mcp.call(method, params)
                await self.quality_tracker.record(mcp_id, capability, result.quality)
                return result
            except Exception as e:
                self.provider_registry.mark_failure(mcp_id)
                continue
        
        raise NoMCPAvailable(capability)
    
    def get_mcp_for_task(self, task: str) -> Optional[str]:
        """Get the best MCP server for a task type."""
        for capability, mcp_ids in self.capability_map.items():
            if capability in task.lower():
                # Return the best-performing one
                return self.quality_tracker.get_best(mcp_ids)
        return None
```

---

## Part X: Event Bus Architecture

### Pub/Sub for Module Communication
```python
class EventBus:
    """
    Simple pub/sub event bus for module communication.
    
    Pattern: signals → analytics → performance → routing (feedback loop)
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
    
    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        handlers = self.subscribers.get(event.type, [])
        
        # Run all handlers in parallel
        tasks = [h(event) for h in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        self.subscribers[event_type].remove(handler)


class Event:
    """Base event class."""
    type: str
    data: dict
    timestamp: float = time.time()


# Event types
class SignalCollectedEvent(Event):
    type = "signal.collected"


class CreativeGeneratedEvent(Event):
    type = "creative.generated"


class CampaignLaunchedEvent(Event):
    type = "campaign.launched"


class PerformanceAlertEvent(Event):
    type = "performance.alert"  # CPA/ROAS threshold breached


class AttributionComputedEvent(Event):
    type = "attribution.computed"


class ThresholdAdjustedEvent(Event):
    type = "threshold.adjusted"


# Example: Subscribe to performance alerts
async def on_performance_alert(event: PerformanceAlertEvent):
    # Trigger optimization
    plan = await optimizer.plan_alert_response(event.data)
    result = await executor.execute(plan)
    await notifier.alert(f"Optimization applied: {result.summary}")


event_bus.subscribe("performance.alert", on_performance_alert)
```

---

## Part XI: New Directory Structure

```
marketic/
├── CLAUDE.md
├── README.md
├── PLAN.md
├── ARCHITECTURE_REDESIGN.md  ← This document
├── requirements.txt
├── setup.py
│
├── marketic/                    # Main package
│   │
│   │   # PIPELINE (canonical flow)
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── engine.py            # Main pipeline orchestrator
│   │   ├── stages/
│   │   │   ├── signal.py       # Stage 1: Signal + context
│   │   │   ├── plan.py         # Stage 2: Route + strategy
│   │   │   ├── execute.py      # Stage 3: Ensemble + fallback
│   │   │   ├── respond.py      # Stage 4: Merge + deliver
│   │   │   └── learn.py       # Stage 5: Feedback loop
│   │   └── events.py           # Event bus
│   │
│   │   # ROUTING (A3M pattern)
│   │
│   ├── router/
│   │   ├── __init__.py
│   │   ├── classifier.py       # Layer 1: Intent classification
│   │   ├── scorer.py          # Layer 2: Difficulty scoring
│   │   ├── selector.py        # Layer 3: Tier provider selection
│   │   ├── tier_router.py     # Tier routing logic
│   │   ├── ensemble.py         # Parallel ensemble executor
│   │   ├── merger.py           # Confidence-weighted merging
│   │   └── thresholds.py      # Dynamic threshold optimizer
│   │
│   │   # PROVIDERS (A3M + OmniClaw pattern)
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── registry.py        # Unified provider registry
│   │   ├── base.py            # Abstract Provider base
│   │   ├── llm_provider.py    # LLM provider (OpenAI, Anthropic, etc.)
│   │   ├── mcp_provider.py   # MCP provider wrapper
│   │   ├── health.py          # Health tracking + circuit breaker
│   │   └── rate_limiter.py    # Token bucket rate limiter
│   │
│   │   # LLM PROVIDERS
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── groq_provider.py
│   │   ├── ollama_provider.py
│   │   ├── minimax_provider.py
│   │   └── openrouter_provider.py
│   │
│   │   # MCP PROVIDERS (each is a provider)
│   │   ├── gomarble.py
│   │   ├── composio.py
│   │   ├── goose_ads.py
│   │   ├── apify.py
│   │   ├── revid.py
│   │   ├── firecrawl.py
│   │   ├── browser_mcp.py
│   │   ├── google_analytics.py
│   │   ├── n8n_mcp.py
│   │   └── higgsfield.py
│   │
│   │   # MIDDLEWARE (OmniClaw pattern)
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── pipeline.py         # Composable middleware chain
│   │   ├── rate_limit.py
│   │   ├── circuit_breaker.py
│   │   ├── retry.py           # Exponential backoff
│   │   ├── semantic_cache.py   # Embedding-based cache
│   │   ├── cost_tracker.py    # Per-provider cost tracking
│   │   └── guardrails.py       # Content policy enforcement
│   │
│   │   # MEMORY (OmniClaw pattern)
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── layer.py           # Three-layer memory facade
│   │   ├── session.py         # In-memory session
│   │   ├── persistent.py      # SQLite persistent storage
│   │   ├── semantic.py        # FAISS embedding search
│   │   └── quality_tracker.py # Provider quality tracking
│   │
│   │   # SKILLS (OmniClaw pattern)
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── bridge.py          # Slash command → skill execution
│   │   ├── base.py           # BaseSkill abstract class
│   │   ├── competitor.py      # CompetitorResearchSkill
│   │   ├── creative.py        # CreativeGenerationSkill
│   │   ├── optimizer.py        # CampaignOptimizerSkill
│   │   ├── attribution.py     # AttributionSkill
│   │   ├── email.py           # EmailSkill
│   │   ├── landing.py         # LandingPageSkill
│   │   ├── abtest.py          # ABTestSkill
│   │   └── reporting.py       # ReportingSkill
│   │
│   │   # DOMAIN MODULES (capabilities)
│   │
│   ├── signals/               # Signal intelligence
│   │   └── collectors/ (reddit, twitter, trends)
│   │
│   ├── competitive/           # Competitive intelligence
│   │
│   ├── creative/             # Creative generation
│   │
│   ├── campaign/             # Campaign management
│   │
│   ├── analytics/            # Attribution + reporting
│   │
│   ├── performance/           # ROAS, bids, budget
│   │
│   ├── email/               # Email marketing
│   │
│   ├── landing/              # Landing pages
│   │
│   ├── ab_test/             # A/B testing
│   │
│   ├── sms/                 # SMS/WhatsApp
│   │
│   ├── push/                # Push notifications
│   │
│   ├── crm/                 # CRM integration
│   │
│   ├── cdp/                 # Customer data platform
│   │
│   ├── revenue/             # Margin/P&L tracking
│   │
│   ├── retention/           # Churn/win-back
│   │
│   ├── influencer/          # Influencer marketing
│   │
│   ├── affiliate/           # Affiliate management
│   │
│   ├── distribution/         # Content distribution
│   │
│   ├── collaboration/       # Team collaboration
│   │
│   │   # CLI (entry point)
│   │
│   └── cli/
│       ├── __init__.py
│       ├── main.py            # Main CLI entry
│       ├── context.py         # CLI context management
│       └── commands/
│           ├── competitor.py
│           ├── creative.py
│           ├── campaign.py
│           ├── optimize.py
│           ├── report.py
│           ├── email.py
│           ├── landing.py
│           └── ab.py
│
├── tests/
│   ├── test_pipeline.py
│   ├── test_router.py
│   ├── test_ensemble.py
│   ├── test_middleware.py
│   ├── test_memory.py
│   └── test_skills.py
│
└── examples/
    ├── config.yaml            # Provider + MCP config
    ├── run_pipeline.sh
    └── examples/
        ├── competitor_research.py
        ├── creative_generation.py
        ├── campaign_optimization.py
        └── full_funnel.py
```

---

## Part XII: Quality Tracker (A3M Pattern)

### Per-Provider Per-Intent Quality Tracking
```python
class QualityTracker:
    """
    Track quality scores per provider per task type.
    Update provider profiles based on actual performance.
    
    Pattern from A3M: record quality after each call,
    use to adjust thresholds and provider selection.
    """
    
    def __init__(self, db_path: str = "marketic_memory.db"):
        self.db_path = db_path
        self._init_schema()
    
    async def record(
        self,
        provider_id: str,
        task_type: str,
        quality: float,      # 0-1
        latency_ms: float,
        cost: float,
    ):
        """Record a quality observation."""
        await self.db.execute("""
            INSERT INTO quality_history 
            (provider_id, task_type, quality, latency_ms, cost, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [provider_id, task_type, quality, latency_ms, cost, time.time()])
    
    def get_provider_stats(self, provider_id: str) -> ProviderStats:
        """Get aggregate stats for a provider."""
        rows = self.db.execute("""
            SELECT task_type, AVG(quality), COUNT(*), AVG(cost)
            FROM quality_history
            WHERE provider_id = ? AND created_at > ?
            GROUP BY task_type
        """, [provider_id, time.time() - 7*24*3600])
        
        return ProviderStats(
            provider_id=provider_id,
            accuracy_by_intent={r[0]: r[1] for r in rows},
            total_calls=sum(r[2] for r in rows),
            avg_cost=sum(r[3] for r in rows) / len(rows) if rows else 0,
        )
    
    def get_recent_accuracy(self, task_type: str, window: int = 20) -> float:
        """Get recent accuracy for a task type across all providers."""
        rows = self.db.execute("""
            SELECT AVG(quality) 
            FROM quality_history 
            WHERE task_type = ? AND created_at > ?
            ORDER BY created_at DESC
            LIMIT ?
        """, [task_type, time.time() - 7*24*3600, window])
        
        return rows[0][0] if rows else 0.5
    
    def get_best_provider(self, task_type: str, limit: int = 3) -> List[str]:
        """Get best-performing providers for a task type."""
        rows = self.db.execute("""
            SELECT provider_id, AVG(quality) as avg_q
            FROM quality_history
            WHERE task_type = ? AND created_at > ?
            GROUP BY provider_id
            ORDER BY avg_q DESC
            LIMIT ?
        """, [task_type, time.time() - 7*24*3600, limit])
        
        return [r[0] for r in rows]
```

---

## Part XIII: Migration Plan

### Phase 1: Core Pipeline (Weeks 1-2)
- [ ] `pipeline/engine.py` + stages
- [ ] `router/classifier.py` + `scorer.py` + `selector.py`
- [ ] `providers/registry.py` + `base.py` + 3 LLM providers
- [ ] `middleware/pipeline.py` + rate_limit + circuit_breaker
- [ ] `memory/layer.py` + persistent

### Phase 2: Ensemble + Quality (Week 3)
- [ ] `router/ensemble.py` + `merger.py`
- [ ] `router/thresholds.py`
- [ ] `memory/quality_tracker.py`
- [ ] `memory/semantic.py`

### Phase 3: Skills + CLI (Week 4)
- [ ] `skills/bridge.py` + base + 3 skills
- [ ] `cli/main.py` with slash commands

### Phase 4: Domain Modules (Weeks 5-8)
- [ ] Port existing domain modules (signals, competitive, creative, etc.)
- [ ] Integrate MCPs as providers

### Phase 5: Advanced Routing (Weeks 9-10)
- [ ] `router/tier_router.py` with difficulty awareness
- [ ] `middleware/semantic_cache.py`
- [ ] `middleware/retry.py`

---

## Summary: 12 Architectural Patterns Applied

| # | Pattern | Source | Where Applied |
|---|---------|--------|---------------|
| 1 | Signal→Plan→Execute→Respond | OmniClaw | `pipeline/engine.py` |
| 2 | Parallel ensemble first, fallback second | OmniClaw | `router/ensemble.py` |
| 3 | Tier-based routing (1/2/3 models) | A3M | `router/tier_router.py` |
| 4 | Feature-based difficulty scoring | A3M | `router/scorer.py` |
| 5 | Dynamic threshold optimization | A3M | `router/thresholds.py` |
| 6 | Confidence-weighted voting | A3M | `router/merger.py` |
| 7 | Unified provider registry | OmniClaw | `providers/registry.py` |
| 8 | Middleware pipeline (guardrails, cache, cb) | OmniClaw | `middleware/pipeline.py` |
| 9 | Three-layer memory (session, persistent, semantic) | OmniClaw | `memory/layer.py` |
| 10 | Slash command → skill bridge | OmniClaw | `skills/bridge.py` |
| 11 | MCPs as routing-aware providers | OmniClaw | `mcp_provider.py` |
| 12 | Quality tracking per provider per intent | A3M | `memory/quality_tracker.py` |
