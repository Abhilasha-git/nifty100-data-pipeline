load:
	python -m src.etl.loader

test:
	pytest

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache

report:
	python scripts/report.py