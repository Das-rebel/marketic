# marketic — Marketing Intelligence OS
## Detailed Build Plan (v1.1)

**Purpose:** Comprehensive plan for building marketic — the definitive AI-native marketing operating system.
**Status:** PLANNING PHASE
**Date:** 2026-07-02
**Version:** 1.1 — Added Performance Marketing Module + MCP Ecosystem

---

## Executive Summary

Based on deep vault research (50+ items per query across 20 queries) and agent council review, this plan defines the architecture and build sequence for **marketic** — a Marketing Intelligence OS that positions Subhajit as the premier AI-native marketing leader.

**Core Differentiator:** The marketing intelligence feedback loop — signals → competitive intel → creative generation → campaign management → analytics → signals again — implemented as an open, composable system that competitors like Icon AI CMO and Okara AI do not provide.

**Viral Hook:** "Watch marketic extract a competitor's entire ad strategy, generate 47 counter-variants, and launch a campaign — all in under 20 minutes."

---

## Part I: Vault Research Summary

### What the Vault Contains

The personal knowledge vault contains extensive marketing AI knowledge across 20 search queries with 50+ items each:

| Category | Key Items |
|----------|-----------|
| **AI Marketing Agents** | Icon AI CMO (Founders Fund-backed), Okara AI, Higgsfield Supercomputer 2.0 (NVIDIA), Cluely (24+ UGC creators) |
| **Automation Platforms** | n8n (2,589 workflows), Composio MCP (HubSpot, Salesforce, Meta, LinkedIn), Apify, Firecrawl |
| **Content Generation** | Nano Banana, Arcads, Veo 3, Pomelli (Google Labs), Postel, Weavy |
| **Competitor Intelligence** | GoMarble + Meta Ad Library, Cursor + Firecrawl, Claude + Apify MCP |
| **Vibe Marketing** | 4-level framework (prompting → workflows → vibe-coded → agent swarms), Greg Isenberg, BoringMarketer |
| **Video Automation** | Revid AI, LTX-2 (open-source), Viggle LIVE, 130M+ views from 25 accounts |
| **SEO/GEO** | Matt Diggity AI link-building, Firecrawl MCP, Cursor SEO agent |
| **Growth Patterns** | Sam Altman 100 users, Chatbase $6M ARR, Austin Huang one-person team |

### Key Insight from Vault

The marketing AI space is dominated by **black-box autonomous agents** (Icon, Okara, Higgsfield) that produce results but provide no reasoning trail. The white-space opportunity is:

> **Transparent, composable, learnable marketing intelligence** — where every AI decision is logged, explainable, and human-steered.

---

## Part Ia: Performance Marketing Coverage (NEW)

Your vault has **extensive performance marketing content** (500+ items across 20 queries):

### Coverage by Category

| Category | Vault Items | Key Tools |
|----------|-------------|-----------|
| **AI Ad Creation** | Goose Ads (Claude skill), GoMarble MCP, Nano Banana + n8n, Pomelli | 50+ items |
| **ROAS Optimization** | TACOS as north star, contribution margin > ROAS, 2.5-3x+ targets | 12 items |
| **Google Ads** | Audit checklists, PMax optimization, bidding scripts, 90-day learning curve | 50+ items |
| **Meta Ads** | Andromeda AI, seeding strategy, 3-campaign structure, creative volume | 50+ items |
| **Campaign Structure** | Full funnel (TOF/MOF/BOF), +32% from funnel implementation | 14 items |
| **E-commerce** | Shopify dashboards, D2C case studies, Lexi dashboards | 50+ items |
| **Tracking** | Enhanced conversions (+15%), server-side tracking, Lexi dashboards | 4 items |
| **MCP Ecosystem** | GoMarble, Composio, Goose Ads, Apify, Revid, n8n MCP, Firecrawl, Browser MCP | 16 queries |

### The Four Differentiators (from vault)

1. **Real-time ROAS optimization** — AI continuously adjusts bids based on ROAS performance
2. **AI-generated UGC video ads** — Generate 1000s of ad variations using Nano Banana, Arcads, Veo 3
3. **Cross-platform budget router** — AI shifts budget between Google/Meta/LinkedIn based on real-time ROAS
4. **Attribution + incrementality** — Multi-touch attribution with incrementality testing

### MCP Servers Available (11 total)

| MCP Server | Platform | Capabilities |
|------------|----------|--------------|
| GoMarble | Meta, Google | RCA, competitor intel, ad library |
| Composio | Meta, LI, HS, SF | Campaign launch |
| Goose Ads | Meta | Creative intelligence |
| Apify | TikTok, IG, Twitter | 1000+ scrapers |
| Revid | TikTok | Video creation/scheduling |
| Higgsfield | Google Ads | Creative generation |
| Firecrawl | Web | AI-ready scraping |
| n8n MCP | All 525+ nodes | Workflow automation |
| Browser MCP | Web | 30+ web tools |
| GA MCP | Google Analytics | Natural language queries |
| Goose Works | Meta | Ad trend mining |

---

## Part II: Agent Council Recommendations

### Architecture Critique

**Current 7-module structure is functional but misses critical layers:**

| Missing Layer | Recommendation |
|---------------|----------------|
| **Feedback loop** | Signals ↔ analytics must be bidirectional. Add `events/` layer. |
| **Data/warehouse** | DuckDB for signals/features. Add `data/` layer. |
| **Event bus** | Simple pub/sub or cron-driven pipeline |
| **Brand safety** | `guardrails/` layer for compliance |
| **Multi-workspace** | `projects/` concept for multi-client |

**Over-emphasized:** `vibe_marketing/` abstraction layer is premature. Focus on concrete capabilities first.

### Strategic Differentiation vs Existing Products

| Competitor | Their Weakness | marketic Advantage |
|-----------|----------------|-------------------|
| Icon AI CMO | Black box, no reasoning trail | Full audit trail on every decision |
| Okara AI | Walled garden | Open, composable via n8n/Composio |
| Higgsfield | Enterprise-only, opaque | Accessible, transparent, local-first |
| Cluely | UGC-focused only | Full-funnel: signals → creative → campaigns → analytics |

**Unique positioning:** "The marketing intelligence loop — transparent, learnable, composable"

### MVP Recommendation

**MVP Scope:** Competitive Creative Intelligence System

```
Signals (Reddit + Twitter + Trends)
    → FUSE into "buzz signal"
    → competitor_intel.py (Apify/GoMarble: pull competitor ads, landing pages)
    → creative_generator.py (given competitor weaknesses → 20+ ad variants)
    → Output: ranked variant list with reasoning
```

**Why MVP over alternatives:**
- Clear value prop in one sentence
- Data moat builds with every competitor analyzed
- Demoable in 3-minute loom
- Extends naturally to full loop

### Build vs Borrow

| Layer | Decision | Rationale |
|-------|----------|-----------|
| Signal ingestion | BUILD | Simple Python + cron, free APIs |
| Competitor intel | BORROW | GoMarble + Apify already solved |
| Creative generation | BUILD | Core differentiator |
| Campaign management | BORROW | Composio MCP for Meta/LinkedIn/Google |
| Analytics | BORROW | DuckDB + existing BI tools |
| Workflow orchestration | BORROW | n8n handles glue |
| Data storage | BUILD | DuckDB + SQLite, simple |
| Guardrails | BUILD | Brand safety = differentiator |

### Viral Factor

**The 20-minute demo is the product:**

1. `marketic analyze-competitor --brand notion`
2. System scrapes: Notion's Meta ads (90 days), LinkedIn posts, Google Ads, App Store screenshots
3. AI identifies: positioning gaps, audience overlaps, underutilized emotional triggers
4. Output: "Notion is ignoring [X]. Here's your counter-positioning."
5. Generate: 47 ad variants across 6 formats
6. Each variant tagged with: audience segment, emotional trigger, gap exploited, confidence score

**This is demoable in a GIF. It's shareable, tweetable, and answers a real pain point.**

---

## Part III: Architecture Design

### Directory Structure

