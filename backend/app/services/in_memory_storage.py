"""
In-memory storage service for parsed PCAP data
This is used when Cloudinary is not configured
"""
import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from app.models.packet import Packet

logger = logging.getLogger(__name__)


class InMemoryStorage:
    """In-memory storage for parsed PCAP data"""
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._cache = {}
        self._current_file_id = None
        logger.info("In-memory storage initialized")
    
    async def store_file(self, filename: str, packets: List[Packet], stats: Dict) -> str:
        """Store parsed file data in memory"""
        file_id = str(uuid.uuid4())
        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        upload_time = datetime.now(ist_timezone)
        
        try:
            # Prepare data for storage
            file_info = {
                'id': file_id,
                'filename': filename,
                'upload_time': upload_time.isoformat(),
                'packet_count': len(packets),
                'total_bytes': stats.get('total_bytes', 0)
            }
            
            # Convert packets to serializable format
            packets_data = [packet.model_dump() for packet in packets]
            
            # Prepare stats data (ensure it's serializable)
            stats_data = stats.copy()
            if 'protocols' in stats_data and isinstance(stats_data['protocols'], dict):
                stats_data['protocols'] = dict(stats_data['protocols'])
            
            # Store in memory
            self._cache[file_id] = {
                'info': file_info,
                'packets': packets_data,
                'stats': stats_data
            }
            
            # Set as current file
            self._current_file_id = file_id
            
            logger.info(f"Stored file {filename} with ID {file_id}, {len(packets)} packets")
            return file_id
            
        except Exception as e:
            logger.error(f"Error storing file: {e}", exc_info=True)
            raise
    
    async def get_packets(self, file_id: Optional[str] = None, skip: int = 0, limit: int = 1000) -> List[Packet]:
        """Get packets for a file"""
        # If no file_id provided, use current file
        if not file_id:
            file_id = self._current_file_id
        
        if not file_id:
            logger.warning("No file_id provided and no current file")
            return []
        
        try:
            # Check cache
            if file_id not in self._cache:
                logger.warning(f"File {file_id} not found in cache")
                return []
            
            packets_data = self._cache[file_id]['packets']
            
            # Apply pagination
            paginated_data = packets_data[skip:skip + limit]
            
            # Convert to Packet objects
            packets = []
            for data in paginated_data:
                try:
                    packet = Packet(**data)
                    packets.append(packet)
                except Exception as e:
                    logger.warning(f"Error parsing packet: {e}")
            
            return packets
            
        except Exception as e:
            logger.error(f"Error retrieving packets: {e}", exc_info=True)
            return []
    
    async def get_stats(self, file_id: Optional[str] = None) -> Dict:
        """Get statistics for a file"""
        # If no file_id provided, use current file
        if not file_id:
            file_id = self._current_file_id
        
        if not file_id:
            logger.warning("No file_id provided and no current file")
            return {}
        
        try:
            # Check cache
            if file_id not in self._cache:
                logger.warning(f"File {file_id} not found in cache")
                return {}
            
            stats = self._cache[file_id].get('stats', {})
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving stats: {e}", exc_info=True)
            return {}
    
    async def get_file_info(self, file_id: Optional[str] = None) -> Optional[Dict]:
        """Get file metadata"""
        # If no file_id provided, use current file
        if not file_id:
            file_id = self._current_file_id
        
        if not file_id:
            logger.warning("No file_id provided and no current file")
            return None
        
        try:
            # Check cache
            if file_id not in self._cache:
                logger.warning(f"File {file_id} not found in cache")
                return None
            
            return self._cache[file_id].get('info')
            
        except Exception as e:
            logger.error(f"Error retrieving file info: {e}", exc_info=True)
            return None
    
    async def get_files_list(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all stored files"""
        try:
            files = []
            for file_id, data in self._cache.items():
                if 'info' in data:
                    files.append(data['info'])
            
            # Sort by upload_time (descending)
            files.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
            return files[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Error retrieving files list: {e}", exc_info=True)
            return []
    
    async def delete_file(self, file_id: str):
        """Delete file and associated data"""
        try:
            if file_id in self._cache:
                del self._cache[file_id]
            logger.info(f"Deleted file {file_id}")
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}", exc_info=True)
    
    async def count_packets(self, file_id: Optional[str] = None) -> int:
        """Count total packets for a file"""
        if not file_id:
            return 0
        
        try:
            if file_id not in self._cache:
                return 0
            
            packets_data = self._cache[file_id].get('packets', [])
            return len(packets_data)
            
        except Exception as e:
            logger.error(f"Error counting packets: {e}", exc_info=True)
            return 0


# Global in-memory storage instance
in_memory_storage = InMemoryStorage()

