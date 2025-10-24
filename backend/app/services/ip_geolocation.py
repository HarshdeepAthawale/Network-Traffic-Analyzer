"""
IP geolocation service
"""
import logging
from typing import Optional, Dict, Any
import requests
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Cache for geolocation lookups
geo_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache for 1 hour


async def get_ip_geolocation(ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Get geolocation information for an IP address
    
    Args:
        ip_address: IP address string
        
    Returns:
        Geolocation data or None if not found
    """
    try:
        # Check cache first
        if ip_address in geo_cache:
            return geo_cache[ip_address]
        
        # Skip private IP addresses
        if ip_address.startswith(('192.168.', '10.', '172.')):
            geo_cache[ip_address] = None
            return None
        
        # Use a free IP geolocation service
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                geo_data = {
                    'country': data.get('country'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org')
                }
                geo_cache[ip_address] = geo_data
                return geo_data
        
        geo_cache[ip_address] = None
        return None
        
    except Exception as e:
        logger.debug(f"Could not get geolocation for IP {ip_address}: {e}")
        geo_cache[ip_address] = None
        return None


def get_ip_geolocation_sync(ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Synchronous wrapper for IP geolocation
    """
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_ip_geolocation(ip_address))
        loop.close()
        return result
    except Exception:
        return None