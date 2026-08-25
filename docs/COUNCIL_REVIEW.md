# Agent Council Review — Marketic vs Comparable Repos

*3-agent council · 2026-08-25 · Lenses: Product/GTM, Developer Experience, Architecture*

**Repos benchmarked:**
| Repo | Stars | What it wins on |
|---|---|---|
| [pawbytes/skill-suites](https://github.com/pawbytes/skill-suites) | 88 | One-command install (`npx skills add`), master router agent |
| [growthack88/growth-marketing-os](https://github.com/growthack88/growth-marketing-os) | 84 | Proof-included assets, bilingual, `llms.txt` AI discoverability |
| [Hk669/AI-Marketing-Agents](https://github.com/Hk669/AI-Marketing-Agents) | 8 | Video demo at top of README — visible working product |
| litellm / one-api | 48K/34K | Infrastructure-standard patterns: proxy, provider-agnostic |

---

## Verdict Summary (cross-council consensus)

All three lenses independently converged on the same top theme:

> **Marketic's depth is invisible.** Competitors with less capability win adoption through *instant visible utility* — video demos, copy-paste assets, one-command installs. Marketic has 39 tools and probability-calibrated signals, but a visitor can't see any of that work in under 60 seconds.

---

## Ranked Recommendations

### P0 — Adoption blockers

**1. Fix the import shadowing + packaging (DX lens)**
- Outer repo dir `marketic/` vs inner package `marketic/marketic/` — `find_packages()` picks the wrong one; `init_memory_db.py` and modules use conflicting import paths. This silently breaks installs for anyone using `pip install`.
- **Action:** Delete/nested-merge the legacy inner package, standardize on absolute imports (`from signals.collectors import ...`), migrate `setup.py` → `pyproject.toml`, verify with `pip install -e .` in a clean venv.

**2. Add a 60-second demo to the README (GTM lens)**
- GIF/asciinema of `python3 daily_briefing.py` showing real signal output. Competitor with 8 stars converts better because proof is the first thing seen.
- **Action:** Record once, embed at top of README above the fold.

**3. Version the brief schema (Architecture lens)**
- `generate_brief` output is an unversioned contract. Any schema change breaks every downstream execution agent simultaneously.
- **Action:** `"schema_version": "1.0"` field + `docs/BRIEF_SCHEMA.md` published as the spec; additive-only changes within a major version.

### P1 — High leverage

**4. Ship `llms.txt` + MCP config snippets (GTM+DX)**
- growth-marketing-os gets indexed by AI assistants via `llms.txt`. Our buyers ARE AI-assistant users.
- **Action:** `llms.txt` at repo root; ready-to-paste Claude/Cursor `mcp.json` blocks in README.

**5. Extract ensemble voting as a standalone library (Architecture lens)**
- The confidence-weighted voting + audit trail is the most differentiated component and is useful far outside marketing. A separate `marketic-vote` pip package becomes a distribution channel back to the main repo (the litellm playbook).

**6. Minimum viable test suite (DX)**
- Zero tests today. Priority order: budget router math (margin-adjusted), Polymarket calibration (P(YES) scoring), brief generation golden-file test. These three protect the core claims.

### P2 — Differentiators worth building

**7. Signal-quality evaluation harness (Architecture)** — publish weekly accuracy scorecard of signal fan-out predictions vs outcomes; turns "probability-calibrated" from a claim into a tracked metric.

**8. "Proof included" pattern for strategies (GTM)** — every generated strategy ships with its evidence chain (which signals triggered it, what they scored); mirrors growth-marketing-os's biggest trust win.

**9. Master router tool (GTM)** — one `ask_marketic` meta-tool that routes natural-language marketing questions to the right specialist tools, like skill-suites' agency agent. Reduces the 39-tool surface to one entry point for MCP clients.

---

## Explicitly deprioritized (council discussed, rejected for now)
- Bilingual docs (audience not MENA-focused yet)
- Chat UI (execution agents are the interface; a chat panel duplicates them)
- More integrations before tests exist

---
*Next review: after P0 items ship.*
