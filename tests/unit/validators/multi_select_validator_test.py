"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest
from validataclass.exceptions import ListItemsValidationError, ListLengthError
from validataclass.validators import StringValidator, EnumValidator, IntegerValidator

from tests.helpers import UnitTestEnum
from validataclass_search_queries.validators import (
    MultiSelectValidator,
    MultiSelectIntegerValidator,
    MultiSelectAnyOfValidator,
    MultiSelectEnumValidator,
)


# Tests for MultiSelectValidator

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


@pytest.mark.parametrize(
    'validator', [
        MultiSelectValidator(StringValidator()),
        MultiSelectValidator(IntegerValidator()),
        MultiSelectValidator(EnumValidator(UnitTestEnum)),
        MultiSelectIntegerValidator(),
        MultiSelectAnyOfValidator(['foo', 'bar', 'baz']),
        MultiSelectEnumValidator(UnitTestEnum),
    ]
)
def test_multi_select_validator_invalid_empty_string_list_length_error(validator):
    """
    Test the MultiSelectValidator and its subclasses with an empty string as input
    (which is parsed as an empty list and always invalid because the base ListValidator has a min_length of 1).
    """
    # Empty string input fails at the list length validation, regardless of item validator.
    with pytest.raises(ListLengthError):
        validator.validate('')


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


# Tests for MultiSelectAnyOfValidator

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


# Tests for MultiSelectEnumValidator

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
