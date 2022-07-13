"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import List, TypeVar

__all__ = [
    'PaginatedResult',
    'T_Result',
]

T_Result = TypeVar('T_Result')


class PaginatedResult(List[T_Result]):
    """
    Custom list type for paginated database query results.

    This type behaves exactly like a regular list, but has the additional attribute "total_count" which should be set to
    the total amount of results before the query was paginated (i.e. before the `LIMIT` was applied to the SQL query).
    """

    # Total amount of results in the original query (before pagination)
    total_count: int

    def __init__(self, *args, total_count: int):
        super().__init__(*args)
        self.total_count = total_count
