# contextkeep

**A self-hosted, fully-local memory layer you own — so the same personal AI context follows you across Claude, Cursor, ChatGPT, and any other MCP-capable tool, with nothing stored on a vendor's servers.**

This is the "own your context" stack: a small Docker deployment of [mem0](https://github.com/mem0ai/mem0) wired to local [Ollama](https://ollama.com) (for fact extraction + embeddings) and [Qdrant](https://qdrant.tech) (for the vector store), exposed over the [Model Context Protocol](https://modelcontextprotocol.io) so every AI client reads and writes the *same* memory. You seed it from a plain-Markdown Master Context File that stays your source of truth.

Unlike a hosted memory product, no third party ever sees your context in the default configuration.

---

## Architecture

```
                 ┌─────────────────────────────────────────────┐
   Claude Desktop │                   your server               │
   Cursor / Cline │   ┌──────────────┐                          │
   Windsurf  ─────┼──▶│ memory (MCP) │── extracts via ──▶ ┌────────────┐
   (over Tailscale)│  │  FastMCP +   │                    │   ollama   │
                 │   │    mem0      │── embeds via ─────▶ │ (local LLM │
                 │   └──────┬───────┘                    │ + embedder)│
                 │          │ stores vectors             └────────────┘
                 │          ▼                                   │
                 │   ┌────────────┐         (optional)   ┌────────────┐
                 │   │   qdrant   │                       │   neo4j    │
                 │   │ (vectors)  │                       │  (graph)   │
                 │   └────────────┘                       └────────────┘
                 └─────────────────────────────────────────────┘
   seed source: ./context/context.md  (your Master Context File)
```

The MCP port binds to `127.0.0.1` on the host and is published privately to your devices over Tailscale — never the open internet.

---

## Requirements

- A Linux server (mini PC, NAS, old laptop, or VPS). For the default `llama3.1:8b` extractor, budget **~8 GB RAM**; on smaller boxes set `MEM0_LLM_MODEL=llama3.2:3b` in `.env`. A GPU helps but isn't required.
- **Docker** + **Docker Compose v2**.
- **Tailscale** (recommended) for private multi-device/mobile access.
- **Node.js** on client machines only if you use the `mcp-remote` bridge.

---

## Quick start

```bash
# 1. Clone and configure
git clone <your-fork-url> contextkeep && cd contextkeep
cp .env.example .env
# (edit .env if you want a smaller model or a different user id)

# 2. Edit your context — this is your source of truth
$EDITOR context/context.md

# 3. Start the stack
make up

# 4. Pull the local models into Ollama (one-time, can take a few minutes)
make pull-models

# 5. Seed your context into memory
make seed

# 6. Verify
make list          # should print consolidated memories
./scripts/healthcheck.sh
```

Then expose it privately and wire up a client:

```bash
# expose to your tailnet (see docs/tailscale.md)
sudo tailscale serve --bg 8080
```

Point a client at `http://<your-tailscale-name>:8080/mcp` — see [`clients/`](clients/README.md) for Claude Desktop and Cursor configs, and the one-paragraph rule that makes the model actually call `search_memory`/`add_memory`.

---

## How it works day to day

1. **At session start**, your client calls `search_memory` and loads what's already known about you.
2. **As you work**, the model calls `add_memory` when it learns something durable. mem0 runs the local LLM to extract, de-duplicate, and consolidate — you don't get raw transcript dumps, you get clean facts.
3. **Your Markdown file stays canonical.** Re-run `make seed` after editing it. The vector store is a queryable cache built from (and added to beyond) that file.

Because the interface is MCP, the *same* memory serves every compatible tool. Switch from Claude to Cursor mid-project and the context is already there.

---

## What's in the box

| Path | Purpose |
|---|---|
| `docker-compose.yml` | qdrant + ollama + memory (+ optional neo4j `graph` profile) |
| `memory-server/` | FastMCP server (`server.py`), mem0 wrapper (`memory_layer.py`), seeder (`seed.py`) |
| `context/context.md` | Master Context File template — **edit this** |
| `clients/` | Claude Desktop / Cursor MCP configs + wiring guide |
| `scripts/` | model pull + healthcheck helpers |
| `docs/tailscale.md` | private remote access |
| `docs/security.md` | threat model, backups, the "is it really local?" answer |
| `Makefile` | `up`, `pull-models`, `seed`, `list`, `logs`, `status`, `nuke` |

---

## Honest caveats — read before trusting this

- **It's a scaffold, not an audited product.** It runs as designed, but review the code and pin versions before relying on it for anything important.
- **Version drift is the main risk.** mem0's config schema and return shapes, and the MCP Python SDK's FastMCP API (transport names, host/port kwargs, mount path), change between releases. If something errors after `pip` resolves newer versions, check the inline `NOTE ON VERSIONS` comments in `memory_layer.py` and `server.py` against current upstream docs.
- **No built-in auth.** Security depends on the loopback bind + Tailscale (or a reverse proxy you add). Don't publish port 8080 publicly. See `docs/security.md`.
- **"Fully local" depends on your model choice.** Default = local Ollama, nothing leaves the host. Point the model env vars at a cloud API and your memories transit that API during extraction.
- **Seeding is LLM-bound.** Each line in `context.md` triggers a local extraction call, so the first `make seed` on a CPU-only box can be slow. That's expected.
- **The discipline is still yours.** This automates storage and injection; it does not maintain the accuracy of `context.md` for you. Keep that file current — it's the part that actually makes the system work.

---

## License

MIT — see [LICENSE](LICENSE).

Built on the open-source [mem0](https://github.com/mem0ai/mem0), [Qdrant](https://github.com/qdrant/qdrant), [Ollama](https://github.com/ollama/ollama), and the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). Not affiliated with any of them.
