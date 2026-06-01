# Wiring clients to contextkeep

Your server exposes an MCP endpoint at:

    http://<host>:8080/mcp        (streamable-http)

where `<host>` is your Tailscale MagicDNS name or tailnet IP (recommended),
or `127.0.0.1` if the client runs on the same machine as the server.

## Two connection styles

1. **Native remote MCP (URL).** Clients that support remote MCP servers
   (recent Cursor, Windsurf, Cline, and Claude Desktop on supporting plans)
   take the URL directly. See `cursor-mcp.json`.

2. **stdio bridge (`mcp-remote`).** For clients that only speak stdio MCP,
   use the `npx -y mcp-remote <url>` shim. See `claude_desktop_config.json`.
   Requires Node.js on the client machine.

## Make the model actually USE it

Add a rule like this to the client's system/rules surface
(e.g. Claude Desktop project instructions, Cursor Rules, or ~/.claude/CLAUDE.md):

    At the start of each session, call `search_memory` for relevant context
    before asking me to re-explain anything. Whenever you learn a durable
    fact about me, my preferences, my projects, or people I work with, call
    `add_memory` to store it. Refer to this as your "memory".

## Verify it's reachable

    curl -i http://<host>:8080/mcp
    # An MCP endpoint will respond (often 400/406 to a bare GET) — that's
    # enough to confirm the port is open and serving. Use a real MCP client
    # for actual tool calls.
