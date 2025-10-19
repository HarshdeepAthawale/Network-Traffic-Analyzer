"""
Packets list API endpoint with pagination and filtering
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.models.packet import Packet, PacketListResponse
from app.services.storage import storage
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/packets", response_model=PacketListResponse)
async def get_packets(
    page: int = Query(1, ge=1),
    perPage: int = Query(settings.DEFAULT_PACKETS_PER_PAGE, ge=1, le=settings.MAX_PACKETS_PER_PAGE),
    protocol: Optional[str] = Query(None, description="Filter by protocol"),
    ip: Optional[str] = Query(None, description="Filter by IP address"),
    file_id: Optional[str] = Query(None, description="File ID")
):
    """
    Get paginated list of packets with optional filtering
    
    Args:
        page: Page number (1-based)
        perPage: Number of packets per page
        protocol: Optional protocol filter (TCP, UDP, ICMP, etc.)
        ip: Optional IP address filter (matches source or destination)
        file_id: Optional file ID, uses current file if not provided
        
    Returns:
        Paginated packet list
    """
    try:
        # Get all packets from storage
        all_packets = storage.get_packets(file_id)
        
        if not all_packets:
            raise HTTPException(
                status_code=404,
                detail="No parsed data found. Please upload a PCAP file first."
            )
        
        # Apply filters
        filtered_packets = _filter_packets(all_packets, protocol, ip)
        
        # Calculate pagination
        total = len(filtered_packets)
        start_idx = (page - 1) * perPage
        end_idx = start_idx + perPage
        
        # Get page of packets
        page_packets = filtered_packets[start_idx:end_idx]
        
        return PacketListResponse(
            items=page_packets,
            total=total,
            page=page,
            per_page=perPage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting packets: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving packets: {str(e)}"
        )


def _filter_packets(packets: List[Packet], protocol: Optional[str], ip: Optional[str]) -> List[Packet]:
    """Apply filters to packet list"""
    filtered = packets
    
    # Filter by protocol
    if protocol:
        protocol_upper = protocol.upper()
        filtered = [p for p in filtered if p.proto.upper() == protocol_upper]
    
    # Filter by IP (source or destination)
    if ip:
        filtered = [p for p in filtered if ip in p.src or ip in p.dst]
    
    return filtered
