"""
Generate README visual assets.
Run: python3 docs/assets/generate_assets.py
Outputs: docs/assets/
"""
from __future__ import annotations
import os

OUT = os.path.join(os.path.dirname(__file__))

# -----------------------------------------------------------------------
# 1. Architecture flow diagram
# -----------------------------------------------------------------------
def build_architecture_diagram():
    """ASCII/Unicode architecture flow — no external deps needed."""
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║                      MARKETIC — THE FLOW                     ║",
        "╠══════════════════════════════════════════════════════════════╣",
        "║                                                               ║",
        "║   ┌─────────────┐      ┌─────────────┐      ┌───────────┐ ║",
        "║   │   SENSE     │      │    THINK    │      │  HANDOFF  │ ║",
        "║   │             │      │             │      │           │ ║",
        "║   │ Polymarket  │      │ Ensemble AI │      │  Brief    │ ║",
        "║   │ Google      │ ───▶ │ Scorecard   │ ───▶ │  (JSON)   │ ║",
        "║   │ Trends IN   │      │ Budget      │      │           │ ║",
        "║   │ HN / Reddit │      │ Router      │      │  Brand    │ ║",
        "║   │ X / YouTube │      │ Ad Analyzer │      │  Tokens   │ ║",
        "║   │ Indian RSS  │      │ Prospect    │      │           │ ║",
        "║   │ FB Ads Lib  │      │ Scout       │      │  Posting  │ ║",
        "║   └─────────────┘      └─────────────┘      │  Windows  │ ║",
        "║          │                   │              └─────┬─────┘ ║",
        "║          │                   │                    │       ║",
        "║          ▼                   ▼                    ▼       ║",
        "║   ┌─────────────────────────────────────────────────────┐ ║",
        "║   │                      LEARN                          │ ║",
        "║   │   Audit Trail  →  Distillation  →  Brand Brain   │ ║",
        "║   │   (every decision logged)   (patterns)  (markdown)│ ║",
        "║   └─────────────────────────────────────────────────────┘ ║",
        "║                                                               ║",
        "╚══════════════════════════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


# -----------------------------------------------------------------------
# 2. Sample daily briefing (ASCII)
# -----------------------------------------------------------------------
def build_sample_briefing():
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║           MARKETIC DAILY BRIEFING — 2026-08-27           ║",
        "╠══════════════════════════════════════════════════════════════╣",
        "║                                                               ║",
        "║  GOOD MORNING. HERE IS WHAT MATTERS TODAY.                ║",
        "║                                                               ║",
        "║  ── TOP SIGNALS ─────────────────────────────────────     ║",
        "║                                                               ║",
        "║  ① Kraken IPO buzz                                         ║",
        "║     $1.6M bet · 15% probability · Effective: $240K          ║",
        "║     SOURCE: Polymarket  ·  SCORE: 72/100                   ║",
        "║     ACTION: Ride this narrative in fintech content this week ║",
        "║                                                               ║",
        "║  ② UK election called                                      ║",
        "║     $822K bet · 31% probability · Effective: $255K          ║",
        "║     SOURCE: Polymarket  ·  SCORE: 81/100                   ║",
        "║     ACTION: Strong signal — angle: UK fintech regulation    ║",
        "║                                                               ║",
        "║  ③ D2C skincare conversation (India)                       ║",
        "║     Rising Google searches: 'sabse acha moisturizer'         ║",
        "║     SOURCE: Google Trends IN  ·  SCORE: 68/100            ║",
        "║     ACTION: Publish skincare content before the spike peaks  ║",
        "║                                                               ║",
        "║  ── IGNORE ───────────────────────────────────────────     ║",
        "║  ⚠ Macron out speculation  $2.1M / 4%  · Drama, not signal ║",
        "║     Probability-adjusted: $84K effective · SCORE: 18/100    ║",
        "║                                                               ║",
        "║  ── BUDGET ───────────────────────────────────────────     ║",
        "║  Recommended split: Email $8,908 · Paid Social $6,092      ║",
        "║  Reasoning: Email 85% margin vs Paid Social 15% margin      ║",
        "║  (Margin-adjusted, not vanity-ROAS)                        ║",
        "║                                                               ║",
        "║  ── COMPETITOR ALERT ─────────────────────────────────     ║",
        "║  Brand X launched new ad: 'Skin that survives Delhi heat'   ║",
        "║  Hook: survival · CTA: shop now · Counter-angle: clinical   ║",
        "║                                                               ║",
        "║  ── CALIBRATION ─────────────────────────────────────     ║",
        "║  Tracked: 47  ·  Resolved: 12  ·  Brier: 0.14           ║",
        "║  Polymarket signals well-calibrated (Brier 0.09, n=8)     ║",
        "║  Twitter signals need more data (Brier 0.31, n=22)        ║",
        "║                                                               ║",
        "╚══════════════════════════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


