#!/usr/bin/env python3
"""
Barebones MCP Server Implementation
Using official MCP types for client-server initialization
"""

import json
import sys
from typing import Dict, Any, Optional
from mcp.types import (
    InitializeRequest, 
    InitializeResult,
    Implementation,
    ServerCapabilities,
    JSONRPCError,
    ErrorData,
    PromptsCapability,
    ResourcesCapability,
    ToolsCapability,
    LoggingCapability
)


class MCPServer:
    """
    Minimal MCP Server with proper initialization flow
    """
    
    def __init__(self, server_name: str = "Barebones MCP Server", server_version: str = "1.0.0"):
        """
        Initialize the MCP Server
        
        Args:
            server_name: Name of this server
            server_version: Version of this server
        """
        self.server_name = server_name
        self.server_version = server_version
        self.protocol_version = "2024-11-05"  # Current MCP protocol version
        self.initialized = False
        
        # Server info that will be sent to client
        self.server_info = Implementation(
            name=self.server_name,
            version=self.server_version,
        )
        
        self.capabilities = ServerCapabilities(
            experimental={},
            logging=LoggingCapability(),
            prompts=PromptsCapability(listChanged=False),
            resources=ResourcesCapability(listChanged=False, subscribe=False),
            tools=ToolsCapability(listChanged=False),
        )
    
    def handle_initialize(self, request: InitializeRequest) -> InitializeResult:
        """
        Handle the MCP initialize request from client
        
        This is the first method called in the MCP lifecycle.
        The client sends its info and we respond with our capabilities.
        
        Args:
            request: Initialize request from client
            
        Returns:
            Initialize result with our server info and capabilities
        """
        # Store client info for reference
        self.client_info = request.params.clientInfo if request.params else None
        
        # Mark as initialized
        self.initialized = True
        
        # Return our server capabilities and info
        return InitializeResult(
            protocolVersion=self.protocol_version,
            capabilities=self.capabilities,
            serverInfo=self.server_info
        )
    
    def handle_notifications_initialized(self) -> None:
        """
        Handle the initialized notification from client
        
        This is sent after successful initialize to confirm the session is ready.
        No response needed - it's a notification.
        """
        print("Server fully initialized and ready!", file=sys.stderr)
    
    def handle_request(self, raw_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Main request handler - routes JSON-RPC requests to appropriate methods
        
        Args:
            raw_request: Raw JSON-RPC request
            
        Returns:
            JSON-RPC response or None for notifications
        """
        method = raw_request.get("method")
        params = raw_request.get("params", {})
        request_id = raw_request.get("id")
        
        try:
            # Handle initialize request
            if method == "initialize":
                # Create InitializeRequest object from raw JSON
                init_request = InitializeRequest(
                    method="initialize",
                    params=params
                )
                
                # Handle initialization
                result = self.handle_initialize(init_request)
                
                # Return JSON-RPC response
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result.model_dump()  # Convert Pydantic model to dict
                }
            
            # Handle initialized notification (no response needed)
            elif method == "notifications/initialized":
                self.handle_notifications_initialized()
                return None  # Notifications don't get responses
            
            # Handle unknown methods
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,  # Method not found
                        "message": f"Method '{method}' not implemented"
                    }
                }
        
        except Exception as e:
            # Return error response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,  # Internal error
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """
        Main server loop - reads JSON-RPC messages from stdin
        """
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse JSON-RPC request
                    request = json.loads(line)
                    
                    # Handle request
                    response = self.handle_request(request)
                    
                    # Send response (if not a notification)
                    if response is not None:
                        print(json.dumps(response))
                        sys.stdout.flush()
                
                except json.JSONDecodeError as e:
                    # Handle parse error
                    error_response = JSONRPCError(
                        jsonrpc="2.0",
                        id = "1",
                        error = ErrorData(
                            code = 0,
                            message=f"Error parsing stdin: {e}"
                        )
                    )
                    print(json.dumps(error_response))
                    sys.stdout.flush()
        
        except KeyboardInterrupt:
            print("Server shutting down...", file=sys.stderr)


def main():
    """
    Entry point - create and run the server
    """
    server = MCPServer(
        server_name="Barebones MCP Server",
        server_version="1.12.2"
    )
    
    print("Starting MCP Server...", file=sys.stderr)
    server.run()


if __name__ == "__main__":
    main()

