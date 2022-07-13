"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from validataclass_search_queries.sorting import SortingDirection, SortingDirectionValidator


def test_hello_world():
    assert SortingDirectionValidator().validate('ASC') == SortingDirection.ASC
