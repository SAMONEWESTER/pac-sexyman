UV_SKIP_WHEEL_FILENAME_CHECK := 1
export UV_SKIP_WHEEL_FILENAME_CHECK

CONFIG ?= config.json


install:
	uv sync --all-groups

run:
	uv run python run.py $(CONFIG)

build: install
	uv run pyinstaller \
		--clean \
		--noconfirm \
		--name pac-man \
		--onefile \
		--paths "$PWD" \
		--hidden-import=src \
		--hidden-import=src.__main__ \
		--collect-submodules src \
		--add-data "assets:assets" \
		run.py

play:
	./dist/pac-man $(CONFIG)

debug:
	uv run python -m pdb pac-man.py $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache build dist

fclean: clean
	rm -rf .venv

lint-flake8:
	uv run flake8 --exclude=.venv

lint-mypy:
	uv run mypy . \
		--strict \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env)/'

lint: install lint-flake8 lint-mypy

.PHONY: install build play run debug clean fclean lint-flake8 lint-mypy lint
