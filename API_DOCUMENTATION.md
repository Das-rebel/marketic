# Marketic MCP Server — API Documentation

> **Version:** 2.0.0 | **Tools:** 43 | **Protocol:** JSON-RPC 2.0 over stdio
> **Regenerated from the live server's TOOLS list — cannot drift from code.**

## Protocol Reference

```bash
python3 mcp_server.py
# list all tools:
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | python3 mcp_server.py
# call a tool:
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"signal_fanout","arguments":{"query":"ai"}},"id":2}' | python3 mcp_server.py
```

## Tool Reference (43 tools)


### Router (1)

#### `ask_marketic`

Master router - one entry point for Marketic.

| Param | Type | Required | Description |
|---|---|---|---|
| `question` | string | ✅ | Natural-language marketing question or task |
| `route_only` | boolean |  |  |
| `arguments` | object |  | Optional arguments passed through to the routed tool |


### Intelligence (2)

#### `collect_signals`

Collect marketing signals from Product Hunt, Hacker News, Twitter, Reddit for a brand.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string | ✅ |  |
| `days` | integer |  |  |
| `sources` | array |  |  |

#### `signal_fanout`

Parallel multi-source signal search (Product Hunt, HN, Twitter, Reddit, Polymarket) with cross-source engagement normalization.

| Param | Type | Required | Description |
|---|---|---|---|
| `query` | string |  |  |
| `sources` | array |  |  |
| `limit_per_source` | integer |  |  |


### GTM (25)

#### `analyze_competitor`

Deep-dive competitive analysis: positioning, messaging, ad strategy, audience targeting, strengths, weaknesses, and exploitable gaps.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string | ✅ |  |
| `category` | string |  |  |

#### `compare_competitors`

Compare your product against multiple competitors.

| Param | Type | Required | Description |
|---|---|---|---|
| `your_product` | string | ✅ |  |
| `competitors` | array | ✅ |  |

#### `analyze_positioning`

Analyze your brand's market positioning against competitors.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string | ✅ |  |
| `product` | string |  |  |
| `industry` | string |  |  |

#### `launch_campaign_ad`

⚠️ REQUIRES APPROVAL.

| Param | Type | Required | Description |
|---|---|---|---|
| `platform` | string | ✅ |  |
| `campaign_name` | string | ✅ |  |
| `budget_daily` | number |  |  |
| `ad_creative` | string |  | JSON string of ad creative |
| `targeting` | string |  | JSON string of targeting params |

#### `generate_narrative`

Generate brand narrative, stories, and messaging frameworks for marketing.

| Param | Type | Required | Description |
|---|---|---|---|
| `narrative_type` | string | ✅ |  |
| `brand` | string | ✅ |  |
| `industry` | string |  |  |
| `product` | string |  |  |

#### `hub_health_check`

Check health status of ALL connected marketing platforms.

#### `hub_broadcast_event`

Track an event across ALL connected marketing platforms simultaneously.

| Param | Type | Required | Description |
|---|---|---|---|
| `event_name` | string | ✅ |  |
| `contact_id` | string | ✅ |  |
| `properties` | object |  |  |
| `revenue` | number |  |  |

#### `hub_sync_contact`

Sync a contact to ALL connected marketing platforms.

| Param | Type | Required | Description |
|---|---|---|---|
| `contact_id` | string | ✅ |  |
| `email` | string | ✅ |  |
| `phone` | string |  |  |
| `first_name` | string |  |  |
| `last_name` | string |  |  |
| `company` | string |  |  |
| `lifecycle_stage` | string |  |  |
| `attributes` | object |  |  |
| `tags` | array |  |  |

#### `hub_send_campaign`

Send a marketing campaign via the best available platform.

| Param | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | ✅ |  |
| `channel` | string |  |  |
| `subject` | string |  |  |
| `content_html` | string |  |  |
| `segment_name` | string |  |  |
| `preferred_platform` | string |  |  |

#### `hub_get_dashboard`

Get unified analytics dashboard across ALL connected marketing platforms.

#### `hub_search_prospects`

Search for prospects using Clay data enrichment.

| Param | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ |  |
| `limit` | integer |  |  |

#### `hub_create_segment`

Create an audience segment across ALL connected marketing platforms.

| Param | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ |  |
| `conditions` | array |  |  |
| `description` | string |  |  |

#### `hub_send_transactional`

Send a transactional message (single contact) via the best platform for the channel.

| Param | Type | Required | Description |
|---|---|---|---|
| `contact_id` | string | ✅ |  |
| `channel` | string |  |  |
| `title` | string |  |  |
| `body` | string | ✅ |  |
| `deep_link` | string |  |  |

