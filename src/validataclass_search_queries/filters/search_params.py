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
    'SearchParamEquals',
    'SearchParamContains',
    'SearchParamStartsWith',
    'SearchParamEndsWith',
    'SearchParamBoolean',
    'SearchParamIsNone',
    'SearchParamIsNotNone',
    'SearchParamTernary',
    'SearchParamGreaterThan',
    'SearchParamGreaterOrEqual',
    'SearchParamLessThan',
    'SearchParamLessOrEqual',
    'SearchParamSince',
    'SearchParamUntil',
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


class SearchParamEquals(SearchParam):
    """
    Search parameter to filter for exact value matches (`column == value`).

    Note: For strings, this might or might not be case sensitive, depending on your database collations.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column == value


class SearchParamContains(SearchParam):
    """
    Search parameter to filter for partial string matches, i.e. the specified string is contained in the column value.

    This is implemented using a `column LIKE "%{value}%"` expression. The value is escaped, so that '%' and '_' are
    interpreted as literal characters, not as wildcard characters.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        # Short-circuit if value is empty
        return column.contains(value, autoescape=True) if value else column


class SearchParamStartsWith(SearchParam):
    """
    Search parameter to filter for prefix string matches, i.e. the column value starts with the specified string.

    This is implemented using a `column LIKE "{value}%"` expression. The value is escaped, so that '%' and '_' are
    interpreted as literal characters, not as wildcard characters.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        # Short-circuit if value is empty
        return column.startswith(value, autoescape=True) if value else column


class SearchParamEndsWith(SearchParam):
    """
    Search parameter to filter for suffix string matches, i.e. the column value ends with the specified string.

    This is implemented using a `column LIKE "%{value}"` expression. The value is escaped, so that '%' and '_' are
    interpreted as literal characters, not as wildcard characters.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        # Short-circuit if value is empty
        return column.endswith(value, autoescape=True) if value else column


class SearchParamBoolean(SearchParam):
    """
    Boolean search parameter to filter a boolean column for true or false.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column.is_(bool(value))


class SearchParamIsNone(SearchParam):
    """
    Boolean search parameter to filter a column for values that are None or not None.

    If the search parameter is True, only results where the specified column is None will be included.
    If the search parameter is False, only results where the specified column is NOT None will be included.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column.is_(None) if value is True else column.is_not(None)


class SearchParamIsNotNone(SearchParam):
    """
    Boolean search parameter to filter a column for values that are None or not None. Inverted version of SearchParamIsNone.

    If the search parameter is True, only results where the specified column is NOT None will be included.
    If the search parameter is False, only results where the specified column is None will be included.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column.is_not(None) if value is True else column.is_(None)


class SearchParamTernary(SearchParam):
    """
    Boolean search parameter that behaves like a ternary operator. Requires two values, one for True, one for False.

    Example: `SearchParamTernary('yes', 'no')`

    If the search parameter is True, only include results where the specified column equals `value_true` (e.g. "yes").
    If the search parameter is False, only include results where the specified column equals `value_false` (e.g. "no").

    To specify an alternative column name for this search parameter, use the keyword argument `column_name`.
    """

    value_true: Any
    value_false: Any

    def __init__(self, true: Any, false: Any, *, column_name: Optional[str] = None):
        super().__init__(column_name)
        self.value_true = true
        self.value_false = false

    def sqlalchemy_filter(self, column: ColumnElement, value: Any) -> ColumnElement:
        return column == (self.value_true if value else self.value_false)


class SearchParamGreaterThan(SearchParam):
    """
    Search parameter to filter for values greater than the filter value (`column > value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column > value


class SearchParamGreaterOrEqual(SearchParam):
    """
    Search parameter to filter for values greater than or equal to the filter value (`column >= value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column >= value


class SearchParamLessThan(SearchParam):
    """
    Search parameter to filter for values less than the filter value (`column < value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column < value


class SearchParamLessOrEqual(SearchParam):
    """
    Search parameter to filter for values less than or equal to the filter value (`column <= value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column <= value


class SearchParamSince(SearchParamGreaterOrEqual):
    """
    Alias for SearchParamGreaterOrEqual. Search parameter to filter for values (e.g. datetimes) since the filter value.
    """
    pass


class SearchParamUntil(SearchParamLessOrEqual):
    """
    Alias for SearchParamLessOrEqual. Search parameter to filter for values (e.g. datetimes) until the filter value.
    """
    pass
