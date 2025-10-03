from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether, ARP
from scapy.layers.dns import DNS
from scapy.layers.http import HTTP
import ipaddress
import hashlib
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import urllib.parse

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'analysis_data'

# MongoDB Configuration
from config import MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DATABASE]
    collection = db[MONGO_COLLECTION]
    # Test connection
    client.admin.command('ping')
    print(f"Connected to MongoDB: {MONGO_DATABASE}.{MONGO_COLLECTION}")
    mongo_connected = True
except ConnectionFailure:
    print("Failed to connect to MongoDB. Falling back to local storage.")
    mongo_connected = False
    # Keep local storage as fallback
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

def save_analysis_to_mongo(analysis_id, analysis_data, report_text):
    """Save analysis data to MongoDB"""
    if not mongo_connected:
        return False
    
    try:
        doc = {
            '_id': analysis_id,
            'analysis_data': analysis_data,
            'report_text': report_text,
            'created_at': datetime.now(),
            'filename': analysis_data['summary'].get('filename', 'unknown'),
            'total_packets': analysis_data['summary']['total_packets'],
            'total_bytes': analysis_data['summary']['total_bytes']
        }
        
        result = collection.replace_one(
            {'_id': analysis_id}, 
            doc, 
            upsert=True
        )
        
        print(f"Saved analysis {analysis_id} to MongoDB")
        return True
        
    except Exception as e:
        print(f"Error saving to MongoDB: {str(e)}")
        return False

def get_analysis_from_mongo(analysis_id):
    """Get analysis data from MongoDB"""
    if not mongo_connected:
        return None
    
    try:
        doc = collection.find_one({'_id': analysis_id})
        if doc:
            return doc['analysis_data']
        return None
        
    except Exception as e:
        print(f"Error retrieving from MongoDB: {str(e)}")
        return None

def get_report_from_mongo(analysis_id):
    """Get report text from MongoDB"""
    if not mongo_connected:
        return None
    
    try:
        doc = collection.find_one({'_id': analysis_id}, {'report_text': 1})
        if doc:
            return doc['report_text']
        return None
        
    except Exception as e:
        print(f"Error retrieving report from MongoDB: {str(e)}")
        return None

def list_analyses_from_mongo():
    """List all analyses from MongoDB"""
    if not mongo_connected:
        return []
    
    try:
        analyses = list(collection.find(
            {}, 
            {'_id': 1, 'created_at': 1, 'filename': 1, 'total_packets': 1, 'total_bytes': 1}
        ).sort('created_at', -1))
        
        return analyses
        
    except Exception as e:
        print(f"Error listing analyses from MongoDB: {str(e)}")
        return []

