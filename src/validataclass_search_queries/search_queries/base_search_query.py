"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import dataclasses
from enum import Enum
from typing import Any, Dict, Iterator, Tuple

from validataclass.helpers import UnsetValue

from ..filters import BoundSearchFilter

__all__ = [
    'BaseSearchQuery',
]


class BaseSearchQuery:
    """
    Base class for search query validataclasses, which can be used to validate search parameters (e.g. GET query
    parameters to search the database by specific criteria).

    Use as a base class together with the `@search_query_database` decorator.

    The SearchParam subclasses (e.g. SearchParamEquals) can be used to define the actual search parameters.

    Please note: All fields with search parameters automatically have `Default(None)` unless specified otherwise.

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

    def get_search_filters(self) -> Iterator[Tuple[str, BoundSearchFilter]]:
        """
        Returns an iterator that instantiates BoundSearchFilters for all search parameters in this class that are set
        by the user (i.e. not None).

        The iterator yields tuples consisting of exactly two elements: the parameter name (i.e. the field name in the
        dataclass) and the BoundSearchFilter.

        To generate a dictionary from this, simply use `dict(search_query.get_search_filters())`.
        """
        dataclass_fields = dataclasses.fields(self)  # noqa (will raise TypeError if not a dataclass)

        # Iterate over all dataclass fields that have a search parameter defined and have a value other than None
        for field in dataclass_fields:
            search_param = field.metadata.get('search_param', None)
            value = getattr(self, field.name)

            if search_param and value is not None and value is not UnsetValue:
                # Generate tuples of parameter name and BoundSearchFilters
                yield field.name, BoundSearchFilter(field.name, search_param, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns the data of all fields that are set in the dataclass as a dictionary, i.e. all fields with values other
        than None or UnsetValue.

        Does NOT recurse into the data, since search queries should be more or less flat. (This might change in the
        future to allow for multi-select parameters.)
        """
        dataclass_fields = dataclasses.fields(self)  # noqa (will raise TypeError if not a dataclass)
        data = {}

        for field in dataclass_fields:
            value = getattr(self, field.name)
            if value is not None and value is not UnsetValue:
                # Convert enums to their values
                if isinstance(value, Enum):
                    value = value.value

                data[field.name] = value

        return data
