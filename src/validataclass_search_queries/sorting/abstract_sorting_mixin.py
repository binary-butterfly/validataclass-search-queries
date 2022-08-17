"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any

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
    def get_order_column(self, model_cls: Any) -> ColumnElement:
        """
        Returns the column that the query should be ordered by (including the sorting direction).

        The "model_cls" parameter should be the class of the database model that is queried.
        """
        raise NotImplementedError
