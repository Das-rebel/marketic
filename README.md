# Marketic — Marketing Intelligence OS

**AI-native marketing operating system with ensemble AI reasoning and full audit trails.**

*Closed-loop: Analyze → Generate counter-variants → Execute → Measure → Learn*

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 What Marketic Does

```bash
# Start the MCP server
python3 mcp_server.py

# Analyze a competitor
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"analyze_competitor","arguments":{"brand":"HubSpot"}},"id":1}' | python3 mcp_server.py
```

**Output:**
```json
{
  "competitor": "HubSpot",
  "analysis": "HubSpot dominates with all-in-one platform...",
  "confidence": 0.85,
  "models_used": ["stealth/ox-alpha"],
  "cost": 0.0,
  "analyzed_at": "2026-08-23T14:15:40"
}
```

**Why this is different:** Marketic exposes 43 marketing intelligence tools via MCP (Model Context Protocol), with ensemble AI voting, full audit trails, and transparent decision reasoning.

---

## 🔌 MCP Server — 43 Tools

| Category | Tools | Description |
|----------|-------|-------------|
| **GTM Strategy** | `analyze_competitor`, `compare_competitors`, `analyze_positioning` | Competitive intel, positioning maps, gap analysis |
| **Creative** | `generate_creatives`, `generate_social_posts`, `generate_seo_content` | Multi-channel ad copy, social posts, SEO articles |
| **Campaigns** | `build_campaign`, `optimize_budget` | Full campaign generation, ROAS-based budget rebalancing |
| **Narrative** | `generate_narrative` | Brand stories, thought leadership, industry analysis |
| **Signals** | `collect_signals` | Product Hunt, Hacker News, Twitter, Reddit intelligence |
| **Analytics** | `get_attribution` | 5 attribution models (first-touch, last-touch, linear, time-decay, position-based) |
| **Hub Connect** | `hub_*` (9 tools) | Unified multi-platform orchestration |
| **CRM** | `crm_*` (8 tools) | Leads, deals, pipeline, activity logging |
| **Ensemble AI** | `ensemble_vote` | Multi-model voting with confidence scoring |
| **Audit Trail** | `audit_log`, `audit_get_log`, `audit_get_cost_summary` | Full AI decision logging |

### Quick Test

```bash
# List all tools
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | python3 mcp_server.py

# Run a sample
python3 run_sample_campaigns.py
```

---

## 🧠 Ensemble AI Architecture

Marketic uses **tiered model routing** for cost-effective intelligence:

| Task Complexity | Models Used | Est. Cost |
|----------------|-------------|-----------|
| Simple (ad copy) | 1 cheap model | ~$0.0001 |
| Medium (competitor analysis) | 1 mid-tier model | ~$0.002 |
| Complex (campaign strategy) | 3 models parallel + voting | ~$0.05 |
| Critical (brand narrative) | ox-alpha + premium models | FREE* |

*ox-alpha via OpenCode Go is free

**Available Models:**
- `stealth/ox-alpha` — FREE via OpenCode Go
- `qwen/qwen3.7-max` — Premium reasoning
- `google/gemini-3.6-flash` — Fast, cost-effective
- `deepseek/deepseek-v4-flash` — Budget option
- `minimax/m3` — Via OpenCode Go

---

## 📊 Audit Trail

Every AI decision is logged with full transparency:

```json
{
  "audit_id": "a1b2c3d4e5f6",
  "timestamp": "2026-08-23T14:15:40",
  "action": "generate_creatives",
  "model": "stealth/ox-alpha",
  "cost": 0.0,
  "confidence": 0.87,
  "reasoning_chain": [
    "[stealth/ox-alpha] Lead with transformation angle...",
    "[google/gemini-3.6-flash] Lead with social proof..."
  ],
  "human_approved": null,
  "consensus": true
}
```

Query audit logs:
```
audit_get_log(brand_id="acme", action="generate_creatives", limit=100)
audit_get_cost_summary(start_date="2026-08-01")
```

---

## 🏗️ Architecture