```
marketic/
├── CLAUDE.md              # Developer context
├── README.md              # Public overview
├── PLAN.md                # This document
├── requirements.txt        # Dependencies
├── setup.py              # Package config
│
├── marketic/              # Main package
│   ├── __init__.py
│   │
│   ├── signals/          # Signal ingestion layer
│   │   ├── __init__.py
│   │   ├── collectors/   # Source-specific collectors
│   │   │   ├── reddit.py
│   │   │   ├── twitter.py
│   │   │   ├── trends.py
│   │   │   ├── reddit_api.py
│   │   │   └── __init__.py
│   │   ├── fusion.py     # Fuse signals into unified view
│   │   ├── signals.py    # Signal data models
│   │   └── run_pipeline.py
│   │
│   ├── data/             # Data storage layer
│   │   ├── __init__.py
│   │   ├── store.py      # DuckDB + SQLite operations
│   │   ├── schema.py     # Database schema
│   │   └── queries.py    # Common queries
│   │
│   ├── events/           # Event bus layer
│   │   ├── __init__.py
│   │   ├── bus.py        # Simple pub/sub
│   │   └── triggers.py   # Cron/event triggers
│   │
│   ├── competitive/       # Competitive intelligence (CORE MODULE)
│   │   ├── __init__.py
│   │   ├── extractor.py  # Apify/GoMarble/Meta Ad Library
│   │   ├── analyzer.py   # AI analysis of competitor data
│   │   ├── gaps.py       # Positioning gap identification
│   │   └── reports.py    # Competitor intel reports
│   │
│   ├── creative/         # Creative generation
│   │   ├── __init__.py
│   │   ├── copy.py       # Ad copy generation
│   │   ├── social.py     # Social media content
│   │   ├── seo.py        # SEO/GEO content
│   │   ├── video.py      # Video scripts
│   │   ├── variants.py    # Multi-variant generation
│   │   └── ranker.py     # Rank variants by expected performance
│   │
│   ├── campaign/         # Campaign management
│   │   ├── __init__.py
│   │   ├── builder.py     # Campaign structure
│   │   ├── launcher.py   # Launch via Composio MCP
│   │   ├── optimizer.py   # Performance optimization
│   │   └── budget.py      # Budget routing
│   │
│   ├── analytics/         # Analytics & attribution
│   │   ├── __init__.py
│   │   ├── attribution.py # Multi-touch attribution
│   │   ├── dashboards.py  # Dashboard generation
│   │   └── reports.py     # Report generation
│   │
│   ├── integrations/      # External platform integrations
│   │   ├── __init__.py
│   │   ├── composio.py    # Composio MCP wrapper
│   │   ├── apify.py       # Apify scraper wrapper
│   │   ├── meta_ads.py    # Meta Ads API
│   │   ├── linkedin.py    # LinkedIn Ads API
│   │   └── n8n.py         # n8n workflow trigger
│   │
│   ├── guardrails/        # Brand safety & compliance
│   │   ├── __init__.py
│   │   ├── content_check.py # Content policy checks
│   │   ├── brand_safety.py # Brand safety rules
│   │   └── compliance.py    # Regulatory compliance
│   │
│   └── cli/               # Command-line interface
│       ├── __init__.py
│       ├── main.py         # Main CLI entry
│       ├── analyze.py       # Competitor analysis command
│       ├── generate.py       # Creative generation command
│       └── run.py           # Pipeline run command
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_signals.py
│   ├── test_competitive.py
│   ├── test_creative.py
│   └── test_integration.py
│
└── examples/              # Example configs and scripts
    ├── config.yaml
    ├── competitor_analysis_example.py
    └── run_pipeline_example.sh
```

---

## Part IV: Build Sequence

### Phase 1: Foundation (Week 1-2)

**Goal:** Working end-to-end pipeline for competitor → creative

#### 4.1 signals/ Layer
- [ ] `signals/collectors/reddit.py` — Reddit API collector (free, no auth needed for public posts)
- [ ] `signals/collectors/twitter.py` — Twitter v2 API collector (requires API key)
- [ ] `signals/collectors/trends.py` — Google Trends RSS collector
- [ ] `signals/fusion.py` — Fuse signals into unified "buzz score" per brand/topic
- [ ] `signals/run_pipeline.py` — Cron-triggerable pipeline

#### 4.2 data/ Layer
- [ ] `data/store.py` — DuckDB + SQLite hybrid (DuckDB for analytics, SQLite for key-value)
- [ ] `data/schema.py` — Schema: raw_signals, processed_signals, competitor_intel, creative_variants
- [ ] `data/queries.py` — Pre-built queries for common analyses

#### 4.3 events/ Layer
- [ ] `events/bus.py` — Simple in-memory pub/sub
- [ ] `events/triggers.py` — Cron triggers for pipeline stages

**Deliverable:** Running `python -m marketic.signals.run_pipeline` collects and stores signals for configured keywords.

---

### Phase 2: Core Module — Competitive Intelligence (Week 3-4)

**Goal:** `marketic analyze-competitor --brand X` → competitor analysis + 20 ad variants

#### 4.4 competitive/ Layer (CORE DIFFERENTIATOR)
- [ ] `competitive/extractor.py` — Unified interface to:
  - GoMarble (Meta Ad Library API) — for active competitor ads
  - Apify Facebook/LinkedIn scrapers — for organic content
  - Direct scraping (Playwright) — for landing pages, pricing pages
- [ ] `competitive/analyzer.py` — AI analysis:
  - Extract: positioning themes, emotional triggers, audience targeting, CTA patterns
  - Use: parallel LLM analysis (qwen3:4b locally or Groq)
- [ ] `competitive/gaps.py` — Identify positioning gaps:
  - What is competitor NOT addressing?
  - What audiences are they underserving?
  - What emotional triggers are they not using?
- [ ] `competitive/reports.py` — Generate readable competitor intel reports

**Deliverable:** `python -m marketic.cli.analyze --competitor notion` produces:
- Positioning map (2x2 matrix)
- Top 5 emotional triggers used
- Top 3 gaps (opportunities)
- Audience segments being underserved

---

### Phase 3: Creative Generation (Week 5-6)

**Goal:** Given competitor gaps → 47 ad variants with reasoning

#### 4.5 creative/ Layer
- [ ] `creative/copy.py` — Ad copy generator:
  - Google Search ads (headlines, descriptions)
  - Meta Feed ads (primary text, headlines, CTAs)
  - LinkedIn Sponsored (professional copy)
- [ ] `creative/social.py` — Social content:
  - Twitter threads
  - LinkedIn posts
  - Carousel scripts
- [ ] `creative/seo.py` — SEO/GEO content:
  - Blog post outlines
  - LLM.txt generation (for GEO optimization)
- [ ] `creative/video.py` — Video scripts:
  - TikTok/short-form (hook + 3 points + CTA)
  - YouTube ads (15-sec hook + story + CTA)
- [ ] `creative/variants.py` — Generate N variants per format
- [ ] `creative/ranker.py` — Rank variants by:
  - Gap exploitation score
  - Brand fit
  - Confidence (based on LLM reasoning)

**Deliverable:** `python -m marketic.cli.generate --competitor notion --count 47` produces 47 ad variants, each tagged with:
- Format (search ad, feed ad, social post, video script)
- Gap exploited
- Emotional trigger
- Confidence score
- Human-readable rationale

---

### Phase 4: Campaign Integration (Week 7-8)

**Goal:** Launch generated variants via Composio MCP

#### 4.6 campaign/ Layer
- [ ] `campaign/launcher.py` — Composio MCP wrapper:
  - Connect Meta Ads (create campaign, create ad set, create ads)
  - Connect LinkedIn Ads
  - Connect Google Ads
- [ ] `campaign/optimizer.py` — A/B test analysis:
  - Compare variant performance
  - Suggest winning variants to scale
- [ ] `campaign/budget.py` — Budget reallocation:
  - Shift budget to winning variants
  - Reduce budget on underperformers

#### 4.7 integrations/ Layer
- [ ] `integrations/composio.py` — Composio MCP client wrapper
- [ ] `integrations/meta_ads.py` — Meta Marketing API wrapper (backup if Composio insufficient)
- [ ] `integrations/n8n.py` — n8n webhook trigger for workflow automation

**Deliverable:** `python -m marketic.cli.launch --competitor notion --budget 5000` launches top 5 variants as a Meta campaign with $5K budget.

---

### Phase 5: Analytics & Reporting (Week 9-10)

**Goal:** Full feedback loop — campaigns → analytics → signals

#### 4.8 analytics/ Layer
- [ ] `analytics/attribution.py` — Multi-touch attribution:
  - First touch
  - Last touch
  - Linear
  - Time decay
  - Position-based
- [ ] `analytics/dashboards.py` — Dashboard generation:
  - Campaign performance table
  - ROAS by creative variant
  - Cost curves
- [ ] `analytics/reports.py` — Weekly automated reports

