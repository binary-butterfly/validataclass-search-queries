# 4. Type checking with mypy

To allow proper type checking of validataclasses and search queries with mypy, you need to use the mypy plugin provided
by validataclass and configure it correctly to recognize search queries as a variant of validataclasses.

Please refer to the [validataclass docs](https://github.com/binary-butterfly/validataclass/blob/main/docs/07-mypy-plugin.md)
for more details.

## How to enable and configure the validataclass mypy plugin

The mypy plugin is included in validataclass, but you need to enable it explicitly in your mypy configuration. You also
need to configure the plugin itself so that it recognizes the `@search_query_dataclass` decorator as a validataclass
decorator. The plugin also needs to know to ignore the `SearchParam` objects in a validataclass.

If you're using a `pyproject.toml` file (which is the recommended way nowadays to configure Python projects and tools),
this is an example configuration for mypy and the validataclass mypy plugin:

```toml
[tool.mypy]
# These lines are just an example and might not be needed or need to be adjusted in your project:
files = ["src/"]
mypy_path = "src/"
explicit_package_bases = true

# This is the important part to enable the plugin:
plugins = ["validataclass.mypy.plugin"]

# This is the configuration for the plugin itself:
[tool.validataclass_mypy]
# Declare @search_query_dataclass as a decorator that creates validataclasses
custom_validataclass_decorators = [
    "validataclass_search_queries.search_queries.search_query_dataclass.search_query_dataclass",
]

# Ignore SearchParam objects in validataclass field definitions
ignore_custom_types_in_fields = [
    "validataclass_search_queries.filters.search_params.base_search_param.SearchParam",
]
```
