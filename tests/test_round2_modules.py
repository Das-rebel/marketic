"""
Round-2 module tests: crm/prospect_loop, ensemble/learnings,
creative/seo_generator.rank_opportunities, gtm/fb_ads_library.

Run: python3 -m pytest tests/test_round2_modules.py -q --confcutdir=. -o addopts=""
"""
import asyncio
import os
import sqlite3
import sys
import uuid

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm.prospect_loop import ProspectLoop
from crm import get_connection
from ensemble.learnings import LearningEngine
from creative.seo_generator import rank_opportunities
from gtm.fb_ads_library import FBAdsLibraryClient


# ---------------------------------------------------------------------- #
# 1. crm/prospect_loop.ProspectLoop
# ---------------------------------------------------------------------- #

class _FakeContact:
    def __init__(self, company="Acme", first_name="Ada"):
        self.contact_id = f"c_{company}"
        self.email = ""
        self.phone = ""
        self.first_name = first_name
        self.last_name = ""
        self.company = company
        self.job_title = "Head of Growth"
        self.lifecycle_stage = "prospect"
        self.attributes = {}
        self.tags = []


def test_draft_outreach_contains_company_and_signal_keyword():
    loop = ProspectLoop()
    contact = _FakeContact(company="Acme")
    signals = [{
        "title": "AI agents for fintech growth",
        "source": "hn",
        "topics": ["ai", "fintech"],
        "score": 1.0,
        "engagement_raw": 100,
    }]
    draft = loop.draft_outreach(contact, signals)

    assert set(["subject", "body", "personalization_hooks"]).issubset(draft)
    assert "Acme" in draft["body"]
    # at least one signal keyword token appears in the body
    body_lower = draft["body"].lower()
    assert any(kw in body_lower for kw in ("ai", "fintech", "growth"))
    assert draft["personalization_hooks"]


def test_run_twice_same_niche_no_unique_crash():
    """
    Integration-ish: DB path is hardcoded in crm/__init__.py (no env override),
    so we run against the real DB but stub the network layers (adapter/fanout)
    for speed and determinism. The second run must hit the UNIQUE-constraint
    skip path instead of raising.
    """
    marker = f"deditest_{uuid.uuid4().hex[:8]}"

    class _FakeFanout:
        async def run(self, query="", sources=None, limit_per_source=25):
            return {"brief_top_10": [
                {"title": f"{marker} growth playbook", "source": "hn",
                 "url": "http://x/1", "score": 1.0, "engagement_raw": 5},
                {"title": f"{marker} pricing trends", "source": "reddit",
                 "url": "http://x/2", "score": 0.9, "engagement_raw": 4},
            ], "errors": {}}

    def _fake_prospects(self, signals, limit=5):
        contacts = []
        for i, sig in enumerate(signals):
            c = _FakeContact(company=f"{marker}Co{i}")
            c.attributes = {"source": "signals"}
            contacts.append(c)
        return contacts

    loop = ProspectLoop()
    loop.fanout = _FakeFanout()
    loop._prospects_from_signals = _fake_prospects.__get__(loop, ProspectLoop)

    async def _go():
        # Force the fallback path deterministically (discover returns []).
        async def _no_discover(niche_query, limit=10):
            return []
        loop.discover = _no_discover
        r1 = await loop.run(f"{marker} niche", f"{marker} market", limit=3)
        r2 = await loop.run(f"{marker} niche", f"{marker} market", limit=3)
        return r1, r2

    r1, r2 = asyncio.run(_go())
    for r in (r1, r2):
        assert set(r) >= {
            "niche_query", "market_query", "discovered",
            "added_to_crm", "fallback_to_signals", "drafts",
        }
    # second run must not have re-added the same leads (UNIQUE skipped)
    assert r2["added_to_crm"] == 0

    # cleanup rows we created
    conn = get_connection()
    try:
        conn.execute("DELETE FROM crm_leads WHERE company LIKE ?", (f"{marker}%",))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------- #
