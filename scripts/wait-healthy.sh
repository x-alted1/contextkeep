#!/usr/bin/env bash
# Wait until qdrant, ollama, and memory report healthy in docker compose.
set -euo pipefail
cd "$(dirname "$0")/.."

TIMEOUT="${1:-300}"
INTERVAL=5
elapsed=0
services=(qdrant ollama memory)

echo "Waiting up to ${TIMEOUT}s for ${services[*]} to become healthy..."

while [ "$elapsed" -lt "$TIMEOUT" ]; do
  all_healthy=true
  for svc in "${services[@]}"; do
    status="$(docker compose ps "$svc" --format '{{.Health}}' 2>/dev/null || true)"
    if [ "$status" != "healthy" ]; then
      all_healthy=false
      echo "  ${svc}: ${status:-starting}"
    fi
  done
  if $all_healthy; then
    echo "All services healthy."
    exit 0
  fi
  sleep "$INTERVAL"
  elapsed=$((elapsed + INTERVAL))
done

echo "Timed out waiting for services to become healthy." >&2
docker compose ps
exit 1
