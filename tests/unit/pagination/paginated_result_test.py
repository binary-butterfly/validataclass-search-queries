"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

import pytest

from validataclass_search_queries.pagination import PaginatedResult


class MockItem:
    """ Used to test PaginatedResult with objects. """

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name


class MockItemToDictable(MockItem):
    """ Variation of MockItem that has a to_dict() method. """

    def to_dict(self) -> dict[str, Any]:
        return {'name': self.name}


class MockMapper:
    """ Class with mapper methods to test PaginatedResult.map(). """

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def map_static(item: MockItem) -> str:
        return str(item)

    @classmethod
    def map_class(cls, item: MockItem) -> str:
        return f'[{cls.__name__}] {item}'

    def map_instance(self, item: MockItem) -> str:
        return f'[{self.name}] {item}'


@pytest.mark.parametrize(
    'input_list, total_count',
    [
        ([], 0),
        ([1, 3, 1, 2], 42),
        ([{'foo': 1}, {'bar': 2}], 10),
        ([MockItem('foo'), MockItemToDictable('bar')], 10),
    ]
)
def test_paginated_result(input_list, total_count):
    """ Test base functionality of PaginatedResult (behaves like a list with an extra attribute). """
    paginated_result = PaginatedResult(input_list, total_count=total_count)
    assert paginated_result == input_list
    assert len(paginated_result) == len(input_list)
    assert paginated_result.total_count == total_count


@pytest.mark.parametrize(
    'paginated_result, expected_dict',
    [
        (
            PaginatedResult([], total_count=0),
            {'items': [], 'total_count': 0},
        ),
        (
            PaginatedResult([1, 3, 1, 2], total_count=42),
            {'items': [1, 3, 1, 2], 'total_count': 42},
        ),
        (
            PaginatedResult([{'foo': 1}, {'bar': 2}], total_count=12),
            {'items': [{'foo': 1}, {'bar': 2}], 'total_count': 12},
        ),
        (
            PaginatedResult([MockItem('foo'), MockItem('bar')], total_count=12),
            {'items': [MockItem('foo'), MockItem('bar')], 'total_count': 12},
        ),
    ]
)
def test_paginated_result_to_dict_basic_types(paginated_result, expected_dict):
    """ Test PaginatedResult.to_dict() with basic types and objects without to_dict() method (recursive and non-recursive). """
    assert paginated_result.to_dict() == expected_dict
    assert paginated_result.to_dict(recursive=False) == expected_dict
    assert paginated_result.to_dict(recursive=True) == expected_dict


@pytest.mark.parametrize(
    'paginated_result, expected_dict, expected_dict_recursive',
    [
        (
            PaginatedResult([MockItemToDictable('foo'), MockItemToDictable('bar')], total_count=12),
            {'items': [MockItemToDictable('foo'), MockItemToDictable('bar')], 'total_count': 12},
            {'items': [{'name': 'foo'}, {'name': 'bar'}], 'total_count': 12},
        ),
        (
            PaginatedResult([123, MockItem('foo'), MockItemToDictable('bar')], total_count=13),
            {'items': [123, MockItem('foo'), MockItemToDictable('bar')], 'total_count': 13},
            {'items': [123, MockItem('foo'), {'name': 'bar'}], 'total_count': 13},
        ),
    ]
)
def test_paginated_result_to_dict_with_to_dictable(paginated_result, expected_dict, expected_dict_recursive):
    """ Test PaginatedResult.to_dict() with objects that have a to_dict() method (recursive and non-recursive). """
    assert paginated_result.to_dict() == expected_dict
    assert paginated_result.to_dict(recursive=False) == expected_dict
    assert paginated_result.to_dict(recursive=True) == expected_dict_recursive


@pytest.mark.parametrize(
    'paginated_result, map_func, expected_mapped_items',
    [
        (
            PaginatedResult([1, 3, 1, 2], total_count=10),
            lambda x: str(x),
            ['1', '3', '1', '2'],
        ),
        (
            PaginatedResult([1, 2, 3], total_count=10),
            MockMapper.map_static,
            ['1', '2', '3'],
        ),
        (
            PaginatedResult([1, 2, 3], total_count=10),
            MockMapper.map_class,
            ['[MockMapper] 1', '[MockMapper] 2', '[MockMapper] 3'],
        ),
        (
            PaginatedResult([1, 2, 3], total_count=10),
            MockMapper('unittest').map_instance,
            ['[unittest] 1', '[unittest] 2', '[unittest] 3'],
        ),
        (
            PaginatedResult([MockItemToDictable('foo'), MockItemToDictable('bar')], total_count=10),
            MockItemToDictable.to_dict,
            [{'name': 'foo'}, {'name': 'bar'}],
        ),
    ]
)
def test_paginated_result_map(paginated_result, map_func, expected_mapped_items):
    """ Test PaginatedResult.map() with different kinds of mapping functions. """
    mapped_result = paginated_result.map(map_func)
    assert mapped_result == expected_mapped_items
    assert mapped_result.total_count == paginated_result.total_count
