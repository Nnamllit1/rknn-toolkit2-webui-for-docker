#!/bin/bash
# Set up the container with docker-compose and print the server IP
set -e

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
