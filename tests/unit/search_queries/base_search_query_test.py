"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Iterator

import pytest
from validataclass.dataclasses import DefaultUnset
from validataclass.exceptions import DictFieldsValidationError
from validataclass.helpers import UnsetValue, UnsetValueType
from validataclass.validators import DataclassValidator, EnumValidator, IntegerValidator, StringValidator

from helpers import UnitTestEnum
from validataclass_search_queries.filters import BoundSearchFilter, SearchParamEquals, SearchParamGreaterThan
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass


@search_query_dataclass
class UnitTestSearchQuery(BaseSearchQuery):
    """ Example search query dataclass to use in unit tests. """

    # Regular validataclass field (should be ignored by get_search_filters)
    regular_required: str = StringValidator()

    # Simple search parameter with default column name (auto-determined from field name) and implicit default None
    filter1: int | None = SearchParamEquals(), IntegerValidator(allow_strings=True)

    # Search parameter with explicit column name
    filter2: int | None = SearchParamEquals('example_column'), IntegerValidator(allow_strings=True)

    # Search parameter with explicit default UnsetValue
    filter3: int | UnsetValueType = SearchParamGreaterThan(), IntegerValidator(allow_strings=True), DefaultUnset


def test_search_query_manual_instantiation_with_minimal_data():
    """ Test manual instantiation of a search query dataclass with minimal data (i.e. only required fields). """
    search_query = UnitTestSearchQuery(regular_required='test')

    # Check values
    assert search_query.regular_required == 'test'
    assert search_query.filter1 is None
    assert search_query.filter2 is None
    assert search_query.filter3 is UnsetValue

    # Only set fields are regular validataclass fields, so there should be no search filters
    assert list(search_query.get_search_filters()) == []

    # Check result of to_dict()
    assert search_query.to_dict() == {
        'regular_required': 'test',
    }


def test_search_query_manual_instantiation_with_complete_data():
    """ Test manual instantiation of a search query dataclass with complete data (all fields set). """
    search_query = UnitTestSearchQuery(
        regular_required='foo',
        filter1=42,
        filter2=1312,
        filter3=10,
    )

    # Check values
    assert search_query.regular_required == 'foo'
    assert search_query.filter1 == 42
    assert search_query.filter2 == 1312
    assert search_query.filter3 == 10

    # Check that get_search_filters returns an Iterator
    assert isinstance(search_query.get_search_filters(), Iterator)

    # Check bound search filters (should only contain fields with SearchParam)
    bound_filters = [
        (field_name, bound_filter.column_name, type(bound_filter.search_param), bound_filter.value)
        for field_name, bound_filter in search_query.get_search_filters()
    ]
    assert bound_filters == [
        ('filter1', 'filter1', SearchParamEquals, 42),
        ('filter2', 'example_column', SearchParamEquals, 1312),
        ('filter3', 'filter3', SearchParamGreaterThan, 10),
    ]

    # Check result of to_dict()
    assert search_query.to_dict() == {
        'regular_required': 'foo',
        'filter1': 42,
        'filter2': 1312,
        'filter3': 10,
    }


def test_search_query_with_dataclass_validator_valid():
    """ Test validation of a search query dataclass with the DataclassValidator. """
    validator = DataclassValidator(UnitTestSearchQuery)
    search_query = validator.validate(
        {
            'regular_required': 'meow',
            'filter1': '42',
        }
    )

    # Check values
    assert search_query.regular_required == 'meow'
    assert search_query.filter1 == 42
    assert search_query.filter2 is None
    assert search_query.filter3 is UnsetValue

    # Check bound search filters (should only contain fields with SearchParam)
    bound_filters: dict[str, BoundSearchFilter] = dict(search_query.get_search_filters())
    assert list(bound_filters.keys()) == ['filter1']
    assert bound_filters['filter1'].column_name == 'filter1'
    assert bound_filters['filter1'].value == 42
    assert type(bound_filters['filter1'].search_param) is SearchParamEquals

    # Check result of to_dict()
    assert search_query.to_dict() == {
        'regular_required': 'meow',
        'filter1': 42,
    }


def test_search_query_with_dataclass_validator_invalid():
    """ Test validation of a search query dataclass with the DataclassValidator and invalid data. """
    validator = DataclassValidator(UnitTestSearchQuery)

    with pytest.raises(DictFieldsValidationError) as exception_info:
        validator.validate(
            {
                'filter1': 'banana',
                'filter2': True,
            }
        )

    assert exception_info.value.to_dict() == {
        'code': 'field_errors',
        'field_errors': {
            'regular_required': {'code': 'required_field'},
            'filter1': {'code': 'invalid_integer'},
            'filter2': {
                'code': 'invalid_type',
                'expected_types': ['int', 'str'],
            },
        },
    }


def test_to_dict_with_enums():
    """ Test that `BaseSearchQuery.to_dict()` properly converts enums to their values. """

    @search_query_dataclass
    class SearchQueryWithEnum(BaseSearchQuery):
        enum_filter: UnitTestEnum | None = SearchParamEquals(), EnumValidator(UnitTestEnum)

    search_query = SearchQueryWithEnum(enum_filter=UnitTestEnum.FOO)
    assert search_query.to_dict() == {
        'enum_filter': 'foo',
    }
