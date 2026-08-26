# marketic — Performance Marketing Module

## PART VIII: PERFORMANCE MARKETING MODULE

**Based on vault research: 500+ items covering paid ads, ROAS, attribution, e-commerce, Google/Meta ads**

---

## 1. Overview

The performance marketing module is the **closed loop** that makes marketic a true operating system, not just a content generator.

```
signals/ → competitive/ → creative/ → variants/
                                        ↓
                              campaign/launcher/
                                        ↓
                            ┌───────────┴───────────┐
                            ↓                       ↓
                      performance/              analytics/
                      (THE CLOSED LOOP)         (reporting)
                            ↓                       ↓
                      bid_optimization          dashboards
                            ↓                       ↓
                      budget_router            reports
                            ↓                       ↓
                      ab_tester ←───────────── attribution
                            ↓
                      ROAS_tracker
                            ↓
                      funnel_analyzer
```

---

## 2. Module Structure

```
marketic/
├── performance/              # NEW - Full performance marketing module
│   ├── __init__.py
│   ├── roas_tracker.py      # Track ROAS in real-time
│   ├── bid_optimizer.py     # AI-powered bid optimization
│   ├── budget_router.py     # Cross-platform budget routing
│   ├── ab_tester.py         # Automated A/B testing
│   ├── funnel_analyzer.py   # TOF/MOF/BOF analysis
│   ├── attribution.py       # Multi-touch attribution
│   ├── incrementality.py     # Incrementality testing
│   ├── dash.py              # Performance dashboard generator
│   └── cli.py               # CLI: perf status, optimize, report
│
├── video_ads/               # NEW - AI video ad generation
│   ├── __init__.py
│   ├── script_gen.py        # Generate video ad scripts
│   ├── thumbnail_gen.py     # Generate thumbnails
│   ├── voiceover.py         # AI voiceover (ElevenLabs integration)
│   ├── platform_adapter.py   # Adapt content for TikTok/IG/Reels/YT
│   └── batch.py             # Batch generate 100s of variants
│
├── ecommerce/               # NEW - E-commerce specific
│   ├── __init__.py
│   ├── storefront_tracker.py # Track Shopify/WooCommerce
│   ├── product_feed.py      # Google Shopping / Meta Catalog
│   ├── review_ads.py        # Review-based ad generation
│   └── competitor_price.py   # Price intelligence
│
└── tracking/                # NEW - Server-side tracking
    ├── __init__.py
    ├── server_side.py       # GTM server-side conversion tracking
    ├── enhanced_conv.py     # Enhanced conversions API
    ├── offline_conv.py      # Offline conversion uploads
    └── gclid_tracker.py     # Google Click ID tracking
```

---

## 3. The Four Differentiators

### 3.1 Real-Time ROAS Optimization

**Vault source:** "Low ROAS bids don't always yield low ROAS - let algorithm optimize, start small and increase"

**What it does:**
- Monitors ROAS per ad set/campaign/keyword in real-time
- AI decides: increase bid, decrease bid, or pause
- Learns from conversion lag (90-day Google learning phase)
- Respects campaign structure: testing vs scaling vs retargeting

**Implementation:**
```python
class ROASOptimizer:
    """
    AI-powered ROAS optimization.
    
    Rules from vault:
    - Don't judge ROAS until 90-day learning phase complete
    - Start small bids, scale winners
    - Let algorithm optimize (don't override constantly)
    - TACOS > ROAS as profitability metric
    """
    
    def analyze(self, campaign_id: str) -> OptimizationAction:
        """
        Returns: increase_bid | decrease_bid | pause | no_change
        with confidence score and reasoning
        """
    
    def optimize_bid(self, ad_set_id: str, target_roas: float) -> BidRecommendation:
        """
        AI generates bid recommendation based on:
        - Current ROAS vs target
        - Conversion volume
        - Cost per conversion trend
        - Learning phase status
        """
```

**Key metrics tracked:**
- ROAS (Return on Ad Spend)
- TACOS (Total Advertising Cost of Sales) — vault says this is the "north star"
- Contribution margin per product
- Blended ROAS across campaigns

