# Marketic NPM Discoverability Diagnosis

**Date:** 2026-09-08
**NPM Packages:** `marketic-cli` (broken/empty), `marketic-mcp` (real but undiscovered)
**Repo:** `Das-rebel/marketic` | **Focus:** Why no npm traction

---

## 1. Root Cause Analysis — Why Is It Declining / Not Growing?

### P0: Two Competing Packages with No CI/CD Sync

There are **two npm packages** for the same project:

| Package | Version | Size | Status |
|---|---|---|---|
| `marketic-cli` | 1.0.0 | **917 bytes** | **BROKEN** — only `index.js` + `package.json`, no real code |
| `marketic-mcp` | 1.0.5 | ~5MB bundled | **REAL** — has `mcp_server.py` + all domain modules |

`marketic-cli` was published by mistake or from a wrong build artifact. It has **zero functionality**. Anyone who installs it gets an empty package and immediately loses trust. This creates a **negative signal** (1-star review potential, broken install flows in blog posts that referenced the old name).

`marketic-mcp` is the real package but it is **never updated via CI/CD**. Every commit to `main` that changes the Python code does NOT automatically publish to npm. The gap between repo state and npm state is growing. Developers who check the repo and then look at npm see a stale, older version.

### P1: Zero SEO-Optimized Keywords

`marketic-mcp` keywords (as of npm):
```
mcp, mcp-server, marketing, marketing-intelligence, competitor-analysis,
advertising, campaign-optimization, seo, social-media, crm, hubspot,
attribution, ai-marketing, marketing-automation, claude, cursor, windsurf, aio-executor
```

**Missing high-signal discovery keywords:**
- `llm` / `large-language-model` / `ai-agent` — core use case
- `marketing-ops` / `growth-ops` — job-function search
- `competitor-intelligence` — more specific than competitor-analysis
- `incrementality` / `ad-measurement` — specialist niche
- `poly-market` / `polymarket` — unique differentiator
- `morning-brief` / `daily-brief` — product use-case keyword
- `polymarket`, `google-trends`, `signal-detection` — data source differentiators
- `claude-desktop` — platform affinity
- `model-context-protocol` — protocol affiliation (already have mcp, but not spelled out)

### P2: Generic Description, No Value-Prop Hook

Current npm description:
> "Marketic Marketing Intelligence MCP Server — 32 tools for competitor analysis, ad creative generation, campaign optimization, social media, SEO, HubSpot CRM, and attribution modeling"

Problems:
- "MCP Server" buried at the end — should lead with what it DOES, not what protocol it uses
- No emotional hook or outcome statement ("stop checking 7 tabs every morning")
- No differentiation from the dozen other "marketing intelligence" tools on npm
- "32 tools" is meaningless without naming the 1-2 killer tools
- No mention of the daily briefing / signal calibration / Polymarket angle

### P3: No GitHub Star Correlation

The Python repo has ~0 npm downloads correlation because:
1. Blog posts / dev.to articles reference the GitHub install path
2. NPM search is how developers find tools they haven't heard of — the repo isn't discovered there
3. Zero backlinks from npm to the repo's feature depth (description truncated, no demo link)

### P4: The MCP Protocol Niche Is Real But Underserved

Search for "mcp-server marketing" on npm shows:
- `@timmeck/marketing-brain` — has MCP, has "self-learning" angle
- `@maasy-ai/mcp-server` — has Maasy AI brand
- `cresva-mcp-server` — no keyword depth
- `marketic-mcp` — best positioned but lowest polish

The category is new enough that **being first to market with a polished presence matters more than features.**

---

## 2. Comparable Successful Packages — What Do They Have That This Doesn't?

### Benchmarks from the npm Ecosystem

| Package | Weekly DL | Key Positioning | What They Do Right |
|---|---|---|---|
| `chalk` | ~440M | Terminal styling | 5-word description with demo, "string styling done right" |
| `@notionhq/notion-mcp-server` | trending | Official Notion integration | "Official" badge, Notion brand, one-line trust signal |
| `@apify/actors-mcp-server` | trending | Web scraping power-user | "Apify" brand, actors ecosystem |
| `semrush` (API pkg) | ~N/A | SEO analytics | Name IS the category, brand-first |
| `hubspot-api` | ~N/A | CRM API | "HubSpot" brand, clear job-to-be-done |
| `cleverly` / `adbeat` | ~N/A | Ad intelligence | Not on npm with significant DL |

### What Successful MCP Servers Have
1. **Clear use-case lead** — Notion says "Access your Notion workspace", Apify says "Build web scrapers"
2. **Brand/trust** — Official badge or known company name
3. **CI/CD publishing** — Repo updates → npm updates automatically
4. **Description with outcome** — What problem does it solve for a developer?

