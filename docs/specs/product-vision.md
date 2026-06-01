# contextkeep product vision

> **mem0 gives your app memory. contextkeep gives *you* memory — one Markdown file, every AI tool, your server.**

## Thesis

Two principles drive every feature decision:

1. **Universal cross-tool memory (B)** — One MCP endpoint on your server. Cursor, Claude Desktop, Windsurf, and any MCP client read and write the *same* store. No per-app SDK.

2. **Markdown-first (C)** — `context/context.md` is the source of truth you edit and version. The vector store is a searchable index built from that file plus runtime additions you choose to keep.

## Architecture

```
  Cursor / Claude / Windsurf  ──▶  MCP (Tailscale URL)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            context/context.md   context/inbox.md    Qdrant + mem0
            (you edit)           (auto on add_memory)  (local Ollama)
```

## Approach: canonical file + inbox

| Artifact | Role |
|---|---|
| `context/context.md` | Master Context File — canonical identity, preferences, projects |
| `context/inbox.md` | Append-only log of facts learned at runtime via `add_memory` |
| Vector store | Queryable index; seeded from `context.md`, updated by mem0 extraction |

**Workflow**

1. Edit `context.md` → `make sync` (or `make seed`) re-indexes into memory.
2. During sessions, clients call `add_memory` → stored in Qdrant **and** appended to `inbox.md`.
3. Periodically review `inbox.md` → merge valuable lines into `context.md` → `make sync`.

## Better than mem0

| Dimension | mem0 (hosted) | contextkeep |
|---|---|---|
| Integration | SDK per application | **One MCP URL** for all tools |
| Data location | Vendor cloud | **Your server** |
| Human-readable source | Dashboard / API | **`context.md` + git** |
| Runtime additions | Opaque store | **`inbox.md` + vector** |
| Cost model | Subscription | **Your hardware** |

## Implementation phases

### Done / in progress (P0)

- Pinned dependencies and images
- Compose healthchecks + `make bootstrap`
- Embedding dimension validation
- Server + client deployment docs

### This release

- `inbox.md` append on `add_memory`
- `make sync` re-seed from `context.md`
- Shipped Cursor rule for memory tool usage
- `delete_memory` / guarded `delete_all_memories`
- Product vision + server/client setup guides

### Next

- `make merge-inbox` helper
- `MCP_API_KEY` or reverse-proxy auth recipe
- Memory browser UI (optional)
- Export/drift report between file and vector store

## Positioning

**Target user:** Someone who uses multiple AI tools daily and wants one durable, owned context layer — not a different memory silo per vendor.

**Not competing on:** Enterprise SOC2 dashboard, managed scale, or framework-specific SDK ergonomics.

**Competing on:** Ownership, portability, MCP universality, and a Markdown file you can read at 2am.
