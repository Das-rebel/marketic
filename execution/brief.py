"""
Brief Generator — The strategy-brain → execution-agent handoff artifact.

Produces ONE self-contained JSON brief that any Helena-style brand agent can
execute without calling back into Marketic: positioning, copy variants,
budget split, hashtags, optimal times, resolved BrandTokens.
Pattern validated by @tibo_maker's 7-agent org chart (lead brain → specialists).
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from execution.design_templates import BrandTokens
except ImportError:
    from execution.design_templates import BrandTokens


def generate_brief(
    campaign_name: str,
    objective: str,
    product_name: str,
    product_description: str,
    target_audience: str = "",
    channels: Optional[List[str]] = None,
    total_budget: float = 10000,
    duration_weeks: int = 4,
    key_benefits: Optional[List[str]] = None,
    brand_tokens: Optional[Dict[str, Any]] = None,
    channel_performance: Optional[Dict[str, Any]] = None,
    positioning_summary: str = "",
    competitor_insights: str = "",
    source_signals: Optional[List[Dict[str, Any]]] = None,
    brand: str = "",
) -> Dict[str, Any]:
    """
    Build the complete handoff brief. Pure orchestration of existing modules —
    no new intelligence, just assembly.
    """
    channels = channels or ["social", "email"]

    # ---- Learnings injection (Feature B) — never crash brief generation ----
    def _load_brand_rules(brand_name: str) -> List[Dict[str, Any]]:
        if not brand_name:
            return []
        try:
            try:
                from ensemble.audit_trail import get_connection
            except ImportError:
                from audit_trail import get_connection
            conn = get_connection()
            try:
                rows = conn.execute("""
                    SELECT rule_text, category FROM learnings
                    WHERE brand IS ?
                      AND (status = 'approved' OR confidence >= 0.7)
                    ORDER BY occurrences DESC, confidence DESC
                    LIMIT 10
                """, (brand_name,)).fetchall()
                return [{"rule": r["rule_text"], "category": r["category"]}
                        for r in rows]
            finally:
                conn.close()
        except Exception:
            return []

    brand_rules = _load_brand_rules(brand)

    key_benefits = key_benefits or []
    channel_performance = channel_performance or {}
    tokens = BrandTokens.from_brand_memory(brand_tokens or {})

    brief: Dict[str, Any] = {
        "brief_version": "1.0",
        "generated_at": datetime.utcnow().isoformat(),
        "campaign": {
            "name": campaign_name,
            "objective": objective,
            "duration_weeks": duration_weeks,
        },
        "brand_kit": {
            # Execution agent renders EVERYTHING from these tokens — zero
            # hardcoded brand values on their side.
            **tokens.to_substitution_map(),
            "voice_notes": (brand_tokens or {}).get("voice_notes", ""),
            "banned_words": (brand_tokens or {}).get("banned_words", []),
        },
        "product": {
            "name": product_name,
            "description": product_description,
            "audience": target_audience or "primary buyers",
            "key_benefits": key_benefits,
        },
    }

    # Evidence chain (Feature A) — only present when source signals provided
    if source_signals is not None:
        brief["evidence_chain"] = {
            "signal_count": len(source_signals),
            "top_signals": [
                {"title": s.get("title", ""), "source": s.get("source", ""),
                 "score": s.get("engagement_score")}
                for s in source_signals[:5]
            ],
            "generated_from": "marketic signal fan-out",
        }
    if brand_rules:
        brief["brand_rules"] = brand_rules

    if positioning_summary:
        brief["positioning"] = {"summary": positioning_summary}
    if competitor_insights:
        brief["competitive_context"] = {"insights": competitor_insights}

    # Budget split (margin-aware when performance data provided)
    budget_section: Dict[str, Any] = {"total": total_budget}
    if channel_performance:
        try:
            import asyncio
            try:
                from campaign.budget_router import BudgetRouter
            except ImportError:
                from campaign.budget_router import BudgetRouter
            router = BudgetRouter()
            allocations = asyncio.run(router.rebalance(
                total_budget=total_budget,
                channel_data=channel_performance,
                strategy="roas_optimized",
            )) or []
            def _get(a, key):
                return a[key] if isinstance(a, dict) else getattr(a, key)
            budget_section["recommended_split"] = [
                {"channel": _get(a, "channel"), "amount": _get(a, "recommended_spend"),
                 "change_pct": _get(a, "change_percentage"), "reasoning": _get(a, "reasoning")}
                for a in allocations
            ]
        except Exception as e:
            budget_section["error"] = f"budget optimization unavailable: {e}"
            budget_section["recommended_split"] = [
                {"channel": ch, "amount": round(total_budget / len(channels), 2)}
                for ch in channels
            ]
    else:
        budget_section["recommended_split"] = [
            {"channel": ch, "amount": round(total_budget / len(channels), 2)}
            for ch in channels
        ]
    brief["budget"] = budget_section

    # Optimal posting windows per platform (from ContentCalendarManager)
    try:
        try:
            from execution.publisher import Platform, ContentCalendarManager
        except ImportError:
            from execution.publisher import Platform, ContentCalendarManager
        mgr = ContentCalendarManager()
        platform_map = {
            "social": Platform.INSTAGRAM, "instagram": Platform.INSTAGRAM,
            "twitter": Platform.TWITTER, "linkedin": Platform.LINKEDIN,
        }
        windows = {}
        for ch in channels:
            p = platform_map.get(ch)
            if p:
                times = mgr.get_optimal_times(p, count=2)
                windows[ch] = [t.isoformat() for t in times]
        if windows:
            brief["posting_windows_utc"] = windows
    except Exception:
        pass

    # Execution instructions for the receiving agent
    brief["execution_contract"] = {
        "renders_from_tokens_only": True,
        "expected_outputs": [
            "static posts via design templates (ig_menu_highlight, ig_vibe_post, ...)",
            "captions matching voice notes",
            "scheduling per posting_windows_utc",
            "performance report back as audit_log entries",
        ],
        "must_not": [
            "modify brand tokens without PR review",
            "publish without human_approved flag set",
            "store secrets or PII in memory files",
            "remove or fabricate evidence_chain entries",
        ],
    }

    return brief
