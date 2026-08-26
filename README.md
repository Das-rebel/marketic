# Marketic — Marketing Intelligence OS

**Transform market signals into execution-ready briefs. Every decision audited. Every claim measured. All tools open.**

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![Tests](https://github.com/Das-rebel/marketic/actions/workflows/tests.yml/badge.svg)](https://github.com/Das-rebel/marketic/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Quick Launch

```bash
git clone https://github.com/Das-rebel/marketic
cd marketic && pip install -e .
python3 daily_briefing.py "ai agents"
```

Live briefing in 60 seconds. Here's real output:

![Marketic daily briefing — real terminal output](docs/demo_terminal.png)

---

## What This Does

Marketic runs the full marketing intelligence loop:

```
📡 SENSE        6-source signal fan-out (Polymarket · HN · Reddit · X · Product Hunt · TikTok)
                probability-calibrated: volume × P(YES) — drama filtered, demand ranked
      ↓
🧠 THINK        ensemble AI voting · competitor ad intel (real creatives via Facebook
                Ads Library) · margin-aware budgets (roas × contribution margin)
      ↓
📦 HANDOFF      self-contained JSON brief: positioning + copy + budget + posting times
                + brand tokens + evidence chain — execution agents never call back
      ↺
🔁 LEARN        audit trail → recurring patterns → brain/<brand>.md → human PR review
                → approved rules injected into every future brief
```

Everything the brain decides is logged (model, cost, confidence, reasoning).
And the core claim is **measured**: prediction signals are tracked against real
outcomes with Brier scores, not just asserted.

---

## Key Features

| Feature | What It Does |
|---|---|
| **Signal Fan-Out** | Parallel collection across 6 sources with consensus-theme synthesis |
| **Probability-Adjusted Scoring** | `volume × P(YES)` — because 73.4% of Polymarket markets resolve "No", raw volume rewards drama |
| **Calibration Scorecard** | Predictions auto-resolved against outcomes; Brier score proves (or disproves) the calibration live |
| **Real Competitor Ad Intel** | Facebook Ads Library integration returns actual ad copy and delivery data — ground truth, not image guessing |
| **Signal-Driven Prospecting** | Discover prospects → enrich with live market signals → auto-draft outreach → scored CRM leads |
| **Self-Learning Brain** | Recurring decision patterns distilled into brand rules; humans approve via PR; approved rules bind every future brief |
| **Ensemble AI Voting** | Multiple models vote; cost tracked per execution; free-tier aware |
| **Margin-Aware Budgeting** | Optimizes `roas × contribution_margin` — profit over vanity ROAS |
| **Brand-as-Data** | Zero hardcoded brands; one template renders any identity via `{{brand.*}}` tokens |
| **43 MCP Tools** | Stdio JSON-RPC server; drops into Claude, Cursor, or any MCP client |

---

## MCP Usage

```json
{
  "mcpServers": {
    "marketic": {
      "command": "python3",
      "args": ["/absolute/path/to/marketic/mcp_server.py"]
    }
  }
}
```

Paste into **Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`)
or **Cursor** (`.cursor/mcp.json`).

### Tool Highlights

| You need | Tool |
|---|---|
| What's moving right now | `signal_fanout` |
| Real competitor ads + spend | `search_fb_ads` |
| A full campaign strategy | `build_campaign` |
| Creative variants | `generate_creatives` |
| An agent-ready brief | `generate_brief` |
| Prospect pipeline | `run_prospect_loop` |
| Budget allocation by margin | `optimize_budget` |
| What the system has learned | `distill_learnings` |
| Plain-language entry point | `ask_marketic` — routes any question to the right tool |

Or skip tool-picking entirely: `ask_marketic("what's moving in AI markets")`.

---

## The Learning Loop

Every AI decision feeds the audit trail. Recurring patterns get distilled into
brand-level rules (`brain/<brand>.md`), reviewed by humans via PR, and approved
rules are injected into every future brief. See [docs/BRAIN_WORKFLOW.md](docs/BRAIN_WORKFLOW.md).

## Measured, Not Asserted

The probability-calibration isn't a slogan — it's a scoreboard:

```
## 🎯 Signal Calibration
- Tracked: 26 · Resolved: 12 · Pending: 14
- Brier score: 0.183 (good; <0.25 beats chance)
- 20-40% bucket: 5 predictions, actual YES rate 40%
```

Predictions snapshot on every fan-out, auto-resolve against Polymarket outcomes,
and surface in the daily briefing.

---

## Adaptability

| Adaptation | How |
|---|---|
| **Brand swap** | `BrandTokens.from_image()` or config — same templates, any identity |
| **Scale** | Free stack (local LLMs, $0) → enriched (Serper) → full (HubSpot/Clay) |
| **Sources** | Filter per-run: `signal_fanout(sources=["polymarket"])` |
| **Scheduling** | Built-in GitHub Action runs the daily briefing at 08:00 UTC |

---

## Why Startups Choose It

- **No marketing expert needed** — signal→brief translation is the product
- **$0 to start** — all 43 tools run on free local models
- **Pay-as-you-grow** — API keys optional, everything degrades gracefully
- **Investor-ready** — audit trail on every decision, evidence chains on every brief

---

## Documentation

- [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) — full 43-tool reference
- [`docs/BRIEF_SCHEMA.md`](docs/BRIEF_SCHEMA.md) — versioned brief contract for agents
- [`docs/BRAIN_WORKFLOW.md`](docs/BRAIN_WORKFLOW.md) — how learning works end-to-end
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contributing guide
- [`docs/COUNCIL_ROUND2.md`](docs/COUNCIL_ROUND2.md) — architecture review vs comparable repos
- [`docs/VAULT_PICKS.md`](docs/VAULT_PICKS.md) — evidence behind every feature decision

---

MIT © Subho Das