---

### 3.2 AI-Generated UGC Video Ads

**Vault sources:**
- Nano Banana + n8n → "1,000+ ad variations in minutes"
- $100K Cadbury ad recreated for $15 using Seedance + Nano Banana
- Goose Ads (Claude skill) — "finds competitor ads and remakes them"
- Pomelli (Google Labs) — "generates on-brand content from URLs"
- Arcads — "AI video ads with gesture control"
- Viggle LIVE — "real-time video with motion capture"

**What it does:**
- Takes competitor creative analysis → generates counter-variants
- Generates 100s of video ad scripts in minutes
- Adds AI voiceover (ElevenLabs)
- Generates thumbnails (Flux/DALL-E)
- Adapts for each platform (TikTok: 15s, IG Reels: 30s, YT: 60s)

**Pipeline:**
```
competitor_analysis (from competitive/)
    → video_ads/script_gen.py (generate 100+ scripts)
    → video_ads/voiceover.py (ElevenLabs audio)
    → video_ads/thumbnail_gen.py (static variants)
    → video_ads/batch.py (render 100s of combinations)
    → campaign/launcher.py (launch to Meta/Google/TikTok)
    → performance/roas_tracker.py (measure)
    → creative/ranker.py (rank by actual ROAS)
```

**Vault workflow (n8n-based):**
```
1. Claude analyzes competitor ads
2. Nano Banana generates image ads
3. Arcads/Viggle generates video variants
4. ElevenLabs generates voiceover
5. n8n assembles and publishes
```

---

### 3.3 Cross-Platform Budget Router

**Vault sources:**
- Full funnel strategy: TOF (catch-all), MOF (feed PMax), BOF (brand + retargeting)
- "+32% sales increase" from funnel implementation
- Cross-platform intelligence (Google vs Meta vs LinkedIn)

