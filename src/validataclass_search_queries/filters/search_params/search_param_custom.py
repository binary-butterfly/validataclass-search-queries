"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from sqlalchemy.sql import ColumnElement

from .base_search_param import SearchParam

__all__ = [
    'SearchParamCustom',
]


class SearchParamCustom(SearchParam):
    """
    Search parameter for custom filters that need to be implemented *manually* (e.g. in the repository).

    This filter will always raise a `NotImplementedError` if used directly. The purpose of this SearchParam class is to
    ensure that a search parameter can only be used if the actual filteris implemented directly in the repository by
    overriding either `_apply_bound_search_filter` or `_filter_by_search_query`.
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        raise NotImplementedError('Custom search parameter needs to be handled in the repository!')
