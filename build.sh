#!/usr/bin/env bash
# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg
apt-get update
apt-get install -y ffmpeg