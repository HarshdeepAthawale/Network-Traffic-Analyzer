"""
PCAP file parser service using Scapy
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
import hashlib
import io

from scapy.all import rdpcap, sniff, Packet as ScapyPacket
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether, ARP
from scapy.layers.dns import DNS
from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse

from app.models.packet import Packet, PacketLayers
from app.services.vendor_lookup import get_vendor_by_mac
from app.services.dns_resolver import resolve_hostname

logger = logging.getLogger(__name__)


class PCAPParser:
    """PCAP file parser"""
    
    def __init__(self):
        self.packets: List[Packet] = []
        self.raw_packets: List[ScapyPacket] = []
        self.stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'start_time': None,
            'end_time': None,
            'protocols': Counter(),
            'ip_stats': defaultdict(lambda: {'packets': 0, 'bytes': 0}),
            'mac_stats': defaultdict(lambda: {'packets': 0, 'bytes': 0}),
            'ip_mac_map': {},
            'packet_sizes': []
        }
    
    async def parse_file(self, file_content: bytes) -> Tuple[List[Packet], Dict[str, Any]]:
        """Parse PCAP file content"""
        try:
            # Use BytesIO to read from memory
            file_obj = io.BytesIO(file_content)
            
            # Read packets from PCAP
            logger.info("Starting PCAP parsing...")
            self.raw_packets = rdpcap(file_obj)
            logger.info(f"Loaded {len(self.raw_packets)} packets")
            
            # Process packets in batches for better performance
            batch_size = 100
            total_packets = len(self.raw_packets)
            
            for batch_start in range(0, total_packets, batch_size):
                batch_end = min(batch_start + batch_size, total_packets)
                batch = self.raw_packets[batch_start:batch_end]
                
                # Process batch
                for i, pkt in enumerate(batch):
                    idx = batch_start + i
                    self._process_packet(pkt, idx)
                
                # Log progress for large files
                if total_packets > 1000:
                    progress = (batch_end / total_packets) * 100
                    logger.info(f"Progress: {progress:.1f}% ({batch_end}/{total_packets} packets)")
            
            # Calculate final statistics
            self._calculate_final_stats()
            
            logger.info(f"Parsed {len(self.packets)} packets successfully")
            return self.packets, self.stats
            
        except Exception as e:
            logger.error(f"Error parsing PCAP file: {e}", exc_info=True)
            raise
    
    def _process_packet(self, pkt: ScapyPacket, idx: int):
        """Process a single packet"""
        try:
            # Extract basic info - Convert to Indian Standard Time (IST = UTC+5:30)
            ist_timezone = timezone(timedelta(hours=5, minutes=30))
            packet_time = datetime.fromtimestamp(float(pkt.time), tz=ist_timezone)
            packet_size = len(pkt)
            
            # Update stats
            self.stats['total_packets'] += 1
            self.stats['total_bytes'] += packet_size
            self.stats['packet_sizes'].append(packet_size)
            
            # Update time range
            if self.stats['start_time'] is None or packet_time < self.stats['start_time']:
                self.stats['start_time'] = packet_time
            if self.stats['end_time'] is None or packet_time > self.stats['end_time']:
                self.stats['end_time'] = packet_time
            
            # Extract layer information
            layers = self._extract_layers(pkt)
            
            # Determine protocol and IPs
            proto = self._get_protocol(pkt)
            src_ip, dst_ip = self._get_ips(pkt)
            
            # Update protocol stats
            self.stats['protocols'][proto] += 1
            
            # Update IP stats
            if src_ip:
                self.stats['ip_stats'][src_ip]['packets'] += 1
                self.stats['ip_stats'][src_ip]['bytes'] += packet_size
            if dst_ip:
                self.stats['ip_stats'][dst_ip]['packets'] += 1
                self.stats['ip_stats'][dst_ip]['bytes'] += packet_size
            
            # Update MAC stats and IP-MAC mapping
            if Ether in pkt:
                src_mac = pkt[Ether].src
                dst_mac = pkt[Ether].dst
                
                self.stats['mac_stats'][src_mac]['packets'] += 1
                self.stats['mac_stats'][src_mac]['bytes'] += packet_size
                self.stats['mac_stats'][dst_mac]['packets'] += 1
                self.stats['mac_stats'][dst_mac]['bytes'] += packet_size
                
                # Map IP to MAC
                if src_ip and src_mac:
                    self.stats['ip_mac_map'][src_ip] = src_mac
                if dst_ip and dst_mac:
                    self.stats['ip_mac_map'][dst_ip] = dst_mac
            
            # Create packet object
            packet = Packet(
                id=f"pkt-{idx}",
                ts=packet_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                src=src_ip or "Unknown",
                dst=dst_ip or "Unknown",
                proto=proto,
                size=packet_size,
                info=self._get_packet_info(pkt, proto),
                layers=layers,
                hex=""  # Disable hex dump to improve performance
            )
            
            self.packets.append(packet)
            
        except Exception as e:
            logger.warning(f"Error processing packet {idx}: {e}")
    
    def _extract_layers(self, pkt: ScapyPacket) -> PacketLayers:
        """Extract layer information from packet"""
        layers = PacketLayers()
        
        # Ethernet layer
        if Ether in pkt:
            layers.ethernet = {
                "src_mac": pkt[Ether].src,
                "dst_mac": pkt[Ether].dst,
                "type": pkt[Ether].type
            }
        
        # IP layer
        if IP in pkt:
            layers.ip = {
                "version": pkt[IP].version,
                "src": pkt[IP].src,
                "dst": pkt[IP].dst,
                "ttl": pkt[IP].ttl,
                "proto": pkt[IP].proto,
                "len": pkt[IP].len
            }
        
        # Transport layer
        if TCP in pkt:
            layers.transport = {
                "type": "TCP",
                "sport": pkt[TCP].sport,
                "dport": pkt[TCP].dport,
                "flags": str(pkt[TCP].flags),
                "seq": pkt[TCP].seq,
                "ack": pkt[TCP].ack
            }
        elif UDP in pkt:
            layers.transport = {
                "type": "UDP",
                "sport": pkt[UDP].sport,
                "dport": pkt[UDP].dport,
                "len": pkt[UDP].len
            }
        elif ICMP in pkt:
            layers.transport = {
                "type": "ICMP",
                "type_code": pkt[ICMP].type,
                "code": pkt[ICMP].code
            }
        
        # Application layer
        if DNS in pkt:
            layers.app = {
                "type": "DNS",
                "qname": pkt[DNS].qd.qname.decode() if pkt[DNS].qd else None,
                "qtype": pkt[DNS].qd.qtype if pkt[DNS].qd else None
            }
        elif HTTP in pkt:
            layers.app = {"type": "HTTP"}
            if HTTPRequest in pkt:
                layers.app.update({
                    "method": pkt[HTTPRequest].Method.decode() if pkt[HTTPRequest].Method else None,
                    "path": pkt[HTTPRequest].Path.decode() if pkt[HTTPRequest].Path else None,
                    "host": pkt[HTTPRequest].Host.decode() if pkt[HTTPRequest].Host else None
                })
        
        return layers
    
    def _get_protocol(self, pkt: ScapyPacket) -> str:
        """Determine packet protocol - simplified for top 10 protocols"""
        # Check for specific application layer protocols first
        if DNS in pkt:
            return "DNS"
        elif HTTP in pkt or HTTPRequest in pkt or HTTPResponse in pkt:
            return "HTTP"
        
        # Check transport layer and common ports
        if TCP in pkt:
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            
            # Top 10 TCP protocols
            if sport == 443 or dport == 443:
                return "HTTPS"
            elif sport == 22 or dport == 22:
                return "SSH"
            elif sport == 21 or dport == 21:
                return "FTP"
            elif sport == 23 or dport == 23:
                return "Telnet"
            elif sport == 25 or dport == 25:
                return "SMTP"
            elif sport == 53 or dport == 53:
                return "DNS"
            elif sport == 80 or dport == 80:
                return "HTTP"
            elif sport == 110 or dport == 110:
                return "POP3"
            elif sport == 143 or dport == 143:
                return "IMAP"
            elif sport == 993 or dport == 993:
                return "IMAPS"
            elif sport == 995 or dport == 995:
                return "POP3S"
            elif sport == 3389 or dport == 3389:
                return "RDP"
            elif sport == 5900 or dport == 5900:
                return "VNC"
            elif sport == 8080 or dport == 8080:
                return "HTTP-Alt"
            elif sport == 8443 or dport == 8443:
                return "HTTPS-Alt"
            else:
                return "TCP"
        
        elif UDP in pkt:
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            
            # Top 10 UDP protocols
            if sport == 53 or dport == 53:
                return "DNS"
            elif sport == 67 or dport == 67 or sport == 68 or dport == 68:
                return "DHCP"
            elif sport == 69 or dport == 69:
                return "TFTP"
            elif sport == 123 or dport == 123:
                return "NTP"
            elif sport == 161 or dport == 161:
                return "SNMP"
            elif sport == 162 or dport == 162:
                return "SNMP-Trap"
            elif sport == 500 or dport == 500:
                return "IKE"
            elif sport == 4500 or dport == 4500:
                return "IPSec-NAT"
            elif sport == 5353 or dport == 5353:
                return "mDNS"
            elif sport == 443 or dport == 443:
                return "QUIC"
            else:
                return "UDP"
        
        elif ICMP in pkt:
            return "ICMP"
        elif ARP in pkt:
            return "ARP"
        elif IP in pkt:
            return "IP"
        else:
            return "Other"
    
    def _get_ips(self, pkt: ScapyPacket) -> Tuple[Optional[str], Optional[str]]:
        """Extract source and destination IPs"""
        if IP in pkt:
            return str(pkt[IP].src), str(pkt[IP].dst)
        elif ARP in pkt:
            return str(pkt[ARP].psrc), str(pkt[ARP].pdst)
        return None, None
    
    def _get_packet_info(self, pkt: ScapyPacket, proto: str) -> str:
        """Generate packet info string"""
        info_parts = []
        
        if TCP in pkt:
            flags = str(pkt[TCP].flags)
            info_parts.append(f"{pkt[TCP].sport} → {pkt[TCP].dport} [{flags}]")
            if pkt[TCP].payload:
                info_parts.append(f"Len={len(pkt[TCP].payload)}")
        elif UDP in pkt:
            info_parts.append(f"{pkt[UDP].sport} → {pkt[UDP].dport}")
            info_parts.append(f"Len={pkt[UDP].len}")
        elif ICMP in pkt:
            icmp_types = {0: "Echo Reply", 8: "Echo Request", 3: "Destination Unreachable"}
            icmp_type = icmp_types.get(pkt[ICMP].type, f"Type {pkt[ICMP].type}")
            info_parts.append(icmp_type)
        elif ARP in pkt:
            op_types = {1: "Request", 2: "Reply"}
            op = op_types.get(pkt[ARP].op, f"Op {pkt[ARP].op}")
            info_parts.append(f"{op}: Who has {pkt[ARP].pdst}? Tell {pkt[ARP].psrc}")
        elif DNS in pkt and pkt[DNS].qd:
            qname = pkt[DNS].qd.qname.decode()
            info_parts.append(f"Query: {qname}")
        
        return " ".join(info_parts) if info_parts else proto
    
    def _get_hex_dump(self, pkt: ScapyPacket) -> str:
        """Get hex dump of packet (limited size for performance)"""
        raw_bytes = bytes(pkt)
        # Limit to first 50 bytes to reduce storage size
        hex_string = " ".join(f"{b:02x}" for b in raw_bytes[:50])
        return hex_string
    
    def _calculate_final_stats(self):
        """Calculate final statistics"""
        # Calculate duration
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            self.stats['duration'] = max(duration, 0.001)  # Avoid division by zero
        else:
            self.stats['duration'] = 0
        
        # Calculate unique counts
        self.stats['unique_ips'] = len(self.stats['ip_stats'])
        self.stats['unique_macs'] = len(self.stats['mac_stats'])
        
        # Calculate average packet size
        if self.stats['packet_sizes']:
            self.stats['avg_packet_size'] = sum(self.stats['packet_sizes']) / len(self.stats['packet_sizes'])
        else:
            self.stats['avg_packet_size'] = 0
        
        # Calculate packet rate
        if self.stats['duration'] > 0:
            self.stats['packet_rate'] = self.stats['total_packets'] / self.stats['duration']
        else:
            self.stats['packet_rate'] = 0
