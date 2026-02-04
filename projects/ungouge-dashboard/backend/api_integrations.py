"""
API Integrations for UnGouge Dashboard
Handles YouTube Data API, Stripe API, Google Analytics 4
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx

# Cache duration (seconds)
CACHE_DURATION = 3600  # 1 hour

class APICache:
    """Simple in-memory cache for API responses"""
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            data, expires_at = self._cache[key]
            if time.time() < expires_at:
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_DURATION):
        """Set cache value with TTL"""
        expires_at = time.time() + ttl
        self._cache[key] = (value, expires_at)
    
    def clear(self):
        """Clear all cache"""
        self._cache = {}

# Global cache instance
cache = APICache()


class YouTubeAPI:
    """YouTube Data API v3 integration"""
    
    def __init__(self, api_key: str, channel_id: Optional[str] = None):
        self.api_key = api_key
        self.channel_id = channel_id
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def get_channel_stats(self) -> Dict[str, Any]:
        """Get channel statistics"""
        if not self.channel_id:
            return self._empty_stats()
        
        cache_key = f"youtube_channel_{self.channel_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/channels",
                    params={
                        "key": self.api_key,
                        "id": self.channel_id,
                        "part": "statistics,snippet"
                    }
                )
                
                if response.status_code != 200:
                    print(f"YouTube API error: {response.status_code} - {response.text}")
                    return self._empty_stats()
                
                data = response.json()
                if not data.get("items"):
                    return self._empty_stats()
                
                item = data["items"][0]
                stats = item.get("statistics", {})
                
                result = {
                    "subscribers": int(stats.get("subscriberCount", 0)),
                    "total_views": int(stats.get("viewCount", 0)),
                    "total_videos": int(stats.get("videoCount", 0)),
                    "channel_title": item.get("snippet", {}).get("title", "Unknown"),
                    "last_updated": datetime.now().isoformat()
                }
                
                cache.set(cache_key, result)
                return result
        
        except Exception as e:
            print(f"YouTube API exception: {e}")
            return self._empty_stats()
    
    async def get_recent_videos(self, max_results: int = 10) -> list:
        """Get recent videos"""
        if not self.channel_id:
            return []
        
        cache_key = f"youtube_videos_{self.channel_id}_{max_results}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                # Get uploads playlist ID
                channel_response = await client.get(
                    f"{self.base_url}/channels",
                    params={
                        "key": self.api_key,
                        "id": self.channel_id,
                        "part": "contentDetails"
                    }
                )
                
                if channel_response.status_code != 200:
                    return []
                
                channel_data = channel_response.json()
                if not channel_data.get("items"):
                    return []
                
                uploads_playlist_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                
                # Get videos from uploads playlist
                videos_response = await client.get(
                    f"{self.base_url}/playlistItems",
                    params={
                        "key": self.api_key,
                        "playlistId": uploads_playlist_id,
                        "part": "snippet",
                        "maxResults": max_results
                    }
                )
                
                if videos_response.status_code != 200:
                    return []
                
                videos_data = videos_response.json()
                videos = []
                
                for item in videos_data.get("items", []):
                    snippet = item.get("snippet", {})
                    videos.append({
                        "video_id": snippet.get("resourceId", {}).get("videoId"),
                        "title": snippet.get("title"),
                        "published_at": snippet.get("publishedAt"),
                        "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url")
                    })
                
                cache.set(cache_key, videos)
                return videos
        
        except Exception as e:
            print(f"YouTube videos API exception: {e}")
            return []
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            "subscribers": 0,
            "total_views": 0,
            "total_videos": 0,
            "channel_title": "Not Connected",
            "last_updated": datetime.now().isoformat()
        }


class StripeAPI:
    """Stripe API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stripe.com/v1"
    
    async def get_revenue_stats(self) -> Dict[str, Any]:
        """Get revenue statistics"""
        cache_key = "stripe_revenue"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                # Get charges from last 30 days
                thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
                
                response = await client.get(
                    f"{self.base_url}/charges",
                    headers=headers,
                    params={
                        "created[gte]": thirty_days_ago,
                        "limit": 100
                    }
                )
                
                if response.status_code != 200:
                    print(f"Stripe API error: {response.status_code}")
                    return self._empty_stats()
                
                data = response.json()
                charges = data.get("data", [])
                
                # Calculate stats
                total_revenue = sum(c["amount"] for c in charges if c["paid"]) / 100  # Convert cents to dollars
                successful_charges = len([c for c in charges if c["paid"]])
                
                # Get current month revenue
                now = datetime.now()
                month_start = int(datetime(now.year, now.month, 1).timestamp())
                month_revenue = sum(
                    c["amount"] for c in charges 
                    if c["paid"] and c["created"] >= month_start
                ) / 100
                
                result = {
                    "total_revenue_30d": round(total_revenue, 2),
                    "total_revenue_mtd": round(month_revenue, 2),
                    "successful_charges": successful_charges,
                    "last_updated": datetime.now().isoformat()
                }
                
                cache.set(cache_key, result)
                return result
        
        except Exception as e:
            print(f"Stripe API exception: {e}")
            return self._empty_stats()
    
    async def get_customer_stats(self) -> Dict[str, Any]:
        """Get customer statistics"""
        cache_key = "stripe_customers"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                response = await client.get(
                    f"{self.base_url}/customers",
                    headers=headers,
                    params={"limit": 100}
                )
                
                if response.status_code != 200:
                    return {"total_customers": 0}
                
                data = response.json()
                total_customers = len(data.get("data", []))
                
                result = {"total_customers": total_customers}
                cache.set(cache_key, result)
                return result
        
        except Exception as e:
            print(f"Stripe customers API exception: {e}")
            return {"total_customers": 0}
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            "total_revenue_30d": 0.0,
            "total_revenue_mtd": 0.0,
            "successful_charges": 0,
            "last_updated": datetime.now().isoformat()
        }


