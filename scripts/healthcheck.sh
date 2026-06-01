#!/usr/bin/env bash
# Quick local sanity check of the three services.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== containers =="
docker compose ps
echo
echo "== qdrant =="
docker compose exec qdrant sh -c 'wget -qO- http://localhost:6333/healthz || true'
echo
echo "== ollama models =="
docker compose exec ollama ollama list || true
echo
echo "== mcp port (host loopback) =="
(curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8080/mcp || echo "no response")
