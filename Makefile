.PHONY: api ui dev

api:
	cd /Users/helder/Projetos/workflow-dev && \
	source .venv/bin/activate && \
	uvicorn dev_workflow.api.server:app --reload --port 8000

ui:
	cd /Users/helder/Projetos/workflow-dev/frontend && npm run dev

dev:
	@echo "Start two terminals:"
	@echo "  Terminal 1: make api"
	@echo "  Terminal 2: make ui"
