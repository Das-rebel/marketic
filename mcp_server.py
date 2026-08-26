#!/usr/bin/env python3
"""
Marketic MCP Server — Exposes marketing domain tools via MCP stdio protocol.

Quay spawns this as a child process and communicates via JSON-RPC over stdin/stdout.

Run standalone:  python3 mcp_server.py
Via Quay:        spawned automatically by quay/src/server/marketing/config.ts
"""

import sys
import json
from dataclasses import asdict
import asyncio
import traceback
from typing import Any, Dict, List, Optional

# ─── MCP Protocol Constants ───────────────────────────────────

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "marketic"
SERVER_VERSION = "1.0.0"

# ─── Tool Definitions ─────────────────────────────────────────

TOOLS = [
    # Signal Calibration Tools
    {
        "name": "track_signal",
        "description": "Record a signal prediction for later calibration tracking. Once tracked, you can call resolve_signal when the outcome is known to measure prediction accuracy (Brier score). Used to build calibration over time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "source": {"type": "string"},
                "signal_type": {"type": "string"},
                "url": {"type": "string"},
                "engagement_score": {"type": "number"},
                "topics": {"type": "array", "items": {"type": "string"}},
                "metadata": {"type": "object"},
            },
            "required": ["title", "source", "signal_type", "url", "engagement_score"],
        },
    },
    {
        "name": "get_calibration_report",
        "description": "Get the signal calibration report: number of predictions, Brier score (lower=better), resolved vs pending breakdown, and per-source accuracy. Shows whether Marketic's signal sources are reliable.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "source": {"type": "string"},
            },
        },
    },
    {
        "name": "resolve_signal",
        "description": "Resolve a previously tracked signal with its actual outcome (YES/NO/PARTIAL). Used to close the calibration loop and improve future signal quality.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "signal_id": {"type": "string"},
                "actual_outcome": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["signal_id", "actual_outcome"],
        },
    },
    # GTM Tools
    {
        "name": "analyze_competitor",
        "description": "Deep-dive competitive analysis: positioning, messaging, ad strategy, audience targeting, strengths, weaknesses, and exploitable gaps.",
        "inputSchema": {
            "type": "object",
            "properties": {"brand": {"type": "string"}, "category": {"type": "string", "default": ""}},
            "required": ["brand"],
        },
    },
    {
        "name": "compare_competitors",
        "description": "Compare your product against multiple competitors. Returns feature comparison matrix, price comparison, and strategic recommendations.",
        "inputSchema": {
            "type": "object",
            "properties": {"your_product": {"type": "string"}, "competitors": {"type": "array", "items": {"type": "string"}}},
            "required": ["your_product", "competitors"],
        },
    },
    {
        "name": "analyze_positioning",
        "description": "Analyze your brand's market positioning against competitors. Returns positioning map, differentiation strategy, and messaging framework.",
        "inputSchema": {
            "type": "object",
            "properties": {"brand": {"type": "string"}, "product": {"type": "string", "default": ""}, "industry": {"type": "string", "default": ""}},
            "required": ["brand"],
        },
    },
    # Creative Tools
    {
        "name": "generate_creatives",
        "description": "Generate ad copy variants across channels (Google, Meta, LinkedIn, etc.). Each variant includes headline, description, CTA, hooks, confidence score, and performance prediction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "product_description": {"type": "string"},
                "channel": {"type": "string", "enum": ["google_search", "google_display", "meta_feed", "linkedin_sponsored", "email"], "default": "meta_feed"},
                "objective": {"type": "string", "enum": ["awareness", "consideration", "conversion"], "default": "conversion"},
                "target_audience": {"type": "string", "default": ""},
                "key_benefits": {"type": "array", "items": {"type": "string"}, "default": []},
                "num_variants": {"type": "integer", "default": 5, "minimum": 1, "maximum": 50},
                "tone": {"type": "string", "enum": ["persuasive", "emotional", "logical", "urgent", "friendly"], "default": "persuasive"},
            },
            "required": ["product_name", "product_description"],
        },
    },
    {
        "name": "generate_social_posts",
        "description": "Generate platform-specific social media posts (LinkedIn, X/Twitter, Instagram, Facebook). Supports threads, single posts, and multi-format content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "platform": {"type": "string", "enum": ["linkedin", "twitter", "instagram", "facebook"], "default": "linkedin"},
                "format": {"type": "string", "enum": ["post", "thread", "carousel", "story"], "default": "post"},
                "tone": {"type": "string", "default": "professional"},
                "length": {"type": "integer", "default": 1, "minimum": 1, "maximum": 20},
                "hashtags": {"type": "boolean", "default": True},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "generate_seo_content",
        "description": "Generate SEO-optimized content including meta titles, descriptions, headers, and FAQs for target keywords.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_keyword": {"type": "string"},
                "content_type": {"type": "string", "enum": ["landing_page", "blog_post", "product_page", "faq"], "default": "blog_post"},
                "word_count": {"type": "integer", "default": 1500, "minimum": 300, "maximum": 5000},
                "competitor_url": {"type": "string", "default": ""},
            },
            "required": ["target_keyword"],
        },
    },
    # Campaign Tools
    {
        "name": "build_campaign",
        "description": "Build a complete multi-channel campaign strategy with channel-specific tactics, budgets, and timelines.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_name": {"type": "string"},
                "objective": {"type": "string", "enum": ["awareness", "lead_generation", "conversion", "retention"]},
                "target_audience": {"type": "string"},
                "channels": {"type": "array", "items": {"type": "string"}, "default": ["email", "social"]},
                "duration_weeks": {"type": "integer", "default": 4},
                "total_budget": {"type": "number", "default": 10000},
            },
            "required": ["campaign_name", "objective"],
        },
    },
    {
        "name": "optimize_budget",
        "description": "Optimize budget allocation across marketing channels based on historical ROAS data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "total_budget": {"type": "number"},
                "current_allocation": {"type": "object", "description": "JSON of channel -> amount"},
                "channel_performance": {"type": "object", "description": "JSON of channel -> {roas, conversions}"},
                "strategy": {"type": "string", "enum": ["roas_optimized", "conversion_focused", "awareness_focused", "balanced"], "default": "roas_optimized"},
            },
            "required": ["total_budget", "current_allocation", "channel_performance"],
        },
    },
    {
        "name": "launch_campaign_ad",
        "description": "⚠️ REQUIRES APPROVAL. Launch a campaign ad via Composio integration (Meta, LinkedIn, Google Ads).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string", "enum": ["meta", "linkedin", "google", "hubspot", "salesforce"]},
                "campaign_name": {"type": "string"},
                "budget_daily": {"type": "number", "default": 50},
                "ad_creative": {"type": "string", "description": "JSON string of ad creative"},
                "targeting": {"type": "string", "default": "{}", "description": "JSON string of targeting params"},
            },
            "required": ["platform", "campaign_name"],
        },
    },
    # Signal & Analytics Tools
    {
        "name": "collect_signals",
        "description": "Collect marketing signals from Product Hunt, Hacker News, Twitter, Reddit for a brand.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {"type": "string"},
                "days": {"type": "integer", "default": 7},
                "sources": {"type": "array", "items": {"type": "string"}, "default": ["product_hunt", "hacker_news", "twitter", "reddit"]},
            },
            "required": ["brand"],
        },
    },
    {
        "name": "get_attribution",
        "description": "Calculate multi-touch attribution across marketing channels using various models.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel_points": {"type": "array", "description": "Array of {channel, touchpoints, conversion_value}"},
                "model": {"type": "string", "enum": ["first_touch", "last_touch", "linear", "time_decay", "position_based"], "default": "linear"},
            },
            "required": ["channel_points"],
        },
    },
    {
        "name": "generate_narrative",
        "description": "Generate brand narrative, stories, and messaging frameworks for marketing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "narrative_type": {"type": "string", "enum": ["brand_story", "founder_story", "product_story", "thought_leadership", "industry_analysis"]},
                "brand": {"type": "string"},
                "industry": {"type": "string", "default": ""},
                "product": {"type": "string", "default": ""},
            },
            "required": ["narrative_type", "brand"],
        },
    },
    # Marketing Hub Tools
    {
        "name": "hub_health_check",
        "description": "Check health status of ALL connected marketing platforms. Returns connection status and capabilities.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "hub_broadcast_event",
        "description": "Track an event across ALL connected marketing platforms simultaneously.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_name": {"type": "string"},
                "contact_id": {"type": "string"},
                "properties": {"type": "object", "default": {}},
                "revenue": {"type": "number", "default": 0},
            },
            "required": ["event_name", "contact_id"],
        },
    },
    {
        "name": "hub_sync_contact",
        "description": "Sync a contact to ALL connected marketing platforms. Creates/updates profile across WebEngage, HubSpot, CleverTap, Braze, Mailchimp, etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string", "default": ""},
                "first_name": {"type": "string", "default": ""},
                "last_name": {"type": "string", "default": ""},
                "company": {"type": "string", "default": ""},
                "lifecycle_stage": {"type": "string", "enum": ["lead", "mql", "sql", "opportunity", "customer", "churned"], "default": "lead"},
                "attributes": {"type": "object", "default": {}},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["contact_id", "email"],
        },
    },
    {
        "name": "hub_send_campaign",
        "description": "Send a marketing campaign via the best available platform. Routes to Mailchimp, HubSpot, WebEngage, Braze, or CleverTap.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_name": {"type": "string"},
                "channel": {"type": "string", "enum": ["email", "sms", "push", "whatsapp", "in_app"], "default": "email"},
                "subject": {"type": "string", "default": ""},
                "content_html": {"type": "string", "default": ""},
                "segment_name": {"type": "string", "default": "all"},
                "preferred_platform": {"type": "string", "default": ""},
            },
            "required": ["campaign_name"],
        },
    },
    {
        "name": "hub_get_dashboard",
        "description": "Get unified analytics dashboard across ALL connected marketing platforms. Aggregates metrics from WebEngage, CleverTap, Mixpanel, HubSpot, Braze, etc.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "hub_search_prospects",
        "description": "Search for prospects using Clay data enrichment. Returns enriched company/contact data including title, company size, tech stack, funding, and social profiles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
            },
            "required": ["query"],
        },
    },
    {
        "name": "hub_create_segment",
        "description": "Create an audience segment across ALL connected marketing platforms.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "conditions": {"type": "array", "items": {"type": "object"}, "default": []},
                "description": {"type": "string", "default": ""},
            },
            "required": ["name"],
        },
    },
    {
        "name": "hub_send_transactional",
        "description": "Send a transactional message (single contact) via the best platform for the channel.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string"},
                "channel": {"type": "string", "enum": ["email", "sms", "push", "whatsapp", "in_app"], "default": "email"},
                "title": {"type": "string", "default": ""},
                "body": {"type": "string"},
                "deep_link": {"type": "string", "default": ""},
            },
            "required": ["contact_id", "body"],
        },
    },
    {
        "name": "hub_list_platforms",
        "description": "List all supported marketing platforms and their capabilities. Returns platform features, supported channels, and connection status.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # CRM Tools
    {
        "name": "crm_create_lead",
        "description": "Create a new CRM lead from marketing data. Stores lead with email, name, company, source, and scoring data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "first_name": {"type": "string", "default": ""},
                "last_name": {"type": "string", "default": ""},
                "phone": {"type": "string", "default": ""},
                "company": {"type": "string", "default": ""},
                "job_title": {"type": "string", "default": ""},
                "source": {"type": "string", "enum": ["organic", "paid", "referral", "social", "cold_outreach"], "default": "organic"},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["email"],
        },
    },
    {
        "name": "crm_create_deal",
        "description": "Create a new deal/opportunity from a lead. Sets deal value, stage, and links to lead.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number", "default": 0},
                "stage": {"type": "string", "enum": ["lead", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"], "default": "lead"},
                "lead_id": {"type": "string", "default": ""},
                "owner_id": {"type": "string", "default": ""},
            },
            "required": ["name"],
        },
    },
    {
        "name": "crm_move_deal",
        "description": "Move a deal to a new pipeline stage. Updates probability and logs stage history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "string"},
                "new_stage": {"type": "string", "enum": ["lead", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]},
            },
            "required": ["deal_id", "new_stage"],
        },
    },
    {
        "name": "crm_log_activity",
        "description": "Log an activity (call, email, meeting, note) on a lead or deal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string"},
                "activity_type": {"type": "string", "enum": ["call", "email", "meeting", "note", "task", "campaign"]},
                "subject": {"type": "string", "default": ""},
                "notes": {"type": "string", "default": ""},
                "duration_minutes": {"type": "integer", "default": 0},
            },
            "required": ["entity_id", "activity_type"],
        },
    },
    {
        "name": "crm_get_dashboard",
        "description": "Get CRM dashboard with lead/deal pipeline metrics.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "crm_search_leads",
        "description": "Search CRM leads by name, email, or company.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10, "maximum": 50},
            },
            "required": ["query"],
        },
    },
    {
        "name": "crm_get_pipeline",
        "description": "Get deal pipeline summary with values per stage.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "crm_get_timeline",
        "description": "Get timeline of all activities and stage changes for a lead or deal.",
        "inputSchema": {
            "type": "object",
            "properties": {"entity_id": {"type": "string"}},
            "required": ["entity_id"],
        },
    },
    # Workflow & UTM Tools
    {
        "name": "build_utm_url",
        "description": "Build a UTM-tagged URL for campaign tracking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "base_url": {"type": "string"},
                "source": {"type": "string"},
                "medium": {"type": "string"},
                "campaign": {"type": "string"},
                "content": {"type": "string", "default": ""},
                "term": {"type": "string", "default": ""},
            },
            "required": ["base_url", "source", "medium", "campaign"],
        },
    },
    {
        "name": "parse_utm_params",
        "description": "Extract UTM parameters from a URL.",
        "inputSchema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "run_workflow",
        "description": "Execute a multi-step marketing workflow. Chain operations: sync_contact → create_segment → send_campaign.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string"},
                "name": {"type": "string", "default": ""},
                "steps": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "step_id": {"type": "string"},
                        "action": {"type": "string"},
                        "params": {"type": "object"},
                        "on_success": {"type": "string", "default": ""},
                        "on_failure": {"type": "string", "default": ""},
                    },
                    "required": ["step_id", "action", "params"],
                }},
                "first_step": {"type": "string"},
            },
            "required": ["workflow_id", "steps", "first_step"],
        },
    },
    {
        "name": "generate_brief",
        "description": "Generate a self-contained campaign brief (handoff artifact) for any brand execution agent: positioning, budget split, posting windows, resolved BrandTokens, and execution contract. The agent can execute without calling back.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_name": {"type": "string"},
                "objective": {"type": "string", "enum": ["awareness", "consideration", "conversion", "lead_generation", "retention"]},
                "product_name": {"type": "string"},
                "product_description": {"type": "string"},
                "target_audience": {"type": "string", "default": ""},
                "channels": {"type": "array", "items": {"type": "string"}, "default": ["social", "email"]},
                "total_budget": {"type": "number", "default": 10000},
                "duration_weeks": {"type": "integer", "default": 4},
                "key_benefits": {"type": "array", "items": {"type": "string"}, "default": []},
                "brand_tokens": {"type": "object", "description": "Brand kit: name, colors, font, handle, voice_notes"},
                "channel_performance": {"type": "object", "description": "channel -> {spend, roas, contribution_margin, conversions}"},
                "positioning_summary": {"type": "string", "default": ""},
                "competitor_insights": {"type": "string", "default": ""},
            },
            "required": ["campaign_name", "objective", "product_name", "product_description"],
        },
    },
    {
        "name": "signal_fanout",
        "description": "Parallel multi-source signal search (Product Hunt, HN, Twitter, Reddit, Polymarket) with cross-source engagement normalization. Returns one synthesized brief with consensus themes and money outliers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "default": ""},
                "sources": {"type": "array", "items": {"type": "string"}, "default": []},
                "limit_per_source": {"type": "integer", "default": 25},
            },
        },
    },
    {
        "name": "analyze_competitor_ad",
        "description": "Deconstruct a competitor ad (image/video frame URL or local path) via VLM: hook, pacing, psychological triggers, CTA, counter-angles. Falls back to copy heuristics when no vision backend available. Use derive=true to aggregate multiple ads into a counter-brief for generate_creatives.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path_or_url": {"type": "string", "default": ""},
                "transcript": {"type": "string", "default": ""},
                "caption": {"type": "string", "default": ""},
                "batch": {"type": "array", "items": {"type": "object"}, "description": "list of {image_path_or_url, transcript, caption}"},
                "derive": {"type": "boolean", "default": False, "description": "return aggregated counter-brief instead of raw breakdowns"},
            },
        },
    },
    {
        "name": "breakdown_ad",
        "description": "Break down a competitor ad into its structural components: hook, offer, call-to-action, emotional triggers, pacing, and format. Works from a URL (uses Ollama vision model locally if available, falls back to cloud vision then heuristic parsing) or from raw ad copy text. Optionally enrich with brand context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ad_url_or_text": {"type": "string", "description": "URL to competitor ad image/video, or raw ad copy text if no URL"},
                "brand_name": {"type": "string", "default": "", "description": "Name of the competitor brand for context"},
                "analysis_depth": {"type": "string", "enum": ["quick", "standard", "deep"], "default": "standard", "description": "Depth of analysis: quick (heuristic only), standard (VLM if available), deep (full VLM with extended output)"},
            },
            "required": ["ad_url_or_text"],
        },
    },
    {
        "name": "ask_marketic",
        "description": "Master router - one entry point for Marketic. Describe what you need in plain language (e.g. 'what's moving in AI markets', 'allocate my budget', 'deconstruct this competitor ad') and it routes to the right specialist tool(s). Use route_only=true to preview routing without executing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Natural-language marketing question or task"},
                "route_only": {"type": "boolean", "default": False},
                "arguments": {"type": "object", "description": "Optional arguments passed through to the routed tool"},
            },
            "required": ["question"],
        },
    },
    {
        "name": "run_prospect_loop",
        "description": "Signal-driven prospecting (JoeCRM pattern): discover prospects matching a niche, enrich with live market signals, auto-draft personalized outreach, insert scored leads into CRM. Degrades to signal-derived prospects when Serper key absent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "niche_query": {"type": "string", "description": "Who to prospect, e.g. 'D2C skincare brands founder'"},
                "market_query": {"type": "string", "description": "Market topic for signal enrichment"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["niche_query"],
        },
    },
    {
        "name": "distill_learnings",
        "description": "Promote recurring audit-trail patterns into brand learnings; optionally capture an explicit rule; export brain/<brand>.md markdown for human review.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "default": "default"},
                "capture_rule": {"type": "string", "description": "If set, capture this rule instead of distilling"},
                "category": {"type": "string", "default": "general"},
                "min_occurrences": {"type": "integer", "default": 3},
                "export_brain": {"type": "boolean", "default": True},
            },
        },
    },
    {
        "name": "search_fb_ads",
        "description": "Search Facebook Ads Library for REAL competitor ad creatives, copy and delivery data (ground truth, not VLM guessing). Requires FB_ACCESS_TOKEN env var.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {"type": "string", "description": "Advertiser/brand to search"},
                "country": {"type": "string", "default": "ALL"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["brand_name"],
        },
    },
    # Ensemble & Audit Tools
    {
        "name": "ensemble_vote",
        "description": "Run ensemble voting across multiple AI models. Selects optimal model tier based on task complexity. Returns consensus decision with confidence score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "enum": ["ad_copy", "social_post", "keyword_research", "competitor_analysis", "campaign_strategy", "brand_voice_analysis", "briefing_generation"]},
                "prompt": {"type": "string"},
                "context": {"type": "object", "default": {}},
                "models": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["task_type", "prompt"],
        },
    },
    {
        "name": "audit_log",
        "description": "Log an AI marketing action with full audit trail. Records model, cost, confidence, reasoning chain, and human approval status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "model": {"type": "string", "default": ""},
                "input_tokens": {"type": "integer", "default": 0},
                "output_tokens": {"type": "integer", "default": 0},
                "cost": {"type": "number", "default": 0.0},
                "confidence": {"type": "number", "default": 0.0},
                "reasoning_chain": {"type": "array", "items": {"type": "string"}, "default": []},
                "result_summary": {"type": "string", "default": ""},
                "human_approved": {"type": "boolean", "default": None},
                "brand_id": {"type": "string", "default": ""},
                "metadata": {"type": "object", "default": {}},
            },
            "required": ["action"],
        },
    },
    {
        "name": "audit_get_log",
        "description": "Retrieve audit log entries with filtering by brand, action, and date range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "string", "default": ""},
                "action": {"type": "string", "default": ""},
                "start_date": {"type": "string", "default": ""},
                "end_date": {"type": "string", "default": ""},
                "limit": {"type": "integer", "default": 100},
            },
        },
    },
    {
        "name": "audit_get_cost_summary",
        "description": "Get cost summary by model and action type for a date range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "string", "default": ""},
                "start_date": {"type": "string", "default": ""},
                "end_date": {"type": "string", "default": ""},
            },
        },
    },
    # Publishing layer
    {
        "name": "schedule_content",
        "description": "Schedule a social media post to a platform via Postiz or direct API. Takes platform, content text, optional media URLs, scheduled time (ISO datetime), and hashtags. Falls back to PostizPublisher.publish_post() when platform=postiz.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string", "enum": ["postiz", "instagram", "linkedin", "twitter"]},
                "content_text": {"type": "string"},
                "media_urls": {"type": "array", "items": {"type": "string"}, "default": []},
                "scheduled_time": {"type": "string", "description": "ISO datetime string, e.g. 2025-01-15T10:00:00"},
                "hashtags": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["platform", "content_text"],
        },
    },
    {
        "name": "get_upcoming_posts",
        "description": "Get all scheduled posts for the upcoming N days from the content calendar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string", "default": ""},
                "days": {"type": "integer", "default": 7},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "optimize_hashtags",
        "description": "Get optimized hashtags for a social media post. Returns a mix of trending and content-specific hashtags, respecting platform limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content_text": {"type": "string"},
                "platform": {"type": "string", "default": "instagram"},
                "limit": {"type": "integer", "default": 15},
            },
            "required": ["content_text"],
        },
    },
    # UGC layer
    {
        "name": "curate_ugc",
        "description": "Curate user-generated content for a given hashtag. Discovers posts via hashtag monitoring, filters by aesthetic score, and returns a list sorted by combined relevance + aesthetic score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hashtag": {"type": "string"},
                "platform": {"type": "string", "default": "instagram"},
                "limit": {"type": "integer", "default": 10},
                "min_aesthetic_score": {"type": "number", "default": 0.4},
            },
            "required": ["hashtag"],
        },
    },
    {
        "name": "request_ugc_permission",
        "description": "Request permission from a UGC creator to repost their content. Sends a DM template (English or Indonesian) via platform API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content_url": {"type": "string"},
                "platform": {"type": "string"},
                "message": {"type": "string", "default": ""},
            },
            "required": ["content_url", "platform"],
        },
    },
    {
        "name": "track_ugc",
        "description": "Track UGC repost performance: reach, likes, comments, saves, and shares across platforms.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repost_id": {"type": "string"},
                "platform": {"type": "string"},
            },
            "required": ["repost_id", "platform"],
        },
    },
    # Creative / design layer
    {
        "name": "render_template",
        "description": "Render a brand design template to a Paper MCP script or JSON layer spec. Accepts a template name, brand tokens (name, primary, background, accent, secondary, font, handle, tagline), and optional content overrides. Returns HTML/layers or a placeholders list if required content is missing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_name": {"type": "string"},
                "brand": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "primary": {"type": "string"},
                        "background": {"type": "string"},
                        "accent": {"type": "string"},
                        "secondary": {"type": "string"},
                        "font": {"type": "string"},
                        "handle": {"type": "string"},
                        "tagline": {"type": "string"},
                    },
                    "required": ["name", "primary", "background", "accent", "secondary", "font", "handle"],
                },
                "content_overrides": {"type": "object", "default": {}},
            },
            "required": ["template_name", "brand"],
        },
    },
]