class NetworkAnalyzer:
    def __init__(self):
        self.packets = []
        self.hosts = {}
        self.protocols = {}
        self.connections = {}
        self.statistics = {}
        
    def analyze_pcap(self, file_path):
        """Analyze PCAP file and extract network information"""
        try:
            # Read PCAP file
            packets = rdpcap(file_path)
            self.packets = packets
            
            # Initialize analysis data
            self.hosts = {'ips': set(), 'macs': set(), 'hostnames': set()}
            self.protocols = {}
            self.connections = {}
            self.statistics = {
                'total_packets': len(packets),
                'total_bytes': 0,
                'time_range': {'start': None, 'end': None},
                'top_talkers': {},
                'protocol_distribution': {},
                'packet_sizes': {'min': float('inf'), 'max': 0, 'avg': 0}
            }
            
            # Analyze each packet
            for packet in packets:
                self._analyze_packet(packet)
            
            # Calculate final statistics
            self._calculate_statistics()
            
            return self._get_analysis_results(os.path.basename(file_path))
            
        except Exception as e:
            raise Exception(f"Error analyzing PCAP file: {str(e)}")
    
    def _analyze_packet(self, packet):
        """Analyze individual packet"""
        try:
            # Extract basic packet info
            packet_info = {
                'timestamp': packet.time,
                'length': len(packet),
                'protocols': []
            }
            
            # Update statistics
            self.statistics['total_bytes'] += packet_info['length']
            
            if self.statistics['time_range']['start'] is None:
                self.statistics['time_range']['start'] = packet.time
            self.statistics['time_range']['end'] = packet.time
            
            # Analyze Ethernet layer
            if Ether in packet:
                eth = packet[Ether]
                packet_info['src_mac'] = eth.src
                packet_info['dst_mac'] = eth.dst
                packet_info['protocols'].append('Ethernet')
                
                self.hosts['macs'].add(eth.src)
                self.hosts['macs'].add(eth.dst)
            
            # Analyze IP layer
            if IP in packet:
                ip = packet[IP]
                packet_info['src_ip'] = ip.src
                packet_info['dst_ip'] = ip.dst
                packet_info['protocols'].append('IP')
                
                self.hosts['ips'].add(ip.src)
                self.hosts['ips'].add(ip.dst)
                
                # Update top talkers
                if ip.src not in self.statistics['top_talkers']:
                    self.statistics['top_talkers'][ip.src] = {'packets': 0, 'bytes': 0}
                if ip.dst not in self.statistics['top_talkers']:
                    self.statistics['top_talkers'][ip.dst] = {'packets': 0, 'bytes': 0}
                
                self.statistics['top_talkers'][ip.src]['packets'] += 1
                self.statistics['top_talkers'][ip.src]['bytes'] += packet_info['length']
                self.statistics['top_talkers'][ip.dst]['packets'] += 1
                self.statistics['top_talkers'][ip.dst]['bytes'] += packet_info['length']
            
            # Analyze transport layer protocols
            if TCP in packet:
                tcp = packet[TCP]
                packet_info['src_port'] = tcp.sport
                packet_info['dst_port'] = tcp.dport
                packet_info['protocols'].append('TCP')
                
                # Track connections
                conn_key = f"{packet_info.get('src_ip', 'unknown')}:{tcp.sport}-{packet_info.get('dst_ip', 'unknown')}:{tcp.dport}"
                if conn_key not in self.connections:
                    self.connections[conn_key] = {
                        'src_ip': packet_info.get('src_ip', 'unknown'),
                        'src_port': tcp.sport,
                        'dst_ip': packet_info.get('dst_ip', 'unknown'),
                        'dst_port': tcp.dport,
                        'packets': 0,
                        'bytes': 0,
                        'flags': set()
                    }
                self.connections[conn_key]['packets'] += 1
                self.connections[conn_key]['bytes'] += packet_info['length']
                self.connections[conn_key]['flags'].add(tcp.flags)
                
            elif UDP in packet:
                udp = packet[UDP]
                packet_info['src_port'] = udp.sport
                packet_info['dst_port'] = udp.dport
                packet_info['protocols'].append('UDP')
                
            elif ICMP in packet:
                packet_info['protocols'].append('ICMP')
            
            # Analyze application layer protocols
            if DNS in packet:
                packet_info['protocols'].append('DNS')
                dns = packet[DNS]
                if dns.qd:
                    query_name = dns.qd.qname.decode('utf-8').rstrip('.')
                    self.hosts['hostnames'].add(query_name)
            
            # Count protocols
            for protocol in packet_info['protocols']:
                if protocol not in self.protocols:
                    self.protocols[protocol] = 0
                self.protocols[protocol] += 1
            
            # Update packet size statistics
            packet_len = packet_info['length']
            if packet_len < self.statistics['packet_sizes']['min']:
                self.statistics['packet_sizes']['min'] = packet_len
            if packet_len > self.statistics['packet_sizes']['max']:
                self.statistics['packet_sizes']['max'] = packet_len
                
        except Exception as e:
            print(f"Error analyzing packet: {str(e)}")
    
    def _calculate_statistics(self):
        """Calculate final statistics"""
        # Calculate average packet size
        if self.statistics['total_packets'] > 0:
            self.statistics['packet_sizes']['avg'] = self.statistics['total_bytes'] / self.statistics['total_packets']
        
        # Sort top talkers by bytes
        self.statistics['top_talkers'] = dict(sorted(
            self.statistics['top_talkers'].items(),
            key=lambda x: x[1]['bytes'],
            reverse=True
        )[:10])  # Top 10
        
        # Convert sets to lists for JSON serialization
        self.hosts['ips'] = list(self.hosts['ips'])
        self.hosts['macs'] = list(self.hosts['macs'])
        self.hosts['hostnames'] = list(self.hosts['hostnames'])
        
                # Convert connection flags sets to lists and handle FlagValue objects
        for conn in self.connections.values():
            flags_list = []
            for flag in conn['flags']:
                if hasattr(flag, 'name'):
                    flags_list.append(flag.name)
                else:
                    flags_list.append(str(flag))
            conn['flags'] = flags_list
    
    def _get_analysis_results(self, filename=None):
        """Get formatted analysis results"""
        return {
            'summary': {
                'total_packets': self.statistics['total_packets'],
                'total_bytes': self.statistics['total_bytes'],
                'duration_seconds': round(self.statistics['time_range']['end'] - self.statistics['time_range']['start'], 2),
                'unique_ips': len(self.hosts['ips']),
                'unique_macs': len(self.hosts['macs']),
                'unique_hostnames': len(self.hosts['hostnames']),
                'unique_connections': len(self.connections),
                'filename': filename
            },
            'hosts': self.hosts,
            'protocols': self.protocols,
            'connections': self.connections,
            'statistics': self.statistics,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard view for managing all analyses"""
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.pcap', '.pcapng')):
            return jsonify({'error': 'File must be a .pcap or .pcapng file'}), 400
        
        # Save uploaded file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Analyze the PCAP file
        analyzer = NetworkAnalyzer()
        analysis_results = analyzer.analyze_pcap(file_path)
        
        # Generate unique analysis ID
        analysis_id = hashlib.md5(filename.encode()).hexdigest()
        
        # Generate human-readable text report
        report_text = generate_text_report(analysis_results)
        
        # Try to save to MongoDB first
        if save_analysis_to_mongo(analysis_id, analysis_results, report_text):
            print(f"Successfully saved analysis {analysis_id} to MongoDB")
        else:
            # Fallback to local storage if MongoDB fails
            print(f"Failed to save to MongoDB, using local storage for {analysis_id}")
            results_file = os.path.join(app.config['DATA_FOLDER'], f"{analysis_id}.json")
            with open(results_file, 'w') as f:
                json.dump(analysis_results, f, indent=2, default=str)
            
            report_file = os.path.join(app.config['DATA_FOLDER'], f"{analysis_id}_report.txt")
            with open(report_file, 'w') as f:
                f.write(report_text)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'results': analysis_results,
            'report_file': f"{analysis_id}_report.txt",
            'storage': 'mongodb' if mongo_connected else 'local'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_text_report(results):
    """Generate a human-readable text report"""
    report = []
    report.append("=" * 60)
    report.append("NETWORK TRAFFIC ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Analysis Date: {results['analysis_timestamp']}")
    report.append("")
    
    # Summary
    summary = results['summary']
    report.append("SUMMARY")
    report.append("-" * 20)
    report.append(f"Total Packets: {summary['total_packets']:,}")
    report.append(f"Total Bytes: {summary['total_bytes']:,}")
    report.append(f"Duration: {summary['duration_seconds']} seconds")
    report.append(f"Unique IP Addresses: {summary['unique_ips']}")
    report.append(f"Unique MAC Addresses: {summary['unique_macs']}")
    report.append(f"Unique Hostnames: {summary['unique_hostnames']}")
    report.append(f"Unique Connections: {summary['unique_connections']}")
    report.append("")
    
    # Hosts
    hosts = results['hosts']
    report.append("HOST INFORMATION")
    report.append("-" * 20)
    report.append(f"IP Addresses ({len(hosts['ips'])}):")
    for ip in hosts['ips'][:10]:  # Show first 10
        report.append(f"  - {ip}")
    if len(hosts['ips']) > 10:
        report.append(f"  ... and {len(hosts['ips']) - 10} more")
    report.append("")
    
    report.append(f"MAC Addresses ({len(hosts['macs'])}):")
    for mac in hosts['macs'][:10]:  # Show first 10
        report.append(f"  - {mac}")
    if len(hosts['macs']) > 10:
        report.append(f"  ... and {len(hosts['macs']) - 10} more")
    report.append("")
    
    if hosts['hostnames']:
        report.append(f"Hostnames ({len(hosts['hostnames'])}):")
        for hostname in hosts['hostnames'][:10]:  # Show first 10
            report.append(f"  - {hostname}")
        if len(hosts['hostnames']) > 10:
            report.append(f"  ... and {len(hosts['hostnames']) - 10} more")
        report.append("")
    
    # Protocols
    report.append("PROTOCOL DISTRIBUTION")
    report.append("-" * 20)
    total_packets = results['statistics']['total_packets']
    for protocol, count in sorted(results['protocols'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_packets) * 100
        report.append(f"{protocol}: {count:,} packets ({percentage:.1f}%)")
    report.append("")
    
    # Top Talkers
    report.append("TOP TALKERS (by bytes)")
    report.append("-" * 20)
    for ip, stats in list(results['statistics']['top_talkers'].items())[:10]:
        report.append(f"{ip}: {stats['packets']:,} packets, {stats['bytes']:,} bytes")
    report.append("")
    
    # Connections
    report.append("NETWORK CONNECTIONS")
    report.append("-" * 20)
    for conn_key, conn in list(results['connections'].items())[:20]:  # Show first 20
        report.append(f"{conn['src_ip']}:{conn['src_port']} -> {conn['dst_ip']}:{conn['dst_port']}")
        report.append(f"  Packets: {conn['packets']}, Bytes: {conn['bytes']}, Flags: {', '.join(conn['flags'])}")
    if len(results['connections']) > 20:
        report.append(f"... and {len(results['connections']) - 20} more connections")
    
    report.append("")
    report.append("=" * 60)
    report.append("End of Report")
    report.append("=" * 60)
    
    return "\n".join(report)

@app.route('/analysis/<analysis_id>')
def get_analysis(analysis_id):
    try:
        # Try to get from MongoDB first
        if mongo_connected:
            results = get_analysis_from_mongo(analysis_id)
            if results:
                return jsonify(results)
        
        # Fallback to local storage
        results_file = os.path.join(app.config['DATA_FOLDER'], f"{analysis_id}.json")
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
            return jsonify(results)
        
        return jsonify({'error': 'Analysis not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<analysis_id>')
def download_report(analysis_id):
    try:
        # Try to get report from MongoDB first
        if mongo_connected:
            report_text = get_report_from_mongo(analysis_id)
            if report_text:
                # Create a temporary file-like response
                response = jsonify({
                    'success': True,
                    'content': report_text,
                    'filename': f"{analysis_id}_report.txt"
                })
                response.headers['Content-Disposition'] = f'attachment; filename="{analysis_id}_report.txt"'
                response.headers['Content-Type'] = 'text/plain'
                return response
        
        # Fallback to local storage
        report_file = os.path.join(app.config['DATA_FOLDER'], f"{analysis_id}_report.txt")
        if os.path.exists(report_file):
            return send_from_directory(app.config['DATA_FOLDER'], f"{analysis_id}_report.txt", as_attachment=True)
        
        return jsonify({'error': 'Report not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyses')
def list_analyses():
    """List all network analyses"""
    try:
        if mongo_connected:
            analyses = list_analyses_from_mongo()
            # Enhance analyses with additional data for dashboard
            enhanced_analyses = []
            for analysis in analyses:
                enhanced = analysis.copy()
                enhanced['storage'] = 'mongodb'
                enhanced_analyses.append(enhanced)
            
            return jsonify({
                'success': True,
                'storage': 'mongodb',
                'analyses': enhanced_analyses,
                'total': len(enhanced_analyses)
            })
        
        # Fallback: list local files
        analysis_files = []
        if os.path.exists(app.config['DATA_FOLDER']):
            for filename in os.listdir(app.config['DATA_FOLDER']):
                if filename.endswith('.json'):
                    analysis_id = filename[:-5]  # Remove .json extension
                    file_path = os.path.join(app.config['DATA_FOLDER'], filename)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        analysis_files.append({
                            '_id': analysis_id,
                            'filename': data['summary'].get('filename', 'unknown'),
                            'total_packets': data['summary']['total_packets'],
                            'total_bytes': data['summary']['total_bytes'],
                            'created_at': data['analysis_timestamp']
                        })
                    except:
                        continue
        
        # Enhance local analyses with additional data for dashboard
        enhanced_files = []
        for analysis in analysis_files:
            enhanced = analysis.copy()
            enhanced['storage'] = 'local'
            enhanced_files.append(enhanced)
        
        return jsonify({
            'success': True,
            'storage': 'local',
            'analyses': enhanced_files,
            'total': len(enhanced_files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
