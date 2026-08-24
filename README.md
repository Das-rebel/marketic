# Marketic — Marketing Intelligence OS

**A white-label strategy brain for marketing: ensemble AI reasoning, calibrated market signals, and self-contained briefs any execution agent can run — with every decision audited.**

*Signals in → intelligence → briefs out. Transparent by default.*

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## The Architecture

```
┌─────────────────────────────────────────────────┐
│  Marketic = Strategy Brain (white-label)        │
│  signal fan-out · competitor intel · ensemble   │
│  margin-aware budgets · attribution · audit     │
└───────────────────┬─────────────────────────────┘
                    ↓  generate_brief (self-contained JSON)
┌─────────────────────────────────────────────────┐
│  Execution Agents (per-brand, your choice)      │
│  voice · calendar · creative · publishing       │
│  powered by existing tools: Paper MCP, Runway,  │
│  Postiz, Ollama — orchestrated, not cloned      │
└─────────────────────────────────────────────────┘
```

Marketic produces the **brief** (positioning + copy variants + budget + hashtags +
optimal times + resolved brand tokens). A brand agent executes it without calling back.

---

## What Makes It Different

| | Typical AI marketing tool | Marketic |
|---|---|---|
| Decisions | Black box | **Every call audited**: model, cost, confidence, reasoning chain |
| Signals | Single source, raw counts | **5-source parallel fan-out**, cross-source normalized, probability-calibrated |
| Budgets | Raw ROAS (vanity) | **Contribution-margin adjusted** (`roas × margin`) |
| Creative | Generates blind | **Counter-variants informed by VLM deconstruction of competitor ads** |
| Brand | Hardcoded per deployment | **Brand-as-data** — one template renders any brand via tokens |

---

## Quick Start

```bash
git clone https://github.com/Das-rebel/marketic && cd marketic
pip install -e .
python3 init_memory_db.py

# Daily briefing — live market signals + AI spend + pipeline
python3 daily_briefing.py "ai agents"

# MCP server (39 tools)
python3 mcp_server.py
```

Live briefing output:

```
📡 Signals (21 matched)
- [hacker_news] Anthropic's best AI model struggles to attract users...
💰 Money talking (Polymarket):
- Kraken IPO by ___? ($247K probability-adjusted)
💸 AI Spend: 14 decisions · $0.0031 total
```

Cron it: `0 8 * * * cd ~/marketic && python3 daily_briefing.py >> logs/briefing.log 2>&1`

---

## The Signal Fan-Out

**Identity:** You're the market-intelligence layer — before anyone writes a single line of copy, you know what's moving across platforms.

**Philosophy:** Real dollars should count more than noisy mentions, but *only when they're betting on likely outcomes*. The platform itself is structurally biased toward spectacle (see vault source below), so we score:

```
effective_volume = volume × implied_probability_of_YES
```

**Why this matters:**

- Polymarket volume alone = drama bias (73.4% of markets resolve "No" — see below)
- Our approach weights real demand by actual probability, not hype
- Output: consensus themes across sources, money outliers with adjusted scores, top-10 ranked items

### Sources Ranked by Signal Quality

| Source | Weight | Why |
|---|---|---|
| **Polymarket** | Highest | Real dollars on real outcomes — but `volume × P(YES)` corrected (see rationale) |
| Hacker News | High | Technical early-adopter density |
| Reddit | Med-High | Community depth |
| Product Hunt | Medium | Launch-day spike bias |
| Twitter/X | Baseline | Highest noise floor — included for coverage, never ranked #1 |

### Polymarket Base-Rate Rationale

**The problem:** prediction markets attract big money on dramatic but unlikely events. Raw volume overweights spectacle.

**The evidence (vault-cited):** @sterlingcrispin's "Nothing Ever Happens" analysis found that **73.4% of all Polymarket markets historically resolve "No"**. The platform structurally overflows with low-probability sensationalism.

**The fix:** score each market as `volume × implied P(YES)`:

| Market | Raw Volume | P(YES) | Effective Score | Before → After |
|---|---|---|---|---|
| Macron out by...? | $2,149,097 | 4% | **$79,517** | #1 → #4 |
| UK election called | $822,256 | 31% | **$254,899** | #4 → #1 |
| Kraken IPO | $1,597,835 | 15% | **$247,664** | #3 → #2 |

The sensational $2.1M market now correctly ranks below the $822K market with 8× the probability.

**Why it matters:** without probability correction, the briefing leads with viral headlines, not actual demand movement. This fix keeps you focused on *likely* events where money is on the table.

**Implementation:** `PolymarketCollector` pulls Gamma API `outcomePrices`, computes implied P(YES), scores `volume × prob`. Falls back to base rate 0.266 (73.4% resolve No) when prices are unavailable — deliberately conservative.

### Why Helena Would Approve

