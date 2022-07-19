"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.sql import ColumnElement

__all__ = [
    'AbstractSortingMixin',
]


class AbstractSortingMixin(ABC):
    """
    Abstract base class for the sorting mixin used in search query dataclasses.
    """

    @abstractmethod  # pragma: nocover
    def get_order_column(self, model_cls: Any) -> ColumnElement:
        """
        Returns the column that the query should be ordered by (including the sorting direction).

        The "model_cls" parameter should be the class of the database model that is queried.
        """
        raise NotImplementedError
