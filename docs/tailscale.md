# Exposing contextkeep over Tailscale (recommended)

The compose file binds the MCP port to `127.0.0.1:8080` on the host, so it is
**not** reachable from the public internet. Tailscale lets your other devices
(laptop, phone) reach it over an encrypted private mesh — without opening any
firewall port.

## 1. Install Tailscale on the server
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up
Follow the auth URL. Note the machine's MagicDNS name (e.g. `myserver.tailnet-xxxx.ts.net`).

## 2. Serve the local port to your tailnet
Keep Docker bound to loopback, and let Tailscale proxy it privately:

    sudo tailscale serve --bg 8080

This publishes `http://<magicdns-name>:8080` to devices on your tailnet only.
(Check `tailscale serve status`. Syntax can vary by Tailscale version — see
`tailscale serve --help` if your build differs.)

## 3. Point your clients at it
Use `http://<magicdns-name>:8080/mcp` in `clients/cursor-mcp.json` or the
`mcp-remote` bridge in `clients/claude_desktop_config.json`. Your phone and
laptop must be signed into the same tailnet.

## Why not just publish 0.0.0.0:8080?
Because this endpoint has no auth and holds your personal context. Anything
that can reach the port can read/write your memory. Tailscale = private by
default. If you must use a VPS without Tailscale, put it behind an
authenticating reverse proxy (e.g. Caddy + basic auth or mTLS) and firewall
everything else.
