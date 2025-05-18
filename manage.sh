#!/bin/bash
# Management script for the rknn-webui container and config
set -e

SERVICE="rknn-webui"
CONFIG="config.json"

show_config() {
  cat "$CONFIG"
}

set_config() {
  key="$1"
  value="$2"
  python3 -c "import json; f='$CONFIG'; d=json.load(open(f)); d['$key'] = $value; json.dump(d, open(f, 'w'), indent=2)"
  echo "Set $key to $value in $CONFIG"
}

case "$1" in
  start)
    echo "Starting container..."
    docker compose up -d
    ;;
  stop)
    echo "Stopping container..."
    docker compose stop
    ;;
  restart)
    echo "Restarting container..."
    docker compose restart
    ;;
  status)
    docker compose ps
    ;;
  logs)
    docker compose logs -f
    ;;
  build)
    echo "Rebuilding container..."
    docker compose build
    ;;
  cleanup)
    echo "Are you sure you want to remove all containers and images (may have unwanted side effects)? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
      echo "Removing all containers and images..."
      docker system prune -a --volumes
    else
      echo "Cleanup aborted."
    fi
    ;;
  config)
    if [ "$2" = "show" ]; then
      show_config
    elif [ "$2" = "set" ] && [ -n "$3" ] && [ -n "$4" ]; then
      set_config "$3" "$4"
    else
      echo "Usage: $0 config show | config set <key> <value>"
      exit 1
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs|build|config show|cleanup|config set <key> <value>}"
    exit 1
    ;;
esac
