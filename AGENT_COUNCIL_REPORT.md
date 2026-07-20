# Agent Council Review: MAIS 2.0 Architectural Decisions

**Reviewed by:** Claude MiniMax, Gemini 2.5 Flash, Claude Opus, Gemini Pro, Claude Haiku, Claude (general-purpose)  
**Date:** 2026-07-02  
**Decisions Reviewed:** 6

---

## VERDICT SUMMARY

| Decision | Verdict | Agent(s) |
|----------|---------|----------|
| Two-Loop Autoresearch (Orchestra) | FLAG | Claude MiniMax, Gemini Flash |
| Knowledge Graph as Primary Memory | FLAG | Claude Opus |
| A-Evolve Self-Improvement Loop | FLAG | Claude MiniMax |
| Fine-Tuned Small Model Router | FLAG | Gemini Pro |
| Skills Library Architecture | FLAG | Gemini Flash |
| n8n + MCP Tool Layer | FLAG | Claude |
| GEO as First-Class Feature | FLAG | Claude Haiku |

**Overall: 7 FLAGS — No clear approvals, no rejections.**

---

## DECISION 1: Two-Loop Autoresearch Architecture (Orchestra Pattern)

**Agents:** Claude MiniMax, Gemini 2.5 Flash

### Verdict: FLAG

### Claude MiniMax Analysis:
- **Strength:** Proven primitives (Karpathy lineage), knowledge graph persistence, heartbeat continuity
- **Weakness:** INNER LOOP frequency ("every minute/hour") incompatible with marketing experiment timelines (days/weeks). ROAS has high variance. No proposed noise-handling mechanism.
- **Reasoning:** "Transplants a research-domain pattern into fundamentally different operational environment without accounting for temporal dynamics and signal-to-noise ratio differences between scientific research and marketing optimization."

### Gemini Flash Analysis:
- **Strength:** Two-loop separation is theoretically sound for varying feedback latencies
- **Weakness:** INNER LOOP iteration frequency ("every minute/hour") fundamentally incompatible with marketing experimentation. ROAS feedback requires days, not hours.
- **Reasoning:** The proposed frequencies assume rapid iteration cycles. Marketing does not provide them.

### Specific Conditions for Approval:
1. INNER LOOP must adapt to marketing timescales (daily for ad performance, weekly for campaign outcomes)
2. Must implement statistical significance testing before recording to knowledge graph
3. Outer loop synthesis must be human-reviewable (false pattern detection)
4. No direct model updates from noisy marketing metrics without denoising

---

## DECISION 2: Knowledge Graph as Primary Memory

**Agent:** Claude Opus

### Verdict: FLAG

### Analysis:
- **Strength:** Relationship-first is domain-correct for marketing (competitors, gaps, audiences, ROAS). Multi-hop reasoning is a core use case. Audit trail = decision justification.
- **Weakness:** Schema rigidity vs. marketing chaos. Entity resolution (Meta ≠ Facebook ≠ Meta Platforms) is the actual hard problem. Pure graph without vector fallback risks query brittleness.
- **Reasoning:** "If you build pure graph with no vector fallback, REJECT. If you build graph + vector hybrid with graph as the reasoning layer, APPROVE with conditions."

### Specific Conditions for Approval:
1. MUST be hybrid: Graph (reasoning/traversal) + Vector (retrieval/similarity)
2. Dynamic schema extension (open properties, not rigid)
3. Natural language interface for analyst queries
4. Accept unstructured intake → embeddings AND extracted entities

---

## DECISION 3: A-Evolve Self-Improvement Loop

**Agent:** Claude MiniMax

### Verdict: FLAG

### Analysis:
- **Strength:** Intuition is directionally correct (learn from outcomes)
- **Weakness:** Marketing feedback is fundamentally noisy. RL is not noise-tolerant. A-Evolve's evidence is from software (SWE-bench, Terminal-Bench) where ground truth is deterministic.
- **Specific Issues:**
  1. Reward hacking will be severe: Early campaigns that over-perform will be treated as high-reward, amplifying lucky configurations
  2. "3% smarter/week" is not falsifiable (no metric defined)
  3. Distribution shift breaks the loop (Q4 data ≠ Q1 conditions)
  4. No confounder-aware credit assignment

