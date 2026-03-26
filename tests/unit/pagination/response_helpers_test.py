"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from dataclasses import dataclass
from typing import Any

import pytest

from validataclass_search_queries.pagination import (
    CursorPaginationMixin,
    OffsetPaginationMixin,
    PaginatedResult,
    paginated_api_response,
)
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass


@dataclass
class MockItem:
    """ Object used to test the response helper functions. """
    id: int

    def to_dict(self) -> dict[str, Any]:
        return {'id': self.id}


@search_query_dataclass
class ExampleQueryCursorPagination(CursorPaginationMixin, BaseSearchQuery):
    """ Search query with offset pagination for testing the response helper functions. """


@search_query_dataclass
class ExampleQueryOffsetPagination(OffsetPaginationMixin, BaseSearchQuery):
    """ Search query with offset pagination for testing the response helper functions. """


@pytest.mark.parametrize(
    'paginated_result, search_query, expected_response',
    [
        (
            # No search query (and thus no pagination)
            PaginatedResult([1, 3, 1, 2], total_count=10),
            None,
            {
                'items': [1, 3, 1, 2],
                'total_count': 10,
            },
        ),
        (
            # Empty result (implies last page)
            PaginatedResult([], total_count=10),
            ExampleQueryCursorPagination(),
            {
                'items': [],
                'total_count': 10,
            },
        ),
        (
            # Full page with cursor pagination
            PaginatedResult([MockItem(13), MockItem(37), MockItem(41)], total_count=10),
            ExampleQueryCursorPagination(start=13, limit=3),
            {
                'items': [{'id': 13}, {'id': 37}, {'id': 41}],
                'total_count': 10,
                'next_id': 42,
            },
        ),
        (
            # Full page with offset pagination
            PaginatedResult([MockItem(13), MockItem(37), MockItem(41)], total_count=10),
            ExampleQueryOffsetPagination(offset=6, limit=3),
            {
                'items': [{'id': 13}, {'id': 37}, {'id': 41}],
                'total_count': 10,
                'next_offset': 9,
            },
        ),
        (
            # Non-full page (implies last page)
            PaginatedResult([MockItem(99)], total_count=10),
            ExampleQueryOffsetPagination(offset=9, limit=3),
            {
                'items': [{'id': 99}],
                'total_count': 10,
            },
        ),
    ],
)
def test_paginated_api_response(paginated_result, search_query, expected_response):
    """ Test paginated_api_response() with different search queries and results. """
    assert paginated_api_response(
        paginated_result,
        search_query,
    ) == expected_response


@pytest.mark.parametrize(
    'paginated_result, search_query, original_params, expected_response',
    [
        (
            # Full page with cursor pagination
            PaginatedResult([MockItem(13), MockItem(37), MockItem(41)], total_count=10),
            ExampleQueryCursorPagination(start=13, limit=3),
            None,
            {
                'items': [{'id': 13}, {'id': 37}, {'id': 41}],
                'total_count': 10,
                'next_id': 42,
                'next_path': '/unit/test?start=42&limit=3',
            },
        ),
        (
            # Full page with offset pagination
            PaginatedResult([MockItem(13), MockItem(37), MockItem(41)], total_count=10),
            ExampleQueryOffsetPagination(offset=6, limit=3),
            None,
            {
                'items': [{'id': 13}, {'id': 37}, {'id': 41}],
                'total_count': 10,
                'next_offset': 9,
                'next_path': '/unit/test?offset=9&limit=3',
            },
        ),
        (
            # With original parameters (numbers are strings here, like in HTTP query parameters)
            PaginatedResult([MockItem(13), MockItem(37), MockItem(41)], total_count=10),
            ExampleQueryOffsetPagination(offset=6, limit=3),
            {'foo': 'bar', 'limit': '3', 'offset': '6', 'something': 'else'},
            {
                'items': [{'id': 13}, {'id': 37}, {'id': 41}],
                'total_count': 10,
                'next_offset': 9,
                'next_path': '/unit/test?foo=bar&limit=3&offset=9&something=else',
            },
        ),
    ],
)
def test_paginated_api_response_with_next_path(paginated_result, search_query, original_params, expected_response):
    """ Test paginated_api_response() with request_path and original_params to generate the "next_path" field. """
    assert paginated_api_response(
        paginated_result,
        search_query,
        request_path='/unit/test',
        original_params=original_params,
    ) == expected_response


def test_paginated_api_response_no_recursive_to_dict():
    """ Test paginated_api_response() with recursive_to_dict=False. """
    paginated_result = PaginatedResult([MockItem(13), MockItem(37), MockItem(41)], total_count=10)
    response = paginated_api_response(paginated_result, None, recursive_to_dict=False)

    # Check that items were not modified
    assert response == {
        'items': [MockItem(13), MockItem(37), MockItem(41)],
        'total_count': 10,
    }
