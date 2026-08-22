# Marketic — Marketing Intelligence OS

**An AI-native marketing operating system with ensemble reasoning and full audit trails.**

Marketic turns any MCP-compatible AI agent into a complete marketing team — competitor analysis, creative generation, campaign execution, multi-platform orchestration, and transparent performance tracking, all with every decision logged.

It ships one core server and a layered module system:

| Layer | Component | What it does |
|-------|-----------|--------------|
| **🧠 Ensemble** | `ensemble/voting.py` | Multi-model AI voting with confidence scoring |
| **📋 Audit** | `ensemble/audit_trail.py` | Full decision logging — model, cost, reasoning, approval |
| **🎨 Creative** | `creative/*` | Ad copy, social posts, SEO content |
| **📣 Campaign** | `campaign/*` | Multi-channel campaign builder + ROAS optimizer |
| **🗺️ GTM** | `gtm/*` | Competitive intel, positioning maps, brand narratives |
| **📡 Signals** | `signals/collectors.py` | PH, HN, Twitter, Reddit intelligence |
| **📊 Analytics** | `analytics/attribution.py` | 5 attribution models |
| **🔗 Hub** | `integrations/unified_adapter.py` | 8+ marketing platforms |
| **👥 CRM** | `crm/__init__.py` | Leads, deals, pipeline |

---

## Quick Start

```bash
# Install
pip install -e .

# Initialize database
python3 init_memory_db.py

# Run MCP server (stdio — works with any MCP client)
python3 mcp_server.py
```

Or import as a Python package:

```python
from marketic.ensemble.voting import EnsembleVoter
from marketic.creative.copy_generator import CopyGenerator

voter = EnsembleVoter()
result = voter.vote(task_type="competitor_analysis", prompt="Analyze Drift's positioning")

gen = CopyGenerator()
variants = await gen.generate_variants(request)
```

---

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | Premium AI models (ox-alpha, gemini, qwen) | — |
| `OPENAI_API_KEY` | Fallback AI | — |
| `OPENCODE_GO_TOKEN` | **FREE** ox-alpha via OpenCode Go | — |
| `WEBENGAGE_API_KEY` | Marketing platform integrations | — |
| `HUBSPOT_API_KEY` | CRM + marketing hub | — |
| `CLAY_API_KEY` | Prospect data enrichment | — |

> 🔒 Set secrets in environment — never hardcode in the repo.

---

## How It Works

**Simple tasks** → one cheap model (~$0.0001)
```
generate_creatives → deepseek flash → variant
```

**Complex tasks** → ensemble voting (~$0.05)
```
campaign_strategy → ox-alpha + qwen + gemini → vote → consensus → decision
```

**Every call is logged:**
```json
{
  "audit_id": "a1b2c3d4",
  "action": "generate_creatives",
  "model": "stealth/ox-alpha",
  "cost": 0.0,
  "confidence": 0.87,
  "reasoning_chain": ["[ox-alpha] Lead with transformation..."],
  "human_approved": null
}
```

Query logs: `audit_get_log()`, `audit_get_cost_summary()`

---

## MCP Tools — 43 Total

| Category | Tools |
|----------|-------|
| **GTM** | `analyze_competitor`, `compare_competitors`, `analyze_positioning` |
| **Creative** | `generate_creatives`, `generate_social_posts`, `generate_seo_content` |
| **Campaign** | `build_campaign`, `optimize_budget` |
| **Narrative** | `generate_narrative` |
| **Signals** | `collect_signals` |
| **Analytics** | `get_attribution` |
| **Hub** | `hub_health_check`, `hub_sync_contact`, `hub_send_campaign`, `hub_broadcast_event`, `hub_create_segment`, `hub_search_prospects`, `hub_send_transactional`, `hub_list_platforms`, `hub_get_dashboard` |
| **CRM** | `crm_create_lead`, `crm_create_deal`, `crm_move_deal`, `crm_log_activity`, `crm_get_dashboard`, `crm_search_leads`, `crm_get_pipeline`, `crm_get_timeline` |
| **Ensemble** | `ensemble_vote` |
| **Audit** | `audit_log`, `audit_get_log`, `audit_get_cost_summary` |
| **Utilities** | `build_utm_url`, `parse_utm_params`, `run_workflow` |

---

## Ensemble AI — Model Tiers

| Task | Model(s) | Est. Cost |
|------|----------|-----------|
| Ad copy | `deepseek/deepseek-v4-flash` | ~$0.0001 |
| Social posts | `google/gemini-3.6-flash` | ~$0.001 |
| Competitor analysis | `stealth/ox-alpha` | **FREE** |
| Campaign strategy | `ox-alpha` + `qwen3.7-max` + `gemini-3.6-flash` | ~$0.05 |

**Free tier:** ox-alpha via OpenCode Go (`stealth/ox-alpha`) — no API key needed.

---

## Repository Layout

```
marketic/
├── mcp_server.py                 # MCP stdio server (43 tools)
├── init_memory_db.py              # SQLite setup
├── ensemble/
│   ├── voting.py                 # Multi-model ensemble voting
│   └── audit_trail.py           # Full AI decision logging
├── creative/
│   ├── copy_generator.py         # Multi-channel ad copy
│   ├── social_generator.py      # Platform-specific social posts
│   └── seo_generator.py         # SEO content + meta tags
├── campaign/
│   ├── builder.py              # Full campaign generation
│   └── budget_router.py         # ROAS-based budget rebalancing
├── gtm/
│   ├── competitive.py           # Deep competitive analysis
│   ├── positioning.py           # Market positioning maps
│   └── narrative.py             # Brand stories + thought leadership
├── signals/
│   └── collectors.py            # PH, HN, Twitter, Reddit
├── analytics/
│   └── attribution.py            # 5 multi-touch models
├── integrations/
│   └── unified_adapter.py        # 8+ platform hub
├── crm/
│   └── __init__.py              # Leads, deals, activities
└── memory/
    ├── brand_memory.py          # Brand context storage
    ├── voice_profile.py         # Brand voice training
    └── embedding_index.py       # Semantic search
```

---

## Audit Trail — Transparency by Default

Marketic logs every AI decision. No black boxes.

```bash
# See all decisions for a brand
audit_get_log(brand_id="acme", limit=100)

# Get cost breakdown
audit_get_cost_summary(start_date="2026-08-01")
```

Every log entry captures:
- **Model used** — track which model made the call
- **Cost** — real-time spend tracking
- **Confidence** — ensemble voting confidence score
- **Reasoning chain** — what each model said
- **Human approval** — null (auto), true (approved), false (rejected)

---

## Campaign Example

```python
# Build and launch a multi-channel campaign
campaign = await builder.build(
    name="Q3 Product Launch",
    objective=CampaignObjective.PURCHASES,
    target_audience="SMB founders",
    channels=["email", "social", "paid_search"],
    timeline_weeks=6,
    total_budget=25000,
)

# Optimize budget based on attribution
allocations = await budget_router.rebalance(
    total_budget=25000,
    channel_data={"email": {"spend": 5000, "roas": 4.2}, "social": {"spend": 10000, "roas": 2.1}},
    strategy="roas_optimized",
)
```

---

## Integration

Marketic works as:
- **MCP server** — stdio JSON-RPC, works with any MCP client
- **Python package** — import modules directly
- **Quay integration** — drop-in marketing intelligence engine

```typescript
// Quay config
const MARKETIC_MCP = {
  name: 'marketic',
  command: 'python3',
  args: ['/path/to/marketic/mcp_server.py'],
};
```

---

MIT © Subho Das
