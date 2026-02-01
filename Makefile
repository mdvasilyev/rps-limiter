format:
	isort .
	black .

run-app:
	PYTHONPATH=. poetry run python src/main.py
