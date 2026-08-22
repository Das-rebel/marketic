# Marketic MCP Server

> **32 marketing intelligence tools** exposed via the Model Context Protocol (MCP) for AI coding assistants.

[![npm version](https://img.shields.io/npm/v/marketic-mcp)](https://www.npmjs.com/package/marketic-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

A standalone MCP server that gives AI coding assistants **real marketing superpowers**:

- **Competitor Analysis** - Analyze any brand's positioning, pricing, marketing approach
- **Ad Creative Generation** - Generate 5 variants of ad copy for any channel (Meta, Google, LinkedIn, etc.)
- **Campaign Planning** - Build multi-channel campaigns with budget allocation
- **Social Media** - Generate platform-specific posts for LinkedIn, Twitter, Instagram
- **SEO Content** - Create SEO-optimized blog posts and landing page copy
- **Attribution Modeling** - Multi-touch attribution with Linear, Time-Decay, Position-Decay
- **Budget Optimization** - Route budget to best-performing channels using ROAS data
- **HubSpot CRM** - Full CRM: contacts, deals, workflows, email campaigns
- **Signal Collection** - Aggregate trends from Product Hunt, Twitter, Google Trends

## Installation

```bash
npm install -g marketic-mcp
```

## Quick Start

```bash
# Start the MCP server (stdio mode)
marketic-mcp

# Test it directly
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"analyze_competitor","arguments":{"brand":"HubSpot","category":"marketing automation"}},"id":1}' | python3 mcp_server.py
```

## MCP Tools (32 total)

| Category | Tools |
|----------|-------|
| **Competitor Intel** | `analyze_competitor`, `compare_competitors` |
| **Creative Generation** | `generate_creatives`, `generate_social_posts`, `generate_seo_content` |
| **Campaign Management** | `build_campaign`, `optimize_budget`, `run_pacing_model` |
| **Attribution** | `run_attribution_model`, `calculate_roi`, `simulate_funnels` |
| **Analytics** | `analyze_performance`, `ab_analyze`, `segment_audience`, `predict_ltv` |
| **HubSpot CRM** | `hub_sync_contact`, `hub_broadcast_event`, `hub_send_campaign`, `hub_search_prospects`, `hub_create_segment`, `hub_send_transactional` |
| **General CRM** | `crm_create_lead`, `crm_create_deal`, `crm_move_deal`, `crm_log_activity` |
| **Workflows** | `run_workflow` |
| **Collection** | `collect_signals` |
| **Optimization** | `optimize_ctr`, `model_churn_risk`, `credit_allocate` |

## Configuration

```bash
# Optional: a3m-router for LLM calls (faster, cached)
export A3M_BASE_URL="http://localhost:8787/v1"
export GROQ_API_KEY="gsk_..."

# Or direct Groq
export GROQ_API_KEY="gsk_..."
```

## Use with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "marketic": {
      "command": "marketic-mcp"
    }
  }
}
```

## Use with Cursor

Settings → MCP Servers → Add new:

```
Name: Marketic
Command: marketic-mcp
```

## Use with Windsurf

Windsurf Settings → MCP → Add server:

```
Name: Marketic  
Command: marketic-mcp
```

## Architecture

```
AI Assistant (Claude/Cursor/Windsurf)
        ↓ MCP stdio
marketic-mcp (npm package)
        ↓
Python MCP Server → LLM Router → Groq/a3m-router
                         ↓
               Marketic Foundation Models
               (Attribution, Budget, Analytics, Copy)
```

## License

MIT - [github.com/Das-rebel/marketic](https://github.com/Das-rebel/marketic)
