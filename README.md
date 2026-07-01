# Marketic — Marketing Intelligence OS

**AI-native full-stack marketing operating system.**

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## What is Marketic?

Marketic is an AI-native marketing operating system that proves Subhajit can build the **entire marketing stack** as an integrated AI system — not just use AI, but *build* the AI that runs marketing.

### The Proof, Not the Claim

| Capability | Traditional | Marketic |
|------------|-------------|----------|
| Signal Intelligence | Tools + manual | Automated AI collection + analysis |
| Content Generation | Human + templates | Multi-model AI generation + variants |
| Campaign Optimization | A/B tests + intuition | Real-time AI optimization |
| Analytics & Attribution | Dashboards + reports | AI-generated insights + predictions |
| Personalization | Segmentation + rules | AI-driven dynamic personalization |
| GTM Strategy | Consultants + frameworks | AI-encoded strategic intelligence |

---

## Core Modules

### 🔍 Signal Intelligence (`signal/`)
Real-time market intelligence from Reddit, Twitter, Google Trends, ProductHunt, RSS feeds.
```bash
python -m signal.run_pipeline --daily
python -m signal.collectors.reddit --subreddits marketing,growthhacking,fintech
```

### ✍️ Creative Generation (`creative/`)
AI-powered content creation across all channels: ads, social, blogs, email, video.
```bash
python -m creative.copy generate --product "AI tool" --channel google_ads
python -m creative.social twitter --topic "fintech" --thread-length 8
python -m creative.seo blog --keyword "marketing automation" --length 2000
```

### 🚀 Campaign Orchestration (`campaign/`)
End-to-end campaign management with AI-driven optimization and budget routing.
```bash
python -m campaign.build --objective "lead_gen" --budget 50000
python -m campaign.optimize --campaign-id abc123
python -m campaign.budget_router --rebalance daily
```

### 📊 Analytics & Tracking (`analytics/`)
Multi-touch attribution, funnel analysis, performance dashboards, automated reports.
```bash
python -m analytics.attribution --model linear --date-range 30d
python -m analytics.report --weekly --channels google,meta,linkedin
```

### 🎯 Personalization (`personalization/`)
AI-powered audience segmentation, dynamic content, product recommendations.
```bash
python -m personalization.segment --source user_behavior
python -m personalization.recommend --user-id abc123 --n 5
```

### 🗺️ GTM Intelligence (`gtm/`)
Positioning strategy, competitive analysis, market narrative, launch orchestration.
```bash
python -m gtm.positioning --competitor "hubspot" --category "marketing automation"
python -m gtm.narrative generate --product "AI marketing tool"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MARKETIC OS                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   SIGNAL    │  │  CREATIVE  │  │ CAMPAIGN    │              │
│  │ INTELLIGENCE│  │ GENERATION │  │ ORCHESTRATION│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  ANALYTICS  │  │  PERSONALI-│  │    GTM      │              │
│  │  & TRACKING │  │   ZATION   │  │  INTELLIGENCE│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                    FOUNDATION LAYER                             │
│  LLM Router (a3m-style) │ Memory │ Orchestration │ Alerts       │
└─────────────────────────────────────────────────────────────────┘
```

**Built on:**
- [a3m](https://github.com/Das-rebel/a3m-router) — Parallel multi-LLM routing
- [growth-workflow-os](https://github.com/Das-rebel/growth-workflow-os) — Signal intelligence
- [omniclaw](https://github.com/Das-rebel/omniclaw) — AI orchestration

---

## Quick Start

```bash
# Clone
git clone https://github.com/Das-rebel/marketic
cd marketic

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY=your_key
export GROQ_API_KEY=your_key

# Run signal intelligence
python -m signal.run_pipeline

# Generate campaign
python -m campaign.build --objective "app_installs" --budget 10000

# Run analytics
python -m analytics.report --weekly
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| LLM Routing | Custom parallel multi-model |
| Memory | SQLite (local), PostgreSQL (prod) |
| Orchestration | AsyncIO + custom pipeline |
| Browser | Playwright |
| APIs | OpenRouter, Groq, Anthropic |

---

## Why This Exists

This repository demonstrates that Subhajit can build **production AI systems** that actually execute marketing — not just write prompts.

It combines:
- 10+ years of performance marketing judgment
- Real operator experience (Axis Bank ₹1,500Cr, Groww 7x, NIRO)
- AI systems thinking (a3m, growth-workflow-os, omniclaw)
- Vault knowledge (17K+ marketing insights from Twitter, LinkedIn, research)

---

## License

MIT © Subhajit
