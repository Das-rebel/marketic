# marketic — Performance Marketing MCPs, Agents & Capabilities

**Vault research: 16 queries, 500+ items covering all paid ads automation, MCP servers, and marketing agents**

---

## PART IX: PERFORMANCE MARKETING MCP ECOSYSTEM

### The MCP Landscape (from vault)

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERFORMANCE MARKETING MCPs                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  GoMarble   │  │  Composio   │  │  Goose Ads  │            │
│   │  (Meta/Google)│ │ (Meta/LI/HS)│  │  (Meta)     │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  Apify MCP  │  │  Revid_ai   │  │  Higgsfield │            │
│   │  (Scraping) │  │  (TikTok)   │  │ (Google Ads)│            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  Firecrawl  │  │  Browser    │  │   n8n MCP  │            │
│   │   MCP       │  │   MCP       │  │  (525+     │            │
│   │             │  │             │  │   nodes)   │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. MCP Integration Architecture

```
marketic/
├── mcp/                          # NEW - MCP client layer
│   ├── __init__.py
│   ├── client.py                 # Unified MCP client wrapper
│   ├── registry.py               # MCP server registry
│   │
│   ├── servers/                  # MCP server integrations
│   │   ├── __init__.py
│   │   ├── gomarble.py           # GoMarble: Meta/Google Ads
│   │   ├── composio.py            # Composio: HubSpot/SF/Meta/LI
│   │   ├── goose_ads.py           # Goose Ads: Meta competitor intel
│   │   ├── apify.py               # Apify: 1000+ scrapers
│   │   ├── revid.py               # Revid: TikTok creation
│   │   ├── firecrawl.py           # Firecrawl: AI scraping
│   │   ├── browser_mcp.py          # Browser: Web access
│   │   ├── google_analytics.py    # GA: Natural language queries
│   │   └── n8n_mcp.py             # n8n: 525+ workflow nodes
│   │
│   └── orchestrator.py            # Orchestrate multiple MCPs together
```

### MCP Registry

```python
MCP_REGISTRY = {
    "gomarble": {
        "platform": "meta_ads",
        "capabilities": [
            "competitor_creative_intel",
            "rca_performance_drops",
            "weekly_client_reports",
            "ad_library_search",
        ],
        "auth": "api_key",
        "vault_ref": "GoMarble + Meta Ad Library - 4 min competitor intel",
    },
    "composio": {
        "platform": "multi",
        "capabilities": [
            "meta_ads",
            "linkedin_ads",
            "hubspot_crm",
            "salesforce_crm",
            "google_ads",
        ],
        "auth": "oauth",
        "vault_ref": "Marketing Skills v1.4.0 - Composio integration",
    },
    "goose_ads": {
        "platform": "meta",
        "capabilities": [
            "competitor_ad_finder",
            "converting_angle_mining",
            "ad_creation",
        ],
        "auth": "api_key",
        "vault_ref": "Goose Ads MCP - finds trending ads, mines converting angles",
    },
    "apify": {
        "platform": "scraping",
        "capabilities": [
            "tiktok_data",
            "instagram_data",
            "twitter_scraping",
            "competitor_pricing",
            "product_data",
        ],
        "auth": "api_key",
        "vault_ref": "Apify MCP - 1000+ pre-built scrapers",
    },
    "revid_ai": {
        "platform": "tiktok",
        "capabilities": [
            "video_creation",
            "video_scheduling",
            "video_publishing",
        ],
        "auth": "api_key",
        "vault_ref": "Revid_ai MCP - TikTok create/schedule/publish",
    },
    "higgsfield": {
        "platform": "google_ads",
        "capabilities": [
            "creative_generation",
            "ad_variants",
            "copy_testing",
        ],
        "auth": "api_key",
        "vault_ref": "Higgsfield MCP - Google Ads creative generation",
    },
    "firecrawl": {
        "platform": "scraping",
        "capabilities": [
            "web_crawl",
            "sitemap_extract",
            "ai_ready_output",
        ],
        "auth": "api_key",
        "vault_ref": "Firecrawl MCP - search + scrape web",
    },
    "n8n_mcp": {
        "platform": "workflow",
        "capabilities": [
            "all_525_nodes",
            "workflow_creation",
            "automation_trigger",
        ],
        "auth": "self_hosted",
        "vault_ref": "n8n MCP - Claude knows all 525+ n8n nodes",
    },
}
```

