"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest
from validataclass.exceptions import ListItemsValidationError, ListLengthError
from validataclass.validators import StringValidator, EnumValidator

from tests.helpers import UnitTestEnum
from validataclass_search_queries.validators import MultiSelectValidator, MultiSelectIntegerValidator


# Tests for MultiSelectValidator

@pytest.mark.parametrize(
    'item_validator, input_data, expected_result',
    [
        (StringValidator(min_length=1), 'foo', ['foo']),
        (StringValidator(min_length=1), 'foo,bar,baz', ['foo', 'bar', 'baz']),

        (StringValidator(), '', ['']),
        (StringValidator(), 'foo,', ['foo', '']),

        (EnumValidator(UnitTestEnum), 'foo', [UnitTestEnum.FOO]),
        (EnumValidator(UnitTestEnum), 'foo,baz', [UnitTestEnum.FOO, UnitTestEnum.BAZ]),
    ]
)
def test_multi_select_validator_valid_input(item_validator, input_data, expected_result):
    """ Test the MultiSelectValidator with valid input. """
    validator = MultiSelectValidator(item_validator)
    assert validator.validate(input_data) == expected_result


@pytest.mark.parametrize(
    'item_validator, input_data',
    [
        (StringValidator(min_length=1), ''),
        (StringValidator(min_length=1), 'foo,'),
        (StringValidator(min_length=1), 'foo,,baz'),

        (EnumValidator(UnitTestEnum), 'banana'),
    ]
)
def test_multi_select_validator_invalid_input(item_validator, input_data):
    """ Test the MultiSelectValidator with invalid input. """
    validator = MultiSelectValidator(item_validator)
    with pytest.raises(ListItemsValidationError):
        validator.validate(input_data)


def test_multi_select_validator_with_custom_delimiter():
    """ Test the MultiSelectValidator with a custom delimiter. """
    validator = MultiSelectValidator(StringValidator(min_length=1), delimiter='|')
    assert validator.validate('foo,bar|baz') == ['foo,bar', 'baz']


def test_multi_select_validator_with_max_length():
    """ Test the MultiSelectValidator with a maximum length. """
    validator = MultiSelectValidator(StringValidator(), max_length=3)

    # Valid input
    assert validator.validate('a,b,c') == ['a', 'b', 'c']

    # Invalid input
    with pytest.raises(ListLengthError):
        assert validator.validate('a,b,c,d')


# Tests for MultiSelectIntegerValidator

@pytest.mark.parametrize(
    'input_data, expected_result',
    [
        ('1', [1]),
        ('10', [10]),
        ('1,3,1,2', [1, 3, 1, 2]),
    ]
)
def test_multi_select_integer_validator_valid_input(input_data, expected_result):
    """ Test the MultiSelectIntegerValidator with valid input. """
    validator = MultiSelectIntegerValidator(min_value=1, max_value=10)
    assert validator.validate(input_data) == expected_result


@pytest.mark.parametrize(
    'input_data',
    [
        '',
        'banana',
        '0',
        '11',
    ]
)
def test_multi_select_integer_validator_invalid_input(input_data):
    """ Test the MultiSelectIntegerValidator with invalid input. """
    validator = MultiSelectIntegerValidator(min_value=1, max_value=10)
    with pytest.raises(ListItemsValidationError):
        validator.validate(input_data)


def test_multi_select_integer_validator_with_custom_delimiter():
    """ Test the MultiSelectIntegerValidator with a custom delimiter. """
    validator = MultiSelectIntegerValidator(delimiter='|')
    assert validator.validate('1|2|3') == [1, 2, 3]


def test_multi_select_integer_validator_with_max_length():
    """ Test the MultiSelectIntegerValidator with a maximum length. """
    validator = MultiSelectIntegerValidator(max_length=3)

    # Valid input
    assert validator.validate('123,456,789') == [123, 456, 789]

    # Invalid input
    with pytest.raises(ListLengthError):
        assert validator.validate('1,2,3,4')
