#!/usr/bin/env bash
# ==============================================================================
# 🗼 MEDIA WATCHTOWER - AUTOMATED INSTALLATION MATRIX
# ==============================================================================
set -e

echo "[*] Initializing system dependency configuration check..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Error: Python 3 ecosystem infrastructure missing. Run: sudo apt install python3 python3-pip -y"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "[!] Error: Git tool tree missing. Run: sudo apt install git -y"
    exit 1
fi

# Define path configurations using your actual username
TARGET_DIR="/home/cole/media_watchtower"

if [ -d "$TARGET_DIR" ]; then
    echo "[*] Pre-existing node footprint detected. Wiping local environment storage..."
    rm -rf "$TARGET_DIR"
fi

echo "[*] Fetching application package clusters from cloud repository..."
# FIX: Updated to your exact underscore URL
git clone "https://github.com/crazymolemusic/media_watchtower.git" "$TARGET_DIR"

# FIX: Changing directory into the correct folder name
cd "$TARGET_DIR"

echo "[*] Deploying runtime configuration vault..."
cat << 'EOF' > config.json
{
    "is_installed": false,
    "custom_logo_url": "",
    "global_check_interval": 30,
    "users": {},
    "apps": {
        "Jellyfin": {"url": "http://127.0.0.1:8096", "type": "jellyfin", "enabled": true},
        "Threadfin": {"url": "http://127.0.0.1:34400", "type": "threadfin", "enabled": true},
        "Pihole": {"url": "http://127.0.0.1:80", "type": "pihole", "enabled": false}
    },
    "metrics": {
        "Jellyfin": {"uptime": 0, "downtime": 0, "status": "Offline Data", "log": "Awaiting execution loop..."},
        "Threadfin": {"uptime": 0, "downtime": 0, "status": "Offline Data", "log": "Awaiting execution loop..."},
        "Pihole": {"uptime": 0, "downtime": 0, "status": "Disabled", "log": "Monitoring loop inactive."}
    }
}
EOF

echo "[*] Granting execution tokens to core application files..."
chmod +x run.py

echo "[*] Launching system daemon threads detached in user memory spaces..."
python3 run.py

exit 0
