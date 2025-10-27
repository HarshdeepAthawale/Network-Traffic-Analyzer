"""
Storage service for parsed PCAP data - Cloudinary
"""
import logging
from typing import Optional, Dict, List

from app.models.packet import Packet
from app.services.cloudinary_storage import cloudinary_storage

logger = logging.getLogger(__name__)


class StorageProxy:
    """Proxy to access Cloudinary storage"""
    
    async def store_file(self, filename: str, packets: List[Packet], stats: Dict) -> str:
        """Store parsed file data"""
        return await cloudinary_storage.store_file(filename, packets, stats)
    
    async def get_packets(self, file_id: Optional[str] = None, skip: int = 0, limit: int = 1000) -> List[Packet]:
        """Get packets for a file with pagination"""
        return await cloudinary_storage.get_packets(file_id, skip=skip, limit=limit)
    
    async def get_stats(self, file_id: Optional[str] = None) -> Dict:
        """Get statistics for a file"""
        return await cloudinary_storage.get_stats(file_id)
    
    async def get_file_info(self, file_id: Optional[str] = None) -> Optional[Dict]:
        """Get file metadata"""
        return await cloudinary_storage.get_file_info(file_id)
    
    def clear(self):
        """Clear all stored data"""
        logger.info("Clear operation called - Cloudinary storage is persistent")


# Create global storage proxy instance
storage = StorageProxy()
