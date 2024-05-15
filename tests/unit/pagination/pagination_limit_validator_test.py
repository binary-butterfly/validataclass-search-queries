"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest
from validataclass.exceptions import ValidationError

from validataclass_search_queries.pagination import PaginationLimitValidator


@pytest.mark.parametrize(
    'input_data, expected_result',
    [
        # Integers
        (1, 1),
        (42, 42),
        (100000, 100000),

        # Integer strings
        ('1', 1),
        ('42', 42),
        ('100000', 100000),
    ]
)
def test_pagination_limit_validator_default_valid(input_data, expected_result):
    """ Test PaginationLimitValidator with default configuration and valid input. """
    validator = PaginationLimitValidator()
    assert validator.validate(input_data) == expected_result


@pytest.mark.parametrize(
    'input_data, expected_error_code',
    [
        # Always invalid input
        (1.234, 'invalid_type'),
        ('banana', 'invalid_integer'),
        (-1, 'number_range_error'),

        # Pagination is required by default
        (None, 'pagination_required'),
        (0, 'pagination_required'),
        ('0', 'pagination_required'),
    ]
)
def test_pagination_limit_validator_default_invalid(input_data, expected_error_code):
    """ Test PaginationLimitValidator with default configuration and invalid input. """
    validator = PaginationLimitValidator()
    with pytest.raises(ValidationError) as error:
        validator.validate(input_data)
    assert error.value.code == expected_error_code


@pytest.mark.parametrize(
    'input_data, expected_result',
    [
        # Always valid
        (10, 10),
        ('10', 10),

        # No pagination
        (None, None),
        (0, None),
        ('0', None),
    ]
)
def test_pagination_limit_validator_optional_valid(input_data, expected_result):
    """ Test PaginationLimitValidator with optional=True and valid input. """
    validator = PaginationLimitValidator(optional=True)
    assert validator.validate(input_data) == expected_result


@pytest.mark.parametrize(
    'input_data, expected_error_code',
    [
        # Always invalid input
        (1.234, 'invalid_type'),
        ('banana', 'invalid_integer'),
        (-1, 'number_range_error'),
    ]
)
def test_pagination_limit_validator_optional_invalid(input_data, expected_error_code):
    """ Test PaginationLimitValidator with optional=True and invalid input. """
    validator = PaginationLimitValidator(optional=True)
    with pytest.raises(ValidationError) as error:
        validator.validate(input_data)
    assert error.value.code == expected_error_code


@pytest.mark.parametrize(
    'input_data, expected_result',
    [
        (1, 1),
        (10, 10),
        ('1', 1),
        ('10', 10),
    ]
)
def test_pagination_limit_validator_max_value_valid(input_data, expected_result):
    """ Test PaginationLimitValidator with custom max_value and valid input. """
    validator = PaginationLimitValidator(max_value=10)
    assert validator.validate(input_data) == expected_result


@pytest.mark.parametrize(
    'input_data, expected_error_code',
    [
        # Always invalid input
        (1.234, 'invalid_type'),
        ('banana', 'invalid_integer'),
        (-1, 'number_range_error'),

        # Not optional
        (0, 'pagination_required'),

        # Too high
        (11, 'number_range_error'),
        ('11', 'number_range_error'),
    ]
)
def test_pagination_limit_validator_max_value_invalid(input_data, expected_error_code):
    """ Test PaginationLimitValidator with custom max_value and invalid input. """
    validator = PaginationLimitValidator(max_value=10)
    with pytest.raises(ValidationError) as error:
        validator.validate(input_data)
    assert error.value.code == expected_error_code
