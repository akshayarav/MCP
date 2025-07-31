#!/usr/bin/env python3
import json
import subprocess
import sys
from typing import Dict, Any, Optional
import time

# Start MCP server
server = subprocess.Popen([sys.executable, "mcp_server.py"], 
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, text=True)

# Give server time to start
time.sleep(0.5)

if server.poll() is not None:
    print(f"Server exited with code: {server.returncode}")
    if server.stderr:
        stderr_output = server.stderr.read()
        if stderr_output:
            print(f"Server error: {stderr_output}")
        sys.exit(1)

def send(method:str, params:Optional[Dict[str, Any]] = None, id:Optional[int] = None):
    msg: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params: msg["params"] = params
    if id: msg["id"] = id
    if not server.stdin:
        raise Exception("Server.stdin is None")
    if not server.stdout:
        raise Exception("Server.stdin is None")
    
    server.stdin.write(json.dumps(msg) + '\n')
    server.stdin.flush()
    
    if id:  # Request - expect response
        response = server.stdout.readline()
        print(f"Response: {response.strip()}")

print("MCP Test Client - Commands: init, initialized, unknown, quit")

try:
    while True:
        cmd = input("> ").strip()
        
        if cmd == "quit":
            break
        elif cmd == "init":
            send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}}, 1)
        elif cmd == "initialized":
            send("notifications/initialized")
        elif cmd == "unknown":
            send("unknown_method", {}, 2)
        else:
            print("Commands: init, initialized, unknown, quit")

except KeyboardInterrupt:
    pass

server.terminate()


# =============================================================================
# EXAMPLE USAGE & TESTING
# =============================================================================

"""
Test this server with these JSON-RPC messages:

1. Initialize the server:
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"Test Client","version":"1.0.0"}},"id":1}' | python barebones_server.py

Expected response:
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {}},
    "serverInfo": {"name": "Barebones MCP Server", "version": "1.0.0"}
  }
}

2. Send initialized notification:
echo '{"jsonrpc":"2.0","method":"notifications/initialized"}' | python barebones_server.py

Expected: No response (it's a notification), but server logs "Server fully initialized and ready!"

3. Test unknown method:
echo '{"jsonrpc":"2.0","method":"unknown","id":2}' | python barebones_server.py

Expected response:
{
  "jsonrpc": "2.0", 
  "id": 2,
  "error": {
    "code": -32601,
    "message": "Method 'unknown' not implemented"
  }
}
"""