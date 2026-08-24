# Marketic — Marketing Intelligence OS

A white-label AI marketing platform that generates strategic briefs for execution agents — startup-friendly, MCP-ready, and built to adapt to any brand, budget, or market.

---

## For Startups: Why This Exists (Quick Version)

You have a product. You have potential customers. You don't have a 10-person marketing team to turn market noise into a plan.

Marketic takes 5 sources of market data (Polymarket bets, HN threads, Reddit discussions, Twitter trends, Product Hunt launches), finds what's actually important, and writes the brief your team (or AI agents) can act on.

**You don't need a marketing expert. You need a marketing brain that works.**

---

## Key Features That Adapt With You

| Feature | How It Adapts To You |
|---|---|
| **Signal Fan-Out** | Pick your sources: just Polymarket? Just HN? Add Reddit, Twitter, Product Hunt as you grow |
| **Brand-as-Data** | One template renders your brand colors, font, and tone — swap brand by changing tokens |
| **Margin-Aware Budgeting** | Works at $500/month or $50K/month; scales with your contribution margins |
| **Ensemble AI** | Uses cheap/free models (ox-alpha FREE, gemini-flash) first; escalates only when needed |
| **MCP Server (39 tools)** | Drop into any existing AI pipeline — Claude, Cursor, custom agents |
| **Execution Brief Handoff** | Produces structured JSON briefs any agent can consume — no custom integrations needed |
| **Audit Trail** | Track every AI decision for transparency — critical for investor reporting |

---

## Quick Launch (5 Minutes)

```bash
# 1. Clone
git clone https://github.com/Das-rebel/marketic && cd marketic

# 2. Install (Python 3.11+ only)
pip install -e .

# 3. Initialize database
python3 init_memory_db.py

# 4. See what's happening right now
python3 daily_briefing.py "ai marketing"

# 5. Start the MCP server (connect from Claude, Cursor, etc.)
python3 mcp_server.py
```

### First Output (Real Example)

```
# ☀️ Marketic Daily Briefing — 2026-08-24

📡 Signals (21 matched across Polymarket, HN, Reddit, Twitter, PH)
- [polymarket] Kraken IPO — $1.6M volume, 15% probability
- [hacker_news] Anthropic's best model struggles to attract users
- [reddit] AI agent implementations growing

💰 Money Talking (Probability-Adjusted)
- Kraken IPO: $247K effective (high probability, real demand)
- Macron removal: $79K effective (low probability — drama, not deal)

🎯 Pipeline
- Open deals: 0 · Leads: 0 · Revenue tracked
```

> **Startup tip:** The probability-adjusted score is designed specifically for lean teams — it prevents you from chasing viral but unlikely events instead of real demand.

---

## MCP Usage (For Customers / Integrators)

Marketic exposes 39 MCP tools via `mcp_server.py`. Use with any MCP-compatible client:

### Claude / Anthropic
```json
{
  "mcpServers": {
    "marketic": {
      "command": "python3",
      "args": ["/Users/Subho/marketic/mcp_server.py"]
    }
  }
}
```

### Cursor / VS Code
Add to `.cursor/mcp.json` or settings — same JSON structure.

### Direct Python
```python
from marketic.mcp_server import MCPServer
server = MCPServer()
result = server.dispatch({"method": "tools/call", "params": {"name": "signal_fanout", "arguments": {"query":"AI agents"}}})
```

### Key MCP Tools by Use Case

| You Need | Tool | Example
|---|---|---|
| **Market intel** | `signal_fanout` | `"query": "marketing AI"` → 5-source synthesized brief |
| **Competitor ads** | `analyze_competitor_ad` | Image URL → hook/pacing/triggers + counter-angles |
| **Campaign build** | `build_campaign` | Objective + budget + timeline → full strategy |
| **Creative variants** | `generate_creatives` | Brief → 10 variants with scores |
| **Social posts** | `generate_social_posts` | Brand voice + topics → scheduled posts |
| **Budget** | `optimize_budget` | Channel data + margins → allocation strategy |
| **Brief export** | `generate_brief` | Campaign JSON → self-contained agent brief |

---

## Adaptability Features (Built In)

### Multi-Brand
```python
# One codebase, different brands
from execution.design_templates import BrandTokens
tokens = BrandTokens.from_brand_memory("brand_acme")
# Same templates, different colors/fonts/tone
```

### Multi-Language / Region
- Signal sources are configurable (filter by region, language, source)
- Brand tokens include language preferences
- Brief generation supports localization

### Multi-Scale
- $500/month startup: use free ox-alpha, local Ollama, no paid APIs
- $50K/month: add OpenRouter vision, Serper enrichment, Clay deep-dive
- Scale by adding sources — not by changing code

### Custom Brief Formats
The `generate_brief` MCP tool accepts any execution context:
- Calendar-only (no budget details)
- Full campaign (positioning + creative + budget + timeline + tokens)
- Export formats (JSON, Markdown, HTML for different agents)

---

## Price / Cost Structure

| Tier | Cost | What's Included |
|---|---|---|
| **Free / Self-Hosted** | $0 | Core 39 tools, local LLM, ollama vision, free models (ox-alpha, gemini-flash) |
| **Enriched** | ~$10/mo | Serper (cheap prospect enrichment), OpenRouter (better vision) |
| **Full** | ~$50/mo | All integrations (HubSpot, Clay, Postiz), premium vision, full audit |

No mandatory subscriptions for the core. The architecture is designed so you only pay for what you use — and the audit trail tells you exactly which calls cost what.

---

## Real Results From Use

- **Signal fan-out**: 21 matched sources daily across 5 platforms
- **Polymarket calibration**: $2.1M dramatic market correctly demoted to $84K (4% probability) — prevents chasing noise
- **Campaign structure**: 3-campaign funnel (testing/scaling/retargeting) with single-ad testing
- **Audit transparency**: Every decision logged with model, cost, and reasoning chain

---

## Documentation & References

- [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) — All 39 MCP tools with signatures
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — How to contribute
- [`docs/VAULT_PICKS.md`](docs/VAULT_PICKS.md) — Evidence for every feature decision
- [`docs/FEATURE_GAP_ANALYSIS.md`](docs/FEATURE_GAP_ANALYSIS.md) — Architecture reasoning
- `daily_briefing.py` — Cronnable digest pipeline
- `mcp_server.py` — MCP server (run with `python3 mcp_server.py`)

---

## What Comes Next (Built Into The Design)

- Brain files (`brain/<brand>.md`) — versioned strategy learnings
- Signal sources — TikTok transcripts, additional prediction markets
- Execution integration — deeper Postiz/Runway/Paper MCP connections
- Multi-brand orchestration — single brain, multiple execution agents

---

**License:** MIT © Subho Das
**Quick links:** [`README`](README.md) · [`API_DOCS`](API_DOCUMENTATION.md) · [`CONTRIBUTING`](CONTRIBUTING.md)