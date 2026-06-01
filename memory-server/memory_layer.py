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

import os
from functools import lru_cache

from mem0 import Memory


def _config() -> dict:
    ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
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

    # OPTIONAL graph memory (entity/relationship recall) via Neo4j.
    # Enable by running the compose `graph` profile and setting NEO4J_URL.
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
    return Memory.from_config(_config())


def _normalize(result) -> list[str]:
    """mem0 returns either a list or {'results': [...]} depending on version.
    Flatten to a list of plain memory strings for MCP transport."""
    if isinstance(result, dict):
        result = result.get("results", [])
    out = []
    for r in result or []:
        if isinstance(r, dict):
            out.append(r.get("memory") or r.get("text") or str(r))
        else:
            out.append(str(r))
    return out


def add(text: str, user_id: str) -> str:
    res = get_memory().add(text, user_id=user_id)
    return f"stored ({len(_normalize(res)) or 1} item(s))"


def search(query: str, user_id: str, limit: int = 5) -> list[str]:
    return _normalize(get_memory().search(query, user_id=user_id, limit=limit))


def get_all(user_id: str) -> list[str]:
    return _normalize(get_memory().get_all(user_id=user_id))


def delete_all(user_id: str) -> str:
    get_memory().delete_all(user_id=user_id)
    return f"deleted all memories for '{user_id}'"
