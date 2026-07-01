"""
Marketic Alerts Layer

Multi-channel alerting (WhatsApp, Telegram, Email, Slack).
Based on omniclaw's notification capabilities.
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AlertChannel(Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"


@dataclass
class Alert:
    title: str
    message: str
    priority: AlertPriority
    channels: List[AlertChannel]
    metadata: Dict = None


@dataclass
class AlertResult:
    channel: str
    status: str  # sent, failed
    message_id: str = ""
    error: str = ""


class AlertLayer:
    """
    Multi-channel alerting system.
    
    Sends notifications via WhatsApp, Telegram, Email, Slack, SMS.
    
    Usage:
        alerts = AlertLayer()
        
        # Send alert
        results = await alerts.send(
            title="Campaign Alert",
            message="CPA increased by 25%",
            priority=AlertPriority.HIGH,
            channels=[AlertChannel.WHATSAPP, AlertChannel.SLACK]
        )
    """
    
    def __init__(self):
        self.sent_alerts = []
    
    async def send(
        self,
        title: str,
        message: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
        channels: List[AlertChannel] = None,
        metadata: Dict = None,
    ) -> List[AlertResult]:
        """Send alert to specified channels."""
        
        if channels is None:
            channels = [AlertChannel.EMAIL]
        
        alert = Alert(
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            metadata=metadata,
        )
        
        # Send to all channels in parallel
        tasks = []
        for channel in channels:
            tasks.append(self._send_to_channel(alert, channel))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        alert_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                alert_results.append(AlertResult(
                    channel=channels[i].value,
                    status="failed",
                    error=str(result),
                ))
            else:
                alert_results.append(result)
        
        self.sent_alerts.append(alert)
        return alert_results
    
    async def _send_to_channel(
        self,
        alert: Alert,
        channel: AlertChannel,
    ) -> AlertResult:
        """Send to a specific channel."""
        
        # Simulated sending
        await asyncio.sleep(0.05)
        
        # In production:
        # - WhatsApp: WhatsApp Business API
        # - Telegram: Bot API
        # - Email: SendGrid, AWS SES
        # - Slack: Slack webhooks
        # - SMS: Twilio
        
        return AlertResult(
            channel=channel.value,
            status="sent",
            message_id=f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
    
    async def send_campaign_alerts(
        self,
        campaign_name: str,
        metrics: Dict,
        thresholds: Dict,
    ) -> List[AlertResult]:
        """Send campaign-specific alerts based on thresholds."""
        
        results = []
        
        # Check CPA threshold
        if "cpa" in metrics and "cpa_threshold" in thresholds:
            if metrics["cpa"] > thresholds["cpa_threshold"]:
                result = await self.send(
                    title=f"⚠️ CPA Alert: {campaign_name}",
                    message=f"CPA is ${metrics['cpa']:.2f}, above threshold of ${thresholds['cpa_threshold']:.2f}",
                    priority=AlertPriority.HIGH,
                    channels=[AlertChannel.WHATSAPP, AlertChannel.SLACK],
                )
                results.extend(result)
        
        # Check ROAS threshold
        if "roas" in metrics and "roas_threshold" in thresholds:
            if metrics["roas"] < thresholds["roas_threshold"]:
                result = await self.send(
                    title=f"⚠️ ROAS Alert: {campaign_name}",
                    message=f"ROAS is {metrics['roas']:.2f}x, below threshold of {thresholds['roas_threshold']:.2f}x",
                    priority=AlertPriority.HIGH,
                    channels=[AlertChannel.WHATSAPP, AlertChannel.SLACK],
                )
                results.extend(result)
        
        # Check budget threshold
        if "spend" in metrics and "budget" in metrics and "budget_threshold" in thresholds:
            budget_pct = (metrics["spend"] / metrics["budget"]) * 100
            if budget_pct > thresholds["budget_threshold"]:
                result = await self.send(
                    title=f"💰 Budget Alert: {campaign_name}",
                    message=f"Budget {budget_pct:.0f}% spent (${metrics['spend']:.0f} of ${metrics['budget']:.0f})",
                    priority=AlertPriority.MEDIUM,
                    channels=[AlertChannel.EMAIL],
                )
                results.extend(result)
        
        return results
    
    async def send_daily_digest(
        self,
        daily_metrics: Dict,
        top_performers: List[Dict],
        issues: List[str],
    ) -> List[AlertResult]:
        """Send daily performance digest."""
        
        message = f"""📊 Daily Marketing Digest

💰 Today's Performance:
- Spend: ${daily_metrics.get('spend', 0):,.0f}
- Revenue: ${daily_metrics.get('revenue', 0):,.0f}
- ROAS: {daily_metrics.get('roas', 0):.2f}x
- Conversions: {daily_metrics.get('conversions', 0):,}

🏆 Top Performers:
"""
        
        for perf in top_performers[:3]:
            message += f"- {perf['name']}: {perf['metric']}\n"
        
        if issues:
            message += "\n⚠️ Issues:\n"
            for issue in issues[:3]:
                message += f"- {issue}\n"
        
        return await self.send(
            title="📊 Daily Marketing Digest",
            message=message,
            priority=AlertPriority.MEDIUM,
            channels=[AlertChannel.WHATSAPP],
        )


async def demo():
    """Demo alerting."""
    print("=" * 60)
    print("MARKETIC ALERTS LAYER DEMO")
    print("=" * 60)
    
    alerts = AlertLayer()
    
    # Send a simple alert
    print("\n📨 Sending Alert...")
    results = await alerts.send(
        title="Test Alert",
        message="This is a test marketing alert",
        priority=AlertPriority.LOW,
        channels=[AlertChannel.WHATSAPP, AlertChannel.EMAIL],
    )
    
    for result in results:
        icon = "✅" if result.status == "sent" else "❌"
        print(f"  {icon} {result.channel}: {result.status}")
    
    # Campaign alert
    print("\n\n🚨 Sending Campaign Alert...")
    campaign_alerts = await alerts.send_campaign_alerts(
        campaign_name="Q3 Product Launch",
        metrics={
            "cpa": 89.50,
            "roas": 1.8,
            "spend": 45000,
            "budget": 75000,
        },
        thresholds={
            "cpa_threshold": 75,
            "roas_threshold": 2.5,
            "budget_threshold": 50,
        },
    )
    
    for result in campaign_alerts:
        icon = "✅" if result.status == "sent" else "❌"
        print(f"  {icon} {result.channel}: {result.status}")
    
    return results, campaign_alerts


if __name__ == "__main__":
    asyncio.run(demo())
