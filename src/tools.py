"""
Defines the tools available in the MCP server.
"""

from mcp.types import (
    Tool,
)

import os
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
                "content": {
                    "type": "string",
                    "description": "Content to write. When writing code, the content should only use comments when necessary. The code should be as concise as possible and follow the standards already present in the file. Avoid writing new helper functions over using alreadt existing implementations. Again, avoid comments and the code ideally should document itself.",
                },
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


class CreateDirectoryTool(MCPTool):
    """
    A tool that creates a directory.
    """

    def __init__(self):
        input_schema = {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Path to the directory to create"},
                "parents": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
            },
            "required": ["directory_path"],
        }
        super().__init__(
            name="create_directory",
            title="Create Directory Tool",
            description="Creates a directory at the specified path.",
            input_schema=input_schema,
        )

    def call(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Creates a directory.

        Args:
            arguments: Dictionary containing the directory path and optional parents flag

        Returns:
            Dictionary with a success message
        """
        if not arguments or "directory_path" not in arguments:
            raise ValueError("Missing 'directory_path' argument in tool call")

        directory_path = arguments["directory_path"]
        parents = arguments.get("parents", True)
        
        try:
            if os.path.exists(directory_path):
                if os.path.isdir(directory_path):
                    return {"message": f"Directory '{directory_path}' already exists"}
                else:
                    raise ValueError(f"'{directory_path}' exists but is not a directory")
            
            if parents:
                os.makedirs(directory_path, exist_ok=True)
            else:
                os.mkdir(directory_path)
            
            return {"message": f"Directory created at {directory_path}"}
        except Exception as e:
            raise ValueError(f"Error creating directory '{directory_path}': {str(e)}")


class ListDirectoryTool(MCPTool):
    """
    A tool that lists files in a directory, filtering out unnecessary files.
    """

    def __init__(self):
        input_schema = {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Path to the directory"}
            },
            "required": ["directory_path"],
        }
        super().__init__(
            name="list_directory",
            title="List Directory Tool",
            description="Lists all relevant files in a directory, filtering out cache and system files.",
            input_schema=input_schema,
        )

    def call(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Lists files in a directory, filtering out unnecessary files.

        Args:
            arguments: Dictionary containing the directory path

        Returns:
            Dictionary with lists of files and directories
        """
        if not arguments or "directory_path" not in arguments:
            raise ValueError("Missing 'directory_path' argument in tool call")

        directory_path = arguments["directory_path"]
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory '{directory_path}' does not exist")
        
        if not os.path.isdir(directory_path):
            raise ValueError(f"'{directory_path}' is not a directory")

        skip_patterns = {
            '__pycache__', '.git', '.svn', '.hg', '.bzr', 'node_modules',
            '.vscode', '.idea', '.DS_Store', 'Thumbs.db', '.pytest_cache',
            '.coverage', '.tox', '.mypy_cache', '.env', 'venv', 'env',
            '.venv', 'build', 'dist', '*.egg-info', '.cache'
        }
        
        skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.log', '.tmp', '.swp', '.bak'}

        try:
            all_items = os.listdir(directory_path)
            files = []
            directories = []
            
            for item in all_items:
                if item.startswith('.') and item not in {'.gitignore', '.env.example', '.dockerignore'}:
                    continue
                if item in skip_patterns:
                    continue
                if any(item.endswith(ext) for ext in skip_extensions):
                    continue
                if any(pattern.replace('*', '') in item for pattern in skip_patterns if '*' in pattern):
                    continue
                
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    directories.append(item)
            
            return {
                "directory": directory_path,
                "files": sorted(files),
                "directories": sorted(directories),
                "total_files": len(files),
                "total_directories": len(directories)
            }
        except Exception as e:
            raise ValueError(f"Error listing directory '{directory_path}': {str(e)}")
