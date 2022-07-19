"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Any

from sqlalchemy.sql import ColumnElement

from .search_params import SearchParam

__all__ = [
    'BoundSearchFilter',
]


class BoundSearchFilter:
    """
    Represents a concrete search filter for a specfic column that is bound to a value (usually user input).

    It mostly consists of a `SearchParam` object and a concrete value.

    A SearchParam is created only once to define a search *parameter* based on a field name (i.e. database column) and
    a filter function (e.g. equals, contains, greater/less than), so it's independent of actual requests.

    When an actual request with search parameters is handled, a BoundSearchFilter is created for every SearchParam that
    is set in the request, bound to the value specified by the user. These BoundSearchFilters then can be used to
    generate SQLAlchemy filter expressions based on the column name, filter operation and filter value.

    Example:

    ```
    # Construction of a BoundSearchFilter (happens internally in BaseSearchQuery.get_search_filters)
    bound_filter = BoundSearchFilter('modified_since', SearchParamSince('modified'), datetime(...))

    # Get column of an SQLAlchemy model by name from BoundSearchFilter
    column = getattr(MyModel, bound_filter.column_name)

    # Apply filter on an SQLAlchemy query
    query = session.query(MyModel).filter(bound_filter.get_sqlalchemy_filter(column))
    ```

    Attributes:

        param_name: Original name of the search parameter (as in: name of GET parameter)
        search_param: SearchParam object describing the filter function
        value: Filter value (usually user input)
    """

    param_name: str
    search_param: SearchParam
    value: Any

    def __init__(
        self,
        param_name: str,
        search_param: SearchParam,
        value: Any,
    ):
        self.param_name = param_name
        self.search_param = search_param
        self.value = value

    @property
    def column_name(self) -> str:
        """
        Name of the column/attribute of the database model that the filter should be applied on by default.
        """
        return self.search_param.column_name or self.param_name

    def get_sqlalchemy_filter(self, column: ColumnElement) -> ColumnElement:
        """
        Returns an SQLAlchemy filter for the given column (can be any ColumnElement, i.e. any SQLAlchemy expression that
        can be used in a WHERE clause) based on the filter function defined by the SearchParam.
        """
        return self.search_param.sqlalchemy_filter(column, self.value)
