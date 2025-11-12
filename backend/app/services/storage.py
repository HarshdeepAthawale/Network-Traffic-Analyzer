"""
Storage service abstraction backed by MongoDB.
"""
import logging
from typing import Dict, List, Optional, Tuple

from app.models.packet import Packet
from app.services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)


class StorageProxy:
    """Proxy to access MongoDB-backed storage."""

    async def store_file(
        self,
        file_id: str,
        packets: List[Packet],
        stats: Dict,
    ) -> str:
        """Persist parsed packet data and statistics."""
        await mongodb_service.store_parsed_data(file_id, packets, stats)
        return file_id

    async def get_packets(
        self,
        file_id: Optional[str],
        skip: int = 0,
        limit: int = 1000,
        protocol: Optional[str] = None,
        ip_query: Optional[str] = None,
    ) -> Tuple[List[Packet], int]:
        """Return packets and total count for a file."""
        if not file_id:
            file_id = await mongodb_service.get_latest_file_id()
            if not file_id:
                return [], 0

        return await mongodb_service.get_packets(
            file_id=file_id,
            skip=skip,
            limit=limit,
            protocol=protocol,
            ip_query=ip_query,
        )

    async def get_all_packets(self, file_id: Optional[str]) -> List[Packet]:
        """Return all packets for summary calculations."""
        if not file_id:
            file_id = await mongodb_service.get_latest_file_id()
            if not file_id:
                return []

        return await mongodb_service.get_all_packets(file_id)

    async def get_stats(self, file_id: Optional[str]) -> Dict:
        """Fetch stored statistics for a file."""
        if not file_id:
            file_id = await mongodb_service.get_latest_file_id()
            if not file_id:
                return {}

        stats = await mongodb_service.get_stats(file_id)
        return stats or {}

    async def get_file_info(self, file_id: Optional[str]) -> Optional[Dict]:
        """Fetch file metadata."""
        if not file_id:
            file_id = await mongodb_service.get_latest_file_id()
            if not file_id:
                return None
        return await mongodb_service.get_file_metadata(file_id)

    async def list_files(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List stored file metadata."""
        return await mongodb_service.list_files(skip=skip, limit=limit)

    def clear(self):
        """Clear stored data (not implemented)."""
        logger.info("Clear operation requested - MongoDB storage retains data.")


storage = StorageProxy()