#### 4.9 guardrails/ Layer
- [ ] `guardrails/content_check.py` — Block prohibited content categories
- [ ] `guardrails/brand_safety.py` — Brand safety rules per client
- [ ] `guardrails/compliance.py` — FTC/disclosure compliance

**Deliverable:** `python -m marketic.cli.report --weekly` produces markdown report with:
- Campaign performance summary
- Top/bottom variants
- Recommendations for next week

---

### Phase 6: Polish & Launch (Week 11-12)

- [ ] CLI polish: argparse with subcommands, config files
- [ ] Documentation: README, examples, architecture doc
- [ ] Demo video (Loom, 3 minutes)
- [ ] GitHub repo: clean commit history, proper .gitignore, LICENSE
- [ ] Optional: Publish to PyPI as `marketic` package

---

## Part V: Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Language** | Python 3.11+ | Subhajit's primary skill |
| **LLM Routing** | a3m-style custom | Parallel execution, cost optimization |
| **Local LLM** | qwen3:4b (Ollama) | Fast, cheap, reliable JSON |
| **External LLM** | Groq (llama-3.1-8b) | Free tier, fast inference |
| **Data Storage** | DuckDB + SQLite | DuckDB for analytics, SQLite for key-value |
| **Web Scraping** | Apify + Firecrawl | Pre-built, maintained, scalable |
| **Competitor Intel** | GoMarble + Meta Ad Library | Direct API, not scraping |
| **Integrations** | Composio MCP | HubSpot, Salesforce, Meta, LinkedIn |
| **Workflow** | n8n (optional) | Glue between marketic and external systems |
| **Browser** | Playwright (sota-browser style) | For JavaScript-heavy pages |
| **CLI** | argparse + click | Standard Python CLI |

---

## Part VI: Key Differentiators to Emphasize

### 1. The Feedback Loop
Every competitor analyzed feeds the creative generator. Every campaign run feeds the attribution model. Every attribution insight feeds the next competitor analysis. **This is a flywheel, not a pipeline.**

### 2. Reasoning Transparency
Icon AI CMO and Okara are black boxes. marketic logs:
- Why each competitor gap was identified
- Why each creative variant was generated
- Why each budget allocation was made
- Human can override at any point

### 3. GEO (Generative Engine Optimization)
Nobody is doing this well. Generate `llm.txt` files and answer-engine-optimized content for Perplexity, ChatGPT, and Gemini. First-mover advantage.

### 4. Open Composability
- n8n workflow templates that use marketic
- Composio MCP for HubSpot/Salesforce/Meta/LinkedIn
- CLI-first design (pipe marketic output anywhere)
- No lock-in: export everything as JSON

---

## Part VII: Risk Factors

| Risk | Mitigation |
|------|------------|
| Meta/LinkedIn API rate limits | Use GoMarble for Meta (official API partner), cache aggressively |
| LLM cost at scale | Use qwen3:4b locally via Ollama for generation; only use paid APIs for analysis |
| Competitor legal risk | Only use public data; don't store proprietary ad creative |
| Guardrails failures | Human-in-the-loop by default; auto-launch requires explicit flag |
| Vault API downtime | Cache vault queries; fallback to local data |

---

## Part VIII: Success Metrics

| Metric | Target |
|--------|--------|
| GitHub stars (30 days) | 100+ |
| Demo video views | 1,000+ |
| Competitor analyses done | 50+ unique brands |
| Creative variants generated | 10,000+ |
| CLI usability score | <5 min to first competitor analysis |
| Test coverage | 80%+ on core modules |

---

## Appendix: File Inventory

```
marketic/
├── CLAUDE.md                           # Developer context (exists)
├── README.md                           # Public overview (exists)
├── PLAN.md                             # This plan (to write)
├── requirements.txt                    # Dependencies (to finalize)
├── setup.py                            # Package (to finalize)
│
├── marketic/                           # Package
│   ├── __init__.py                    # (exists)
│   │
│   ├── signals/                        # NEW - 6 files
│   │   ├── __init__.py
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── reddit.py
│   │   │   ├── twitter.py
│   │   │   └── trends.py
│   │   ├── fusion.py
│   │   ├── signals.py
│   │   └── run_pipeline.py
│   │
│   ├── data/                           # NEW - 3 files
│   │   ├── __init__.py
│   │   ├── store.py
│   │   └── schema.py
│   │
│   ├── events/                         # NEW - 2 files
│   │   ├── __init__.py
│   │   └── bus.py
│   │
│   ├── competitive/                    # NEW - 5 files (CORE)
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── analyzer.py
│   │   ├── gaps.py
│   │   └── reports.py
│   │
│   ├── creative/                       # NEW - 7 files
│   │   ├── __init__.py
│   │   ├── copy.py
│   │   ├── social.py
│   │   ├── seo.py
│   │   ├── video.py
│   │   ├── variants.py
│   │   └── ranker.py
│   │
│   ├── campaign/                       # NEW - 4 files
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   ├── launcher.py
│   │   └── optimizer.py
│   │
│   ├── analytics/                     # EXISTING (needs cleanup)
│   │   ├── __init__.py
│   │   ├── attribution.py
│   │   ├── dashboards.py
│   │   └── reports.py
│   │
│   ├── integrations/                  # NEW - 5 files
│   │   ├── __init__.py
│   │   ├── composio.py
│   │   ├── apify.py
│   │   ├── meta_ads.py
│   │   └── n8n.py
│   │
│   ├── guardrails/                    # NEW - 3 files
│   │   ├── __init__.py
│   │   ├── content_check.py
│   │   └── brand_safety.py
│   │
│   └── cli/                            # NEW - 4 files
│       ├── __init__.py
│       ├── main.py
│       ├── analyze.py
│       └── generate.py
│
├── tests/                              # NEW - 5 files
│   ├── __init__.py
│   ├── test_signals.py
│   ├── test_competitive.py
│   ├── test_creative.py
│   └── test_integration.py
│
└── examples/                          # NEW - 3 files
    ├── config.yaml
    ├── competitor_analysis_example.py
    └── run_pipeline_example.sh
```

**Total new files to create:** ~45
**Existing files to reuse/cleanup:** ~10
**Estimated build time:** 12 weeks (full-time) / 24 weeks (part-time)

---

## Part VIII: Performance Marketing Module

**Core differentiator: The closed loop that makes marketic an OS, not just a tool.**

### The Feedback Loop

```
signals/ → competitive/ → creative/ → variants/
                                      ↓
                            campaign/launcher/
                                      ↓
                        ┌───────────┴───────────┐
                        ↓                       ↓
                  performance/              analytics/
                  (THE CLOSED LOOP)         (reporting)
                        ↓                       ↓
                  bid_optimization          dashboards
                        ↓                       ↓
                  budget_router            reports
                        ↓                       ↓
                  ab_tester ←───────────── attribution
                        ↓
                  ROAS_tracker
                        ↓
                  funnel_analyzer
```

### Performance Module Structure

```
marketic/performance/           # ROAS in real-time, AI bid optimization
├── roas_tracker.py           # Track ROAS across campaigns/platforms
├── bid_optimizer.py          # AI-powered bid adjustments
├── budget_router.py          # Cross-platform budget routing
├── ab_tester.py            # Automated A/B test analysis
├── funnel_analyzer.py      # TOF/MOF/BOF analysis
├── attribution.py           # Multi-touch attribution models
├── incrementality.py        # Holdout-based incrementality testing
└── dash.py                 # Performance dashboard generator

marketic/video_ads/          # AI-generated UGC video ads
├── script_gen.py            # Generate video ad scripts
├── voiceover.py             # ElevenLabs integration
├── platform_adapter.py      # Adapt for TikTok/IG/YT
└── batch.py                 # Generate 100s of variants

marketic/ecommerce/          # E-commerce specific
├── storefront_tracker.py    # Shopify/WooCommerce
├── product_feed.py          # Google Shopping / Meta Catalog
└── competitor_price.py     # Price intelligence

marketic/tracking/            # Server-side tracking
├── server_side.py           # GTM server-side
├── enhanced_conv.py         # Enhanced conversions API (+15% lift)
└── offline_conv.py          # Offline conversion uploads
```

### The Four Differentiators

