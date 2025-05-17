#!/bin/bash
# One-line auto-installer for RKNN Toolkit2 Web UI (Linux)
# Usage: wget -O - https://raw.githubusercontent.com/Nnamllit1/rknn-toolkit2-webui-for-docker/main/auto_install.sh | bash
set -e
REPO_URL="https://github.com/Nnamllit1/rknn-toolkit2-webui-for-docker.git"
DIR="rknn-toolkit2-webui-for-docker"
if [ ! -d "$DIR" ]; then
  echo "Cloning repository..."
  git clone "$REPO_URL"
fi
cd "$DIR"
chmod +x install.sh manage.sh
./install.sh
