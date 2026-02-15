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

echo "Setting up database..."

sudo -u postgres psql <<EOF

-- Create user if it doesn't exist
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'student') THEN
      CREATE ROLE student LOGIN PASSWORD 'student';
   END IF;
END
\$\$;

--Create database (may error if it already exists, but we can ignore that)
CREATE DATABASE photon;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE photon TO student;

\c photon;

-- Create table if it doesn't exist
CREATE TABLE IF NOT EXISTS players (
    id INT PRIMARY KEY
    codename TEXT
);

EOF

echo "Install complete!"
echo "Run the application with:"
echo "python3 -m photon_app.main"