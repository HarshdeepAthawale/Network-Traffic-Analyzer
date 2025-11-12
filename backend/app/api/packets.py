"""
Packets list API endpoint with pagination and filtering
"""
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.models.packet import PacketListResponse
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
        # Calculate skip/limit for pagination
        skip = (page - 1) * perPage
        limit = perPage
        
        # Get packets with pagination from MongoDB
        packets, total = await storage.get_packets(
            file_id=file_id,
            skip=skip,
            limit=limit,
            protocol=protocol,
            ip_query=ip,
        )

        if total == 0:
            raise HTTPException(
                status_code=404,
                detail="No parsed data found. Please upload a PCAP file first."
            )
        
        return PacketListResponse(
            items=packets,
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
