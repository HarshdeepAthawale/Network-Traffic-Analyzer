#!/bin/bash
# Simple startup script for the backend

echo "Starting Network Traffic Analyzer Backend..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the backend
python main.py
