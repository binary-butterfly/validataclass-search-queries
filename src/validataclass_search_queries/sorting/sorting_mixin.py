"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.sql import ColumnElement
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import AnyOfValidator

from .sorting_direction import SortingDirection, SortingDirectionValidator

__all__ = [
    'AbstractSortingMixin',
    'SortingMixin',
]


class AbstractSortingMixin(ABC):
    """
    Abstract base class for the sorting mixin used in search query dataclasses.
    """

    @abstractmethod
    def get_order_column(self, model_cls: Any) -> ColumnElement:
        """
        Returns the column that the query should be ordered by (including the sorting direction).

        The "model_cls" parameter should be the class of the database model that is queried.
        """
        raise NotImplementedError


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

    def get_order_column(self, model_cls: Any) -> ColumnElement:
        """
        Returns the column that the query should be ordered by (including the sorting direction).

        The "model_cls" parameter should be the class of the database model that is queried.
        """
        sort_column: ColumnElement = getattr(model_cls, self.sorted_by)
        return sort_column.desc() if self.sorting_direction is SortingDirection.DESC else sort_column.asc()
