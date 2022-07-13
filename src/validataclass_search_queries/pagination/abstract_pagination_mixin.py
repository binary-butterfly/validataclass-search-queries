"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Query

__all__ = [
    'AbstractPaginationMixin',
]


class AbstractPaginationMixin(ABC):
    """
    Abstract base class for pagination mixins used in search query dataclasses.
    """

    @abstractmethod  # pragma: nocover
    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        The exact implementation depends on the type of pagination.

        The "model_cls" parameter should be the class of the database model that is queried. It is needed for example
        for cursor pagination to get the "id" column that the filter should be applied on.
        """
        raise NotImplementedError