---

## 2. Full MCP Capability Matrix

| MCP Server | Ad Platforms | CRM | Creative Gen | Scraping | Analytics | Workflow |
|---|---|---|---|---|---|---|
| **GoMarble** | ✅ Meta, Google | ❌ | ❌ | ✅ Ad Library | ✅ RCA | ❌ |
| **Composio** | ✅ Meta, LI, Google | ✅ HubSpot, SF | ❌ | ❌ | ❌ | ❌ |
| **Goose Ads** | ✅ Meta | ❌ | ✅ Ad creation | ✅ Trend mining | ❌ | ❌ |
| **Apify** | ❌ | ❌ | ❌ | ✅ 1000+ scrapers | ❌ | ❌ |
| **Revid** | ✅ TikTok | ❌ | ✅ Videos | ❌ | ❌ | ❌ |
| **Higgsfield** | ✅ Google | ❌ | ✅ Creatives | ❌ | ❌ | ❌ |
| **Firecrawl** | ❌ | ❌ | ❌ | ✅ Web pages | ❌ | ❌ |
| **n8n MCP** | ✅ All | ✅ All | ✅ Via nodes | ✅ Via nodes | ✅ Via nodes | ✅ 525+ |
| **GA MCP** | ❌ | ❌ | ❌ | ❌ | ✅ GA queries | ❌ |
| **Browser MCP** | ❌ | ❌ | ❌ | ✅ 30+ web tools | ❌ | ❌ |

---

## 3. Integration Implementation

### 3.1 GoMarble MCP — Competitor Creative Intelligence

**Vault source:** "GoMarble + Meta Ad Library = Competitor Creative Intelligence in 4 minutes. Replacing $160/hr Creative Strategists."

```python
class GoMarbleMCP:
    """
    GoMarble MCP integration for Meta + Google Ads intelligence.
    
    Vault capabilities:
    - RCA for performance drops
    - Weekly client update generation
    - Competitor creative intelligence via Meta Ad Library
    """
    
    async def get_competitor_ads(self, competitor_name: str, days: int = 90) -> List[AdData]:
        """
        Get all ads from a competitor over N days.
        Returns: List of ads with creative, copy, targeting, spend estimate
        """
    
    async def analyze_performance_drop(
        self,
        campaign_id: str,
        date_range: str = "7d"
    ) -> RCAResult:
        """
        Root Cause Analysis for campaign performance drops.
        
        Vault insight: Ask Claude to compare this week vs last week
        and identify what changed.
        """
    
    async def generate_weekly_report(
        self,
        account_id: str
    ) -> str:
        """
        Generate weekly performance report via Claude analysis.
        """
    
    async def get_ad_library_search(
        self,
        query: str,
        platform: str = "facebook"
    ) -> List[AdData]:
        """
        Search Meta Ad Library for ads matching query.
        """
```

**Usage in marketic:**
```bash
# Competitor intelligence in 4 minutes
marketic competitor intel --brand notion --days 90 --mcp gomarble

# RCA on performance drop
marketic perf rca --campaign-id abc123 --mcp gomarble

# Generate client report
marketic report weekly --account-id xyz --mcp gomarble
```

### 3.2 Composio MCP — Cross-Platform Ad Management

**Vault source:** "Marketing Skills v1.4.0 with Composio for HubSpot, Salesforce, Meta Ads, LinkedIn"

```python
class ComposioMCP:
    """
    Composio MCP integration for multi-platform ad + CRM management.
    
    Vault capabilities:
    - Meta Ads: Create campaigns, ads, manage budgets
    - LinkedIn Ads: Lead gen forms, matched audiences
    - Google Ads: Campaign management, bidding
    - HubSpot: CRM sync, lead management
    - Salesforce: CRM sync, opportunity tracking
    """
    
    # Meta Ads
    async def meta_create_campaign(
        self,
        name: str,
        objective: str,
        budget: float,
        targeting: dict
    ) -> str:  # campaign_id
    
    async def meta_create_ad_set(
        self,
        campaign_id: str,
        name: str,
        daily_budget: float,
        audience: dict
    ) -> str:
    
    async def meta_create_ad(
        self,
        ad_set_id: str,
        creative: dict,
        placement: str
    ) -> str:
    
    async def meta_get_insights(
        self,
        campaign_ids: List[str],
        date_range: str
    ) -> pd.DataFrame:
    
    # LinkedIn Ads
    async def linkedin_create_campaign(
        self,
        name: str,
        objective: str,
        budget: float
    ) -> str:
    
    async def linkedin_get_lead_forms(
        self,
        campaign_id: str
    ) -> List[LeadFormData]:
    
    async def linkedin_sync_to_hubspot(
        self,
        leads: List[LeadData]
    ) -> bool:
    
    # Google Ads
    async def google_create_campaign(
        self,
        name: str,
        campaign_type: str,  # SEARCH, DISPLAY, PMax
        budget: float,
        bidding_strategy: str
    ) -> str:
    
    async def google_create_ad_group(
        self,
        campaign_id: str,
        keywords: List[str]
    ) -> str:
```

