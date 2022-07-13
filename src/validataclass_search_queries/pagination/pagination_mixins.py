"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Query
from sqlalchemy.sql import ColumnElement
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

from ..sorting import SortingMixin

__all__ = [
    'AbstractPaginationMixin',
    'CursorPaginationMixin',
    'OffsetPaginationMixin',
]


class AbstractPaginationMixin(ABC):
    """
    Abstract base class for pagination mixins used in search query dataclasses.
    """

    @abstractmethod
    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        The exact implementation depends on the type of pagination.

        The "model_cls" parameter should be the class of the database model that is queried. It is needed for example
        for cursor pagination to get the "id" column that the filter should be applied on.
        """
        raise NotImplementedError


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
        if issubclass(cls, OffsetPaginationMixin):
            raise TypeError(f'Invalid base classes in {cls}: Combining multiple pagination mixins is not allowed')
        if issubclass(cls, SortingMixin):
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


@validataclass
class OffsetPaginationMixin(AbstractPaginationMixin):
    """
    Mixin for offset pagination in search query dataclasses.

    Offset pagination works by applying a `LIMIT ... OFFSET ...` clause to the SQL query. To get the next page of
    results, you repeat the query with the offset increased by the specified limit (e.g. with limit=10, you would start
    with offset=0 and continue with offset=10, offset=20, etc.).

    Offset pagination is not stable, which means that results can "shift" between pages when the results are modified
    between queries. The upside is that offset pagination works with any query, so it can be combined with any filter
    and with custom ordering.

    The mixin adds the parameters "offset" and "limit" to the search query dataclass and implements offset pagination
    for SQLAlchemy queries based on those parameters.

    To use the mixin in your search query dataclass, simply include it in the list of base classes. Parameters will be
    added automatically, so nothing else needs to be done to make it work:

    ```
    @search_query_dataclass
    class ExampleSearchQuery(OffsetPaginationMixin, BaseSearchQuery):
        pass
    ```

    The default value for "limit" is set to 20, the maximum value for "limit" is 100. To set a different default value,
    you can simply override the `Default` object in your dataclass. Similarly, to allow values higher than 100, you
    can override the IntegerValidator with a custom value (important: you need to set `allow_strings=True` for the
    integer validator, because GET query parameters are always strings).

    ```
    @search_query_dataclass
    class ExampleSearchQuery(OffsetPaginationMixin, BaseSearchQuery):
        # This only changes the default value:
        limit: int = Default(100)

        # This sets a different maximum value and default:
        limit: int = IntegerValidator(min_value=1, max_value=1000, allow_strings=True), Default(100)
    ```
    """

    # Offset: Number of entries to skip
    offset: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)

    # Limit: Number of entries per page
    limit: int = IntegerValidator(min_value=1, max_value=100, allow_strings=True), Default(20)

    def __init_subclass__(cls, **kwargs):
        # Pagination mixins are not compatible with each other, only one can be used at the same time
        if issubclass(cls, CursorPaginationMixin):
            raise TypeError(f'Invalid base classes in {cls}: Combining multiple pagination mixins is not allowed')

        super().__init_subclass__(**kwargs)

    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        In the case of offset pagination, a `LIMIT ... OFFSET ...` clause is applied to the query.
        """
        return query.offset(self.offset).limit(self.limit)
