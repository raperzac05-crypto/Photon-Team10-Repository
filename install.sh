#!/usr/bin/env bash
set -euo pipefail

# Photon Team 10 - Sprint 2
# Installs Python dependencies for the VM.

echo "Updating system packages..."
sudo apt update 

echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-pygame postgresql libpq-dev python3-dev gcc

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Starting PostgreSQL service..."
sudo service postgresql start

echo "Install complete!"
echo "Run the application with:"
echo "python3 -main.py"
