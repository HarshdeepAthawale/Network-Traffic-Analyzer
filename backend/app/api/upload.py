"""
File upload API endpoint
"""
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.models.packet import UploadResponse
from app.services.pcap_parser import PCAPParser
from app.services.pcap_file_storage import pcap_file_storage
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
        
        # Step 1: Register the file metadata in MongoDB
        file_metadata = await pcap_file_storage.upload_pcap_file(
            file_content=file_content,
            filename=file.filename,
            user="web_upload"  # You can get this from request later
        )
        
        file_id = file_metadata["file_id"]
        logger.info(f"Registered file in MongoDB with ID: {file_id}")
        
        # Step 2: Parse the PCAP file
        parser = PCAPParser()
        packets, stats = await parser.parse_file(file_content)
        
        if not packets:
            raise HTTPException(
                status_code=400,
                detail="No packets found in the file"
            )
        
        # Step 3: Store the parsed data (packets + stats) in MongoDB
        await storage.store_file(file_id, packets, stats)
        logger.info(f"Stored parsed data for file ID: {file_id}")
        
        return UploadResponse(
            success=True,
            fileId=file_id,
            message=f"Successfully uploaded and parsed {len(packets)} packets from {file.filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
