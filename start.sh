#!/usr/bin/env bash
set -e

detect_ip() {
  # Try ip route (Linux)
  if command -v ip &>/dev/null; then
    ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' && return
  fi
  # Try hostname -I (Linux fallback)
  if command -v hostname &>/dev/null && hostname -I &>/dev/null; then
    hostname -I 2>/dev/null | awk '{print $1}' && return
  fi
  # Try ipconfig (macOS)
  if command -v ipconfig &>/dev/null; then
    ipconfig getifaddr en0 2>/dev/null && return
    ipconfig getifaddr en1 2>/dev/null && return
  fi
  # Try ifconfig (macOS/BSD fallback)
  if command -v ifconfig &>/dev/null; then
    ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -1 && return
  fi
  echo ""
}

HOST_IP=$(detect_ip)

if [ -z "$HOST_IP" ]; then
  echo "ERROR: Could not detect the machine's IP address."
  echo "Please create a .env file manually:"
  echo "  echo 'HOST_IP=<your-ip>' > .env"
  exit 1
fi

echo "HOST_IP=$HOST_IP" > .env
echo "Detected IP: $HOST_IP"
echo "Starting AAS services..."

docker compose up -d

echo ""
echo "All services started. Access the Web UI at:"
echo "  http://${HOST_IP}:3000"
