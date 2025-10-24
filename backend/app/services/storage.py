"""
Storage service for parsed PCAP data
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import uuid
from collections import defaultdict

from app.models.packet import Packet
from app.core.config import settings

logger = logging.getLogger(__name__)


class InMemoryStorage:
    """In-memory storage for parsed PCAP data"""
    
    def __init__(self):
        self.files: Dict[str, Dict] = {}  # fileId -> file metadata
        self.packets: Dict[str, List[Packet]] = {}  # fileId -> packets
        self.stats: Dict[str, Dict] = {}  # fileId -> statistics
        self.current_file_id: Optional[str] = None
    
    def store_file(self, filename: str, packets: List[Packet], stats: Dict) -> str:
        """Store parsed file data - clears previous data to prevent history"""
        # Clear all previous data to prevent showing history
        self.clear()
        
        file_id = str(uuid.uuid4())
        
        # Store metadata
        self.files[file_id] = {
            'id': file_id,
            'filename': filename,
            'upload_time': datetime.now(timezone(timedelta(hours=5, minutes=30))),
            'packet_count': len(packets),
            'total_bytes': stats.get('total_bytes', 0)
        }
        
        # Store packets and stats
        self.packets[file_id] = packets
        self.stats[file_id] = stats
        
        # Set as current file
        self.current_file_id = file_id
        
        logger.info(f"Stored file {filename} with ID {file_id}, {len(packets)} packets (cleared previous data)")
        return file_id
    
    def get_packets(self, file_id: Optional[str] = None) -> List[Packet]:
        """Get packets for a file"""
        fid = file_id or self.current_file_id
        if fid and fid in self.packets:
            return self.packets[fid]
        return []
    
    def get_stats(self, file_id: Optional[str] = None) -> Dict:
        """Get statistics for a file"""
        fid = file_id or self.current_file_id
        if fid and fid in self.stats:
            return self.stats[fid]
        return {}
    
    def get_file_info(self, file_id: Optional[str] = None) -> Optional[Dict]:
        """Get file metadata"""
        fid = file_id or self.current_file_id
        if fid and fid in self.files:
            return self.files[fid]
        return None
    
    def clear(self):
        """Clear all stored data"""
        self.files.clear()
        self.packets.clear()
        self.stats.clear()
        self.current_file_id = None


# Global storage instance
storage = InMemoryStorage()
