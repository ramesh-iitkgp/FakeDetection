#!/bin/bash

# Start Fake Content Detection Backend Server

echo "Starting Fake Content Detection Backend..."
echo "==========================================="

# Navigate to backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Kill any existing server on port 5000
pkill -f "app.py" 2>/dev/null
sleep 1

# Activate virtual environment and start server
./venv/bin/python app.py

echo "Server stopped."
