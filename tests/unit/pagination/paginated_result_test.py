"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest

from validataclass_search_queries.pagination import PaginatedResult


@pytest.mark.parametrize(
    'input_list, total_count',
    [
        ([], 0),
        ([1, 3, 1, 2], 42),
        ([{'foo': 1}, {'bar': 2}], 2)
    ]
)
def test_paginated_result(input_list, total_count):
    """ Test the PaginatedResult class. """
    paginated_result = PaginatedResult(input_list, total_count=total_count)
    assert paginated_result == input_list
    assert len(paginated_result) == len(input_list)
    assert paginated_result.total_count == total_count
