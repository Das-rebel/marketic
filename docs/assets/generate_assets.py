"""
Regenerate README visual assets — Mermaid diagrams + ASCII.
These render natively in GitHub Flavored Markdown (GFM).
Run: python3 docs/assets/generate_assets.py
"""
from __future__ import annotations
import os

OUT = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# 1. Architecture — Mermaid flowchart
# ---------------------------------------------------------------------------
def build_architecture_mmd():
    return """```mermaid
flowchart LR
    subgraph SENSE["📡 SENSE"]
        P[Polymarket]
        G[Google Trends]
        H[Hacker News]
        R[Reddit]
        X[X / Twitter]
        Y[YouTube]
        I[Indian RSS]
        F[FB Ads Library]
    end

    subgraph THINK["🧠 THINK"]
        EA[Ensemble AI]
        SC[Scorecard]
        BR[Budget Router]
        AA[Ad Analyzer]
        PS[Prospect Scout]
    end

    subgraph HANDOFF["📋 HANDOFF"]
        BF[Brief JSON]
        BT[Brand Tokens]
        PW[Posting Windows]
    end

    subgraph LEARN["🔄 LEARN"]
        AT[Audit Trail]
        DS[Distillation]
        BB[Brand Brain]
    end

    SENSE -->|"volume × P(YES)"| THINK
    SENSE -->|"all signals"| SC
    THINK -->|"scored signals"| EA
    EA -->|"reasoned"| BR
    EA -->|"ad insights"| AA
    EA -->|"prospects"| PS
    BR -->|"budget split"| BF
    AA -->|"counter-angles"| BF
    PS -->|"enriched leads"| BF
    BF -->|"handoff"| HANDOFF
    BT --> HANDOFF
    PW --> HANDOFF
    HANDOFF -->|"execute"| AT
    AT -->|"patterns"| DS
    DS -->|"approved rules"| BB
    BB -->|"inject"| THINK

    classDef sense fill:#6366f1,color:#fff,stroke:none
    classDef think fill:#f59e0b,color:#fff,stroke:none
    classDef handoff fill:#22c55e,color:#fff,stroke:none
    classDef learn fill:#f43f5e,color:#fff,stroke:none

    class P,G,H,R,X,Y,I,F sense
    class EA,SC,BR,AA,PS think
    class BF,BT,PW handoff
    class AT,DS,BB learn
```
"""


# ---------------------------------------------------------------------------
# 2. Calibration pie — Mermaid
# ---------------------------------------------------------------------------
def build_calibration_mmd():
    return """```mermaid
pie title Signal Calibration — Last 30 Days
    "Polymarket (Brier 0.09 ✅)" : 12
    "Google Trends (Brier 0.14 ✅)" : 8
    "Hacker News (Brier 0.21 ⚠️)" : 6
    "Reddit (Brier 0.28 ⚠️)" : 9
    "Twitter/X (Brier 0.31 ⚠️)" : 14
    "Product Hunt (Brier 0.24 ⚠️)" : 5
```
"""


# ---------------------------------------------------------------------------
# 3. Tool coverage — Mermaid
# ---------------------------------------------------------------------------
def build_tools_mmd():
    return """```mermaid
flowchart TB
    subgraph GTM["🎯 GTM & Intel (20 tools)"]
        A1[search_fb_ads]
        A2[analyze_competitor_ad]
        A3[analyze_competitor]
        A4[analyze_positioning]
        A5[breakdown_ad]
        A6[generate_narrative]
        A7[discover_prospects]
        A8[signal_fanout]
        A9[collect_signals]
    end

    subgraph CORE["⚙️ Core (12 tools)"]
        B1[generate_creatives]
        B2[generate_social_posts]
        B3[generate_seo_content]
        B4[build_campaign]
        B5[optimize_budget]
        B6[launch_campaign_ad]
        B7[generate_brief]
        B8[run_prospect_loop]
        B9[distill_learnings]
        B10[ask_marketic]
        B11[run_workflow]
        B12[...]
    end

    subgraph DATA["📊 Data & Learning (13 tools)"]
        C1[track_signal]
        C2[get_calibration_report]
        C3[resolve_signal]
        C4[ensemble_vote]
        C5[audit_log]
        C6[audit_get_log]
        C7[get_cost_summary]
        C8[get_attribution]
        C9[crm_*]
        C10[crm_*]
        C11[crm_*]
        C12[crm_*]
        C13[crm_*]
    end

    subgraph PUB["🚀 Publishing & UGC (10 tools)"]
        D1[schedule_content]
        D2[get_upcoming_posts]
        D3[optimize_hashtags]
        D4[curate_ugc]
        D5[request_ugc_permission]
        D6[track_ugc]
        D7[render_template]
        D8[hub_*]
        D9[build_utm_url]
        D10[parse_utm_params]
    end

    classDef gtm fill:#6366f1,color:#fff,stroke:none
    classDef core fill:#f59e0b,color:#fff,stroke:none
    classDef data fill:#22c55e,color:#fff,stroke:none
    classDef pub fill:#f43f5e,color:#fff,stroke:none

    class A1,A2,A3,A4,A5,A6,A7,A8,A9 GTM
    class B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,B11,B12 CORE
    class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13 DATA
    class D1,D2,D3,D4,D5,D6,D7,D8,D9,D10 PUB
```
"""


