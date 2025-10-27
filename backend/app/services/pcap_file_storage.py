"""
PCAP file storage service - uploads raw .pcap files to Cloudinary
"""
import logging
import uuid
from typing import Optional, Dict
from datetime import datetime

import cloudinary
import cloudinary.uploader

from app.services.mongodb_service import mongodb_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class PCAPFileStorage:
    """Service for storing raw .pcap files in Cloudinary"""
    
    def __init__(self):
        self.is_initialized = False
    
    def _initialize(self):
        """Initialize Cloudinary connection"""
        if self.is_initialized:
            return
        
        try:
            if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY or not settings.CLOUDINARY_API_SECRET:
                logger.warning("Cloudinary credentials are not configured. File upload features will be unavailable.")
                self.is_initialized = False
                return
            
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            
            self.is_initialized = True
            logger.info("Cloudinary initialized for file storage")
            
        except Exception as e:
            logger.error(f"Error initializing Cloudinary: {e}", exc_info=True)
            self.is_initialized = False
    
    async def upload_pcap_file(
        self,
        file_content: bytes,
        filename: str,
        user: str = "unknown"
    ) -> Dict[str, str]:
        """
        Upload raw .pcap file to Cloudinary and store metadata in MongoDB
        
        Args:
            file_content: Raw bytes of the pcap file
            filename: Original filename
            user: User who uploaded the file
            
        Returns:
            Dict with file_id and cloudinary_url
        """
        if not self.is_initialized:
            self._initialize()
        
        if not self.is_initialized:
            raise RuntimeError("Cloudinary not initialized. Please check your Cloudinary credentials.")
        
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Upload raw pcap file to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file_content,
                public_id=f"pcap_files/{file_id}",
                resource_type="raw",  # Required for .pcap files
                folder="network_analyzer",
                overwrite=False
            )
            
            cloudinary_url = upload_result["secure_url"]
            file_size = len(file_content)
            
            # Store metadata in MongoDB
            await mongodb_service.store_file_metadata(
                file_id=file_id,
                filename=filename,
                cloudinary_url=cloudinary_url,
                size=file_size,
                user=user
            )
            
            logger.info(f"Uploaded .pcap file {filename} to Cloudinary with ID: {file_id}")
            
            return {
                "file_id": file_id,
                "url": cloudinary_url,
                "filename": filename,
                "size": file_size
            }
            
        except Exception as e:
            logger.error(f"Error uploading .pcap file to Cloudinary: {e}", exc_info=True)
            raise
    
    async def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file info from MongoDB"""
        try:
            return await mongodb_service.get_file_metadata(file_id)
        except Exception as e:
            logger.error(f"Error getting file info: {e}", exc_info=True)
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from both Cloudinary and MongoDB"""
        try:
            # Get file info first
            file_info = await mongodb_service.get_file_metadata(file_id)
            
            # Delete from Cloudinary
            if file_info:
                public_id = f"network_analyzer/pcap_files/{file_id}"
                try:
                    cloudinary.uploader.destroy(public_id, resource_type="raw")
                    logger.info(f"Deleted file from Cloudinary: {file_id}")
                except Exception as e:
                    logger.warning(f"Could not delete from Cloudinary: {e}")
            
            # Delete from MongoDB
            deleted = await mongodb_service.delete_file(file_id)
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}", exc_info=True)
            return False


# Global file storage instance
pcap_file_storage = PCAPFileStorage()

