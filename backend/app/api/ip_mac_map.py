"""
IP-MAC mapping API endpoint
"""
import logging
import asyncio
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.packet import IpMacMapping, IpMacMapResponse
from app.services.storage import storage
from app.services.vendor_lookup import get_vendor_by_mac
from app.services.user_extractor import extract_user_name
from app.services.dns_resolver import resolve_hostname

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/ip-mac-map", response_model=IpMacMapResponse)
async def get_ip_mac_map(
    file_id: Optional[str] = Query(None, description="File ID")
):
    """
    Get IP-MAC address mappings with statistics
    
    Args:
        file_id: Optional file ID, uses current file if not provided
        
    Returns:
        List of IP-MAC mappings with host info and statistics
    """
    try:
        # Get stats from storage
        stats = storage.get_stats(file_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail="No parsed data found. Please upload a PCAP file first."
            )
        
        # Get IP-MAC mappings and statistics
        ip_mac_map = stats.get('ip_mac_map', {})
        ip_stats = stats.get('ip_stats', {})
        mac_stats = stats.get('mac_stats', {})
        
        # Build mapping list
        mappings = []
        processed_ips = set()
        
        for ip, mac in ip_mac_map.items():
            if ip in processed_ips:
                continue
            processed_ips.add(ip)
            
            # Get statistics
            ip_stat = ip_stats.get(ip, {'packets': 0, 'bytes': 0})
            
            # Resolve hostname (async)
            hostname = await resolve_hostname(ip)
            
            # Extract user name from hostname
            user_name = extract_user_name(hostname) if hostname else None
            
            # Get vendor info
            vendor = get_vendor_by_mac(mac)
            
            mapping = IpMacMapping(
                ip=ip,
                mac=mac,
                host=hostname or f"host-{ip.split('.')[-1]}",  # Fallback hostname
                packets=ip_stat['packets'],
                bytes=ip_stat['bytes'],
                vendor=vendor,
                user_name=user_name
            )
            
            mappings.append(mapping)
        
        # Sort by packet count (descending)
        mappings.sort(key=lambda x: x.packets, reverse=True)
        
        return IpMacMapResponse(items=mappings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating IP-MAC map: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating IP-MAC map: {str(e)}"
        )
