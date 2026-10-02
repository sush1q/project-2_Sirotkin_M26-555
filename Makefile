install:
	uv sync

project:
	uv run database

build:
	uv build

publish:
	uv publish --dry-run --trusted-publishing never

package-install:
	uv pip install --python .venv/bin/python --reinstall dist/*.whl

lint:
	uv run ruff check .

test:
	uv run python -m pytest -v