> "You're not just collecting signals — you're filtering the noise so your creative team attacks what matters. The signal fan-out isn't a data dump; it's a filter that surfaces the signals worth countering."

---

## Ensemble AI — Model Tiers

| Task | Model(s) | Cost |
|------|----------|------|
| Ad copy | deepseek-v4-flash | ~$0.0001 |
| Social posts | gemini-3.6-flash | ~$0.001 |
| Competitor analysis / narrative | ox-alpha (OpenCode Go) | **FREE** |
| Campaign strategy | 3-model vote + consensus | ~$0.05 |
| Competitor ad deconstruction | local Ollama vision → cloud fallback → heuristics | free → $0 |

Every tier logs to the audit trail. Query spend anytime:
`audit_get_cost_summary(start_date="2026-08-01")`

---

## MCP Tools — 39 Total

**See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for the full reference.**

| Category | Highlights |
|----------|-----------|
| **GTM** | `analyze_competitor`, `analyze_positioning`, `analyze_competitor_ad` (VLM hook/pacing/triggers → counter-brief), `generate_narrative` |
| **Creative** | `generate_creatives` (variant scoring + performance prediction), `generate_social_posts`, `generate_seo_content` |
| **Campaigns** | `build_campaign` (3-campaign funnel tactics), `optimize_budget` (margin-aware, 4 strategies) |
| **Intelligence** | `signal_fanout` (5 sources, synthesized brief), `collect_signals` |
| **Handoff** | `generate_brief` — self-contained campaign JSON for execution agents |
| **Analytics** | `get_attribution` (5 models) |
| **Hub** | 9 unified tools across WebEngage/HubSpot/Serper/Clay/etc. |
| **CRM** | 8 tools: leads, deals, pipeline, activities |
| **AI ops** | `ensemble_vote`, `audit_log`, `audit_get_log`, `audit_get_cost_summary` |

Full list: `echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | python3 mcp_server.py`

---

## Brand-as-Data

Zero hardcoded brands anywhere in the codebase. The entire visual identity is configuration:

```python
from execution.design_templates import BrandTokens, TemplateLibrary

tokens = BrandTokens.from_image("brand-screenshot.png")  # vision-extracted
# or BrandTokens.from_brand_memory(record), or hand-built

lib = TemplateLibrary(tokens)
out = lib.render_template("ig_menu_highlight", {"LABEL": "NEW", "TITLE": "NIGHT BREW"})
```

Same 8 templates render Bukito (`#6D0000`/Kisrre) or Acme (`#00AAFF`/Inter) from tokens alone.

---

## Daily Briefing Loop

`daily_briefing.py` chains the strategy brain into one cronnable digest:
signal fan-out → AI spend from audit trail → CRM pipeline pulse → markdown file
→ optional webhook (`MARKETIC_BRIEF_WEBHOOK` env).

---

## Repository Layout

```
marketic/
├── mcp_server.py              # MCP stdio server (39 tools)
├── daily_briefing.py          # cronnable strategy digest
├── init_memory_db.py          # SQLite setup
├── ensemble/                  # multi-model voting + audit trail
├── creative/                  # copy / social / SEO generators
├── campaign/                  # builder (funnel tactics) + margin-aware budget router
├── gtm/                       # competitive intel, positioning, narratives, VLM ad analysis
├── signals/                   # parallel fan-out collectors (incl. Polymarket P(YES))
├── analytics/                 # 5 attribution models
├── integrations/              # unified hub (WebEngage, HubSpot, Serper, Clay...)
├── execution/                 # design templates (token-driven), UGC, publisher, brief generator
├── crm/                       # leads, deals, activities, pipeline
├── memory/                    # brand memory, voice profile, embeddings
└── docs/
    ├── FEATURE_GAP_ANALYSIS.md  # architecture lessons from Helena (v2)
    └── VAULT_PICKS.md           # evidence-backed feature decisions
```

---

## Configuration

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENROUTER_API_KEY` | Premium + vision models | optional (free tiers exist) |
| `OPENCODE_GO_TOKEN` | FREE ox-alpha access | optional |
| `OLLAMA_BASE` | Local LLM/vision backend (default `127.0.0.1:11434`) | optional |
| `SERPER_API_KEY` | Cheap prospect enrichment | optional |
| `CLAY_API_KEY` | Deep enrichment escalation | optional |
| `MARKETIC_BRIEF_WEBHOOK` | Briefing delivery endpoint | optional |
| `HUBSPOT_API_KEY` etc. | Platform integrations | optional |

Everything degrades gracefully — no key is required to run the core.

---

## Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** — full reference for all 39 tools
- **[docs/FEATURE_GAP_ANALYSIS.md](docs/FEATURE_GAP_ANALYSIS.md)** — why the architecture looks this way
- **[docs/VAULT_PICKS.md](docs/VAULT_PICKS.md)** — evidence-backed feature decisions

---

## License

MIT © Subho Das
