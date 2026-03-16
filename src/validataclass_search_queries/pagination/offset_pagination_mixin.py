"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from sqlalchemy.orm import Query
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

from .abstract_pagination_mixin import AbstractPaginationMixin
from .paginated_result import PaginatedResult
from .pagination_limit_validator import PaginationLimitValidator
from .. import pagination

__all__ = [
    'OffsetPaginationMixin',
]


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

    The default value for "limit" is set to 20, the maximum value for "limit" is 100. For this parameter, a specialized
    validator `PaginationLimitValidator` (which is based on an `IntegerValidator`) is used. To override the default
    and/or maximum value for "limit", you can simply override the `Default` object and/or the validator in your
    dataclass. For example:

    ```
    @search_query_dataclass
    class ExampleSearchQuery(OffsetPaginationMixin, BaseSearchQuery):
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
    class ExampleSearchQuery(OffsetPaginationMixin, BaseSearchQuery):
        # Make pagination opt-out (user can set limit=0 to disable pagination)
        limit: int | None = PaginationLimitValidator(optional=True, max_value=100), Default(20)

        # Make pagination opt-in (no pagination by default, user can set e.g. limit=10 to enable pagination)
        limit: int | None = PaginationLimitValidator(optional=True, max_value=100), Default(None)

        # Make pagination opt-in, but don't restrict the value of limit (except for the default 32-bit integer limit)
        limit: int | None = PaginationLimitValidator(optional=True), Default(None)
    ```
    """

    # Offset: Number of entries to skip
    offset: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)

    # Limit: Number of entries per page
    limit: int | None = PaginationLimitValidator(max_value=100), Default(20)

    def __init_subclass__(cls, **kwargs):
        # Pagination mixins are not compatible with each other, only one can be used at the same time
        if issubclass(cls, pagination.CursorPaginationMixin):
            raise TypeError(f'Invalid base classes in {cls}: Combining multiple pagination mixins is not allowed')

        super().__init_subclass__(**kwargs)

    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        In the case of offset pagination, a `LIMIT ... OFFSET ...` clause is applied to the query.
        """
        # If limit is 0 or None, pagination is disabled
        if not self.limit:
            return query

        return query.offset(self.offset).limit(self.limit)

    def get_start_parameter_name(self) -> str:
        """
        Returns the name of the pagination start parameter ("offset" for offset pagination).
        """
        return 'offset'

    def get_next_start_value(self, paginated_result: PaginatedResult) -> int | None:
        """
        Returns the next value for the pagination start parameter to retrieve the next page of data, or None if there
        is no next page.

        In case of offset pagination, this is the next offset value (i.e. the current offset value + page limit).
        """
        # If pagination is disabled, there is no next offset
        if not self.limit:
            return None

        # As long as the next offset is smaller than the total result count, there should be a next page
        next_offset = self.offset + self.limit
        return next_offset if next_offset < paginated_result.total_count else None
