format:
	isort .
	black .

up:
	docker-compose up

up-build:
	docker-compose up --build
