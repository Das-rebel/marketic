# Marketic — Marketing Intelligence OS

**AI-native marketing operating system that encodes real performance marketing judgment.**

*Closed-loop: Analyze competitors → Generate counter-variants → Launch campaigns → Measure → Learn*

[![GitHub stars](https://img.shields.io/github/stars/Das-rebel/marketic)](https://github.com/Das-rebel/marketic)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![npm: quay-ai-factory](https://img.shields.io/badge/npm-v0.1.0-purple.svg)](https://www.npmjs.com/package/quay-ai-factory)

---

## 🎯 What Marketic Does

```bash
# Start the MCP server
python3 mcp_server.py

# In another terminal, analyze a competitor
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"analyze_competitor","arguments":{"brand":"HubSpot","category":"marketing automation"}},"id":1}' | python3 mcp_server.py
```

**Output:**
```json
{
  "competitor": "HubSpot",
  "analysis": "HubSpot dominates with all-in-one platform...",
  "confidence": 0.85,
  "analyzed_at": "2026-07-20T14:15:40.171150"
}
```

**Why this is different:** Marketic exposes 32 marketing intelligence tools via MCP (Model Context Protocol), enabling any MCP-compatible agent (including Quay) to call marketing domain functions natively.

---

## 🔌 MCP Server — 32 Tools

Marketic exposes **32 tools** across 7 categories via JSON-RPC 2.0 over stdio:

| Category | Tools | Use Case |
|----------|-------|---------|
| **Competitive Analysis** | `analyze_competitor`, `compare_competitors`, `analyze_positioning` | Competitor research, gap analysis, positioning maps |
| **Creative Generation** | `generate_creatives`, `generate_social_posts`, `generate_seo_content`, `generate_narrative` | Ad copy, social posts, SEO articles, brand stories |
| **Campaign Management** | `build_campaign`, `optimize_budget`, `launch_campaign_ad` | Multi-channel campaign planning, ROAS optimization |
| **Analytics** | `get_attribution`, `collect_signals` | Attribution modeling, market signal collection |
| **Hub Connectors** | `hub_*` (9 tools) | Unified marketing platform integration (WebEngage, HubSpot, etc.) |
| **CRM** | `crm_*` (8 tools) | Lead/deal management, activity logging |
| **Utilities** | `build_utm_url`, `parse_utm_params`, `run_workflow` | URL tracking, workflow orchestration |

### Quick Test

```bash
# List all tools
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | python3 mcp_server.py

# Run a sample campaign suite
python3 run_sample_campaigns.py
```

---

## 🏗️ Architecture

```
Signal → Plan → Execute → Respond → Learn
   ↓        ↓        ↓         ↓        ↓
 Context  Route   Ensemble   Merge    Quality
 Loading   Tier   +Fallback  +Deliver  Tracking
```

**Tiered LLM Routing:**
- Easy task (ad copy): 1 cheap model, ~$0.0001
- Medium task (gap analysis): 2 mid-tier models parallel, ~$0.002
- Hard task (campaign strategy): 3 premium models + confidence voting, ~$0.05

---

## 🚀 Integration with Quay

Marketic is integrated into **Quay** (Autonomous AI Software Factory) as a native MCP tool provider:

```typescript
// Quay's marketing module config (src/server/marketing/config.ts)
export const MARKETIC_MCP_CONFIG: MCPServerConfig = {
  name: 'marketic',
  command: 'python3',
  args: ['/Users/Subho/marketic/mcp_server.py'],
  env: { /* API keys */ },
};
```

**Quay Marketing Routes:**
- `POST /api/marketing/analyze` → `marketic::analyze_competitor`
- `POST /api/marketing/creatives` → `marketic::generate_creatives`
- `POST /api/marketing/campaign` → `marketic::build_campaign` / `launch_campaign_ad`
- `POST /api/marketing/signals` → `marketic::collect_signals`

---

## 📊 Test Results (2026-07-20)

**67 integration tests passing** across Marketic MCP server and Quay API routes:

```
npm test -- tests/integration/
# 43 Marketic MCP tool tests + 24 API route contract tests
```

### Sample Campaigns Verified

| Campaign | Tools Chained | Status |
|----------|--------------|--------|
| **A: Position-and-Attack** | `analyze_competitor` → `analyze_positioning` → `generate_creatives` | ✅ |
| **B: ROAS Optimizer** | `get_attribution` → `optimize_budget` | ✅ |
| **C: Creative-Bomb** | `generate_creatives` → `generate_social_posts` → `build_campaign` | ✅ |
| **D: SEO Content Engine** | `generate_seo_content` → `generate_narrative` | ✅ |

---

## 🛠️ Quick Start

```bash
# Clone
git clone https://github.com/Das-rebel/marketic
cd marketic

# Install dependencies
pip install -e .

# Run MCP server (for use by Quay or other MCP clients)
python3 mcp_server.py

# Or run sample campaigns
python3 run_sample_campaigns.py
```

---

## 📁 Project Structure

```
marketic/
├── mcp_server.py           # MCP stdio server (32 tools)
├── run_sample_campaigns.py  # Sample campaign runner
├── API_DOCUMENTATION.md    # Full API reference
├── marketic/
│   ├── gtm/                # Go-to-market tools
│   │   ├── positioning.py
│   │   ├── narrative.py
│   │   └── ...
│   ├── creative/           # Creative generation
│   │   ├── social_generator.py
│   │   ├── seo_generator.py
│   │   └── ...
│   ├── campaign/           # Campaign management
│   │   ├── builder.py
│   │   ├── budget_router.py
│   │   └── ...
│   ├── analytics/          # Attribution & signals
│   ├── integrations/       # Hub connectors
│   └── crm/               # CRM tools
└── tests/                 # Integration tests
```

---

## ⚙️ Environment Variables

```bash
# LLM API keys (for real AI-powered analysis)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Marketing platform integrations (optional)
HUBSPOT_API_KEY=...
WEBENGAGE_API_KEY=...
CLEVERTAP_ACCOUNT_ID=...
BRAZE_API_KEY=...
MAILCHIMP_API_KEY=...
CLAY_API_KEY=...
```

---

## 📈 Differentiation

| Tool | What it does | Marketic advantage |
|------|-------------|-------------------|
| Icon AI CMO | Black-box autonomous ads | **Transparency**: every decision logged with reasoning |
| HubSpot/Marketo | Enterprise platforms | **Open, learnable** system that gets smarter over time |
| `dub.co` | Link attribution only | Attribution + competitive intel + creative generation |
| `claude-seo` | SEO skills only | Full marketing intelligence, not just SEO |

---

## 📄 Documentation

- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) — Complete 32-tool API reference with examples
- [AGENT_COUNCIL_REPORT.md](./AGENT_COUNCIL_REPORT.md) — Architectural review by multiple AI agents

---

## License

MIT © Subhajit Das
