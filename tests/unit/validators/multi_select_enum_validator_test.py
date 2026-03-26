"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest
from validataclass.exceptions import ListItemsValidationError, ListLengthError

from tests.helpers import UnitTestEnum
from validataclass_search_queries.validators import MultiSelectEnumValidator


def test_multi_select_enum_validator_valid_input():
    """ Test the MultiSelectEnumValidator with valid input (case-insensitive). """
    validator = MultiSelectEnumValidator(UnitTestEnum)
    assert validator.validate('Foo,baz,BAR') == [UnitTestEnum.FOO, UnitTestEnum.BAZ, UnitTestEnum.BAR]


@pytest.mark.parametrize(
    'input_data', [
        ',',
        '0',
        'banana',
        'foo|bar',
    ]
)
def test_multi_select_enum_validator_invalid_input(input_data):
    """ Test the MultiSelectEnumValidator with invalid input. """
    validator = MultiSelectEnumValidator(UnitTestEnum)
    with pytest.raises(ListItemsValidationError):
        validator.validate(input_data)


def test_multi_select_enum_validator_invalid_empty_string():
    """
    Test the MultiSelectEnumValidator with an empty string as input, which should result in a ListLengthError because
    it's parsed as an empty list and the base ListValidator always has a min_length of 1.
    """
    validator = MultiSelectEnumValidator(UnitTestEnum)
    with pytest.raises(ListLengthError):
        validator.validate('')


def test_multi_select_enum_validator_with_allowed_values():
    """ Test the MultiSelectEnumValidator with the allowed_values parameter. """
    validator = MultiSelectEnumValidator(UnitTestEnum, allowed_values=[UnitTestEnum.FOO])

    # Valid input
    assert validator.validate('foo,foo') == [UnitTestEnum.FOO, UnitTestEnum.FOO]

    # Invalid input
    with pytest.raises(ListItemsValidationError):
        validator.validate('foo,bar')


def test_multi_select_enum_validator_case_sensitive_valid():
    """ Test the MultiSelectEnumValidator with case_sensitive=True. """
    validator = MultiSelectEnumValidator(UnitTestEnum, case_sensitive=True)

    # Valid input
    assert validator.validate('foo,baz,bar') == [UnitTestEnum.FOO, UnitTestEnum.BAZ, UnitTestEnum.BAR]

    # Invalid input
    with pytest.raises(ListItemsValidationError):
        validator.validate('foo,banana')


@pytest.mark.parametrize('input_data', ['FOO', 'foo,BAZ'])
def test_multi_select_enum_validator_case_sensitive_invalid(input_data):
    """ Test the MultiSelectEnumValidator with case_sensitive=True. """
    validator = MultiSelectEnumValidator(UnitTestEnum, case_sensitive=True)
    with pytest.raises(ListItemsValidationError):
        validator.validate(input_data)


def test_multi_select_enum_validator_with_custom_delimiter():
    """ Test the MultiSelectEnumValidator with a custom delimiter. """
    validator = MultiSelectEnumValidator(UnitTestEnum, delimiter='|')

    # Valid input
    assert validator.validate('foo|baz') == [UnitTestEnum.FOO, UnitTestEnum.BAZ]

    # Invalid input
    with pytest.raises(ListItemsValidationError):
        validator.validate('foo,bar')


def test_multi_select_enum_validator_with_max_length():
    """ Test the MultiSelectEnumValidator with a maximum length. """
    validator = MultiSelectEnumValidator(UnitTestEnum, max_length=2)

    # Valid input
    assert validator.validate('foo,baz') == [UnitTestEnum.FOO, UnitTestEnum.BAZ]

    # Invalid input
    with pytest.raises(ListLengthError):
        validator.validate('foo,bar,baz')
