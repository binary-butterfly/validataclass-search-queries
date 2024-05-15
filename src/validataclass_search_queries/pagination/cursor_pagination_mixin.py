"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional

from sqlalchemy.orm import Query
from sqlalchemy.sql import ColumnElement
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

from .abstract_pagination_mixin import AbstractPaginationMixin
from .paginated_result import PaginatedResult
from .pagination_limit_validator import PaginationLimitValidator
from .. import pagination, sorting

__all__ = [
    'CursorPaginationMixin',
]


@validataclass
class CursorPaginationMixin(AbstractPaginationMixin):
    """
    Mixin for cursor pagination in search query dataclasses.

    Cursor pagination is a stable type of pagination that uses the ID (primary key) of database objects as a "cursor"
    which is used to filter the queries. To get the next page of results, you take the last ID on the current page,
    increment it by one, and use this value as your next cursor, filtering your query for all IDs greater or equal to
    that value.

    Cursor pagination only works when your query is ordered by ID. This is done automatically, but it means that you
    cannot combine cursor pagination with user-defined ordering.

    By default, the model class must have a column named "id" which is used as the cursor column. To change this, you
    can override the `get_cursor_column_name()` method in your class to return a different column name. There is also
    `get_cursor_column()` which can be overridden in more complex scenarios.

    The mixin adds the parameters "start" and "limit" to the search query dataclass and implements cursor pagination
    for SQLAlchemy queries based on those parameters (using "start" as the cursor value).

    To use the mixin in your search query dataclass, simply include it in the list of base classes. Parameters will be
    added automatically, so nothing else needs to be done to make it work:

    ```
    @search_query_dataclass
    class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
        pass
    ```

    The default value for "limit" is set to 20, the maximum value for "limit" is 100. For this parameter, a specialized
    validator `PaginationLimitValidator` (which is based on an `IntegerValidator`) is used. To override the default
    and/or maximum value for "limit", you can simply override the `Default` object and/or the validator in your
    dataclass. For example:

    ```
    @search_query_dataclass
    class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
        # This only changes the default value:
        limit: int = Default(100)

        # This sets a different maximum value and default:
        limit: int = PaginationLimitValidator(max_value=1000), Default(100)
    ```

    By default, when you include this mixin in your dataclass, pagination is always required. This means that the user
    will always get paginated results. To make pagination optional, you can set the parameter `optional=True` in the
    `PaginationLimitValidator`. With this option, the validator will allow 0 and None as input, returning None in both
    cases. This means that the user can set `limit=0` in the GET query to disable pagination (i.e. they will get all
    results at once). You can also set `Default(None)` as the default to make pagination opt-in (meaning the user has
    to set "limit" to some number to enable pagination).

    ```
    @search_query_dataclass
    class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
        # Make pagination opt-out (user can set limit=0 to disable pagination)
        limit: Optional[int] = PaginationLimitValidator(optional=True, max_value=100), Default(20)

        # Make pagination opt-in (no pagination by default, user can set e.g. limit=10 to enable pagination)
        limit: Optional[int] = PaginationLimitValidator(optional=True, max_value=100), Default(None)

        # Make pagination opt-in, but don't restrict the value of limit (except for the default 32-bit integer limit)
        limit: Optional[int] = PaginationLimitValidator(optional=True), Default(None)
    ```
    """

    # Start ID: Query is filtered by "Model.id >= start"
    start: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)

    # Limit: Number of entries per page
    limit: Optional[int] = PaginationLimitValidator(max_value=100), Default(20)

    def __init_subclass__(cls, **kwargs):
        # Pagination mixins are not compatible with each other, only one can be used at the same time
        if issubclass(cls, pagination.OffsetPaginationMixin):
            raise TypeError(f'Invalid base classes in {cls}: Combining multiple pagination mixins is not allowed')
        if issubclass(cls, sorting.SortingMixin):
            raise TypeError(f'Invalid base classes in {cls}: CursorPaginationMixin cannot be combined with SortingMixin')

        super().__init_subclass__(**kwargs)

    @staticmethod
    def get_cursor_column_name() -> str:
        """
        Returns the name of the column that is used as cursor for cursor pagination. Defaults to "id".

        You can override this method in your class to use a different column. For more complex customization, see also
        `get_cursor_column()` which returns the column (instead of just the name of the column).
        """
        return 'id'

    def get_cursor_column(self, model_cls: Any) -> ColumnElement:
        """
        Returns the column that is used as cursor for cursor pagination.

        By default, this returns the column of a model with the name defined by `get_cursor_column_name()`.

        In most cases, overriding `get_cursor_column_name()` should be enough to use a different column. If you override
        THIS method, be sure to also adjust `get_cursor_column_name()` so that it still works with other methods like
        `get_next_start_value()`.
        """
        return getattr(model_cls, self.get_cursor_column_name())

    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        In the case of cursor pagination, the query is first ordered by ID, then filtered by `Model.id >= start` and
        lastly a `LIMIT ...` clause is applied.
        """
        # If limit is 0 or None, pagination is disabled
        if not self.limit:
            return query

        # The start parameter should always be set, but in case it is not, default to 0
        if self.start is None:
            self.start = 0

        # Get the cursor column from the model class
        key_column = self.get_cursor_column(model_cls)

        # Cursor pagination requires the data to be ordered by the cursor column
        return query.order_by(key_column) \
            .filter(key_column >= self.start) \
            .limit(self.limit)

    def get_start_parameter_name(self) -> str:
        """
        Returns the name of the pagination start parameter ("start" for cursor pagination).
        """
        return 'start'

    def get_next_start_value(self, paginated_result: PaginatedResult) -> Optional[int]:
        """
        Returns the next value for the pagination start parameter to retrieve the next page of data, or None if there
        is no next page.

        In case of cursor pagination, this is the next start ID (i.e. the last ID of the current page + 1).
        """
        # If pagination is disabled, there is no next start ID
        if not self.limit:
            return None

        # If the page is not "filled" (less results than page limit), there probably is no next page.
        if len(paginated_result) < self.limit:
            return None

        # Get last result in list
        last_item = paginated_result[-1]

        # Get cursor value (e.g. ID) of last result, allowing both objects and dictionaries, and increment by one
        cursor_key = self.get_cursor_column_name()
        if isinstance(last_item, dict):
            return last_item.get(cursor_key) + 1
        elif hasattr(last_item, cursor_key):
            return getattr(last_item, cursor_key) + 1
        else:
            raise Exception(f'Last item of PaginatedResult has neither attribute nor dictionary key "{cursor_key}": {last_item}')
