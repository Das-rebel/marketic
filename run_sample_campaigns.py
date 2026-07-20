#!/usr/bin/env python3
"""
Complete Marketic MCP Sample Campaign Suite
Runs 4 end-to-end marketing campaigns and documents each result.
"""
import json
import subprocess
import sys
import os
from datetime import datetime

SERVER = "/Users/Subho/marketic/mcp_server.py"
RESULTS_DIR = "/Users/Subho/marketic/sample_campaign_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def call_tool(name, arguments, req_id=1):
    """Call a single Marketic MCP tool and return parsed result."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
        "id": req_id
    }) + "\n"
    result = subprocess.run(
        ["python3", SERVER],
        input=payload,
        capture_output=True,
        text=True,
        timeout=15
    )
    # Parse last JSON line from stdout
    for line in reversed(result.stdout.strip().split('\n')):
        line = line.strip()
        if line.startswith('{'):
            try:
                data = json.loads(line)
                if "error" in data:
                    return {"_error": data["error"]}
                content = data.get("result", {}).get("content", [{}])[0].get("text", "{}")
                return json.loads(content)
            except json.JSONDecodeError:
                continue
    return {"_error": "No valid response received"}


def call_tool_raw(name, arguments, req_id=1):
    """Call a tool and return the full JSON-RPC envelope (for debugging)."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
        "id": req_id
    }) + "\n"
    result = subprocess.run(
        ["python3", SERVER],
        input=payload,
        capture_output=True,
        text=True,
        timeout=15
    )
    for line in reversed(result.stdout.strip().split('\n')):
        line = line.strip()
        if line.startswith('{'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def save_result(name, data):
    """Save campaign result to file."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RESULTS_DIR, f"{name}_{ts}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return path


# ═══════════════════════════════════════════════════════════════
# CAMPAIGN A: Position-and-Attack
# ═══════════════════════════════════════════════════════════════
def campaign_a():
    print("\n" + "=" * 60)
    print("CAMPAIGN A: Position-and-Attack (Quay vs HubSpot)")
    print("=" * 60)

    results = {}

    # Step 1: Analyze competitor
    print("\n[Step 1/3] analyze_competitor(HubSpot)...")
    r = call_tool("analyze_competitor", {
        "brand": "HubSpot",
        "category": "marketing automation"
    }, req_id=1)
    results["competitor_analysis"] = r
    print(f"  ✓ Done — confidence: {r.get('confidence', 'N/A')}")

    # Step 2: Analyze positioning
    print("[Step 2/3] analyze_positioning(Quay)...")
    r = call_tool("analyze_positioning", {
        "brand": "Quay AI Factory",
        "product": "Quay",
        "industry": "AI/ML platforms"
    }, req_id=2)
    results["positioning"] = r
    print(f"  ✓ Done")

    # Step 3: Generate creatives
    print("[Step 3/3] generate_creatives(linkedin_sponsored, 3 variants)...")
    r = call_tool("generate_creatives", {
        "product_name": "Quay AI Factory",
        "product_description": "Self-hosted AI agents with marketing intelligence",
        "channel": "linkedin_sponsored",
        "num_variants": 3,
        "tone": "persuasive",
        "target_audience": "CTOs and VP Engineering",
        "key_benefits": ["Self-hosted", "Cost transparency", "No vendor lock-in"]
    }, req_id=3)
    results["creatives"] = r
    count = r.get("count", 0) if isinstance(r, dict) else 0
    print(f"  ✓ Done — {count} variants generated")

    path = save_result("campaign_a_position_attack", results)
    print(f"\n📦 Results saved to: {path}")
    return results


# ═══════════════════════════════════════════════════════════════
# CAMPAIGN B: ROAS Optimizer
# ═══════════════════════════════════════════════════════════════
def campaign_b():
    print("\n" + "=" * 60)
    print("CAMPAIGN B: ROAS Optimizer ($10K Budget Reallocation)")
    print("=" * 60)

    results = {}

    # Step 1: Get attribution
    print("\n[Step 1/2] get_attribution(linear model)...")
    r = call_tool("get_attribution", {
        "channel_points": [
            {"channel": "google_search", "touchpoints": 150, "conversion_value": 17500},
            {"channel": "meta_feed", "touchpoints": 100, "conversion_value": 6300},
            {"channel": "linkedin_sponsored", "touchpoints": 75, "conversion_value": 3600}
        ],
        "model": "linear"
    }, req_id=4)
    results["attribution"] = r
    print(f"  ✓ Done")

    # Step 2: Optimize budget
    print("[Step 2/2] optimize_budget($10K across 3 channels)...")
    r = call_tool("optimize_budget", {
        "total_budget": 10000,
        "current_allocation": {
            "google_search": 5000,
            "meta_feed": 3000,
            "linkedin_sponsored": 2000
        },
        "channel_performance": {
            "google_search": {"roas": 3.5, "conversions": 250},
            "meta_feed": {"roas": 2.1, "conversions": 180},
            "linkedin_sponsored": {"roas": 1.8, "conversions": 120}
        }
    }, req_id=5)
    results["optimization"] = r
    print(f"  ✓ Done")

    path = save_result("campaign_b_roas_optimizer", results)
    print(f"\n📦 Results saved to: {path}")
    return results


# ═══════════════════════════════════════════════════════════════
# CAMPAIGN C: Creative-Bomb (Full Launch Kit)
# ═══════════════════════════════════════════════════════════════
def campaign_c():
    print("\n" + "=" * 60)
    print("CAMPAIGN C: Creative-Bomb (Product Launch Kit)")
    print("=" * 60)

    results = {}

    # Step 1: Generate ad creatives
    print("\n[Step 1/3] generate_creatives(meta_feed, 5 variants)...")
    r = call_tool("generate_creatives", {
        "product_name": "Quay AI Factory",
        "product_description": "Self-hosted AI agents that plan, code, review, and deploy",
        "channel": "meta_feed",
        "num_variants": 5,
        "tone": "emotional",
        "target_audience": "Startup founders and growth hackers",
        "key_benefits": ["Full automation", "Cost transparency", "MIT licensed"]
    }, req_id=6)
    results["ad_creatives"] = r
    count = r.get("count", 0) if isinstance(r, dict) else 0
    print(f"  ✓ Done — {count} variants")

    # Step 2: Generate social posts
    print("[Step 2/3] generate_social_posts(linkedin thread, 3 posts)...")
    r = call_tool("generate_social_posts", {
        "topic": "Self-hosted AI agents for marketing automation",
        "platform": "linkedin",
        "format": "thread",
        "tone": "professional",
        "length": 3,
        "hashtags": True
    }, req_id=7)
    results["social_posts"] = r
    print(f"  ✓ Done")

    # Step 3: Build campaign
    print("[Step 3/3] build_campaign(multi-channel, $8K, 4 weeks)...")
    r = call_tool("build_campaign", {
        "campaign_name": "Quay-AI-Launch-Q3-2026",
        "objective": "conversion",
        "target_audience": "B2B SaaS growth teams",
        "channels": ["meta_feed", "google_search", "email"],
        "duration_weeks": 4,
        "total_budget": 8000
    }, req_id=8)
    results["campaign_plan"] = r
    print(f"  ✓ Done")

    path = save_result("campaign_c_creative_bomb", results)
    print(f"\n📦 Results saved to: {path}")
    return results


# ═══════════════════════════════════════════════════════════════
# CAMPAIGN D: SEO Content Engine
# ═══════════════════════════════════════════════════════════════
def campaign_d():
    print("\n" + "=" * 60)
    print("CAMPAIGN D: SEO Content Engine")
    print("=" * 60)

    results = {}

    # Step 1: Generate SEO content
    print("\n[Step 1/2] generate_seo_content(AI marketing automation)...")
    r = call_tool("generate_seo_content", {
        "target_keyword": "AI marketing automation",
        "content_type": "blog_post",
        "word_count": 1500
    }, req_id=9)
    results["seo_content"] = r
    print(f"  ✓ Done")

    # Step 2: Generate brand narrative
    print("[Step 2/2] generate_narrative(brand_story)...")
    r = call_tool("generate_narrative", {
        "narrative_type": "brand_story",
        "brand": "Quay AI Factory",
        "industry": "AI/ML",
        "product": "Self-hosted AI software factory"
    }, req_id=10)
    results["narrative"] = r
    print(f"  ✓ Done")

    path = save_result("campaign_d_seo_content", results)
    print(f"\n📦 Results saved to: {path}")
    return results


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    all_results = {}

    print("╔" + "═" * 58 + "╗")
    print("║  MARKETIC MCP — COMPLETE CAMPAIGN SUITE (4 Campaigns)   ║")
    print("╚" + "═" * 58 + "╝")

    all_results["campaign_a"] = campaign_a()
    all_results["campaign_b"] = campaign_b()
    all_results["campaign_c"] = campaign_c()
    all_results["campaign_d"] = campaign_d()

    # Save combined results
    master_path = save_result("ALL_CAMPAIGNS_MASTER", all_results)
    print("\n" + "=" * 60)
    print(f"✅ ALL 4 CAMPAIGNS COMPLETE")
    print(f"📦 Master results: {master_path}")
    print("=" * 60)