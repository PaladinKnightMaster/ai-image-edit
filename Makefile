.PHONY: dev dev-backend dev-frontend dev-worker lint test

# Convenience targets only. On Windows, the profile-aware backend entrypoints are:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode main
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode fast-check

ifeq ($(OS),Windows_NT)
BACKEND_DEV_CMD = powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1 -Mode main
else
BACKEND_DEV_CMD = cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
endif

dev:
	@$(MAKE) -j 2 dev-backend dev-frontend

dev-backend:
	@$(BACKEND_DEV_CMD)

dev-frontend:
	@cd frontend && npm run dev

dev-worker:
	@cd backend && python -m uvicorn worker.main:app --reload --host 0.0.0.0 --port 8001

lint:
	@cd backend && python -m ruff check .
	@cd backend && python -m ruff format --check .
	@cd frontend && npm run lint

test:
	@cd backend && python -m unittest discover -s tests