# ─── Tool Handlers ────────────────────────────────────────────

async def handle_analyze_competitor(args):
    from gtm.competitive import CompetitiveIntelligence
    ci = CompetitiveIntelligence()
    return await ci.analyze_competitor(competitor_name=args["brand"], category=args.get("category", ""))


async def handle_compare_competitors(args):
    from gtm.competitive import CompetitiveIntelligence
    ci = CompetitiveIntelligence()
    return await ci.compare_with_competitors(your_product=args["your_product"], competitors=args["competitors"])


async def handle_generate_creatives(args):
    from creative.copy_generator import CopyGenerator, AdCopyRequest, AdChannel, AdObjective
    gen = CopyGenerator()
    request = AdCopyRequest(
        product_name=args["product_name"],
        product_description=args["product_description"],
        channel=AdChannel(args.get("channel", "meta_feed")),
        objective=AdObjective(args.get("objective", "conversion")),
        target_audience=args.get("target_audience", ""),
        key_benefits=args.get("key_benefits", []),
        num_variants=args.get("num_variants", 5),
        tone=args.get("tone", "persuasive"),
    )
    variants = await gen.generate_variants(request)
    return {"variants": [{"variant_id": v.variant_id, "headline": v.headline, "description": v.description, "cta": v.cta, "confidence": v.confidence} for v in variants], "count": len(variants)}