| Differentiator | Vault Source | Implementation |
|---------------|--------------|----------------|
| **Real-time ROAS optimization** | "Low ROAS bids don't always yield low ROAS - let algorithm optimize, start small" | AI adjusts bids based on ROAS, respects 90-day learning phase |
| **AI-generated UGC video ads** | Nano Banana + n8n → "1000+ ad variations in minutes" | Goose Ads → Nano Banana → Arcads pipeline |
| **Cross-platform budget router** | Full funnel (TOF/MOF/BOF), "+32% sales increase" | AI shifts budget between Google/Meta/LI based on ROAS |
| **Attribution + incrementality** | "Enhanced conversions → +15% increase" | Multi-touch models + holdout testing |

---

## Part IX: MCP Ecosystem (11 MCP Servers)

**Vault source: 16 queries, comprehensive MCP coverage**

### MCP Integration Architecture

```
marketic/mcp/                          # NEW - MCP client layer
├── client.py                         # Unified MCP client wrapper
├── registry.py                        # MCP server registry
├── servers/                          # MCP server integrations
│   ├── gomarble.py                  # Meta/Google Ads + RCA
│   ├── composio.py                   # HubSpot/SF/Meta/LI
│   ├── goose_ads.py                  # Meta creative intel
│   ├── apify.py                      # 1000+ scrapers
│   ├── revid.py                      # TikTok video
│   ├── firecrawl.py                 # AI-ready web scraping
│   ├── browser_mcp.py                # Web access
│   ├── google_analytics.py            # Natural language GA queries
│   └── n8n_mcp.py                   # 525+ workflow nodes
└── orchestrator.py                   # Orchestrate multiple MCPs
```

### MCP Registry

```python
MCP_REGISTRY = {
    "gomarble": {
        "platform": "meta_ads",
        "capabilities": ["competitor_creative_intel", "rca_performance_drops",
                         "weekly_client_reports", "ad_library_search"],
        "auth": "api_key",
        "vault": "GoMarble + Meta Ad Library = 4 min competitor intel",
    },
    "composio": {
        "platform": "multi",
        "capabilities": ["meta_ads", "linkedin_ads", "hubspot_crm",
                         "salesforce_crm", "google_ads"],
        "auth": "oauth",
        "vault": "Marketing Skills v1.4.0 - Composio integration",
    },
    "goose_ads": {
        "platform": "meta",
        "capabilities": ["competitor_ad_finder", "converting_angle_mining", "ad_creation"],
        "auth": "api_key",
        "vault": "Goose Ads MCP - finds trending ads, mines converting angles",
    },
    "apify": {
        "platform": "scraping",
        "capabilities": ["tiktok_data", "instagram_data", "twitter_scraping",
                         "competitor_pricing", "product_data"],
        "auth": "api_key",
        "vault": "Apify MCP - 1000+ pre-built scrapers",
    },
    "revid_ai": {
        "platform": "tiktok",
        "capabilities": ["video_creation", "video_scheduling", "video_publishing"],
        "auth": "api_key",
        "vault": "Revid_ai MCP - TikTok create/schedule/publish",
    },
    "higgsfield": {
        "platform": "google_ads",
        "capabilities": ["creative_generation", "ad_variants", "copy_testing"],
        "auth": "api_key",
        "vault": "Higgsfield MCP - Google Ads creative generation",
    },
    "firecrawl": {
        "platform": "scraping",
        "capabilities": ["web_crawl", "sitemap_extract", "ai_ready_output"],
        "auth": "api_key",
        "vault": "Firecrawl MCP - search + scrape web",
    },
    "n8n_mcp": {
        "platform": "workflow",
        "capabilities": ["all_525_nodes", "workflow_creation", "automation_trigger"],
        "auth": "self_hosted",
        "vault": "n8n MCP - Claude knows all 525+ n8n nodes",
    },
}
```

---

## Part X: Agent Layer (6 Agents)

**Vault source: Icon AI CMO, Okara AI, Higgsfield, Helena, Cluely, Hermes, Overlap**

```
marketic/agents/                       # NEW - Autonomous agents
├── ad_creative_agent.py              # Generate + optimize ad creatives
├── competitor_research_agent.py       # Full competitor intelligence
├── campaign_optimizer_agent.py        # ROAS/bid optimization
├── content_pipeline_agent.py          # End-to-end content workflow
├── reporting_agent.py                 # Weekly/monthly reports
└── multi_platform_agent.py            # Orchestrate all platforms
```

### Agent Capabilities

| Agent | Vault Reference | Inputs | Outputs |
|-------|-----------------|--------|---------|
| **AdCreativeAgent** | Goose Ads + Nano Banana + Arcads | Competitor intel, brand kit | 100s of ad variants |
| **CompetitorResearchAgent** | GoMarble + Meta Ad Library + Apify | Competitor brand/URL | Positioning map, gaps, counter-strategy |
| **CampaignOptimizerAgent** | Lexi dashboard, GoMarble RCA | Campaign IDs, target ROAS | Bid adjustments, budget reallocations |
| **ContentPipelineAgent** | n8n workflow | Product URL | Multi-platform content |
| **ReportingAgent** | GoMarble weekly reports | Account data | Markdown/HTML reports |
| **MultiPlatformAgent** | Composio | Brief | Campaigns on all platforms |

---

## Part XI: Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MARKETIC OS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    MCP LAYER (11 MCPs)                           │   │
│  ├─────────────┬─────────────┬─────────────┬──────────────────────┤   │
│  │  GoMarble   │  Composio   │  Goose Ads │  Apify               │   │
│  │  Meta/Google│  Meta/LI/HS │  Meta      │  TikTok/IG/Twitter   │   │
│  ├─────────────┼─────────────┼─────────────┼──────────────────────┤   │
│  │  Revid_ai  │  Higgsfield │  Firecrawl │  Browser MCP         │   │
│  │  TikTok    │  Google Ads │  Web crawl │  30+ web tools       │   │
│  ├─────────────┼─────────────┼─────────────┼──────────────────────┤   │
│  │  n8n MCP   │  GA MCP     │            │                      │   │
│  │  525+ nodes│  Analytics  │            │                      │   │
│  └─────────────┴─────────────┴─────────────┴──────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AGENT LAYER (6 Agents)                       │   │
│  ├───────────────┬───────────────┬───────────────┬─────────────────┤   │
│  │Ad Creative     │Competitor     │Campaign       │Content          │   │
│  │Agent          │Research Agent │Optimizer Agent│Pipeline Agent   │   │
│  ├───────────────┼───────────────┼───────────────┼─────────────────┤   │
│  │Reporting     │Multi-Platform │              │                 │   │
│  │Agent        │Agent          │              │                 │   │
│  └───────────────┴───────────────┴───────────────┴─────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   CORE MODULES (12 modules)                      │   │
│  ├──────────┬──────────┬──────────┬──────────┬───────────────────┤   │
│  │ signals/ │competitive│ creative/│ campaign/│ analytics/        │   │
│  │          │/         │          │          │                   │   │
│  ├──────────┼──────────┼──────────┼──────────┼───────────────────┤   │
│  │performance│video_ads │ ecommerce│ tracking │ guardrails/       │   │
│  │          │          │          │          │                   │   │
│  └──────────┴──────────┴──────────┴──────────┴───────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FOUNDATION LAYER                             │   │
│  │  LLM Router (a3m) │ Memory (DuckDB) │ Orchestration │ Alerts   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part XII: Complete File Inventory

