# Marketic — Marketing Intelligence OS

## Identity

Marketic is an AI-native marketing operating system that encodes real operator judgment into executable marketing intelligence.

It is NOT a collection of prompts or a generic AI marketing tool.

It is a demonstration of systems-level marketing intelligence that can only come from someone who has:
- Scaled campaigns from zero to millions
- Built growth machines for fintech, SaaS, and consumer products
- Operated across performance marketing, brand, content, and GTM
- Deployed AI orchestration in production at scale

---

## Positioning

**This repository proves Subhajit can do what no other marketing leader claims:**

> Build the entire marketing stack — signal intelligence, creative generation, campaign orchestration, performance analytics, and GTM strategy — as an integrated AI-native operating system.

NOT:
- "I use AI for marketing"
- "I built some marketing automations"
- "I know how to prompt ChatGPT"

BUT:
- "I built the marketing OS that runs itself"
- "I encoded 10 years of performance marketing judgment into production AI systems"
- "I can build any marketing capability and demonstrate it end-to-end"

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MARKETIC OS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   SIGNAL    │  │  CREATIVE  │  │ CAMPAIGN    │              │
│  │ INTELLIGENCE│  │ GENERATION │  │ ORCHESTRATION│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  ANALYTICS  │  │  PERSONALI-│  │    GTM      │              │
│  │  & TRACKING │  │   ZATION   │  │  INTELLIGENCE│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    FOUNDATION LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  LLM     │  │ MEMORY   │  │ORCHESTRATION│ │ ALERTS   │       │
│  │  ROUTING │  │  LAYER   │  │  LAYER    │  │  LAYER   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Map

### 1. Signal Intelligence (`signal/`)

**What it does:** Collects market signals from RSS, Reddit, Twitter, Google Trends, ProductHunt

**Why it matters:** Real-time market intelligence is the foundation of adaptive marketing

**Files:**
- `collectors/` — Source-specific collectors (RSS, Reddit, Twitter, Trends, PH)
- `analyzers/` — Signal analysis and categorization
- `alerts.py` — Priority-based alerting

**Examples:**
```bash
python -m signal.collectors.reddit --subreddits marketing,growthmarketing
python -m signal.collectors.trends --query "fintech marketing"
python -m signal.run_pipeline --daily
```

---

### 2. Creative Generation (`creative/`)

**What it does:** AI-powered content creation across all formats and channels

**Why it matters:** Creative velocity is the #1 differentiator in modern marketing

**Files:**
- `copy/` — Ad copy, landing page copy, email copy generation
- `social/` — Twitter threads, LinkedIn posts, Instagram captions
- `seo/` — Blog posts, articles, SEO-optimized content
- `video/` — Video script generation, short-form content

**Key Features:**
- Multi-variant copy generation (A/B ready)
- Channel-specific adaptation
- Tone/style customization
- SEO + GEO optimization

**Examples:**
```bash
python -m creative.copy generate --product "AI marketing tool" --channel google_ads
python -m creative.social twitter --topic "AI in fintech" --thread-length 10
python -m creative.seo blog --keyword "marketing automation" --length 2000
```

---

### 3. Campaign Orchestration (`campaign/`)

**What it does:** End-to-end campaign management with AI optimization

**Why it matters:** Campaigns that adapt outperform static campaigns 3-5x

**Files:**
- `builder.py` — Campaign structure and architecture
- `optimizer.py` — Real-time performance optimization
- `budget_router.py` — AI-powered budget allocation
- `ab_tester.py` — Automated A/B test analysis

**Examples:**
```bash
python -m campaign.build --objective "lead_generation" --budget 10000
python -m campaign.optimize --campaign-id abc123 --objective cpa
python -m campaign.budget_router --rebalance daily
```

---

### 4. Analytics & Tracking (`analytics/`)

**What it does:** Performance measurement, attribution, and ROI analysis

**Why it matters:** You can't improve what you don't measure

**Files:**
- `attribution.py` — Multi-touch attribution modeling
- `dashboards.py` — Real-time performance dashboards
- `reports.py` — Automated reporting
- `funnel.py` — Funnel analysis and conversion tracking

**Examples:**
```bash
python -m analytics.attribution --model linear --date-range 30d
python -m analytics.report --weekly --channels google,meta,linkedin
```

---

### 5. Personalization (`personalization/`)

**What it does:** Audience segmentation and dynamic content personalization

**Why it matters:** Personalized experiences convert 2-5x higher

**Files:**
- `segmentation.py` — AI-powered audience segmentation
- `dynamic_content.py` — Personalized content generation
- `recommender.py` — Product/content recommendations

---

### 6. GTM Intelligence (`gtm/`)

**What it does:** Go-to-market strategy, positioning, competitive analysis

**Why it matters:** The best product loses without the right GTM

**Files:**
- `positioning.py` — Market positioning analysis
- `competitive.py` — Competitive intelligence
- `narrative.py` — Market narrative generation
- `launch.py` — Launch orchestration

**From growth-workflow-os DNA:**
- Strategic narrative analysis
- Market positioning maps
- Competitive framing

---

## Foundation Layer

### LLM Routing (`foundation/llm_router/`)

Built on a3m-style parallel multi-LLM execution:
- Query classification → optimal model routing
- Parallel generation → result merging
- Confidence-weighted voting
- Cost-performance optimization

### Memory Layer (`foundation/memory/`)

SQLite-backed persistent memory:
- Campaign performance memory
- Creative asset library
- Audience insight database
- Market thesis tracking

### Orchestration Layer (`foundation/orchestration/`)

omniclaw-style multi-channel orchestration:
- Multi-platform publishing
- Workflow automation
- Event-driven triggers
- Error recovery

### Alert Layer (`foundation/alerts/`)

Multi-channel alerting:
- WhatsApp notifications
- Telegram alerts
- Email reports
- Slack integration

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Das-rebel/marketic
cd marketic
pip install -r requirements.txt

# Run full signal intelligence pipeline
python -m signal.run_pipeline

# Generate a marketing campaign
python -m campaign.build --objective "app_installs" --budget 50000

# Run analytics report
python -m analytics.report --weekly
```

---

## What Makes This Different

| Traditional Marketing | Marketic |
|---------------------|----------|
| Point solutions | Integrated OS |
| Static campaigns | Adaptive campaigns |
| Manual optimization | AI-optimized |
| Siloed data | Unified intelligence |
| Single-channel | Cross-channel orchestration |
| Delayed insights | Real-time signals |
| Generic content | Personalized at scale |

---

## Technical Stack

- **Language:** Python 3.11+
- **LLM:** MiniMax-M2.7 (primary), qwen3:4b (local teacher), parallel routing
- **Database:** SQLite (memory), PostgreSQL (production)
- **Orchestration:** Custom async pipeline
- **Browser:** Playwright (sota-browser style)
- **APIs:** OpenRouter, Groq, Anthropic, custom

---

## Project Context

This repo demonstrates capabilities built on top of:
- **a3m** — Parallel multi-LLM routing (github.com/Das-rebel/a3m-router)
- **growth-workflow-os** — AI-enabled growth systems (github.com/Das-rebel/growth-workflow-os)
- **omniclaw** — Universal AI orchestration

---

## Success Criteria

A reviewer should think:

> "This isn't just prompts or automation scripts. This is someone who understands marketing at a systems level and knows how to build AI that actually executes."

---

## Contributing

This is a personal portfolio project demonstrating AI-native marketing capabilities.

## License

MIT
