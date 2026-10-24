UV_SKIP_WHEEL_FILENAME_CHECK := 1
export UV_SKIP_WHEEL_FILENAME_CHECK

CONFIG ?= config.json


install:
	uv sync --all-groups

build: install
	uv run pyinstaller \
		--clean \
		--noconfirm \
		--name pac-man \
		--onedir \
		--paths "$PWD" \
		--hidden-import=src \
		--hidden-import=src.__main__ \
		--collect-submodules src \
		--add-data "assets:assets" \
		run.py

play:
	./dist/pac-man/pac-man $(CONFIG)

run:
	uv run python pac-man.py $(CONFIG)

debug:
	uv run python -m pdb pac-man.py $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache build dist

fclean: clean
	rm -rf .venv

lint: install
	uv run flake8 --exclude=.venv
	uv run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env)/'

lint-strict: install
	uv run flake8 --exclude=.venv
	uv run mypy . \
		--strict \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env)/'

.PHONY: install build run debug clean lint lint-strict