#### `hub_list_platforms`

List all supported marketing platforms and their capabilities.

#### `crm_create_lead`

Create a new CRM lead from marketing data.

| Param | Type | Required | Description |
|---|---|---|---|
| `email` | string | ✅ |  |
| `first_name` | string |  |  |
| `last_name` | string |  |  |
| `phone` | string |  |  |
| `company` | string |  |  |
| `job_title` | string |  |  |
| `source` | string |  |  |
| `tags` | array |  |  |

#### `crm_create_deal`

Create a new deal/opportunity from a lead.

| Param | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ |  |
| `value` | number |  |  |
| `stage` | string |  |  |
| `lead_id` | string |  |  |
| `owner_id` | string |  |  |

#### `crm_move_deal`

Move a deal to a new pipeline stage.

| Param | Type | Required | Description |
|---|---|---|---|
| `deal_id` | string | ✅ |  |
| `new_stage` | string | ✅ |  |

#### `crm_log_activity`

Log an activity (call, email, meeting, note) on a lead or deal.

| Param | Type | Required | Description |
|---|---|---|---|
| `entity_id` | string | ✅ |  |
| `activity_type` | string | ✅ |  |
| `subject` | string |  |  |
| `notes` | string |  |  |
| `duration_minutes` | integer |  |  |

#### `crm_get_dashboard`

Get CRM dashboard with lead/deal pipeline metrics.

#### `crm_search_leads`

Search CRM leads by name, email, or company.

| Param | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ |  |
| `limit` | integer |  |  |

#### `crm_get_pipeline`

Get deal pipeline summary with values per stage.

#### `crm_get_timeline`

Get timeline of all activities and stage changes for a lead or deal.

| Param | Type | Required | Description |
|---|---|---|---|
| `entity_id` | string | ✅ |  |

#### `run_workflow`

Execute a multi-step marketing workflow.

| Param | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string | ✅ |  |
| `name` | string |  |  |
| `steps` | array | ✅ |  |
| `first_step` | string | ✅ |  |

#### `analyze_competitor_ad`

Deconstruct a competitor ad (image/video frame URL or local path) via VLM: hook, pacing, psychological triggers, CTA, counter-angles.

| Param | Type | Required | Description |
|---|---|---|---|
| `image_path_or_url` | string |  |  |
| `transcript` | string |  |  |
| `caption` | string |  |  |
| `batch` | array |  | list of {image_path_or_url, transcript, caption} |
| `derive` | boolean |  | return aggregated counter-brief instead of raw breakdowns |

#### `search_fb_ads`

Search Facebook Ads Library for REAL competitor ad creatives, copy and delivery data (ground truth, not VLM guessing).

| Param | Type | Required | Description |
|---|---|---|---|
| `brand_name` | string | ✅ | Advertiser/brand to search |
| `country` | string |  |  |
| `limit` | integer |  |  |


### Creative (3)

#### `generate_creatives`

