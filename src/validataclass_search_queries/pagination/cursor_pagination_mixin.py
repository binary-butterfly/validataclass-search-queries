"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Any

from sqlalchemy.orm import Query
from sqlalchemy.sql import ColumnElement
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

from .. import pagination, sorting

__all__ = [
    'CursorPaginationMixin',
]


@validataclass
class CursorPaginationMixin(pagination.AbstractPaginationMixin):
    """
    Mixin for cursor pagination in search query dataclasses.

    Cursor pagination is a stable type of pagination that uses the ID (primary key) of database objects as a "cursor"
    which is used to filter the queries. To get the next page of results, you take the last ID on the current page,
    increment it by one, and use this value as your next cursor, filtering your query for all IDs greater or equal to
    that value.

    Cursor pagination only works when your query is ordered by ID. This is done automatically, but it means that you
    cannot combine cursor pagination with user-defined ordering.

    By default, the model class must have a column named "id" which is used as the cursor column. To change this,
    override the `get_pagination_cursor_column` method in your class to return a different cursor column (see default
    implementation below for how to do that).

    The mixin adds the parameters "start" and "limit" to the search query dataclass and implements cursor pagination
    for SQLAlchemy queries based on those parameters (using "start" as the cursor value).

    To use the mixin in your search query dataclass, simply include it in the list of base classes. Parameters will be
    added automatically, so nothing else needs to be done to make it work:

    ```
    @search_query_dataclass
    class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
        pass
    ```

    The default value for "limit" is set to 20, the maximum value for "limit" is 100. To set a different default value,
    you can simply override the `Default` object in your dataclass. Similarly, to allow values higher than 100, you
    can override the IntegerValidator with a custom value (important: you need to set `allow_strings=True` for the
    integer validator, because GET query parameters are always strings).

    ```
    @search_query_dataclass
    class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
        # This only changes the default value:
        limit: int = Default(100)

        # This sets a different maximum value and default:
        limit: int = IntegerValidator(min_value=1, max_value=1000, allow_strings=True), Default(100)
    ```
    """

    # Start ID: Query is filtered by "Model.id >= start"
    start: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)

    # Limit: Number of entries per page
    limit: int = IntegerValidator(min_value=1, max_value=100, allow_strings=True), Default(20)

    def __init_subclass__(cls, **kwargs):
        # Pagination mixins are not compatible with each other, only one can be used at the same time
        if issubclass(cls, pagination.OffsetPaginationMixin):
            raise TypeError(f'Invalid base classes in {cls}: Combining multiple pagination mixins is not allowed')
        if issubclass(cls, sorting.SortingMixin):
            raise TypeError(f'Invalid base classes in {cls}: CursorPaginationMixin cannot be combined with SortingMixin')

        super().__init_subclass__(**kwargs)

    @staticmethod
    def get_pagination_cursor_column(model_cls: Any) -> ColumnElement:
        """
        Returns the column that is used as cursor for cursor pagination.

        By default, this returns the "id" column of a model. This method can be overridden in your class to use a
        different column.
        """
        return getattr(model_cls, 'id')

    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        In the case of cursor pagination, the query is first ordered by ID, then filtered by `Model.id >= start` and
        lastly a `LIMIT ...` clause is applied.
        """
        # The parameters should always be set, but in case they are not, set start to 0 (limit can be None)
        if self.start is None:
            self.start = 0

        # Get the cursor column from the model class
        key_column = self.get_pagination_cursor_column(model_cls)

        # Cursor pagination requires the data to be ordered by the cursor column
        return query.order_by(key_column) \
            .filter(key_column >= self.start) \
            .limit(self.limit)