# ---------------------------------------------------------------------------
# 4. The Monday Problem — rich ASCII
# ---------------------------------------------------------------------------
def build_monday_ascii():
    return r"""
```
╔══════════════════════════════════════════════════════════════╗
║             YOUR MONDAY WITHOUT MARKETIC                     ║
╚══════════════════════════════════════════════════════════════╝

  7:45 AM  Wake up. Coffee. Open laptop.

  8:00 AM  Open 7 browser tabs:

              +-------------------------------------+
              |  Google Trends    "what's trending?"  |
              |  Competitor ads   "what launched?"    |
              |  Mixpanel        "why did last wk drop?"|
              |  LinkedIn        "what's everyone saying?"|
              |  Slack #mktg   "did anyone reply?"     |
              |  Email to analyst "can you pull..."     |
              |  HubSpot        "which lead converted?"  |
              +-------------------------------------+

  9:30 AM  Still don't know what actually matters today.

  10:00 AM Stand-up. Wing it.


╔══════════════════════════════════════════════════════════════╗
║             YOUR MONDAY WITH MARKETIC                       ║
╚══════════════════════════════════════════════════════════════╝

  7:58 AM  Notification: "Your briefing is ready"

  8:00 AM  Read 6 sentences:

              +-----------------------------------------+
              |  ① Kraken IPO buzz ($1.6M, 15% likely)  |
              |     → Ride this in fintech content today    |
              |  ② D2C skincare India rising (Google IN)  |
              |     → Publish before the spike peaks        |
              |  ③ Shark Tank India: 3x mentions wk/wk   |
              |     → "As seen on Shark Tank" angle        |
              |  ⚠ IGNORED: Crypto drama ($4M, 6% likely)|
              |     → Probability-adjusted out of the brief  |
              |  📊 Budget: Email $9,200 · Social $5,800  |
              |     → Email margin 85% > Social 15%        |
              |  🤖 Competitor X: new ad live since Tue    |
              |     → Counter-angle: clinical vs DIY       |
              +-----------------------------------------+

  8:07 AM  Coffee. Done.

  8:08 AM  Start the actual work.
```"""


# ---------------------------------------------------------------------------
# 5. Sample brief — formatted ASCII
# ---------------------------------------------------------------------------
def build_sample_brief():
    return r"""
```
+=========================================================================+
|  MARKETIC BRIEF — GlowSkincare India · Generated 2026-08-27        |
+=========================================================================+
|  SIGNAL SUMMARY                    |  BUDGET ALLOCATION               |
|  -------------------------------  |  ------------------------------  |
|  ① Kraken IPO buzz  SCORE 72     |  Email    $9,200  60%            |
|     $1.6M bet · 15% probability   |  (margin: 85%)                   |
|  ② D2C skincare IN   SCORE 68     |  Social   $6,100  40%            |
|     Rising Google searches          |  (margin: 15%)                   |
|  ③ Shark Tank India  SCORE 61     |                                  |
|     3x mentions wk/wk              |                                  |
|  -------------------------------  |                                  |
|  ⚠ IGNORED: Crypto $4M / 6%     |                                  |
|  (noise, probability-adjusted)      |                                  |
+=========================================================================+
|  COMPETITOR INTEL — Brand X "Skin that survives Delhi heat"          |
|  ----------------------------------------------------------------     |
|  Running since Aug 20 · Est. spend $12-18K/wk                       |
|  Hook: survival · Offer: heat-proof · CTA: shop now                 |
|  Counter-angles:                                                     |
|    ① Clinical vs DIY: "Derms agree: $47 gel > $300 AC"            |
|    ② Speed: "Results in 14 days or money back"                     |
|    ③ Transparency: "We list every active ingredient"                |
+=========================================================================+
|  COPY VARIANTS                     |  POSTING WINDOWS (India)         |
|  -------------------------------  |  ------------------------------  |
|  A: "Your skin deserves clinical  |  7:00-9:00 AM                   |
|     -grade care"                 |  12:00-1:00 PM                  |
|  B: "Dermatologist-approved.      |  7:00-9:00 PM                   |
|     Now in India."                |                                  |
|  C: "Skincare that actually works |                                  |
|     in Delhi heat"               |                                  |
|  -------------------------------  |                                  |
|  BRAND TOKENS: #6D0000 · DM Sans · @glowskinofficial               |
+=========================================================================+
```"""


