"""
MongoDB service for storing file metadata
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDBService:
    """MongoDB service for file metadata storage"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Build connection options
            connection_options = {
                "maxPoolSize": 50,
                "minPoolSize": 10,
                "serverSelectionTimeoutMS": 10000,  # Increased timeout
                "socketTimeoutMS": 30000,
                "connectTimeoutMS": 20000,
                "retryWrites": True,
            }
            
            # For mongodb+srv, let Motor handle SSL automatically
            # Don't add tls parameters as they conflict with SRV DNS records
            
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                **connection_options
            )
            self.db = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def store_file_metadata(
        self,
        file_id: str,
        filename: str,
        cloudinary_url: str,
        size: int,
        user: str = "unknown"
    ) -> str:
        """Store file metadata in MongoDB"""
        try:
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "url": cloudinary_url,
                "size": size,
                "user": user,
                "upload_date": datetime.utcnow(),
                "has_parsed_data": False
            }
            
            result = await self.db.files.insert_one(metadata)
            logger.info(f"Stored file metadata for {filename} with ID: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error storing file metadata: {e}", exc_info=True)
            raise
    
    async def update_parsed_data_status(
        self,
        file_id: str,
        packet_count: int,
        stats: Dict
    ):
        """Update file with parsed data status"""
        try:
            await self.db.files.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "has_parsed_data": True,
                        "packet_count": packet_count,
                        "upload_date": datetime.utcnow(),  # Update timestamp
                        **{f"stats.{k}": v for k, v in stats.items()}
                    }
                }
            )
            logger.info(f"Updated parsed data status for file: {file_id}")
            
        except Exception as e:
            logger.error(f"Error updating parsed data status: {e}", exc_info=True)
            raise
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Get file metadata by file_id"""
        try:
            metadata = await self.db.files.find_one({"file_id": file_id})
            if metadata:
                # Convert ObjectId to string if present
                if "_id" in metadata:
                    metadata["_id"] = str(metadata["_id"])
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}", exc_info=True)
            return None
    
    async def list_files(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all stored files with pagination"""
        try:
            cursor = self.db.files.find().sort("upload_date", -1).skip(skip).limit(limit)
            files = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for file in files:
                if "_id" in file:
                    file["_id"] = str(file["_id"])
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}", exc_info=True)
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file metadata"""
        try:
            result = await self.db.files.delete_one({"file_id": file_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}", exc_info=True)
            return False


# Global MongoDB service instance
mongodb_service = MongoDBService()

