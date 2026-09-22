.PHONY: install install-dev lint fmt test test-network run docker-build docker-up docker-down

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

lint:
	ruff check .

fmt:
	black .
	ruff check --fix .

test:
	pytest -m "not network"

test-network:
	pytest

run:
	python dashboard.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
