# Marketic — Your Marketing Brain

**You get a market briefing every morning at 8am. Competitor moves, budget advice, and campaign plans — before your first coffee. No analyst headcount required.**

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![Tests](https://github.com/Das-rebel/marketic/actions/workflows/tests.yml/badge.svg)](https://github.com/Das-rebel/marketic/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## A Day With Marketic

**☕ 8:00 AM — Your briefing is waiting.**
Overnight, Marketic scanned prediction markets, Hacker News, Reddit, X, Product Hunt and TikTok.
Today it tells you: *the Kraken IPO conversation has $1.6M riding on it at 15% odds — worth
riding that narrative this week. The Macron story? $2.1M volume but 4% likely — ignore it,
it's noise dressed as signal.*

**🔍 10:00 AM — "What is our competitor doing?"**
You ask. Marketric pulls their **real ads from the Facebook Ads Library** — actual copy,
actual delivery dates, actual spend signals — and tells you their hook, their offer,
and three angles they're leaving open.

**💰 11:00 AM — "Where should next month's budget go?"**
Not "email gets 5x ROAS so put everything there." Marketic knows that channel runs at 15%
margin while paid social runs at 85% — so it recommends where profit actually lands.

**📝 2:00 PM — You need a campaign brief for the team.**
One command produces it: positioning, copy variants, channel split, posting times,
brand colors and fonts already resolved. Hand it to any AI agent or junior marketer —
they don't need to ask you anything.

**🌙 Whenever — It remembers.**
Every decision is logged with its cost and reasoning. Patterns that repeat become
written rules your future campaigns automatically follow.

---

## What This Replaces

| Instead of... | You have |
|---|---|
| A junior analyst compiling Monday reports | An automatic 8am briefing |
| Guessing which market buzz matters | Probability-scored signals with a track record (Brier-scored against outcomes) |
| Manually stalking competitor ads | Real ad library pulls on demand |
| Spreadsheet budget debates | Margin-aware allocation with reasoning attached |
| Re-explaining brand rules every project | Rules learned once, enforced in every brief |

---

## Setup (Once, ~5 Minutes)

```bash
git clone https://github.com/Das-rebel/marketic
cd marketic && pip install -e .
python3 init_memory_db.py
```

That's the whole setup. The daily briefing schedules itself (GitHub Action, 8am UTC)
and commits each digest so you never miss one. Optional keys unlock more:

| Key | Unlocks |
|---|---|
| *(none)* | Briefings, campaigns, creative, budgets — free local models |
| `FB_ACCESS_TOKEN` | Real competitor ad library data |
| `SERPER_API_KEY` | Automatic prospect finding for outreach |

---

## Questions Marketic Answers Daily

| You ask | It does |
|---|---|
| "What's moving in my market?" | Scans 6 sources, filters drama from demand |
| "Is this trend real?" | Shows the money behind it and its track record |
| "Build me a launch campaign" | Full brief: strategy, creative, budget, schedule |
| "Find me customers" | Prospects matching your niche, researched, outreach drafted |
| "How did we do last week?" | Pipeline pulse + AI spend + signal accuracy score |

No prompt engineering. One plain-English entry point (`ask_marketic`) routes
any marketing question to the right specialist.

---

## For Your Technical Teammate

Marketic is also a **43-tool MCP server** — drops into Claude Desktop or Cursor
with one JSON block, so your AI assistant gains all of these abilities natively:

```json
{ "mcpServers": { "marketic": {
    "command": "python3",
    "args": ["/absolute/path/to/marketic/mcp_server.py"] } } }
```

Every capability is callable programmatically; every brief is versioned JSON
([schema](docs/BRIEF_SCHEMA.md)); every decision is auditable via SQLite.

---

## Why Trust It?

- **Measured, not asserted:** prediction signals are scored against real outcomes (Brier score in every briefing). If calibration slips, you'll see it.
- **Transparent by default:** every AI call logs model, cost, confidence, and reasoning chain.
- **Evidence chains:** every campaign brief lists the exact signals that informed it.
- **Open source, MIT** — self-hosted, your data stays yours.

## Learn More

- [`docs/BRAIN_WORKFLOW.md`](docs/BRAIN_WORKFLOW.md) — how it learns and improves
- [`docs/BRIEF_SCHEMA.md`](docs/BRIEF_SCHEMA.md) — what's inside a brief
- [`docs/COUNCIL_ROUND2.md`](docs/COUNCIL_ROUND2.md) — architecture vs comparable repos
- [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) — all 43 tools

---

MIT © Subho Das