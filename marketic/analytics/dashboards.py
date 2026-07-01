"""
Analytics Dashboards

Real-time performance dashboards and visualizations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


@dataclass
class MetricCard:
    """A single metric card for the dashboard."""
    name: str
    value: float
    previous_value: float = 0
    unit: str = ""
    format: str = "number"  # number, currency, percent, decimal
    change: float = 0  # percentage change
    trend: str = "up"  # up, down, neutral


class AnalyticsDashboard:
    """
    Generates marketing performance dashboards.
    
    Usage:
        dashboard = AnalyticsDashboard()
        cards = dashboard.get_campaign_dashboard(campaign_id="abc123")
    """
    
    def get_campaign_dashboard(self, campaign_data: Dict) -> List[MetricCard]:
        """Get dashboard metrics for a campaign."""
        cards = []
        
        # Spend
        spend = campaign_data.get("spend", 0)
        budget = campaign_data.get("budget", 1)
        spend_card = MetricCard(
            name="Spend",
            value=spend,
            previous_value=spend * 0.9,  # Simulated
            unit="$",
            format="currency",
            change=((spend - spend * 0.9) / (spend * 0.9)) * 100,
            trend="up",
        )
        cards.append(spend_card)
        
        # ROAS
        roas = campaign_data.get("roas", 0)
        cards.append(MetricCard(
            name="ROAS",
            value=roas,
            previous_value=roas * 0.95,
            format="decimal",
            change=((roas - roas * 0.95) / (roas * 0.95)) * 100,
            trend="up" if roas > campaign_data.get("target_roas", roas) else "down",
        ))
        
        # CPA
        cpa = campaign_data.get("cpa", 0)
        cards.append(MetricCard(
            name="CPA",
            value=cpa,
            previous_value=cpa * 1.1,
            unit="$",
            format="currency",
            change=-((cpa - cpa * 1.1) / (cpa * 1.1)) * 100,
            trend="down" if cpa < campaign_data.get("target_cpa", cpa) else "up",
        ))
        
        # Conversions
        conversions = campaign_data.get("conversions", 0)
        cards.append(MetricCard(
            name="Conversions",
            value=conversions,
            previous_value=conversions * 0.85,
            format="number",
            change=((conversions - conversions * 0.85) / (conversions * 0.85)) * 100,
            trend="up",
        ))
        
        return cards
    
    def get_channel_breakdown(self, channel_data: Dict) -> List[Dict]:
        """Get performance breakdown by channel."""
        breakdown = []
        
        for channel, data in channel_data.items():
            breakdown.append({
                "channel": channel,
                "spend": data.get("spend", 0),
                "impressions": data.get("impressions", 0),
                "clicks": data.get("clicks", 0),
                "conversions": data.get("conversions", 0),
                "revenue": data.get("revenue", 0),
                "roas": data.get("roas", 0),
                "cpa": data.get("cpa", 0),
                "ctr": data.get("clicks", 0) / max(data.get("impressions", 1), 1) * 100,
                "conversion_rate": data.get("conversions", 0) / max(data.get("clicks", 1), 1) * 100,
            })
        
        # Sort by revenue
        breakdown.sort(key=lambda x: x["revenue"], reverse=True)
        
        return breakdown
    
    def generate_market_mix_table(self, channel_data: Dict) -> str:
        """Generate a market mix table in markdown format."""
        
        breakdown = self.get_channel_breakdown(channel_data)
        
        # Calculate totals
        total_spend = sum(c["spend"] for c in breakdown)
        total_revenue = sum(c["revenue"] for c in breakdown)
        total_conversions = sum(c["conversions"] for c in breakdown)
        
        table = """
