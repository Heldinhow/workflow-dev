.PHONY: api ui dev docker-up docker-down docker-logs

ROOT := $(shell git rev-parse --show-toplevel)

api:
	cd $(ROOT) && \
	source .venv/bin/activate && \
	uvicorn dev_workflow.api.server:app --reload --port 8000

ui:
	cd $(ROOT)/frontend && npm run dev

dev:
	@echo "Start two terminals:"
	@echo "  Terminal 1: make api"
	@echo "  Terminal 2: make ui"

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
