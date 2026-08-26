# Council Round 2 — Re-suggestions After Vault + GitHub Mining

*Input: 7 missed builds from Round-1 audit + newly found solutions from bookmark vault & GitHub.*
*Verdict theme: several "build" plans should become "wire up existing infrastructure" plans.*

---

## The Big Call: Change the Plan on Gap 1

**Council verdict: STOP building local VLM guesswork. Route ad intelligence through the Facebook Ads Library MCP instead.**

| | Old plan | New evidence |
|---|---|---|
| Approach | `ollama pull llava` → vision model *guesses* what an ad image means | [proxy-intell/facebook-ads-library-mcp](https://github.com/proxy-intell/facebook-ads-library-mcp) (**293★**) queries the FB Ad Library directly |
| Data quality | Inferred hooks/triggers from pixels | **Real creatives, real copy, real spend data** — ground truth, not interpretation |
| Effort | Model download + prompt engineering + GPU cycles | One MCP server config |
| Fits architecture? | Builds what exists elsewhere | **Orchestrate-don't-build** — our own stated principle |

Local VLM demotes to a fallback for ads not present in the Ad Library (TikTok/organic).
Gemma 4 12B Dynamic GGUF (8GB RAM) noted as the fallback backend if ever needed.

---

## Per-Gap Recommendations

### Gap 1 — Ad analysis → `facebook-ads-library-mcp` ✅ CHANGE THE PLAN
Wire the MCP server into `gtm/ad_analysis.py` as the *primary* backend; keep heuristics
as last-resort fallback. `analyze_competitor_ad` gains real spend data — something no
image-VLM could ever provide.

### Gap 2 — Scheduler → GitHub Actions cron ⚡ SIMPLER THAN PLANNED
Crontab requires sysadmin care; APScheduler adds a process to babysit.
A scheduled GitHub Action is free, visible (run history in the repo), logs persist,
and the briefing markdown can be committed back or dispatched via webhook.
**Recommendation:** GH Action on schedule + webhook dispatch; crontab only if latency matters.

### Gap 3 — Prospect→CRM loop → adopt the JoeCRM pattern 🔺 UPGRADE THE PLAN
[JoeCRM](https://x.com/AlexReibman/status/1789894464577671468): AI-first CRM that
*receives signals about customers → researches them automatically → drafts outreach*.
Not "wire Serper into add_lead" but make CRM **signal-driven**: signal fan-out already
detects demand topics → match against prospect list → auto-research → draft outreach
with the brief generator. Same plumbing we built, connected in a smarter order.

### Gap 4 — Brain files → extend audit_trail, don't add a parallel system
Three options evaluated. The SQLite audit trail already logs every decision with
reasoning chains. Adding Helena-style markdown brains would duplicate storage.
**Recommendation:** add a `learnings` table + a `distill_learnings()` job that
promotes recurring audit-trail patterns into brand-level learnings; export to
`brain/<brand>.md` for human PR review. One source of truth, git-visible output.

### Gap 5 — Ad launch → keep stubbed, revisit after Gap 1
facebook-ads-library-mcp is read-focused. Composio integration remains the path for
*writing* ads, but launching spend before the intelligence loop is complete is
premature. Deprioritized by consensus.

### Gap 6 — SEO opportunities → accept `opportunity_signals`, free sources first
Shape confirmed: `{keyword, difficulty, serp_gap[]}` input on `generate_seo_content`.
Free data paths: Reddit page-1 opportunity scanning (ConnorShowler pattern) before any
paid API. Generate *against* documented gaps.

### Gap 7 — TikTok → yt-dlp subtitles, not scrapers
Apify actors cost $0.90/1K; `yt-dlp --write-auto-sub` is free and already battle-tested
in our stack. Add TikTok as fan-out source #6 via subtitle extraction.

---

## Compounding Insight (council's cross-cutting finding)

> **Gaps 1+3 share one root:** Marketic detects signals but doesn't act on them end-to-end.
> Fixing Gap 3 (signal-driven CRM) makes Gaps 1/6/7 more valuable because every source
> added feeds outreach, not just dashboards. Build order should optimize the *loop*,
> not individual features.

## Suggested Build Order

| Day | Item | Why first |
|---|---|---|
| 1 | Gap 2: GH Action scheduler | Heartbeat enables everything else to run autonomously |
| 1–2 | Gap 1: FB Ads Library MCP wiring | Biggest capability jump, config-level effort |
| 2–3 | Gap 3: JoeCRM-style loop | Turns intelligence into pipeline |
| 4 | Gap 4: learnings distillation | Starts compounding knowledge |
| 5 | Gaps 6+7: SEO inputs + TikTok source | Cheap additive wins |

---
*Council round 2 · solutions sourced from bookmark vault + GitHub mining · supersedes round-1 build plans where marked.*
