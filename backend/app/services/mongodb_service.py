"""
MongoDB service for storing file metadata, parsed packets, and statistics.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo import ASCENDING

from app.core.config import settings
from app.models.packet import Packet

logger = logging.getLogger(__name__)


class MongoDBService:
    """MongoDB service for file storage"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.files_collection: Optional[AsyncIOMotorCollection] = None
        self.packets_collection: Optional[AsyncIOMotorCollection] = None
        self.stats_collection: Optional[AsyncIOMotorCollection] = None

    async def connect(self):
        """Connect to MongoDB and prepare collections."""
        if self.client:
            return

        try:
            connection_options = {
                "maxPoolSize": 50,
                "minPoolSize": 10,
                "serverSelectionTimeoutMS": 10000,
                "socketTimeoutMS": 30000,
                "connectTimeoutMS": 20000,
                "retryWrites": True,
            }

            self.client = AsyncIOMotorClient(settings.MONGODB_URI, **connection_options)
            self.db = self.client[settings.MONGODB_DATABASE]
            await self.client.admin.command("ping")

            self.files_collection = self.db[settings.MONGODB_FILES_COLLECTION]
            self.packets_collection = self.db[settings.MONGODB_PACKETS_COLLECTION]
            self.stats_collection = self.db[settings.MONGODB_STATS_COLLECTION]

            await self._ensure_indexes()
            logger.info("Connected to MongoDB successfully")
        except Exception as exc:
            logger.error("Failed to connect to MongoDB: %s", exc)
            raise

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.files_collection = None
            self.packets_collection = None
            self.stats_collection = None
            logger.info("Disconnected from MongoDB")

    async def create_file_record(
        self,
        file_id: str,
        filename: str,
        size: int,
        user: str = "unknown",
    ) -> Dict[str, Any]:
        """Create a file metadata record."""
        metadata = {
            "file_id": file_id,
            "filename": filename,
            "size": size,
            "user": user,
            "upload_date": datetime.utcnow(),
            "has_parsed_data": False,
            "packet_count": 0,
        }

        try:
            await self.files_collection.insert_one(metadata)
            logger.info("Stored file metadata for %s (%s)", filename, file_id)
            return metadata
        except Exception as exc:
            logger.error("Error storing file metadata: %s", exc, exc_info=True)
            raise

    async def store_parsed_data(
        self,
        file_id: str,
        packets: List[Packet],
        stats: Dict[str, Any],
    ) -> None:
        """Persist parsed packets and statistics for a file."""
        if not packets:
            return

        try:
            packet_docs = []
            for index, packet in enumerate(packets):
                doc = packet.model_dump()
                doc.update(
                    {
                        "file_id": file_id,
                        "packet_index": index,
                        "ingested_at": datetime.utcnow(),
                    }
                )
                packet_docs.append(doc)

            if packet_docs:
                await self.packets_collection.delete_many({"file_id": file_id})
                await self.packets_collection.insert_many(packet_docs, ordered=True)

            stats_doc = self._serialize_stats(stats)
            stats_doc.update(
                {
                    "file_id": file_id,
                    "updated_at": datetime.utcnow(),
                    "packet_count": len(packets),
                }
            )

            await self.stats_collection.update_one(
                {"file_id": file_id},
                {"$set": stats_doc},
                upsert=True,
            )

            await self.files_collection.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "has_parsed_data": True,
                        "packet_count": len(packets),
                        "last_processed_at": datetime.utcnow(),
                    }
                },
            )

            logger.info(
                "Persisted parsed data for file %s (%s packets)",
                file_id,
                len(packets),
            )
        except Exception as exc:
            logger.error("Error storing parsed data: %s", exc, exc_info=True)
            raise

    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata for a specific file."""
        if not self.files_collection:
            return None

        metadata = await self.files_collection.find_one({"file_id": file_id})
        if not metadata:
            return None

        metadata["_id"] = str(metadata.get("_id"))
        metadata["upload_date"] = self._format_datetime(metadata.get("upload_date"))
        metadata["last_processed_at"] = self._format_datetime(
            metadata.get("last_processed_at")
        )
        return metadata

    async def list_files(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List stored file metadata."""
        if not self.files_collection:
            return []

        cursor = (
            self.files_collection.find()
            .sort("upload_date", -1)
            .skip(skip)
            .limit(limit)
        )
        files = await cursor.to_list(length=limit)

        for item in files:
            item["_id"] = str(item.get("_id"))
            item["upload_date"] = self._format_datetime(item.get("upload_date"))
            item["last_processed_at"] = self._format_datetime(
                item.get("last_processed_at")
            )
        return files

    async def delete_file(self, file_id: str) -> bool:
        """Delete all information for a file."""
        if not self.files_collection:
            return False

        try:
            await self.packets_collection.delete_many({"file_id": file_id})
            await self.stats_collection.delete_many({"file_id": file_id})
            result = await self.files_collection.delete_one({"file_id": file_id})
            return result.deleted_count > 0
        except Exception as exc:
            logger.error("Error deleting file %s: %s", file_id, exc, exc_info=True)
            return False

    async def get_packets(
        self,
        file_id: str,
        skip: int = 0,
        limit: int = 100,
        protocol: Optional[str] = None,
        ip_query: Optional[str] = None,
    ) -> Tuple[List[Packet], int]:
        """Retrieve packets for pagination and filtering."""
        if not self.packets_collection:
            return [], 0

        query: Dict[str, Any] = {"file_id": file_id}

        if protocol:
            query["proto"] = protocol.upper()

        if ip_query:
            query["$or"] = [
                {"src": {"$regex": ip_query, "$options": "i"}},
                {"dst": {"$regex": ip_query, "$options": "i"}},
            ]

        total = await self.packets_collection.count_documents(query)

        cursor = (
            self.packets_collection.find(query)
            .sort("packet_index", ASCENDING)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)

        packets = [self._map_packet(doc) for doc in docs]
        return packets, total

    async def get_all_packets(self, file_id: str) -> List[Packet]:
        """Return all packets for a file (used for summary calculations)."""
        if not self.packets_collection:
            return []

        cursor = self.packets_collection.find({"file_id": file_id}).sort(
            "packet_index", ASCENDING
        )
        docs = await cursor.to_list(length=None)
        return [self._map_packet(doc) for doc in docs]

    async def get_stats(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Fetch stored statistics for a file."""
        if not self.stats_collection:
            return None

        stats = await self.stats_collection.find_one({"file_id": file_id})
        if not stats:
            return None

        stats["_id"] = str(stats.get("_id"))
        stats["updated_at"] = self._format_datetime(stats.get("updated_at"))
        return stats

    async def get_latest_file_id(self) -> Optional[str]:
        """Return the most recently processed file ID."""
        if not self.files_collection:
            return None

        result = await self.files_collection.find_one(
            {"has_parsed_data": True},
            sort=[("last_processed_at", -1)],
        )
        if not result:
            return None
        return result.get("file_id")

    async def _ensure_indexes(self):
        """Create required indexes on first connection."""
        if not self.files_collection or not self.packets_collection:
            return

        await self.files_collection.create_index("file_id", unique=True)
        await self.files_collection.create_index("upload_date")

        await self.packets_collection.create_index(
            [("file_id", ASCENDING), ("packet_index", ASCENDING)],
            unique=True,
        )
        await self.packets_collection.create_index(
            [("file_id", ASCENDING), ("proto", ASCENDING)]
        )
        await self.packets_collection.create_index(
            [("file_id", ASCENDING), ("src", ASCENDING)]
        )
        await self.packets_collection.create_index(
            [("file_id", ASCENDING), ("dst", ASCENDING)]
        )

        await self.stats_collection.create_index("file_id", unique=True)

    @staticmethod
    def _serialize_stats(stats: Dict[str, Any]) -> Dict[str, Any]:
        """Convert parser stats into JSON-friendly structures."""
        serialized: Dict[str, Any] = {}
        for key, value in stats.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif hasattr(value, "items"):
                serialized[key] = {}
                for sub_key, sub_val in value.items():
                    serialized[key][sub_key] = sub_val
            elif hasattr(value, "most_common"):
                serialized[key] = dict(value)
            else:
                serialized[key] = value
        return serialized

    @staticmethod
    def _map_packet(doc: Dict[str, Any]) -> Packet:
        """Transform a MongoDB document into a Packet model."""
        packet_data = {key: value for key, value in doc.items() if key not in {"_id", "file_id", "packet_index", "ingested_at"}}
        packet_data["layers"] = packet_data.get("layers", {})  # Ensure nested structure
        return Packet.model_validate(packet_data)

    @staticmethod
    def _format_datetime(value: Any) -> Optional[str]:
        """Convert datetime objects to ISO strings."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value


# Global MongoDB service instance
mongodb_service = MongoDBService()


