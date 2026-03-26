"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest
from validataclass.exceptions import ListItemsValidationError, ListLengthError

from validataclass_search_queries.validators import MultiSelectAnyOfValidator


def test_multi_select_any_of_validator_valid_input():
    """ Test the MultiSelectAnyOfValidator with valid input (case-insensitive). """
    validator = MultiSelectAnyOfValidator(['foo', 'BAR', 'baz'])
    assert validator.validate('FOO,baz,Bar') == ['foo', 'baz', 'BAR']


@pytest.mark.parametrize(
    'input_data', [
        ',',
        '0',
        'banana',
        'foo|bar',
    ]
)
def test_multi_select_any_of_validator_invalid_input(input_data):
    """ Test the MultiSelectAnyOfValidator with invalid input. """
    validator = MultiSelectAnyOfValidator(['foo', 'bar', 'baz'])
    with pytest.raises(ListItemsValidationError):
        validator.validate(input_data)


def test_multi_select_any_of_validator_invalid_empty_string():
    """
    Test the MultiSelectAnyOfValidator with an empty string as input, which should result in a ListLengthError because
    it's parsed as an empty list and the base ListValidator always has a min_length of 1.
    """
    validator = MultiSelectAnyOfValidator(['foo', 'bar', 'baz'])
    with pytest.raises(ListLengthError):
        validator.validate('')


def test_multi_select_any_of_validator_case_sensitive_valid():
    """ Test the MultiSelectAnyOfValidator with case_sensitive=True. """
    validator = MultiSelectAnyOfValidator(['foo', 'BAR', 'baz'], case_sensitive=True)
    assert validator.validate('foo,baz,BAR') == ['foo', 'baz', 'BAR']


@pytest.mark.parametrize('input_data', ['FOO', 'bar', 'foo,BAZ'])
def test_multi_select_any_of_validator_case_sensitive_invalid(input_data):
    """ Test the MultiSelectAnyOfValidator with case_sensitive=True. """
    validator = MultiSelectAnyOfValidator(['foo', 'BAR', 'baz'], case_sensitive=True)
    with pytest.raises(ListItemsValidationError):
        validator.validate(input_data)


def test_multi_select_any_of_validator_with_custom_delimiter():
    """ Test the MultiSelectAnyOfValidator with a custom delimiter. """
    validator = MultiSelectAnyOfValidator(['foo', 'bar', 'baz'], delimiter='|')

    # Valid input
    assert validator.validate('foo|baz') == ['foo', 'baz']

    # Invalid input
    with pytest.raises(ListItemsValidationError):
        validator.validate('foo,bar')


def test_multi_select_any_of_validator_with_max_length():
    """ Test the MultiSelectAnyOfValidator with a maximum length. """
    validator = MultiSelectAnyOfValidator(['foo', 'bar', 'baz'], max_length=2)

    # Valid input
    assert validator.validate('foo,baz') == ['foo', 'baz']

    # Invalid input
    with pytest.raises(ListLengthError):
        validator.validate('foo,bar,baz')
