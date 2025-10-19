"""
DNS hostname resolver service
"""
import logging
import asyncio
import aiodns
from typing import Optional
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Cache for DNS lookups
dns_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache for 1 hour


async def resolve_hostname(ip_address: str) -> Optional[str]:
    """
    Resolve IP address to hostname
    
    Args:
        ip_address: IP address string
        
    Returns:
        Hostname or None if not resolved
    """
    try:
        # Check cache first
        if ip_address in dns_cache:
            return dns_cache[ip_address]
        
        # Create resolver
        resolver = aiodns.DNSResolver()
        
        # Perform reverse DNS lookup
        result = await resolver.gethostbyaddr(ip_address)
        hostname = result.name if result else None
        
        # Cache result
        dns_cache[ip_address] = hostname
        
        return hostname
        
    except Exception as e:
        logger.debug(f"Could not resolve hostname for IP {ip_address}: {e}")
        dns_cache[ip_address] = None  # Cache negative result
        return None


def resolve_hostname_sync(ip_address: str) -> Optional[str]:
    """
    Synchronous wrapper for hostname resolution
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(resolve_hostname(ip_address))
        loop.close()
        return result
    except Exception:
        return None
