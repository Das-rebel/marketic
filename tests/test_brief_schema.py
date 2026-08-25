"""
Brief Schema Lock Test — guards the generate_brief contract.

Any change to the brief's key shape fails here BEFORE it breaks
downstream execution agents. See docs/BRIEF_SCHEMA.md.

Run: pytest tests/test_brief_schema.py -v
"""
import sys, os, pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.brief import generate_brief


@pytest.fixture(scope="module")
def brief():
    return generate_brief(
        campaign_name="LockTest",
        objective="conversion",
        product_name="Widget",
        product_description="A test widget",
        target_audience="testers",
        channels=["social", "email"],
        total_budget=10000,
        key_benefits=["fast", "cheap"],
    )


EXPECTED_TOP_KEYS = {
    "brief_version", "generated_at", "campaign", "brand_kit",
    "product", "budget", "posting_windows_utc", "execution_contract",
}

BRAND_TOKEN_KEYS = {
    "{{brand.primary}}", "{{brand.background}}", "{{brand.accent}}",
    "{{brand.secondary}}", "{{brand.font}}", "{{brand.handle}}",
    "{{brand.name}}", "{{brand.tagline}}",
}


def test_top_level_keys_exact(brief):
    assert set(brief.keys()) == EXPECTED_TOP_KEYS


def test_schema_version_is_10(brief):
    assert brief["brief_version"] == "1.0"


def test_campaign_fields(brief):
    c = brief["campaign"]
    assert {"name", "objective", "duration_weeks"} <= set(c.keys())
    assert isinstance(c["duration_weeks"], int)


def test_brand_kit_has_all_tokens(brief):
    bk = brief["brand_kit"]
    missing = BRAND_TOKEN_KEYS - set(bk.keys())
    assert not missing, f"missing brand tokens: {missing}"
    assert isinstance(bk["banned_words"], list)
    for k in BRAND_TOKEN_KEYS:
        assert isinstance(bk[k], str) and bk[k], f"token {k} empty"


def test_budget_split_sums_to_total(brief):
    b = brief["budget"]
    split_sum = sum(item["amount"] for item in b["recommended_split"])
    assert abs(split_sum - b["total"]) < 0.01


def test_execution_contract_rules(brief):
    ec = brief["execution_contract"]
    assert ec["renders_from_tokens_only"] is True
    assert isinstance(ec["expected_outputs"], list) and ec["expected_outputs"]
    assert isinstance(ec["must_not"], list)


def test_posting_windows_shape(brief):
    pw = brief.get("posting_windows_utc")
    if pw:  # optional key
        assert isinstance(pw, dict)
        for channel, times in pw.items():
            assert isinstance(times, list)
