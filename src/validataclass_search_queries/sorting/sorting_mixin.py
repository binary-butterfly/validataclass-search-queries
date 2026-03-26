"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, TypeVar, cast

from sqlalchemy.orm import Query
from sqlalchemy.sql import ColumnElement
from typing_extensions import override
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import AnyOfValidator

from .abstract_sorting_mixin import AbstractSortingMixin
from .sorting_direction import SortingDirection, SortingDirectionValidator

__all__ = [
    'SortingMixin',
]

T = TypeVar('T')


@validataclass
class SortingMixin(AbstractSortingMixin):
    """
    Mixin for sorting parameters in search query dataclasses.

    This mixin adds the validated parameters "sorted_by" and "sorting_direction" to the search query dataclass.

    Please note that the SortingMixin cannot be used in combination with cursor pagination, because cursor pagination
    requires the query to always be ordered by ID.

    To use the mixin in your search query dataclass, simply include it in the list of base classes. Parameters will
    be added automatically. However, by default only "id" is allowed as the sorting key. To specify a list of columns
    that are allowed as sorting keys, override the validator of the "sorted_by" field with another `AnyOfValidator`.

    You can also override the default sorting key, and if you want even limit the allowed sorting directions and the
    default sorting direction.

    Examples:

    ```
    @search_query_dataclass
    class ExampleSearchQuery(SortingMixin, BaseSearchQuery):
        # Override the list of allowed sorting keys, but keep "id" as the default
        sorted_by: str = AnyOfValidator(['id', 'created', 'modified'])

        # Only allow one sorting key and set it as the default (effectively enforcing a specific sorting key)
        sorted_by: str = AnyOfValidator(['created']), Default('created')

        # Change the default sorting direction to descending instead of ascending
        sorting_direction: SortingDirection = Default(SortingDirection.DESC)
    ```
    """

    # Name of column that the results should be ordered by
    sorted_by: str = AnyOfValidator(['id']), Default('id')

    # Sorting direction ("ASC" or "DESC", case-insensitive)
    sorting_direction: SortingDirection = SortingDirectionValidator(), Default(SortingDirection.ASC)

    @override
    def get_sorting_column(self, model_cls: Any) -> ColumnElement[Any]:
        """
        Returns the column that the query should be ordered by (excluding the sorting direction).

        The "model_cls" parameter should be the class of the database model that is queried.
        """
        # SQLAlchemy's typing is complicated and we don't know what exact types we have to expect here, so we'll just
        # pretend it's always a ColumnElement to make the type checker happy.
        return cast(ColumnElement[Any], getattr(model_cls, self.sorted_by))

    @override
    def apply_sorting_direction(self, column: ColumnElement[T]) -> ColumnElement[T]:
        """
        Applies the sorting direction to an SQLAlchemy column element, i.e. `column.asc()` or `column.desc()`, and
        returns the new column element.
        """
        return column.desc() if self.sorting_direction is SortingDirection.DESC else column.asc()

    @override
    def apply_sorting_to_query(self, query: Query[T], model_cls: Any) -> Query[T]:
        """
        Applies the sorting parameters to an SQLAlchemy query (`query.order_by()`) and returns the new query.

        The "model_cls" parameter should be the class of the database model that is queried. It is needed to get the
        sorting column from the model.
        """
        # If someone wants to disable sorting for some reason
        if self.sorted_by is None:  # type: ignore[comparison-overlap]
            return query  # type: ignore[unreachable]

        sorting_column = self.get_sorting_column(model_cls)
        return query.order_by(self.apply_sorting_direction(sorting_column))
