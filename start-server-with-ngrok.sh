#!/bin/bash
# Script to start SimplyBook MCP server with ngrok tunnel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "SimplyBook MCP Server with Ngrok Tunnel"
echo "============================================================"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ Error: ngrok is not installed${NC}"
    echo ""
    echo "📥 Install ngrok:"
    echo "   1. Download from https://ngrok.com/download"
    echo "   2. Extract and add to PATH"
    echo ""
    echo "🔐 After installation, authenticate:"
    echo "   ngrok config add-authtoken YOUR_AUTH_TOKEN"
    exit 1
fi

# Get port from environment or use default
PORT=${MCP_PORT:-8001}

echo -e "${GREEN}🚀 Starting SimplyBook MCP server...${NC}"

# Start server in background
python src/main.py > server.log 2>&1 &
SERVER_PID=$!

echo "⏳ Waiting for server to initialize..."
sleep 5

# Check if server is still running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}❌ Server failed to start!${NC}"
    echo "Check server.log for details"
    exit 1
fi

echo -e "${GREEN}✅ Server started (PID: $SERVER_PID)${NC}"
echo ""

echo -e "${YELLOW}🚇 Starting ngrok tunnel on port $PORT...${NC}"

# Start ngrok in background
ngrok http $PORT > ngrok.log 2>&1 &
NGROK_PID=$!

sleep 3

# Get public URL from ngrok API
PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$PUBLIC_URL" ]; then
    # Try HTTP if HTTPS not available
    PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"http://[^"]*' | head -1 | cut -d'"' -f4)
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✅ Server and ngrok are running!${NC}"
echo "============================================================"
echo ""
echo -e "${GREEN}🌐 Public URL:${NC} $PUBLIC_URL"
echo -e "${GREEN}📋 MCP Endpoint:${NC} $PUBLIC_URL/sse/"
echo ""
echo "📊 Monitoring:"
echo "   - Server logs: tail -f server.log"
echo "   - Ngrok dashboard: http://127.0.0.1:4040"
echo ""
echo -e "${YELLOW}💡 Use this URL in your client configuration:${NC}"
echo '   "http://localhost:8001/sse/" -> "'$PUBLIC_URL'/sse/"'
echo ""
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop both server and ngrok${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $SERVER_PID 2>/dev/null || true
    kill $NGROK_PID 2>/dev/null || true
    echo "✅ Server and ngrok stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait

