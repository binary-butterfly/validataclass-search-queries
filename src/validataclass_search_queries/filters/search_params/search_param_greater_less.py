"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any
from typing_extensions import override

from sqlalchemy.sql import ColumnElement

from .base_search_param import SearchParam

__all__ = [
    'SearchParamGreaterThan',
    'SearchParamGreaterOrEqual',
    'SearchParamLessThan',
    'SearchParamLessOrEqual',
    'SearchParamSince',
    'SearchParamUntil',
]


class SearchParamGreaterThan(SearchParam):
    """
    Search parameter to filter for values greater than the filter value (`column > value`).
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.__gt__(value)


class SearchParamGreaterOrEqual(SearchParam):
    """
    Search parameter to filter for values greater than or equal to the filter value (`column >= value`).
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.__ge__(value)


class SearchParamLessThan(SearchParam):
    """
    Search parameter to filter for values less than the filter value (`column < value`).
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.__lt__(value)


class SearchParamLessOrEqual(SearchParam):
    """
    Search parameter to filter for values less than or equal to the filter value (`column <= value`).
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.__le__(value)


class SearchParamSince(SearchParamGreaterOrEqual):
    """
    Alias for SearchParamGreaterOrEqual. Search parameter to filter for values (e.g. datetimes) since the filter value.
    """
    pass


class SearchParamUntil(SearchParamLessOrEqual):
    """
    Alias for SearchParamLessOrEqual. Search parameter to filter for values (e.g. datetimes) until the filter value.
    """
    pass
