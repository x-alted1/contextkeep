# contextkeep — convenience targets
SHELL := /bin/bash

.PHONY: help bootstrap up down restart logs build pull-models seed sync list nuke status wait-healthy healthcheck check-docker

help:
	@echo "contextkeep targets:"
	@echo "  make bootstrap    - first-run: up, wait healthy, pull models, seed, verify"
	@echo "  make up           - build + start the stack (detached)"
	@echo "  make wait-healthy - block until qdrant, ollama, memory are healthy"
	@echo "  make pull-models  - download the local LLM + embedding models into Ollama"
	@echo "  make seed         - ingest ./context/context.md into memory"
	@echo "  make sync         - re-index context.md after edits (same as seed)"
	@echo "  make list         - print all stored memories for CONTEXT_USER_ID"
	@echo "  make healthcheck  - verify qdrant, ollama, and MCP are responding"
	@echo "  make logs         - tail logs"
	@echo "  make status       - show container + health status"
	@echo "  make down         - stop the stack"
	@echo "  make nuke         - stop AND delete all data volumes (irreversible)"

bootstrap: check-docker
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")
	$(MAKE) up
	$(MAKE) wait-healthy
	$(MAKE) pull-models
	$(MAKE) seed
	$(MAKE) healthcheck

check-docker:
	@command -v docker >/dev/null 2>&1 || { \
	  echo "ERROR: docker not found." >&2; \
	  echo "Install Docker Desktop for Mac, then start it before running make bootstrap:" >&2; \
	  echo "  brew install --cask docker" >&2; \
	  echo "  open /Applications/Docker.app" >&2; \
	  echo "Docs: https://docs.docker.com/desktop/setup/install/mac-install/" >&2; \
	  exit 1; \
	}
	@docker info >/dev/null 2>&1 || { \
	  echo "ERROR: Docker is installed but the daemon is not running." >&2; \
	  echo "Start Docker Desktop, wait until it shows 'Running', then retry:" >&2; \
	  echo "  open /Applications/Docker.app" >&2; \
	  exit 1; \
	}

up: check-docker
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

build:
	docker compose build

logs:
	docker compose logs -f --tail=100

status:
	docker compose ps

wait-healthy:
	@./scripts/wait-healthy.sh

healthcheck:
	@./scripts/healthcheck.sh

pull-models:
	@./scripts/init-ollama.sh

seed:
	docker compose exec memory python seed.py

sync:
	docker compose exec memory python sync.py

list:
	@set -a; source .env; set +a; \
	docker compose exec memory python -c "import memory_layer as m,os; \
import json; print(json.dumps(m.get_all(os.environ.get('CONTEXT_USER_ID','me')), indent=2))"

nuke:
	docker compose down -v