### 3.3 Goose Ads MCP — Meta Creative Intelligence

**Vault source:** "Goose Ads MCP finds trending ads, competitor analysis, mines converting angles, runs inside Claude"

```python
class GooseAdsMCP:
    """
    Goose Ads MCP for Meta creative intelligence.
    
    Vault capabilities:
    - Find trending ads in any niche
    - Competitor analysis
    - Mining converting angles
    - Ad creation
    """
    
    async def find_trending_ads(
        self,
        niche: str,
        limit: int = 20
    ) -> List[TrendingAd]:
        """
        Find currently running, high-performing ads in a niche.
        """
    
    async def analyze_competitor(
        self,
        competitor_page: str
    ) -> CompetitorAnalysis:
        """
        Analyze what a competitor is advertising.
        """
    
    async def mine_converting_angles(
        self,
        product_url: str
    ) -> List[ConvertingAngle]:
        """
        Extract the emotional/functional triggers that convert.
        """
    
    async def generate_ad_variants(
        self,
        angle: ConvertingAngle,
        count: int = 10
    ) -> List[AdVariant]:
        """
        Generate N ad variants based on winning angle.
        """
```

### 3.4 Apify MCP — Data Collection

**Vault source:** "Apify MCP for AI agents - chat with TikTok/Instagram data in Claude Desktop"

```python
class ApifyMCP:
    """
    Apify MCP for web scraping and data collection.
    
    Vault capabilities:
    - 1000+ pre-built scrapers
    - TikTok data (profiles, videos, comments)
    - Instagram data
    - Twitter/X data
    - E-commerce product data
    - Competitor pricing
    """
    
    # Pre-built actors
    async def scrape_tiktok_profile(
        self,
        username: str
    ) -> TikTokProfile:
        """Scrape TikTok profile data"""
    
    async def scrape_instagram_profile(
        self,
        username: str
    ) -> InstagramProfile:
        """Scrape Instagram profile data"""
    
    async def scrape_competitor_pricing(
        self,
        url: str
    ) -> List[PricingData]:
        """Scrape competitor pricing pages"""
    
    async def scrape_product_data(
        self,
        url: str
    ) -> ProductData:
        """Scrape product data from e-commerce"""
    
    # Custom actor runner
    async def run_actor(
        self,
        actor_id: str,
        input_data: dict
    ) -> Any:
        """Run any Apify actor with custom input"""
    
    # Search
    async def google_search(
        self,
        query: str,
        num_results: int = 10
    ) -> List[SearchResult]:
        """Google search via Apify"""
```

### 3.5 Revid AI MCP — TikTok Video Automation

**Vault source:** "Revid_ai MCP creates, schedules, publishes TikTok videos via AI agent prompts"

```python
class RevidMCP:
    """
    Revid AI MCP for TikTok video creation and publishing.
    
    Vault capabilities:
    - Create TikTok videos from prompts
    - Schedule videos for optimal times
    - Publish automatically
    - Track performance
    """
    
    async def create_video(
        self,
        prompt: str,
        style: str = "UGC",  # UGC, tutorial, review, etc.
        duration: int = 30,   # seconds
        hooks: List[str] = None
    ) -> str:  # video_id
    
    async def create_batch(
        self,
        prompts: List[str],
        count: int = 10
    ) -> List[str]:  # video_ids
    
    async def schedule_video(
        self,
        video_id: str,
        publish_time: datetime,
        caption: str,
        hashtags: List[str]
    ) -> bool:
    
    async def publish_video(
        self,
        video_id: str,
        caption: str,
        hashtags: List[str]
    ) -> str:  # tiktok_post_url
    
    async def get_video_analytics(
        self,
        video_id: str
    ) -> VideoAnalytics:
        """Get views, likes, comments, shares"""
```

