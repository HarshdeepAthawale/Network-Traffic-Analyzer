"""
Storage service for parsed PCAP data
Uses Cloudinary if configured, otherwise falls back to in-memory storage
"""
import logging
from typing import Optional, Dict, List

from app.models.packet import Packet
from app.core.config import settings
from app.services.in_memory_storage import in_memory_storage
from app.services.cloudinary_storage import cloudinary_storage

logger = logging.getLogger(__name__)


class StorageProxy:
    """Proxy to access storage - uses Cloudinary if configured, otherwise in-memory"""
    
    def __init__(self):
        """Initialize storage proxy"""
        # Check if Cloudinary is configured
        self.use_cloudinary = bool(
            settings.CLOUDINARY_CLOUD_NAME and 
            settings.CLOUDINARY_API_KEY and 
            settings.CLOUDINARY_API_SECRET
        )
        
        if self.use_cloudinary:
            logger.info("Using Cloudinary for storage")
            self.active_storage = cloudinary_storage
        else:
            logger.info("Using in-memory storage (Cloudinary not configured)")
            self.active_storage = in_memory_storage
    
    async def store_file(self, filename: str, packets: List[Packet], stats: Dict) -> str:
        """Store parsed file data"""
        return await self.active_storage.store_file(filename, packets, stats)
    
    async def get_packets(self, file_id: Optional[str] = None, skip: int = 0, limit: int = 1000) -> List[Packet]:
        """Get packets for a file with pagination"""
        return await self.active_storage.get_packets(file_id, skip=skip, limit=limit)
    
    async def get_stats(self, file_id: Optional[str] = None) -> Dict:
        """Get statistics for a file"""
        return await self.active_storage.get_stats(file_id)
    
    async def get_file_info(self, file_id: Optional[str] = None) -> Optional[Dict]:
        """Get file metadata"""
        return await self.active_storage.get_file_info(file_id)
    
    def clear(self):
        """Clear all stored data"""
        logger.info("Clear operation called")


# Create global storage proxy instance
_storage_instance = None

def get_storage():
    """Get or create storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageProxy()
    return _storage_instance

# Initialize storage
storage = get_storage()
