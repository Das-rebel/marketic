# Marketic vs Helena — Architecture Analysis (v2)

> **Revision note:** v1 of this doc proposed cloning Helena's features (design
> templates, UGC curator, publisher). That was wrong. This version corrects the thesis.

---

## The Wrong Lesson vs The Right Lesson

### ❌ What we initially did (wrong)
Copied Helena's *features*: hardcoded her brand's hex codes into "default templates,"
wrote a Postiz clone, built UGC flows with Bukito-specific copy. Result: a
general-purpose OS full of one restaurant's branding.

### ✅ What Helena actually teaches (right)
Helena's innovation is **architectural**, not functional:

| Pattern | Helena's implementation | Marketic adoption |
|---------|------------------------|-------------------|
| **Brand-as-data** | `bukito-brand` skill = colors/fonts/tone as config | `BrandTokens` + `brand_memory` — templates render against tokens |
| **Versioned brain** | `brain/helena.md` in git; learnings merged via PR | Audit trail already logs decisions; add brain files for durable strategy learnings |
| **Skills with triggers** | SKILL.md frontmatter declares when to activate | MCP tools already self-describe; add trigger metadata to tool descriptions |
| **Thin integrations** | Paper/Runway/Postiz used *as-is*, not reimplemented | Orchestrate existing MCP servers; write adapters only where none exist |

---

## Corrected Positioning

```
┌─────────────────────────────────────────────────┐
│  Marketic = Strategy Brain (white-label)        │
│  competitive intel · positioning · ensemble AI  │
│  attribution · budgets · audit trail · CRM      │
└───────────────────┬─────────────────────────────┘
                    │ hands off briefs + brand kit
┌───────────────────▼─────────────────────────────┐
│  Execution Agents (per-brand, e.g. "Helena")    │
│  voice · calendar · creative · publishing       │
│  powered by: Paper MCP · Runway · Postiz        │
└─────────────────────────────────────────────────┘
```

**Marketic does not need to be Helena.** Marketic produces the *brief* (positioning,
copy variants, budget, hashtags, optimal times) + the *brand kit* (tokens).
A brand agent — Helena-style, one per brand — executes it with design/publishing tools.

## What Changed in the Code

1. **`execution/design_templates.py` rewritten as token-driven**
   - New `BrandTokens` dataclass: entire visual identity as configuration
   - All 8 templates now reference `{{brand.primary}}`, `{{brand.font}}`, etc.
   - Zero hardcoded brand values. Verified: same template renders Bukito (#6D0000)
     and a fictional Acme (#00AAFF) correctly.
   - `TemplateLibrary(BrandTokens.from_brand_memory(record))` loads any brand

2. **UGC curator & publisher kept but de-scoped**
   - They orchestrate; they don't replace Postiz/platform APIs
   - Direct-publish paths are explicit fallbacks, not primary paths

3. **What we will NOT build**
   - ❌ Video generation (Runway already exists as API/MCP)
   - ❌ Design canvas (Paper MCP already exists)
   - ❌ Scheduling backend (Postiz already exists)
   - ❌ Per-brand logic anywhere in `marketic/*`

## Remaining Genuine Gaps (small now)

| Gap | Fix | Effort |
|-----|-----|--------|
| Brain files not git-versioned per brand | Add `brain/<brand>.md` convention + PR workflow doc | Low |
| No handoff artifact (brief → agent) | `generate_brief` MCP tool: outputs JSON brief + resolved brand kit | Medium |
| Tool descriptions lack trigger phrases | Add "use when..." lines to MCP tool descriptions | Low |

---

*Revised: 2026-08-24 — supersedes v1 feature-parity framing.*
