"""
Insight Generator — Generate plain-English insights from marketing data.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class Insight:
    type: str  # opportunity, threat, anomaly, trend, win, concern
    text: str
    recommendation: str
    priority: str  # high, medium, low
    metric: Optional[str] = None
    change_pct: Optional[float] = None


@dataclass
class Briefing:
    date: str
    summary: str
    metrics: Dict[str, Any]
    insights: List[Insight]
    recommendations: List[str]


class InsightGenerator:
    """Generate actionable insights from marketing metrics."""
    
    def __init__(self):
        self._openai = None
        if OPENAI_AVAILABLE:
            self._openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def generate_insights(self, metrics: Dict[str, Any], 
                        changes: Dict[str, Any],
                        campaigns: List[Any]) -> List[Insight]:
        """Generate insights from metrics and changes."""
        insights = []
        
        # Analyze traffic
        if "traffic" in changes:
            change = changes["traffic"]
            if change["change_pct"] > 20:
                insights.append(Insight(
                    type="win",
                    text=f"Traffic up {change['change_pct']:.0f}% vs baseline ({change['current']} visits)",
                    recommendation="Consider increasing ad spend to capitalize on momentum",
                    priority="high" if change["change_pct"] > 30 else "medium",
                    metric="traffic",
                    change_pct=change["change_pct"]
                ))
            elif change["change_pct"] < -20:
                insights.append(Insight(
                    type="concern",
                    text=f"Traffic down {abs(change['change_pct']):.0f}% vs baseline ({change['current']} visits)",
                    recommendation="Review recent changes to site or marketing channels",
                    priority="high" if change["change_pct"] < -30 else "medium",
                    metric="traffic",
                    change_pct=change["change_pct"]
                ))
        
        # Analyze revenue
        if "revenue" in changes:
            change = changes["revenue"]
            if change["change_pct"] > 15:
                insights.append(Insight(
                    type="win",
                    text=f"Revenue up {change['change_pct']:.0f}% vs baseline (${change['current']:.0f})",
                    recommendation="Identify top-performing campaigns and reallocate budget",
                    priority="high",
                    metric="revenue",
                    change_pct=change["change_pct"]
                ))
        
        # Analyze ROAS from campaigns
        for campaign in campaigns:
            if campaign.roas < 1.0:
                insights.append(Insight(
                    type="concern",
                    text=f"Campaign '{campaign.campaign_name}' has ROAS of {campaign.roas} (below 1.0)",
                    recommendation=f"Reduce budget or pause {campaign.platform} campaign",
                    priority="high",
                    metric=f"{campaign.platform}_roas"
                ))
            elif campaign.roas > 4.0:
                insights.append(Insight(
                    type="opportunity",
                    text=f"Campaign '{campaign.campaign_name}' ROAS of {campaign.roas} is excellent",
                    recommendation=f"Scale {campaign.platform} campaign by 20-30%",
                    priority="medium"
                ))
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda x: priority_order.get(x.priority, 2))
        
        return insights
    
    def generate_performance_narrative(self, metrics: Dict[str, Any],
                                      insights: List[Insight]) -> str:
        """
        Generate a plain-English narrative summary.
        Uses GPT if available, else template-based.
        """
        # Find top insights
        high_priority = [i for i in insights if i.priority == "high"]
        
        if high_priority and self._openai:
            prompt = f"""Write a 2-sentence summary of this marketing performance:

Key insight: {high_priority[0].text}
Total visits: {metrics.get('traffic', 'N/A')}
Revenue: ${metrics.get('revenue', 0):.0f}

Return ONLY the summary, no quotes."""
            
            try:
                response = self._openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass
        
        # Fallback template
        traffic = metrics.get("traffic", 0)
        revenue = metrics.get("revenue", 0)
        
        summary = f"Yesterday you received {traffic:,} visits and generated ${revenue:,.0f} in revenue. "
        
        if high_priority:
            summary += f"Key highlight: {high_priority[0].text.lower()}."
        
        return summary
    
    def generate_recommendations(self, insights: List[Insight]) -> List[str]:
        """Generate actionable recommendations from insights."""
        recommendations = []
        
        for insight in insights[:5]:  # Top 5
            if insight.recommendation:
                recommendations.append(f"- {insight.recommendation}")
        
        return recommendations
    
    def generate_full_briefing(self, metrics: Dict[str, Any],
                               changes: Dict[str, Any],
                               campaigns: List[Any],
                               date: str = None) -> Briefing:
        """Generate complete daily briefing."""
        if date is None:
            from datetime import datetime
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        insights = self.generate_insights(metrics, changes, campaigns)
        summary = self.generate_performance_narrative(metrics, insights)
        recommendations = self.generate_recommendations(insights)
        
        return Briefing(
            date=date,
            summary=summary,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations
        )
