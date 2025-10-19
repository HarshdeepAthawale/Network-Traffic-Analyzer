"""
Packet data models
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class PacketLayers(BaseModel):
    """Packet layer information"""
    ethernet: Optional[Dict[str, Any]] = None
    ip: Optional[Dict[str, Any]] = None
    transport: Optional[Dict[str, Any]] = None
    app: Optional[Dict[str, Any]] = None


class Packet(BaseModel):
    """Individual packet model"""
    id: str
    ts: str  # Timestamp string
    src: str  # Source IP
    dst: str  # Destination IP
    proto: str  # Protocol name
    size: int  # Packet size in bytes
    info: str  # Brief info about the packet
    layers: PacketLayers
    hex: Optional[str] = None  # Hex dump


class PacketListResponse(BaseModel):
    """Paginated packet list response"""
    items: List[Packet]
    total: int
    page: int
    perPage: int = Field(alias="per_page")


class ProtocolDistribution(BaseModel):
    """Protocol distribution statistics"""
    protocol: str
    count: int
    pct: float  # Percentage


class PacketsPerSecond(BaseModel):
    """Packets per second data point"""
    t: str  # Time string
    pps: int  # Packets per second
    bps: int  # Bytes per second


class SizeHistogram(BaseModel):
    """Packet size histogram bin"""
    range: str
    count: int
    min: int
    max: int
    mean: float
    median: float
    p95: float


class Overview(BaseModel):
    """Overview statistics"""
    totalPackets: int
    totalBytes: int
    uniqueIps: int
    uniqueMacs: int
    durationSec: float


class SummaryResponse(BaseModel):
    """Summary API response"""
    overview: Overview
    protocolDistribution: List[ProtocolDistribution]
    pps: List[PacketsPerSecond]
    sizeHistogram: List[SizeHistogram]


class IpMacMapping(BaseModel):
    """IP-MAC mapping with statistics"""
    ip: str
    mac: str
    host: Optional[str] = None
    packets: int
    bytes: int
    vendor: Optional[str] = None
    user_name: Optional[str] = None


class IpMacMapResponse(BaseModel):
    """IP-MAC map API response"""
    items: List[IpMacMapping]


class UploadResponse(BaseModel):
    """File upload response"""
    success: bool
    fileId: str
    message: str