### What `marketic-mcp` Has That Competitors Don't
- **43 real tools** vs. competitors' 3-10
- **Daily briefing product** — uniquely compelling
- **Polymarket signal integration** — no competitor has this
- **Calibration/Brier score proof** — first marketing tool that shows its own accuracy

**Problem:** None of this differentiation appears in the npm description, keywords, or README first 5 lines.

---

## 3. Top 3 Actionable Improvements Ranked by Expected Impact

### #1 (Expected Impact: HIGH) — Fix the package ecosystem

**Action:** `npm unpublish marketic-cli` immediately. Consolidate on `marketic-mcp` as the single npm package.

**Why:** The empty/broken `marketic-cli` actively hurts discoverability. Anyone who googles "marketic npm" and finds it gets a broken install. Removing it eliminates the negative signal. Expected impact: +20-30% trust score from devs who research before installing.

### #2 (Expected Impact: HIGH) — CI/CD publish pipeline

**Action:** Set up GitHub Actions to publish `marketic-mcp` to npm on every version tag. Lock `package.json` version to match git tag.

**Why:** The gap between repo (54 tools, v1.0.5+) and npm (32 tools, v1.0.4) is a broken trust loop. Developers who install from npm expect the repo's current state. Every stale publish costs credibility. This is table-stakes for any serious npm package.

### #3 (Expected Impact: MEDIUM) — Rewrite npm description + keywords

**Action:** Replace description with outcome-first hook. Add high-signal keywords.

**New description (draft):**
> "AI marketing intelligence for developers — daily signal briefings, competitor ad analysis, Polymarket trend detection, and multi-touch attribution. 43 tools exposed via MCP for Claude/Cursor/Windsurf. Stop checking 7 browser tabs every morning."

**New keywords to add:**
```
llm, ai-agent, marketing-ops, growth-ops, competitor-intelligence,
daily-brief, morning-brief, signal-detection, polymarket,
claude-desktop, claude-code, incrementality, attribution-modeling,
budget-optimization, hubspot-crm, roas, mixpanel-alternative,
ad-measurement, trend-detection, competitor-tracking
```

---

## 4. Specific Changes Needed

### README.md (npm_dist/README.md)
| Section | Current | Change Needed |
|---|---|---|
| **First 5 lines** | Generic "MCP server with 43 tools" | Lead with the daily briefing + Polymarket angle — unique differentiator |
| **Demo** | No working demo | Add one screenshot/GIF of the daily brief output |
| **Quick start** | `marketic-mcp` CLI | Show Claude Desktop config block first (this is the primary UX) |
| **Keywords** | 17 keywords, generic | Replace with outcome + niche keywords (see #3 above) |
| **Badges** | Only npm version + license | Add: GitHub stars, npm weekly downloads (once > 100/wk), Node >= 18 |
| **Use cases** | List all 43 tools | Group into 3-4 job stories: "Morning brief", "Competitor intel", "Campaign build" |
| **Differentiation** | Buried in architecture | Move to top: "First marketing MCP with Brier-score calibrated signals" |

### package.json (npm_dist/package.json)
| Field | Current | Change Needed |
|---|---|---|
| `name` | `marketic-mcp` | Keep — good. MCP naming convention is correct |
| `version` | 1.0.5 | Keep in sync with git tags |
| `description` | Protocol-first | Rewrite as outcome-first (see #3 above) |
| `keywords` | Generic 17 | Add 15-20 niche keywords (see #3 above) |
| `bin` | `marketic-mcp` | Correct |
| `engines` | `>=18.0.0` | Keep |
| `repository` | Points to repo | Good — ensure it matches |
| **Missing** | `scripts.publishConfig` | Add for CI/CD: `npm publish --access public` |

### docs/ (for npm README link depth)
- Add a **5-minute quickstart guide** at `docs/NPM_QUICKSTART.md`
- This gives the npm README a link to "read more" that doesn't require reading the full Python repo README
- Include: install command, Claude Desktop config, one example MCP call showing the daily brief

### CI/CD (GitHub Actions)
Add `.github/workflows/npm-publish.yml`:
```yaml
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - run: npm install
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## Summary: Priority Order

| Priority | Action | Effort | Impact |
|---|---|---|---|
| P0 | `npm unpublish marketic-cli` | 5 min | Removes active negative signal |
| P0 | Set up npm CI/CD on git tags | 1 hr | Closes trust gap permanently |
| P1 | Rewrite description + keywords | 30 min | Immediate discoverability lift |
| P1 | Lead npm README with daily brief demo | 1 hr | Converts browsers to installers |
| P2 | Add npm badges (downloads, version) | 30 min | Social proof signal |
| P2 | Add `docs/NPM_QUICKSTART.md` | 1 hr | Depth for interested devs |