```
marketic/
├── CLAUDE.md                           # Developer context
├── README.md                           # Public overview
├── PLAN.md                             # This plan
├── PERFORMANCE_MODULE_PLAN.md           # Performance marketing detail
├── PERFORMANCE_MCP_PLAN.md             # MCP ecosystem detail
├── requirements.txt                    # Dependencies
├── setup.py                            # Package config
│
├── marketic/                          # Main package
│   ├── __init__.py
│   │
│   ├── signals/                       # 6 files - Signal ingestion
│   │   ├── collectors/ (reddit, twitter, trends)
│   │   ├── fusion.py
│   │   └── run_pipeline.py
│   │
│   ├── data/                          # 3 files - DuckDB storage
│   │   ├── store.py
│   │   └── schema.py
│   │
│   ├── events/                        # 2 files - Event bus
│   │   └── bus.py
│   │
│   ├── competitive/                    # 5 files - CORE competitor intel
│   │   ├── extractor.py
│   │   ├── analyzer.py
│   │   ├── gaps.py
│   │   └── reports.py
│   │
│   ├── creative/                      # 7 files - Creative generation
│   │   ├── copy.py
│   │   ├── social.py
│   │   ├── seo.py
│   │   ├── video.py
│   │   ├── variants.py
│   │   └── ranker.py
│   │
│   ├── campaign/                      # 4 files - Campaign management
│   │   ├── builder.py
│   │   ├── launcher.py
│   │   └── optimizer.py
│   │
│   ├── analytics/                     # 4 files - Attribution & reporting
│   │   ├── attribution.py
│   │   ├── dashboards.py
│   │   └── reports.py
│   │
│   ├── performance/                   # 8 files - THE CLOSED LOOP
│   │   ├── roas_tracker.py
│   │   ├── bid_optimizer.py
│   │   ├── budget_router.py
│   │   ├── ab_tester.py
│   │   ├── funnel_analyzer.py
│   │   ├── attribution.py
│   │   ├── incrementality.py
│   │   └── dash.py
│   │
│   ├── video_ads/                    # 4 files - AI video ads
│   │   ├── script_gen.py
│   │   ├── voiceover.py
│   │   ├── platform_adapter.py
│   │   └── batch.py
│   │
│   ├── ecommerce/                    # 3 files - E-commerce
│   │   ├── storefront_tracker.py
│   │   ├── product_feed.py
│   │   └── competitor_price.py
│   │
│   ├── tracking/                      # 3 files - Server-side tracking
│   │   ├── server_side.py
│   │   ├── enhanced_conv.py
│   │   └── offline_conv.py
│   │
│   ├── mcp/                          # 11 files - MCP client layer
│   │   ├── client.py
│   │   ├── registry.py
│   │   └── servers/ (gomarble, composio, goose_ads, apify, revid,
│   │                 firecrawl, browser_mcp, google_analytics, n8n_mcp)
│   │
│   ├── agents/                       # 6 files - Autonomous agents
│   │   ├── ad_creative_agent.py
│   │   ├── competitor_research_agent.py
│   │   ├── campaign_optimizer_agent.py
│   │   ├── content_pipeline_agent.py
│   │   ├── reporting_agent.py
│   │   └── multi_platform_agent.py
│   │
│   ├── integrations/                  # 5 files - External integrations
│   │   ├── composio.py
│   │   ├── apify.py
│   │   ├── meta_ads.py
│   │   └── n8n.py
│   │
│   ├── guardrails/                   # 3 files - Brand safety
│   │   ├── content_check.py
│   │   └── brand_safety.py
│   │
│   └── cli/                           # 4 files - CLI
│       ├── main.py
│       ├── analyze.py
│       └── generate.py
│
├── tests/                             # 5 files - Test suite
│   ├── test_signals.py
│   ├── test_competitive.py
│   ├── test_creative.py
│   └── test_integration.py
│
└── examples/                         # 3 files - Example configs
    ├── config.yaml
    ├── competitor_analysis_example.py
    └── run_pipeline_example.sh
```

**Total files: ~80**
**Build time: 24 weeks (part-time) / 12 weeks (full-time)**

---

## Part XIII: Critical Gaps Identified by Agent Council

**Agent Council Review Date:** 2026-07-02
**Gaps Found:** 11 missing categories identified through vault research and council review

---

### Critical Missing Modules (11 categories)

| Priority | Missing Module | Why It Matters | Vault Reference |
|----------|---------------|----------------|-----------------|
| **P0** | Email Marketing | D2C/SaaS email is 30-40% of revenue | "D2C tech stack: Email: Klaviyo" |
| **P0** | Landing Pages | Can't capture leads being generated | "high-quality landing pages with Lovable + 21stdev" |
| **P1** | A/B Testing | 47 variants generated but no validation framework | Optimizely/VWO absent |
| **P1** | SMS/WhatsApp | Post-purchase, abandoned cart, re-engagement | Twilio, WhatsApp Business API |
| **P1** | Push Notifications | Retention channel completely absent | OneSignal, Pushwoosh |
| **P1** | CRM Depth | Full lead scoring, nurturing, pipeline management | JoeCRM, full HubSpot/SF |
| **P2** | Customer Data Platform (CDP) | Unify signals across email + ads + web + CRM | Segment, Rudderstack |
| **P2** | Affiliate/Partnership | Independent revenue channel | Impact, Refersion, ShareASale |
| **P2** | Influencer Marketing | Discovery, outreach, tracking, ROI | Lightreel (150K+ TikTok UGC videos) |
| **P2** | Content Distribution | Medium, Substack, guest posting, PR | Content syndication absent |
| **P2** | Collaboration | Multi-user, client portals, approval workflows | No team workflows |

---

## Part XIV: Missing Module Specifications

### 1. Email Marketing Module

**Vault References:**
- "D2C tech stack: Email: Klaviyo"
- "Sendwave - email marketing campaign dashboard"
- "Reacher - email existence checker (GitHub: reacherhq/check-if-email-exists)"
- "Enhanced conversions → up to 15% increase in registered conversions"

**Module Structure:**
```
marketic/email/
├── __init__.py
├── klaviyo_client.py        # Klaviyo email marketing API
├── sendgrid_client.py        # SendGrid transactional + marketing
├── mailchimp_client.py       # Mailchimp integration
├── sender.py                 # Send emails (transactional + campaigns)
├── verifier.py               # Email validation (Reacher-style)
├── templates.py              # Email template management
├── sequences.py              # Drip/automation sequences
├── segment_sync.py           # Sync segments from CDP
├── analytics.py              # Email performance (open, click, conversion)
└── cli.py                   # CLI: send, schedule, report
```

**Capabilities:**
- Create/send email campaigns
- Build drip sequences (welcome, nurture, onboarding, cart abandonment)
- Segment sync with CRM/CDP
- A/B test subject lines, copy, send times
- Personalization tokens
- Deliverability monitoring
- Analytics: open rate, click rate, conversion rate, revenue attributed

**CLI:**
```bash
marketic email send --campaign "welcome" --list leads.csv
marketic email sequence create --trigger cart_abandon --delay 1h
marketic email verify --file emails.csv
marketic email report --date-range 30d
```

---

### 2. Landing Page Module

**Vault References:**
- "high-quality landing pages with Lovable + 21stdev"
- "Replo - product page buy box builder"
- "Unicorn Platform - easy directory builder"
- "Figma landing page templates"

**Module Structure:**
```
marketic/landing/
├── __init__.py
├── page_builder.py            # AI landing page generation (Lovable-style)
├── templates.py               # Template library
├── ab_test_manager.py         # A/B test management for pages
├── lead_capture.py            # Form generation, lead capture
├── cta_generator.py           # Call-to-action optimization
├── page_analytics.py          # Page-level analytics (heatmaps, scroll)
├── seo_checker.py             # On-page SEO validation
├── mobile_checker.py          # Mobile responsiveness check
├── load_speed.py              # Page speed optimization
├── screenshot.py              # Screenshot comparison
└── cli.py                    # CLI: generate, test, publish
```

**Capabilities:**
- Generate landing pages from product URL or description
- A/B test multiple variants (headline, CTA, images, copy)
- Lead capture form generation
- Mobile responsiveness validation
- On-page SEO checker
- Page speed optimization
- Screenshot comparison for visual regression

**CLI:**
```bash
marketic landing generate --product-url https://notion.so
marketic landing ab-test create --url https://landing.com --variants 4
marketic landing seo-check --url https://landing.com
marketic landing publish --page-id page_123 --destination https://pages.company.com
```

---

### 3. A/B Testing Module

**Vault References:**
- No lean A/B testing framework found
- Optimizely, VWO absent
- "47 variants generated but no validation framework"

**Module Structure:**
```
marketic/ab_test/
├── __init__.py
├── experiment_design.py        # Design A/B tests (sample size, duration)
├── splitter.py                 # Traffic splitter (cookie-based, server-side)
├── statistical_engine.py       # Statistical significance calculator
├── multi_arm_bandit.py        # Multi-armed bandit optimizer
├── results_analyzer.py        # Analyze results (conversion lift, p-value)
├── sequential_testing.py       # Sequential testing for early stopping
├── report_generator.py         # Generate test reports
├── winner_selector.py          # Select winner with confidence
└── cli.py                    # CLI: create, monitor, declare winner
```

**Capabilities:**
- Design experiments with proper sample size calculation
- Traffic splitting (cookie-based, server-side, feature flags)
- Multi-armed bandit auto-optimization
- Statistical significance calculation (frequentist + Bayesian)
- Sequential testing for early stopping
- Winner declaration with confidence intervals
- Integration with Meta/Google Ads for ad testing

**CLI:**
```bash
marketic ab create --name "CTA test" --variants "Buy Now,Get Started" --metric conversion
marketic ab monitor --experiment-id exp_123
marketic ab results --experiment-id exp_123
marketic ab winner --experiment-id exp_123 --confidence 95
```

