# Network Traffic Analyzer Backend

FastAPI backend for analyzing PCAP network capture files.

## Features

- Upload and parse PCAP/PCAPNG files
- Protocol distribution analysis
- Packet statistics and metrics
- IP-MAC address mapping with vendor lookup
- DNS hostname resolution
- Paginated packet browsing with filtering
- RESTful API with CORS support

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment (optional):
```bash
# Copy the example environment file
cp env.example .env

# Edit .env to set your configuration
```

### Cloudinary Setup (Required)

The application requires Cloudinary for file storage.

1. Sign up for a free Cloudinary account at https://cloudinary.com/users/register/free
2. Go to your dashboard at https://console.cloudinary.com
3. Copy your credentials (Cloud Name, API Key, API Secret)
4. Set the following environment variables:
   ```bash
   NTA_CLOUDINARY_CLOUD_NAME=your_cloud_name
   NTA_CLOUDINARY_API_KEY=your_api_key
   NTA_CLOUDINARY_API_SECRET=your_api_secret
   ```

### MongoDB Setup (Required)

The application requires MongoDB for metadata storage.

**Option A: Local MongoDB (Recommended for Development)**

1. Install MongoDB from https://www.mongodb.com/try/download/community
2. Or use Docker:
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

**Option B: MongoDB Atlas (Recommended for Production)**

1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get your connection string

Set environment variables:
```bash
NTA_MONGODB_URI=mongodb://localhost:27017/
NTA_MONGODB_DATABASE=network_analyzer
```

**Full Setup Documentation:** See [CLOUDINARY_SETUP.md](./CLOUDINARY_SETUP.md) for detailed instructions.

## Running the Backend

### Development mode:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

- `POST /api/upload` - Upload PCAP file for analysis
- `GET /api/summary` - Get summary statistics
- `GET /api/packets` - Get paginated packet list with filtering
- `GET /api/ip-mac-map` - Get IP-MAC mappings with statistics
- `GET /api/files` - List all uploaded files (with metadata from MongoDB)
- `GET /api/files/{file_id}` - Get specific file metadata

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `NTA_HOST` - Host to bind to (default: 0.0.0.0)
- `NTA_PORT` - Port to bind to (default: 8000)
- `NTA_DEBUG` - Debug mode (default: True)
- `NTA_MAX_UPLOAD_SIZE` - Max upload file size in bytes (default: 500MB)
- `NTA_CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name (required)
- `NTA_CLOUDINARY_API_KEY` - Cloudinary API key (required)
- `NTA_CLOUDINARY_API_SECRET` - Cloudinary API secret (required)
- `NTA_MONGODB_URI` - MongoDB connection string (default: mongodb://localhost:27017/)
- `NTA_MONGODB_DATABASE` - MongoDB database name (default: network_analyzer)
- `NTA_CORS_ORIGINS` - CORS allowed origins (default: *)

## Frontend Integration

The backend is configured to accept requests from any origin (CORS enabled).
For production, update the CORS settings in `main.py` to specify allowed origins.

## Directory Structure

```
backend/
├── app/
│   ├── api/           # API endpoint routes
│   ├── core/          # Core configuration and utilities
│   ├── models/        # Pydantic data models
│   └── services/      # Business logic services (Cloudinary + MongoDB)
├── logs/              # Application logs
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Testing with Sample PCAP

You can test the backend using sample PCAP files from:
- https://wiki.wireshark.org/SampleCaptures
- https://www.netresec.com/index.ashx?page=PcapFiles

## Troubleshooting

1. **Import errors**: Make sure you're in the virtual environment and all dependencies are installed
2. **Permission errors**: Some features like raw packet capture require elevated privileges
3. **Memory issues**: Large PCAP files may consume significant memory. Consider chunking for production use

## Future Enhancements

- Real-time packet capture mode
- WebSocket support for live updates
- Export functionality (CSV, JSON)
- Advanced filtering and search
- Performance optimizations for large files
- Multiple file comparison and analysis
