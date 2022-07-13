"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Any

from sqlalchemy.orm import Query
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

from .. import pagination

__all__ = [
    'OffsetPaginationMixin',
]


@validataclass
class OffsetPaginationMixin(pagination.AbstractPaginationMixin):
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
        if issubclass(cls, pagination.CursorPaginationMixin):
            raise TypeError(f'Invalid base classes in {cls}: Combining multiple pagination mixins is not allowed')

        super().__init_subclass__(**kwargs)

    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        In the case of offset pagination, a `LIMIT ... OFFSET ...` clause is applied to the query.
        """
        return query.offset(self.offset).limit(self.limit)
