#!/bin/bash
# EE Flask Server Launcher for Linux/Mac
# Starts the EE web interface server

echo "Starting EE Flask Server..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check if we're in the EE directory
if [ ! -f "ee_config.yaml" ]; then
    echo "ERROR: ee_config.yaml not found"
    echo "Please run this script from the EE directory"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start server
echo ""
echo "Starting EE Web Interface..."
echo "Access at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python run_server.py
