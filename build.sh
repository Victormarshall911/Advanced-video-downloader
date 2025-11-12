#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify FFmpeg is available (Render provides it)
echo "Checking FFmpeg..."
which ffmpeg || echo "FFmpeg not in PATH"
ffmpeg -version || echo "FFmpeg version check failed"

echo "Build completed successfully!"