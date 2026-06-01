"""
server.py
---------
Exposes the local mem0 memory layer as an MCP server over HTTP, so any
MCP-capable client (Claude Desktop, Cursor, Windsurf, Cline, VS Code agents)
can read/write the SAME personal context.

Transport: streamable-http (default mount path: /mcp).
Bind:      0.0.0.0:8080 inside the container; compose maps it to 127.0.0.1
           on the host so it is NOT publicly reachable. Expose to your
           devices over Tailscale (see docs/tailscale.md), never the open net.

NOTE ON VERSIONS: the `mcp` Python SDK's FastMCP API evolves. If `host`/`port`
constructor kwargs or the `transport` value are rejected by your installed
version, set FASTMCP_HOST / FASTMCP_PORT env vars instead and/or check
https://github.com/modelcontextprotocol/python-sdk for the current call.
"""

import os

from mcp.server.fastmcp import FastMCP

import memory_layer as ml

HOST = os.environ.get("MCP_HOST", "0.0.0.0")
PORT = int(os.environ.get("MCP_PORT", "8080"))
DEFAULT_USER = os.environ.get("CONTEXT_USER_ID", "me")

mcp = FastMCP("contextkeep", host=HOST, port=PORT)


@mcp.tool()
def add_memory(text: str, user_id: str = DEFAULT_USER) -> str:
    """Store a new long-term fact, preference, or standing instruction about the user.
    Also appends to context/inbox.md for later merge into context.md.
    Use when you learn something durable (identity, preferences, projects, people, decisions)."""
    return ml.add(text, user_id=user_id)


@mcp.tool()
def search_memory(query: str, user_id: str = DEFAULT_USER, limit: int = 5) -> list[str]:
    """Retrieve the most relevant stored memories for a query.
    Call this at the START of a session to load what is already known about the user."""
    return ml.search(query, user_id=user_id, limit=limit)


@mcp.tool()
def list_memories(user_id: str = DEFAULT_USER) -> list[str]:
    """Return every memory currently stored for the user (includes ids when available)."""
    return ml.list_with_ids(user_id=user_id)


@mcp.tool()
def delete_memory(memory_id: str, user_id: str = DEFAULT_USER) -> str:
    """Delete a single memory by id (from list_memories)."""
    return ml.delete_one(memory_id, user_id=user_id)


@mcp.tool()
def delete_all_memories(user_id: str = DEFAULT_USER, confirm: bool = False) -> str:
    """Permanently delete ALL stored memories for the user. Requires confirm=True."""
    return ml.delete_all(user_id=user_id, confirm=confirm)


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)
