"""
Report Collector — Pull data from analytics platforms for daily briefings.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import httpx


@dataclass
class DailyMetrics:
    date: str
    traffic: int
    conversions: int
    revenue: float
    ad_spend: float
    social_engagement: int
    email_opens: int
    email_clicks: int


@dataclass
class CampaignPerformance:
    campaign_name: str
    platform: str
    spend: float
    revenue: float
    roas: float
    impressions: int
    clicks: int
    conversions: int


class ReportCollector:
    """Collect marketing metrics from various platforms."""
    
    def __init__(self):
        self._clients: Dict[str, httpx.Client] = {}
    
    def connect_google_analytics(self, property_id: str, credentials_json: str = None) -> Dict:
        """
        Connect to Google Analytics Data API.
        property_id: GA4 property ID (e.g., "properties/123456789")
        credentials: path to service account JSON or None for measurement protocol
        """
        # For now, use simple simulation - in production would use Google Analytics Data API
        self._clients["ga"] = {"property_id": property_id}
        return {"connected": True, "property_id": property_id}
    
    def connect_meta_ads(self, access_token: str, ad_account_id: str) -> Dict:
        """Connect to Meta Marketing API."""
        try:
            client = httpx.Client(
                base_url="https://graph.facebook.com/v19.0",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30.0
            )
            
            # Test connection
            response = client.get(f"/act_{ad_account_id}")
            if response.status_code == 200:
                self._clients["meta"] = {"client": client, "ad_account_id": ad_account_id}
                return {"connected": True, "ad_account_id": ad_account_id}
            else:
                return {"connected": False, "error": f"Connection failed: {response.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def collect_daily_metrics(self, date: str = None) -> DailyMetrics:
        """
        Collect daily metrics from all connected platforms.
        Returns aggregated metrics.
        """
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Collect from each platform
        metrics = {
            "date": date,
            "traffic": 0,
            "conversions": 0,
            "revenue": 0.0,
            "ad_spend": 0.0,
            "social_engagement": 0,
            "email_opens": 0,
            "email_clicks": 0
        }
        
        # Google Analytics
        if "ga" in self._clients:
            ga_metrics = self._collect_ga_metrics(date)
            for k, v in ga_metrics.items():
                if k in metrics:
                    metrics[k] += v
        
        # Meta Ads
        if "meta" in self._clients:
            meta_metrics = self._collect_meta_metrics(date)
            metrics["ad_spend"] += meta_metrics.get("spend", 0)
            metrics["revenue"] += meta_metrics.get("revenue", 0)
        
        return DailyMetrics(**metrics)
    
    def _collect_ga_metrics(self, date: str) -> Dict[str, Any]:
        """Collect from Google Analytics (simulated)."""
        # In production, use Google Analytics Data API
        # For now, return simulated data
        return {
            "traffic": 1250,
            "conversions": 32,
            "social_engagement": 245
        }
    
    def _collect_meta_metrics(self, date: str) -> Dict[str, Any]:
        """Collect from Meta Ads."""
        client_config = self._clients["meta"]
        client = client_config["client"]
        ad_account_id = client_config["ad_account_id"]
        
        try:
            # Get ad insights for date
            params = {
                "fields": "spend,impressions,clicks,actions",
                "time_range": json.dumps({"since": date, "until": date}),
                "actions_breakdowns": "action_type"
            }
            
            response = client.get(f"/act_{ad_account_id}/insights", params=params)
            if response.status_code == 200:
                data = response.json()
                insights = data.get("data", [])
                if insights:
                    i = insights[0]
                    spend = float(i.get("spend", 0))
                    revenue = spend * 3.5  # Estimate ROAS
                    return {"spend": spend, "revenue": revenue}
        except Exception:
            pass
        
        return {"spend": 0.0, "revenue": 0.0}
    
    def compare_to_baseline(self, current_metrics: DailyMetrics, 
                           baseline_days: int = 30) -> Dict[str, Any]:
        """
        Compare current metrics to historical baseline.
        Returns percentage changes and anomaly flags.
        """
        # Simulated baseline
        baseline = {
            "traffic": 1100,
            "conversions": 28,
            "revenue": 3200.0,
            "ad_spend": 450.0,
            "social_engagement": 200
        }
        
        current = {
            "traffic": current_metrics.traffic,
            "conversions": current_metrics.conversions,
            "revenue": current_metrics.revenue,
            "ad_spend": current_metrics.ad_spend,
            "social_engagement": current_metrics.social_engagement
        }
        
        changes = {}
        for key in baseline:
            if baseline[key] > 0:
                change_pct = ((current[key] - baseline[key]) / baseline[key]) * 100
                changes[key] = {
                    "change_pct": round(change_pct, 1),
                    "is_anomaly": abs(change_pct) > 30,  # Flag if >30% change
                    "current": current[key],
                    "baseline": baseline[key]
                }
        
        return changes
    
    def get_campaign_performance(self, days: int = 7) -> List[CampaignPerformance]:
        """Get campaign performance across platforms."""
        campaigns = []
        
        # Simulated campaign data
        campaign_data = [
            {"name": "Brand Awareness", "platform": "meta", "spend": 150.0, "revenue": 520.0},
            {"name": "Product Launch", "platform": "google", "spend": 200.0, "revenue": 890.0},
            {"name": "Retargeting", "platform": "meta", "spend": 75.0, "revenue": 420.0},
        ]
        
        for c in campaign_data:
            roas = c["revenue"] / c["spend"] if c["spend"] > 0 else 0
            campaigns.append(CampaignPerformance(
                campaign_name=c["name"],
                platform=c["platform"],
                spend=c["spend"],
                revenue=c["revenue"],
                roas=round(roas, 2),
                impressions=5000,
                clicks=350,
                conversions=25
            ))
        
        return campaigns


# Add json import that was used above
import json
