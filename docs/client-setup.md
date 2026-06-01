# Client setup

Your **server** runs contextkeep. This guide wires **clients** (Mac, Windows, etc.) to that server — no local Docker required.

## 1. Get your MCP URL

From the server admin (or Tailscale):

```
http://<server-hostname>:8080/mcp
```

Verify from a client on the same tailnet:

```bash
curl -i http://<server-hostname>:8080/mcp
# HTTP 4xx is fine — it means the endpoint is reachable
```

## 2. Cursor

Edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project):

```json
{
  "mcpServers": {
    "contextkeep": {
      "url": "http://<server-hostname>:8080/mcp"
    }
  }
}
```

Copy the rule from this repo into your project or user rules:

```bash
mkdir -p ~/.cursor/rules
cp /path/to/contextkeep/.cursor/rules/contextkeep-memory.mdc ~/.cursor/rules/
```

Or paste the rule text from [clients/README.md](../clients/README.md).

Restart Cursor after changing MCP config.

## 3. Claude Desktop

If your plan supports remote MCP, add the URL as a custom connector in Settings.

Otherwise use the stdio bridge (requires Node.js on the client):

```json
{
  "mcpServers": {
    "contextkeep": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://<server-hostname>:8080/mcp"]
    }
  }
}
```

See [clients/claude_desktop_config.json](../clients/claude_desktop_config.json).

## 4. Other MCP clients

Any client that supports **streamable HTTP** remote MCP can use the same URL. Replace `YOUR-TAILSCALE-HOSTNAME` in [clients/cursor-mcp.json](../clients/cursor-mcp.json).

## 5. Make the model use memory

Tools only help if the model calls them. Use the Cursor rule in `.cursor/rules/contextkeep-memory.mdc`, or add equivalent instructions to Claude project settings:

> At session start, call `search_memory` before asking me to re-explain context. When you learn a durable fact about me, call `add_memory`.

## Workflow reminder

| Where | What |
|---|---|
| Server `context/context.md` | You edit — canonical identity & preferences |
| Server `context/inbox.md` | Auto — facts from `add_memory` |
| Your clients | MCP URL only — no local stack |

Merge inbox → context.md on the server, then `make sync`.