Generate ad copy variants across channels (Google, Meta, LinkedIn, etc.

| Param | Type | Required | Description |
|---|---|---|---|
| `product_name` | string | ✅ |  |
| `product_description` | string | ✅ |  |
| `channel` | string |  |  |
| `objective` | string |  |  |
| `target_audience` | string |  |  |
| `key_benefits` | array |  |  |
| `num_variants` | integer |  |  |
| `tone` | string |  |  |

#### `generate_social_posts`

Generate platform-specific social media posts (LinkedIn, X/Twitter, Instagram, Facebook).

| Param | Type | Required | Description |
|---|---|---|---|
| `topic` | string | ✅ |  |
| `platform` | string |  |  |
| `format` | string |  |  |
| `tone` | string |  |  |
| `length` | integer |  |  |
| `hashtags` | boolean |  |  |

#### `generate_seo_content`

Generate SEO-optimized content including meta titles, descriptions, headers, and FAQs for target keywords.

| Param | Type | Required | Description |
|---|---|---|---|
| `target_keyword` | string | ✅ |  |
| `content_type` | string |  |  |
| `word_count` | integer |  |  |
| `competitor_url` | string |  |  |


### Campaigns (2)

#### `build_campaign`

Build a complete multi-channel campaign strategy with channel-specific tactics, budgets, and timelines.

| Param | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | ✅ |  |
| `objective` | string | ✅ |  |
| `target_audience` | string |  |  |
| `channels` | array |  |  |
| `duration_weeks` | integer |  |  |
| `total_budget` | number |  |  |

#### `optimize_budget`

Optimize budget allocation across marketing channels based on historical ROAS data.

| Param | Type | Required | Description |
|---|---|---|---|
| `total_budget` | number | ✅ |  |
| `current_allocation` | object | ✅ | JSON of channel -> amount |
| `channel_performance` | object | ✅ | JSON of channel -> {roas, conversions} |
| `strategy` | string |  |  |


### Handoff (1)

#### `generate_brief`

Generate a self-contained campaign brief (handoff artifact) for any brand execution agent: positioning, budget split, posting windows, resolved BrandTokens, and execution contract.

| Param | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | ✅ |  |
| `objective` | string | ✅ |  |
| `product_name` | string | ✅ |  |
| `product_description` | string | ✅ |  |
| `target_audience` | string |  |  |
| `channels` | array |  |  |
| `total_budget` | number |  |  |
| `duration_weeks` | integer |  |  |
| `key_benefits` | array |  |  |
| `brand_tokens` | object |  | Brand kit: name, colors, font, handle, voice_notes |
| `channel_performance` | object |  | channel -> {spend, roas, contribution_margin, conversions} |
| `positioning_summary` | string |  |  |
| `competitor_insights` | string |  |  |


### Analytics (1)

#### `get_attribution`

Calculate multi-touch attribution across marketing channels using various models.

| Param | Type | Required | Description |
|---|---|---|---|
| `channel_points` | array | ✅ | Array of {channel, touchpoints, conversion_value} |
| `model` | string |  |  |


### Learning (1)

#### `distill_learnings`

Promote recurring audit-trail patterns into brand learnings; optionally capture an explicit rule; export brain/<brand>.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand` | string |  |  |
| `capture_rule` | string |  | If set, capture this rule instead of distilling |
| `category` | string |  |  |
| `min_occurrences` | integer |  |  |
| `export_brain` | boolean |  |  |


### CRM Growth Loop (1)

#### `run_prospect_loop`

Signal-driven prospecting (JoeCRM pattern): discover prospects matching a niche, enrich with live market signals, auto-draft personalized outreach, insert scored leads into CRM.

| Param | Type | Required | Description |
|---|---|---|---|
| `niche_query` | string | ✅ | Who to prospect, e.g. 'D2C skincare brands founder' |
| `market_query` | string |  | Market topic for signal enrichment |
| `limit` | integer |  |  |


### Hub (2)

#### `build_utm_url`

Build a UTM-tagged URL for campaign tracking.

| Param | Type | Required | Description |
|---|---|---|---|
| `base_url` | string | ✅ |  |
| `source` | string | ✅ |  |
| `medium` | string | ✅ |  |
| `campaign` | string | ✅ |  |
| `content` | string |  |  |
| `term` | string |  |  |

#### `parse_utm_params`

Extract UTM parameters from a URL.

| Param | Type | Required | Description |
|---|---|---|---|
| `url` | string | ✅ |  |


### AI Ops (4)

#### `ensemble_vote`

Run ensemble voting across multiple AI models.

| Param | Type | Required | Description |
|---|---|---|---|
| `task_type` | string | ✅ |  |
| `prompt` | string | ✅ |  |
| `context` | object |  |  |
| `models` | array |  |  |

#### `audit_log`

Log an AI marketing action with full audit trail.

| Param | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ |  |
| `model` | string |  |  |
| `input_tokens` | integer |  |  |
| `output_tokens` | integer |  |  |
| `cost` | number |  |  |
| `confidence` | number |  |  |
| `reasoning_chain` | array |  |  |
| `result_summary` | string |  |  |
| `human_approved` | boolean |  |  |
| `brand_id` | string |  |  |
| `metadata` | object |  |  |

#### `audit_get_log`

Retrieve audit log entries with filtering by brand, action, and date range.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand_id` | string |  |  |
| `action` | string |  |  |
| `start_date` | string |  |  |
| `end_date` | string |  |  |
| `limit` | integer |  |  |

#### `audit_get_cost_summary`

Get cost summary by model and action type for a date range.

| Param | Type | Required | Description |
|---|---|---|---|
| `brand_id` | string |  |  |
| `start_date` | string |  |  |
| `end_date` | string |  |  |


---

## Error Handling

| Code | Meaning | Fix |
|---|---|---|
| `-32601` | Unknown tool | Check `tools/list` for exact names |
| Missing required param | Validation error | See ✅ column in tool reference |
| Graceful degradation | Optional backend unavailable | Set the relevant env key (FB_ACCESS_TOKEN, SERPER_API_KEY, etc.) |

---
*Auto-generated from mcp_server.py TOOLS — regenerate after adding tools.*