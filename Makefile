dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	uv run python3 -m script.ingest

test:
	uv run pytest -v

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-seed:
	docker-compose exec app uv run python3 -m script.ingest
