"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy.sql import ColumnElement

__all__ = [
    'SearchParam',
]


class SearchParam(ABC):
    """
    Abstract base class for search parameters.

    A SearchParam object can be used to define a search parameter in a search query, i.e. in a validataclass based on
    BaseSearchQuery. It is then stored in the dataclass fields' metadata attributes (similar to how the validators are
    stored).

    The SearchParam itself does *not* contain the value of the filter, only the name of the column (optional) and the
    filter operation (implemented by the various subclasses, e.g. SearchParamEquals, SearchParamContains, ...).

    When an actual request with search parameters is handled, a BoundSearchFilter is created for every SearchParam that
    is set in the request, bound to the value specified by the user. These BoundSearchFilters then can be used to
    generate SQLAlchemy filter expressions based on the column name and filter operation (supplied by the SearchParam)
    and filter value (set from user data).

    If no column name is specified in the SearchParam, the parameter name itself is used.

    Example:

    ```
    @search_query_dataclass
    class MySearchQuery(BaseSearchQuery):
        # Search for a concrete name (parameter name equals column name, so it doesn't need to be specified)
        name: Optional[str] = SearchParamEquals(), StringValidator()

        # Filter objects by modification date (based on the 'modified' column)
        modified_since: Optional[datetime] = SearchParamSince('modified'), DateTimeValidator()
        modified_until: Optional[datetime] = SearchParamUntil('modified'), DateTimeValidator()
    ```
    """

    # Optional: Name of the column (if not specified, the parameter name will be used)
    column_name: Optional[str]

    def __init__(self, column_name: Optional[str] = None):
        self.column_name = column_name

    @staticmethod  # pragma: nocover
    @abstractmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        """
        This abstract method defines the SQLAlchemy filter expression. See existing implementations for examples.
        """
        raise NotImplementedError
