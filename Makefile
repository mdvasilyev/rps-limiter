format:
	isort .
	black .

revision:
	poetry run alembic revision --autogenerate -m "$(m)"

upgrade:
	poetry run alembic upgrade head

downgrade:
	poetry run alembic downgrade -1

run-fastapi:
	PYTHONPATH=. poetry run python src/application/main.py

run-faststream:
	PYTHONPATH=. poetry run python src/application/workers/fetch_and_process.py

up:
	docker compose up

up-build:
	docker compose up --build
