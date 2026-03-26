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
    'SearchParamContains',
    'SearchParamStartsWith',
    'SearchParamEndsWith',
]


class SearchParamContains(SearchParam):
    """
    Search parameter to filter for partial string matches, i.e. the specified string is contained in the column value.

    This is implemented using a `column LIKE "%{value}%"` expression. The value is escaped, so that '%' and '_' are
    interpreted as literal characters, not as wildcard characters.
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.contains(value, autoescape=True)


class SearchParamStartsWith(SearchParam):
    """
    Search parameter to filter for prefix string matches, i.e. the column value starts with the specified string.

    This is implemented using a `column LIKE "{value}%"` expression. The value is escaped, so that '%' and '_' are
    interpreted as literal characters, not as wildcard characters.
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.startswith(value, autoescape=True)


class SearchParamEndsWith(SearchParam):
    """
    Search parameter to filter for suffix string matches, i.e. the column value ends with the specified string.

    This is implemented using a `column LIKE "%{value}"` expression. The value is escaped, so that '%' and '_' are
    interpreted as literal characters, not as wildcard characters.
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        return column.endswith(value, autoescape=True)
