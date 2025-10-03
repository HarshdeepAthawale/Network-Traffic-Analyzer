# Network Traffic Analyzer 🚀

A comprehensive web-based network traffic analyzer that processes PCAP files from Wireshark and extracts detailed network information including hosts, IP addresses, MAC addresses, protocols, connections, and traffic statistics.

## ✨ Features

- **📁 File Upload**: Drag and drop or browse to upload PCAP files (.pcap only)
- **🔍 Comprehensive Analysis**: Extracts detailed network information from PCAP files
- **🌐 Host Information**: IP addresses, MAC addresses, and hostnames
- **📡 Protocol Analysis**: Protocol distribution and statistics
- **🔗 Connection Tracking**: Network connections with packet counts and byte statistics
- **📊 Traffic Statistics**: Packet sizes, top talkers, and general statistics
- **💾 Local Storage**: All analysis data is stored locally
- **🎨 Modern UI**: Responsive web interface with real-time analysis
- **📄 Text Reports**: Generate clean, human-readable text reports

## 📊 Analysis Capabilities

### General Statistics
- Total packet count, bytes transferred, capture duration
- Packet size distribution (min, max, average)

### Host Information  
- Unique IP addresses, MAC addresses, hostnames

### Protocol Analysis
- Protocol distribution and statistics

### Network Connections
- Source/destination IP:port pairs with packet counts and TCP flags

### Top Talkers
- Hosts with highest traffic volume ranked by bytes

## 🚀 Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Open browser**: `http://localhost:5000`

## 📋 File Support

- **✅ Supported formats**: .pcap files only
- **📏 Maximum file size**: 100MB
- **🛠️ Source tools**: Wireshark, tcpdump, or any tool that generates PCAP files

## 📁 Project Structure

```
Network-traffic-Analyzer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies  
├── README.md             # Documentation
├── templates/
│   └── index.html       # Web interface
├── uploads/             # Temporary storage (auto-created)
└── analysis_data/       # Analysis results (auto-created)
```
