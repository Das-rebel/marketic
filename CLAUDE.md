# Marketic — AI Assistant Guide

Current-state reference for AI assistants (Claude Code, Cursor, PI) working in this repo.

## What Marketic Is Now (2026-08-26)

A white-label marketing strategy brain: probability-calibrated signal fan-out →
ensemble AI reasoning → self-contained briefs that execution agents consume.
Every decision audited; the core calibration claim is measured with Brier scores.

**43 MCP tools** over stdio JSON-RPC (`mcp_server.py`). **23 tests** (`pytest tests/ --confcutdir=. -o addopts=""`).

## The Loop

```
SENSE   signals/collectors.py — 6 sources, volume × P(YES) scoring,
        auto-snapshots prediction markets into analytics/scorecard.py
THINK   ensemble/voting.py + audit_trail.py · gtm/ad_analysis.py
        (FB Ads Library rung 1 via FB_ACCESS_TOKEN, then vision, then heuristics)
        campaign/budget_router.py — margin-adjusted allocation
HANDOFF execution/brief.py — generate_brief() → versioned JSON contract
        (docs/BRIEF_SCHEMA.md v1.0) with evidence_chain + brand_rules
LEARN   audit trail → ensemble/learnings.py distills patterns →
        brain/<brand>.md for human PR review → approved rules re-injected
        into future briefs (docs/BRAIN_WORKFLOW.md)
```

## Hard Rules

1. **No `from marketic.*` imports.** The nested legacy package was deleted
   (round-2 P0); CI greps for regressions. Top-level modules only:
   `from signals.collectors import ...`
2. **Brief schema is additive-only within v1.x.** New fields must be optional;
   existing keys never change type. Update docs/BRIEF_SCHEMA.md + the lock test.
3. **Zero hardcoded brands.** All identity flows through BrandTokens
   (execution/design_templates.py).
4. **New MCP tools need:** handler fn + HANDLERS entry + TOOLS schema entry +
   API_DOCUMENTATION.md row + ask_marketic route if user-facing.
5. **Scorecard/fan-out failures must never crash the briefing.** Wrap and degrade.
6. **pytest needs `--confcutdir=. -o addopts=""`** on this machine (stray ~/conftest.py).
7. **Bot conflict rule:** logs/briefing_*.md conflicts on rebase → bot's version wins.

## Key Files

| File | Role |
|---|---|
| `mcp_server.py` | 43-tool stdio server; HANDLERS + TOOLS must stay in sync |
| `daily_briefing.py` | Cronnable digest; also runs as GitHub Action 08:00 UTC |
| `signals/collectors.py` | SignalFanout + PolymarketCollector (P(YES) logic lives here) |
| `analytics/scorecard.py` | Prediction tracking, Gamma-API auto-resolution, Brier score |
| `ensemble/learnings.py` | LearningEngine: capture/distill/export_brain_md |
| `crm/prospect_loop.py` | JoeCRM-style signal-driven prospecting |
| `execution/brief.py` | generate_brief — the agent handoff artifact |
| `npm_dist/` | npm wrapper; bundles domain modules — resync after tool changes |

## Region Profiles

`SignalFanout().run(query, region=...)` supports `global`, `us` (default behavior), and `india`. Profile definitions live in the `REGION_PROFILES` dict in `signals/collectors.py`. The india profile adds google_trends (Trends India, geo=IN rising queries), indian_media (ET Brand Equity / Afaqs / YourStory / Inc42 / Mint RSS), and youtube (yt-dlp search ranked by view count); it excludes polymarket (near-zero India markets) and tiktok (banned in India since 2020) while keeping twitter and reddit. Use `expand_hinglish()` in the same module to broaden English queries with Hinglish variants for Indian social search.

## Docs Map

- README.md — manager-first overview
- API_DOCUMENTATION.md — regenerated from TOOLS list (source of truth)
- docs/BRIEF_SCHEMA.md — handoff contract (additive-only v1.x)
- docs/BRAIN_WORKFLOW.md — learning loop end-to-end
- docs/COUNCIL_ROUND2.md + docs/archive/ — decision history
- llms.txt — AI-discoverable summary (keep updated when tools change)

## Environment Keys (all optional, all degrade gracefully)

FB_ACCESS_TOKEN · SERPER_API_KEY · OPENROUTER_API_KEY · OPENCODE_GO_TOKEN ·
OLLAMA_BASE (default 127.0.0.1:11434) · MARKETIC_BRIEF_WEBHOOK
