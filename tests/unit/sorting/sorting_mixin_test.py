"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest
import sqlalchemy
from sqlalchemy.sql import ColumnElement
from validataclass.dataclasses import validataclass, Default
from validataclass.exceptions import DictFieldsValidationError
from validataclass.validators import DataclassValidator, AnyOfValidator

from validataclass_search_queries.sorting import SortingMixin, SortingDirection


class MockModelCls:
    """ This class is used as a mock for a database model class. """
    id = sqlalchemy.column('id')
    unit_test_field = sqlalchemy.column('unit_test_field')


def test_sorting_mixin_get_order_column():
    """ Test SortingMixin without validation. """
    # It's supposed to be used as a mixin, but it should function on its own, too.
    # (Also, we bypass the validators here by creating the object directly, so we can test with any sorted_by key.)
    sorting_mixin = SortingMixin(sorted_by='unit_test_field', sorting_direction=SortingDirection.DESC)
    order_column = sorting_mixin.get_order_column(MockModelCls)

    assert isinstance(order_column, ColumnElement)
    assert str(order_column) == 'unit_test_field DESC'


@pytest.mark.parametrize(
    'query_input, expected_order_column_str',
    [
        # Defaults
        ({}, 'id ASC'),
        ({'sorted_by': 'id'}, 'id ASC'),
        ({'sorting_direction': 'DESC'}, 'id DESC'),

        # Explicit values
        ({'sorted_by': 'id', 'sorting_direction': 'ASC'}, 'id ASC'),
        ({'sorted_by': 'id', 'sorting_direction': 'DESC'}, 'id DESC'),
    ]
)
def test_sorting_mixin_with_validation_valid(query_input, expected_order_column_str):
    """ Test SortingMixin (as an independent class) with validation with valid input. """
    query_validator = DataclassValidator(SortingMixin)

    # Validate input and get order column
    sorting_mixin = query_validator.validate(query_input)
    order_column = sorting_mixin.get_order_column(MockModelCls)

    assert isinstance(order_column, ColumnElement)
    assert str(order_column) == expected_order_column_str


def test_sorting_mixin_with_validation_invalid():
    """ Test SortingMixin (as an independent class) with validation with invalid input. """
    query_validator = DataclassValidator(SortingMixin)

    with pytest.raises(DictFieldsValidationError) as error:
        query_validator.validate({
            'sorted_by': 'banana',
            'sorting_direction': 'banana',
        })

    assert error.value.to_dict() == {
        'code': 'field_errors',
        'field_errors': {
            'sorted_by': {'code': 'value_not_allowed'},
            'sorting_direction': {'code': 'value_not_allowed'},
        },
    }


@pytest.mark.parametrize(
    'query_input, expected_order_column_str',
    [
        # Defaults
        ({}, 'unit_test_field DESC'),
        ({'sorted_by': 'id'}, 'id DESC'),
        ({'sorting_direction': 'ASC'}, 'unit_test_field ASC'),

        # Explicit values
        ({'sorted_by': 'id', 'sorting_direction': 'ASC'}, 'id ASC'),
        ({'sorted_by': 'id', 'sorting_direction': 'DESC'}, 'id DESC'),
        ({'sorted_by': 'unit_test_field', 'sorting_direction': 'ASC'}, 'unit_test_field ASC'),
        ({'sorted_by': 'unit_test_field', 'sorting_direction': 'DESC'}, 'unit_test_field DESC'),
    ]
)
def test_dataclass_with_sorting_mixin_with_validation(query_input, expected_order_column_str):
    """ Test a dataclass that uses and customizes the SortingMixin with validation. """

    @validataclass
    class UnitTestSortingQuery(SortingMixin):
        sorted_by: str = AnyOfValidator(['id', 'unit_test_field']), Default('unit_test_field')
        sorting_direction: SortingDirection = Default(SortingDirection.DESC)

    query_validator = DataclassValidator(UnitTestSortingQuery)

    # Validate input and get order column
    sorting_mixin = query_validator.validate(query_input)
    order_column = sorting_mixin.get_order_column(MockModelCls)

    assert isinstance(order_column, ColumnElement)
    assert str(order_column) == expected_order_column_str
