#!/usr/bin/env python3
import json
import subprocess
import sys
from typing import Dict, Any, Optional

# Start MCP server
server = subprocess.Popen([sys.executable, "barebones_server.py"], 
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, text=True)

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