### Specific Conditions for Approval:
1. Reward denoising layer (multi-armed bandit with UCB before RL)
2. Falsifiable metric defined in advance with statistical significance testing
3. Conservative policy updates (conservative value iteration, not direct gradient)
4. Rollback capability (A/B test before full promotion)
5. Alternative to consider: Bayesian optimization with proper priors instead of vanilla RL

---

## DECISION 4: Fine-Tuned Small Model Router (Qwen3-4B)

**Agent:** Gemini Pro

### Verdict: FLAG

### Analysis:
- **Strength:** Cost/privacy (INT4 GGUF, 2GB VRAM, local). EAGLE speculative decoding (3-5× speedup).
- **Weakness:** Evidence quality is weak. "Kinetic-4B beats Claude Haiku" proves nothing (Haiku is Anthropic's smallest tier). Marketing reasoning requires nuance closer to Opus/Gemini-Pro class, not Haiku class.
- **Specific Issues:**
  1. Small model ceiling problem for multi-step marketing judgment
  2. The cited references don't validate marketing reasoning capability
  3. Claude Haiku comparison is misleading — beating Haiku doesn't mean appropriate for marketing strategic reasoning
  4. Fine-tuning requires clean labeled data at scale

### Specific Conditions for Approval:
1. Hybrid architecture: Small model for ROUTING (low stakes, classification). Claude API for REASONING (high stakes, nuanced judgment)
2. Validate on representative marketing benchmark before committing to full local inference
3. Router accuracy measurement (routing error rate)
4. Fallback to Claude for ambiguous queries

---

## DECISION 5: Skills Library Architecture (Orchestra Pattern)

**Agent:** Gemini Flash

### Verdict: FLAG

### Analysis:
- **Strength:** Dynamic dispatch, precedent at scale (Orchestra 10K+ stars), separation of capability from routing logic.
- **Weakness:** Orchestra's skills ARE code — SKILL.md is documentation alongside implementation. Proposal as stated conflates "skill as documentation" with "skill as software."
- **Specific Issues:**
  1. SKILL.md alone = documentation, not executable
  2. Maintenance grows O(skills × interactions)
  3. No skill-to-skill communication mechanism
  4. Router becomes single point of failure without structured metadata

### Specific Conditions for Approval:
1. Every SKILL.md requires backing implementation file (.py)
2. Enforced skill schema: inputs, outputs, errors, calls
3. Shared skill skeleton (base class, consistent logging/error handling)
4. Cross-skill call mechanism defined before scaling beyond 10 skills

---

## DECISION 6: n8n + MCP as Tool Layer

**Agent:** Claude

### Verdict: FLAG

### Analysis:
- **Strength:** n8n is production-hardened, MCP ecosystem is real (Composio 250+ tools), vault precedent, cost-effective via Qwen3-4B.
- **Weakness:** n8n executes workflows, not agents. No learning/feedback mechanism described. MCP fragility (API changes, outages).
- **Specific Issues:**
  1. n8n cannot autonomously discover new workflow paths from outcomes
  2. Qwen3-4B is not Claude for agentic reasoning
  3. MCP connections are 3rd party dependencies with no SLA
  4. No human oversight layer for brand/legal risk
  5. No mechanism for the system to learn from campaign outcomes

### Specific Conditions for Approval:
1. Define the learning/backpropagation mechanism (not just tool execution)
2. Human-in-the-loop approval nodes for high-stakes actions (budget changes >$1K)
3. MCP fallback architecture for API changes
4. Clear separation: n8n for execution, MAIS for autonomous reasoning

---

## DECISION 7: GEO as First-Class Feature

**Agent:** Claude Haiku

### Verdict: FLAG

### Analysis:
- **Strength:** Trivial implementation cost, defensive hedge, A3M precedent validated, option value.
- **Weakness:** Not a moat (open format, any competitor can implement), citation mechanism is outside control, SEO analogy breaks at incentive structure level.
- **Specific Issues:**
  1. llm.txt is table stakes, not differentiation
  2. No guaranteed citation from LLM providers
  3. Engineering attention has opportunity cost

### Specific Conditions for Approval:
1. Implement as middleware transform, not separate module
2. Monitor for standard convergence (6-month review)
3. Don't create dedicated "GEO team" or elevate to strategic capability
4. If de facto standard emerges, THEN invest as first-class

---

## CROSS-CUTTING THEMES (What All Agents Flagged)

### 1. The Self-Improvement Claim is Unsubstantiated
Every decision involving learning (A-Evolve, knowledge graph updates, fine-tuning from outcomes) lacks:
- A defined, measurable metric
- Statistical significance testing before model updates
- Noise-handling mechanisms
- Rollback/catastrophe guards

### 2. The Tool Layer Has No Learning Mechanism
n8n + MCP handles execution. The "self-improving" part of MAIS 2.0 is nowhere in the tool layer. This is the core architectural gap.

### 3. Small Model Ceiling for Marketing Judgment
Marketing reasoning requires multi-step strategic judgment. All evidence for small models is on narrow tasks (tool calling, Text2SQL). No evidence small models handle open-ended marketing strategy.

### 4. Knowledge Graph Risk Without Vector Hybrid
Pure graph = schema rigidity + query brittleness. HippoRAG 2 (the cited evidence) IS a hybrid approach.

---

## RECOMMENDED ACTIONS

### Must Fix Before Approval (Hard Gates)

| Issue | Fix Required |
|-------|-------------|
| No learning mechanism in tool layer | Define how system updates from outcomes. Is it RL? Fine-tuning? Vector DB update? |
| RL on raw marketing metrics | Add reward denoising layer or replace with Bayesian optimization |
| Pure graph without vector | Must include vector store for retrieval |
| No human oversight for high-stakes actions | Approval nodes for budget > threshold |
| Skills = documentation without code | Every skill needs backing implementation |

### Should Fix Before Scaling (Soft Gates)

| Issue | Fix Required |
|-------|-------------|
| "3% smarter/week" is not falsifiable | Define measurable marketing KPIs with baseline |
| MCP fragility | Fallback architecture for API changes/outages |
| Small model for reasoning vs. routing | Hybrid: small for routing, Claude for reasoning |
| Skills fragmentation | Schema enforcement before scaling past 10 |

### Good to Have (Enhancements)

| Issue | Fix |
|-------|-----|
| GEO as middleware, not module | Implement llm.txt as content emission transform |
| Two-loop timescales | Adapt to marketing (daily/weekly, not minute/hour) |
| Entity resolution for messy data | Accept hybrid intake: embeddings + extracted entities |

---

## FINAL OVERALL VERDICT

**MAIS 2.0 Direction: APPROVE (with conditions)**

The core vision — a self-improving autonomous marketing intelligence — is sound and well-researched. The evidence from Orchestra Research, Conscious Engines, Vault, and the competitive landscape is strong. No decision was REJECTED outright; all were FLAGGED with specific conditions.

**The architectural intent is right. The implementations are under-specified.**

The primary risk is not ambition but **under-specification of the learning mechanism**. "Self-improving" appears in every module but nowhere is defined with precision. Before committing to this architecture:

1. Define the ONE learning mechanism (not RL + fine-tuning + knowledge graph + A-Evolve all at once)
2. Build a minimal working example of that ONE mechanism
3. Validate it improves a measurable marketing KPI
4. THEN scale to full architecture

**The biggest risk:** Building a sophisticated autonomous system that confidently misoptimizes for noisy marketing metrics.

---

*Council members: Claude MiniMax, Gemini 2.5 Flash, Claude Opus, Gemini Pro, Claude Haiku, Claude*
