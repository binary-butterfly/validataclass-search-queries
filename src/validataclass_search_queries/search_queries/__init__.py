"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from .base_search_query import BaseSearchQuery
from .search_query_dataclass import search_query_dataclass

__all__ = [
    'BaseSearchQuery',
    'search_query_dataclass',
]
