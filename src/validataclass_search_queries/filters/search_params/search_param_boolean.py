"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional

from sqlalchemy.sql import ColumnElement

from .base_search_param import SearchParam

__all__ = [
    'SearchParamBoolean',
    'SearchParamIsNone',
    'SearchParamIsNotNone',
    'SearchParamTernary',
]


class SearchParamBoolean(SearchParam):
    """
    Boolean search parameter to filter a boolean column for true or false.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column.is_(bool(value))


class SearchParamIsNone(SearchParam):
    """
    Boolean search parameter to filter a column for values that are None or not None.

    If the search parameter is True, only results where the specified column is None will be included.
    If the search parameter is False, only results where the specified column is NOT None will be included.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column.is_(None) if value is True else column.is_not(None)


class SearchParamIsNotNone(SearchParam):
    """
    Boolean search parameter to filter a column for values that are None or not None. Inverted version of SearchParamIsNone.

    If the search parameter is True, only results where the specified column is NOT None will be included.
    If the search parameter is False, only results where the specified column is None will be included.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column.is_not(None) if value is True else column.is_(None)


class SearchParamTernary(SearchParam):
    """
    Boolean search parameter that behaves like a ternary operator. Requires two values, one for True, one for False.

    Example: `SearchParamTernary('yes', 'no')`

    If the search parameter is True, only include results where the specified column equals `value_true` (e.g. "yes").
    If the search parameter is False, only include results where the specified column equals `value_false` (e.g. "no").

    To specify an alternative column name for this search parameter, use the keyword argument `column_name`.
    """

    value_true: Any
    value_false: Any

    def __init__(self, true: Any, false: Any, *, column_name: Optional[str] = None):
        super().__init__(column_name)
        self.value_true = true
        self.value_false = false

    def sqlalchemy_filter(self, column: ColumnElement, value: Any) -> ColumnElement:
        return column == (self.value_true if value else self.value_false)
