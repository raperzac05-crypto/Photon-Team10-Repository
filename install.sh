#!/bin/bash

# Photon Laser Tag System - Install

echo "Installing Photon Laser Tag System..."
echo ""

# Install Python packages
echo "Installing Python packages..."
pip3 install pygame psycopg2 --user

echo ""
echo "Installation complete!"
echo "Run: python3 photon.py"