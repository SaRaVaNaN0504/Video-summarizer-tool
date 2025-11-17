#!/bin/bash
# build.sh

echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p uploads temp

echo "Build completed successfully!"