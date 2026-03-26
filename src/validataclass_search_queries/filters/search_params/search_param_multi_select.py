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
    'SearchParamMultiSelect',
]


class SearchParamMultiSelect(SearchParam):
    """
    Search parameter that can be set to a list of one or more values to search for, i.e. the filtered column must be
    equal to one of the values given by the user.

    This is implemented using a `column IN (values...)` SQL expression.

    Note: To make use of this search parameter, you must use a validator that outputs a list of values. If the parameter
    is set to a single value, the filter will be equivalent to an "equals" filter. See the `MultiSelectValidator`.
    """

    @override
    def sqlalchemy_filter(self, column: ColumnElement[Any], value: Any) -> ColumnElement[bool]:
        value_list = value if isinstance(value, list) else [value]
        return column.in_(value_list)
