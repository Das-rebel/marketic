"""
ProspectLoop — signal-driven CRM prospecting (JoeCRM pattern).

Pipeline:
    1. discover()          — find prospects in a niche via SerperProspectAdapter
    2. enrich_with_signals — run SignalFanout ONCE, attach top-3 matched signals
                             per contact (keyword overlap)
    3. draft_outreach()    — template-based personalized email (no LLM)
    4. run()               — orchestrate 1→2→3 and insert leads into CRMMaster

Graceful degradation: if Serper is unavailable (no SERPER_API_KEY or network
error), prospects are synthesized from signal titles themselves (company-name
placeholders marked source="signals").

No existing files are modified by this module.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Make sibling-package imports work when run as a script from anywhere.
_PKG_ROOT = Path(__file__).resolve().parent.parent
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

try:
    from crm import CRMMaster, get_connection
except ImportError:  # pragma: no cover
    from marketic.crm import CRMMaster, get_connection  # type: ignore

try:
    from integrations.unified_adapter import SerperProspectAdapter
except ImportError:  # pragma: no cover
    from marketic.integrations.unified_adapter import SerperProspectAdapter  # type: ignore

try:
    from signals.collectors import SignalFanout
except ImportError:  # pragma: no cover
    from marketic.signals.collectors import SignalFanout  # type: ignore


STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "for", "to", "at", "with",
    "is", "are", "was", "were", "be", "by", "from", "as", "that", "this", "it",
    "new", "how", "why", "what", "vs", "up",
}


def _tokens(text: str) -> set:
    """Lowercase keyword tokens for overlap matching."""
    words = re.findall(r"[a-z0-9+#]{2,}", (text or "").lower())
    return {w for w in words if w not in STOPWORDS}


def _contact_job_title(contact: Any) -> str:
    """
    Defensive job-title read. NOTE: the shared Contact dataclass has NO
    job_title field (SerperProspectAdapter passes one anyway), so we try
    the attribute first, then attributes dict.
    """
    title = getattr(contact, "job_title", None)
    if title:
        return str(title)
    attrs = getattr(contact, "attributes", None) or {}
    return str(attrs.get("job_title", ""))


class ProspectLoop:
    """Signal-driven prospecting loop: discover → enrich → draft → CRM."""

    def __init__(self):
        self.crm = CRMMaster()
        self.adapter = SerperProspectAdapter()
        self.fanout = SignalFanout()

    # ------------------------------------------------------------------ #
    # 1. Discover
    # ------------------------------------------------------------------ #
    async def discover(self, niche_query: str, limit: int = 10) -> List[Any]:
        """Find prospects matching a niche via Serper LinkedIn-site search."""
        query = f"{niche_query} founder OR head of growth"
        try:
            self.adapter.connect()
            if not self.adapter.connected:
                print("[prospect_loop] Serper unavailable (no SERPER_API_KEY); "
                      "will fall back to signal-derived prospects.")
                return []
            contacts = await self.adapter.search_contacts(query, limit=limit)
            return contacts or []
        except Exception as exc:  # noqa: BLE001
            print(f"[prospect_loop] discover failed ({exc}); "
                  "will fall back to signal-derived prospects.")
            return []

    # ------------------------------------------------------------------ #
    # 2. Enrich with signals
    # ------------------------------------------------------------------ #
    async def enrich_with_signals(self, contacts: List[Any],
                                  market_query: str) -> List[Dict[str, Any]]:
        """
        Run SignalFanout ONCE for the market_query, then attach the top-3
        matched signals to each contact ranked by keyword overlap between the
        contact's company/job_title and each signal's title/topics.
        """
        signals: List[Dict[str, Any]] = []
        errors: Dict[str, Any] = {}
        try:
            brief = await self.fanout.run(query=market_query)
            errors = brief.get("errors", {}) or {}
            # brief_top_10 entries: {source, title, url, score, engagement_raw}
            signals = list(brief.get("brief_top_10") or [])
            if errors:
                print(f"[prospect_loop] some signal sources errored: {list(errors)}")
        except Exception as exc:  # noqa: BLE001
            print(f"[prospect_loop] SignalFanout failed: {exc}")

        enriched: List[Dict[str, Any]] = []
        for c in contacts:
            company = getattr(c, "company", "") or ""
            job_title = _contact_job_title(c)
            c_tokens = _tokens(f"{company} {job_title}")
            scored = []
            for sig in signals:
                s_tokens = _tokens(
                    f"{sig.get('title', '')} {' '.join(sig.get('topics', []) or [])}"
                    if isinstance(sig, dict) else str(sig)
                )
                overlap = len(c_tokens & s_tokens)
                scored.append((overlap, sig))
            scored.sort(key=lambda x: x[0], reverse=True)
            matched = [sig for ov, sig in scored[:3]]
            enriched.append({
                "contact": c,
                "matched_signals": matched,
                "match_scores": [ov for ov, _ in scored[:3]],
            })
        return enriched

    # ------------------------------------------------------------------ #
    # 3. Draft outreach (template-only, no LLM)
    # ------------------------------------------------------------------ #
    def draft_outreach(self, contact: Any, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a personalized outreach draft from templates + attached signals."""
        first = getattr(contact, "first_name", "") or "there"
        company = getattr(contact, "company", "") or "your team"

        hooks: List[str] = []
        signal_lines: List[str] = []
        for i, sig in enumerate(signals or []):
            topic = (sig.get("title") or "what's happening in your space").strip()
            source = sig.get("source", "")
            hooks.append(topic[:80])
            signal_lines.append(
                f"{i + 1}. Saw the conversation around \"{topic}\""
                + (f" (via {source})" if source else "")
                + " — we help teams with exactly this."
            )

        if signal_lines:
            body = (
                f"Hi {first},\n\n"
                f"I've been following the buzz around {company}'s space lately:\n\n"
                + "\n".join(signal_lines)
                + "\n\nWe work with teams like yours to turn this kind of momentum "
                  "into pipeline. Open to a quick 15-minute chat this week?\n\n"
                  "Best,\nMarketic"
            )
            subject = f"{first}, the {company} angle on {hooks[0][:40] if hooks else 'this'}"
        else:
            body = (
                f"Hi {first},\n\n"
                f"We help teams at companies like {company} grow faster with "
                "signal-driven marketing. Open to a quick 15-minute chat?\n\n"
                "Best,\nMarketic"
            )
            subject = f"A thought for {company}"

        return {
            "contact_id": getattr(contact, "contact_id", ""),
            "subject": subject.strip(),
            "body": body,
            "personalization_hooks": hooks,
        }

    # ------------------------------------------------------------------ #
    # Fallback prospect synthesis from signals
    # ------------------------------------------------------------------ #
    def _prospects_from_signals(self, signals: List[Dict[str, Any]],
                                limit: int) -> List[Any]:
        """Synthesize placeholder prospects from signal titles when Serper is down."""
        try:
            from integrations.unified_adapter import Contact as _C
        except ImportError:  # pragma: no cover
            from marketic.integrations.unified_adapter import Contact as _C  # type: ignore

        class SimpleContact:  # lightweight stand-in mirroring Contact fields used here
            pass

        prospects: List[Any] = []
        seen = set()
        for sig in signals:
            if len(prospects) >= limit:
                break
            title = sig.get("title", "") or ""
            m = re.search(r"\b([A-Z][A-Za-z0-9]{2,}(?:\.[A-Za-z]{2,})?)\b", title.replace(" ", " ", 1))
            company = m.group(1) if m else f"SignalCo{len(prospects) + 1}"
            if company.lower() in seen:
                continue
            seen.add(company.lower())
            sc = SimpleContact()
            sc.contact_id = f"sig_{abs(hash(company)) % 10**10}"
            sc.email = ""
            sc.phone = ""
            sc.first_name = "There"
            sc.last_name = ""
            sc.company = company
            sc.job_title = None
            sc.lifecycle_stage = "prospect"
            sc.attributes = {"source": "signals", "signal_title": title}
            sc.tags = ["signals-fallback"]
            prospects.append(sc)
        return prospects

    # ------------------------------------------------------------------ #
    # 4. Orchestration
    # ------------------------------------------------------------------ #
    async def run(self, niche_query: str, market_query: str,
                  limit: int = 5) -> Dict[str, Any]:
        """discover → enrich_with_signals → draft_outreach → insert into CRM."""
        contacts = await self.discover(niche_query, limit=limit)

        enriched = await self.enrich_with_signals(contacts, market_query)

        # Graceful degradation: derive prospects from the signals themselves.
        fallback_used = False
        if not enriched:
            fallback_used = True
            try:
                brief = await self.fanout.run(query=market_query)
                signals = list(brief.get("brief_top_10") or [])
            except Exception:
                signals = []
            placeholder_contacts = self._prospects_from_signals(signals, limit=limit)
            enriched = await self.enrich_with_signals(placeholder_contacts, market_query)
            print(f"[prospect_loop] fallback active: {len(placeholder_contacts)} "
                  "signal-derived prospects.")

        drafts: List[Dict[str, Any]] = []
        added = 0
        skipped_existing = 0
        for item in enriched:
            contact = item["contact"]
            matched = item["matched_signals"]
            try:
                draft = self.draft_outreach(contact, matched)
            except Exception as exc:  # noqa: BLE001
                print(f"[prospect_loop] draft failed for {contact}: {exc}")
                continue

            lead_id = ""
            try:
                email = getattr(contact, "email", "") or \
                    f"{(getattr(contact, 'first_name', '') or 'unknown').lower()}@{getattr(contact, 'company', 'unknown').lower().replace(' ', '')}.placeholder"
                source = "signals" if fallback_used else "prospect_loop_serper"
                tags = ["prospect-loop"] + [
                    (s.get("source") or "signal") for s in matched
                ]
                lead_id = None
                try:
                    lead = self.crm.create_lead(
                        email=email,
                        first_name=getattr(contact, "first_name", "") or "",
                        last_name=getattr(contact, "last_name", "") or "",
                        phone=getattr(contact, "phone", "") or "",
                        company=getattr(contact, "company", "") or "",
                        job_title=_contact_job_title(contact),
                        source=source,
                        tags=tags,
                    )
                    lead_id = lead.lead_id
                    added += 1
                except Exception as exc:
                    if "UNIQUE" in str(exc):
                        # already in CRM — treat as skip, not error
                        skipped_existing += 1
                    else:
                        print(f"[prospect_loop] CRM insert failed: {exc}")

                if lead_id:
                    # Score: number of matched signals x 10 (own write; does not
                    # modify crm/__init__.py). Applied on top of CRMMaster base.
                    score = float(len(matched)) * 10.0
                    conn = get_connection()
                    try:
                        conn.execute(
                            "UPDATE crm_leads SET score = score + ?, "
                            "updated_at = CURRENT_TIMESTAMP WHERE lead_id = ?",
                            (score, lead_id),
                        )
                        conn.commit()
                    finally:
                        conn.close()
            except Exception as exc:  # noqa: BLE001
                print(f"[prospect_loop] CRM insert failed: {exc}")

            drafts.append({
                **draft,
                "lead_id": lead_id,
                "company": getattr(contact, "company", ""),
                "matched_signal_count": len(matched),
                "source": getattr(contact, "attributes", {}).get("source", "serper")
                          if hasattr(contact, "attributes") else "signals",
            })

        return {
            "niche_query": niche_query,
            "market_query": market_query,
            "discovered": len(enriched),
            "added_to_crm": added,
            "fallback_to_signals": fallback_used,
            "drafts": drafts,
        }


# ---------------------------------------------------------------------- #
# Smoke test — safe defaults; degrades gracefully without API keys.
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    async def _smoke():
        loop = ProspectLoop()
        result = await loop.run(
            niche_query="fintech",
            market_query="ai agents marketing",
            limit=5,
        )
        print("=== ProspectLoop smoke ===")
        print(f"discovered:      {result['discovered']}")
        print(f"added_to_crm:    {result['added_to_crm']}")
        print(f"fallback_active: {result['fallback_to_signals']}")
        for d in result["drafts"]:
            print(f"- [{d['company']}] subject={d['subject']!r} "
                  f"hooks={len(d['personalization_hooks'])}")
        assert isinstance(result["drafts"], list)
        print("SMOKE OK")

    asyncio.run(_smoke())
