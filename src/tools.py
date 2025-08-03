"""
Defines the tools available in the MCP server.
"""

from mcp.types import (
    Tool,
)

from typing import Dict, Any, Optional


class MCPTool:
    """
    Base class for all MCP tools.
    Each tool should implement the `call` method.
    """

    def __init__(self, name: str, title: str, description, input_schema):
        self.name = name
        self.title = title
        self.description = description
        self.input_schema = input_schema

    def call(self, arguments: dict) -> dict:
        """
        Call the tool with the provided arguments.

        Args:
            arguments: Dictionary of arguments for the tool

        Returns:
            Dictionary containing the result of the tool call
        """
        raise NotImplementedError("Subclasses must implement this method")

    def to_tool(self) -> Tool:
        """
        Convert the tool to a Tool object.

        Returns:
            Tool object representing this MCP tool
        """
        return Tool(
            name=self.name,
            title=self.title,
            description=self.description,
            inputSchema=self.input_schema,
        )


class Greeting(MCPTool):
    """
    A simple tool that returns a greeting message.
    """

    def __init__(self):
        input_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the user"}
            },
            "required": ["name"],
        }
        super().__init__(
            name="greeting",
            title="Greeting Tool",
            description="Returns a greeting message with the user's name.",
            input_schema=input_schema,
        )

    def call(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Returns a greeting message.

        Args:
            arguments: Dictionary containing the user's name

        Returns:
            Dictionary with a greeting message
        """
        if not arguments or "name" not in arguments:
            raise ValueError("Missing 'name' argument in tool call")
        return {"message": f"Hello from the MCP Server {arguments['name']}!"}


class ReadFileTool(MCPTool):
    """
    A tool that reads the contents of a file.
    """

    def __init__(self):
        input_schema = {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["file_path"],
        }
        super().__init__(
            name="read_file",
            title="Read File Tool",
            description="Reads the contents of a specified file.",
            input_schema=input_schema,
        )

    def call(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Reads the contents of a file.

        Args:
            arguments: Dictionary containing the file path

        Returns:
            Dictionary with the file contents
        """
        if not arguments or "file_path" not in arguments:
            raise ValueError("Missing 'file_path' argument in tool call")

        file_path = arguments["file_path"]
        try:
            with open(file_path, "r") as file:
                content = file.read()
            return {"content": content}
        except Exception as e:
            raise ValueError(f"Error reading file '{file_path}': {str(e)}")


class WriteFileTool(MCPTool):
    """
    A tool that writes content to a file.
    """

    def __init__(self):
        input_schema = {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["file_path", "content"],
        }
        super().__init__(
            name="write_file",
            title="Write File Tool",
            description="Writes content to a specified file.",
            input_schema=input_schema,
        )

    def call(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Writes content to a file.

        Args:
            arguments: Dictionary containing the file path and content

        Returns:
            Dictionary with a success message
        """
        if not arguments or "file_path" not in arguments or "content" not in arguments:
            raise ValueError("Missing 'file_path' or 'content' argument in tool call")

        file_path = arguments["file_path"]
        content = arguments["content"]
        try:
            with open(file_path, "w") as file:
                file.write(content)
            return {"message": f"Content written to {file_path}"}
        except Exception as e:
            raise ValueError(f"Error writing to file '{file_path}': {str(e)}")
