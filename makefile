mypy:
	poetry run mypy --config-file pyproject.toml .
test:
	poetry run pytest