# ---------------------------------------------------------------------------
# 6. Calibration table
# ---------------------------------------------------------------------------
def build_calibration_table():
    return r"""
```
SIGNAL CALIBRATION — Last 30 Days
====================================================
 Source            Signals   Brier   Verdict
----------------------------------------------------
 Polymarket              12    0.09   ✅  Well-calibrated
 Google Trends            8    0.14   ✅  Reliable
 Hacker News              6    0.21   ⚠️  Uncertain
 Reddit                   9    0.28   ⚠️  Needs data
 Twitter / X             14    0.31   ⚠️  Needs data
 Product Hunt             5    0.24   ⚠️  Needs data
----------------------------------------------------
 Overall                54    0.19   📊  Honest
 Random baseline         —    0.25   ---------  --------
====================================================

Brier score:  0.00 = perfect  ·  0.25 = random  ·  Higher = worse

Interpretation:
  Polymarket (0.09): right ~9 out of 10 times — trust this first
  Twitter/X (0.31): 3 more weeks of data needed before acting on it
  This is the first marketing tool that tells you how wrong it might be.
```"""


# ---------------------------------------------------------------------------
# 7. Comparison table
# ---------------------------------------------------------------------------
def build_comparison():
    return r"""
```
TIME SPENT ON MONDAY MORNING
====================================================
 Task                  Before        With Marketic
----------------------------------------------------
 Finding signals        45 min    →     5 min
 Competitor research    60 min    →    10 min
 Building the brief     40 min    →     5 min
 Budget analysis        30 min    →     5 min
----------------------------------------------------
 TOTAL                175 min    →    25 min     (-86%)
 TIME SAVED PER WEEK:   3.2 hours
====================================================

DECISIONS INFORMED PER DAY
----------------------------------------------------
                Before    With Marketic
 Monday           2-3         4-5
 Tuesday          1-2         2-3
 Wednesday        2-3         3-4
 Thursday         3-4         5-6
 Friday           1-2         2-3
----------------------------------------------------
 Weekly avg        9          17         (+89%)
====================================================
```"""


# ---------------------------------------------------------------------------
# Generate all artifacts
# ---------------------------------------------------------------------------
def main():
    artifacts = {
        'monday_problem.txt':      build_monday_ascii(),
        'sample_brief.txt':        build_sample_brief(),
        'calibration_table.txt':    build_calibration_table(),
        'comparison_table.txt':     build_comparison(),
    }

    for fname, content in artifacts.items():
        path = os.path.join(OUT, fname)
        with open(path, 'w') as f:
            f.write(content.strip() + '\n')
        print(f"Saved: {path}")

    mmd_files = {
        'architecture.mmd': build_architecture_mmd(),
        'calibration.mmd':  build_calibration_mmd(),
        'tools.mmd':        build_tools_mmd(),
    }
    for fname, content in mmd_files.items():
        path = os.path.join(OUT, fname)
        with open(path, 'w') as f:
            f.write(content.strip() + '\n')
        print(f"Saved: {path}")

    # Index README for docs/assets/
    index = [
        "# Visual Assets",
        "",
        "All artifacts render natively in GitHub Flavored Markdown — no images, no dependencies.",
        "",
        "## Mermaid Diagrams (render in GitHub, VS Code, any GFM viewer)",
        "",
        "| File | Description |",
        "|---|---|",
        "| [`architecture.mmd`](architecture.mmd) | SENSE → THINK → HANDOFF → LEARN flow |",
        "| [`calibration.mmd`](calibration.mmd) | Signal calibration by source (pie chart) |",
        "| [`tools.mmd`](tools.mmd) | 55 tools across 4 groups |",
        "",
        "## Text Artifacts (always render, even in terminals)",
        "",
        "| File | Description |",
        "|---|---|",
        "| [`monday_problem.txt`](monday_problem.txt) | The before/after Monday illustration |",
        "| [`sample_brief.txt`](sample_brief.txt) | Full campaign brief in ASCII box format |",
        "| [`calibration_table.txt`](calibration_table.txt) | Brier scores with interpretation |",
        "| [`comparison_table.txt`](comparison_table.txt) | Before/after time and decision comparison |",
        "",
        "## Embed in README",
        "",
        "Mermaid: copy `.mmd` content into a ````mermaid``` fenced code block.",
        "Text: copy `.txt` content into a ```` ``` ```` fenced code block.",
        "",
        "## Regenerate",
        "```bash",
        "python3 docs/assets/generate_assets.py",
        "```",
    ]
    path = os.path.join(OUT, 'README.md')
    with open(path, 'w') as f:
        f.write('\n'.join(index) + '\n')
    print(f"Saved: {path}")


if __name__ == '__main__':
    main()
