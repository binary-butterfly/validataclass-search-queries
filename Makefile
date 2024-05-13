# Settings
DOCKER_MULTI_PYTHON_IMAGE = acidrain/multi-python:latest
DOCKER_USER = "$(shell id -u):$(shell id -g)"

# Default target
.DEFAULT_GOAL := tox


# Development environment
# -----------------------

# Install a virtualenv
.PHONY: venv
venv:
	virtualenv venv
	. venv/bin/activate && pip install --upgrade pip tox build && pip install -e ".[testing]"

# Build distribution package
.PHONY: build
build:
	. venv/bin/activate && python -m build


# Test suite
# ----------

# Run complete tox suite with local Python interpreter
.PHONY: tox
tox:
	tox run

# Run tox in venv (needs to be installed with `make venv` first)
.PHONY: venv-tox
venv-tox:
	. venv/bin/activate && tox run

# Only run pytest
.PHONY: test
test:
	tox run -e clean,py,report

# Only run flake8 linter
.PHONY: flake8
flake8:
	tox run -e flake8

# Open HTML coverage report in browser
.PHONY: open-coverage
open-coverage:
	$(or $(BROWSER),firefox) ./reports/coverage_html/index.html

# Run complete tox test suite in a multi-python Docker container
.PHONY: docker-tox
docker-tox:
	docker run --rm --tty \
		--user $(DOCKER_USER) \
		--mount "type=bind,src=$(shell pwd),target=/code" \
		--workdir /code \
		--env HOME=/tmp/home \
		$(DOCKER_MULTI_PYTHON_IMAGE) \
		tox run --workdir .tox_docker $(TOX_ARGS)

# Run partial tox test suites in Docker
.PHONY: docker-test-py312-sqlalchemy1.4 docker-test-py312-sqlalchemy2.0 \
		docker-test-py311-sqlalchemy1.4 docker-test-py311-sqlalchemy2.0 \
		docker-test-py310-sqlalchemy1.4 docker-test-py310-sqlalchemy2.0 \
		docker-test-py39-sqlalchemy1.4 docker-test-py39-sqlalchemy2.0 \
		docker-test-py38-sqlalchemy1.4 docker-test-py38-sqlalchemy2.0
docker-test-py312-sqlalchemy1.4: TOX_ARGS="-e clean,py312,py312-report,sqlalchemy1.4"
docker-test-py312-sqlalchemy1.4: docker-tox
docker-test-py312-sqlalchemy2.0: TOX_ARGS="-e clean,py312,py312-report,sqlalchemy2.0"
docker-test-py312-sqlalchemy2.0: docker-tox
docker-test-py311-sqlalchemy1.4: TOX_ARGS="-e clean,py311,py311-report,sqlalchemy1.4"
docker-test-py311-sqlalchemy1.4: docker-tox
docker-test-py311-sqlalchemy2.0: TOX_ARGS="-e clean,py311,py311-report,sqlalchemy2.0"
docker-test-py311-sqlalchemy2.0: docker-tox
docker-test-py310-sqlalchemy1.4: TOX_ARGS="-e clean,py310,py310-report,sqlalchemy1.4"
docker-test-py310-sqlalchemy1.4: docker-tox
docker-test-py310-sqlalchemy2.0: TOX_ARGS="-e clean,py310,py310-report,sqlalchemy2.0"
docker-test-py310-sqlalchemy2.0: docker-tox
docker-test-py39-sqlalchemy1.4: TOX_ARGS="-e clean,py39,py39-report,sqlalchemy1.4"
docker-test-py39-sqlalchemy1.4: docker-tox
docker-test-py39-sqlalchemy2.0: TOX_ARGS="-e clean,py39,py39-report,sqlalchemy2.0"
docker-test-py39-sqlalchemy2.0: docker-tox
docker-test-py38-sqlalchemy1.4: TOX_ARGS="-e clean,py38,py38-report,sqlalchemy1.4"
docker-test-py38-sqlalchemy1.4: docker-tox
docker-test-py38-sqlalchemy2.0: TOX_ARGS="-e clean,py38,py38-report,sqlalchemy2.0"
docker-test-py38-sqlalchemy2.0: docker-tox

# Run all tox test suites, but separately to check code coverage individually
.PHONY: docker-test-all
docker-test-all:
	make docker-test-py38-sqlalchemy1.4
	make docker-test-py39-sqlalchemy1.4
	make docker-test-py310-sqlalchemy1.4
	make docker-test-py311-sqlalchemy1.4
	make docker-test-py312-sqlalchemy1.4
	make docker-test-py38-sqlalchemy2.0
	make docker-test-py39-sqlalchemy2.0
	make docker-test-py310-sqlalchemy2.0
	make docker-test-py311-sqlalchemy2.0
	make docker-test-py312-sqlalchemy2.0

# Pull the latest image of the multi-python Docker image
.PHONY: docker-pull
docker-pull:
	docker pull $(DOCKER_MULTI_PYTHON_IMAGE)


# Cleanup
# -------

.PHONY: clean
clean:
	rm -rf .coverage .pytest_cache reports src/*/_version.py .tox .tox_docker .eggs src/*.egg-info venv

.PHONY: clean-dist
clean-dist:
	rm -rf dist/

.PHONY: clean-all
clean-all: clean clean-dist
