#!/bin/bash
# run_dashboard.sh — start local HTTP server and display the dashboard link

# Define the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8080
HTML_PATH="dashboard/prototype/prototype.html"

# Go to the project root
cd "$BASE_DIR/.."

# Kill any previous python server on the same port (optional)
if lsof -i:$PORT >/dev/null 2>&1; then
  echo "Port $PORT already in use — killing old server..."
  kill $(lsof -t -i:$PORT)
  sleep 1
fi

# Start server in background
echo "Starting local server on port $PORT..."
python3 -m http.server $PORT >/dev/null 2>&1 &

# Give it a moment to start
sleep 1

# Display link
URL="http://localhost:${PORT}/${HTML_PATH}"
echo ""
echo "Dashboard server is running."
echo "Click or copy this link into your browser:"
echo ""
echo "  ${URL}"
echo ""
echo "Press Ctrl+C in this terminal to stop the server."

wait

