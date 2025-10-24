# Network Traffic Analyzer

**Upload PCAP files and get instant network insights with beautiful visualizations**


## Key Features

### **Instant Analysis**
Upload .pcap/.pcapng files and get comprehensive network insights within seconds. No complex setup required - just drag, drop, and analyze.

### **Real-time Metrics Dashboard**
- Live packets per second (PPS) monitoring
- Bandwidth usage visualization
- Traffic volume trends and patterns
- Interactive charts with zoom and filtering

### **IP Geolocation Mapping**
- Visualize network traffic origins on world map
- Identify suspicious or unexpected connections
- Track communication patterns across different countries
- Enhanced security analysis capabilities

### **Protocol Breakdown**
- Interactive pie charts showing protocol distribution
- Deep dive into TCP, UDP, HTTP, DNS, and other protocols
- Protocol-specific statistics and insights
- Export protocol analysis reports

### **MAC Address Intelligence**
- Automatic vendor identification from MAC addresses
- Device fingerprinting and network mapping
- Hardware manufacturer lookup database
- Network topology visualization

### **Modern Dashboard**
- Beautiful, responsive UI built with Next.js
- Dark/light mode toggle for comfortable viewing
- Mobile-friendly design
- Real-time data updates without page refresh

## Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd network-traffic-analyzer

# Backend (Terminal 1)
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

# Frontend (Terminal 2)
npm install
npm run dev
```

Open http://localhost:3000 and upload your first PCAP file!


## Contributing

1. Fork → Create branch → Commit → Push → PR

## License

MIT License

---

