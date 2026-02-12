format:
	isort .
	black .

run:
	PYTHONPATH=. poetry run python src/main.py
