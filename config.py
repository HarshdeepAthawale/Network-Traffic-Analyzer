# Configuration for Network Traffic Analyzer with MongoDB

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
MONGO_DATABASE = os.environ.get('MONGODB_DATABASE', 'network_analyzer')
MONGO_COLLECTION = os.environ.get('MONGODB_COLLECTION', 'network_analyses')

# Flask Configuration
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Application Settings
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 104857600))  # 100MB

print(f"MongoDB Configuration:")
print(f"- URI: {MONGO_URI}")
print(f"- Database: {MONGO_DATABASE}")
print(f"- Collection: {MONGO_COLLECTION}")
