#!/usr/bin/env python3
"""
Daily Marketing Briefing — cronnable loop combining the strategy brain.

Pipeline (all existing modules, zero new intelligence):
  1. SignalFanout      → what's moving across HN/Reddit/PH/Polymarket/Twitter
  2. AuditLogger       → cost summary of yesterday's AI decisions
  3. CRM dashboard     → pipeline movement
  4. Output            → markdown briefing to stdout / file / webhook

Cron example (daily 8am):
  0 8 * * *  cd ~/marketic && python3 daily_briefing.py >> logs/briefing.log 2>&1

Webhook delivery (WhatsApp/Slack/etc):
  MARKETIC_BRIEF_WEBHOOK=https://your-endpoint  → POSTs {"text": "..."} 
"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from signals.collectors import SignalFanout
except ImportError:
    from signals.collectors import SignalFanout


def build_briefing(query: str = "", sources: list = None) -> str:
    now = datetime.utcnow()
    lines = [
        f"# ☀️ Marketic Daily Briefing",
        f"**{now.strftime('%Y-%m-%d %H:%M UTC')}**\n",
    ]

    # ── 1. Market signals ────────────────────────────────────────────
    try:
        import asyncio
        fanout = SignalFanout()
        sig = asyncio.run(fanout.run(query=query, sources=sources))
        if sig and sig.get("total"):
            lines.append(f"## 📡 Signals ({sig['total']} matched)")
            for item in sig.get("brief_top_10", [])[:5]:
                lines.append(f"- **[{item['source']}]** {item['title']}")
                if item.get("url"):
                    lines.append(f"  {item['url']}")
            themes = sig.get("consensus_themes", [])
            if themes:
                lines.append(f"\n**Consensus themes:** {', '.join(themes[:5])}")
            money = sig.get("money_outliers", [])
            if money:
                lines.append("\n**💰 Money talking (Polymarket):**")
                for m in money:
                    vol = m.get("volume_usd")
                    vol_str = f"${float(vol):,.0f}" if vol else "?"
                    lines.append(f"- {m['title'][:90]} ({vol_str})")
            errs = sig.get("errors", {})
            if errs:
                lines.append(f"\n*Source errors: {list(errs.keys())}*")
        else:
            lines.append("## 📡 Signals\nNo matches today.")
    except Exception as e:
        lines.append(f"## 📡 Signals\n*collector failed: {e}*")

    # ── 2. AI spend yesterday ────────────────────────────────────────
    try:
        from ensemble.audit_trail import AuditLogger
        logger = AuditLogger()
        yesterday = (now - timedelta(days=1)).date().isoformat()
        costs = logger.get_cost_summary(start_date=yesterday)
        if costs.get("total_decisions"):
            lines.append(
                f"\n## 💸 AI Spend (since {yesterday})\n"
                f"- Decisions: {costs['total_decisions']} · Total: ${costs['total_cost']:.4f}\n"
                f"- By model: {json.dumps(costs.get('by_model', {}))}"
            )
    except Exception:
        pass

    # ── 3. Signal calibration scorecard ────────────────────────────
    try:
        from analytics.scorecard import SignalScorecard
        card = SignalScorecard()
        resolved_n = card.resolve_pending()
        rep = card.calibration_report()
        lines.append(f"\n## 🎯 Signal Calibration")
        if rep.get("n_resolved", 0) == 0 and rep.get("n_pending", 0) == 0:
            lines.append("No predictions tracked yet — snapshots collect automatically with each fan-out.")
        else:
            if resolved_n:
                lines.append(f"*{resolved_n} predictions auto-resolved this run*")
            brier = rep.get("brier_score", 0)
            n = rep.get("n_total", 0)
            lines.append(f"- Tracked: {n} · Resolved: {rep.get('n_resolved', 0)} · Pending: {rep.get('n_pending', 0)}")
            if rep.get("n_resolved", 0):
                # Brier < 0.25 beats random guessing; lower is better
                grade = "good" if brier < 0.25 else "needs tuning"
                lines.append(f"- Brier score: **{brier:.3f}** ({grade}; <0.25 beats chance)")
                for bucket, stats in (rep.get("buckets") or {}).items():
                    if stats.get("n"):
                        lines.append(f"  - {bucket}: {stats['n']} predictions, actual YES rate {stats['actual_yes_rate']:.0%}")
    except Exception as e:
        pass  # scorecard section is optional; never break the briefing

    # ── 4. Pipeline pulse ────────────────────────────────────────────
    try:
        from crm import CRMMaster
        dash = CRMMaster().get_crm_dashboard()
        leads = dash.get("leads", {})
        deals = dash.get("deals", {})
        lines.append(
            f"\n## 🎯 Pipeline\n"
            f"- Leads: {leads.get('total', 0)} (avg score {leads.get('avg_score', 0):.0f})\n"
            f"- Open deals: {deals.get('total_open', 0)} worth ${deals.get('total_pipeline', 0):,.0f}"
        )
    except Exception:
        pass

    lines.append(f"\n---\n*Generated by Marketic strategy brain · every number traceable via audit trail*")
    return "\n".join(lines)


def deliver(text: str):
    """File + optional webhook."""
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"briefing_{datetime.utcnow().strftime('%Y%m%d')}.md")
    with open(path, "w") as f:
        f.write(text)

    webhook = os.environ.get("MARKETIC_BRIEF_WEBHOOK")
    if webhook:
        try:
            import httpx
            httpx.post(webhook, json={"text": text}, timeout=15.0)
        except Exception as e:
            print(f"[briefing] webhook delivery failed: {e}", file=sys.stderr)
    return path


if __name__ == "__main__":
    q = " ".join(sys.argv[1:2]) or ""
    text = build_briefing(query=q)
    print(text)
    path = deliver(text)
    print(f"\n[saved → {path}]", file=sys.stderr)