```
Signal → Plan → Ensemble → Execute → Audit → Learn
   ↓        ↓        ↓         ↓        ↓        ↓
 Collect  Route   Vote+Log  Deploy   Track   Quality
         Model   Consensus  Multi   Cost    Loop
                  +Fallback Platform
```

**Closed-Loop Learning:**
1. **Collect** signals from Product Hunt, HN, Twitter, Reddit
2. **Plan** with competitive analysis and positioning maps
3. **Ensemble** vote across multiple models with confidence scoring
4. **Execute** campaigns via Hub Connectors (WebEngage, HubSpot, etc.)
5. **Audit** every decision with full reasoning chain
6. **Learn** from attribution data and performance metrics

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Das-rebel/marketic
cd marketic

# Install dependencies
pip install -e .

# Initialize database
python3 init_memory_db.py

# Run MCP server
python3 mcp_server.py

# Run sample campaigns
python3 run_sample_campaigns.py
```

**Environment variables** (optional for AI features):
```bash
OPENROUTER_API_KEY=...     # For premium models
OPENAI_API_KEY=sk-...      # Fallback
WEBENGAGE_API_KEY=...      # Marketing platform integrations
HUBSPOT_API_KEY=...
```

---

## 📁 Project Structure

```
marketic/
├── mcp_server.py              # MCP stdio server (43 tools)
├── init_memory_db.py           # SQLite database setup
├── run_sample_campaigns.py     # Sample campaign runner
├── ensemble/
│   ├── voting.py               # Multi-model ensemble voting
│   └── audit_trail.py          # Full AI decision audit logging
├── creative/
│   ├── copy_generator.py        # Multi-channel ad copy
│   ├── social_generator.py      # Platform-specific social posts
│   └── seo_generator.py         # SEO content with meta tags
├── campaign/
│   ├── builder.py              # Full campaign generation
│   └── budget_router.py         # ROAS-based budget rebalancing
├── gtm/
│   ├── competitive.py          # Deep competitive analysis
│   ├── positioning.py          # Market positioning maps
│   └── narrative.py            # Brand stories & thought leadership
├── signals/
│   └── collectors.py            # PH, HN, Twitter, Reddit collectors
├── analytics/
│   └── attribution.py           # 5 multi-touch attribution models
├── integrations/
│   └── unified_adapter.py       # 8+ platform connector hub
├── crm/
│   └── __init__.py             # Full CRM (leads, deals, pipeline)
└── memory/
    ├── brand_memory.py          # Brand context storage
    ├── voice_profile.py         # Brand voice training
    └── embedding_index.py        # Semantic search
```

---

## 🔗 Integration with Quay

Marketic is the marketing intelligence engine for **Quay** (Autonomous AI Software Factory):

```typescript
// Quay marketing config
export const MARKETIC_MCP_CONFIG = {
  name: 'marketic',
  command: 'python3',
  args: ['/Users/Subho/marketic/mcp_server.py'],
};
```

---

## ⚡ Sample Campaigns

| Campaign | Tools Chained | Status |
|----------|--------------|--------|
| **Position-and-Attack** | `analyze_competitor` → `analyze_positioning` → `generate_creatives` | ✅ |
| **ROAS Optimizer** | `get_attribution` → `optimize_budget` | ✅ |
| **Creative Engine** | `generate_creatives` → `generate_social_posts` → `build_campaign` | ✅ |
| **Signal Intelligence** | `collect_signals` → `generate_narrative` | ✅ |
| **Ensemble Decision** | `ensemble_vote` → `audit_log` → `hub_sync_contact` | ✅ |

---

## 📈 Differentiation

| Tool | What it does | Marketic advantage |
|------|-------------|-------------------|
| Generic AI | Black-box marketing | **Transparent**: every decision logged with reasoning |
| HubSpot/Marketo | Enterprise platforms | **Open**: ensemble AI that learns from performance |
| Link trackers | Attribution only | **Full stack**: attribution + competitive intel + creative |

---

## License

MIT © Subhajit Das
