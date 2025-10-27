# Cloudinary + MongoDB Setup Guide

This guide will walk you through setting up **Cloudinary** for `.pcap` file storage and **MongoDB** for metadata storage.

---

## 🎯 Overview

The Network Traffic Analyzer now stores:
- **Raw `.pcap` files** → **Cloudinary** (as `resource_type="raw"`)
- **Parsed packet data** → **Cloudinary** (compressed JSON)
- **File metadata** → **MongoDB** (filename, URL, size, upload date, etc.)

---

## 📋 Step 1: Get Cloudinary Credentials

1. Go to **[https://cloudinary.com](https://cloudinary.com)** and sign up for a free account
2. Navigate to your **Dashboard** at [https://console.cloudinary.com](https://console.cloudinary.com)
3. Copy your credentials:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

---

## 🗄️ Step 2: Setup MongoDB

### Option A: Local MongoDB (Recommended for Development)

1. **Install MongoDB:**
   - Windows: Download from [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
   - Or use Docker:
     ```bash
     docker run -d -p 27017:27017 --name mongodb mongo:latest
     ```

2. **Verify MongoDB is running:**
   ```bash
     # Windows
     net start MongoDB
   ```

### Option B: MongoDB Atlas (Cloud - Recommended for Production)

1. Sign up at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get your connection string

---

## ⚙️ Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cd backend
   copy env.example .env
   ```

2. Edit `.env` and add your credentials:

   ```env
   # Cloudinary Settings (Required)
   NTA_CLOUDINARY_CLOUD_NAME=your_cloud_name
   NTA_CLOUDINARY_API_KEY=your_api_key
   NTA_CLOUDINARY_API_SECRET=your_api_secret

   # MongoDB Settings
   NTA_MONGODB_URI=mongodb://localhost:27017/
   NTA_MONGODB_DATABASE=network_analyzer
   ```

   For MongoDB Atlas, use:
   ```env
   NTA_MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

---

## 📦 Step 4: Install Dependencies

```bash
cd backend

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install packages
pip install -r requirements.txt
```

New packages installed:
- `cloudinary` - For file storage
- `pymongo` - MongoDB Python driver
- `motor` - Async MongoDB driver for FastAPI

---

## 🚀 Step 5: Run the Backend

```bash
# Windows
python main.py
# or
.\run.bat

# Mac/Linux
python main.py
# or
.\run.sh
```

You should see:
```
✅ Cloudinary initialized successfully
✅ MongoDB initialized successfully
```

---

## 📤 How It Works

When you upload a `.pcap` file:

1. **Raw file uploaded** → Stored in Cloudinary as `network_analyzer/pcap_files/{file_id}`
2. **File parsed** → Packet data extracted
3. **Parsed data stored** → Stored in Cloudinary as `network_analyzer/{file_id}/packets`
4. **Metadata stored** → Saved in MongoDB collection `files`:
   ```json
   {
     "file_id": "uuid",
     "filename": "traffic.pcap",
     "url": "https://res.cloudinary.com/.../traffic.pcap",
     "size": 1234567,
     "user": "web_upload",
     "upload_date": "2024-01-01T12:00:00",
     "has_parsed_data": true,
     "packet_count": 1234,
     "stats": { ... }
   }
   ```

---

## 🔍 Example: Query Files

You can query MongoDB to list all uploaded files:

```python
from app.services.mongodb_service import mongodb_service

# List all files
files = await mongodb_service.list_files(skip=0, limit=10)
for file in files:
    print(f"{file['filename']} → {file['url']}")
```

---

## ✅ Verification

Test the upload endpoint:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@path/to/your/traffic.pcap"
```

Expected response:
```json
{
  "success": true,
  "fileId": "uuid-here",
  "message": "Successfully uploaded and parsed X packets from traffic.pcap"
}
```

---

## 🎉 Summary

✅ **Raw `.pcap` files** → Stored in **Cloudinary**  
✅ **Metadata** → Stored in **MongoDB**  
✅ **Parsed packet data** → Stored in **Cloudinary**  
✅ **Scalable**, **cloud-friendly**, and **production-ready** 💪

---

## 🛠️ Troubleshooting

### Cloudinary not initialized
- Check your `.env` file has correct credentials
- Verify credentials in Cloudinary dashboard

### MongoDB connection failed
- Check if MongoDB is running: `net start MongoDB` (Windows)
- Verify connection string in `.env`
- For Atlas, check IP whitelist

### Import errors
- Make sure you installed requirements: `pip install -r requirements.txt`
- Activate virtual environment before running

---

## 📚 Additional Resources

- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [MongoDB Documentation](https://docs.mongodb.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

