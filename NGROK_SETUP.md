# Ngrok Setup Guide for SimplyBook MCP Server

This guide explains how to expose your SimplyBook MCP server publicly using ngrok, allowing you to access it from other machines or clients over the internet.

## Prerequisites

1. **Ngrok Account**: Sign up at [ngrok.com](https://ngrok.com) (free tier available)
2. **Ngrok Installed**: Download and install ngrok on your system

## Installation

### Step 1: Install Ngrok

#### Windows
```powershell
# Using Chocolatey
choco install ngrok

# Or download from https://ngrok.com/download
# Extract and add to PATH
```

#### macOS
```bash
# Using Homebrew
brew install ngrok

# Or download from https://ngrok.com/download
```

#### Linux
```bash
# Download and extract
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Or use package manager if available
```

### Step 2: Authenticate Ngrok

After installation, authenticate with your ngrok account:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

You can find your auth token in the [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).

## Usage

### Option 1: Automated Script (Recommended)

#### Using Python Script (Cross-platform)

```bash
python start-server-with-ngrok.py
```

This script will:
- Start the MCP server
- Start ngrok tunnel
- Display the public URL
- Monitor both processes

#### Using Bash Script (Linux/macOS)

```bash
chmod +x start-server-with-ngrok.sh
./start-server-with-ngrok.sh
```

### Option 2: Manual Setup

#### Step 1: Start the MCP Server

```bash
# Set port (optional, defaults to 8001)
export MCP_PORT=8001

# Start server
python src/main.py
```

#### Step 2: Start Ngrok (in a separate terminal)

```bash
# For default port 8001
ngrok http 8001

# Or specify port explicitly
ngrok http 5001
```

#### Step 3: Get the Public URL

Ngrok will display the public URL in the terminal:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8001
```

Or visit the ngrok web interface at: http://127.0.0.1:4040

## Client Configuration

Once you have the ngrok public URL, update your client configuration:

### For Claude Desktop

```json
{
  "mcpServers": {
    "simplybook": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://YOUR_NGROK_URL.ngrok-free.app/sse/"
      ]
    }
  }
}
```

### For Python Client

```python
from fastmcp import Client

# Use the ngrok public URL
client = Client("https://YOUR_NGROK_URL.ngrok-free.app/sse/")

async with client:
    tools = await client.list_tools()
    print(f"Found {len(tools)} tools")
```

## Important Notes

### Security Considerations

⚠️ **Warning**: Exposing your server publicly means anyone with the URL can access it. Consider:

1. **Authentication**: The server uses SimplyBook credentials, but the MCP endpoint itself is exposed
2. **HTTPS**: Ngrok provides HTTPS by default (recommended)
3. **Temporary URLs**: Free ngrok URLs change on restart. Consider:
   - Using a paid ngrok account for static domains
   - Updating client config when URL changes
   - Using ngrok config file for reserved domains

### Ngrok Free Tier Limitations

- URLs change on each restart
- Limited bandwidth
- Session timeout after 2 hours of inactivity
- Requires ngrok account

### Reserved Domains (Paid)

For production use, consider ngrok's paid plans which offer:
- Static domains (URL doesn't change)
- Custom domains
- More bandwidth
- No session timeouts

## Troubleshooting

### Issue: "ngrok: command not found"

**Solution**: Make sure ngrok is installed and in your PATH.

```bash
# Check if ngrok is accessible
which ngrok  # Linux/macOS
where ngrok  # Windows

# If not found, add to PATH or use full path
```

### Issue: "ngrok: authtoken not configured"

**Solution**: Authenticate ngrok with your auth token.

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Issue: "Connection refused" from client

**Solutions**:
1. Verify server is running: `curl http://localhost:8001/sse/`
2. Check ngrok is forwarding correctly: Visit http://127.0.0.1:4040
3. Ensure you're using the correct endpoint: `/sse/` (with trailing slash)
4. Check firewall settings

### Issue: "424 Failed Dependency" error

**Solutions**:
1. Wait a few seconds after starting server (initialization delay)
2. Verify server logs show "Server initialization complete"
3. Check that all routers registered successfully
4. Ensure credentials are correct in `.env` file

### Issue: Ngrok URL changes frequently

**Solution**: 
- Use ngrok config file to reserve a domain (paid feature)
- Or use the Python script which can detect URL changes

## Advanced Configuration

### Custom Ngrok Configuration

Create `ngrok.yml` in your home directory:

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN
tunnels:
  simplybook:
    proto: http
    addr: 8001
    inspect: true
```

Then start with:
```bash
ngrok start simplybook
```

### Running in Background

#### Using screen (Linux/macOS)
```bash
screen -S mcp-server
python start-server-with-ngrok.py
# Press Ctrl+A then D to detach
```

#### Using tmux (Linux/macOS)
```bash
tmux new -s mcp-server
python start-server-with-ngrok.py
# Press Ctrl+B then D to detach
```

#### Using Windows Task Scheduler
Create a scheduled task to run `start-server-with-ngrok.py` at startup.

## Monitoring

### Ngrok Web Interface

Visit http://127.0.0.1:4040 to see:
- Request/response details
- Traffic statistics
- Public URL information

### Server Logs

Check `simplybook_mcp.log` for server activity:
```bash
tail -f simplybook_mcp.log
```

## Example Workflow

1. **Start server with ngrok**:
   ```bash
   python start-server-with-ngrok.py
   ```

2. **Note the public URL** (e.g., `https://abc123.ngrok-free.app`)

3. **Update client config** with the ngrok URL

4. **Test connection**:
   ```python
   from fastmcp import Client
   import asyncio
   
   async def test():
       client = Client("https://abc123.ngrok-free.app/sse/")
       async with client:
           tools = await client.list_tools()
           print(f"Connected! Found {len(tools)} tools")
   
   asyncio.run(test())
   ```

## Support

For issues:
1. Check server logs: `simplybook_mcp.log`
2. Check ngrok dashboard: http://127.0.0.1:4040
3. Verify credentials in `.env` file
4. Ensure port is not blocked by firewall

