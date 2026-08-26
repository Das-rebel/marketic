# Marketic MCP Server — API Documentation

> **Version:** 2.1.0 | **Tools:** 54 | **Protocol:** JSON-RPC 2.0 over stdio
> **Regenerated from the live server's TOOLS list — cannot drift from code.**

## Protocol Reference

```bash
python3 mcp_server.py
# list all tools:
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | python3 mcp_server.py
# call a tool:
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"signal_fanout","arguments":{"query":"ai"}},"id":2}' | python3 mcp_server.py
```

## Tool Reference (54 tools)

### Router (1)

#### `ask_marketic`

Master router - one entry point for Marketic. Describe what you need in plain language (e.g. 'what's moving in AI markets', 'allocate my budget', 'deconstruct this competitor ad') and it routes to the right specialist tool(s). Use route_only=true to preview routing without executing.

| Param | Type | Required | Description |
|---|---|---|---|
| `question` | string | ✅ | Natural-language marketing question or task |
| `route_only` | boolean |  | Default: False |
| `arguments` | object |  | Optional arguments passed through to the routed tool |


### Intelligence (2)

#### `collect_signals`

Collect marketing signals from Product Hunt, Hacker News, Twitter, Reddit for a brand.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string | ✅ |  |
| `days` | integer |  | Default: 7 |
| `sources` | array |  | Default: ['product_hunt', 'hacker_news', 'twitter', 'reddit'] |

#### `signal_fanout`

Parallel multi-source signal search (Product Hunt, HN, Twitter, Reddit, Polymarket) with cross-source engagement normalization. Returns one synthesized brief with consensus themes and money outliers.

| Param | Type | Required | Description |
|---|---|---|---|
| `query` | string |  | Default: |
| `sources` | array |  | Default: [] |
| `limit_per_source` | integer |  | Default: 25 |


### Calibration (3)

#### `track_signal`

Record a signal prediction for later calibration tracking. Once tracked, you can call resolve_signal when the outcome is known to measure prediction accuracy (Brier score). Used to build calibration over time.

| Param | Type | Required | Description |
|---|---|---|---|
| `title` | string | ✅ |  |
| `source` | string | ✅ |  |
| `signal_type` | string | ✅ |  |
| `url` | string | ✅ |  |
| `engagement_score` | number | ✅ |  |
| `topics` | array |  |  |
| `metadata` | object |  |  |

#### `get_calibration_report`

Get the signal calibration report: number of predictions, Brier score (lower=better), resolved vs pending breakdown, and per-source accuracy. Shows whether Marketic's signal sources are reliable.

| Param | Type | Required | Description |
|---|---|---|---|
| `start_date` | string |  |  |
| `end_date` | string |  |  |
| `source` | string |  |  |

#### `resolve_signal`

Resolve a previously tracked signal with its actual outcome (YES/NO/PARTIAL). Used to close the calibration loop and improve future signal quality.

| Param | Type | Required | Description |
|---|---|---|---|
| `signal_id` | string | ✅ |  |
| `actual_outcome` | string | ✅ |  |
| `notes` | string |  |  |


### CRM Growth Loop (1)

#### `run_prospect_loop`

Signal-driven prospecting (JoeCRM pattern): discover prospects matching a niche, enrich with live market signals, auto-draft personalized outreach, insert scored leads into CRM. Degrades to signal-derived prospects when Serper key absent.

| Param | Type | Required | Description |
|---|---|---|---|
| `niche_query` | string | ✅ | Who to prospect, e.g. 'D2C skincare brands founder' |
| `market_query` | string |  | Market topic for signal enrichment |
| `limit` | integer |  | Default: 5 |


### Learning (1)

#### `distill_learnings`

Promote recurring audit-trail patterns into brand learnings; optionally capture an explicit rule; export brain/<brand>.md markdown for human review.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string |  | Default: default |
| `capture_rule` | string |  | If set, capture this rule instead of distilling |
| `category` | string |  | Default: general |
| `min_occurrences` | integer |  | Default: 3 |
| `export_brain` | boolean |  | Default: True |


### Creative (3)

#### `generate_creatives`

Generate ad copy variants across channels (Google, Meta, LinkedIn, etc.). Each variant includes headline, description, CTA, hooks, confidence score, and performance prediction.

| Param | Type | Required | Description |
|---|---|---|---|
| `product_name` | string | ✅ |  |
| `product_description` | string | ✅ |  |
| `channel` | string |  | Enum: google_search, google_display, meta_feed, linkedin_sponsored, email Default: meta_feed |
| `objective` | string |  | Enum: awareness, consideration, conversion Default: conversion |
| `target_audience` | string |  | Default: |
| `key_benefits` | array |  | Default: [] |
| `num_variants` | integer |  | Default: 5 |
| `tone` | string |  | Enum: persuasive, emotional, logical, urgent, friendly Default: persuasive |

#### `generate_social_posts`

Generate platform-specific social media posts (LinkedIn, X/Twitter, Instagram, Facebook). Supports threads, single posts, and multi-format content.

| Param | Type | Required | Description |
|---|---|---|---|
| `topic` | string | ✅ |  |
| `platform` | string |  | Enum: linkedin, twitter, instagram, facebook Default: linkedin |
| `format` | string |  | Enum: post, thread, carousel, story Default: post |
| `tone` | string |  | Default: professional |
| `length` | integer |  | Default: 1 |
| `hashtags` | boolean |  | Default: True |

#### `generate_seo_content`

Generate SEO-optimized content including meta titles, descriptions, headers, and FAQs for target keywords.

| Param | Type | Required | Description |
|---|---|---|---|
| `target_keyword` | string | ✅ |  |
| `content_type` | string |  | Enum: landing_page, blog_post, product_page, faq Default: blog_post |
| `word_count` | integer |  | Default: 1500 |
| `competitor_url` | string |  | Default: |


### Campaigns (2)

#### `build_campaign`

Build a complete multi-channel campaign strategy with channel-specific tactics, budgets, and timelines.

| Param | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | ✅ |  |
| `objective` | string | ✅ | Enum: awareness, lead_generation, conversion, retention |
| `target_audience` | string |  |  |
| `channels` | array |  | Default: ['email', 'social'] |
| `duration_weeks` | integer |  | Default: 4 |
| `total_budget` | number |  | Default: 10000 |

#### `optimize_budget`

Optimize budget allocation across marketing channels based on historical ROAS data.

| Param | Type | Required | Description |
|---|---|---|---|
| `total_budget` | number | ✅ |  |
| `current_allocation` | object | ✅ | JSON of channel -> amount |
| `channel_performance` | object | ✅ | JSON of channel -> {roas, conversions} |
| `strategy` | string |  | Enum: roas_optimized, conversion_focused, awareness_focused, balanced Default: roas_optimized |


### Handoff (1)

#### `generate_brief`

Generate a self-contained campaign brief (handoff artifact) for any brand execution agent: positioning, budget split, posting windows, resolved BrandTokens, and execution contract. The agent can execute without calling back.

| Param | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | ✅ |  |
| `objective` | string | ✅ | Enum: awareness, consideration, conversion, lead_generation, retention |
| `product_name` | string | ✅ |  |
| `product_description` | string | ✅ |  |
| `target_audience` | string |  | Default: |
| `channels` | array |  | Default: ['social', 'email'] |
| `total_budget` | number |  | Default: 10000 |
| `duration_weeks` | integer |  | Default: 4 |
| `key_benefits` | array |  | Default: [] |
| `brand_tokens` | object |  | Brand kit: name, colors, font, handle, voice_notes |
| `channel_performance` | object |  | channel -> {spend, roas, contribution_margin, conversions} |
| `positioning_summary` | string |  | Default: |
| `competitor_insights` | string |  | Default: |


### Publishing (3)

#### `schedule_content`

Schedule a social media post to a platform via Postiz or direct API. Takes platform, content text, optional media URLs, scheduled time (ISO datetime), and hashtags. Falls back to PostizPublisher.publish_post() when platform=postiz.

| Param | Type | Required | Description |
|---|---|---|---|
| `platform` | string | ✅ | Enum: postiz, instagram, linkedin, twitter |
| `content_text` | string | ✅ |  |
| `media_urls` | array |  | Default: [] |
| `scheduled_time` | string |  | ISO datetime string, e.g. 2025-01-15T10:00:00 |
| `hashtags` | array |  | Default: [] |

#### `get_upcoming_posts`

Get all scheduled posts for the upcoming N days from the content calendar.

| Param | Type | Required | Description |
|---|---|---|---|
| `platform` | string |  | Default: |
| `days` | integer |  | Default: 7 |
| `limit` | integer |  | Default: 20 |

#### `optimize_hashtags`

Get optimized hashtags for a social media post. Returns a mix of trending and content-specific hashtags, respecting platform limits.

| Param | Type | Required | Description |
|---|---|---|---|
| `content_text` | string | ✅ |  |
| `platform` | string |  | Default: instagram |
| `limit` | integer |  | Default: 15 |


### UGC (3)

#### `curate_ugc`

Curate user-generated content for a given hashtag. Discovers posts via hashtag monitoring, filters by aesthetic score, and returns a list sorted by combined relevance + aesthetic score.

| Param | Type | Required | Description |
|---|---|---|---|
| `hashtag` | string | ✅ |  |
| `platform` | string |  | Default: instagram |
| `limit` | integer |  | Default: 10 |
| `min_aesthetic_score` | number |  | Default: 0.4 |

#### `request_ugc_permission`

Request permission from a UGC creator to repost their content. Sends a DM template (English or Indonesian) via platform API.

| Param | Type | Required | Description |
|---|---|---|---|
| `content_url` | string | ✅ |  |
| `platform` | string | ✅ |  |
| `message` | string |  | Default: |

#### `track_ugc`

Track UGC repost performance: reach, likes, comments, saves, and shares across platforms.

| Param | Type | Required | Description |
|---|---|---|---|
| `repost_id` | string | ✅ |  |
| `platform` | string | ✅ |  |


### Creative Templates (1)

#### `render_template`

Render a brand design template to a Paper MCP script or JSON layer spec. Accepts a template name, brand tokens (name, primary, background, accent, secondary, font, handle, tagline), and optional content overrides. Returns HTML/layers or a placeholders list if required content is missing.

| Param | Type | Required | Description |
|---|---|---|---|
| `template_name` | string | ✅ |  |
| `brand` | object | ✅ |  |
| `content_overrides` | object |  | Default: {} |


### Analytics (1)

#### `get_attribution`

Calculate multi-touch attribution across marketing channels using various models.

| Param | Type | Required | Description |
|---|---|---|---|
| `channel_points` | array | ✅ | Array of {channel, touchpoints, conversion_value} |
| `model` | string |  | Enum: first_touch, last_touch, linear, time_decay, position_based Default: linear |


### AI Ops (4)

#### `ensemble_vote`

Run ensemble voting across multiple AI models. Selects optimal model tier based on task complexity. Returns consensus decision with confidence score.

| Param | Type | Required | Description |
|---|---|---|---|
| `task_type` | string | ✅ | Enum: ad_copy, social_post, keyword_research, competitor_analysis, campaign_strategy, brand_voice_analysis, briefing_generation |
| `prompt` | string | ✅ |  |
| `context` | object |  | Default: {} |
| `models` | array |  | Default: [] |

#### `audit_log`

Log an AI marketing action with full audit trail. Records model, cost, confidence, reasoning chain, and human approval status.

| Param | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ |  |
| `model` | string |  | Default: |
| `input_tokens` | integer |  | Default: 0 |
| `output_tokens` | integer |  | Default: 0 |
| `cost` | number |  | Default: 0.0 |
| `confidence` | number |  | Default: 0.0 |
| `reasoning_chain` | array |  | Default: [] |
| `result_summary` | string |  | Default: |
| `human_approved` | boolean |  | Default: None |
| `brand_id` | string |  | Default: |
| `metadata` | object |  | Default: {} |

#### `audit_get_log`

Retrieve audit log entries with filtering by brand, action, and date range.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand_id` | string |  | Default: |
| `action` | string |  | Default: |
| `start_date` | string |  | Default: |
| `end_date` | string |  | Default: |
| `limit` | integer |  | Default: 100 |

#### `audit_get_cost_summary`

Get cost summary by model and action type for a date range.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand_id` | string |  | Default: |
| `start_date` | string |  | Default: |
| `end_date` | string |  | Default: |


### Hub (2)

#### `build_utm_url`

Build a UTM-tagged URL for campaign tracking.

| Param | Type | Required | Description |
|---|---|---|---|
| `base_url` | string | ✅ |  |
| `source` | string | ✅ |  |
| `medium` | string | ✅ |  |
| `campaign` | string | ✅ |  |
| `content` | string |  | Default: |
| `term` | string |  | Default: |

#### `parse_utm_params`

Extract UTM parameters from a URL.

| Param | Type | Required | Description |
|---|---|---|---|
| `url` | string | ✅ |  |


### GTM (26)

#### `analyze_competitor`

Deep-dive competitive analysis: positioning, messaging, ad strategy, audience targeting, strengths, weaknesses, and exploitable gaps.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string | ✅ |  |
| `category` | string |  | Default: |

#### `compare_competitors`

Compare your product against multiple competitors. Returns feature comparison matrix, price comparison, and strategic recommendations.

| Param | Type | Required | Description |
|---|---|---|---|
| `your_product` | string | ✅ |  |
| `competitors` | array | ✅ |  |

#### `analyze_positioning`

Analyze your brand's market positioning against competitors. Returns positioning map, differentiation strategy, and messaging framework.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string | ✅ |  |
| `product` | string |  | Default: |
| `industry` | string |  | Default: |

#### `launch_campaign_ad`

⚠️ REQUIRES APPROVAL. Launch a campaign ad via Composio integration (Meta, LinkedIn, Google Ads).

| Param | Type | Required | Description |
|---|---|---|---|
| `platform` | string | ✅ | Enum: meta, linkedin, google, hubspot, salesforce |
| `campaign_name` | string | ✅ |  |
| `budget_daily` | number |  | Default: 50 |
| `ad_creative` | string |  | JSON string of ad creative |
| `targeting` | string |  | JSON string of targeting params Default: {} |

#### `generate_narrative`

Generate brand narrative, stories, and messaging frameworks for marketing.

| Param | Type | Required | Description |
|---|---|---|---|
| `narrative_type` | string | ✅ | Enum: brand_story, founder_story, product_story, thought_leadership, industry_analysis |
| `brand` | string | ✅ |  |
| `industry` | string |  | Default: |
| `product` | string |  | Default: |

#### `hub_health_check`

Check health status of ALL connected marketing platforms. Returns connection status and capabilities.

*No parameters.*

#### `hub_broadcast_event`

Track an event across ALL connected marketing platforms simultaneously.

| Param | Type | Required | Description |
|---|---|---|---|
| `event_name` | string | ✅ |  |
| `contact_id` | string | ✅ |  |
| `properties` | object |  | Default: {} |
| `revenue` | number |  | Default: 0 |

#### `hub_sync_contact`

Sync a contact to ALL connected marketing platforms. Creates/updates profile across WebEngage, HubSpot, CleverTap, Braze, Mailchimp, etc.

| Param | Type | Required | Description |
|---|---|---|---|
| `contact_id` | string | ✅ |  |
| `email` | string | ✅ |  |
| `phone` | string |  | Default: |
| `first_name` | string |  | Default: |
| `last_name` | string |  | Default: |
| `company` | string |  | Default: |
| `lifecycle_stage` | string |  | Enum: lead, mql, sql, opportunity, customer, churned Default: lead |
| `attributes` | object |  | Default: {} |
| `tags` | array |  | Default: [] |

#### `hub_send_campaign`

Send a marketing campaign via the best available platform. Routes to Mailchimp, HubSpot, WebEngage, Braze, or CleverTap.

| Param | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | ✅ |  |
| `channel` | string |  | Enum: email, sms, push, whatsapp, in_app Default: email |
| `subject` | string |  | Default: |
| `content_html` | string |  | Default: |
| `segment_name` | string |  | Default: all |
| `preferred_platform` | string |  | Default: |

#### `hub_get_dashboard`

Get unified analytics dashboard across ALL connected marketing platforms. Aggregates metrics from WebEngage, CleverTap, Mixpanel, HubSpot, Braze, etc.

*No parameters.*

#### `hub_search_prospects`

Search for prospects using Clay data enrichment. Returns enriched company/contact data including title, company size, tech stack, funding, and social profiles.

| Param | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ |  |
| `limit` | integer |  | Default: 10 |

#### `hub_create_segment`

Create an audience segment across ALL connected marketing platforms.

| Param | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ |  |
| `conditions` | array |  | Default: [] |
| `description` | string |  | Default: |

#### `hub_send_transactional`

Send a transactional message (single contact) via the best platform for the channel.

| Param | Type | Required | Description |
|---|---|---|---|
| `contact_id` | string | ✅ |  |
| `channel` | string |  | Enum: email, sms, push, whatsapp, in_app Default: email |
| `title` | string |  | Default: |
| `body` | string | ✅ |  |
| `deep_link` | string |  | Default: |

#### `hub_list_platforms`

List all supported marketing platforms and their capabilities. Returns platform features, supported channels, and connection status.

*No parameters.*

#### `crm_create_lead`

Create a new CRM lead from marketing data. Stores lead with email, name, company, source, and scoring data.

| Param | Type | Required | Description |
|---|---|---|---|
| `email` | string | ✅ |  |
| `first_name` | string |  | Default: |
| `last_name` | string |  | Default: |
| `phone` | string |  | Default: |
| `company` | string |  | Default: |
| `job_title` | string |  | Default: |
| `source` | string |  | Enum: organic, paid, referral, social, cold_outreach Default: organic |
| `tags` | array |  | Default: [] |

#### `crm_create_deal`

Create a new deal/opportunity from a lead. Sets deal value, stage, and links to lead.

| Param | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ |  |
| `value` | number |  | Default: 0 |
| `stage` | string |  | Enum: lead, qualified, proposal, negotiation, closed_won, closed_lost Default: lead |
| `lead_id` | string |  | Default: |
| `owner_id` | string |  | Default: |

#### `crm_move_deal`

Move a deal to a new pipeline stage. Updates probability and logs stage history.

| Param | Type | Required | Description |
|---|---|---|---|
| `deal_id` | string | ✅ |  |
| `new_stage` | string | ✅ | Enum: lead, qualified, proposal, negotiation, closed_won, closed_lost |

#### `crm_log_activity`

Log an activity (call, email, meeting, note) on a lead or deal.

| Param | Type | Required | Description |
|---|---|---|---|
| `entity_id` | string | ✅ |  |
| `activity_type` | string | ✅ | Enum: call, email, meeting, note, task, campaign |
| `subject` | string |  | Default: |
| `notes` | string |  | Default: |
| `duration_minutes` | integer |  | Default: 0 |

#### `crm_get_dashboard`

Get CRM dashboard with lead/deal pipeline metrics.

*No parameters.*

#### `crm_search_leads`

Search CRM leads by name, email, or company.

| Param | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ |  |
| `limit` | integer |  | Default: 10 |

#### `crm_get_pipeline`

Get deal pipeline summary with values per stage.

*No parameters.*

#### `crm_get_timeline`

Get timeline of all activities and stage changes for a lead or deal.

| Param | Type | Required | Description |
|---|---|---|---|
| `entity_id` | string | ✅ |  |

#### `run_workflow`

Execute a multi-step marketing workflow. Chain operations: sync_contact → create_segment → send_campaign.

| Param | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string | ✅ |  |
| `name` | string |  | Default: |
| `steps` | array | ✅ |  |
| `first_step` | string | ✅ |  |

#### `analyze_competitor_ad`

Deconstruct a competitor ad (image/video frame URL or local path) via VLM: hook, pacing, psychological triggers, CTA, counter-angles. Falls back to copy heuristics when no vision backend available. Use derive=true to aggregate multiple ads into a counter-brief for generate_creatives.

| Param | Type | Required | Description |
|---|---|---|---|
| `image_path_or_url` | string |  | Default: |
| `transcript` | string |  | Default: |
| `caption` | string |  | Default: |
| `batch` | array |  | list of {image_path_or_url, transcript, caption} |
| `derive` | boolean |  | return aggregated counter-brief instead of raw breakdowns Default: False |

#### `breakdown_ad`

Break down a competitor ad into its structural components: hook, offer, call-to-action, emotional triggers, pacing, and format. Works from a URL (uses Ollama vision model locally if available, falls back to cloud vision then heuristic parsing) or from raw ad copy text. Optionally enrich with brand context.

| Param | Type | Required | Description |
|---|---|---|---|
| `ad_url_or_text` | string | ✅ | URL to competitor ad image/video, or raw ad copy text if no URL |
| `brand_name` | string |  | Name of the competitor brand for context Default: |
| `analysis_depth` | string |  | Depth of analysis: quick (heuristic only), standard (VLM if available), deep (full VLM with extended output) Enum: quick, standard, deep Default: standard |

#### `search_fb_ads`

Search Facebook Ads Library for REAL competitor ad creatives, copy and delivery data (ground truth, not VLM guessing). Requires FB_ACCESS_TOKEN env var.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand_name` | string | ✅ | Advertiser/brand to search |
| `country` | string |  | Default: ALL |
| `limit` | integer |  | Default: 20 |


---

## Error Handling

| Code | Meaning | Fix |
|---|---|---|
| `-32601` | Unknown tool | Check `tools/list` for exact names |
| Missing required param | Validation error | See ✅ column in tool reference |
| Graceful degradation | Optional backend unavailable | Set the relevant env key (FB_ACCESS_TOKEN, SERPER_API_KEY, etc.) |

---
*Auto-generated from mcp_server.py TOOLS — regenerate after adding tools.*