---

### 4. SMS/WhatsApp Module

**Vault References:**
- "SMS for post-purchase, abandoned cart, re-engagement"
- "WhatsApp Business API"
- Twilio mentioned in n8n context

**Module Structure:**
```
marketic/sms/
├── __init__.py
├── twilio_client.py           # Twilio SMS integration
├── whatsapp_client.py          # WhatsApp Business API
├── message_templates.py        # Pre-approved message templates
├── opt_in_manager.py           # SMS consent/DTC management
├── campaign_sender.py          # Send SMS campaigns
├── drip_sequences.py           # SMS drip sequences
├── analytics.py               # SMS performance analytics
├── phone_verifier.py          # Validate phone numbers
├── scrubber.py                # Scrub against DNC/state registries
└── cli.py                    # CLI: send, schedule, report
```

**Capabilities:**
- Send SMS via Twilio
- Send WhatsApp via WhatsApp Business API
- Pre-approved message templates
- DTC (Direct to Consumer) compliance
- SMS drip sequences (abandoned cart, post-purchase, win-back)
- Phone number validation
- DNC scrubbing
- Performance analytics (delivery, click, conversion)

**CLI:**
```bash
marketic sms send --template cart_abandon --phone +1234567890
marketic sms campaign create --name "Win-back Q3" --segment lapsed_90d
marketic sms verify --phone +1234567890
marketic sms report --date-range 7d
```

---

### 5. Push Notifications Module

**Module Structure:**
```
marketic/push/
├── __init__.py
├── onesignal_client.py        # OneSignal integration
├── pushwoosh_client.py        # Pushwoosh integration
├── firebase_client.py          # Firebase Cloud Messaging
├── segment_sync.py            # Sync segments from CDP
├── campaign_sender.py          # Send push campaigns
├── drip_sequences.py          # Push notification sequences
├── analytics.py               # Push performance analytics
└── cli.py                    # CLI: send, schedule, report
```

**Capabilities:**
- Send push notifications via OneSignal/Pushwoosh/FCM
- Web + iOS + Android support
- Segmentation sync
- Drip sequences
- Analytics (delivery, open rate, conversion)

---

### 6. CRM Deep Module

**Vault References:**
- "JoeCRM - AI-first CRM with signal reception + outreach drafts"
- Composio covers HubSpot/Salesforce but shallowly

**Module Structure:**
```
marketic/crm/
├── __init__.py
├── hubspot_client.py          # HubSpot CRM deep integration
├── salesforce_client.py       # Salesforce CRM deep integration
├── lead_scoring.py            # AI-powered lead scoring
├── lead_routing.py            # Automatic lead routing
├── nurture_engine.py           # Lead nurturing automation
├── pipeline_manager.py         # Deal/pipeline management
├── activity_tracker.py        # Track all touchpoints
├── contact_enricher.py        # Enrich contacts with data
├── task_automation.py          # Auto-create tasks from signals
└── cli.py                    # CLI: score, route, nurture, report
```

**Capabilities:**
- Deep HubSpot/Salesforce integration
- AI lead scoring (based on engagement signals)
- Automatic lead routing by territory/team/skill
- Nurture engine with personalized cadences
- Activity tracking (calls, emails, meetings, web visits)
- Contact enrichment
- Task automation

**CLI:**
```bash
marketic crm score-leads --segment mql
marketic crm route --lead-id lead_123 --strategy round_robin
marketic crm enrich --file contacts.csv
marketic crm nurture start --lead-id lead_123 --sequence enterprise_outreach
```

---

### 7. Customer Data Platform (CDP) Module

**Module Structure:**
```
marketic/cdp/
├── __init__.py
├── unified_profile.py          # Single customer view
├── identity_resolution.py       # Cross-device identity linking
├── event_tracker.py            # Track customer events
├── audience_builder.py          # Build segments from events
├── data_enricher.py            # Enrich with external data
├── export_manager.py           # Export to downstream tools
├── privacy_compliance.py       # GDPR/CCPA compliance
├── lifetime_value.py           # LTV calculation
└── cli.py                    # CLI: segments, exports, reports
```

**Capabilities:**
- Unified customer profile (all touchpoints)
- Identity resolution (cross-device, cross-channel)
- Event tracking (web, mobile, email, ads, CRM)
- Audience/segment builder
- Export to Klaviyo, HubSpot, Meta, Google
- GDPR/CCPA compliance (consent management, data deletion)
- LTV calculation per customer

---

### 8. Affiliate/Partnership Module

**Module Structure:**
```
marketic/affiliate/
├── __init__.py
├── impact_client.py            # Impact.com integration
├── shareasale_client.py        # ShareASale integration
├── affiliate_discovery.py       # Find new affiliates
├── commission_calculator.py     # Calculate commissions
├── fraud_detector.py           # Detect affiliate fraud
├── payout_manager.py           # Manage affiliate payouts
├── performance_tracker.py      # Track affiliate performance
└── cli.py                    # CLI: manage affiliates, track, pay
```

---

### 9. Influencer Marketing Module

**Vault References:**
- "Lightreel - analyses 150K+ TikTok UGC videos for marketing insights (60M views achieved)"
- No dedicated influencer tool found

**Module Structure:**
```
marketic/influencer/
├── __init__.py
├── discovery.py                # Find influencers by niche/platform
├── profile_analyzer.py          # Analyze influencer profiles
├── reach_estimator.py           # Estimate reach and engagement
├── outreach_automation.py       # Automated outreach sequences
├── contract_generator.py        # Generate influencer contracts
├── content_approval.py          # Content approval workflow
├── performance_tracker.py       # Track influencer ROI
├── ugc_rights_manager.py        # Manage UGC rights
└── cli.py                    # CLI: discover, outreach, track
```

**Capabilities:**
- Discover influencers by niche, follower count, engagement rate
- Profile analysis (followers, engagement, audience demographics)
- Automated outreach sequences
- Contract generation
- Content approval workflow
- Performance tracking (views, clicks, conversions, revenue)
- UGC rights management

---

### 10. Content Distribution Module

**Module Structure:**
```
marketic/distribution/
├── __init__.py
├── medium_client.py            # Medium publishing API
├── substack_client.py           # Substack integration
├── guest_post_manager.py        # Guest posting tracker
├── pr_wire.py                  # PR wire service integration
├── syndication_manager.py      # Cross-post content
├── social_scheduler.py         # Schedule to social platforms
└── cli.py                    # CLI: distribute, track
```

---

### 11. Collaboration Module

**Module Structure:**
```
marketic/collaboration/
├── __init__.py
├── approval_workflow.py         # Creative approval workflows
├── client_portal.py            # Client-facing dashboard
├── team_management.py          # Multi-user/team management
├── role_permissions.py         # RBAC for team members
├── comment_system.py            # Comments on creatives/campaigns
├── notification_center.py       # In-app notifications
├── activity_feed.py             # Activity feed for team
└── cli.py                    # CLI: invite, assign, approve
```

---

## Part XV: Critical Gap #1 — Revenue/Margin Tracking

**Agent Council's #1 Finding:** The plan tracks ROAS but not **contribution margin**.

> "Performance marketing is 100% about margin, not just ROAS. ROAS doesn't tell you profitability."

### Revenue Module

```
marketic/revenue/
├── __init__.py
├── margin_calculator.py        # Calculate contribution margin per product/order
├── pnl_tracker.py              # P&L per campaign/ad set
├── blended_roas.py             # Calculate blended ROAS across campaigns
├── tacos_calculator.py         # TACOS (Total Advertising Cost of Sales)
├── ltv_analyzer.py             # Customer lifetime value analysis
├── roas_vs_margin.py           # ROAS vs Margin comparison
├── attribution_revenue.py      # Revenue attribution to channels
└── cli.py                    # CLI: margin, pnl, ltv
```

**Key Metrics:**
| Metric | Formula | Why It Matters |
|--------|---------|----------------|
| **Contribution Margin** | Revenue - COGS - Ad Spend | True profitability |
| **TACOS** | Ad Spend / Total Revenue | "North star" per vault |
| **Blended ROAS** | Total Revenue / Total Ad Spend | Aggregate performance |
| **LTV** | Avg Order Value × Purchase Frequency × Churn | Customer value |
| **LTV:CAC** | Lifetime Value / Customer Acquisition Cost | Business sustainability |

---

## Part XVI: Critical Gap #2 — Retention Loop

