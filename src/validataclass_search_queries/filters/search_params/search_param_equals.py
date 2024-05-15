"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from sqlalchemy.sql import ColumnElement

from .base_search_param import SearchParam

__all__ = [
    'SearchParamEquals',
]


class SearchParamEquals(SearchParam):
    """
    Search parameter to filter for exact value matches (`column == value`).

    Note: For strings, this might or might not be case sensitive, depending on your database collations.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column == value
