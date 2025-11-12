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

## Stack

- Backend: FastAPI with async MongoDB persistence (Motor)
- Frontend: Next.js App Router hosted on Vercel
- Database: MongoDB Atlas or self-managed deployment
- Hosting: Render for the API, Vercel for the dashboard

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
# configure backend/.env (see backend/env.example)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` when running the frontend locally. Open http://localhost:3000 and upload your first PCAP file!

## Deployment

- **Render (backend)**: Deploy with `render.yaml`. Configure `NTA_MONGODB_URI`, `NTA_MONGODB_DATABASE`, `NTA_CORS_ORIGINS`, and any other FastAPI settings in the Render dashboard. The service builds with `pip install -r requirements.txt` and runs `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- **Vercel (frontend)**: Set `NEXT_PUBLIC_API_URL` to the Render backend URL (e.g., `https://network-traffic-analyzer-backend.onrender.com`). Deploy via Vercel; the dashboard fetches data at runtime via `fetch` with `cache: "no-store"`.
- **MongoDB**: Use MongoDB Atlas or another hosted instance. Ensure Render outbound IPs are allowed, and URL-encode sensitive characters in the connection string added to `NTA_MONGODB_URI`.

## Contributing

1. Fork → Create branch → Commit → Push → PR

## License

MIT License

---