**The plan is 100% acquisition. Zero retention.**

### Retention Module

```
marketic/retention/
├── __init__.py
├── churn_predictor.py          # Predict customer churn
├── win_back_campaigns.py        # Automated win-back sequences
├── loyalty_program.py           # Points/rewards program management
├── upsell_engine.py            # Cross-sell/upsell automation
├── nps_tracker.py              # Track NPS and feedback
├── reactivation.py             # Re-engage lapsed customers
└── cli.py                    # CLI: predict, automate, track
```

---

## Part XVII: Complete Architecture (Updated with All Gaps Fixed)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MARKETIC OS - COMPLETE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    MCP LAYER (11 MCPs)                           │   │
│  │  GoMarble │ Composio │ Goose Ads │ Apify │ Revid │ Higgsfield│   │
│  │  Firecrawl │ Browser MCP │ GA MCP │ n8n MCP                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AGENT LAYER (6 Agents)                        │   │
│  │  AdCreative │ Competitor │ CampaignOptimizer │ ContentPipeline   │   │
│  │  Reporting │ MultiPlatform                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   CORE MODULES (20 modules)                      │   │
│  │                                                                  │   │
│  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐           │   │
│  │  │ signals │ │competitive│ │creative│ │ campaign │           │   │
│  │  └─────────┘ └──────────┘ └────────┘ └──────────┘           │   │
│  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐           │   │
│  │  │analytics│ │performance│ │video   │ │ ecommerce│           │   │
│  │  │         │ │          │ │_ads    │ │          │           │   │
│  │  └─────────┘ └──────────┘ └────────┘ └──────────┘           │   │
│  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐           │   │
│  │  │tracking │ │ guardrails│ │ mcp    │ │ agents   │           │   │
│  │  └─────────┘ └──────────┘ └────────┘ └──────────┘           │   │
│  │                                                                  │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │              NEW: GAPS IDENTIFIED (11 modules)           │   │   │
│  │  │  email │ landing │ ab_test │ sms │ push │ crm │ cdp │   │   │
│  │  │  affiliate │ influencer │ distribution │ collaboration     │   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  │                                                                  │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │              CRITICAL: NEW SECTIONS                     │   │   │
│  │  │  revenue (margin/P&L/TACOS/LTV) │ retention (churn/winback)│   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FOUNDATION LAYER                              │   │
│  │  LLM Router (a3m) │ Memory (DuckDB) │ Orchestration │ Alerts │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part XVIII: Complete File Inventory (Final)

```
marketic/
├── CLAUDE.md                           # Developer context
├── README.md                           # Public overview
├── PLAN.md                             # This plan (with gaps fixed)
├── PERFORMANCE_MODULE_PLAN.md         # Performance marketing detail
├── PERFORMANCE_MCP_PLAN.md            # MCP ecosystem detail
├── requirements.txt                    # Dependencies
├── setup.py                           # Package config
│
├── marketic/                         # Main package
│   ├── __init__.py
│   │
│   ├── signals/                       # 6 files
│   │   └── collectors/ (reddit, twitter, trends)
│   │
│   ├── data/                          # 3 files
│   │   └── store.py, schema.py
│   │
│   ├── events/                        # 2 files
│   │   └── bus.py
│   │
│   ├── competitive/                   # 5 files (CORE)
│   │   └── extractor, analyzer, gaps, reports
│   │
│   ├── creative/                     # 7 files
│   │   └── copy, social, seo, video, variants, ranker
│   │
│   ├── campaign/                      # 4 files
│   │   └── builder, launcher, optimizer
│   │
│   ├── analytics/                    # 4 files
│   │   └── attribution, dashboards, reports
│   │
│   ├── performance/                  # 8 files
│   │   └── roas_tracker, bid_optimizer, budget_router,
│   │       ab_tester, funnel_analyzer, attribution,
│   │       incrementality, dash
│   │
│   ├── video_ads/                   # 4 files
│   │   └── script_gen, voiceover, platform_adapter, batch
│   │
│   ├── ecommerce/                    # 3 files
│   │   └── storefront_tracker, product_feed, competitor_price
│   │
│   ├── tracking/                    # 3 files
│   │   └── server_side, enhanced_conv, offline_conv
│   │
│   ├── mcp/                         # 11 files
│   │   └── client, registry, servers/ (9 servers)
│   │
│   ├── agents/                      # 6 files
│   │   └── ad_creative, competitor_research,
│   │       campaign_optimizer, content_pipeline,
│   │       reporting, multi_platform
│   │
│   ├── integrations/                 # 5 files
│   │   └── composio, apify, meta_ads, n8n
│   │
│   ├── guardrails/                 # 3 files
│   │   └── content_check, brand_safety
│   │
│   ├── cli/                         # 4 files
│   │   └── main, analyze, generate
│   │
│   │   NEW MODULES FROM GAPS:
│   │
│   ├── email/                       # 10 files (NEW - P0)
│   │   └── klaviyo_client, sendgrid_client,
│   │       sender, verifier, templates, sequences,
│   │       segment_sync, analytics, cli
│   │
│   ├── landing/                     # 10 files (NEW - P0)
│   │   └── page_builder, templates, ab_test_manager,
│   │       lead_capture, cta_generator, page_analytics,
│   │       seo_checker, mobile_checker, load_speed, cli
│   │
│   ├── ab_test/                     # 9 files (NEW - P1)
│   │   └── experiment_design, splitter, statistical_engine,
│   │       multi_arm_bandit, results_analyzer,
│   │       sequential_testing, report_generator,
│   │       winner_selector, cli
│   │
│   ├── sms/                         # 10 files (NEW - P1)
│   │   └── twilio_client, whatsapp_client,
│   │       message_templates, opt_in_manager,
│   │       campaign_sender, drip_sequences, analytics,
│   │       phone_verifier, scrubber, cli
│   │
│   ├── push/                        # 8 files (NEW - P1)
│   │   └── onesignal_client, pushwoosh_client,
│   │       firebase_client, segment_sync,
│   │       campaign_sender, drip_sequences, analytics, cli
│   │
│   ├── crm/                         # 10 files (NEW - P1)
│   │   └── hubspot_client, salesforce_client,
│   │       lead_scoring, lead_routing, nurture_engine,
│   │       pipeline_manager, activity_tracker,
│   │       contact_enricher, task_automation, cli
│   │
│   ├── cdp/                         # 9 files (NEW - P2)
│   │   └── unified_profile, identity_resolution,
│   │       event_tracker, audience_builder, data_enricher,
│   │       export_manager, privacy_compliance,
│   │       lifetime_value, cli
│   │
│   ├── affiliate/                   # 7 files (NEW - P2)
│   │   └── impact_client, shareasale_client,
│   │       affiliate_discovery, commission_calculator,
│   │       fraud_detector, payout_manager,
│   │       performance_tracker, cli
│   │
│   ├── influencer/                   # 9 files (NEW - P2)
│   │   └── discovery, profile_analyzer, reach_estimator,
│   │       outreach_automation, contract_generator,
│   │       content_approval, performance_tracker,
│   │       ugc_rights_manager, cli
│   │
│   ├── distribution/                 # 7 files (NEW - P2)
│   │   └── medium_client, substack_client,
│   │       guest_post_manager, pr_wire,
│   │       syndication_manager, social_scheduler, cli
│   │
│   ├── collaboration/               # 8 files (NEW - P2)
│   │   └── approval_workflow, client_portal,
│   │       team_management, role_permissions,
│   │       comment_system, notification_center,
│   │       activity_feed, cli
│   │
│   ├── revenue/                    # 8 files (NEW - CRITICAL)
│   │   └── margin_calculator, pnl_tracker, blended_roas,
│   │       tacos_calculator, ltv_analyzer,
│   │       roas_vs_margin, attribution_revenue, cli
│   │
│   └── retention/                   # 7 files (NEW - CRITICAL)
│       └── churn_predictor, win_back_campaigns,
│           loyalty_program, upsell_engine,
│           nps_tracker, reactivation, cli
│
├── tests/                          # 10 files
│   └── test_signals, test_competitive, test_creative,
│       test_integration, test_email, test_ab_test,
│       test_sms, test_crm, test_revenue, test_retention
│
└── examples/                       # 5 files
    ├── config.yaml
    ├── competitor_analysis_example.py
    ├── email_campaign_example.py
    ├── ab_test_example.py
    └── run_pipeline_example.sh
```

**Total files: ~150**
**Build time: 48 weeks (part-time) / 24 weeks (full-time)**

