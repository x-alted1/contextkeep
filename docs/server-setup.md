# Server setup

Install contextkeep on a Linux machine (VPS, mini PC, NAS, homelab). Clients on your laptop/phone only **reference** the MCP URL — they do not run Docker or Ollama.

## Requirements

- Linux with Docker + Compose v2
- ~8 GB RAM for default `llama3.1:8b` (use `llama3.2:3b` in `.env` on smaller boxes)
- [Tailscale](https://tailscale.com) on server and client devices (recommended)

## Install

```bash
git clone https://github.com/x-alted1/contextkeep.git
cd contextkeep
cp .env.example .env
$EDITOR context/context.md   # your Master Context File

make bootstrap
```

`bootstrap` starts the stack, waits for healthchecks, pulls Ollama models, seeds `context.md`, and verifies the MCP endpoint.

## Expose to your tailnet

Keep Docker bound to loopback; publish privately with Tailscale:

```bash
sudo tailscale serve --bg 8080
tailscale serve status
```

Your MCP URL:

```
http://<server-magicdns-name>:8080/mcp
```

## Day-two operations

| Task | Command |
|---|---|
| Re-index after editing `context.md` | `make sync` |
| View stored memories | `make list` |
| Check services | `make healthcheck` |
| Review runtime facts | `cat context/inbox.md` on the server |
| Logs | `make logs` |

After merging `inbox.md` into `context.md`, run `make sync`.

## Security

- Do not publish port 8080 to the public internet without an authenticating reverse proxy.
- The MCP endpoint has no built-in auth; Tailscale membership is your access control.
- See [security.md](security.md) for backups and threat model.

## Updating

```bash
git pull
docker compose pull
make up
make healthcheck
```

Re-run `make sync` if `context.md` changed upstream in the repo template (usually you keep your own file).
