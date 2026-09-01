#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python packages
pip install -r requirements.txt

# Download and extract static ffmpeg binary into a local bin folder
mkdir -p bin
cd bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ --strip-components=1
cd ..
