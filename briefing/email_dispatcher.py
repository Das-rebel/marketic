"""
Email Dispatcher — Send daily briefings via email.
"""

import os
from typing import Dict, Optional, List

import httpx


class EmailDispatcher:
    """Send briefing emails via SendGrid, Mailchimp, or SMTP."""
    
    def __init__(self):
        self._sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        self._from_email = os.environ.get("BRIEFING_FROM_EMAIL", "noreply@quay.ai")
    
    def format_briefing_email(self, briefing, brand_name: str = "Your Brand") -> Dict[str, str]:
        """Format briefing as HTML email."""
        from datetime import datetime
        
        # Build insights HTML
        insights_html = ""
        for insight in briefing.insights[:5]:
            priority_color = {
                "high": "#dc3545",
                "medium": "#ffc107", 
                "low": "#28a745"
            }.get(insight.priority, "#6c757d")
            
            insights_html += f"""
            <div style="margin-bottom: 16px; padding: 12px; border-left: 4px solid {priority_color};">
                <strong style="color: {priority_color};">{insight.type.upper()}</strong>
                <p style="margin: 8px 0 0 0;">{insight.text}</p>
                <p style="margin: 4px 0 0 0; color: #666; font-size: 14px;">
                    <em>Recommended action:</em> {insight.recommendation}
                </p>
            </div>
            """
        
        # Build recommendations HTML
        recs_html = ""
        for rec in briefing.recommendations:
            recs_html += f"<li>{rec}</li>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 24px;">
                    ☀️ Good morning from Quay
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0;">
                    {briefing.date} • Your AI Marketing Briefing
                </p>
            </div>
            
            <div style="background: #f8f9fa; padding: 24px; border-radius: 0 0 12px 12px;">
                
                <h2 style="margin-top: 0; color: #1a1a2e;">📊 Performance Summary</h2>
                <p style="font-size: 16px; line-height: 1.6;">{briefing.summary}</p>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 20px 0;">
                    <div style="background: white; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #667eea;">{briefing.metrics.get('traffic', 0):,}</div>
                        <div style="font-size: 12px; color: #666;">Visits</div>
                    </div>
                    <div style="background: white; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #28a745;">${briefing.metrics.get('revenue', 0):,.0f}</div>
                        <div style="font-size: 12px; color: #666;">Revenue</div>
                    </div>
                    <div style="background: white; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #17a2b8;">{briefing.metrics.get('conversions', 0):,}</div>
                        <div style="font-size: 12px; color: #666;">Conversions</div>
                    </div>
                </div>
                
                <h2 style="color: #1a1a2e;">💡 Key Insights</h2>
                {insights_html}
                
                <h2 style="color: #1a1a2e;">✅ Recommended Actions</h2>
                <ol style="padding-left: 20px;">
                    {recs_html or '<li>Review your campaigns and make adjustments as needed</li>'}
                </ol>
                
            </div>
            
            <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                <p>Powered by Quay Marketing Intelligence • Built by AI, for humans</p>
                <p><a href="#" style="color: #667eea;">View full dashboard</a> • 
                   <a href="#" style="color: #667eea;">Adjust preferences</a> • 
                   <a href="#" style="color: #667eea;">Pause briefings</a></p>
            </div>
            
        </body>
        </html>
        """
        
        text = f"""
QUAY DAILY BRIEFING - {briefing.date}
{'='*50}

PERFORMANCE SUMMARY
{briefing.summary}

KEY METRICS
- Visits: {briefing.metrics.get('traffic', 0):,}
- Revenue: ${briefing.metrics.get('revenue', 0):,.0f}
- Conversions: {briefing.metrics.get('conversions', 0):,}

{'='*50}

TOP INSIGHTS
"""
        for insight in briefing.insights[:5]:
            text += f"\n[{insight.priority.upper()}] {insight.text}\n  → {insight.recommendation}\n"
        
        text += f"""
{'='*50}

RECOMMENDED ACTIONS
"""
        for i, rec in enumerate(briefing.recommendations, 1):
            text += f"{i}. {rec}\n"
        
        subject = f"☀️ Daily Briefing: {briefing.metrics.get('traffic', 0):,} visits, ${briefing.metrics.get('revenue', 0):.0f} revenue"
        
        return {"subject": subject, "html_body": html, "text_body": text}
    
    def send_email(self, to_email: str, subject: str, html_body: str, 
                   text_body: str = None) -> Dict[str, Any]:
        """Send email via SendGrid."""
        if not self._sendgrid_api_key:
            return {
                "sent": False,
                "error": "SENDGRID_API_KEY not configured"
            }
        
        try:
            client = httpx.Client(
                base_url="https://api.sendgrid.com",
                headers={
                    "Authorization": f"Bearer {self._sendgrid_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": self._from_email},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": text_body or html_body},
                    {"type": "text/html", "value": html_body}
                ]
            }
            
            response = client.post("/v3/mail/send", json=payload)
            
            if response.status_code in (200, 201, 202):
                return {"sent": True, "message_id": response.headers.get("X-Message-Id")}
            else:
                return {"sent": False, "error": f"Failed: {response.status_code}"}
        
        except Exception as e:
            return {"sent": False, "error": str(e)}
    
    def send_daily_briefing(self, to_email: str, briefing, brand_name: str = "Your Brand") -> Dict[str, Any]:
        """Format and send daily briefing."""
        formatted = self.format_briefing_email(briefing, brand_name)
        return self.send_email(
            to_email=to_email,
            subject=formatted["subject"],
            html_body=formatted["html_body"],
            text_body=formatted["text_body"]
        )
