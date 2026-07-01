"""
Marketic Analytics & Tracking

Performance measurement, attribution modeling, and reporting.
"""

from .attribution import AttributionModel, MultiTouchAttribution
from .dashboards import AnalyticsDashboard
from .reports import ReportGenerator

__all__ = [
    "AttributionModel",
    "MultiTouchAttribution",
    "AnalyticsDashboard",
    "ReportGenerator",
]
