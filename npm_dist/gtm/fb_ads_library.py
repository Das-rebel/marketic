"""
Facebook Ads Library client — real competitor creatives from Meta's public archive.

Queries the public ads_archive endpoint. Auth via FB_ACCESS_TOKEN env var;
if unset, the client reports itself unavailable so callers fall back
gracefully to other backends.
"""

import os
from typing import Dict, List

import httpx

ADS_ARCHIVE_URL = "https://graph.facebook.com/v19.0/ads_archive"
FIELDS = ("id,ad_creative_bodies,ad_creative_link_titles,"
          "ad_delivery_start_time,publisher_platforms,page_name")


class FBAdsLibraryClient:
    """Thin wrapper over Meta's public Ad Library API (ads_archive)."""

    def __init__(self, access_token: str = "", timeout: float = 30.0):
        self._token = access_token or os.environ.get("FB_ACCESS_TOKEN", "")
        self._timeout = timeout

    def is_available(self) -> bool:
        """True only if an access token is configured."""
        return bool(self._token)

    def search_ads(self, brand_name: str, country: str = "ALL",
                   limit: int = 20) -> List[Dict]:
        """
        Search the Ad Library for a brand's active ads.

        Returns normalized dicts:
          {ad_id, page_name, bodies[], titles[], platforms[], delivery_start}
        Empty list on any error or if unavailable.
        """
        if not self.is_available() or not brand_name:
            return []

        params: Dict[str, str] = {
            "search_terms": brand_name,
            "access_token": self._token,
            "ad_type": "ALL",
            "fields": FIELDS,
            "limit": str(max(1, min(int(limit), 100))),
        }
        if country and country != "ALL":
            params["ad_reached_countries"] = country.upper()
        else:
            # ads_archive requires a country; default to US when unspecified
            params["ad_reached_countries"] = "US"

        try:
            resp = httpx.get(ADS_ARCHIVE_URL, params=params,
                             timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json().get("data", [])
        except Exception as e:
            print(f"[fb_ads_library] search failed for {brand_name!r}: {e}")
            return []

        return [self._normalize(item) for item in data]

    @staticmethod
    def _normalize(item: Dict) -> Dict:
        page = item.get("page") or {}
        return {
            "ad_id": item.get("id", ""),
            "page_name": page.get("name", "") if isinstance(page, dict) else str(page),
            "bodies": list(item.get("ad_creative_bodies") or []),
            "titles": list(item.get("ad_creative_link_titles") or []),
            "platforms": list(item.get("publisher_platforms") or []),
            "delivery_start": item.get("ad_delivery_start_time", ""),
        }
