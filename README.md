# MCP Server - From Scratch

A Model Context Protocol (MCP) server implementation developed **from scratch**. When I say scratch I literally mean, that the JSON-RPC, STDIO, and server to client connection is written by hand! This is not a simple implementation that uses the ``` @mcp.tool ``` functionality you see online. 

This project was created to help me understand the MCP protocol and was carefully modeled after the [official MCP server specification](https://modelcontextprotocol.io/specification/2025-06-18).

## Project Goals

- **Simple Architecture**: Clean, from-scratch implementation following official MCP specification
- **Extensible Tools**: Easy to add new tools and capabilities
- **Learning-Focused**: Well-documented code to understand MCP internals

## Architecture

```
┌─────────────────┐    JSON-RPC     ┌─────────────────┐
│   AI Model      │ ◄──────────────► │   MCP Server    │
│ (Any Provider)  │     (stdio)     │   (Python)      │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │     Tools       │
                                    │ • File Reader   │
                                    │ • File Writer   │
                                    │ • Directory Ops │
                                    └─────────────────┘
```

## Quick Start

### Running the MCP Server

```bash
# Create virtual environment
python3 -m venv mcp-venv

# Activate virtual environment
source mcp-venv/bin/activate  # On macOS/Linux
# or
mcp-venv\Scripts\activate     # On Windows
```

```bash
# Install required packages
pip install -r requirements.txt
```

```bash
# Test server starts correctly
python3 src/mcp_server.py
```

### Integrating with Models

#### Claude Desktop Config

For Claude Desktop, create or edit the config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`    
Add the following configuration to ` vim claude_desktop_config.json `: 

```json
{
  "mcpServers": {
    "barebones-server": {
      "command": "{project_path}/mcp-venv/bin/python",
      "args": ["{project_path}/src/mcp_server.py"],
      "env": {
        "PYTHONPATH": "{project_path}/src"
      }
    }
  }
}
```


## Available Tools

### Current Tools
- **`greeting`**: Returns a greeting message
- **`read_file`**: Read contents of a file within allowed paths
- **`write_file`**: Write content to files


### Planned Tools
- **`list_directory`**: List files and folders in a directory

## Testing

### Run with MCP Inspector
```bash
# Install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector
# Run the MCP server with Inspector
npx @modelcontextprotocol/inspector \
  /{path_to_MCP_projecct}/mcp-venv/bin/python \
  /{path_to_MCP_projecct}/src/mcp_server.py
```

### Unit Tests
```bash
python -m __tests__.main
```