### 3.6 Higgsfield MCP — Google Ads Creative Generation

**Vault source:** "Higgsfield MCP - Generate all Google Ads creatives inside Claude"

```python
class HiggsfieldMCP:
    """
    Higgsfield MCP for Google Ads creative generation.
    
    Vault capabilities:
    - Generate Google Search ad copy
    - Generate Display ad creatives
    - Generate responsive search ads
    - Generate video ads
    """
    
    async def generate_search_ads(
        self,
        product_name: str,
        key_benefits: List[str],
        cta: str,
        count: int = 5
    ) -> List[SearchAd]:
        """Generate Google Search ad variants"""
    
    async def generate_display_ads(
        self,
        brand_kit: BrandKit,  # logo, colors, fonts
        templates: List[str],
        count: int = 10
    ) -> List[DisplayAd]:
        """Generate Display ad creatives"""
    
    async def generate_rsa(
        self,
        headlines: List[str],
        descriptions: List[str]
    ) -> str:  # RSA ID for Google Ads API
        """Create Responsive Search Ad"""
```

### 3.7 n8n MCP — Workflow Automation

**Vault source:** "n8n MCP - Claude gets deep knowledge of all 525+ n8n nodes"

```python
class N8nMCP:
    """
    n8n MCP for workflow automation.
    
    Vault capabilities:
    - Knows all 525+ n8n nodes natively
    - Create workflows from prompts
    - Trigger workflows
    - Self-hostable (free on Oracle Cloud)
    
    Key marketing nodes:
    - HTTP Request
    - Slack/Teams
    - Google Sheets
    - Airtable
    - Facebook
    - LinkedIn
    - Twitter/X
    - HubSpot
    - Salesforce
    - Gmail
    - And 515 more
    """
    
    async def create_workflow(
        self,
        prompt: str,
        nodes: List[str] = None  # Optional constraint to specific nodes
    ) -> Workflow:
        """
        Create n8n workflow from natural language prompt.
        Claude knows the API/schemas of all 525+ nodes.
        """
    
    async def trigger_workflow(
        self,
        workflow_id: str,
        payload: dict
    ) -> WorkflowResult:
    
    async def search_nodes(
        self,
        capability: str
    ) -> List[Node]:
        """
        Find nodes that do X.
        E.g., "find nodes that send Slack messages with attachments"
        """
```

---

## 4. Agent Architecture

```
marketic/
├── agents/                          # NEW - Autonomous agents
│   ├── __init__.py
│   │
│   ├── ad_creative_agent.py         # Generate + optimize ad creatives
│   ├── competitor_research_agent.py # Full competitor intelligence
│   ├── campaign_optimizer_agent.py  # ROAS/bid optimization
│   ├── content_pipeline_agent.py    # End-to-end content workflow
│   ├── reporting_agent.py           # Weekly/monthly reports
│   └── multi_platform_agent.py     # Orchestrate all platforms
│
├── agent_templates/                 # Prompt templates for agents
│   ├── creative_agent.yaml
│   ├── competitor_agent.yaml
│   ├── optimizer_agent.yaml
│   └── reporter_agent.yaml
```

### 4.1 Ad Creative Agent

```python
class AdCreativeAgent:
    """
    Autonomous agent for ad creative generation and optimization.
    
    Vault reference: Goose Ads + Nano Banana + Arcads workflow
    
    Inputs:
    - Competitor analysis (from GoMarble/competitor_research)
    - Brand guidelines (colors, fonts, tone)
    - Product info (URL, benefits, CTA)
    
    Outputs:
    - 100s of ad variants (images + copy)
    - Ranked by expected performance
    - Tagged with emotional triggers, audience segments
    """
    
    async def run(self, brief: CreativeBrief) -> List[CreativeVariant]:
        """
        Full creative pipeline:
        1. Mine competitor converting angles (Goose Ads)
        2. Generate copy variants (qwen3:4b locally)
        3. Generate image ads (Nano Banana via n8n)
        4. Generate video scripts (Arcads)
        5. Rank by gap exploitation score
        6. Return top N with reasoning
        """
```

### 4.2 Competitor Research Agent

