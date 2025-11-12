"""
PCAP file storage service backed by MongoDB metadata.
"""
import logging
import uuid
from typing import Dict, Optional

from app.services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)


class PCAPFileStorage:
    """Service for tracking uploaded PCAP files."""

    async def upload_pcap_file(
        self,
        file_content: bytes,
        filename: str,
        user: str = "unknown",
    ) -> Dict[str, str]:
        """
        Store PCAP metadata in MongoDB.

        Args:
            file_content: Raw bytes of the PCAP file (retained for future storage options).
            filename: Original filename.
            user: User who uploaded the file.

        Returns:
            Dict with file_id, filename, and size.
        """
        file_id = str(uuid.uuid4())
        file_size = len(file_content)

        await mongodb_service.create_file_record(
            file_id=file_id,
            filename=filename,
            size=file_size,
            user=user,
        )

        logger.info("Registered PCAP file %s (%s) in MongoDB", filename, file_id)
        return {
            "file_id": file_id,
            "filename": filename,
            "size": file_size,
        }

    async def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file metadata from MongoDB."""
        return await mongodb_service.get_file_metadata(file_id)

    async def delete_file(self, file_id: str) -> bool:
        """Delete file metadata and associated parsed data."""
        return await mongodb_service.delete_file(file_id)


pcap_file_storage = PCAPFileStorage()


