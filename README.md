# contextkeep

**mem0 gives your app memory. contextkeep gives *you* memory — one Markdown file, every AI tool, your server.**

A self-hosted memory layer: [mem0](https://github.com/mem0ai/mem0) + local [Ollama](https://ollama.com) + [Qdrant](https://qdrant.tech), exposed over [MCP](https://modelcontextprotocol.io). Same personal context in Cursor, Claude Desktop, Windsurf, and any MCP client — nothing on a vendor's servers by default.

- **`context/context.md`** — Master Context File you edit (source of truth)
- **`context/inbox.md`** — runtime facts from `add_memory` (merge into `context.md` when ready)
- **Vector store** — searchable index built from both

See [docs/specs/product-vision.md](docs/specs/product-vision.md) for the full product direction.

---

## Deploy on a server, reference from clients

| Role | What to do |
|---|---|
| **Server** (Linux VPS, homelab) | [docs/server-setup.md](docs/server-setup.md) — `make bootstrap`, Tailscale |
| **Client** (Mac, laptop) | [docs/client-setup.md](docs/client-setup.md) — MCP URL only, no Docker |

---

## Architecture

```
   Cursor / Claude / Windsurf
            │
            │  MCP over Tailscale
            ▼
   ┌────────────────────────────────────────┐
   │  your server: memory (FastMCP + mem0)  │
   │         │                    │         │
   │         ▼                    ▼         │
   │  context/context.md   context/inbox.md │
   │  (you edit)            (auto append)   │
   │         │                    │         │
   │         └────────┬───────────┘         │
   │                  ▼                     │
   │            qdrant + ollama             │
   └────────────────────────────────────────┘
```

The MCP port binds to `127.0.0.1` on the host; expose privately via Tailscale ([docs/tailscale.md](docs/tailscale.md)).

---

## Quick start (server)

```bash
git clone https://github.com/x-alted1/contextkeep.git && cd contextkeep
cp .env.example .env
$EDITOR context/context.md

make bootstrap
sudo tailscale serve --bg 8080
```

Then wire clients to `http://<server-hostname>:8080/mcp` — [docs/client-setup.md](docs/client-setup.md).

Copy the Cursor rule so models actually call memory tools:

```bash
cp .cursor/rules/contextkeep-memory.mdc ~/.cursor/rules/
```

---

## How it works day to day

1. **Session start** — clients call `search_memory` to load what is already known.
2. **While working** — `add_memory` stores durable facts in Qdrant **and** appends to `inbox.md`.
3. **You stay canonical** — merge inbox into `context.md`, then `make sync` to re-index.

The same memory serves every MCP tool. Switch from Claude to Cursor and context is already there.

---

## What's in the box

| Path | Purpose |
|---|---|
| `docker-compose.yml` | qdrant + ollama + memory (+ optional neo4j `graph` profile) |
| `memory-server/` | MCP server, mem0 wrapper, seed/sync, inbox writer |
| `context/context.md` | Master Context File — **edit this** |
| `context/inbox.md` | Runtime memory inbox — review & merge |
| `.cursor/rules/` | Cursor rule to invoke memory tools |
| `clients/` | MCP config templates |
| `docs/server-setup.md` | Install on a server |
| `docs/client-setup.md` | Reference from laptops |
| `docs/specs/product-vision.md` | Product thesis |
| `Makefile` | `bootstrap`, `sync`, `seed`, `healthcheck`, … |

---

## Honest caveats

- **Scaffold, not audited product** — review before trusting with sensitive data.
- **Dependencies pinned** — bump intentionally; re-run `make bootstrap` after upgrades.
- **No built-in MCP auth** — use Tailscale or a reverse proxy; see [docs/security.md](docs/security.md).
- **Seeding is LLM-bound** — first `make bootstrap` can take a while on CPU-only hardware.
- **`delete_all_memories`** requires `confirm=True` (or `CONFIRM_DELETE=1` in `.env`).

---

## License

MIT — see [LICENSE](LICENSE).

Built on [mem0](https://github.com/mem0ai/mem0), [Qdrant](https://github.com/qdrant/qdrant), [Ollama](https://github.com/ollama/ollama), and the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). Not affiliated with any of them.
