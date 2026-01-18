.PHONY: dev dev-backend dev-frontend lint test

dev:
	@$(MAKE) -j 2 dev-backend dev-frontend

dev-backend:
	@cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@cd frontend && npm run dev

lint:
	@cd backend && python -m ruff check .
	@cd backend && python -m ruff format --check .
	@cd frontend && npm run lint

test:
	@cd backend && python -m unittest discover -s tests

