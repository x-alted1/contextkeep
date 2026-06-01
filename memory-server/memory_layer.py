"""
memory_layer.py
---------------
Thin wrapper that builds a mem0 `Memory` instance configured to run FULLY LOCAL:
  - LLM (fact extraction)      -> Ollama
  - Embeddings                 -> Ollama
  - Vector store               -> Qdrant

Nothing leaves the host unless you deliberately point MEM0_LLM_* at a cloud API.

NOTE ON VERSIONS: mem0's config schema and return shapes change between releases.
This targets the `mem0ai` config style documented as of early 2026. If `Memory.from_config`
rejects a key, check the current docs at https://docs.mem0.ai and adjust here only.
"""

import json
import os
import urllib.error
import urllib.request
from functools import lru_cache

from mem0 import Memory

import context_io


def _ollama_base() -> str:
    return os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434").rstrip("/")


def _ollama_tags() -> list[str]:
    req = urllib.request.Request(f"{_ollama_base()}/api/tags")
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    return [m.get("name", "") for m in data.get("models", []) if m.get("name")]


def _model_available(name: str, available: list[str]) -> bool:
    if name in available:
        return True
    base = name.split(":")[0]
    return any(m == name or m.startswith(f"{name}:") or m.startswith(f"{base}:") for m in available)


def _require_ollama_models() -> None:
    llm_model = os.environ.get("MEM0_LLM_MODEL", "llama3.1:8b")
    embed_model = os.environ.get("MEM0_EMBED_MODEL", "nomic-embed-text")
    try:
        available = _ollama_tags()
    except Exception as e:  # noqa: BLE001 - surface a clear bootstrap hint
        raise RuntimeError(
            f"Could not reach Ollama at {_ollama_base()}: {e}. "
            "Start the stack with 'make up' first."
        ) from e

    missing = [m for m in (llm_model, embed_model) if not _model_available(m, available)]
    if missing:
        raise RuntimeError(
            f"Ollama is missing required models: {', '.join(missing)}. "
            "Run 'make pull-models' (or 'make bootstrap') first."
        )


def _probe_embedding_dims() -> int:
    model = os.environ.get("MEM0_EMBED_MODEL", "nomic-embed-text")
    payload = json.dumps({"model": model, "prompt": "dimension probe"}).encode()
    req = urllib.request.Request(
        f"{_ollama_base()}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(
            f"Ollama embedding probe failed for '{model}' ({e.code}): {body}. "
            "Run 'make pull-models' first."
        ) from e

    embedding = data.get("embedding")
    if not embedding and data.get("embeddings"):
        embedding = data["embeddings"][0]
    if not embedding:
        raise RuntimeError(f"Unexpected Ollama embeddings response: {data!r}")
    return len(embedding)


def _validate_embedding_dims() -> None:
    configured = int(os.environ.get("MEM0_EMBED_DIMS", "768"))
    actual = _probe_embedding_dims()
    if actual != configured:
        model = os.environ.get("MEM0_EMBED_MODEL", "nomic-embed-text")
        raise ValueError(
            f"MEM0_EMBED_DIMS={configured} but '{model}' produces {actual}-dim vectors. "
            f"Update MEM0_EMBED_DIMS in .env (nomic-embed-text = 768)."
        )


def ensure_ready() -> None:
    """Fail fast if Ollama models or embedding dimensions are not ready."""
    _require_ollama_models()
    _validate_embedding_dims()


def _config() -> dict:
    ollama_base = _ollama_base()
    qdrant_host = os.environ.get("QDRANT_HOST", "qdrant")
    qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
    llm_model = os.environ.get("MEM0_LLM_MODEL", "llama3.1:8b")
    embed_model = os.environ.get("MEM0_EMBED_MODEL", "nomic-embed-text")
    embed_dims = int(os.environ.get("MEM0_EMBED_DIMS", "768"))  # nomic-embed-text = 768
    collection = os.environ.get("QDRANT_COLLECTION", "contextkeep")

    cfg = {
        "llm": {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "ollama_base_url": ollama_base,
                "temperature": 0.1,
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": embed_model,
                "ollama_base_url": ollama_base,
            },
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "host": qdrant_host,
                "port": qdrant_port,
                "collection_name": collection,
                "embedding_model_dims": embed_dims,
            },
        },
    }

    neo4j_url = os.environ.get("NEO4J_URL")
    if neo4j_url:
        cfg["graph_store"] = {
            "provider": "neo4j",
            "config": {
                "url": neo4j_url,
                "username": os.environ.get("NEO4J_USER", "neo4j"),
                "password": os.environ.get("NEO4J_PASSWORD", "contextkeep"),
            },
        }

    return cfg


@lru_cache(maxsize=1)
def get_memory() -> Memory:
    """Build (once) and return a configured mem0 Memory instance."""
    ensure_ready()
    return Memory.from_config(_config())


def _extract_items(result) -> list[dict]:
    if isinstance(result, dict):
        result = result.get("results", result.get("memories", []))
    items: list[dict] = []
    for r in result or []:
        if isinstance(r, dict):
            text = r.get("memory") or r.get("text") or str(r)
            items.append({"id": r.get("id"), "memory": text})
        else:
            items.append({"id": None, "memory": str(r)})
    return items


def _normalize(result) -> list[str]:
    return [i["memory"] for i in _extract_items(result)]


def add(text: str, user_id: str, *, record_inbox: bool = True) -> str:
    res = get_memory().add(text, user_id=user_id)
    if record_inbox:
        context_io.append_inbox(text, user_id)
    return f"stored ({len(_normalize(res)) or 1} item(s))"


def search(query: str, user_id: str, limit: int = 5) -> list[str]:
    return _normalize(get_memory().search(query, user_id=user_id, limit=limit))


def get_all(user_id: str) -> list[str]:
    return _normalize(get_memory().get_all(user_id=user_id))


def list_with_ids(user_id: str) -> list[str]:
    """Return memories formatted with ids when mem0 provides them."""
    items = _extract_items(get_memory().get_all(user_id=user_id))
    out: list[str] = []
    for item in items:
        mid = item.get("id")
        if mid:
            out.append(f"{mid}: {item['memory']}")
        else:
            out.append(item["memory"])
    return out


def delete_one(memory_id: str, user_id: str) -> str:
    m = get_memory()
    try:
        m.delete(memory_id=memory_id, user_id=user_id)
    except TypeError:
        m.delete(memory_id=memory_id)
    return f"deleted memory {memory_id}"


def delete_all(user_id: str, *, confirm: bool = False) -> str:
    if os.environ.get("CONFIRM_DELETE") != "1" and not confirm:
        raise RuntimeError(
            "Refusing to delete all memories. Set CONFIRM_DELETE=1 in .env or pass confirm=True."
        )
    get_memory().delete_all(user_id=user_id)
    return f"deleted all memories for '{user_id}'"
