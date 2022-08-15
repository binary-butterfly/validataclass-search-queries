"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Any

from sqlalchemy.sql import ColumnElement


def assert_column_element(element: Any, expected_string: str, *expected_params) -> None:
    """ Helper function to check the SQL and bound parameters of a generated ColumnElement. """
    assert isinstance(element, ColumnElement)
    compiled_expr = element.compile()
    assert str(compiled_expr) == expected_string
    assert list(compiled_expr.params.values()) == list(expected_params)
