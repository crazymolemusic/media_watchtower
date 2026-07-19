#!/usr/bin/env bash
# ================================================================================
# 🗼 MEDIA WATCHTOWER AUTOMATED INSTALLER & LAUNCHER
# ================================================================================

# Ensure the system has git and python3 installed
echo "[*] Verifying system pre-requisites..."
if ! command -v git &> /dev/null; then
    echo "[*] Git not found. Installing git..."
    sudo apt-get update && sudo apt-get install -y git
fi

if ! command -v python3 &> /dev/null; then
    echo "[*] Python3 not found. Installing python3..."
    sudo apt-get update && sudo apt-get install -y python3 python3-pip
fi

# Target download directory
TARGET_DIR="$HOME/media-watchtower"

if [ -d "$TARGET_DIR" ]; then
    echo "[*] Existing installation found at $TARGET_DIR. Updating repository..."
    cd "$TARGET_DIR" || exit
    git pull
else
    echo "[*] Cloning Media Watchtower repository from GitHub..."
    git clone https://github.com/YOUR_GITHUB_USERNAME/media-watchtower.git "$TARGET_DIR"
    cd "$TARGET_DIR" || exit
fi

# Run the project's cross-platform bootstrapper
echo "[*] Initializing background server applications..."
python3 run.py