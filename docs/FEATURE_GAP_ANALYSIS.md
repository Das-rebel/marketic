# Marketic vs Helena — Feature Gap Analysis

## Overview

**Helena** (Bukito Setup) = Brand voice specialist + Creative execution pipeline  
**Marketic** = Strategic marketing intelligence + Orchestration layer

---

## Feature Comparison Matrix

| Category | Feature | Helena | Marketic | Gap |
|----------|---------|--------|----------|-----|
| **Strategy** | Content calendar planning | ✅ | ❌ | **GAP** |
| | Campaign planning | ✅ | ✅ | — |
| | Social strategy | ✅ | ❌ | **GAP** |
| | Competitive analysis | ❌ | ✅ | Helena missing |
| | Positioning maps | ❌ | ✅ | Helena missing |
| **Creative** | Ad copy generation | ❌ | ✅ | — |
| | Social post generation | ✅ | ✅ | — |
| | SEO content | Partial | ✅ | — |
| | Static posts (design) | ✅ (Paper MCP) | ❌ | **GAP** |
| | Animated video | ✅ (Remotion) | ❌ | **GAP** |
| | AI video from photos | ✅ (Runway) | ❌ | **GAP** |
| **Brand** | Brand voice/personality | ✅ | ❌ | **GAP** |
| | Color palette rules | ✅ | ❌ | **GAP** |
| | Typography rules | ✅ | ❌ | **GAP** |
| | Logo/asset management | ✅ | ❌ | **GAP** |
| **Distribution** | Scheduling via Postiz | ✅ | ❌ | **GAP** |
| | Multi-platform posting | ✅ (Postiz) | ❌ | **GAP** |
| | UGC curation | ✅ | ❌ | **GAP** |
| | Hashtag monitoring | ✅ | ❌ | **GAP** |
| **Intelligence** | Engagement analytics | ✅ | ❌ | **GAP** |
| | Signal collection | ❌ | ✅ | Helena missing |
| | Competitive intel | ❌ | ✅ | Helena missing |
| | Attribution modeling | ❌ | ✅ | Helena missing |
| **Execution** | Hub integrations | ❌ | ✅ | — |
| | CRM (leads/deals) | ❌ | ✅ | — |
| | Budget optimization | ❌ | ✅ | — |
| **AI** | Ensemble voting | ❌ | ✅ | Helena missing |
| | Full audit trail | ❌ | ✅ | Helena missing |
| | Multi-model routing | ❌ | ✅ | Helena missing |

---

## What's Unique to Marketic (Helena Missing)

| Feature | Description |
|---------|-------------|
| **Ensemble AI Voting** | Multi-model confidence-weighted decision making |
| **Full Audit Trail** | Every AI decision logged with reasoning chain |
| **Competitive Intelligence** | Deep analysis, positioning maps, SWOT |
| **Attribution Modeling** | 5 models: first-touch, last-touch, linear, time-decay, position-based |
| **Signal Collection** | Product Hunt, HN, Twitter, Reddit intelligence |
| **Hub Orchestration** | Unified API for 8+ marketing platforms |
| **CRM** | Complete lead/deal/activity management |
| **Budget Router** | ROAS-based budget rebalancing |

---

## What's Unique to Helena (Marketic Missing)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Brand Voice System** | Personality, tone, language rules | HIGH |
| **Design Templates** | Static post layouts (Paper MCP) | HIGH |
| **Video Generation** | Remotion + Runway AI video | HIGH |
| **Publishing Pipeline** | Postiz integration for scheduling | HIGH |
| **Content Calendar** | Planning + scheduling workflow | HIGH |
| **UGC Curation** | Hashtag monitoring, permission workflow | MEDIUM |
| **Asset Management** | Photo library, Supabase storage | MEDIUM |
| **Engagement Analytics** | Platform-native metrics | MEDIUM |

---

## Recommended Additions to Marketic

### HIGH Priority

1. **Brand Voice Module** (`memory/voice_profile.py`)
   - Already exists: `voice_profile.py` — needs integration
   - Brand personality, tone rules, language patterns

2. **Design Template System** (new: `creative/design_templates.py`)
   - Static post layouts (Instagram, Twitter, Facebook)
   - Paper MCP integration
   - Platform-specific dimensions

3. **Publishing Pipeline** (new: `execution/publisher.py`)
   - Postiz API integration
   - Multi-platform scheduling
   - Content calendar management

4. **UGC Curation** (new: `creative/ugc_collector.py`)
   - Hashtag monitoring
   - Permission request templates
   - Repost workflow

### MEDIUM Priority

5. **Video Generation** (new: `creative/video_generator.py`)
   - Runway API integration
   - Remotion template system
   - AI clip generation from photos

6. **Asset Management** (new: `memory/asset_manager.py`)
   - Photo/video library
   - Supabase storage integration
   - Brand asset versioning

7. **Engagement Analytics** (extend: `analytics/engagement.py`)
   - Platform-native metrics
   - Cross-platform dashboard
   - Performance trends

---

## Architecture Comparison

### Helena: Agent + Skills Pattern
```
Helena (agent)
├── bukito-brand (skill) — brand rules
├── bukito-content (skill) — creative generation
└── bukito-ugc (skill) — UGC curation
    ├── Paper MCP — design canvas
    ├── Runway API — AI video
    ├── Remotion — animated video
    └── Postiz — scheduling
```

### Marketic: Module Layer Pattern
```
Marketic (MCP server)
├── ensemble/ — AI voting + audit
├── creative/ — copy generation
├── campaign/ — strategy + budgets
├── gtm/ — competitive intel
├── signals/ — market signals
├── analytics/ — attribution
├── integrations/ — platform hub
└── crm/ — lead/deal management
```

---

## Conclusion

**Marketic** is a **strategic intelligence layer** — it excels at analysis, planning, and orchestration across multiple channels and platforms.

**Helena** is a **brand-embedded execution agent** — it deeply understands the brand voice and owns the creative-to-publishing pipeline.

**The gap is execution, not strategy.**

Marketic needs a **content execution layer** to go from "generate campaign" to "publish and measure."

---

*Generated: 2026-08-24*
