"""
Attribution Modeling

Multi-touch attribution models for accurate performance measurement.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class AttributionModel(Enum):
    """Attribution model types."""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LAST_NON_DIRECT = "last_non_direct"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"


@dataclass
class Touchpoint:
    """A single touchpoint in the customer journey."""
    touchpoint_id: str
    channel: str
    campaign: str
    timestamp: str
    event: str  # impression, click, conversion
    revenue: float = 0
    conversion_value: float = 0


@dataclass
class AttributionResult:
    """Result of attribution analysis."""
    channel: str
    attributed_revenue: float
    attributed_conversions: float
    attribution_share: float  # 0-1
    touchpoints: int


class MultiTouchAttribution:
    """
    Calculate attribution across touchpoints using various models.
    
    Usage:
        mta = MultiTouchAttribution()
        results = mta.calculate(
            touchpoints=user_journey,
            model=AttributionModel.LINEAR
        )
    """
    
    def calculate(
        self,
        touchpoints: List[Touchpoint],
        model: AttributionModel,
        total_conversions: int = None,
        total_revenue: float = None,
    ) -> List[AttributionResult]:
        """Calculate attribution for each channel."""
        
        if not touchpoints:
            return []
        
        # Group by channel
        channel_points = {}
        for tp in touchpoints:
            if tp.channel not in channel_points:
                channel_points[tp.channel] = []
            channel_points[tp.channel].append(tp)
        
        # Calculate based on model
        if model == AttributionModel.FIRST_TOUCH:
            return self._first_touch(channel_points)
        elif model == AttributionModel.LAST_TOUCH:
            return self._last_touch(channel_points)
        elif model == AttributionModel.LAST_NON_DIRECT:
            return self._last_non_direct(channel_points)
        elif model == AttributionModel.LINEAR:
            return self._linear(channel_points)
        elif model == AttributionModel.TIME_DECAY:
            return self._time_decay(channel_points)
        elif model == AttributionModel.POSITION_BASED:
            return self._position_based(channel_points)
        else:
            return self._linear(channel_points)
    
    def _first_touch(self, channel_points: Dict) -> List[AttributionResult]:
        """First touch attribution - 100% to first touchpoint."""
        results = []
        total_value = sum(tp.conversion_value for pts in channel_points.values() for tp in pts)
        
        for channel, pts in channel_points.items():
            if pts:
                # Sort by timestamp
                sorted_pts = sorted(pts, key=lambda x: x.timestamp)
                first = sorted_pts[0]
                results.append(AttributionResult(
                    channel=channel,
                    attributed_revenue=first.conversion_value,
                    attributed_conversions=1 if first.event == "conversion" else 0,
                    attribution_share=first.conversion_value / total_value if total_value > 0 else 0,
                    touchpoints=len(pts),
                ))
        
        return results
    
    def _last_touch(self, channel_points: Dict) -> List[AttributionResult]:
        """Last touch attribution - 100% to last touchpoint."""
        results = []
        total_value = sum(tp.conversion_value for pts in channel_points.values() for tp in pts)
        
        for channel, pts in channel_points.items():
            if pts:
                sorted_pts = sorted(pts, key=lambda x: x.timestamp, reverse=True)
                last = sorted_pts[0]
                results.append(AttributionResult(
                    channel=channel,
                    attributed_revenue=last.conversion_value,
                    attributed_conversions=1 if last.event == "conversion" else 0,
                    attribution_share=last.conversion_value / total_value if total_value > 0 else 0,
                    touchpoints=len(pts),
                ))
        
        return results
    
    def _last_non_direct(self, channel_points: Dict) -> List[AttributionResult]:
        """Last non-direct click attribution."""
        results = []
        
        for channel, pts in channel_points.items():
            if pts and channel != "direct":
                sorted_pts = sorted(pts, key=lambda x: x.timestamp, reverse=True)
                last = sorted_pts[0]
                results.append(AttributionResult(
                    channel=channel,
                    attributed_revenue=last.conversion_value,
                    attributed_conversions=1 if last.event == "conversion" else 0,
                    attribution_share=1.0,
                    touchpoints=len(pts),
                ))
        
        return results
    
    def _linear(self, channel_points: Dict) -> List[AttributionResult]:
        """Linear attribution - equal credit to all touchpoints."""
        results = []
        
        # Count total touchpoints
        total_points = sum(len(pts) for pts in channel_points.values())
        if total_points == 0:
            return []
        
        for channel, pts in channel_points.items():
            if pts:
                share = len(pts) / total_points
                revenue = sum(p.conversion_value for p in pts) * share
                
                results.append(AttributionResult(
                    channel=channel,
                    attributed_revenue=revenue,
                    attributed_conversions=len([p for p in pts if p.event == "conversion"]) * share,
                    attribution_share=share,
                    touchpoints=len(pts),
                ))
        
        return results
    
    def _time_decay(self, channel_points: Dict) -> List[AttributionResult]:
        """Time decay - more credit to recent touchpoints."""
        results = []
        
        # Calculate weights based on recency
        all_points = []
        for ch, pts in channel_points.items():
            for p in pts:
                all_points.append((ch, p))
        
        if not all_points:
            return []
        
        # Sort by timestamp
        all_points.sort(key=lambda x: x[1].timestamp)
        
        # Assign weights (exponential decay)
        n = len(all_points)
        decay_rate = 0.5  # Half-life factor
        
        channel_weights = {}
        for i, (ch, pt) in enumerate(all_points):
            # Weight increases exponentially for more recent
            weight = 2 ** (i / decay_rate)
            if ch not in channel_weights:
                channel_weights[ch] = 0
            channel_weights[ch] += weight * pt.conversion_value
        
        total = sum(channel_weights.values())
        
        for channel in channel_points.keys():
            weight = channel_weights.get(channel, 0)
            results.append(AttributionResult(
                channel=channel,
                attributed_revenue=weight,
                attributed_conversions=weight / total if total > 0 else 0,
                attribution_share=weight / total if total > 0 else 0,
                touchpoints=len(channel_points.get(channel, [])),
            ))
        
        return results
    
    def _position_based(self, channel_points: Dict) -> List[AttributionResult]:
        """Position based - 40% first, 40% last, 20% middle."""
        results = []
        
        for channel, pts in channel_points.items():
            if pts:
                sorted_pts = sorted(pts, key=lambda x: x.timestamp)
                n = len(sorted_pts)
                
                if n == 1:
                    share = 1.0
                elif n == 2:
                    share = 0.5
                else:
                    # 40% first, 40% last, 20% distributed
                    share = (0.4 + 0.4 + 0.2 * (n - 2) / n)
                
                revenue = sum(p.conversion_value for p in pts) * share / n
                
                results.append(AttributionResult(
                    channel=channel,
                    attributed_revenue=revenue,
                    attributed_conversions=0,  # Simplified
                    attribution_share=share / n,
                    touchpoints=n,
                ))
        
        return results
    
    def generate_report(
        self,
        touchpoints: List[Touchpoint],
        models: List[AttributionModel] = None,
    ) -> Dict:
        """Generate comparison report across multiple models."""
        if models is None:
            models = [
                AttributionModel.FIRST_TOUCH,
                AttributionModel.LAST_TOUCH,
                AttributionModel.LINEAR,
                AttributionModel.TIME_DECAY,
                AttributionModel.POSITION_BASED,
            ]
        
        report = {}
        for model in models:
            results = self.calculate(touchpoints, model)
            report[model.value] = {
                r.channel: {
                    "attributed_revenue": r.attributed_revenue,
                    "attribution_share": r.attribution_share,
                    "touchpoints": r.touchpoints,
                }
                for r in results
            }
        
        return report


def demo():
    """Demo attribution modeling."""
    print("=" * 60)
    print("MARKETIC ATTRIBUTION MODELING DEMO")
    print("=" * 60)
    
    mta = MultiTouchAttribution()
    
    # Sample customer journey
    touchpoints = [
        Touchpoint("t1", "google_search", "brand", "2025-01-01T10:00:00", "click", conversion_value=0),
        Touchpoint("t2", "meta_feed", "awareness", "2025-01-03T14:00:00", "impression", conversion_value=0),
        Touchpoint("t3", "google_search", "brand", "2025-01-05T09:00:00", "click", conversion_value=0),
        Touchpoint("t4", "email", "newsletter", "2025-01-07T11:00:00", "click", conversion_value=0),
        Touchpoint("t5", "google_search", "retargeting", "2025-01-10T16:00:00", "click", conversion_value=500),
    ]
    
    print("\n📊 Customer Journey:")
    for tp in touchpoints:
        print(f"  {tp.timestamp[5:10]} | {tp.channel:20} | {tp.event}")
    
    # Compare models
    print("\n🔄 Attribution by Model:")
    for model in AttributionModel:
        if model.value in ["first_touch", "last_touch", "linear", "time_decay"]:
            results = mta.calculate(touchpoints, model)
            total_revenue = sum(r.attributed_revenue for r in results)
            print(f"\n  {model.value.replace('_', ' ').title()}:")
            for r in results:
                print(f"    {r.channel:20}: ${r.attributed_revenue:.2f} ({r.attribution_share*100:.1f}%)")
    
    # Full comparison report
    print("\n📋 Full Model Comparison:")
    report = mta.generate_report(touchpoints)
    for model_name, channels in report.items():
        print(f"\n  {model_name}:")
        for ch, data in channels.items():
            print(f"    {ch}: ${data['attributed_revenue']:.2f}")
    
    return mta


if __name__ == "__main__":
    demo()
