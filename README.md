# validataclass Search Queries

[![Unit tests](https://github.com/binary-butterfly/validataclass-search-queries/actions/workflows/tests.yml/badge.svg)
](https://github.com/binary-butterfly/validataclass-search-queries/actions/workflows/tests.yml)

Shared Python library for search queries based on [validataclass](https://github.com/binary-butterfly/validataclass).

Implements search filters, pagination and sorting using dataclasses and validators, and provides helpers to work with
database queries (currently only SQLAlchemy 1.4 and 2.0 are supported).

**Status:** Beta.


## Installation

validataclass-search-queries is available on [PyPI](https://pypi.org/project/validataclass-search-queries/).

To install it using [pip](https://pip.pypa.io/en/stable/getting-started/), just run:

```shell
pip install validataclass-search-queries
```

If you add the package to your dependencies, it is recommended to use
[compatible release](https://www.python.org/dev/peps/pep-0440/#compatible-release) version specifiers to make sure you
always get the latest version of the library but without running into breaking changes:

```shell
pip install validataclass-search-queries~=0.5.0
```

However, keep in mind that the library is still in its beta phase (as indicated by the major version of 0). There can
and will be smaller breaking changes between 0.x minor versions, but we will try to keep them at a minimum and save the
big breaking changes for the release of version 1.0.0.


## Usage

See [docs](https://github.com/binary-butterfly/validataclass-search-queries/blob/main/docs/index.md) for
the documentation, including a quick tutorial on how to use this library.


## Development

### Virtual environment

To setup a virtualenv for development of the library, run `make venv`.

This will create a virtualenv in `venv` and install the package in edit mode inside the virtualenv, including testing
dependencies.


### Running unit tests

Unit tests can be run using `make tox` or by directly executing `tox`.

For this to work you need to either be inside the virtualenv (see above) or have [tox](https://tox.wiki/en/latest/)
installed in your system locally.

Take a look at the `Makefile` for more ways to run the unit tests (e.g. inside a Docker container to test for specific
Python versions).
