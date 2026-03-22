"""
p9i REST API - HTTP API for MCP Tools

Simple REST API wrapper that exposes MCP tools via HTTP endpoints.
Run alongside MCP server or import directly.
"""

import json
import os
import asyncio
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI(title="p9i REST API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tool request model
class ToolRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = {}


# In-memory MCP tool registry (populated dynamically)
_mcp_tools = {}


def register_tool(name: str, func):
    """Register an MCP tool function."""
    _mcp_tools[name] = func


@app.on_event("startup")
async def load_tools():
    """Load MCP tools from the server module."""
    try:
        # Import server tools
        import sys
        sys.path.insert(0, "/app")

        # Import main server module
        from src.api import server

        # Register key tools
        tool_mappings = {
            "get_available_mcp_tools": server.get_available_mcp_tools,
            "list_prompts": server.list_prompts,
            "get_project_memory": server.get_project_memory,
            "save_project_memory": server.save_project_memory,
            "generate_jwt_token": server.generate_jwt_token,
            "validate_jwt_token": server.validate_jwt_token,
            "generate_tailwind": server.generate_tailwind,
            "generate_shadcn": server.generate_shadcn,
            "generate_textual": server.generate_textual,
            "generate_tauri": server.generate_tauri,
            "get_figma_file": server.get_figma_file,
            "get_figma_components": server.get_figma_components,
            "get_figma_styles": server.get_figma_styles,
            "export_figma_nodes": server.export_figma_nodes,
            "figma_to_code": server.figma_to_code,
        }

        for name, func in tool_mappings.items():
            if func:
                register_tool(name, func)

    except Exception as e:
        print(f"Warning: Could not load MCP tools: {e}")


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "server": "p9i"}


@app.post("/api/call")
async def call_tool(request: ToolRequest):
    """Call an MCP tool via REST API."""
    tool_name = request.tool

    if tool_name not in _mcp_tools:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

    tool_func = _mcp_tools[tool_name]

    try:
        # Call the tool
        import inspect
        if inspect.iscoroutinefunction(tool_func):
            result = await tool_func(**request.arguments)
        else:
            result = tool_func(**request.arguments)

        # Handle result - convert to JSON if needed
        if hasattr(result, '__dict__'):
            result = result.__dict__

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools")
async def list_tools():
    """List available tools."""
    return {"tools": list(_mcp_tools.keys())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
