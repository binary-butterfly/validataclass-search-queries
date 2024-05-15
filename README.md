# validataclass Search Queries

**NOTE: This is an internal library used by our company, not intended to be used outside of our projects.**

Shared Python library for search queries based on [validataclass](https://github.com/binary-butterfly/validataclass).

Implements search filters, pagination and sorting using dataclasses and validators, and provides helpers to work with
database queries (currently only SQLAlchemy is supported).


## Installation

The library can be installed with `pip` like other libraries. However, since it's an internal library, it can only be
retrieved from our [internal package registry](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/packages).

### requirements.txt

To install the library using a regular `requirements.txt` file, add the following lines to it:

```
# binary butterfly shared libraries (https://git.sectio-aurea.org/public_libraries)
--extra-index-url https://git.sectio-aurea.org/api/v4/groups/262/-/packages/pypi/simple
validataclass-search-queries~=0.5.0
```

(**Note:** The `--extra-index-url` parameter will be used for the whole `requirements.txt` file. If you're using
multiple libraries from the same package registry, you only need to specify the parameter once.)


## Usage

See [docs](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/blob/main/docs/index.md) for
the documentation, including a quick tutorial on how to use this library.


## Development

### Virtual environment

To setup a virtualenv for development of the library, run `make venv`.

This will create a virtualenv in `venv` and install the package in edit mode inside the virtualenv, including testing
dependencies.


### Running unit tests

Unit tests can be run using `make tox` or by directly executing `tox`.

Take a look at the `Makefile` for more ways to run the unit tests (e.g. inside a Docker container to test for specific
Python versions).