| Channel | Spend | % Spend | Revenue | ROAS | Conv | CPA |
|---------|-------|---------|---------|------|------|-----|
"""
        
        for c in breakdown:
            spend_pct = c["spend"] / total_spend * 100 if total_spend > 0 else 0
            table += f"| {c['channel']} | ${c['spend']:,.0f} | {spend_pct:.1f}% | ${c['revenue']:,.0f} | {c['roas']:.2f}x | {c['conversions']:,} | ${c['cpa']:.2f} |\n"
        
        table += f"| **TOTAL** | **${total_spend:,.0f}** | **100%** | **${total_revenue:,.0f}** | **{total_revenue/total_spend:.2f}x** | **{total_conversions:,}** | **${total_spend/total_conversions if total_conversions > 0 else 0:.2f}** |"
        
        return table
    
    def get_performance_trends(self, historical_data: List[Dict], days: int = 7) -> Dict:
        """Calculate performance trends over time."""
        
        if not historical_data:
            return {}
        
        # Sort by date
        sorted_data = sorted(historical_data, key=lambda x: x.get("date", ""))
        
        # Get recent and previous periods
        recent = sorted_data[-days:] if len(sorted_data) >= days else sorted_data
        previous = sorted_data[-days*2:-days] if len(sorted_data) >= days*2 else sorted_data[:days]
        
        def aggregate(data):
            return {
                "spend": sum(d.get("spend", 0) for d in data),
                "revenue": sum(d.get("revenue", 0) for d in data),
                "conversions": sum(d.get("conversions", 0) for d in data),
            }
        
        recent_agg = aggregate(recent)
        previous_agg = aggregate(previous)
        
        # Calculate changes
        def change(curr, prev):
            if prev == 0:
                return 0
            return ((curr - prev) / prev) * 100
        
        return {
            "period": f"{days} days",
            "recent": recent_agg,
            "previous": previous_agg,
            "changes": {
                "spend_change": change(recent_agg["spend"], previous_agg["spend"]),
                "revenue_change": change(recent_agg["revenue"], previous_agg["revenue"]),
                "conversion_change": change(recent_agg["conversions"], previous_agg["conversions"]),
            }
        }


def demo():
    """Demo the analytics dashboard."""
    print("=" * 60)
    print("MARKETIC ANALYTICS DASHBOARD DEMO")
    print("=" * 60)
    
    dashboard = AnalyticsDashboard()
    
    # Sample campaign data
    campaign_data = {
        "campaign_id": "demo_001",
        "name": "Q3 Product Launch",
        "spend": 45678,
        "budget": 75000,
        "roas": 2.84,
        "cpa": 67.23,
        "conversions": 680,
        "impressions": 2500000,
        "clicks": 45000,
        "target_roas": 2.5,
        "target_cpa": 75,
    }
    
    print("\n📊 Campaign Dashboard:")
    cards = dashboard.get_campaign_dashboard(campaign_data)
    for card in cards:
        change_str = f"+{card.change:.1f}%" if card.change >= 0 else f"{card.change:.1f}%"
        trend_icon = "📈" if card.trend == "up" else "📉"
        print(f"  {card.name}: {card.value:.2f} {card.unit} ({change_str}) {trend_icon}")
    
    # Channel breakdown
    print("\n\n📋 Channel Breakdown:")
    channel_data = {
        "google_search": {"spend": 20000, "revenue": 65000, "conversions": 320, "impressions": 800000, "clicks": 18000, "cpa": 62.50, "roas": 3.25},
        "meta_feed": {"spend": 18000, "revenue": 42000, "conversions": 240, "impressions": 1200000, "clicks": 20000, "cpa": 75.00, "roas": 2.33},
        "linkedin": {"spend": 7000, "revenue": 12000, "conversions": 85, "impressions": 350000, "clicks": 5000, "cpa": 82.35, "roas": 1.71},
        "youtube": {"spend": 678, "revenue": 1800, "conversions": 35, "impressions": 150000, "clicks": 2000, "cpa": 19.37, "roas": 2.65},
    }
    
    breakdown = dashboard.get_channel_breakdown(channel_data)
    for ch in breakdown:
        print(f"  {ch['channel']}: ${ch['revenue']:,} revenue, {ch['roas']:.2f}x ROAS, {ch['conversions']} conv")
    
    # Market mix table
    print("\n\n📊 Market Mix Table:")
    print(dashboard.generate_market_mix_table(channel_data))
    
    return dashboard


if __name__ == "__main__":
    demo()
