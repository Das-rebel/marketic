"""
Analytics Attribution — Multi-touch attribution models.
"""

import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class AttributionModel(str, Enum):
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"


@dataclass
class Touchpoint:
    touchpoint_id: str
    channel: str
    campaign: str
    timestamp: str
    event: str
    revenue: float
    conversion_value: float


@dataclass
class AttributionResult:
    channel: str
    attributed_value: float
    attribution_percentage: float
    touchpoint_count: int
    model: str


class MultiTouchAttribution:
    """Calculate multi-touch attribution across channels."""

    def __init__(self):
        pass

    def calculate(
        self,
        touchpoints: List[Touchpoint],
        model: AttributionModel = AttributionModel.LINEAR,
    ) -> List[AttributionResult]:
        """Calculate attribution for each channel."""

        if not touchpoints:
            return []

        # Group by channel
        channel_points = defaultdict(list)
        for tp in touchpoints:
            channel_points[tp.channel].append(tp)

        # Calculate attributed value per channel
        total_value = sum(tp.revenue for tp in touchpoints)
        results = []

        if model == AttributionModel.FIRST_TOUCH:
            # All credit to first touch
            if touchpoints:
                first_channel = touchpoints[0].channel
                for channel, points in channel_points.items():
                    attributed = total_value if channel == first_channel else 0
                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))

        elif model == AttributionModel.LAST_TOUCH:
            # All credit to last touch
            if touchpoints:
                last_channel = touchpoints[-1].channel
                for channel, points in channel_points.items():
                    attributed = total_value if channel == last_channel else 0
                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))

        elif model == AttributionModel.LINEAR:
            # Equal credit to all touchpoints
            num_touchpoints = len(touchpoints)
            value_per_touch = total_value / num_touchpoints if num_touchpoints > 0 else 0

            for channel, points in channel_points.items():
                attributed = value_per_touch * len(points)
                results.append(AttributionResult(
                    channel=channel,
                    attributed_value=attributed,
                    attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                    touchpoint_count=len(points),
                    model=model.value,
                ))

        elif model == AttributionModel.TIME_DECAY:
            # More credit to recent touchpoints
            if len(touchpoints) > 1:
                # Simple time decay: each touchpoint gets less credit as time goes on
                decay_factor = 0.5  # Half-life factor
                weights = []
                
                for i, tp in enumerate(touchpoints):
                    # Weight decreases as we go back in the touchpoint sequence
                    weight = pow(decay_factor, (len(touchpoints) - 1 - i))
                    weights.append(weight)
                
                total_weight = sum(weights)
                
                for channel, points in channel_points.items():
                    channel_indices = [i for i, tp in enumerate(touchpoints) if tp.channel == channel]
                    attributed = total_value * sum(weights[i] for i in channel_indices) / total_weight
                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))
            else:
                # Single touchpoint
                for channel, points in channel_points.items():
                    attributed = total_value
                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=100 if touchpoints and touchpoints[0].channel == channel else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))

        elif model == AttributionModel.POSITION_BASED:
            # 40% first touch, 40% last touch, 20% distributed among middle
            if len(touchpoints) == 1:
                # Single touchpoint gets full credit
                for channel, points in channel_points.items():
                    attributed = total_value if channel == touchpoints[0].channel else 0
                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))
            elif len(touchpoints) == 2:
                # 50/50 split
                for channel, points in channel_points.items():
                    attributed = total_value / 2 if channel in [touchpoints[0].channel, touchpoints[-1].channel] else 0
                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))
            else:
                # 40% first, 40% last, 20% distributed
                first_channel = touchpoints[0].channel
                last_channel = touchpoints[-1].channel
                middle_count = len(touchpoints) - 2
                middle_per_point = 0.2 / middle_count if middle_count > 0 else 0

                for channel, points in channel_points.items():
                    attributed = 0
                    if channel == first_channel:
                        attributed += total_value * 0.4
                    if channel == last_channel:
                        attributed += total_value * 0.4
                    if channel not in [first_channel, last_channel]:
                        attributed += total_value * middle_per_point * len(points)

                    results.append(AttributionResult(
                        channel=channel,
                        attributed_value=attributed,
                        attribution_percentage=(attributed / total_value * 100) if total_value > 0 else 0,
                        touchpoint_count=len(points),
                        model=model.value,
                    ))

        else:
            # Default to linear
            return self.calculate(touchpoints, AttributionModel.LINEAR)

        # Sort by attributed value
        results.sort(key=lambda x: x.attributed_value, reverse=True)
        return results
