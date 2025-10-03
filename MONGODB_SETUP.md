# MongoDB Setup Guide for Network Traffic Analyzer

This guide will help you set up MongoDB for the Network Traffic Analyzer application.

## Option 1: Local MongoDB Installation

### For Windows:
1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Install MongoDB following the installer instructions
3. Start MongoDB service:
   - Open Command Prompt as Administrator
   - Run: `net start MongoDB`

### For macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

### For Linux (Ubuntu/Debian):
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Create list file
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package database and install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

## Option 2: MongoDB Atlas (Cloud)

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (free tier available)
4. Create a database user
5. Get your connection string
6. Whitelist your IP address

## Environment Configuration

Create a `.env` file in your project root:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=network_analyzer
MONGODB_COLLECTION=network_analyses

# For MongoDB Atlas, use:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/network_analyzer?retryWrites=true&w=majority

# Flask Configuration
PORT=5000
```

## Installation and Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MongoDB (if using local installation)

**Windows:**
```cmd
net start MongoDB
```

**macOS/Linux:**
```bash
sudo systemctl start mongod
# or
brew services start mongodb/brew/mongodb-community
```

### 3. Run the Application
```bash
python app.py
```

### 4. Migrate Existing Data (Optional)
```bash
python migrate_to_mongo.py
```

## New API Endpoints

The application now includes these new endpoints:

### List All Analyses
```
GET /analyses
```
Returns a list of all network analyses with summary information.

Response:
```json
{
  "success": true,
  "storage": "mongodb",
  "analyses": [
    {
      "_id": "analysis_id",
      "filename": "example.pcap",
      "total_packets": 1000,
      "total_bytes": 50000,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "total": 1
}
```

### Download Report (Enhanced)
```
GET /report/<analysis_id>
```
Returns the text report as a downloadable file.

## MongoDB Collections Structure

### network_analyses Collection
```json
{
  "_id": "analysis_id_hash",
  "analysis_data": {
    "summary": { ... },
    "hosts": { ... },
    "protocols": { ... },
    "connections": { ... },
    "statistics": { ... }
  },
  "report_text": "Network Traffic Analysis Report...",
  "created_at": "2024-01-01T12:00:00",
  "filename": "example.pcap",
  "total_packets": 1000,
  "total_bytes": 50000
}
```

## Features

- **Automatic Fallback**: If MongoDB is unavailable, the app falls back to local JSON storage
- **Data Migration**: Existing JSON files can be migrated to MongoDB
- **Enhanced Reporting**: Reports are stored in MongoDB alongside analysis data
- **Historical Data**: All analyses are preserved with metadata for easy querying
- **Scalability**: MongoDB allows for better querying and data management at scale

## Troubleshooting

### Connection Issues
- Ensure MongoDB is running
- Check firewall settings
- Verify connection string format
- For Atlas, ensure IP is whitelisted

### Migration Issues
- Check file permissions
- Ensure MongoDB is running during migration
- Verify `.env` configuration

### Data Consistency
- The app maintains backward compatibility with JSON files
- Both storage methods can coexist during transition
- Migration script handles duplicate prevention

## Production Considerations

1. **MongoDB Atlas**: For production, consider MongoDB Atlas for managed hosting
2. **Authentication**: Enable MongoDB authentication for production
3. **Indexes**: Add indexes on frequently queried fields for performance
4. **Backup**: Set up regular MongoDB backups
5. **Monitoring**: Monitor MongoDB performance and resource usage
