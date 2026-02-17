format:
	isort .
	black .

run:
	PYTHONPATH=. poetry run python src/main.py

up-build:
	docker-compose up --build
