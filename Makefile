PYTHON ?= python3

.PHONY: install tools lint test examples gate

install:
	$(PYTHON) -m pip install -e ".[dev]"

tools:
	bash scripts/install_tools.sh

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest

examples:
	$(PYTHON) scripts/generate_examples.py

gate:
	$(PYTHON) scripts/qa/check_examples.py