# -----------------------------------------------------------------------
# 3. Matplotlib charts
# -----------------------------------------------------------------------
def build_matplotlib_charts():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    # ── Chart 1: Calibration Brier score by source ──────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    sources = ['Polymarket', 'Google\nTrends', 'Hacker\nNews', 'Reddit', 'Twitter', 'Product\nHunt']
    brier   = [0.09, 0.12, 0.18, 0.24, 0.31, 0.28]
    n_preds = [8, 12, 6, 15, 22, 9]
    colors  = ['#22c55e' if b < 0.15 else '#f59e0b' if b < 0.25 else '#ef4444' for b in brier]

    bars = ax.bar(sources, brier, color=colors, width=0.6, edgecolor='white', linewidth=0.5)
    ax.axhline(0.25, color='#94a3b8', linestyle='--', linewidth=1, label='Random (0.25)')
    ax.axhline(0.15, color='#22c55e', linestyle=':', linewidth=1, label='Good (< 0.15)')

    for bar, n in zip(bars, n_preds):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'n={n}', ha='center', va='bottom', fontsize=8, color='#64748b')

    ax.set_ylabel('Brier Score (lower = better)', fontsize=10)
    ax.set_title('Signal Calibration by Source', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylim(0, 0.40)
    ax.legend(loc='upper right', fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    green = mpatches.Patch(color='#22c55e', label='Well-calibrated (<0.15)')
    amber = mpatches.Patch(color='#f59e0b', label='Uncertain (0.15–0.25)')
    red   = mpatches.Patch(color='#ef4444', label='Poorly calibrated (>0.25)')
    ax.legend(handles=[green, amber, red, plt.Line2D([0], [0], color='#94a3b8', linestyle='--', label='Random')],
              loc='upper right', fontsize=8)

    plt.tight_layout()
    path1 = os.path.join(OUT, 'chart_calibration.png')
    plt.savefig(path1, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path1}")

    # ── Chart 2: Tool coverage donut ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 7))
    categories = [
        'GTM / Intel\n(20 tools)',
        'AI Ops\n(4 tools)',
        'CRM\n(6 tools)',
        'Creative\n(3 tools)',
        'Publishing\n(3 tools)',
        'UGC\n(3 tools)',
        'Calibration\n(3 tools)',
        'Other\n(13 tools)',
    ]
    sizes  = [20, 4, 6, 3, 3, 3, 3, 13]
    palette = ['#6366f1','#8b5cf6','#a855f7','#d946ef','#ec4899','#f43f5e','#f97316','#94a3b8']
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=palette[:len(sizes)],
        autopct='%1.0f%%', startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        pctdistance=0.82,
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight('bold')
        at.set_color('white')

    ax.legend(wedges, categories, loc='lower center', bbox_to_anchor=(0.5, -0.12),
               ncol=2, fontsize=8.5, frameon=False)
    ax.set_title('55 Tools Across 15 Categories', fontsize=13, fontweight='bold', pad=12)
    fig.patch.set_facecolor('white')

    # Centre label
    ax.text(0, 0, '55\nTools', ha='center', va='center', fontsize=18,
            fontweight='bold', color='#1e293b')

    plt.tight_layout()
    path2 = os.path.join(OUT, 'chart_tools.png')
    plt.savefig(path2, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path2}")

    # ── Chart 3: Budget allocation comparison ─────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    channels = ['Email\nMarketing', 'Paid\nSocial', 'Content\nMarketing', 'Organic\nSocial']
    roas     = [5.2, 3.8, 2.1, 1.4]
    margins  = [85, 15, 62, 100]

    x = np.arange(len(channels))
    ax1.bar(x, roas, color='#6366f1', width=0.5, edgecolor='white')
    ax1.set_xticks(x)
    ax1.set_xticklabels(channels, fontsize=9)
    ax1.set_ylabel('ROAS (×)', fontsize=10)
    ax1.set_title('ROAS by Channel', fontsize=11, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_facecolor('#f8fafc')
    for bar, v in zip(ax1.patches, roas):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{v}×', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.bar(x, margins, color='#f97316', width=0.5, edgecolor='white')
    ax2.set_xticks(x)
    ax2.set_xticklabels(channels, fontsize=9)
    ax2.set_ylabel('Contribution Margin (%)', fontsize=10)
    ax2.set_title('Margin by Channel', fontsize=11, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_facecolor('#f8fafc')
    ax2.set_ylim(0, 120)
    for bar, v in zip(ax2.patches, margins):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{v}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    fig.patch.set_facecolor('white')
    plt.suptitle('Vanilla ROAS vs. Margin-Adjusted Budget Allocation',
                 fontsize=12, fontweight='bold', y=1.01)
    plt.tight_layout()
    path3 = os.path.join(OUT, 'chart_budget.png')
    plt.savefig(path3, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path3}")

    return path1, path2, path3


# -----------------------------------------------------------------------
# Generate all
# -----------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    # ASCII diagrams
    arch = build_architecture_diagram()
    with open(os.path.join(OUT, 'architecture.txt'), 'w') as f:
        f.write(arch)
    print(f"Saved: {OUT}/architecture.txt")

    briefing = build_sample_briefing()
    with open(os.path.join(OUT, 'sample_briefing.txt'), 'w') as f:
        f.write(briefing)
    print(f"Saved: {OUT}/sample_briefing.txt")

    # PNG charts
    p1, p2, p3 = build_matplotlib_charts()
    print("\nAll assets generated successfully.")
    print(f"  {OUT}/architecture.txt")
    print(f"  {OUT}/sample_briefing.txt")
    print(f"  {p1}")
    print(f"  {p2}")
    print(f"  {p3}")
