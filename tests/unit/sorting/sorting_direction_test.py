"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest
from validataclass.exceptions import ValidationError

from validataclass_search_queries.sorting import SortingDirection, SortingDirectionValidator


@pytest.mark.parametrize(
    'input_data, expected_result',
    [
        ('ASC', SortingDirection.ASC),
        ('Asc', SortingDirection.ASC),
        ('asc', SortingDirection.ASC),
        ('DESC', SortingDirection.DESC),
        ('Desc', SortingDirection.DESC),
        ('desc', SortingDirection.DESC),
    ]
)
def test_sorting_direction_validator_valid_input(input_data, expected_result):
    """ Test the SortingDirectionValidator with valid input. """
    validator = SortingDirectionValidator()
    assert validator.validate(input_data) is expected_result


@pytest.mark.parametrize(
    'input_data, expected_error_code',
    [
        (None, 'required_value'),
        (False, 'invalid_type'),
        (42, 'invalid_type'),
        ('', 'value_not_allowed'),
        ('FOO', 'value_not_allowed'),
    ]
)
def test_sorting_direction_validator_invalid_input(input_data, expected_error_code):
    """ Test that the SortingDirectionValidator raises validation errors for invalid input. """
    validator = SortingDirectionValidator()
    with pytest.raises(ValidationError) as error:
        validator.validate(input_data)

    assert error.value.code == expected_error_code


@pytest.mark.parametrize(
    'allowed_values, input_data, expected_result',
    [
        # Only allow ASC
        ([SortingDirection.ASC], 'asc', SortingDirection.ASC),
        ([SortingDirection.ASC], 'desc', None),
        ([SortingDirection.ASC], 'foo', None),

        # Only allow DESC
        ([SortingDirection.DESC], 'asc', None),
        ([SortingDirection.DESC], 'desc', SortingDirection.DESC),
        ([SortingDirection.DESC], 'foo', None),
    ]
)
def test_sorting_direction_validator_with_allowed_values(allowed_values, input_data, expected_result):
    """ Test the SortingDirectionValidator with the allowed_values parameter. """
    validator = SortingDirectionValidator(allowed_values=allowed_values)

    # We use None here as a special value for "validator should raise error"
    if expected_result is None:
        with pytest.raises(ValidationError):
            validator.validate(input_data)
    else:
        assert validator.validate(input_data) == expected_result