```python
class CompetitorResearchAgent:
    """
    Full competitor intelligence agent.
    
    Vault reference: GoMarble + Meta Ad Library + Apify + Goose Ads
    
    Inputs:
    - Competitor brand/URL
    - Platforms to analyze (Meta, Google, TikTok, LinkedIn)
    - Time range (30d, 90d, 180d)
    
    Outputs:
    - Positioning map
    - Emotional trigger analysis
    - Audience overlap analysis
    - Gap opportunities
    - Counter-strategy recommendations
    """
    
    async def run(self, competitor: str) -> CompetitorIntelReport:
        """
        1. Get ads via GoMarble (Meta Ad Library)
        2. Scrape landing pages via Apify
        3. Analyze with Claude (parallel LLM)
        4. Identify gaps
        5. Generate counter-positioning
        6. Output: structured report + ad variants
        """
```

### 4.3 Campaign Optimizer Agent

```python
class CampaignOptimizerAgent:
    """
    Autonomous ROAS optimization agent.
    
    Vault reference: Lexi dashboard, GoMarble RCA
    
    Inputs:
    - Campaign IDs
    - Target ROAS/CPA
    - Constraints (budget floors/ceilings)
    
    Outputs:
    - Bid adjustments
    - Budget reallocations
    - Creative rotation decisions
    - Pause/scale recommendations
    """
    
    async def run(self, optimization_request: OptimizationRequest):
        """
        1. Fetch current performance (Composio Meta/Google API)
        2. Calculate ROAS per ad set/campaign
        3. Compare to targets
        4. Identify underperformers
        5. Run RCA (GoMarble)
        6. Generate optimization actions
        7. Apply (with human approval) or auto-apply
        """
```

---

## 5. Complete CLI Interface

```bash
# MCP Management
marketic mcp list                           # List all available MCPs
marketic mcp enable gomarble                 # Enable GoMarble MCP
marketic mcp status                          # Show enabled MCPs and health

# Competitor Intelligence (uses GoMarble + Goose Ads + Apify)
marketic competitor analyze --brand notion --days 90 --mcp all
marketic competitor ads --brand hubspot --platform meta
marketic competitor pricing --competitors notion,asana,trello

# Ad Creative Generation (uses Goose Ads + Nano Banana + Arcads)
marketic creative generate --product-url https://notion.so --count 100 --platforms meta,google,tiktok
marketic creative scripts --angle "project management for remote teams" --count 50
marketic creative images --brand-kit ./brand.json --count 200

# Campaign Management (uses Composio Meta/Google/LinkedIn)
marketic campaign create --name "Q1 Launch" --platforms meta,google --budget 50000
marketic campaign launch --campaign-id abc123 --ad-sets 5 --daily-budget 500
marketic campaign pause --campaign-id abc123 --reason "CPA above threshold"

# Performance Optimization (uses GoMarble RCA + Composio)
marketic perf status --platforms google,meta --date-range 7d
marketic perf rca --campaign-id abc123 --mcp gomarble
marketic perf optimize-roas --campaign-id abc123 --target-roas 3.0 --auto-approve false
marketic perf budget-route --strategy roas --lookback 7d --min-roas 2.0

# Funnel Analysis (uses n8n + GA)
marketic funnel analyze --funnel-type DTC --products product_1,product_2
marketic funnel optimize --current '{"TOF": 30, "MOF": 40, "BOF": 30}' --target roas 3.5

# Attribution (uses Composio + GA MCP)
marketic attr report --model linear --date-range 30d --channels google,meta,linkedin
marketic attr incrementality design --campaign-id abc123
marketic attr incrementality results --test-id test_456

# Video Ads (uses Revid + ElevenLabs)
marketic video generate --competitor notion --count 100 --platform tiktok
marketic video schedule --videos video_1,video_2 --times "10:00,14:00,18:00"
marketic video publish --video-id vid_123

# Reporting
marketic report weekly --account-id abc123 --format markdown
marketic report client --client-name "Acme Corp" --email email@example.com
marketic report rca --campaign-id abc123 --issue "CPA increased 40%"

# Workflows (uses n8n MCP)
marketic workflow create --prompt "When competitor launches new ad, alert Slack and generate counter-variants"
marketic workflow run --workflow-id wf_123 --input '{"brand": "notion"}'
```

---

