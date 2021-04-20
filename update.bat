poetry config virtualenvs.in-project true
poetry update --dry-run --no-dev
poetry run python -m pip install --upgrade pip
poetry update --no-dev