format:
	isort .
	black .

revision:
	poetry run alembic revision --autogenerate -m "$(m)"

upgrade:
	poetry run alembic upgrade head

downgrade:
	poetry run alembic downgrade -1

run-app:
	PYTHONPATH=. poetry run python src/application/main.py

up:
	docker compose up

up-build:
	docker compose up --build
