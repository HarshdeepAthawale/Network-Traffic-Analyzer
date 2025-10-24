"""
Summary statistics API endpoint
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from collections import Counter
import statistics

from fastapi import APIRouter, HTTPException

from app.models.packet import (
    SummaryResponse, Overview, ProtocolDistribution, 
    PacketsPerSecond, SizeHistogram
)
from app.services.storage import storage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(file_id: str = None):
    """
    Get summary statistics for parsed PCAP file
    
    Args:
        file_id: Optional file ID, uses current file if not provided
        
    Returns:
        Summary statistics
    """
    try:
        # Get stats from storage
        stats = storage.get_stats(file_id)
        packets = storage.get_packets(file_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail="No parsed data found. Please upload a PCAP file first."
            )
        
        # Create overview
        overview = Overview(
            totalPackets=stats.get('total_packets', 0),
            totalBytes=stats.get('total_bytes', 0),
            uniqueIps=stats.get('unique_ips', 0),
            uniqueMacs=stats.get('unique_macs', 0),
            durationSec=round(stats.get('duration', 0), 2)
        )
        
        # Create protocol distribution
        protocol_dist = _calculate_protocol_distribution(stats.get('protocols', {}))
        
        # Create packets per second
        pps_data = _calculate_pps(packets, stats)
        
        # Create size histogram
        size_hist = _calculate_size_histogram(stats.get('packet_sizes', []))
        
        return SummaryResponse(
            overview=overview,
            protocolDistribution=protocol_dist,
            pps=pps_data,
            sizeHistogram=size_hist
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


def _calculate_protocol_distribution(protocols: Counter) -> List[ProtocolDistribution]:
    """Calculate protocol distribution percentages"""
    total = sum(protocols.values())
    if total == 0:
        return []
    
    distribution = []
    for protocol, count in protocols.most_common():
        pct = round((count / total) * 100, 1)
        distribution.append(ProtocolDistribution(
            protocol=protocol,
            count=count,
            pct=pct
        ))
    
    return distribution


def _calculate_pps(packets: List, stats: Dict) -> List[PacketsPerSecond]:
    """Calculate packets per second over time"""
    if not packets or stats.get('duration', 0) == 0:
        return []
    
    # Group packets by second
    start_time = stats.get('start_time')
    if not start_time:
        return []
    
    # Create time buckets with higher precision (every 5 seconds for better visualization)
    duration = int(stats.get('duration', 0)) + 1
    bucket_size = max(1, duration // 20)  # Create about 20 data points
    buckets = {}
    
    # Fill buckets
    for packet in packets:
        try:
            packet_time = datetime.strptime(packet.ts, "%Y-%m-%d %H:%M:%S.%f")
            elapsed = (packet_time - start_time).total_seconds()
            bucket = int(elapsed // bucket_size) * bucket_size
            
            if bucket not in buckets:
                buckets[bucket] = {'packets': 0, 'bytes': 0}
            buckets[bucket]['packets'] += 1
            buckets[bucket]['bytes'] += packet.size
        except Exception as e:
            logger.warning(f"Error processing packet timestamp: {e}")
    
    # Create PPS data points with actual timestamps
    pps_data = []
    for bucket_time in sorted(buckets.keys()):
        actual_time = start_time + timedelta(seconds=bucket_time)
        # Show more detailed timestamp if duration is short, otherwise just time
        if duration < 3600:  # Less than 1 hour
            time_str = actual_time.strftime("%H:%M:%S")
        else:  # More than 1 hour, show date and time
            time_str = actual_time.strftime("%m/%d %H:%M:%S")
        pps_data.append(PacketsPerSecond(
            t=time_str,
            pps=buckets[bucket_time]['packets'],
            bps=buckets[bucket_time]['bytes']
        ))
    
    return pps_data


def _calculate_size_histogram(packet_sizes: List[int]) -> List[SizeHistogram]:
    """Calculate packet size distribution histogram"""
    if not packet_sizes:
        return []
    
    # Define size ranges
    ranges = [
        (0, 64, "0-64"),
        (65, 512, "65-512"),
        (513, 1500, "513-1500"),
        (1501, float('inf'), ">1500")
    ]
    
    histogram = []
    
    for min_size, max_size, label in ranges:
        # Filter packets in this range
        range_packets = [s for s in packet_sizes if min_size <= s <= max_size]
        
        if range_packets:
            histogram.append(SizeHistogram(
                range=label,
                count=len(range_packets),
                min=min(range_packets),
                max=max(range_packets),
                mean=round(statistics.mean(range_packets), 1),
                median=round(statistics.median(range_packets), 1),
                p95=round(statistics.quantiles(range_packets, n=20)[18], 1)  # 95th percentile
            ))
        else:
            histogram.append(SizeHistogram(
                range=label,
                count=0,
                min=0,
                max=0,
                mean=0,
                median=0,
                p95=0
            ))
    
    return histogram
