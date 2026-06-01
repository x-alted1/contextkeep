#!/usr/bin/env bash
# Quick sanity check of the three services. Exits non-zero on failure.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0

echo "== containers =="
docker compose ps
echo

echo "== qdrant =="
if docker compose exec -T qdrant sh -c 'wget -qO- http://localhost:6333/healthz' >/dev/null 2>&1; then
  echo "ok"
else
  echo "FAIL: qdrant healthz unreachable" >&2
  fail=1
fi
echo

echo "== ollama models =="
if docker compose exec -T ollama ollama list; then
  :
else
  echo "FAIL: ollama list failed" >&2
  fail=1
fi
echo

echo "== mcp port (host loopback) =="
code="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/mcp || true)"
if [ -n "$code" ] && [ "$code" != "000" ]; then
  echo "ok (HTTP ${code})"
else
  echo "FAIL: no response from http://127.0.0.1:8080/mcp" >&2
  fail=1
fi

exit "$fail"