# 2. ensemble/learnings.LearningEngine
# ---------------------------------------------------------------------- #
# NOTE: LearningEngine's get_connection uses a hardcoded marketic_memory.db
# path (ensemble/audit_trail.py) with no env override, so tests use a unique
# brand name and clean up via direct SQL.

@pytest.fixture()
def learning_brand():
    return f"test_{uuid.uuid4().hex[:10]}"


def _cleanup_learnings(brand):
    from ensemble.audit_trail import get_connection as _gc
    conn = _gc()
    try:
        conn.execute("DELETE FROM learnings WHERE brand = ?", (brand,))
        conn.commit()
    finally:
        conn.close()


def test_capture_dedup_and_confidence_growth(learning_brand):
    eng = LearningEngine()
    rule = f"Always cap CAC payback at {learning_brand} months"
    try:
        id1 = eng.capture(learning_brand, "cost", rule)
        row1 = eng.get_learning(id1) if hasattr(eng, "get_learning") else None
        id2 = eng.capture(learning_brand, "cost", rule)
        assert id1 == id2, "identical rule should update, not duplicate"

        # occurrences incremented to 2 after second capture
        confs = []
        ids = [id1]
        for _ in range(1):  # third capture below
            pass
        eng.capture(learning_brand, "cost", rule)
        eng.capture(learning_brand, "cost", rule)

        conn = sqlite3.connect(os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "marketic_memory.db")))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM learnings WHERE brand = ?", (learning_brand,)
        ).fetchall()
        conn.close()

        assert len(rows) == 1, "must be exactly one row for identical rules"
        assert rows[0]["occurrences"] == 4
        assert rows[0]["confidence"] > 0.5, (
            "confidence should rise above initial default after captures")
    finally:
        _cleanup_learnings(learning_brand)


def test_export_brain_md_writes_rule(tmp_path, learning_brand):
    eng = LearningEngine()
    rule = f"Prefer {learning_brand} organic over paid during launch"
    try:
        lid = eng.capture(learning_brand, "strategy", rule)
        eng.approve(lid)
        path = eng.export_brain_md(learning_brand, out_dir=str(tmp_path))
        assert os.path.exists(path)
        content = open(path).read()
        assert rule in content
    finally:
        _cleanup_learnings(learning_brand)


# ---------------------------------------------------------------------- #
# 3. creative/seo_generator.rank_opportunities
# ---------------------------------------------------------------------- #

def test_rank_opportunities_sorts_by_difficulty_ascending():
    signals = [
        {"keyword": "hard", "difficulty": 90},
        {"keyword": "easy", "difficulty": 10},
        {"keyword": "mid", "difficulty": 50},
    ]
    ranked = rank_opportunities(signals)
    assert [s["difficulty"] for s in ranked] == [10, 50, 90]


def test_rank_opportunities_empty():
    assert rank_opportunities([]) == []
    assert rank_opportunities(None) == []


def test_rank_opportunities_missing_difficulty_defaults_high():
    signals = [
        {"keyword": "nodiff"},               # missing -> treated as high (last)
        {"keyword": "easy", "difficulty": 5},
        {"keyword": "baddiff", "difficulty": "not-a-number"},  # invalid -> high
    ]
    ranked = rank_opportunities(signals)
    assert ranked[0]["keyword"] == "easy"
    assert ranked[-1]["keyword"] in ("nodiff", "baddiff")


# ---------------------------------------------------------------------- #
# 4. gtm/fb_ads_library.FBAdsLibraryClient
# ---------------------------------------------------------------------- #

def test_fb_unavailable_without_token(monkeypatch):
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    client = FBAdsLibraryClient()
    assert client.is_available() is False


def test_fb_search_ads_returns_empty_when_unavailable(monkeypatch):
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    client = FBAdsLibraryClient()
    result = client.search_ads("SomeBrand")
    assert result == []