class GoogleAnalyticsAPI:
    """Google Analytics 4 API integration"""
    
    def __init__(self, property_id: str, credentials_json: str):
        self.property_id = property_id
        self.credentials_json = credentials_json
    
    async def get_traffic_stats(self) -> Dict[str, Any]:
        """Get website traffic statistics"""
        # GA4 requires google-analytics-data package
        # For now, return placeholder
        # TODO: Implement when GA4 is set up
        
        return {
            "sessions_7d": 0,
            "pageviews_7d": 0,
            "users_7d": 0,
            "conversions_7d": 0,
            "last_updated": datetime.now().isoformat(),
            "status": "not_configured"
        }


# Singleton instances (initialized when env vars are set)
youtube_api: Optional[YouTubeAPI] = None
stripe_api: Optional[StripeAPI] = None
ga_api: Optional[GoogleAnalyticsAPI] = None


def initialize_apis():
    """Initialize API clients from environment variables"""
    global youtube_api, stripe_api, ga_api
    
    # YouTube
    youtube_key = os.getenv("YOUTUBE_API_KEY")
    youtube_channel = os.getenv("YOUTUBE_CHANNEL_ID")
    if youtube_key:
        youtube_api = YouTubeAPI(youtube_key, youtube_channel)
        print("✅ YouTube API initialized")
    else:
        print("⚠️ YouTube API not configured (missing YOUTUBE_API_KEY)")
    
    # Stripe
    stripe_key = os.getenv("STRIPE_API_KEY")
    if stripe_key:
        stripe_api = StripeAPI(stripe_key)
        print("✅ Stripe API initialized")
    else:
        print("⚠️ Stripe API not configured (missing STRIPE_API_KEY)")
    
    # Google Analytics
    ga_property = os.getenv("GA4_PROPERTY_ID")
    ga_creds = os.getenv("GA4_CREDENTIALS_JSON")
    if ga_property and ga_creds:
        ga_api = GoogleAnalyticsAPI(ga_property, ga_creds)
        print("✅ Google Analytics API initialized")
    else:
        print("⚠️ Google Analytics not configured (missing GA4_PROPERTY_ID or GA4_CREDENTIALS_JSON)")


async def get_all_external_metrics() -> Dict[str, Any]:
    """Fetch all external API metrics"""
    metrics = {
        "youtube": {},
        "stripe": {},
        "analytics": {}
    }
    
    # YouTube
    if youtube_api:
        try:
            metrics["youtube"] = await youtube_api.get_channel_stats()
        except Exception as e:
            print(f"Error fetching YouTube metrics: {e}")
            metrics["youtube"] = {"error": str(e)}
    
    # Stripe
    if stripe_api:
        try:
            revenue = await stripe_api.get_revenue_stats()
            customers = await stripe_api.get_customer_stats()
            metrics["stripe"] = {**revenue, **customers}
        except Exception as e:
            print(f"Error fetching Stripe metrics: {e}")
            metrics["stripe"] = {"error": str(e)}
    
    # Google Analytics
    if ga_api:
        try:
            metrics["analytics"] = await ga_api.get_traffic_stats()
        except Exception as e:
            print(f"Error fetching GA metrics: {e}")
            metrics["analytics"] = {"error": str(e)}
    
    return metrics
