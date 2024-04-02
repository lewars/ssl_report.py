# Makefile for the Jenkins Credentials Manager (jcm) Tool
# This tools is a Python script that can be used to manage

SHELL := /bin/bash
TOOL_NAME := jcm
TOOL_VERSION := 1.0.0
VENV_NAME := venv
PYTHON_VERSION := 3.9
PYTHON_CMD := python$(PYTHON_VERSION)

TEST_CMD ?= make test # example value: 'python -m pytest -v tests/test_AWSCredentials.py'"

.PHONY: all venv install install-dev lint test test-watch clean

all: clean install

venv: clean
	@echo "Creating virtual environment..."
	$(PYTHON_CMD) -m venv $(VENV_NAME)

install: venv
	@echo "Installing dependencies..."
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON_CMD) -m pip install  --upgrade pip && \
	$(PYTHON_CMD) -m pip install --upgrade setuptools && \
	$(PYTHON_CMD) -m pip install --upgrade wheel && \
	$(PYTHON_CMD) -m pip install -r requirements.txt

install-dev: venv
	@echo "Setting up dev environment..."
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON_CMD) -m pip install  --upgrade pip && \
	$(PYTHON_CMD) -m pip install --upgrade setuptools && \
	$(PYTHON_CMD) -m pip install --upgrade wheel && \
	$(PYTHON_CMD) -m pip install -r requirements.txt
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON_CMD) -m pip install -e .

lint:
	@echo "Linting..."
	. $(VENV_NAME)/bin/activate && \
	pre-commit run --all-files

test: lint
	@echo "Testing..."
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON_CMD) -m pytest -v tests/

test-watch:
	@command -v inotifywait >/dev/null 2>&1 || { echo "inotifywait not found. inotifywait is required."; exit 1; }
	@echo "Start continuous testing. Watching with command $(TEST_CMD)..."
	@while inotifywait  -e close_write tests; do \
		. $(VENV_NAME)/bin/activate && $(TEST_CMD); \
	done

clean:
	@echo "Cleaning up..."
	@rm -vrf $(VENV_NAME)
	@rm -vrf build
	@rm -vrf dist
	@rm -vrf *.egg-info