**What it does:**
- Monitors ROAS/CPA across Google, Meta, LinkedIn, TikTok
- AI shifts budget to best performers automatically
- Maintains funnel structure (TOF feeds MOF feeds BOF)
- Respects pacing constraints (don't overspend day 1)

**Funnel Architecture (from vault):**
```
┌─────────────────────────────────────────┐
│           TOF (Top of Funnel)            │
│  Catch-all, broad targeting              │
│  Objective: Awareness + Consideration     │
│  Campaigns: Shopping (all products)       │
│  Budget: 30%                             │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│          MOF (Middle of Funnel)           │
│  Feed-only PMax, retargeting             │
│  Objective: Conversion                   │
│  Campaigns: Performance Max (feed only)   │
│  Budget: 40%                             │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│          BOF (Bottom of Funnel)          │
│  Brand keywords + retargeting            │
│  Objective: Direct Response              │
│  Campaigns: Brand + Retargeting          │
│  Budget: 30%                             │
└─────────────────────────────────────────┘
```

**CLI Usage:**
```bash
# Route budget based on last 7 days performance
marketic perf route --platforms google,meta --lookback 7d --strategy roas

# Run full funnel optimization
marketic perf funnel --current '{"TOF": 30, "MOF": 40, "BOF": 30}' --target roas 3.0
```

---

### 3.4 Attribution + Incrementality

**Vault sources:**
- "Enhanced conversions → up to 15% increase in registered conversions"
- "Lexi dashboard — clean ROAS, CPA, CTR (zero clicks)"
- Multi-touch attribution models
- Incrementality testing for campaign evaluation

**What it does:**

#### Attribution Models (from analytics/ module):
- First touch
- Last touch
- Last non-direct click
- Linear
- Time decay
- Position-based (40% first, 40% last, 20% middle)
- **Data-driven** (ML-based, when data allows)

#### Incrementality Testing:
```
control_group (no ads) ←→ holdout ←→ exposed_group (saw ads)
                              ↓
                    measure: did exposed buy more?
                    report: +X% lift, statistical significance
```

#### Server-Side Tracking:
- GTM server-side container setup
- Enhanced conversions API (conversions API)
- Offline conversion uploads with gclid
- Consent mode (GDPR/CCPA compliance)

**Implementation:**
```python
class IncrementalityTester:
    """
    Run holdout-based incrementality tests.
    
    Vault insight: Attribution can overcount upper-funnel.
    Incrementality measures TRUE lift from advertising.
    """
    
    def design_test(
        self,
        campaign_id: str,
        test_duration_days: int = 14,
        control_size_percent: float = 10.0
    ) -> TestDesign:
        """
        Returns: test/control split, duration, success criteria
        """
    
    def analyze_results(self, test_id: str) -> TestResult:
        """
        Returns: lift %, confidence interval, statistical significance
        """
```

---

## 4. CLI Interface

```bash
# Performance status dashboard
marketic perf status --campaigns campaign_1,campaign_2
marketic perf status --platforms google,meta --date-range 7d

# ROAS optimization
marketic perf optimize-roas --campaign-id abc123 --target-roas 3.0

# Budget routing
marketic perf route --strategy roas --lookback 7d --min-roas 2.0

# Funnel analysis
marketic perf funnel --funnel-type DTC --products product_1,product_2

# A/B test management
marketic perf ab create --ad-set-id xyz --variants 3 --metric roas
marketic perf ab results --test-id test_123

# Attribution report
marketic perf attribution --model linear --date-range 30d --channels google,meta,linkedin

# Incrementality test
marketic perf incrementality design --campaign-id abc123
marketic perf incrementality results --test-id test_456

# Video ad generation
marketic video generate --competitor notion --count 100 --platforms tiktok,meta,yt

# E-commerce tracking
marketic track shopify --store-url mystore.myshopify.com
marketic track enhanced-conv --upload-csv conversions.csv
```

---

## 5. Integration with Existing Modules

### Full Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT: MARKET INTELLIGENCE                   │
├─────────────────────────────────────────────────────────────────┤
│  signals/                                                         │
│  Reddit + Twitter + Trends → "buzz score" per brand/topic        │
│                          ↓                                        │
│  competitive/                                                      │
│  GoMarble + Apify → competitor ads, pricing, positioning          │
│                          ↓                                        │
│  creative/                                                         │
│  Ad copy variants + social content                                │
│                          ↓                                        │
│  video_ads/                                                        │
│  100s of video scripts + voiceover + thumbnails                   │
│                          ↓                                        │
│  creative/ranker.py                                               │
│  Rank by gap exploitation + expected performance                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     LAUNCH & MONITOR                             │
├─────────────────────────────────────────────────────────────────┤
│  campaign/launcher.py                                             │
│  Composio MCP → Meta Ads + LinkedIn + Google Ads                 │
│                          ↓                                        │
│  tracking/ (server-side, enhanced conversions)                    │
│  Track every conversion with full attribution                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     PERFORMANCE CLOSED LOOP                       │
├─────────────────────────────────────────────────────────────────┤
│  performance/                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ ROAS Tracker │  │Bid Optimizer │  │Budget Router │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  A/B Tester  │  │Funnel Analyzer│ │Attribution   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐                                               │
│  │Incrementality│                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT: INTELLIGENCE                         │
├─────────────────────────────────────────────────────────────────┤
│  analytics/dashboards.py → ROAS/CPA/CTR dashboards              │
│  analytics/reports.py → Weekly automated reports                  │
│  signals/ (feedback) → What worked? What didn't?                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Platform-Specific Capabilities

### Google Ads
| Capability | Implementation |
|-----------|----------------|
| PMax optimization | Custom labels, asset group splits, audience signals |
| Bid strategy | Target ROAS, Maximize Conversions, Manual CPC |
| Scripts | Automated bid adjustments based on rules |
| GMC (Google Merchant Center) | Product feed optimization, broken link detection |
| Enhanced conversions | Server-side tracking, conversion API |

### Meta Ads
| Capability | Implementation |
|-----------|----------------|
| Campaign structure | 3-campaign: testing / scaling / retargeting |
| Andromeda AI | Seeding strategy, creative volume |
| Lookalike audiences | Build from highest LTV customers |
| Retargeting | Website visitors, engagement, purchase |

### LinkedIn Ads
| Capability | Implementation |
|-----------|----------------|
| Lead gen forms | Auto-populate CRM from form submissions |
| Matched audiences | Company targeting + job title |
| InMail | Personalized outreach sequences |

---

## 7. Metrics Tracked

### Primary KPIs
| Metric | Formula | Vault Insight |
|--------|---------|--------------|
| **ROAS** | Revenue / Ad Spend | 2.5-3x+ target for D2C |
| **TACOS** | Ad Spend / Total Revenue | "North star" per vault |
| **CPA** | Ad Spend / Conversions | Varies by industry |
| **CTR** | Clicks / Impressions | Creative quality indicator |
| **CVR** | Conversions / Clicks | Landing page + offer quality |

### Secondary KPIs
| Metric | Formula |
|--------|---------|
| **LTV** | Lifetime value per customer |
| **Contribution Margin** | Revenue - COGS - Ad Spend |
| **Effective CPM** | Cost / Impressions × 1000 |
| **Frequency** | Impressions / Unique Reach |

---

## 8. Build Sequence

### Phase A: Performance Foundation (Weeks 7-8)

Add to existing `campaign/` module:
- [ ] `performance/roas_tracker.py` — Track ROAS per campaign/ad set
- [ ] `performance/bid_optimizer.py` — Basic bid rules engine
- [ ] `performance/dash.py` — Performance dashboard generator

### Phase B: Budget Routing (Weeks 9-10)

- [ ] `performance/budget_router.py` — Cross-platform router
- [ ] `performance/funnel_analyzer.py` — TOF/MOF/BOF structure
- [ ] `campaign/launcher.py` — Composio Meta/Google/LinkedIn launch

### Phase C: Testing & Attribution (Weeks 11-12)

- [ ] `performance/ab_tester.py` — Automated A/B test analysis
- [ ] `performance/attribution.py` — Multi-touch models
- [ ] `performance/incrementality.py` — Holdout testing
- [ ] `tracking/` — Server-side tracking

### Phase D: Video Ads (Weeks 13-14)

- [ ] `video_ads/script_gen.py` — Video script generation
- [ ] `video_ads/voiceover.py` — ElevenLabs integration
- [ ] `video_ads/thumbnail_gen.py` — AI thumbnail generation
- [ ] `video_ads/batch.py` — Batch variant generation

---

## 9. External Integrations

| Platform | Integration | Vault Reference |
|----------|-------------|----------------|
| **Google Ads API** | Composio MCP or direct API | Audit checklists, PMax scripts |
| **Meta Marketing API** | social-cli or Composio | $0/month running via OpenClaw |
| **LinkedIn Ads API** | Composio MCP | Lead gen forms |
| **Shopify** | Storefront API | CEO dashboard automation |
| **Google Merchant Center** | Content API | Product feed optimization |
| **ElevenLabs** | Voiceover API | UGC video ads |
| **TikTok Ads API** | Revid AI MCP | Video creation/scheduling |

---

## 10. Vault Content Mapping

| Vault Item | Used In |
|------------|---------|
| Goose Ads (Claude skill) | competitive/analysis + video_ads/script_gen |
| GoMarble MCP | competitive/extractor + performance/attribution |
| Nano Banana + n8n workflow | video_ads/batch.py |
| Pomelli (Google Labs) | creative/seo.py + video_ads/script_gen |
| Arcads + Viggle | video_ads/video_gen.py |
| Full funnel strategy | performance/funnel_analyzer.py |
| +32% case study | performance/budget_router.py |
| Lexi dashboard | analytics/dashboards.py |
| Enhanced conversions +15% | tracking/enhanced_conv.py |
| social-cli (Meta) | campaign/launcher.py |
| OpenClaw ($0 Meta) | campaign/launcher.py |

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| ROAS improvement (optimized vs baseline) | +20% |
| Time to optimize bid decision | < 1 hour (vs daily manual) |
| Creative variants generated per competitor | 100+ |
| Funnel budget reallocation | Weekly automated |
| Attribution model accuracy | R² > 0.7 |
| Incrementality test completion | 1 test per month per major campaign |