async def handle_generate_social_posts(args):
    from creative.social_generator import SocialGenerator, SocialContentRequest, SocialPlatform, ContentFormat
    gen = SocialGenerator()
    # Map format string to enum; 'post' -> SINGLE_POST, 'thread' -> THREAD, etc.
    format_str = args.get("format", "post")
    format_map = {
        "post": ContentFormat.SINGLE_POST,
        "single_post": ContentFormat.SINGLE_POST,
        "thread": getattr(ContentFormat, "THREAD", ContentFormat.SINGLE_POST),
        "carousel": getattr(ContentFormat, "CAROUSEL", ContentFormat.SINGLE_POST),
        "story": getattr(ContentFormat, "STORY", ContentFormat.SINGLE_POST),
    }
    fmt = format_map.get(format_str, ContentFormat.SINGLE_POST)
    length = args.get("length", 1)
    request = SocialContentRequest(
        topic=args["topic"],
        platform=SocialPlatform(args.get("platform", "linkedin")),
        format=fmt,
        tone=args.get("tone", "professional"),
        num_options=max(length, 1),
        thread_length=max(length, 3) if format_str == "thread" else 1,
        include_hashtags=args.get("hashtags", True),
    )
    posts = await gen.generate(request)
    return {"posts": [{"post_id": p.post_id, "content": p.content, "hashtags": p.hashtags} for p in posts], "count": len(posts)}


