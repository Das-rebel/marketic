# Marketic - Marketing Intelligence OS

A white-label AI marketing platform that generates data-driven briefs for execution agents.

## What It Does

Marketic analyzes market signals, competitor data, and user preferences to generate comprehensive marketing briefs. These briefs include:

- Campaign strategy and channel mix
- Budget allocation by channel
- Creative briefs with hook, pacing, and value proposition
- Posting schedule recommendations
- Brand-consistent messaging

All decisions are traceable through an audit trail.

---

## Key Features

- **Signal Fan-Out**: Parallel collection from Polymarket, HN, Reddit, Twitter/X, and more
- **Probability-adjusted scoring**: Volume × P(YES) to avoid overvaluing sensational but unlikely events
- **VLM-powered ad analysis**: Deconstructs competitor ads into hooks, pacing, and triggers
- **Ensemble voting**: Multiple models vote on decisions with cost tracking
- **Full audit trail**: Every AI decision is logged with cost and reasoning
- **Brand-as-data**: Templates use tokens ({{brand.primary}}) instead of hardcoded values

---

## Getting Started

```bash
# Install
git clone https://github.com/Das-rebel/marketic
cd marketic
pip install -e .

# Initialize database
python3 init_memory_db.py

# Generate a daily briefing
python3 daily_briefing.py "ai marketing"

# Start the MCP server (exposes 39 tools)
python3 mcp_server.py
```

### Example Briefing Output

```
# ☀️ Marketic Daily Briefing
**2026-08-24 00:43 UTC**

## 📡 Signals (21 matched)
- [polymarket] Putin out as President of Russia by...?
  https://polymarket.com/event/putin-out-before-2027

## 💰 Money talking (Polymarket):
- Putin out as President of Russia by...? ($21,542,743)

## 🎯 Pipeline
- Leads: 0 (avg score 0)
- Open deals: 0 worth $0
```

---

## Key Tools

- **Signal Fan-Out**: Parallel gathering from 5 sources
- **Ad Analysis**: VLM-based deconstruction of competitor ads
- **Ensemble Voting**: Multiple models compare responses
- **Audit Trail**: Complete record of all AI decisions
- **Brand-as-Data**: Templates use {{brand.token}} syntax

---

## Getting Help

Questions? Check:
- `mcp_server.py` for tool documentation
- `daily_briefing.py` for briefing loop details
- `docs/VAULT_PICKS.md` for feature origins
- `/search <query>` in the Marketic CLI

---

**Marketic is a strategy brain, not a content generator.** It creates briefs that expert agents use to build campaigns.