dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	uv run python3 -m script.ingest

test:
	uv run pytest -v
