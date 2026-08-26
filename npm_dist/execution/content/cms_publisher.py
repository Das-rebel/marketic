"""
CMS Publisher — Publish content to WordPress, Webflow, and Shopify.
"""

import os
import json
import base64
from typing import Dict, Optional, Any
from dataclasses import dataclass

import httpx


@dataclass
class PublishResult:
    published_url: Optional[str]
    post_id: Optional[str]
    status: str
    message: str


class CMSPublisher:
    """Publish content to various CMS platforms."""
    
    def __init__(self):
        self._clients: Dict[str, httpx.Client] = {}
    
    def connect_wordpress(self, site_url: str, username: str, app_password: str) -> Dict[str, Any]:
        """
        Connect to WordPress site.
        username: WordPress username
        app_password: Application password (not regular password)
        """
        # Validate URL
        if not site_url.startswith(("http://", "https://")):
            site_url = "https://" + site_url
        site_url = site_url.rstrip("/")
        
        # Create auth header
        auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
        
        # Test connection
        try:
            client = httpx.Client(
                base_url=f"{site_url}/wp-json/wp/v2",
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            response = client.get("/users/me")
            if response.status_code == 200:
                user_data = response.json()
                self._clients["wordpress"] = client
                return {
                    "connected": True,
                    "site_url": site_url,
                    "user": user_data.get("name"),
                    "role": user_data.get("roles", [""])[0]
                }
            else:
                return {
                    "connected": False,
                    "error": f"Authentication failed: {response.status_code}"
                }
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def connect_shopify(self, shop_url: str, access_token: str) -> Dict[str, Any]:
        """Connect to Shopify store."""
        if not shop_url.startswith(("http://", "https://")):
            shop_url = "https://" + shop_url
        shop_url = shop_url.rstrip("/")
        
        try:
            client = httpx.Client(
                base_url=f"{shop_url}/admin/api/2024-01",
                headers={
                    "X-Shopify-Access-Token": access_token,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            response = client.get("/shop.json")
            if response.status_code == 200:
                shop_data = response.json()
                self._clients["shopify"] = client
                return {
                    "connected": True,
                    "shop_url": shop_url,
                    "shop_name": shop_data.get("shops", [{}])[0].get("name")
                }
            else:
                return {"connected": False, "error": f"Connection failed: {response.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def publish_article(self, article_data: Dict, cms_target: str = "wordpress",
                       draft: bool = False, author_id: int = 1) -> PublishResult:
        """
        Publish article to CMS.
        
        article_data should have:
        - title: str
        - content: str (HTML or Markdown)
        - meta_description: str
        - featured_image_url: str (optional)
        """
        title = article_data.get("title", "Untitled")
        content = article_data.get("content", "")
        meta_description = article_data.get("meta_description", "")
        
        if cms_target == "wordpress":
            return self._publish_wordpress(title, content, meta_description, draft, author_id)
        elif cms_target == "shopify":
            return self._publish_shopify_article(title, content, draft)
        else:
            return PublishResult(
                published_url=None,
                post_id=None,
                status="error",
                message=f"Unknown CMS target: {cms_target}"
            )
    
    def _publish_wordpress(self, title: str, content: str, meta_description: str,
                          draft: bool, author_id: int) -> PublishResult:
        """Publish to WordPress."""
        if "wordpress" not in self._clients:
            return PublishResult(
                published_url=None,
                post_id=None,
                status="error",
                message="WordPress not connected. Call connect_wordpress() first."
            )
        
        client = self._clients["wordpress"]
        
        # Convert content to HTML if needed
        if not content.startswith("<"):
            content = content.replace("\n", "<br>\n")
            content = f"<p>{content}</p>"
        
        payload = {
            "title": title,
            "content": content,
            "status": "draft" if draft else "publish",
            "author": author_id,
            "meta": {
                "_yoast_wpseo_metadesc": meta_description
            }
        }
        
        try:
            response = client.post("/posts", json=payload)
            if response.status_code in (200, 201):
                data = response.json()
                return PublishResult(
                    published_url=data.get("link"),
                    post_id=str(data.get("id")),
                    status="published" if not draft else "draft",
                    message="Successfully published to WordPress"
                )
            else:
                return PublishResult(
                    published_url=None,
                    post_id=None,
                    status="error",
                    message=f"Publish failed: {response.status_code} - {response.text}"
                )
        except Exception as e:
            return PublishResult(
                published_url=None,
                post_id=None,
                status="error",
                message=f"Publish error: {str(e)}"
            )
    
    def _publish_shopify_article(self, title: str, content: str, draft: bool) -> PublishResult:
        """Publish article to Shopify Blog."""
        if "shopify" not in self._clients:
            return PublishResult(
                published_url=None,
                post_id=None,
                status="error",
                message="Shopify not connected. Call connect_shopify() first."
            )
        
        client = self._clients["shopify"]
        
        # Convert to HTML
        if not content.startswith("<"):
            content = content.replace("\n\n", "</p><p>")
            content = f"<p>{content}</p>"
        
        payload = {
            "article": {
                "title": title,
                "body_html": content,
                "published": not draft
            }
        }
        
        try:
            # Get first blog ID
            blogs_response = client.get("/blogs.json")
            if blogs_response.status_code != 200:
                return PublishResult(
                    published_url=None, post_id=None, status="error",
                    message=f"Failed to get blogs: {blogs_response.status_code}"
                )
            
            blogs = blogs_response.json().get("blogs", [])
            if not blogs:
                return PublishResult(
                    published_url=None, post_id=None, status="error",
                    message="No blogs found in Shopify store"
                )
            
            blog_id = blogs[0]["blog"]["id"]
            
            # Create article
            response = client.post(f"/blogs/{blog_id}/articles.json", json=payload)
            if response.status_code in (200, 201):
                data = response.json()
                article = data.get("article", {})
                return PublishResult(
                    published_url=article.get("handle"),
                    post_id=str(article.get("id")),
                    status="published" if not draft else "draft",
                    message="Successfully published to Shopify"
                )
            else:
                return PublishResult(
                    published_url=None, post_id=None, status="error",
                    message=f"Publish failed: {response.status_code} - {response.text}"
                )
        except Exception as e:
            return PublishResult(
                published_url=None, post_id=None, status="error",
                message=f"Publish error: {str(e)}"
            )
    
    def disconnect(self, cms_target: str):
        """Disconnect from a CMS."""
        if cms_target in self._clients:
            del self._clients[cms_target]
