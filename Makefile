PYTHON ?= python3

.PHONY: install tools lint test

install:
	$(PYTHON) -m pip install -e ".[dev]"

tools:
	bash scripts/install_tools.sh

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest
