# Wiring clients to contextkeep

Install the stack on a **server** ([docs/server-setup.md](../docs/server-setup.md)). Clients only need the MCP URL ([docs/client-setup.md](../docs/client-setup.md)).

Your server exposes:

    http://<host>:8080/mcp        (streamable-http)

where `<host>` is your Tailscale MagicDNS name, or `127.0.0.1` if the client is on the same machine.

## Connection styles

1. **Native remote MCP (URL)** — recent Cursor, Windsurf, Cline. See `cursor-mcp.json`.
2. **stdio bridge (`mcp-remote`)** — Claude Desktop fallback. See `claude_desktop_config.json`. Requires Node.js on the client.

## Make the model actually USE it

**Cursor:** copy the shipped rule:

```bash
cp ../.cursor/rules/contextkeep-memory.mdc ~/.cursor/rules/
```

**Claude / others:** add to project instructions:

    At the start of each session, call search_memory for relevant context
    before asking me to re-explain anything. Whenever you learn a durable
    fact about me, call add_memory to store it.

## Verify reachability

```bash
curl -i http://<host>:8080/mcp
# HTTP 4xx is fine — the endpoint is up
```

## Memory workflow

| File | Role |
|---|---|
| `context/context.md` (server) | You edit — canonical |
| `context/inbox.md` (server) | Auto — review & merge into context.md |
| Client MCP config | URL only — no local Docker |

After merging inbox → `context.md`, run `make sync` on the server.
