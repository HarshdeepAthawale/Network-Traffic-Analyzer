"""
Cloudinary storage service for parsed PCAP data
"""
import logging
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

import cloudinary
import cloudinary.uploader
import cloudinary.api

from app.models.packet import Packet
from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudinaryStorage:
    """Cloudinary storage for parsed PCAP data"""
    
    def __init__(self):
        self.is_initialized = False
        self._cache = {}  # In-memory cache for parsed data
        
    def _initialize(self):
        """Initialize Cloudinary connection"""
        if self.is_initialized:
            return
            
        try:
            if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY or not settings.CLOUDINARY_API_SECRET:
                logger.warning("Cloudinary credentials are not configured. Cloudinary features will be unavailable.")
                self.is_initialized = False
                return
            
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            
            self.is_initialized = True
            logger.info("Cloudinary initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Cloudinary: {e}", exc_info=True)
            self.is_initialized = False
    
    async def connect(self):
        """Connect to Cloudinary (for compatibility with existing code)"""
        self._initialize()
    
    async def disconnect(self):
        """Disconnect from Cloudinary (no-op)"""
        self.is_initialized = False
        logger.info("Disconnected from Cloudinary")
    
    async def store_file(self, filename: str, packets: List[Packet], stats: Dict) -> str:
        """Store parsed file data"""
        if not self.is_initialized:
            self._initialize()
        
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
            
            # Store in Cloudinary if initialized
            if self.is_initialized:
                try:
                    folder = f"network_analyzer/{file_id}"
                    
                    # Upload file info
                    file_info_json = json.dumps(file_info)
                    cloudinary.uploader.upload(
                        file_info_json.encode('utf-8'),
                        public_id=f"{folder}/info",
                        resource_type="raw",
                        overwrite=True
                    )
                    
                    # Upload packets (as JSON)
                    packets_json = json.dumps(packets_data)
                    cloudinary.uploader.upload(
                        packets_json.encode('utf-8'),
                        public_id=f"{folder}/packets",
                        resource_type="raw",
                        overwrite=True
                    )
                    
                    # Upload stats
                    stats_json = json.dumps(stats_data, default=str)
                    cloudinary.uploader.upload(
                        stats_json.encode('utf-8'),
                        public_id=f"{folder}/stats",
                        resource_type="raw",
                        overwrite=True
                    )
                except Exception as e:
                    logger.warning(f"Error uploading to Cloudinary: {e}. Using in-memory storage only.")
            
            # Store in memory cache for quick access (always)
            self._cache[file_id] = {
                'info': file_info,
                'packets': packets_data,
                'stats': stats_data
            }
            
            logger.info(f"Stored file {filename} with ID {file_id}, {len(packets)} packets")
            return file_id
            
        except Exception as e:
            logger.error(f"Error storing file: {e}", exc_info=True)
            raise
    
    async def get_packets(self, file_id: Optional[str] = None, skip: int = 0, limit: int = 1000) -> List[Packet]:
        """Get packets for a file"""
        if not file_id:
            return []
        
        try:
            # Check cache first
            if file_id in self._cache:
                packets_data = self._cache[file_id]['packets']
            else:
                if not self.is_initialized:
                    logger.warning(f"Cloudinary not initialized and file {file_id} not in cache")
                    return []
                
                # Load from Cloudinary
                folder = f"network_analyzer/{file_id}"
                result = cloudinary.uploader.download(
                    f"{folder}/packets",
                    resource_type="raw"
                )
                
                packets_data = json.loads(result)
                # Cache for future use
                if file_id not in self._cache:
                    self._cache[file_id] = {'packets': packets_data}
            
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
        if not file_id:
            return {}
        
        try:
            # Check cache first
            if file_id in self._cache:
                stats = self._cache[file_id].get('stats', {})
                if stats:
                    return stats
            
            if not self.is_initialized:
                logger.warning(f"Cloudinary not initialized and file {file_id} not in cache")
                return {}
            
            # Load from Cloudinary
            folder = f"network_analyzer/{file_id}"
            result = cloudinary.uploader.download(
                f"{folder}/stats",
                resource_type="raw"
            )
            
            stats = json.loads(result)
            
            # Cache for future use
            if file_id not in self._cache:
                self._cache[file_id] = {'stats': stats}
            else:
                self._cache[file_id]['stats'] = stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving stats: {e}", exc_info=True)
            return {}
    
    async def get_file_info(self, file_id: Optional[str] = None) -> Optional[Dict]:
        """Get file metadata"""
        if not file_id:
            return None
        
        try:
            # Check cache first
            if file_id in self._cache:
                return self._cache[file_id].get('info')
            
            if not self.is_initialized:
                logger.warning(f"Cloudinary not initialized and file {file_id} not in cache")
                return None
            
            # Load from Cloudinary
            folder = f"network_analyzer/{file_id}"
            result = cloudinary.uploader.download(
                f"{folder}/info",
                resource_type="raw"
            )
            
            file_info = json.loads(result)
            
            # Cache for future use
            if file_id not in self._cache:
                self._cache[file_id] = {'info': file_info}
            else:
                self._cache[file_id]['info'] = file_info
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error retrieving file info: {e}", exc_info=True)
            return None
    
    async def get_files_list(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all stored files"""
        try:
            # If not using Cloudinary, return files from cache
            if not self.is_initialized:
                files = []
                for file_id, data in self._cache.items():
                    if 'info' in data:
                        files.append(data['info'])
                
                # Sort by upload_time (descending)
                files.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
                return files[skip:skip + limit]
            
            # Get all files from Cloudinary
            result = cloudinary.api.resources(
                type="upload",
                resource_type="raw",
                prefix="network_analyzer/",
                max_results=1000
            )
            
            files = []
            seen_ids = set()
            
            for resource in result.get('resources', []):
                public_id = resource['public_id']
                # Extract file_id from path like "network_analyzer/{file_id}/info"
                parts = public_id.split('/')
                if len(parts) >= 3 and parts[2] == 'info':
                    file_id = parts[1]
                    if file_id not in seen_ids:
                        seen_ids.add(file_id)
                        file_info = await self.get_file_info(file_id)
                        if file_info:
                            files.append(file_info)
            
            # Sort by upload_time (descending)
            files.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
            
            # Apply pagination
            return files[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Error retrieving files list: {e}", exc_info=True)
            return []
    
    async def delete_file(self, file_id: str):
        """Delete file and associated data"""
        try:
            # Always remove from cache
            if file_id in self._cache:
                del self._cache[file_id]
            
            # Delete from Cloudinary if initialized
            if self.is_initialized:
                folder = f"network_analyzer/{file_id}"
                
                # Delete all resources in the folder
                cloudinary.api.delete_resources(
                    [f"{folder}/info", f"{folder}/packets", f"{folder}/stats"],
                    resource_type="raw"
                )
            
            logger.info(f"Deleted file {file_id} and associated data")
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}", exc_info=True)
    
    async def count_packets(self, file_id: Optional[str] = None) -> int:
        """Count total packets for a file"""
        if not file_id:
            return 0
        
        try:
            # Check cache first
            if file_id in self._cache:
                packets_data = self._cache[file_id].get('packets')
                if packets_data:
                    return len(packets_data)
            
            if not self.is_initialized:
                logger.warning(f"Cloudinary not initialized and file {file_id} not in cache")
                return 0
            
            # Load from Cloudinary to count
            folder = f"network_analyzer/{file_id}"
            result = cloudinary.uploader.download(
                f"{folder}/packets",
                resource_type="raw"
            )
            
            packets_data = json.loads(result)
            
            # Cache for future use
            if file_id not in self._cache:
                self._cache[file_id] = {'packets': packets_data}
            else:
                self._cache[file_id]['packets'] = packets_data
            
            return len(packets_data)
            
        except Exception as e:
            logger.error(f"Error counting packets: {e}", exc_info=True)
            return 0


# Global storage instance
cloudinary_storage = CloudinaryStorage()

