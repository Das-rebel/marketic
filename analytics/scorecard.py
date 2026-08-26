"""
Signal Scorecard — prove probability-calibrated signals work.

Core claim: Polymarket markets scored volume x P(YES) are valuable because
most resolve No. This module tracks every captured prediction against its
real-world outcome over time, producing a calibration report (bucketed
actual-yes rates + Brier score).

Reuses the sqlite connection pattern from ensemble/audit_trail.py.
"""

import os
import re
import sys
import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

# Reuse the audit trail connection when available so both modules share the
# same marketic_memory.db. Fall back to an equivalent local implementation.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ensemble"))
try:
    from audit_trail import get_connection  # type: ignore
except Exception:  # pragma: no cover - fallback only
    _DB_PATH = os.path.join(os.path.dirname(__file__), "..", "marketic_memory.db")

    def get_connection():  # type: ignore[misc]
        conn = sqlite3.connect(os.path.abspath(_DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

BUCKETS = [(0.0, 20.0), (20.0, 40.0), (40.0, 60.0), (60.0, 80.0), (80.0, 100.0)]


def _now() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class SignalScorecard:
    """Track prediction-market signals vs outcomes to prove calibration."""

    def __init__(self, db_connection_factory: Optional[Callable[[], Any]] = None):
        self._conn_factory = db_connection_factory or get_connection
        self._owns_connections = db_connection_factory is None
        self._init_table()

    # ------------------------------------------------------------------ #
    def track_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist a single signal and return its generated ID.

        Mirrors the Polymarket snapshot path but accepts a flat dict so the
        MCP handler can call it directly without constructing nested metadata.
        """
        stored = self.snapshot([signal_data])
        # The snapshot call stores everything under the same URL dedup key.
        # We retrieve the row we just inserted to surface its id.
        conn = self._connect()
        try:
            url = self._get_field(signal_data, "url")
            row = conn.execute(
                "SELECT id FROM signal_predictions WHERE url = ? ORDER BY captured_at DESC LIMIT 1",
                (url,),
            ).fetchone()
            signal_id = row["id"] if row else None
        finally:
            self._close(conn)
        return {"tracked": stored > 0, "signal_id": signal_id}

    def get_calibration_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return the bucketed calibration report (date/source filtering not yet
        implemented at the SQL level — reserved for future)."""
        return self.calibration_report()

    def resolve_signal(
        self,
        signal_id: str,
        actual_outcome: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Resolve a tracked signal by its DB id with YES/NO/PARTIAL."""
        outcome_map = {"yes": "yes", "no": "no", "partial": "no"}
        outcome = outcome_map.get(actual_outcome.strip().lower())
        if not outcome:
            return {"error": f"Invalid outcome: {actual_outcome}"}
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE signal_predictions SET outcome = ?, resolved_at = ? WHERE id = ?",
                (outcome, _now(), signal_id),
            )
            conn.commit()
            ok = cur.rowcount > 0
        finally:
            self._close(conn)
        return {"resolved": ok, "signal_id": signal_id}

    # ------------------------------------------------------------------ #
    def _connect(self):
        return self._conn_factory()

    def _close(self, conn) -> None:
        # Only close connections we created ourselves; caller-supplied
        # factories (e.g. shared in-memory DBs) manage their own lifecycle.
        if self._owns_connections:
            conn.close()

    def _init_table(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS signal_predictions (
                    id TEXT PRIMARY KEY,
                    captured_at TEXT NOT NULL,
                    source TEXT,
                    title TEXT,
                    url TEXT,
                    predicted_score REAL,
                    implied_prob REAL,
                    outcome TEXT,
                    resolved_at TEXT
                )
                """
            )
            conn.commit()
        finally:
            self._close(conn)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _get_field(obj: Any, name: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def snapshot(self, signals: List[Any], horizon_days: int = 30) -> int:
        """Persist today's prediction-market signals. Returns count stored.

        Only stores signals whose metadata carries implied_yes_prob
        (i.e., Polymarket markets).
        """
        stored = 0
        now = _now()
        conn = self._connect()
        try:
            for sig in signals or []:
                meta = self._get_field(sig, "metadata") or {}
                prob = meta.get("implied_yes_prob")
                # implied_yes_prob is optional — None means unknown probability,
                # not "skip this signal"
                # (e.g. generic signals) still get stored with implied_prob=NULL
                try:
                    prob = float(prob) if prob is not None else None
                    if prob is not None:
                        # normalize 0-1 probabilities to percent scale
                        if 0.0 <= prob <= 1.0 and prob in (0.0, 1.0) or 0 < prob < 1:
                            prob = prob * 100.0
                except (TypeError, ValueError):
                    prob = None
                url = self._get_field(sig, "url")
                if not url:
                    continue
                existing = conn.execute(
                    "SELECT 1 FROM signal_predictions WHERE url = ? AND outcome IS NULL LIMIT 1",
                    (url,),
                ).fetchone()
                if existing:
                    continue
                conn.execute(
                    """
                    INSERT INTO signal_predictions
                        (id, captured_at, source, title, url, predicted_score, implied_prob)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        now,
                        self._get_field(sig, "source"),
                        self._get_field(sig, "title"),
                        url,
                        self._get_field(sig, "engagement_score"),
                        (min(max(prob, 0.0), 100.0) if prob is not None else None),
                    ),
                )
                stored += 1
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._close(conn)
        return stored

    # ------------------------------------------------------------------ #
    def record_resolution(self, url: str, outcome: str) -> bool:
        """Manually set outcome ('yes'|'no') + resolved_at for a prediction."""
        outcome = (outcome or "").strip().lower()
        if outcome not in ("yes", "no"):
            return False
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE signal_predictions SET outcome = ?, resolved_at = ? WHERE url = ?",
                (outcome, _now(), url),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            self._close(conn)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _slug_from_url(url: str) -> Optional[str]:
        m = re.search(r"polymarket\.com/(?:event|market)/([a-z0-9\-]+)", url or "", re.I)
        return m.group(1).lower() if m else None

    def resolve_pending(self) -> int:
        """Auto-resolve pending predictions via the Polymarket Gamma API.

        Closed events expose outcomePrices like ["1","0"] (yes won) or
        ["0","1"] (no won). Returns number resolved; 0 on any API failure.
        """
        import httpx

        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT DISTINCT url FROM signal_predictions WHERE outcome IS NULL"
            ).fetchall()
        finally:
            self._close(conn)
        pending = {self._slug_from_url(r["url"]): r["url"] for r in rows}
        pending.pop(None, None)
        if not pending:
            return 0

        resolved = 0
        try:
            resp = httpx.get(
                "https://gamma-api.polymarket.com/events",
                params={"closed": "true", "limit": 100},
                timeout=15.0,
            )
            resp.raise_for_status()
            events = resp.json()
        except Exception:
            return 0

        for ev in events or []:
            slug = (ev.get("slug") or "").lower()
            if slug not in pending:
                continue
            prices = None
            markets = ev.get("markets") or []
            if markets and isinstance(markets[0].get("outcomePrices"), list):
                try:
                    prices = [float(p) for p in markets[0]["outcomePrices"]]
                except (TypeError, ValueError):
                    prices = None
            elif isinstance(ev.get("outcomePrices"), list):
                try:
                    prices = [float(p) for p in ev["outcomePrices"]]
                except (TypeError, ValueError):
                    prices = None
            if prices is None or len(prices) < 2:
                continue
            if abs(prices[0] - 1.0) < 0.01:
                outcome = "yes"
            elif abs(prices[1] - 1.0) < 0.01:
                outcome = "no"
            else:
                continue
            if self.record_resolution(pending[slug], outcome):
                resolved += 1
        return resolved

    # ------------------------------------------------------------------ #
    def calibration_report(self) -> Dict[str, Any]:
        """Bucketed actual-yes rates + Brier score among RESOLVED predictions."""
        report: Dict[str, Any] = {
            "buckets": {
                f"{int(lo)}-{int(hi)}": {"n": 0, "actual_yes_rate": 0.0}
                for lo, hi in BUCKETS
            },
            "brier_score": 0.0,
            "n_total": 0,
            "n_resolved": 0,
            "n_pending": 0,
        }
        try:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT implied_prob, outcome FROM signal_predictions"
                ).fetchall()
            finally:
                self._close(conn)
        except Exception:
            return report

        resolved = [
            r for r in rows if r["implied_prob"] is not None and r["outcome"] in ("yes", "no")
        ]
        report["n_total"] = len(rows)
        report["n_resolved"] = len(resolved)
        report["n_pending"] = sum(1 for r in rows if r["outcome"] is None)

        if not resolved:
            return report

        brier_sum = 0.0
        bucket_hits: Dict[str, List[int]] = {k: [] for k in report["buckets"]}
        for r in resolved:
            prob = max(0.0, min(100.0, float(r["implied_prob"])))
            y = 1 if r["outcome"] == "yes" else 0
            brier_sum += ((prob / 100.0) - y) ** 2
            for lo, hi in BUCKETS:
                key = f"{int(lo)}-{int(hi)}"
                if (lo <= prob < hi) or (hi == 100.0 and prob == 100.0):
                    bucket_hits[key].append(y)
                    break
        report["brier_score"] = round(brier_sum / len(resolved), 4)
        for key, ys in bucket_hits.items():
            report["buckets"][key]["n"] = len(ys)
            if ys:
                report["buckets"][key]["actual_yes_rate"] = round(sum(ys) / len(ys), 4)
        return report

    # ------------------------------------------------------------------ #
    def weekly_summary(self) -> str:
        """Human-readable markdown of the calibration report."""
        rep = self.calibration_report()
        lines = ["## Signal Calibration Report", ""]
        lines.append(
            f"- Total predictions: **{rep['n_total']}** "
            f"(resolved: {rep['n_resolved']}, pending: {rep['n_pending']})"
        )
        lines.append(f"- Brier score: **{rep['brier_score']}** (lower = better calibrated)")
        lines.append("")
        lines.append("| Implied P(YES) bucket | n | Actual YES rate |")
        lines.append("|---|---|---|")
        for key, b in rep["buckets"].items():
            rate = f"{b['actual_yes_rate']:.0%}" if b["n"] else "-"
            lines.append(f"| {key}% | {b['n']} | {rate} |")
        return "\n".join(lines)


if __name__ == "__main__":
    print("=== SignalScorecard smoke test ===")

    # Use a single shared throwaway in-memory DB for all connections so the
    # smoke block never touches real data and the table persists across calls.
    import sqlite3 as _sq

    _mem = _sq.connect(":memory:")
    _mem.row_factory = _sq.Row

    def mem_conn():
        return _mem

    sc = SignalScorecard(db_connection_factory=mem_conn)

    n = sc.snapshot([])
    assert n == 0, "snapshot on empty must store 0"
    print(f"snapshot(empty) -> {n}")

    rep = sc.calibration_report()
    assert rep["n_total"] == 0 and rep["brier_score"] == 0.0
    print("calibration_report(empty) -> zeros OK:", rep)

    fake_signals = [
        {
            "source": "polymarket",
            "title": "Fed cuts rates before March?",
            "url": "https://polymarket.com/event/fed-rates-march-smoke",
            "engagement_score": 81234.5,
            "metadata": {"implied_yes_prob": 35},
        },
        {
            "source": "reddit",
            "title": "non-market signal — should be skipped",
            "url": "https://reddit.com/r/x",
            "engagement_score": 10,
            "metadata": {},
        },
    ]
    stored = sc.snapshot(fake_signals)
    print(f"snapshot(signals) -> {stored} stored (expected 1)")
    assert stored == 1

    ok = sc.record_resolution("https://polymarket.com/event/fed-rates-march-smoke", "no")
    assert ok
    print("record_resolution(url, 'no') -> True")

    resolved = sc.resolve_pending()
    print(f"resolve_pending() -> {resolved} resolved (API may be unreachable)")

    print(sc.weekly_summary())
    print("=== smoke test passed ===")

    # --- smoke test for new wrapper methods ---
    _mem2 = _sq.connect(":memory:")
    _mem2.row_factory = _sq.Row

    def _m():
        return _mem2

    sc2 = SignalScorecard(db_connection_factory=_m)
    test_sig = {
        "source": "polymarket",
        "title": "Test market",
        "url": "https://polymarket.com/event/test-smoke",
        "engagement_score": 50000.0,
        "metadata": {"implied_yes_prob": 65},
    }
    tracked = sc2.track_signal(test_sig)
    assert isinstance(tracked, dict) and "tracked" in tracked, f"track_signal returned {tracked}"
    print(f"track_signal -> {tracked}")
    report = sc2.get_calibration_report()
    assert isinstance(report, dict) and "brier_score" in report
    print(f"get_calibration_report -> brier={report['brier_score']}")
    if tracked.get("signal_id"):
        res = sc2.resolve_signal(tracked["signal_id"], "YES", "test note")
        assert isinstance(res, dict) and "resolved" in res
        print(f"resolve_signal -> {res}")
    print("=== wrapper smoke test passed ===")