async def handle_generate_seo_content(args):
    from creative.seo_generator import SEOGenerator, SEOContentRequest
    gen = SEOGenerator()
    keyword = args.get("target_keyword", args.get("keyword", ""))
    request = SEOContentRequest(
        keyword=keyword,
        content_type=args.get("content_type", "blog_post"),
        target_length=args.get("word_count", 1500),
    )
    result = await gen.generate(request)
    # Convert SEOContent object to dict if needed
    if isinstance(result, dict):
        return result
    return {k: v for k, v in vars(result).items() if not k.startswith('_')}


async def handle_build_campaign(args):
    from campaign.builder import CampaignBuilder, CampaignObjective
    builder = CampaignBuilder()
    name = args.get("campaign_name", args.get("name", "Untitled Campaign"))
    # Map common objective strings to valid enum values
    obj_str = args.get("objective", "awareness")
    obj_map = {
        "awareness": CampaignObjective.AWARENESS,
        "traffic": CampaignObjective.TRAFFIC,
        "lead_generation": CampaignObjective.LEAD_GENERATION,
        "app_installs": CampaignObjective.APP_INSTALLS,
        "purchases": CampaignObjective.PURCHASES,
        "brand_loyalty": CampaignObjective.BRAND_LOYALTY,
        "conversion": CampaignObjective.PURCHASES,
        "retention": CampaignObjective.BRAND_LOYALTY,
    }
    obj_enum = obj_map.get(obj_str, CampaignObjective.AWARENESS)
    campaign = await builder.build(
        name=name,
        objective=obj_enum,
        target_audience=args.get("target_audience", ""),
        channels=args.get("channels", ["email", "social"]),
        timeline_weeks=args.get("duration_weeks", 4),
        total_budget=args.get("total_budget", 10000),
    )
    # Convert Campaign object to dict with deep serialization
    def deep_serialize(obj):
        if isinstance(obj, dict):
            return {k: deep_serialize(v) for k, v in obj.items() if not str(k).startswith('_')}
        elif isinstance(obj, list):
            return [deep_serialize(item) for item in obj]
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        elif hasattr(obj, '__dict__'):  # Custom object
            return {k: deep_serialize(v) for k, v in vars(obj).items() if not str(k).startswith('_')}
        else:
            return obj
    if isinstance(campaign, dict):
        return deep_serialize(campaign)
    return deep_serialize(campaign)


async def handle_optimize_budget(args):
    from campaign.budget_router import BudgetRouter
    router = BudgetRouter()
    # Build channel_data dict from current_allocation + channel_performance
    current_alloc = args.get("current_allocation", {})
    perf = args.get("channel_performance", {})
    channel_data = {}
    for ch in set(list(current_alloc.keys()) + list(perf.keys())):
        p = perf.get(ch, {})
        channel_data[ch] = {
            "spend": current_alloc.get(ch, 0),
            "roas": p.get("roas", 0),
            "conversions": p.get("conversions", 0),
            "cpa": p.get("cpa", 0),
        }
    total_budget = args.get("total_budget", sum(current_alloc.values()))
    allocations = await router.rebalance(
        total_budget=total_budget,
        channel_data=channel_data,
        strategy=args.get("strategy", "roas_optimized"),
    )
    return {"allocations": [a if isinstance(a, dict) else getattr(a, '__dict__', str(a)) for a in allocations], "count": len(allocations)}


async def handle_analyze_positioning(args):
    from gtm.positioning import PositioningAnalyzer
    analyzer = PositioningAnalyzer()
    brand = args.get("brand", "Unknown")
    product = args.get("product", brand)
    industry = args.get("industry", "AI/ML")
    return await analyzer.analyze(
        product_name=brand,
        product_description=args.get("product_description", product),
        category=industry,
        competitors=args.get("competitors", []),
        target_audience=args.get("target_audience", ""),
    )


async def handle_collect_signals(args):
    from signals.collectors import ProductHuntCollector, TrendsCollector, TwitterCollector, RedditCollector
    signals = []
    # Map source strings to actual collectors
    source_map = {
        "product_hunt": (ProductHuntCollector, {}),
        "hacker_news": (TrendsCollector, {}),  # TrendsCollector for trend signals
        "twitter": (TwitterCollector, {}),
        "reddit": (RedditCollector, {}),
        "trends": (TrendsCollector, {}),
    }
    sources = args.get("sources", ["product_hunt", "twitter"])
    limit = args.get("days", 7) * 10
    for src in sources:
        collector_cls, extra = source_map.get(src, (None, None))
        if collector_cls:
            try:
                col = collector_cls()
                sigs = await col.collect(limit=limit)
                signals.extend(sigs)
            except Exception:
                pass
    # Convert signals to dicts
    out = []
    for s in signals:
        if hasattr(s, 'to_dict'):
            out.append(s.to_dict())
        elif isinstance(s, dict):
            out.append(s)
        else:
            out.append(str(s))
    return {"signals": out, "count": len(out)}


async def handle_get_attribution(args):
    from analytics.attribution import MultiTouchAttribution, AttributionModel, Touchpoint
    import uuid
    mta = MultiTouchAttribution()
    model_map = {"first_touch": AttributionModel.FIRST_TOUCH, "last_touch": AttributionModel.LAST_TOUCH, "linear": AttributionModel.LINEAR, "time_decay": AttributionModel.TIME_DECAY, "position_based": getattr(AttributionModel, "POSITION_BASED", AttributionModel.LINEAR)}
    model = model_map.get(args.get("model", "linear"), AttributionModel.LINEAR)
    # Convert raw channel_points dicts to Touchpoint objects
    raw_points = args.get("channel_points", [])
    touchpoints = []
    for cp in raw_points:
        if isinstance(cp, dict):
            channel = cp.get("channel", "unknown")
            count = cp.get("touchpoints", cp.get("count", 1))
            value = cp.get("conversion_value", cp.get("revenue", 0))
            for i in range(max(count, 1)):
                touchpoints.append(Touchpoint(
                    touchpoint_id=str(uuid.uuid4()),
                    channel=channel,
                    campaign=channel,
                    timestamp=str(i),
                    event="conversion",
                    revenue=value,
                    conversion_value=value,
                ))
    results = mta.calculate(touchpoints=touchpoints, model=model)
    # Convert AttributionResult objects to dicts
    out = []
    for r in results:
        if isinstance(r, dict):
            out.append(r)
        else:
            out.append({k: v for k, v in vars(r).items() if not k.startswith('_')})
    return {"results": out, "model": args.get("model", "linear"), "touchpoints_analyzed": len(touchpoints)}


async def handle_generate_narrative(args):
    from gtm.narrative import NarrativeGenerator
    gen = NarrativeGenerator()
    narrative_type = args.get("narrative_type", "brand_story")
    brand = args.get("brand", "Unknown")
    if narrative_type == "brand_story":
        story = await gen.generate_brand_story(
            company_name=brand,
            mission=args.get("mission", args.get("industry", "Building the future with AI")),
            founder_story=args.get("founder_story", ""),
            values=args.get("values", []),
        )
        return {"narrative": story, "type": "brand_story", "brand": brand}
    elif narrative_type == "product_story":
        return {"narrative": "[Product story generation requires product_story handler]", "type": "product_story", "brand": brand}
    return {"error": f"Unknown narrative type: {narrative_type}"}


async def handle_launch_campaign_ad(args):
    return {"error": "launch_campaign_ad requires approval — connect via Composio MCP for real ad deployment"}


