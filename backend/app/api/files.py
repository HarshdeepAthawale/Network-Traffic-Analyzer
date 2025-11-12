"""
Files API endpoint - list and manage uploaded files
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.services.storage import storage

logger = logging.getLogger(__name__)

router = APIRouter()


class FileMetadata(BaseModel):
    """File metadata model"""

    file_id: str
    filename: str
    size: int
    user: str
    upload_date: Optional[str] = None
    last_processed_at: Optional[str] = None
    has_parsed_data: bool = False
    packet_count: int = 0


class FilesListResponse(BaseModel):
    """Files list response"""
    files: List[FileMetadata]
    total: int


@router.get("/files", response_model=FilesListResponse)
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List all uploaded files with pagination
    
    Args:
        skip: Number of files to skip
        limit: Maximum number of files to return (1-1000)
        
    Returns:
        List of file metadata
    """
    try:
        files = await storage.list_files(skip=skip, limit=limit)
        
        # Convert to response format
        file_list = []
        for file in files:
            metadata = FileMetadata(
                file_id=file.get("file_id", ""),
                filename=file.get("filename", ""),
                size=file.get("size", 0),
                user=file.get("user", "unknown"),
                upload_date=file.get("upload_date", ""),
                last_processed_at=file.get("last_processed_at"),
                has_parsed_data=file.get("has_parsed_data", False),
                packet_count=file.get("packet_count", 0)
            )
            file_list.append(metadata)
        
        return FilesListResponse(
            files=file_list,
            total=len(file_list)
        )
        
    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )


@router.get("/files/{file_id}", response_model=FileMetadata)
async def get_file(file_id: str):
    """
    Get file metadata by ID
    
    Args:
        file_id: File ID
        
    Returns:
        File metadata
    """
    try:
        file_metadata = await storage.get_file_info(file_id)
        
        if not file_metadata:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        return FileMetadata(
            file_id=file_metadata.get("file_id", ""),
            filename=file_metadata.get("filename", ""),
            size=file_metadata.get("size", 0),
            user=file_metadata.get("user", "unknown"),
            upload_date=file_metadata.get("upload_date", ""),
            last_processed_at=file_metadata.get("last_processed_at"),
            has_parsed_data=file_metadata.get("has_parsed_data", False),
            packet_count=file_metadata.get("packet_count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting file: {str(e)}"
        )

