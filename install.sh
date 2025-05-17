#!/bin/bash
# Set up the container with docker-compose and print the server IP
set -e

# Auto-clone & self-bootstrap, if requested
if [[ "$1" == "--with-clone" ]]; then
  REPO_URL="https://github.com/Nnamllit1/rknn-toolkit2-webui-for-docker.git"
  DIR="rknn-toolkit2-webui-for-docker"
  if [ ! -d "$DIR" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL"
  fi
  cd "$DIR"
  chmod +x install.sh manage.sh
  echo "Running install.sh in $DIR..."
  ./install.sh
  exit $?
fi

chmod +x ./manage.sh

echo "Starting build and setup of the container with docker-compose..."
docker compose build
echo "Container built. Starting container in background..."
docker compose up -d

echo "Container is running. The Web UI is available at:"
if [[ "$(uname -s)" == "Linux" ]]; then
  IP=$(hostname -I | awk '{print $1}')
else
  IP=$(ipconfig 2>/dev/null | grep -Eo 'IPv4-Adresse[ .:]*([0-9]{1,3}\.){3}[0-9]{1,3}' | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n1)
  if [ -z "$IP" ]; then IP="localhost"; fi
fi
echo "http://$IP:5000"