---

## Part XIX: Recommended Build Sequence (Updated)

### Phase 1: Core MVP (Weeks 1-4)
Priority order based on council feedback:
1. signals/ + competitive/ (competitor intelligence)
2. creative/ + campaign/ (generate + launch)
3. **revenue/** (CRITICAL - margin/P&L, the #1 gap)

### Phase 2: Performance Loop (Weeks 5-8)
4. performance/ (ROAS, bids, budget)
5. analytics/ (dashboards, reports)
6. **ab_test/** (P1 - validate variants)

### Phase 3: Capture + Engage (Weeks 9-12)
7. **landing/** (P0 - capture leads)
8. **email/** (P0 - email marketing)
9. **crm/** (P1 - lead management)

### Phase 4: Full Stack (Weeks 13-16)
10. **sms/** (P1 - SMS/WhatsApp)
11. **push/** (P1 - push notifications)
12. **retention/** (CRITICAL - close the retention loop)

### Phase 5: Advanced (Weeks 17-20)
13. **cdp/** (P2 - unified customer view)
14. **influencer/** (P2 - influencer discovery)
15. **affiliate/** (P2 - partner management)

### Phase 6: Polish (Weeks 21-24)
16. **distribution/** (P2 - content syndication)
17. **collaboration/** (P2 - team workflows)
18. MCP integrations + agent layer polish
19. Demo video + GitHub launch

---

## Part XX: Competitive Analysis & Positioning

**Based on analysis of 50+ top GitHub repos in marketing AI space (July 2026)**

---

### Key Competitors Analyzed

| Repo | Stars | Category | Key Insight |
|------|-------|----------|------------|
| `coreyhaines31/marketingskills` | 35.8K | Skills Collection | De-facto standard. Skills format = distribution. |
| `dub.co` | 23.8K | Attribution | Link attribution only. Elite users. Open source. |
| `claude-seo` | 10.3K | GEO/SEO | 25 sub-skills + 18 agents. Niche dominance. |
| `geo-seo-claude` | 8.8K | GEO | Citability scoring. Novel metric. |
| `claude-ads` | 6.6K | Ad Creative | 250+ checks. Most ad platforms covered. |
| `ai-marketing-claude` | 2K | Full Suite | 15 parallel subagents. Website audits + PDF reports. |
| `short-video-factory` | 4.2K | Video | One-click short video. Desktop UX. |
| `lightweight_mmm` | 1.1K | Attribution | Google's Bayesian MMM. Enterprise-grade. |
| `apify-mcp-server` | 1.5K | Data Extraction | AI agent data from social/search/maps. |

---

### The ONE Thing That Makes Marketic Different

**The Marketing Intelligence Flywheel:**

```
Analyze Competitor (GoMarble + Meta Ad Library)
    ↓
Identify Positioning Gaps (AI reasoning + confidence scores)
    ↓
Generate 47 Counter-Variants (parallel ensemble per variant type)
    ↓
Launch Top 5 via Composio (Meta/LI/Google)
    ↓
Track Performance (ROAS, CPA, attribution)
    ↓
Learn: Which variants won? WHY?
    ↓
Feed Back to Gap Analysis (increasingly smarter about this market)
```

**No competitor repo has this closed loop.**

---

### Positioning Strategy

**NOT:** "AI marketing tool" or "marketing automation"

**YES:** "The Marketing Intelligence OS"

The word "OS" is defensible:
- Kernel: LLM routing + memory layer
- Processes: signals → competitive → creative → campaign → analytics
- Feedback loop: attribution → routing adjustment
- Boot into any vertical: performance, email, SEO, social

**The tagline:**
> "Marketic encodes real performance marketing judgment -- not prompts, not automations, but a learnable system that gets smarter about YOUR market every time you run it."

**The demo that goes viral:**
> "I fed 'Notion' into marketic and it found 8 gaps they're not touching. Generated 47 counter-ads in 20 minutes. [GIF]"

---

### What to LEVERAGE from Existing Repos

| What Works | How Marketic Uses It |
|------------|----------------------|
| Claude Code skills format (`coreyhaines31` 35.8K) | Create `skills/analyze-competitor.md`, `skills/generate-variants.md` |
| GEO trend (`claude-seo` 10.3K) | Every blog post = `llm.txt` included. GEO-scored ads. |
| n8n template ecosystem (23.5K templates) | Create `templates/` directory. n8n workflow → marketic CLI = distribution |
| Reasoning transparency | Every output includes the reasoning chain. Black box = bad. |
| dub.co's elite user strategy | Used by Framer, Perplexity, Twilio. Target similar tier. |

---

### What to AVOID

| Mistake | Why | Fix |
|---------|-----|-----|
| Build 20 modules at once | No user believes 20 things work well | Ship 3 killer modules first |
| Compete on "more skills" vs `coreyhaines31` (35.8K) | They have 10x community trust | Compete on SYSTEM, not skills count |
| Build black box like Icon AI CMO | Getting critique for no reasoning trail | Transparency IS the moat |
| Enterprise-only pricing | Closed platforms lose | Open source + paid templates/hosting |
| Skip the demo video | The 20-min GIF IS the launch | Everything else is footnotes |

---

### Priority: The 2-Week MVP

**Ship in 2 weeks, not 12:**

```
Week 1:
  - pipeline/engine.py (Signal → Plan → Execute → Respond)
  - router/ (classifier + scorer + selector + ensemble)
  - competitive/gaps.py (GoMarble integration)
  - creative/variants.py (47 variant generation)
  - campaign/launcher.py (Composio integration)

Week 2:
  - memory/layer.py (3-layer: session + persistent + semantic)
  - middleware/pipeline.py (rate limit + circuit breaker)
  - skills/bridge.py (slash commands)
  - templates/ (10 killer templates)
  - Demo video + GitHub launch
```

**The 3 killer modules:**
1. `competitive/` -- Analyze competitor gaps
2. `creative/` -- Generate 47 variants  
3. `campaign/` -- Launch via Composio

Everything else = expansion after 1,000 stars.

---

### Competitive Scorecard

| Dimension | Marketic | Best Competitor | Verdict |
|-----------|----------|-----------------|---------|
| Breadth | 8/10 | awesome-n8n 9/10 | Strong but overextended at launch |
| Depth (1 thing) | 4/10 | claude-seo 10/10 | Narrow to 1 killer demo first |
| Novelty | 9/10 | None 8/10 | Feedback loop + routing = novel |
| Demo-ability | 9/10 | claude-ads 7/10 | 20-min GIF is strong |
| Community trust | 2/10 | marketingskills 10/10 | Needs 6-12 months |
| Viral potential | 8/10 | GEO repos 7/10 | Strong if demo lands |

---

### Killer App: The 20-Minute Counter-Campaign

```bash
marketic launch-counter-campaign \
  --competitor notion \
  --budget 10000 \
  --platforms meta,linkedin,google

# Output in 20 minutes:
# [1] Positioning Map (2x2 matrix) for Notion
# [2] "8 Gaps Notion Is Leaving Open" -- ranked by market size
# [3] 47 ad variants across Google/Meta/LinkedIn
# [4] Each tagged: gap, emotional trigger, confidence %
# [5] Top 5 auto-launched via Composio with $10K budget
# [6] Attribution model configured for 30-day learning
# [7] Weekly report scheduled to WhatsApp
```

**Why this is viral:**
1. Nobody does this end-to-end
2. Demoable in a 60-second GIF
3. Answers a real pain point (competitor analysis is manual + slow)
4. Compounds (analyze 10 competitors = increasingly authoritative)
5. Shareable ("I ran this for [X] and found [Y]")

---

## Summary: The Pivot to Win

| Before (Old Plan) | After (Competitive Pivot) |
|------------------|-------------------------|
| 20+ modules, all at once | 3 killer modules first |
| 12-week build | 2-week MVP |
| 11 MCP integrations | 2 MCPs first (GoMarble + Composio) |
| "Comprehensive marketing OS" | "The competitor intelligence flywheel" |
| Build all 6 agents | Build 1 agent that demonstrates the loop |
| Compete with skills count | Compete with SYSTEM + reasoning transparency |
| Closed architecture | Open + skills format + templates distribution |

**The repo that wins is not the one that does the most things. It's the one whose ONE thing you can't stop thinking about.**

Marketic's ONE thing: **"Watch it analyze your competitor, find their 8 biggest gaps, and generate 47 counter-variants in 20 minutes -- and show you exactly WHY it made every decision."**
