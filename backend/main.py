"""
FastAPI Backend for Network Traffic Analyzer
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api import upload, summary, packets, ip_mac_map
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info("Starting Network Traffic Analyzer backend...")
    
    # Initialize storage
    try:
        from app.services.storage import storage
        logger.info("Storage initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize storage: {e}")
    
    yield
    
    logger.info("Shutting down Network Traffic Analyzer backend...")


app = FastAPI(
    title="Network Traffic Analyzer API",
    description="Backend API for analyzing PCAP network capture files",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# Parse CORS origins from settings (comma-separated string to list)
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(summary.router, prefix="/api", tags=["summary"])
app.include_router(packets.router, prefix="/api", tags=["packets"])
app.include_router(ip_mac_map.router, prefix="/api", tags=["ip-mac"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Network Traffic Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "summary": "/api/summary",
            "packets": "/api/packets",
            "ip_mac_map": "/api/ip-mac-map"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
