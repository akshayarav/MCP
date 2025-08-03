# Universal MCP Server

A model-agnostic Model Context Protocol (MCP) server implementation that works with any compatible AI model or client, not just Claude Desktop. This project was created to help me understand the MCP protocol and is modeled after the [official MCP server specification](https://modelcontextprotocol.io/specification/2025-06-18).

## Project Goals

- **Universal Compatibility**: Works with any model that supports MCP (Claude, local models via Hugging Face, OpenAI, etc.)
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
# Install dependencies
pip install -r requirements.txt

# Run the server (communicates via stdio)
python mcp_server.py --allowed-paths ./data ./documents

# Test with a simple echo
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python mcp_server.py
```

### Integrating with Models

#### Claude Desktop
```json
{
  "mcpServers": {
    "file-tools": {
      "command": "python",
      "args": ["path/to/mcp_server.py", "--allowed-paths", "./data"]
    }
  }
}
```

#### Hugging Face Models
```python
from mcp_client import MCPClient
from transformers import pipeline

# Initialize your model
model = pipeline("text-generation", model="microsoft/DialoGPT-medium")

# Connect to MCP server
mcp_client = MCPClient("python mcp_server.py")

# Use tools through the model
response = model("Can you read the file data/example.txt?")
tool_result = mcp_client.call_tool("read_file", {"path": "data/example.txt"})
```

## Available Tools

### File Operations
- **`read_file`**: Read contents of a file within allowed paths
- **`list_directory`**: List files and folders in a directory
- **`file_info`**: Get file metadata (size, modified date, etc.)

### Planned Tools
- **`write_file`**: Write content to files
- **`search_files`**: Search for text within files
- **`execute_command`**: Run system commands (with safety restrictions)

## Project Structure

```
universal-mcp-server/
├── mcp_server.py           # Main MCP server implementation
├── mcp_client.py           # Generic client for any model
├── tools/
│   ├── __init__.py
│   ├── file_tools.py       # File operation tools
│   └── system_tools.py     # System information tools
├── examples/
│   ├── huggingface_client.py
│   ├── openai_client.py
│   └── test_tools.py
├── config/
│   └── server_config.yaml
├── requirements.txt
└── README.md
```

## Configuration

### Server Configuration (`config/server_config.yaml`)
```yaml
server:
  name: "Universal File Tools"
  version: "1.0.0"
  
security:
  allowed_paths:
    - "./data"
    - "./documents"
  max_file_size: "10MB"
  
tools:
  file_reader:
    enabled: true
  file_writer:
    enabled: false  # Disabled by default for security
```

### Command Line Options
```bash
python mcp_server.py \
  --config config/server_config.yaml \
  --allowed-paths ./data ./docs \
  --max-file-size 5MB \
  --log-level INFO
```

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

### Integration Tests
```bash
# Test with different models
python examples/test_huggingface.py
python examples/test_openai.py
```