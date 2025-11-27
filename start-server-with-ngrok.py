#!/usr/bin/env python3
"""
Script to start the SimplyBook MCP server with ngrok tunnel for public access.
This allows the server to be accessed from other machines or clients over the internet.
"""

import subprocess
import sys
import time
import os
import json
import requests
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_ngrok_url(ngrok_api_url='http://127.0.0.1:4040/api/tunnels'):
    """Get the public ngrok URL"""
    try:
        response = requests.get(ngrok_api_url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                # Prefer HTTPS tunnel if available
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
                # Fallback to HTTP
                return tunnels[0].get('public_url')
    except Exception as e:
        print(f"⚠️  Could not fetch ngrok URL: {e}")
    return None

def start_ngrok(port=8001):
    """Start ngrok tunnel"""
    print(f"🚇 Starting ngrok tunnel on port {port}...")
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for ngrok to start
    time.sleep(3)
    
    # Get the public URL
    public_url = get_ngrok_url()
    if public_url:
        print(f"✅ Ngrok tunnel active!")
        print(f"🌐 Public URL: {public_url}")
        print(f"📋 MCP Endpoint: {public_url}/sse/")
        print(f"\n💡 Use this URL in your client configuration:")
        print(f'   "http://localhost:8001/sse/" -> "{public_url}/sse/"')
    else:
        print("⚠️  Ngrok started but couldn't retrieve public URL")
        print("   Check http://127.0.0.1:4040 for the ngrok dashboard")
    
    return ngrok_process, public_url

def start_server():
    """Start the MCP server"""
    print("🚀 Starting SimplyBook MCP server...")
    server_process = subprocess.Popen(
        [sys.executable, 'src/main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return server_process

def main():
    """Main function"""
    print("=" * 60)
    print("SimplyBook MCP Server with Ngrok Tunnel")
    print("=" * 60)
    print()
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        print("❌ Error: ngrok is not installed or not in PATH")
        print("\n📥 Install ngrok:")
        print("   1. Download from https://ngrok.com/download")
        print("   2. Extract and add to PATH, or")
        print("   3. Install via package manager:")
        print("      - Windows (choco): choco install ngrok")
        print("      - macOS (brew): brew install ngrok")
        print("      - Linux: Download and add to PATH")
        print("\n🔐 After installation, authenticate:")
        print("   ngrok config add-authtoken YOUR_AUTH_TOKEN")
        sys.exit(1)
    
    # Get port from environment or use default
    port = int(os.getenv('MCP_PORT', '8001'))
    
    # Start the server
    server_process = start_server()
    
    # Wait a bit for server to start
    print("⏳ Waiting for server to initialize...")
    time.sleep(5)
    
    # Check if server is running
    if server_process.poll() is not None:
        print("❌ Server failed to start!")
        stdout, stderr = server_process.communicate()
        print(stdout)
        if stderr:
            print(stderr)
        sys.exit(1)
    
    # Start ngrok
    ngrok_process, public_url = start_ngrok(port)
    
    print("\n" + "=" * 60)
    print("✅ Server and ngrok are running!")
    print("=" * 60)
    print("\n📊 Monitoring:")
    print("   - Server logs: Check console output")
    print("   - Ngrok dashboard: http://127.0.0.1:4040")
    print("\n⚠️  Press Ctrl+C to stop both server and ngrok")
    print()
    
    try:
        # Monitor server output
        for line in server_process.stdout:
            print(f"[SERVER] {line.rstrip()}")
            
            # Periodically update ngrok URL (in case it changes)
            if "Running on" in line:
                time.sleep(2)
                updated_url = get_ngrok_url()
                if updated_url and updated_url != public_url:
                    public_url = updated_url
                    print(f"\n🔄 Ngrok URL updated: {public_url}/sse/")
                    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        server_process.terminate()
        ngrok_process.terminate()
        
        # Wait for processes to terminate
        try:
            server_process.wait(timeout=5)
            ngrok_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            ngrok_process.kill()
        
        print("✅ Server and ngrok stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()

