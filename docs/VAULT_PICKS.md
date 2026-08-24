# Vault Picks — What We're Taking From the Bookmark Vault

Mined 18K+ bookmarks against the v2 architecture (strategy brain + brand-as-data +
orchestrate-don't-build). These are the picks that fit, ranked by fit.

---

## TIER 1 — Directly upgrades existing modules

### 1. Parallel multi-source signal search → rewrite `signals/collectors.py`
**Source:** `last30days-skill` (mvanhorn, +2.1K★ in a week) — https://github.com/mvanhorn/last30days-skill
via @gusik4ever + @sharbel
> Searches Reddit, X, YouTube, HN, Polymarket & web **in parallel**, scores by real
> upvotes/likes/money, synthesizes into one brief.

**Why it fits:** Our collectors run per-platform, unscored, unsynthesized. This is
exactly the ensemble pattern we already use for LLMs — applied to signals.
**Action:** Adopt the pattern: parallel fan-out → engagement-weighted score → single
synthesized brief. Polymarket adds a *prediction market* dimension no other signal
source has (market-implied demand).

### 2. Contribution-margin budgeting → fix `campaign/budget_router.py`
**Source:** eComm metrics tier list — instagram.com/p/DW3P95Sj2Cj
> S-tier (daily): contribution margin, new vs returning split. Break-even CAC is foundational.

**Why it fits:** Our budget router optimizes raw ROAS — which is vanity when margin
varies by channel/product. 
**Action:** Add `contribution_margin` and `break_even_cac` to ChannelPerformance;
optimize on margin-adjusted ROAS. Cheap change, big correctness win.

### 3. Style-cloning bootstrap → new `BrandTokens.from_image()`
**Source:** @EXM7777 3-step style-cloning system — x.com/EXM7777/status/1942675329371496661
> Vision model extracts style descriptors from any reference image.

**Why it fits:** Brand-as-data currently requires someone to type in hex codes.
This bootstraps tokens from one screenshot of the brand.
**Action:** `BrandTokens.from_image(url)` — vision call extracts palette/type/tone
into a token dict. Onboarding goes from form-filling to one image.

---

## TIER 2 — New capabilities the architecture wants

### 4. Competitive ad deconstruction → new `gtm/ad_analysis.py`
**Source:** Gemma4 watching video ads in bulk — instagram.com/p/DW3GltTDFE_
> Local VLM "watches" competitor video ads frame-by-frame: visual hooks, pacing,
> psychological triggers.

**Why it fits:** `gtm/competitive.py` is text-only. Competitor *creative* intel is the
missing input to `generate_creatives` — counter-variants need to know what they're
countering. Local VLM (Gemma/Qwen-VL) = free, private, bulk.
**Action:** Ingest competitor ad URLs → VLM extracts hook/pacing/trigger structure →
feeds creative generation prompts.

### 5. The agent org chart → validate + build the `generate_brief` handoff
**Source:** @tibo_maker hired 7 agents (Tai lead coordinator, Nina outreach, ...) — x.com/tibo_maker/status/2059930221680189744
**Also:** @ericosiu "single brains for companies" — x.com/ericosiu/status/2061084530325540981

**Why it fits:** This is *exactly* our strategy-brain + execution-agents split, proven
in production by tibo. Lead brain produces briefs; specialist agents execute.
**Action:** Build `generate_brief` MCP tool: outputs a self-contained JSON brief
(positioning + copy variants + budget + hashtags + optimal times + resolved BrandTokens)
that any Helena-style execution agent can consume without talking back.

### 6. Autonomous ads agent → wire up the `launch_campaign_ad` stub
**Source:** @codyschneider deployed agent running Google Search ads day one — x.com/codyschneider/status/2058911033004032235

**Why it fits:** Our launch tool returns "requires approval — connect Composio."
The vault shows this is shipping in production now.
**Action:** Route through existing Composio MCP instead of building platform integrations.
Orchestrate-don't-build applies here most of all.

---

## TIER 3 — Grounding data for generators

### 7. SEO opportunity inputs → upgrade `creative/seo_generator.py`
- @ConnorShowler Reddit SEO tool: keywords with page-1 ranking opportunities — x.com/ConnorShowler/status/2056912224468238838
- @timsoulo Ahrefs: 1B datapoints across 14 studies — x.com/timsoulo/status/2061796432534003866

**Action:** SEO generator should accept `opportunity_signals` (keyword difficulty,
SERP gaps, reddit thread targets), not just a bare keyword. Generate *against* gaps.

### 8. Cheap competitor content intel → feed `signals/`
- TikTok Transcript Scraper ($0.90/1K) — x.com/maximehugodupre/status/2057921723429945552
- Top-seller scrape + Seedance + Claude Code — x.com/Mho_23/status/2055316066935722245

**Action:** Add TikTok as a signals source (transcripts are cheap). Competitor
best-sellers = demand ground truth.

### 9. Distribution-first thesis → positioning copy for README
**Source:** @levelsio — everyone builds apps; nobody has distribution — x.com/levelsio/status/2063183917033701708

**Action:** One-liner for positioning: Marketic optimizes the distribution side,
which is the actual bottleneck.

---

## Explicitly Rejected (found in vault, doesn't fit)

| Found | Why rejected |
|-------|-------------|
| MoneyPrinterTurbo-style full-auto video | We orchestrate Runway etc.; don't host video pipelines |
| OmniVoice local voice cloning | Voice-over is execution-agent territory |
| $50K OpenAI credits hacks / API resellers | Not architecture; ops detail |
| Miora all-in-one creative studio | It's a competitor product, not a component |

---

## Sequencing

1. **Now:** #2 (margin budgeting — small diff), #7 (SEO inputs)
2. **Next:** #1 (signal fan-out rewrite — biggest architectural payoff)
3. **Then:** #5 (`generate_brief` — unlocks execution agents), #3 (tokens from image)
4. **Later:** #4 (VLM ad analysis — needs local VLM setup)

*vault: 17,874 items · searched 2026-08-24*
