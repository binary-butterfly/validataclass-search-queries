"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest
from validataclass.exceptions import ListItemsValidationError, ListLengthError

from validataclass_search_queries.validators import MultiSelectIntegerValidator


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
        ',',
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


def test_multi_select_integer_validator_invalid_empty_string():
    """
    Test the MultiSelectIntegerValidator with an empty string as input, which should result in a ListLengthError because
    it's parsed as an empty list and the base ListValidator always has a min_length of 1.
    """
    validator = MultiSelectIntegerValidator()
    with pytest.raises(ListLengthError):
        validator.validate('')


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
        validator.validate('1,2,3,4')
