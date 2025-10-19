# Network Traffic Analyzer 🌐

A powerful web-based network traffic analysis tool that allows you to upload and analyze PCAP (Packet Capture) files with an intuitive dashboard interface.

![Network Traffic Analyzer](https://img.shields.io/badge/Next.js-15.2.4-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features ✨

- 📤 **PCAP File Upload**: Upload and parse .pcap and .pcapng files
- 📊 **Traffic Analysis**: Comprehensive analysis of network packets
- 🔍 **Protocol Breakdown**: Visualize protocol distribution
- 🌍 **IP Geolocation**: Track geographical origins of network traffic
- 🔢 **MAC Address Lookup**: Vendor identification from MAC addresses
- 📈 **Real-time Metrics**: Packets per second, bandwidth usage, and more
- 🎨 **Modern UI**: Built with Next.js, React, and Tailwind CSS
- 🌓 **Dark/Light Mode**: Toggle between themes for comfortable viewing

## Architecture

### Frontend (Next.js)
- **Framework**: Next.js 15.2.4 with React 19
- **UI Components**: Radix UI, Recharts for visualizations
- **Styling**: Tailwind CSS with custom theming
- **State Management**: SWR for data fetching and caching

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Packet Analysis**: Scapy for PCAP parsing
- **DNS Resolution**: DNS lookups for hostnames
- **MAC Vendor Lookup**: Hardware manufacturer identification
- **Storage**: In-memory storage (configurable to SQLite)

## Quick Start 🚀

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd network-traffic-analyzer
   ```

2. **Start the Backend**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   python main.py
   ```
   Backend will run on http://localhost:8000

3. **Start the Frontend** (in a new terminal)
   ```bash
   npm install
   npm run dev
   ```
   Frontend will run on http://localhost:3000

4. **Open your browser**
   Navigate to http://localhost:3000 and upload a PCAP file!

## Deployment 🌍

This application is designed to be deployed with:
- **Backend** → [Render](https://render.com) (Python hosting)
- **Frontend** → [Vercel](https://vercel.com) (Next.js hosting)

### Quick Deploy

#### Deploy Backend to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

1. Sign up/Login to Render
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` and configure automatically
5. Add environment variable: `NTA_CORS_ORIGINS` with your Vercel URL
6. Deploy!

#### Deploy Frontend to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Sign up/Login to Vercel
2. Import your GitHub repository
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
4. Deploy!

### Detailed Deployment Guide

For step-by-step deployment instructions, troubleshooting, and configuration options, see:

📖 **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide

## Project Structure 📁

```
network-traffic-analyzer/
├── app/                      # Next.js pages and API routes
│   ├── dashboard/           # Dashboard page
│   ├── upload/              # Upload page
│   └── layout.tsx           # Root layout
├── components/              # React components
│   ├── ui/                  # UI component library
│   ├── packet-table.tsx     # Packet data table
│   ├── protocol-chart.tsx   # Protocol visualization
│   └── ...
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Data models
│   │   └── services/       # Business logic
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── lib/                    # Utility functions
├── hooks/                  # React hooks
├── public/                 # Static assets
├── render.yaml            # Render deployment config
├── vercel.json            # Vercel deployment config
└── DEPLOYMENT.md          # Deployment guide
```

## API Endpoints 🔌

### Backend API (FastAPI)

- `POST /api/upload` - Upload PCAP file
- `GET /api/summary?file_id={id}` - Get traffic summary
- `GET /api/packets?file_id={id}` - Get packet list with pagination
- `GET /api/ip-mac-map?file_id={id}` - Get IP to MAC address mappings

Full API documentation available at: `http://localhost:8000/docs` (when running locally)

## Environment Variables 🔧

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (backend/.env)
```env
NTA_HOST=0.0.0.0
NTA_PORT=8000
NTA_DEBUG=True
NTA_STORAGE_TYPE=memory
NTA_CORS_ORIGINS=*
NTA_MAX_UPLOAD_SIZE=104857600
```

See `.env.example` files for complete configuration options.

## Tech Stack 💻

### Frontend
- **Next.js 15** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - Component primitives
- **Recharts** - Data visualization
- **SWR** - Data fetching
- **Lucide React** - Icons

### Backend
- **FastAPI** - Modern Python web framework
- **Scapy** - Packet manipulation
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python Multipart** - File upload handling
- **DNSPython** - DNS resolution
- **MAC Vendor Lookup** - Hardware identification

## Development Scripts 📝

### Frontend
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Backend
```bash
python main.py       # Start FastAPI server
uvicorn main:app --reload  # Start with auto-reload
```

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Known Limitations ⚠️

- **Free Tier Hosting**: Render free tier sleeps after 15 minutes of inactivity
- **File Persistence**: In-memory storage means uploaded files don't persist across restarts
- **File Size Limits**: Default 100MB upload limit (configurable)
- **Browser Compatibility**: Best experienced on modern browsers (Chrome, Firefox, Safari, Edge)

## Roadmap 🗺️

- [ ] Persistent storage with database support
- [ ] User authentication and multi-user support
- [ ] Real-time packet capture analysis
- [ ] Export analysis reports (PDF, CSV)
- [ ] Advanced filtering and search capabilities
- [ ] Packet payload inspection
- [ ] Network flow visualization
- [ ] Custom alerting rules

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

- **Documentation**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## Acknowledgments 🙏

- Built with [Next.js](https://nextjs.org/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Packet analysis using [Scapy](https://scapy.net/)
- UI components from [Radix UI](https://www.radix-ui.com/)
- Icons by [Lucide](https://lucide.dev/)

---

Made with ❤️ by the Network Traffic Analyzer Team

**Star ⭐ this repository if you find it helpful!**