## 6. Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MARKETIC OS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    MCP LAYER (11 MCPs)                           │  │
│  ├─────────────┬─────────────┬─────────────┬──────────────────────┤  │
│  │  GoMarble   │  Composio   │  Goose Ads │  Apify               │  │
│  │  Meta/Google│  Meta/LI/HS │  Meta      │  TikTok/IG/Twitter   │  │
│  ├─────────────┼─────────────┼─────────────┼──────────────────────┤  │
│  │  Revid_ai  │  Higgsfield │  Firecrawl │  Browser MCP          │  │
│  │  TikTok    │  Google Ads │  Web crawl │  30+ web tools       │  │
│  ├─────────────┼─────────────┼─────────────┼──────────────────────┤  │
│  │  n8n MCP   │  GA MCP     │            │                      │  │
│  │  525+ nodes│  Analytics  │            │                      │  │
│  └─────────────┴─────────────┴─────────────┴──────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    AGENT LAYER (6 Agents)                       │  │
│  ├───────────────┬───────────────┬───────────────┬─────────────────┤  │
│  │Ad Creative    │Competitor     │Campaign       │Content          │  │
│  │Agent         │Research Agent │Optimizer Agent│Pipeline Agent   │  │
│  ├───────────────┼───────────────┼───────────────┼─────────────────┤  │
│  │Reporting     │Multi-Platform │              │                 │  │
│  │Agent        │Agent          │              │                 │  │
│  └───────────────┴───────────────┴───────────────┴─────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                   CORE MODULES (8 modules)                      │  │
│  ├──────────┬──────────┬──────────┬──────────┬───────────────────┤  │
│  │ signals/ │competitive│creative/ │campaign/ │ analytics/        │  │
│  │          │/         │          │          │                   │  │
│  ├──────────┼──────────┼──────────┼──────────┼───────────────────┤  │
│  │performance│video_ads │ ecommerce│ tracking │ guardrails/       │  │
│  │          │          │          │          │                   │  │
│  └──────────┴──────────┴──────────┴──────────┴───────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    FOUNDATION LAYER                             │  │
│  │  LLM Router (a3m) │ Memory (DuckDB) │ Orchestration │ Alerts    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Build Sequence (Updated)

### Phase 1: MCP Foundation (Weeks 1-2)
- [ ] `mcp/client.py` — Unified MCP client wrapper
- [ ] `mcp/registry.py` — MCP server registry
- [ ] Enable 3 MCPS first: GoMarble, Composio, Apify

### Phase 2: Core Integrations (Weeks 3-4)
- [ ] `mcp/servers/gomarble.py` — GoMarble integration
- [ ] `mcp/servers/composio.py` — Composio integration
- [ ] `mcp/servers/apify.py` — Apify integration
- [ ] `mcp/servers/goose_ads.py` — Goose Ads integration

### Phase 3: Agents (Weeks 5-6)
- [ ] `agents/competitor_research_agent.py`
- [ ] `agents/ad_creative_agent.py`
- [ ] `agents/campaign_optimizer_agent.py`

### Phase 4: Performance Loop (Weeks 7-8)
- [ ] `performance/roas_tracker.py`
- [ ] `performance/bid_optimizer.py`
- [ ] `performance/budget_router.py`

### Phase 5: Video + TikTok (Weeks 9-10)
- [ ] `mcp/servers/revid.py`
- [ ] `video_ads/` module

### Phase 6: Full Stack (Weeks 11-12)
- [ ] `agents/multi_platform_agent.py`
- [ ] `agents/reporting_agent.py`
- [ ] CLI polish + demo video

---

## 8. MCP Quick Reference

| MCP | Install | Auth | Primary Use |
|-----|---------|------|-------------|
| **GoMarble** | `npx @gomarble/mcp` | API key | Meta/Google Ads + RCA |
| **Composio** | `npx @composio/mcp` | OAuth | Multi-platform launch |
| **Goose Ads** | Built into Claude | API key | Meta creative intel |
| **Apify** | `npx @apify/mcp` | API key | Web scraping |
| **Revid** | `npx @revid/mcp` | API key | TikTok video |
| **Higgsfield** | `npx @higgsfield/mcp` | API key | Google Ads creatives |
| **Firecrawl** | `npx @firecrawl/mcp` | API key | AI-ready web scraping |
| **n8n** | Self-hosted | Self-hosted | Workflow automation |
| **Browser MCP** | `npx @browseruse/mcp` | None | Web access |
| **GA MCP** | Custom | OAuth | Analytics queries |
