#!/bin/bash
# Camofox lifecycle manager — template for other agents
# Usage: ./camofox-manager.sh start|stop|status
# 
# NOTE: This script is environment-specific. 
# - For Hermes Agent users: the script lives at ~/.hermes/scripts/camofox-manager.sh
# - For other agents: ensure Camofox is installed and accessible, then adjust paths below.

CAMOFOX_PORT=9377
# Adjust this path to your Camofox installation
CAMOFOX_DIR="${CAMOFOX_DIR:-$HOME/camofox-browser}"

case "${1:-status}" in
  start)
    if curl -sf http://localhost:$CAMOFOX_PORT/health >/dev/null 2>&1; then
      echo "Camofox already running on port $CAMOFOX_PORT"
      exit 0
    fi
    # Try to start Camofox automatically
    if [ -f "$CAMOFOX_DIR/package.json" ]; then
      echo "Starting Camofox from $CAMOFOX_DIR..."
      cd "$CAMOFOX_DIR" && npm start &
      # Wait up to 30s for Camofox to be ready
      for i in $(seq 1 30); do
        sleep 1
        if curl -sf http://localhost:$CAMOFOX_PORT/health >/dev/null 2>&1; then
          echo "Camofox ready"
          exit 0
        fi
      done
      echo "Timed out waiting for Camofox"
      exit 1
    else
      echo "Camofox not found at $CAMOFOX_DIR"
      echo "Please install Camofox first, or set CAMOFOX_DIR to your installation path."
      echo ""
      echo "Hermes Agent users:"
      echo "  ~/.hermes/scripts/camofox-manager.sh start"
      exit 1
    fi
    ;;
  stop)
    echo "Stopping Camofox..."
    kill $(lsof -t -i :$CAMOFOX_PORT) 2>/dev/null || echo "Not running"
    ;;
  status)
    if curl -sf http://localhost:$CAMOFOX_PORT/health >/dev/null 2>&1; then
      echo "Camofox is running on port $CAMOFOX_PORT"
      exit 0
    else
      echo "Camofox is not running"
      exit 1
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
