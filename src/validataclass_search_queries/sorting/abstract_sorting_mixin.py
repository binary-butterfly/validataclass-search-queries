"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Query
from sqlalchemy.sql import ColumnElement

from .sorting_direction import SortingDirection

__all__ = [
    'AbstractSortingMixin',
]


class AbstractSortingMixin(ABC):
    """
    Abstract base class for the sorting mixin used in search query dataclasses.
    """

    @property
    @abstractmethod
    def sorted_by(self) -> str:
        """
        Name of the column that the results should be ordered by.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def sorting_direction(self) -> SortingDirection:
        """
        Sorting direction (ascending or descending, using the `SortingDirection` enum).
        """
        raise NotImplementedError

    @abstractmethod  # pragma: nocover
    def get_sorting_column(self, model_cls: Any) -> ColumnElement:
        """
        Returns the column that the query should be ordered by (excluding the sorting direction).

        The "model_cls" parameter should be the class of the database model that is queried.
        """
        raise NotImplementedError

    @abstractmethod  # pragma: nocover
    def apply_sorting_direction(self, column: ColumnElement) -> ColumnElement:
        """
        Applies the sorting direction to an SQLAlchemy column element, i.e. `column.asc()` or `column.desc()`, and
        returns the new column element.
        """
        raise NotImplementedError

    @abstractmethod  # pragma: nocover
    def apply_sorting_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the sorting parameters to an SQLAlchemy query (`query.order_by()`) and returns the new query.

        The "model_cls" parameter should be the class of the database model that is queried. It is needed to get the
        sorting column from the model.
        """
        raise NotImplementedError
