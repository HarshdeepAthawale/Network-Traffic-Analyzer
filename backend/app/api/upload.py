"""
File upload API endpoint
"""
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.models.packet import UploadResponse
from app.services.pcap_parser import PCAPParser
from app.services.storage import storage
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pcap(file: UploadFile = File(...)):
    """
    Upload and parse a PCAP file
    
    Args:
        file: PCAP or PCAPNG file
        
    Returns:
        Upload response with file ID
    """
    try:
        # Validate file extension
        if not file.filename.endswith(('.pcap', '.pcapng')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .pcap and .pcapng files are supported."
            )
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        logger.info(f"Uploading file: {file.filename}, size: {file_size} bytes")
        
        # Parse the PCAP file
        parser = PCAPParser()
        packets, stats = await parser.parse_file(file_content)
        
        if not packets:
            raise HTTPException(
                status_code=400,
                detail="No packets found in the file"
            )
        
        # Store the parsed data
        file_id = storage.store_file(file.filename, packets, stats)
        
        return UploadResponse(
            success=True,
            fileId=file_id,
            message=f"Successfully parsed {len(packets)} packets from {file.filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
