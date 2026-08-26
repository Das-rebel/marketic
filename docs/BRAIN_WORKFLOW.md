# Brain Workflow — Brand Learnings via Git

How Marketic learns durably: SQLite captures, markdown reviews, PRs promote.

## The Loop

```
audit trail (every AI decision)
      │  distill_learnings MCP tool
      ▼
learnings table (occurrences ↑, confidence ↑ with repetition)
      │  export_brain_md
      ▼
brain/<brand>.md          ← human-reviewable, git-versioned
      │  PR merge = approval
      ▼
status='approved'  →  injected into generate_brief as brand_rules
```

## Daily Operation

### 1. Distill (cron or manual)

```bash
# via MCP
ask_marketic("what did we learn this week")
# or directly — scans audit log for recurring patterns
distill_learnings(brand="acme", min_occurrences=3)
```

Findings land in the `learnings` table as `pending`.

### 2. Export for review

```bash
distill_learnings(brand="acme", export_brain=True)
# writes brain/acme.md — sections: Cost Rules / Quality Rules / Strategy Notes
```

### 3. Review via PR

`brain/*.md` is git-tracked. Weekly flow:

1. Agent opens a PR with the regenerated `brain/<brand>.md`
2. Human reviews: delete wrong rules, sharpen vague ones
3. On merge, run approval:

```bash
distill_learnings(capture_rule="__sync_approved__")  # placeholder
# or approve specific ids programmatically:
python3 -c "
from ensemble.learnings import LearningEngine
e = LearningEngine()
[e.approve(i) for i in e.list_pending(brand='acme')]"
```

**Only `approved` learnings (or confidence ≥ 0.7) reach briefs.**
Pending rules never touch execution agents — review is the gate.

## Rules of Thumb

- A learning needs ≥3 occurrences before it's worth a human's attention (`min_occurrences`)
- Confidence formula: `min(0.95, 0.5 + 0.05 × occurrences)` — repetition earns trust
- One brand per file; never share brains across brands
- If a rule is wrong after approval: edit the md AND flip status back to pending in SQL

## Why This Design

Helena's lesson (see FEATURE_GAP_ANALYSIS.md): durable agent memory belongs in
versioned markdown humans can review — not hidden in a database. But duplicating
storage was wrong too. So: **SQLite is the source of truth, git is the review layer,
briefs are the enforcement point.**
