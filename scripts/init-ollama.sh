#!/usr/bin/env bash
# Pull the models named in .env into the running Ollama container.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a
echo "Pulling LLM: ${MEM0_LLM_MODEL} ..."
docker compose exec ollama ollama pull "${MEM0_LLM_MODEL}"
echo "Pulling embedder: ${MEM0_EMBED_MODEL} ..."
docker compose exec ollama ollama pull "${MEM0_EMBED_MODEL}"
echo "Done. Models ready."
