"""
MAC address vendor lookup service
"""
import logging
from typing import Optional
from mac_vendor_lookup import MacLookup
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Initialize MAC lookup with cache
mac_lookup = MacLookup()
vendor_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache for 1 hour


def get_vendor_by_mac(mac_address: str) -> Optional[str]:
    """
    Get vendor name by MAC address
    
    Args:
        mac_address: MAC address string
        
    Returns:
        Vendor name or None if not found
    """
    try:
        # Check cache first
        if mac_address in vendor_cache:
            return vendor_cache[mac_address]
        
        # Lookup vendor
        vendor = mac_lookup.lookup(mac_address)
        
        # Cache result
        vendor_cache[mac_address] = vendor
        
        return vendor
        
    except Exception as e:
        logger.debug(f"Could not lookup vendor for MAC {mac_address}: {e}")
        return None
