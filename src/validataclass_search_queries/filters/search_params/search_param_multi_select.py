"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Any

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

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        value_list = value if isinstance(value, list) else [value]
        return column.in_(value_list)
