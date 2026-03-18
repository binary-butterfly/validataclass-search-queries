"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest
from validataclass.exceptions import ListItemsValidationError, ListLengthError
from validataclass.validators import EnumValidator, StringValidator

from tests.helpers import UnitTestEnum
from validataclass_search_queries.validators import MultiSelectValidator


@pytest.mark.parametrize(
    'item_validator, input_data, expected_result',
    [
        (StringValidator(min_length=1), 'foo', ['foo']),
        (StringValidator(min_length=1), 'foo,bar,baz', ['foo', 'bar', 'baz']),

        (StringValidator(), ',', ['', '']),
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
        (StringValidator(min_length=1), ','),
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


@pytest.mark.parametrize(
    'item_validator',
    [
        StringValidator(),
        StringValidator(min_length=1),
    ]
)
def test_multi_select_validator_invalid_empty_string_list_length_error(item_validator):
    """
    Test the MultiSelectAnyOfValidator with an empty string as input, which should result in a ListLengthError because
    it's parsed as an empty list and the base ListValidator always has a min_length of 1.
    """
    validator = MultiSelectValidator(item_validator)
    with pytest.raises(ListLengthError):
        validator.validate('')


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
        validator.validate('a,b,c,d')
