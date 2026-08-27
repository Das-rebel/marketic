# Marketic — Your Marketing Brain

> *"The best marketing teams don't guess what the market wants. They measure it."*
> The problem: measuring market signals requires 5 SaaS tools, 2 analysts, and still misses Monday morning.

**Marketic is the marketing nervous system — it watches the market 24/7 and tells you what matters before your first coffee.**

Every morning at 8am, you get a briefing built from Polymarket prediction markets, Google Trends, competitor ads, social signals, and your own CRM pipeline. Not a data dump — a prioritised brief with budget advice, competitor moves, and campaign plans you can act on immediately.

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![Tests](https://github.com/Das-rebel/marketic/actions/workflows/tests.yml/badge.svg)](https://github.com/Das-rebel/marketic/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What Changed Last Week in Your Market?

That's the question every Monday morning. Most teams answer it with:

| Old way | Problem |
|---|---|
| Google Trends manually | Snapshot, no context |
| Stalking competitor ads | Time-consuming, incomplete |
| Asking the analyst | Not available on weekends |
| Gut feeling | Doesn't scale |

**Marketic answers it automatically.**

---

## A Day With Marketic

**☕ 8:00 AM — Your briefing is ready.**

```
TOP SIGNALS (2026-08-27)
━━━━━━━━━━━━━━━━━━━━━━
1. Kraken IPO buzz     $1.6M / 15% odds → real momentum ✅
2. UK election called  $822K / 31% odds   → act on this ⚡
3. Macron speculation  $2.1M / 4% odds   → ignore (noise)

BUDGET RECOMMENDATION
Margin-adjusted: email wins (85% margin) over paid social (15% margin)
Campaign brief: ready for your team
```

No analyst. No spreadsheet. No guesswork.

**🔍 10:00 AM — "What is our competitor doing?"**
Ask once. Get real ad creatives from Facebook Ads Library — actual copy,
delivery dates, spend signals — with three counter-angles generated.

**💰 11:00 AM — "Where should next month's budget go?"**
Not "email gets 5x ROAS." Marketic knows email runs at 15% margin while paid social
runs at 85%. It recommends where profit actually lands, with the reasoning attached.

**📝 2:00 PM — "Build me a campaign brief."**
One command. Positioning, copy variants, channel split, posting windows,
brand colours resolved. Hand it to any team member — they don't need to ask you anything.

**🌙 Evening — It remembers.**
Every signal decision logged with cost and reasoning. Patterns that repeat become
written rules. Next campaign inherits last quarter's lessons automatically.

---

## TL;DR

**Before Marketic:**

```
Marketing team: "Can someone pull competitor ad data for Monday's meeting?"
Analyst: "I'll have it by Tuesday."
(You: spent the weekend worrying about it anyway)
```

**After Marketic:**

```python
from marketic import SignalFanout, CampaignBuilder

# Morning briefing
signals = await SignalFanout(region="india").run("fintech D2C India")
brief   = await generate_brief(signals, brand=my_brand)

# That's it. Brief is ready.
```

**Result:** Monday briefing done before Sunday night.

---

## Quick Start

```bash
git clone https://github.com/Das-rebel/marketic
cd marketic && pip install -e .
python3 init_memory_db.py

# Your first briefing — no API keys needed for the core loop
python3 daily_briefing.py "skincare brand India"
```

Optional keys unlock more:

| Key | Adds |
|---|---|
| `FB_ACCESS_TOKEN` | Real competitor ad data from Facebook Ads Library |
| `SERPER_API_KEY` | Prospect discovery and enrichment |
| `OLLAMA_BASE` | Free local AI models for creative generation |

---

## 55 Tools Across 15 Categories

| Category | What it does |
|---|---|
| **Signal intelligence** | 9-source fan-out: Polymarket, Google Trends, HN, Reddit, X, YouTube, Indian media RSS, Product Hunt, FB Ads |
| **Competitor intelligence** | FB Ads Library search, ad breakdown with hook/offer/CTA, positioning analysis |
| **Calibration** | Track signals → resolve outcomes → Brier score shows what's actually reliable |
| **Campaigns** | Full-funnel brief generation, margin-aware budget allocation, narrative framing |
| **Prospecting** | Top-of-funnel ICP discovery across Serper/Twitter/Reddit/Product Hunt + CRM enrichment |
| **Creative** | Ad copy variants, social posts, SEO articles — scored by predicted performance |
| **Publishing** | Content calendar, hashtag optimisation, platform scheduling |
| **UGC** | Discover, curate, request permission, track reposts |
| **Design** | Brand-as-data templates: one template, any brand, resolved automatically |
| **CRM** | Leads, deals, pipeline, activities — full lifecycle |
| **Analytics** | 5-model attribution: first-touch, last-touch, linear, time-decay, data-driven |
| **Learning** | Audit trail → distillation → brand brain markdown for human review |
| **Ensemble AI** | Multi-model voting with cost/reasoning logged per decision |

---

## The Calibration Claim — Proved, Not Just Stated

Most tools say "our signals are good." Marketic proves it.

```
Brier Score: 0.14 (lower = better; 0 = perfect, 0.25 = random)
Predictions tracked: 47  |  Resolved: 12  |  Pending: 35
Calibration: well-calibrated on Polymarket sources (n=8, Brier=0.09)
             uncertain on Twitter sources (n=22, Brier=0.31)
```

Every briefing shows you which sources are reliable and which to take with caution.
Over time, you know exactly what Marketic is and isn't good at — and it shows you.

---

## Architecture

```
SIGNALS            REASON              HANDOFF              LEARN
─────────          ──────             ──────              ─────
9 sources    →   Ensemble AI   →   Brief (JSON)    →   Audit trail
Polymarket          ↓             ↓                      ↓
Google Trends   Scorecard      Brand tokens         Brand brain
HN / Reddit    Budget router  Posting windows      (markdown)
X / YouTube    Ad analyzer    Execution plan       Human review
Indian media                    ↓                      ↓
              →   Counter-brief      Campaign team      New rules
```

- **Sense:** 9-source parallel fan-out, volume × P(YES) scoring (Polymarket is 73.4% "No"
  historically — raw volume overweights drama, we correct for it)
- **Think:** ensemble AI vote + calibration scorecard + margin-aware budget router
- **Handoff:** self-contained brief JSON with evidence chain, brand tokens, timeline
- **Learn:** every decision logged → distillation → brand brain markdown → human approval

---

## Why Not Just Use Existing Tools?

| Tool | What Marketic replaces |
|---|---|
| Semrush / Ahrefs | SignalFanout + generate_seo_content |
| Facebook Ads Library (manual) | search_fb_ads + analyze_competitor_ad |
| Hotjar / FullStory | UGC curator + trend signals |
| HubSpot (basic) | CRM + pipeline + attribution |
| Morning briefing by analyst | daily_briefing.py (automatic, every morning) |
| Spreadsheet budget allocation | optimize_budget with margin-aware reasoning |

One system. One brief. No copy-paste between tabs.

---

## Open Source, MIT

Everything is self-hosted. Your competitor data, your pipeline, your budget logic — stays yours.

```bash
git clone https://github.com/Das-rebel/marketic
cd marketic && pip install -e . && python3 init_memory_db.py
```

---

## Learn More

| Doc | What it covers |
|---|---|
| [`docs/BRIEF_SCHEMA.md`](docs/BRIEF_SCHEMA.md) | What's inside a campaign brief |
| [`docs/BRAIN_WORKFLOW.md`](docs/BRAIN_WORKFLOW.md) | How the learning loop compounds over time |
| [`docs/COUNCIL_ROUND2.md`](docs/COUNCIL_ROUND2.md) | Architecture decisions and why |
| [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) | All 55 tools, all parameters |

MIT © Subho Das