# Hub handlers
async def handle_hub_health_check(args):
    from integrations.unified_adapter import MarketingHub, create_hub, list_supported_platforms
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "clay": {"api_key": os.getenv("CLAY_API_KEY", "")},
        "mixpanel": {"project_token": os.getenv("MIXPANEL_TOKEN", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
        "mailchimp": {"api_key": os.getenv("MAILCHIMP_API_KEY", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    results = await hub.health_check_all()
    return {"supported_platforms": list_supported_platforms(), "connected_platforms": hub.get_connected_platforms(), "platform_status": results}


async def handle_hub_broadcast_event(args):
    from integrations.unified_adapter import MarketingHub, Event
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "mixpanel": {"project_token": os.getenv("MIXPANEL_TOKEN", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    event = Event(event_name=args["event_name"], contact_id=args["contact_id"], properties=args.get("properties", {}), revenue=args.get("revenue", 0))
    results = await hub.broadcast_event(event)
    return {"event_name": args["event_name"], "contact_id": args["contact_id"], "platform_results": results, "success_count": sum(1 for v in results.values() if v)}


async def handle_hub_sync_contact(args):
    from integrations.unified_adapter import MarketingHub, Contact, ContactStatus
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
        "mailchimp": {"api_key": os.getenv("MAILCHIMP_API_KEY", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    stage_map = {"lead": "lead", "mql": "mql", "sql": "sql", "opportunity": "opportunity", "customer": "customer", "churned": "churned"}
    contact = Contact(
        contact_id=args["contact_id"],
        email=args["email"],
        phone=args.get("phone", ""),
        first_name=args.get("first_name", ""),
        last_name=args.get("last_name", ""),
        company=args.get("company", ""),
        lifecycle_stage=stage_map.get(args.get("lifecycle_stage", "lead"), "lead"),
        attributes=args.get("attributes", {}),
        tags=args.get("tags", []),
    )
    result_contact = await hub.sync_contact(contact)
    return {"contact_id": args["contact_id"], "email": args["email"], "platform_ids": result_contact.platform_ids, "synced_platforms": list(result_contact.platform_ids.keys())}


async def handle_hub_send_campaign(args):
    from integrations.unified_adapter import MarketingHub, Campaign, ChannelType, CampaignStatus
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
        "mailchimp": {"api_key": os.getenv("MAILCHIMP_API_KEY", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    channel_map = {"email": ChannelType.EMAIL, "sms": ChannelType.SMS, "push": ChannelType.PUSH, "whatsapp": ChannelType.WHATSAPP, "in_app": ChannelType.IN_APP}
    campaign = Campaign(name=args["campaign_name"], channel=channel_map.get(args.get("channel", "email"), ChannelType.EMAIL), subject=args.get("subject", ""), content_html=args.get("content_html", ""))
    result = await hub.send_campaign(campaign.campaign_id, preferred=args.get("preferred_platform"))
    return {"campaign_name": args["campaign_name"], "result": result}


async def handle_hub_get_dashboard(args):
    from integrations.unified_adapter import MarketingHub
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "mixpanel": {"project_token": os.getenv("MIXPANEL_TOKEN", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    return await hub.get_unified_dashboard()


async def handle_hub_search_prospects(args):
    from integrations.unified_adapter import ClayAdapter
    import os
    clay_key = os.getenv("CLAY_API_KEY", "")
    if not clay_key:
        return {"error": "CLAY_API_KEY not set", "prospects": []}
    adapter = ClayAdapter(api_key=clay_key)
    await adapter.connect()
    prospects = await adapter.search_contacts(args["query"], limit=args.get("limit", 10))
    return {"query": args["query"], "prospects": [{"email": p.email, "name": p.full_name, "company": p.company, "job_title": p.job_title} for p in prospects], "count": len(prospects)}


async def handle_hub_create_segment(args):
    from integrations.unified_adapter import MarketingHub, Segment
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
        "mailchimp": {"api_key": os.getenv("MAILCHIMP_API_KEY", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    segment = Segment(name=args["name"], description=args.get("description", ""), conditions=args.get("conditions", []))
    result = await hub.create_unified_segment(segment)
    return {"segment_id": result.segment_id, "name": args["name"], "platform_segments": result.platform_segments}


async def handle_hub_send_transactional(args):
    from integrations.unified_adapter import MarketingHub, ChannelType
    import os
    platforms = {
        "webengage": {"api_key": os.getenv("WEBENGAGE_API_KEY", ""), "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")},
        "braze": {"api_key": os.getenv("BRAZE_API_KEY", ""), "app_id": os.getenv("BRAZE_APP_ID", "")},
        "clevertap": {"account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""), "passcode": os.getenv("CLEVERTAP_PASSCODE", "")},
        "intercom": {"api_key": os.getenv("INTERCOM_API_KEY", "")},
    }
    hub = MarketingHub()
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception:
                pass
    await hub.initialize()
    channel_map = {"email": ChannelType.EMAIL, "sms": ChannelType.SMS, "push": ChannelType.PUSH, "whatsapp": ChannelType.WHATSAPP, "in_app": ChannelType.IN_APP}
    channel = channel_map.get(args.get("channel", "email"), ChannelType.EMAIL)
    content = {"title": args.get("title", ""), "body": args["body"], "deep_link": args.get("deep_link", "")}
    result = await hub.send_transactional(args["contact_id"], channel, content)
    return {"contact_id": args["contact_id"], "channel": args.get("channel", "email"), "result": result}


async def handle_hub_list_platforms(args):
    from integrations.unified_adapter import list_supported_platforms, ADAPTER_REGISTRY
    platforms = list_supported_platforms()
    details = {}
    for name in platforms:
        cls = ADAPTER_REGISTRY.get(name)
        if cls:
            details[name] = {"channels": [c.value for c in cls.supported_channels], "supports_journeys": cls.supports_journeys, "supports_analytics": cls.supports_analytics}
    return {"platforms": platforms, "platform_details": details, "total_count": len(platforms)}


# CRM handlers
async def handle_crm_create_lead(args):
    from crm import CRMMaster
    crm = CRMMaster()
    lead = crm.create_lead(email=args["email"], first_name=args.get("first_name", ""), last_name=args.get("last_name", ""), phone=args.get("phone", ""), company=args.get("company", ""), job_title=args.get("job_title", ""), source=args.get("source", "organic"), tags=args.get("tags", []))
    score = crm.score_lead(lead.lead_id)
    return {"lead_id": lead.lead_id, "email": lead.email, "name": lead.full_name, "company": lead.company, "status": lead.status.value, "score": score, "lifecycle_stage": lead.lifecycle_stage}


async def handle_crm_create_deal(args):
    from crm import CRMMaster, DealStage
    crm = CRMMaster()
    stage_map = {"lead": DealStage.LEAD, "qualified": DealStage.QUALIFIED, "proposal": DealStage.PROPOSAL, "negotiation": DealStage.NEGOTIATION, "closed_won": DealStage.CLOSED_WON, "closed_lost": DealStage.CLOSED_LOST}
    deal = crm.create_deal(name=args["name"], value=args.get("value", 0), stage=stage_map.get(args.get("stage", "lead"), DealStage.LEAD), lead_id=args.get("lead_id", "") or None, owner_id=args.get("owner_id", ""))
    return {"deal_id": deal.deal_id, "name": deal.name, "value": deal.value, "stage": deal.stage.value, "probability": deal.probability}


async def handle_crm_move_deal(args):
    from crm import CRMMaster, DealStage
    crm = CRMMaster()
    stage_map = {"lead": DealStage.LEAD, "qualified": DealStage.QUALIFIED, "proposal": DealStage.PROPOSAL, "negotiation": DealStage.NEGOTIATION, "closed_won": DealStage.CLOSED_WON, "closed_lost": DealStage.CLOSED_LOST}
    new_stage = stage_map.get(args["new_stage"])
    if not new_stage:
        return {"error": f"Unknown stage: {args['new_stage']}"}
    deal = crm.move_deal(args["deal_id"], new_stage)
    if not deal:
        return {"error": f"Deal not found: {args['deal_id']}"}
    return {"deal_id": deal.deal_id, "stage": deal.stage.value, "probability": deal.probability}


async def handle_crm_log_activity(args):
    from crm import CRMMaster, ActivityType
    crm = CRMMaster()
    type_map = {"call": ActivityType.CALL, "email": ActivityType.EMAIL, "meeting": ActivityType.MEETING, "note": ActivityType.NOTE, "task": ActivityType.TASK, "campaign": ActivityType.CAMPAIGN}
    activity_type = type_map.get(args["activity_type"], ActivityType.NOTE)
    activity = crm.log_activity(entity_id=args["entity_id"], activity_type=activity_type, subject=args.get("subject", ""), notes=args.get("notes", ""), duration_minutes=args.get("duration_minutes", 0))
    return {"activity_id": activity.activity_id, "entity_id": activity.entity_id, "type": activity.activity_type.value, "created_at": activity.created_at}


async def handle_crm_get_dashboard(args):
    from crm import CRMMaster
    crm = CRMMaster()
    return crm.get_crm_dashboard()


async def handle_crm_search_leads(args):
    from crm import CRMMaster
    crm = CRMMaster()
    leads = crm.search_leads(args["query"], limit=args.get("limit", 10))
    return {"query": args["query"], "leads": [{"lead_id": l.lead_id, "email": l.email, "name": l.full_name, "company": l.company, "score": l.score} for l in leads], "count": len(leads)}


async def handle_crm_get_pipeline(args):
    from crm import CRMMaster
    crm = CRMMaster()
    return crm.get_pipeline_summary()


async def handle_crm_get_timeline(args):
    from crm import CRMMaster
    crm = CRMMaster()
    timeline = crm.get_timeline(args["entity_id"])
    return {"entity_id": args["entity_id"], "events": timeline, "count": len(timeline)}


# UTM & Workflow handlers
async def handle_build_utm_url(args):
    from integrations.unified_adapter import build_utm_url
    url = build_utm_url(
        base_url=args["base_url"],
        source=args["source"],
        medium=args["medium"],
        campaign=args["campaign"],
        content=args.get("content"),
        term=args.get("term")
    )
    return {"url": url}


async def handle_parse_utm_params(args):
    from integrations.unified_adapter import parse_utm_params
    return {"utm_params": parse_utm_params(args["url"])}


async def handle_run_workflow(args):
    from integrations.unified_adapter import MarketingHub, MarketingWorkflow
    import os
    
    wf = MarketingWorkflow(
        workflow_id=args["workflow_id"],
        name=args.get("name", "")
    )
    
    for step in args["steps"]:
        wf.add_step(
            step_id=step["step_id"],
            action=step["action"],
            params=step.get("params", {}),
            on_success=step.get("on_success"),
            on_failure=step.get("on_failure"),
            is_first=(step["step_id"] == args["first_step"])
        )
    
    hub = MarketingHub()
    platforms = {
        "webengage": {
            "api_key": os.getenv("WEBENGAGE_API_KEY", ""),
            "license_code": os.getenv("WEBENGAGE_LICENSE_CODE", "")
        },
        "hubspot": {"api_key": os.getenv("HUBSPOT_API_KEY", "")},
        "clevertap": {
            "account_id": os.getenv("CLEVERTAP_ACCOUNT_ID", ""),
            "passcode": os.getenv("CLEVERTAP_PASSCODE", "")
        },
        "braze": {
            "api_key": os.getenv("BRAZE_API_KEY", ""),
            "app_id": os.getenv("BRAZE_APP_ID", "")
        },
        "mailchimp": {"api_key": os.getenv("MAILCHIMP_API_KEY", "")},
    }
    
    for platform, creds in platforms.items():
        if any(creds.values()):
            try:
                hub.connect(platform, **creds)
            except Exception as e:
                sys.stderr.write(f"[marketic MCP] Hub connect error for {platform}: {e}\n")
    
    await hub.initialize()
    result = await wf.execute(hub)
    # Use shared _serialize helper
    return _serialize(result)


# Ensemble & Audit handlers
async def handle_ensemble_vote(args):
    from ensemble.voting import EnsembleVoter
    voter = EnsembleVoter()
    vote = voter.vote(
        task_type=args["task_type"],
        prompt=args["prompt"],
        context=args.get("context", {}),
        models=args.get("models"),
    )
    return {
        "decision": vote.decision,
        "confidence": vote.confidence,
        "models_used": vote.models_used,
        "reasoning_chain": vote.reasoning_chain,
        "cost": vote.cost,
        "consensus": vote.consensus,
    }


async def handle_audit_log(args):
    from ensemble.audit_trail import AuditLogger
    logger = AuditLogger()
    audit_id = logger.log_action(
        action=args["action"],
        model=args.get("model", ""),
        input_tokens=args.get("input_tokens", 0),
        output_tokens=args.get("output_tokens", 0),
        cost=args.get("cost", 0.0),
        confidence=args.get("confidence", 0.0),
        reasoning_chain=args.get("reasoning_chain", []),
        result_summary=args.get("result_summary", ""),
        human_approved=args.get("human_approved"),
        brand_id=args.get("brand_id", ""),
        metadata=args.get("metadata", {}),
    )
    return {"audit_id": audit_id, "status": "logged"}


async def handle_audit_get_log(args):
    from ensemble.audit_trail import AuditLogger
    logger = AuditLogger()
    entries = logger.get_audit_log(
        brand_id=args.get("brand_id", "") or None,
        action=args.get("action", "") or None,
        start_date=args.get("start_date", "") or None,
        end_date=args.get("end_date", "") or None,
        limit=args.get("limit", 100),
    )
    return {
        "entries": [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "brand_id": e.brand_id,
                "action": e.action,
                "model": e.model,
                "cost": e.cost,
                "confidence": e.confidence,
                "human_approved": e.human_approved,
                "result_summary": e.result_summary,
            }
            for e in entries
        ],
        "count": len(entries),
    }


async def handle_audit_get_cost_summary(args):
    from ensemble.audit_trail import AuditLogger
    logger = AuditLogger()
    summary = logger.get_cost_summary(
        brand_id=args.get("brand_id", "") or None,
        start_date=args.get("start_date", "") or None,
        end_date=args.get("end_date", "") or None,
    )
    return summary


# Brief & Signal handlers
async def handle_generate_brief(args):
    from execution.brief import generate_brief
    return generate_brief(
        campaign_name=args["campaign_name"],
        objective=args["objective"],
        product_name=args["product_name"],
        product_description=args["product_description"],
        target_audience=args.get("target_audience", ""),
        channels=args.get("channels"),
        total_budget=args.get("total_budget", 10000),
        duration_weeks=args.get("duration_weeks", 4),
        key_benefits=args.get("key_benefits"),
        brand_tokens=args.get("brand_tokens"),
        channel_performance=args.get("channel_performance"),
        positioning_summary=args.get("positioning_summary", ""),
        competitor_insights=args.get("competitor_insights", ""),
    )


async def handle_run_prospect_loop(args):
    """Signal-driven prospect discovery -> enrichment -> outreach drafts -> CRM."""
    from crm.prospect_loop import ProspectLoop
    loop = ProspectLoop()
    return await loop.run(
        niche_query=args.get("niche_query", ""),
        market_query=args.get("market_query", ""),
        limit=int(args.get("limit", 5)),
    )


async def handle_distill_learnings(args):
    """Promote recurring audit-trail patterns into brand learnings + brain md export."""
    from ensemble.learnings import LearningEngine
    engine = LearningEngine()
    if args.get("capture_rule"):
        engine.capture(
            brand=args.get("brand", "default"),
            category=args.get("category", "general"),
            rule_text=args["capture_rule"],
            confidence=float(args.get("confidence", 0.5)),
        )
        return {"captured": args["capture_rule"]}
    found = engine.distill(min_occurrences=int(args.get("min_occurrences", 3)))
    path = None
    if args.get("export_brain", True) and (args.get("brand") or "default"):
        path = engine.export_brain_md(args.get("brand", "default"))
    return {"distilled": len(found), "brain_path": path,
            "learnings": [{"rule": l.get("rule_text"), "seen": l.get("occurrences")}
                          for l in (found or [])][:10]}


async def handle_search_fb_ads(args):
    """Search Facebook Ads Library for real competitor creatives/copy (ground truth)."""
    try:
        from gtm.fb_ads_library import FBAdsLibraryClient
    except ImportError:
        return {"error": "fb_ads_library module unavailable"}
    client = FBAdsLibraryClient()
    if not client.is_available():
        return {"error": "FB_ACCESS_TOKEN not set — ads library backend unavailable",
                "hint": "set FB_ACCESS_TOKEN env var (Meta developer token)"}
    return {"ads": client.search_ads(args.get("brand_name", ""),
                                    country=args.get("country", "ALL"),
                                    limit=int(args.get("limit", 20)))}


async def handle_ask_marketic(args):
    """
    Master router: one entry point that routes a natural-language marketing
    question to the right specialist tool(s) and returns combined results.
    Pattern borrowed from skill-suites' agency agent (council rec #9).
    """
    q = (args.get("question") or "").lower()
    route_table = [
        (["prospect", "leads", "find people", "outreach", "email list"], "run_prospect_loop"),
        (["what did we learn", "learnings", "lessons", "brain", "patterns"], "distill_learnings"),
        # fb-ads routes must come BEFORE analyze_competitor_ad so "facebook ads"
        # / "ads library" don't collide with the generic ad-analysis keywords.
        (["facebook ads", "fb ads", "ads library", "real ads", "spend data"], "search_fb_ads"),
        (["competitor ad", "deconstruct", "hook", "their ads", "ad analysis"], "analyze_competitor_ad"),
        (["breakdown ad", "ad structure", "hook offer cta", "ad breakdown"], "breakdown_ad"),
        (["budget", "allocate", "spend", "split"], "optimize_budget"),
        (["campaign", "launch", "funnel"], "build_campaign"),
        (["signal", "trend", "moving", "market news", "buzz"], "signal_fanout"),
        (["positioning", "differentiate", "wedge"], "analyze_positioning"),
        (["narrative", "story", "messaging"], "generate_narrative"),
        (["seo", "keyword", "rank"], "generate_seo_content"),
        (["social post", "instagram", "linkedin", "tweet"], "generate_social_posts"),
        (["brief", "handoff", "execution plan"], "generate_brief"),
        (["attribution", "which channel", "credit"], "get_attribution"),
        (["lead", "deal", "pipeline", "crm"], "crm_dashboard"),
        (["cost", "spend on ai", "audit"], "audit_get_cost_summary"),
        (["track", "calibration", "brier", "signal tracking"], "track_signal"),
        (["calibration report", "brier score", "signal accuracy", "prediction quality"], "get_calibration_report"),
        (["resolve", "close signal", "actual outcome"], "resolve_signal"),
        (["schedule", "post", "publish", "content calendar"], "schedule_content"),
        (["upcoming posts", "what's scheduled", "calendar"], "get_upcoming_posts"),
        (["hashtag", "optimize hashtags", "discover hashtags"], "optimize_hashtags"),
        (["ugc", "curate", "user generated", "repost"], "curate_ugc"),
        (["permission", "ugc request"], "request_ugc_permission"),
        (["track ugc", "ugc analytics"], "track_ugc"),
        (["render", "template", "design", "visual"], "render_template"),
    ]
    routed, matched = [], set()
    for keywords, tool in route_table:
        if any(k in q for k in keywords) and tool not in matched:
            if tool in HANDLERS:
                routed.append(tool)
                matched.add(tool)
    if args.get("route_only"):
        return {"question": q, "routed_tools": routed}
    if not routed:
        return {"question": q, "error": "no matching tool",
                "hint": "try mentioning signals/budget/campaign/competitor/seo/social/brief"}
    # execute the primary match; pass through any supplied arguments
    primary = routed[0]
    result = await HANDLERS[primary](args.get("arguments", {}))
    return {"question": q, "routed_to": routed, "primary_result": result}


async def handle_track_signal(args):
    from analytics.scorecard import SignalScorecard
    sc = SignalScorecard()
    sig = {
        "title": args.get("title", ""),
        "source": args.get("source", ""),
        "signal_type": args.get("signal_type", ""),
        "url": args.get("url", ""),
        "engagement_score": args.get("engagement_score", 0),
        "topics": args.get("topics", []),
        "metadata": args.get("metadata", {}),
    }
    return sc.track_signal(sig)


async def handle_get_calibration_report(args):
    from analytics.scorecard import SignalScorecard
    sc = SignalScorecard()
    return sc.get_calibration_report(
        start_date=args.get("start_date"),
        end_date=args.get("end_date"),
        source=args.get("source"),
    )


async def handle_resolve_signal(args):
    from analytics.scorecard import SignalScorecard
    sc = SignalScorecard()
    return sc.resolve_signal(
        signal_id=args["signal_id"],
        actual_outcome=args["actual_outcome"],
        notes=args.get("notes", ""),
    )


async def handle_signal_fanout(args):
    from signals.collectors import SignalFanout
    fanout = SignalFanout()
    return await fanout.run(
        query=args.get("query", ""),
        sources=args.get("sources") or None,
        limit_per_source=args.get("limit_per_source", 25),
    )


async def handle_analyze_competitor_ad(args):
    try:
        from gtm.ad_analysis import AdAnalyzer
    except ImportError:
        from gtm.ad_analysis import AdAnalyzer
    analyzer = AdAnalyzer()

    def _ser(b):
        d = asdict(b) if hasattr(b, "__dataclass_fields__") else b.__dict__
        return d

    if args.get("batch"):
        breakdowns = analyzer.analyze_batch(args["batch"])
        if args.get("derive"):
            return analyzer.derive_counter_brief(breakdowns)
        return {"breakdowns": [_ser(b) for b in breakdowns], "count": len(breakdowns)}

    b = analyzer.analyze(
        image_path_or_url=args.get("image_path_or_url", ""),
        transcript=args.get("transcript", ""),
        caption=args.get("caption", ""),
    )
    result = _ser(b)
    if args.get("derive"):
        return {"counter_brief": analyzer.derive_counter_brief([b]), "breakdown": result}
    return result


async def handle_breakdown_ad(args):
    """Break down a competitor ad via URL or raw copy text.

    analysis_depth maps to confidence tiers:
      - quick: heuristic fallback only (confidence ~0.2)
      - standard: ollama vision -> cloud vision -> heuristic (confidence 0.2-0.85)
      - deep: same ladder but returns extended counter-angles + tone map
    """
    from gtm.ad_analysis import AdAnalyzer

    ad_input = args.get("ad_url_or_text", "").strip()
    if not ad_input:
        return {"error": "ad_url_or_text is required"}

    brand_name = args.get("brand_name", "")
    depth = args.get("analysis_depth", "standard")

    analyzer = AdAnalyzer()

    # Determine input mode: URL/media reference vs plain-text ad copy
    is_url = ad_input.startswith(("http://", "https://", "file://"))

    if is_url:
        breakdown = analyzer.analyze(
            image_path_or_url=ad_input,
            transcript="",
            caption="",
            brand_name=brand_name,
        )
    else:
        # Plain text / ad copy — route via transcript for heuristic
        breakdown = analyzer.analyze(
            image_path_or_url="",
            transcript=ad_input,
            caption=ad_input,
            brand_name=brand_name,
        )

    result = asdict(breakdown) if hasattr(breakdown, "__dataclass_fields__") else breakdown.__dict__

    if depth == "deep":
        counter = analyzer.derive_counter_brief([breakdown])
        result["_counter_brief"] = counter

    result["_analysis_depth"] = depth
    return result


# Publishing layer handlers
async def handle_schedule_content(args):
    from execution.publisher import ContentCalendarManager, PostizPublisher, Platform, Post, PostStatus
    from datetime import datetime

    platform_str = args.get("platform", "postiz")
    content_text = args.get("content_text", "")
    media_urls = args.get("media_urls", [])
    scheduled_time_str = args.get("scheduled_time")
    hashtags = args.get("hashtags", [])

    # Map platform string to Platform enum
    platform_map = {
        "postiz": Platform.INSTAGRAM,  # postiz maps to IG for calendar purposes
        "instagram": Platform.INSTAGRAM,
        "linkedin": Platform.LINKEDIN,
        "twitter": Platform.TWITTER,
    }
    platform_enum = platform_map.get(platform_str, Platform.INSTAGRAM)

    if platform_str == "postiz":
        # Fall back to PostizPublisher.publish_post
        publisher = PostizPublisher()
        scheduled_for = None
        if scheduled_time_str:
            try:
                scheduled_for = datetime.fromisoformat(scheduled_time_str)
            except ValueError:
                pass
        post = Post(
            post_id=f"postiz_{int(datetime.utcnow().timestamp())}",
            platform=Platform.INSTAGRAM,
            content=content_text,
            media_urls=media_urls,
            hashtags=hashtags,
            status=PostStatus.SCHEDULED if scheduled_for else PostStatus.DRAFT,
            scheduled_for=scheduled_for.isoformat() if scheduled_for else None,
            published_at=None,
        )
        result = await publisher.publish_post(post)
        return {"scheduled": result.success, "post_id": result.post_id, "error": result.error, "url": result.url}

    # Use ContentCalendarManager
    cal = ContentCalendarManager()
    scheduled_for = None
    if scheduled_time_str:
        try:
            scheduled_for = datetime.fromisoformat(scheduled_time_str)
        except ValueError:
            pass

    post = cal.create_calendar_entry(
        platform=platform_enum,
        content=content_text,
        hashtags=hashtags,
        media_urls=media_urls,
        scheduled_time=scheduled_for,
    )
    results = await cal.schedule_content([post])
    if results:
        r = results[0]
        return {"scheduled": r.success, "post_id": r.post_id, "error": r.error, "url": r.url}
    return {"scheduled": False, "post_id": None, "error": "schedule_content returned no results"}


async def handle_get_upcoming_posts(args):
    from execution.publisher import ContentCalendarManager, Platform

    platform_str = args.get("platform")
    days = int(args.get("days", 7))
    limit = int(args.get("limit", 20))

    cal = ContentCalendarManager()
    posts = cal.get_upcoming_posts(days=days)

    if platform_str:
        platform_map = {
            "instagram": Platform.INSTAGRAM,
            "linkedin": Platform.LINKEDIN,
            "twitter": Platform.TWITTER,
        }
        plat = platform_map.get(platform_str)
        if plat:
            posts = [p for p in posts if p.platform == plat]

    posts = posts[:limit]
    return {
        "posts": [
            {
                "post_id": p.post_id,
                "platform": p.platform.value,
                "content": p.content,
                "hashtags": p.hashtags,
                "status": p.status.value,
                "scheduled_for": p.scheduled_for,
            }
            for p in posts
        ],
        "count": len(posts),
    }


async def handle_optimize_hashtags(args):
    from execution.publisher import HashtagOptimizer, Platform

    content_text = args.get("content_text", "")
    platform_str = args.get("platform", "instagram")
    limit = int(args.get("limit", 15))

    platform_map = {
        "instagram": Platform.INSTAGRAM,
        "facebook": Platform.FACEBOOK,
        "twitter": Platform.TWITTER,
        "linkedin": Platform.LINKEDIN,
        "tiktok": Platform.TIKTOK,
    }
    platform_enum = platform_map.get(platform_str, Platform.INSTAGRAM)

    optimizer = HashtagOptimizer()
    hashtags = optimizer.get_hashtags_for_post(
        content=content_text,
        platform=platform_enum,
        count=limit,
    )
    return {"hashtags": hashtags, "optimized": True}


# UGC layer handlers
async def handle_curate_ugc(args):
    from execution.ugc_curator import UGCCurator, UGCContent, PermissionStatus

    hashtag = args.get("hashtag", "")
    platform_str = args.get("platform", "instagram")
    limit = int(args.get("limit", 10))
    min_aesthetic = float(args.get("min_aesthetic_score", 0.4))

    curator = UGCCurator()
    discovered = await curator.discover_content(
        hashtags=[hashtag],
        platforms=[platform_str],
        limit=limit,
    )
    filtered = curator.filter_content(discovered, min_aesthetic=min_aesthetic)

    return {
        "curated": [
            {
                "url": c.image_url,
                "caption": c.caption,
                "author": c.username,
                "aesthetic_score": c.aesthetic_score,
                "hashtags": c.hashtags,
                "likes": c.likes,
                "platform": c.platform,
            }
            for c in filtered[:limit]
        ],
        "total_discovered": len(discovered),
        "total_curated": len(filtered),
    }


async def handle_request_ugc_permission(args):
    from execution.ugc_curator import UGCCurator, UGCContent, PermissionStatus

    content_url = args.get("content_url", "")
    platform_str = args.get("platform", "instagram")
    message = args.get("message", "")

    # Build a minimal UGCContent from the content_url as best-effort
    # (actual impl would look up real content; here we construct for the permission request)
    fake_content = UGCContent(
        content_id=content_url,
        platform=platform_str,
        username="unknown",
        caption="",
        hashtags=[],
        image_url=content_url,
        video_url=None,
        likes=0,
        comments=0,
        posted_at="",
        relevance_score=0.0,
        aesthetic_score=0.0,
        permission_status=PermissionStatus.PENDING,
        permission_requested_at=None,
        permission_granted_at=None,
    )

    curator = UGCCurator()
    perm_request = await curator.request_permission(fake_content)

    return {
        "requested": True,
        "permission_id": perm_request.request_id,
        "username": perm_request.username,
        "platform": perm_request.platform,
        "message_template": perm_request.message_template,
        "status": perm_request.status.value,
    }


async def handle_track_ugc(args):
    from execution.ugc_curator import UGCAnalytics, UGCRepost, UGCContent, PermissionStatus

    repost_id = args.get("repost_id", "")
    platform_str = args.get("platform", "instagram")

    # Build a minimal UGCRepost for tracking (actual impl would look up real repost)
    fake_content = UGCContent(
        content_id="unknown",
        platform=platform_str,
        username="unknown",
        caption="",
        hashtags=[],
        image_url="",
        video_url=None,
        likes=0,
        comments=0,
        posted_at="",
        relevance_score=0.0,
        aesthetic_score=0.0,
        permission_status=PermissionStatus.PENDING,
        permission_requested_at=None,
        permission_granted_at=None,
    )
    fake_repost = UGCRepost(
        repost_id=repost_id,
        original_content=fake_content,
        branded_caption="",
        hashtags=[],
        scheduled_for=None,
        posted_to=[platform_str],
        status="published",
    )

    analytics = UGCAnalytics()
    result = await analytics.track_repost(fake_repost)
    return {"tracked": True, "reposts": result.get("metrics", {}).get("reach", 0)}


# Creative layer handlers
async def handle_render_template(args):
    from execution.design_templates import TemplateRenderer, BrandTokens

    template_name = args.get("template_name", "")
    brand_dict = args.get("brand", {})
    content_overrides = args.get("content_overrides", {})

    # Build BrandTokens from brand dict
    brand_tokens = BrandTokens(
        name=brand_dict.get("name", "Brand"),
        tagline=brand_dict.get("tagline", ""),
        handle=brand_dict.get("handle", "@brand"),
        primary_color=brand_dict.get("primary", "#1A1A1A"),
        background_color=brand_dict.get("background", "#FFFFFF"),
        accent_color=brand_dict.get("accent", "#FF6600"),
        secondary_color=brand_dict.get("secondary", "#008000"),
        font_primary=brand_dict.get("font", "Helvetica"),
    )

    renderer = TemplateRenderer()
    renderer.library.tokens = brand_tokens

    # Collect all [PLACEHOLDER] tokens from the template to detect missing required content
    from execution.design_templates import TemplateLibrary
    library = TemplateLibrary(tokens=brand_tokens)
    tmpl = library.get_template(template_name)

    if not tmpl:
        return {"error": f"Template not found: {template_name}", "available_templates": list(library.templates.keys())}

    # Determine required placeholders from template layers that look like [KEY]
    import re
    required_placeholders = set()
    for layer in tmpl.layers:
        found = re.findall(r'\[([A-Z_]+)\]', layer.content)
        required_placeholders.update(found)

    # Merge content_overrides with defaults
    placeholders = dict(content_overrides)

    # Check which required placeholders are missing
    missing = required_placeholders - set(placeholders.keys())

    if missing:
        # Return placeholders list so caller knows what's needed
        return {"placeholders": sorted(missing), "template_id": template_name, "template_name": tmpl.name}

    # Render using Paper MCP script format
    html = renderer.render_for_paper_mcp(template_name, placeholders)
    return {"html": html, "preview_url": f"marketic://preview/{template_name}", "template_id": template_name}


# ─── Handler Registry ─────────────────────────────────────────

HANDLERS = {
    "analyze_competitor": handle_analyze_competitor,
    "compare_competitors": handle_compare_competitors,
    "generate_creatives": handle_generate_creatives,
    "generate_social_posts": handle_generate_social_posts,
    "generate_seo_content": handle_generate_seo_content,
    "build_campaign": handle_build_campaign,
    "optimize_budget": handle_optimize_budget,
    "analyze_positioning": handle_analyze_positioning,
    "collect_signals": handle_collect_signals,
    "get_attribution": handle_get_attribution,
    "generate_narrative": handle_generate_narrative,
    "launch_campaign_ad": handle_launch_campaign_ad,
    "hub_health_check": handle_hub_health_check,
    "hub_broadcast_event": handle_hub_broadcast_event,
    "hub_sync_contact": handle_hub_sync_contact,
    "hub_send_campaign": handle_hub_send_campaign,
    "hub_get_dashboard": handle_hub_get_dashboard,
    "hub_search_prospects": handle_hub_search_prospects,
    "hub_create_segment": handle_hub_create_segment,
    "hub_send_transactional": handle_hub_send_transactional,
    "hub_list_platforms": handle_hub_list_platforms,
    "crm_create_lead": handle_crm_create_lead,
    "crm_create_deal": handle_crm_create_deal,
    "crm_move_deal": handle_crm_move_deal,
    "crm_log_activity": handle_crm_log_activity,
    "crm_get_dashboard": handle_crm_get_dashboard,
    "crm_search_leads": handle_crm_search_leads,
    "crm_get_pipeline": handle_crm_get_pipeline,
    "crm_get_timeline": handle_crm_get_timeline,
    "build_utm_url": handle_build_utm_url,
    "parse_utm_params": handle_parse_utm_params,
    "run_workflow": handle_run_workflow,
    "ensemble_vote": handle_ensemble_vote,
    "audit_log": handle_audit_log,
    "audit_get_log": handle_audit_get_log,
    "audit_get_cost_summary": handle_audit_get_cost_summary,
    "generate_brief": handle_generate_brief,
    "signal_fanout": handle_signal_fanout,
    "ask_marketic": handle_ask_marketic,
    "run_prospect_loop": handle_run_prospect_loop,
    "distill_learnings": handle_distill_learnings,
    "search_fb_ads": handle_search_fb_ads,
    "analyze_competitor_ad": handle_analyze_competitor_ad,
    "breakdown_ad": handle_breakdown_ad,
    "track_signal": handle_track_signal,
    "get_calibration_report": handle_get_calibration_report,
    "resolve_signal": handle_resolve_signal,
    # Publishing layer
    "schedule_content": handle_schedule_content,
    "get_upcoming_posts": handle_get_upcoming_posts,
    "optimize_hashtags": handle_optimize_hashtags,
    # UGC layer
    "curate_ugc": handle_curate_ugc,
    "request_ugc_permission": handle_request_ugc_permission,
    "track_ugc": handle_track_ugc,
    # Creative layer
    "render_template": handle_render_template,
}


# ─── Serialization Helper ─────────────────────────────────────

def _serialize(obj):
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    elif hasattr(obj, "value"):
        return obj.value
    else:
        return obj


# ─── MCP Protocol Implementation ──────────────────────────────

class MCPServer:
    def __init__(self):
        self.request_id = 0
        self.initialized = False

    def send(self, msg):
        line = json.dumps(msg) + "\n"
        if hasattr(self, 'process') and self.process:
            self.process.stdin.write(line)
            self.process.stdin.flush()
        else:
            # Standalone mode - write to stdout
            sys.stdout.write(line)
            sys.stdout.flush()

    def handle_line(self, line):
        line = line.strip()
        if not line:
            return None
        try:
            msg = json.loads(line)
            return self.dispatch(msg)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[marketic MCP] JSON parse error: {e}\n")
            self.send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
            return None

    def dispatch(self, msg):
        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            self.initialized = True
            self.send({"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {}}, "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}}})
            self.send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            return None

        if method == "notifications/initialized":
            return None

        if method == "tools/list":
            self.send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
            return None

        if method == "tools/call":
            tool_name = msg.get("params", {}).get("name")
            tool_args = msg.get("params", {}).get("arguments", {})
            handler = HANDLERS.get(tool_name)
            if not handler:
                self.send({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}})
                return None
            try:
                result = asyncio.run(handler(tool_args))
                serialized = _serialize(result)
                self.send({"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(serialized)}]}})
            except Exception as e:
                sys.stderr.write(f"[marketic MCP] Tool {tool_name} error: {e}\n")
                self.send({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(e)}})
            return None

        return None

    def run(self):
        sys.stderr.write(f"[marketic MCP] Server starting ({SERVER_NAME} v{SERVER_VERSION})\n")
        sys.stderr.write(f"[marketic MCP] {len(TOOLS)} tools registered: {', '.join(h for h in HANDLERS)}\n")
        for line in sys.stdin:
            self.handle_line(line)


if __name__ == "__main__":
    MCPServer().run()
