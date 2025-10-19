install:
	uv sync

seed: install
	uv run python3 -m script.ingest

dev: install
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: install
	uv run pytest -v

.PHONY: install seed dev test
