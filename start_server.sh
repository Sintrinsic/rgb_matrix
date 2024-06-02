#!/bin/bash

# Navigate to the project directory
cd ~/projects/rgb_matrix

# Check if the virtual environment directory exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
else
    echo "Virtual environment found."
fi

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Run the script
echo "Running simple_display_server.py..."

python lib/simple_display_server.py

# Deactivate the virtual environment
deactivate

