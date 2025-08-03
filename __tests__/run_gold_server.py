from mcp.server.fastmcp import FastMCP
"""
Subprocess script to run the official implementation for a MCP server for testing
"""

gold_server = FastMCP("Barebones MCP Server")

if __name__ == "__main__":
    gold_server.run()
