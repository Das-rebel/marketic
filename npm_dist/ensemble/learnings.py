"""
Learnings — Promote recurring audit-trail patterns into brand-level learnings,
exportable as brain/<brand>.md markdown for human review.

Storage lives alongside the audit log in the same SQLite DB (marketic_memory.db);
no duplication of audit data — learnings only reference source examples.
"""

import os
import re
import json
import uuid
import sqlite3
import statistics
from datetime import datetime
from typing import List, Optional, Dict, Any

try:
    from ensemble.audit_trail import get_connection, DB_PATH
except ImportError:  # running as a script (python3 ensemble/learnings.py)
    from audit_trail import get_connection, DB_PATH

DEFAULT_CONFIDENCE = 0.5
MAX_CONFIDENCE = 0.95
CONFIDENCE_STEP = 0.05


def _normalize_rule(rule_text: str) -> str:
    """Normalize rule text for near-identical matching."""
    return re.sub(r"\s+", " ", (rule_text or "").strip().lower())


class LearningEngine:
    """Capture, distill, approve, and export brand-level learnings."""

    def __init__(self, audit_logger=None):
        self.audit_logger = audit_logger
        # Same DB path/connection pattern as AuditLogger.
        self._ensure_tables()

    def _ensure_tables(self):
        conn = get_connection()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS learnings (
                    id TEXT PRIMARY KEY,
                    brand TEXT,
                    category TEXT NOT NULL,
                    rule_text TEXT NOT NULL,
                    occurrences INTEGER NOT NULL DEFAULT 1,
                    confidence REAL NOT NULL DEFAULT 0.5,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    source_examples TEXT,
                    rule_text_normalized TEXT
                );
            """)
            # Legacy-table safety: ensure rule_text_normalized exists.
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(learnings)").fetchall()]
            if "rule_text_normalized" not in cols:
                conn.execute("ALTER TABLE learnings ADD COLUMN rule_text_normalized TEXT")
                conn.execute(
                    "UPDATE learnings SET rule_text_normalized = LOWER(TRIM(rule_text))"
                )
            conn.executescript("""
                CREATE INDEX IF NOT EXISTS idx_learnings_brand
                    ON learnings(brand);
                CREATE INDEX IF NOT EXISTS idx_learnings_status
                    ON learnings(status);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_learnings_rule
                    ON learnings(brand, category, rule_text_normalized);
            """)
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Capture
    # ------------------------------------------------------------------

    def capture(self, brand: str, category: str, rule_text: str,
                source_example: str = None, confidence: float = DEFAULT_CONFIDENCE) -> str:
        """Insert a learning, or increment occurrences if a near-identical
        rule exists (matched on brand+category+normalized rule_text)."""
        now = datetime.utcnow().isoformat()
        norm = _normalize_rule(rule_text)
        learning_id = str(uuid.uuid4())[:12]

        conn = get_connection()
        try:
            row = conn.execute("""
                SELECT id, occurrences FROM learnings
                WHERE brand IS ? AND category = ? AND rule_text_normalized = ?
            """, (brand or None, category, norm)).fetchone()

            if row:
                occurrences = row["occurrences"] + 1
                new_conf = min(MAX_CONFIDENCE, 0.5 + CONFIDENCE_STEP * occurrences)
                conn.execute("""
                    UPDATE learnings
                    SET occurrences = ?, confidence = ?, last_seen = ?
                    WHERE id = ?
                """, (occurrences, new_conf, now, row["id"]))
                conn.commit()
                return row["id"]

            examples = json.dumps([source_example]) if source_example else None
            conn.execute("""
                INSERT INTO learnings
                (id, brand, category, rule_text, rule_text_normalized,
                 occurrences, confidence, first_seen, last_seen, status,
                 source_examples)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, 'pending', ?)
            """, (learning_id, brand, category, rule_text, norm,
                  confidence,
                  now, now, examples))
            conn.commit()
            return learning_id
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Distillation from audit log
    # ------------------------------------------------------------------

    def distill(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """Scan the audit_log decisions table for recurring patterns.

        Heuristics:
          - Cost learnings: group decisions by model+task-type (action); flag
            groups whose avg cost per decision is > 2x the overall median
            avg-cost across groups (with >= min_occurrences decisions).
          - Quality learnings: group by action+model; flag contexts with
            >= min_occurrences decisions and avg confidence < 0.4.
        Each finding is captured() so repeated distillations increment counts.
        """
        findings: List[Dict[str, Any]] = []

        try:
            import sqlite3 as _s3
            db_path = os.path.abspath(DB_PATH)
            if not os.path.exists(db_path):
                return findings
            conn = _s3.connect(db_path)
            conn.row_factory = _s3.Row
        except Exception:
            return findings

        try:
            try:
                rows = conn.execute("""
                    SELECT COALESCE(model, 'unknown') AS model,
                           COALESCE(action, 'unknown') AS action,
                           AVG(cost) AS avg_cost,
                           AVG(confidence) AS avg_conf,
                           COUNT(*) AS n
                    FROM audit_log
                    GROUP BY model, action
                """).fetchall()
            except _s3.OperationalError:
                return findings  # no audit table yet
        finally:
            conn.close()

        cost_groups = [dict(r) for r in rows if r["n"] >= min_occurrences]
        if not cost_groups:
            return findings

        medians = sorted(g["avg_cost"] for g in cost_groups)
        median_cost = statistics.median(medians) if medians else 0.0

        for g in cost_groups:
            label = f"{g['model']} on {g['action']}"
            if g["avg_cost"] > 2 * median_cost:
                findings.append({
                    "category": "cost",
                    "rule_text": f"High cost pattern: {label} averages "
                                 f"${g['avg_cost']:.4f}/decision (>2x median ${median_cost:.4f}). "
                                 f"Consider routing this task type to a cheaper model.",
                    "source_example": json.dumps(g),
                    "confidence": min(0.9, 0.5 + 0.02 * g["n"]),
                })
            if g["avg_conf"] < 0.4:
                findings.append({
                    "category": "quality",
                    "rule_text": f"Low quality pattern: {label} averages confidence "
                                 f"{g['avg_conf']:.2f} (<0.4) over {g['n']} decisions. "
                                 f"Review prompt/model for this task type.",
                    "source_example": json.dumps(g),
                    "confidence": min(0.9, 0.5 + 0.02 * g["n"]),
                })

        for f in findings:
            self.capture(brand="system", category=f["category"],
                         rule_text=f["rule_text"],
                         source_example=f["source_example"],
                         confidence=f["confidence"])
        return findings

    # ------------------------------------------------------------------
    # Export / review workflow
    # ------------------------------------------------------------------

    def export_brain_md(self, brand: str, out_dir: str = "brain") -> str:
        """Write brain/<brand>.md with Cost Rules, Quality Rules, Strategy Notes."""
        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT * FROM learnings
                WHERE brand IS ?
                  AND (status = 'approved' OR confidence > 0.7)
                ORDER BY category, occurrences DESC
            """, (brand or None,)).fetchall()
        finally:
            conn.close()

        sections: Dict[str, List[str]] = {"cost": [], "quality": [], "strategy": []}
        for r in rows:
            line = f"- [{r['rule_text']}] (seen {r['occurrences']}x, conf {r['confidence']:.1f})"
            sections.setdefault(r["category"], []).append(line)

        safe_brand = re.sub(r"[^A-Za-z0-9_-]+", "_", brand or "default")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{safe_brand}.md")

        with open(path, "w") as f:
            f.write(f"# Brain — {brand}\n\n")
            f.write(f"_Exported {datetime.utcnow().isoformat()}_\n\n")
            f.write("## Cost Rules\n\n")
            f.write("\n".join(sections.get("cost", [])) + "\n\n" if sections.get("cost") else "_None yet._\n\n")
            f.write("## Quality Rules\n\n")
            f.write("\n".join(sections.get("quality", [])) + "\n\n" if sections.get("quality") else "_None yet._\n\n")
            f.write("## Strategy Notes\n\n")
            strategy = sections.get("strategy", [])
            f.write("\n".join(strategy) + "\n" if strategy else "_None yet._\n")

        return path

    def approve(self, learning_id: str):
        conn = get_connection()
        try:
            conn.execute("UPDATE learnings SET status = 'approved' WHERE id = ?",
                         (learning_id,))
            conn.commit()
        finally:
            conn.close()

    def list_pending(self, brand: str = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            sql = "SELECT * FROM learnings WHERE status = 'pending'"
            params = []
            if brand is not None:
                sql += " AND brand IS ?"
                params.append(brand)
            sql += " ORDER BY last_seen DESC"
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


# ----------------------------------------------------------------------
# Smoke test
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("=== LearningEngine smoke test ===")

    engine = LearningEngine()

    # 1. Capture same rule twice + once -> occurrences should increment.
    lid1 = engine.capture("acme", "strategy",
                          "Always A/B test landing headlines before scaling spend.",
                          source_example="campaign_123")
    lid2 = engine.capture("acme", "strategy",
                          "Always A/B test  landing HEADLINES before scaling spend.",  # near-identical
                          source_example="campaign_456")
    lid3 = engine.capture("acme", "strategy",
                          "Always A/B test landing headlines before scaling spend.")
    assert lid1 == lid2 == lid3, "near-identical rules should match to one learning"

    # One distinct rule that stays at 1 occurrence.
    engine.capture("acme", "cost", "Prefer local models for sub-$0.001 tasks.")

    pending = engine.list_pending("acme")
    print(f"\nPending after capture: {len(pending)}")
    for p in pending:
        print(f"  - ({p['category']}) {p['rule_text'][:60]}... "
              f"occ={p['occurrences']} conf={p['confidence']:.2f}")

    # Approve one so export shows mixed statuses.
    engine.approve(lid1)

    # 2. Distill against possibly-empty audit log — must not crash.
    findings = engine.distill(min_occurrences=3)
    print(f"\nDistill findings: {len(findings)}")
    for f in findings:
        print(f"  - [{f['category']}] {f['rule_text'][:70]}...")

    # 3. Export sample brain md.
    path = engine.export_brain_md("acme", out_dir="/tmp/brain_test")
    print(f"\nBrain md written to: {path}")
    with open(path) as fh:
        print("--- file contents ---")
        print(fh.read())

    print("Smoke test OK.")
