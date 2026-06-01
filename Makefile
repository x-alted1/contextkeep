# contextkeep — convenience targets
SHELL := /bin/bash

.PHONY: help up down restart logs build pull-models seed list nuke status

help:
	@echo "contextkeep targets:"
	@echo "  make up           - build + start the stack (detached)"
	@echo "  make pull-models  - download the local LLM + embedding models into Ollama"
	@echo "  make seed         - ingest ./context/context.md into memory"
	@echo "  make list         - print all stored memories for CONTEXT_USER_ID"
	@echo "  make logs         - tail logs"
	@echo "  make status       - show container + health status"
	@echo "  make down         - stop the stack"
	@echo "  make nuke         - stop AND delete all data volumes (irreversible)"

up:
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

# Pull models named in .env into the Ollama container.
pull-models:
	@set -a; source .env; set +a; \
	echo "Pulling $$MEM0_LLM_MODEL ..."; docker compose exec ollama ollama pull "$$MEM0_LLM_MODEL"; \
	echo "Pulling $$MEM0_EMBED_MODEL ..."; docker compose exec ollama ollama pull "$$MEM0_EMBED_MODEL"

seed:
	docker compose exec memory python seed.py

list:
	@set -a; source .env; set +a; \
	docker compose exec memory python -c "import memory_layer as m,os; \
import json; print(json.dumps(m.get_all(os.environ.get('CONTEXT_USER_ID','me')), indent=2))"

nuke:
	docker compose down -v
