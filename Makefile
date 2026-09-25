install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl --force-reinstall 
# по заданию без --force-reinstall

lint:
	poetry run ruff check .
 
test:
	poetry run python -m pytest -v
