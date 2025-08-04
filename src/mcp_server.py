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
    LoggingCapability,
    ListToolsResult,
    CallToolRequest,
    CallToolResult,
    TextContent,
)
from tools import Greeting, ReadFileTool, WriteFileTool, CreateDirectoryTool, ListDirectoryTool
import logging


class MCPServer:
    """
    Minimal MCP Server with proper initialization flow
    """

    def __init__(
        self, server_name: str = "Barebones MCP Server", server_version: str = "1.0.0"
    ):
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
        self.client_info = request.params.clientInfo if request.params else None

        self.initialized = True

        return InitializeResult(
            protocolVersion=self.protocol_version,
            capabilities=self.capabilities,
            serverInfo=self.server_info,
        )

    def handle_notifications_initialized(self) -> None:
        logging.info("Server fully initialized and ready!")

    def handle_list_tools(self) -> ListToolsResult:
        """
        Handle the tools/list request to return available tools

        Returns:
            ListToolsResult containing all registered tools
        """
        tools = [
            Greeting().to_tool(),
            ReadFileTool().to_tool(),
            WriteFileTool().to_tool(),
            CreateDirectoryTool().to_tool(),
            ListDirectoryTool().to_tool(),
        ]

        return ListToolsResult(tools=tools)

    def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        """
        Handle a tool call request

        Args:
            request: CallToolRequest containing tool name and arguments

        Returns:
            Result of the tool call
        """
        name = request.params.name
        arguments = request.params.arguments

        if name == "greeting":
            tool = Greeting()
            try:
                response = tool.call(arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=response["message"])]
                )
            except ValueError as e:
                logging.error(f"Error calling tool '{name}': {str(e)}\n")
                return CallToolResult(
                    content=[TextContent(type="text", text=str(e))],
                    isError=True,
                )
        elif name == "read_file":
            tool = ReadFileTool()
            try:
                response = tool.call(arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=response["content"])]
                )
            except ValueError as e:
                logging.error(f"Error calling tool '{name}': {str(e)}\n")
                return CallToolResult(
                    content=[TextContent(type="text", text=str(e))],
                    isError=True,
                )
        elif name == "write_file":
            tool = WriteFileTool()
            try:
                response = tool.call(arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=response["message"])]
                )
            except ValueError as e:
                logging.error(f"Error calling tool '{name}': {str(e)}\n")
                return CallToolResult(
                    content=[TextContent(type="text", text=str(e))],
                    isError=True,
                )
        elif name == "create_directory":
            tool = CreateDirectoryTool()
            try:
                response = tool.call(arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=response["message"])]
                )
            except ValueError as e:
                logging.error(f"Error calling tool '{name}': {str(e)}\n")
                return CallToolResult(
                    content=[TextContent(type="text", text=str(e))],
                    isError=True,
                )
        elif name == "list_directory":
            tool = ListDirectoryTool()
            try:
                response = tool.call(arguments)
                formatted_response = f"Directory: {response['directory']}\n\n"
                formatted_response += f"Files ({response['total_files']}):\n"
                for file in response['files']:
                    formatted_response += f"  {file}\n"
                formatted_response += f"\nDirectories ({response['total_directories']}):\n"
                for directory in response['directories']:
                    formatted_response += f"  {directory}/\n"
                return CallToolResult(
                    content=[TextContent(type="text", text=formatted_response)]
                )
            except ValueError as e:
                logging.error(f"Error calling tool '{name}': {str(e)}\n")
                return CallToolResult(
                    content=[TextContent(type="text", text=str(e))],
                    isError=True,
                )
        else:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=str(f"Tool '{name}' not found"))
                ],
                isError=True,
            )

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
            if method == "initialize":
                init_request = InitializeRequest(method="initialize", params=params)

                result = self.handle_initialize(init_request)
                serialized = result.model_dump(
                    exclude_none=True,
                )

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": serialized,
                }

            elif method == "notifications/initialized":
                self.handle_notifications_initialized()
                return None

            elif method == "tools/list":
                tools = self.handle_list_tools()
                serialized = tools.model_dump(
                    exclude_none=True,
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": serialized,
                }

            elif method == "tools/call":
                call_request = CallToolRequest(method="tools/call", params=params)
                result = self.handle_call_tool(call_request)
                serialized = result.model_dump(
                    exclude_none=True,
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": serialized,
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not implemented",
                    },
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,  # Internal error
                    "message": f"Internal error: {str(e)}",
                },
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
                    request = json.loads(line)

                    response = self.handle_request(request)

                    if response is not None:
                        print(json.dumps(response))
                        sys.stdout.flush()

                except json.JSONDecodeError as e:
                    # Handle parse error
                    error_response = JSONRPCError(
                        jsonrpc="2.0",
                        id="1",
                        error=ErrorData(code=0, message=f"Error parsing stdin: {e}"),
                    )
                    logging.error(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            print("Server shutting down...", file=sys.stderr)


def main():
    """
    Entry point - create and run the server
    """
    server = MCPServer(server_name="Barebones MCP Server", server_version="1.12.2")

    logging.info("Starting MCP Server...")
    server.run()


if __name__ == "__main__":
    main()
