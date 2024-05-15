"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy.orm import Query

from .paginated_result import PaginatedResult

__all__ = [
    'AbstractPaginationMixin',
]


class AbstractPaginationMixin(ABC):
    """
    Abstract base class for pagination mixins used in search query dataclasses.
    """

    # The pagination limit (i.e. maximum number of items per page), or None if pagination is disabled
    limit: Optional[int]

    @abstractmethod
    def apply_pagination_to_query(self, query: Query, model_cls: Any) -> Query:
        """
        Applies the pagination parameters to an SQLAlchemy query and returns the new query.

        The exact implementation depends on the type of pagination.

        The "model_cls" parameter should be the class of the database model that is queried. It is needed for example
        for cursor pagination to get the "id" column that the filter should be applied on.
        """
        raise NotImplementedError

    @abstractmethod
    def get_start_parameter_name(self) -> str:
        """
        Returns the name of the pagination start parameter (e.g. "start" for cursor pagination or "offset" for offset
        pagination).
        """
        raise NotImplementedError

    @abstractmethod
    def get_next_start_value(self, paginated_result: PaginatedResult) -> Optional[int]:
        """
        Returns the next value for the pagination start parameter (see also: `get_start_parameter_name()`) to retrieve
        the next page of data, or None if there is no next page.
        """
        raise NotImplementedError
