"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional

from validataclass.exceptions import ValidationError
from validataclass.validators import IntegerValidator

__all__ = [
    'PaginationLimitValidator',
    'PaginationLimitRequiredError',
]


class PaginationLimitValidator(IntegerValidator):
    """
    Validator for the pagination limit, based on an IntegerValidator.

    Strings will be automatically converted to integers.

    By default, the validator only allows positive integers. The maximum value is the default maximum value of the
    IntegerValidator (2^32 - 1 = 2147483647), unless specified using `max_value`.

    If the parameter `optional` is set to True, the validator additionally allows the values 0 and None, which are
    returned as None in both cases. This represents "no limit", i.e. no pagination at all, which can be used by the
    user to request an unpaginated result.

    If `optional` is False, a `PaginationLimitRequiredError` exception will be raised for 0 or None as input.

    Examples:

    ```
    # Accepts any positive 32-bit number (i.e. no zero)
    PaginationLimitValidator()

    # Accepts any positive number up to 1000
    PaginationLimitValidator(max_value=1000)

    # Accepts any positive number, but also None and 0 (returns None in both cases)
    PaginationLimitValidator(optional=True)
    ```
    """

    # If true, pagination is optional for the user (set limit=0 to disable pagination)
    optional: bool

    def __init__(
        self,
        *,
        optional: bool = False,
        max_value: Optional[int] = IntegerValidator.DEFAULT_MAX_VALUE,
    ):
        """
        Creates a PaginationLimitValidator.

        If `optional` is True, the validator accepts the value 0 as input, in which case the validator returns None,
        meaning that pagination is disabled (i.e. unlimited results).

        Parameters:
            optional: Boolean, whether pagination is optional, i.e. the user can set limit=0 to disable pagination (default: False)
            max_value: Integer or None, maximum value for pagination limit (default: IntegerValidator.DEFAULT_MAX_VALUE = 2147483647)
        """
        super().__init__(
            min_value=0,  # if optional else 1,
            max_value=max_value,
            allow_strings=True,
        )
        self.optional = optional

    def validate(self, input_data: Any, **kwargs) -> Optional[int]:
        """
        Validates the input as an integer. Returns the integer or None if the input is 0 or None.
        """
        # Treat None as 0 (meaning "no limit" if allowed)
        if input_data is None:
            input_data = 0

        # Validate input as integer
        validated_input = super().validate(input_data, **kwargs)

        # If pagination is optional, treat 0 as "no limit" (i.e. no pagination)
        if validated_input == 0:
            if self.optional:
                return None
            else:
                raise PaginationLimitRequiredError()

        return validated_input


class PaginationLimitRequiredError(ValidationError):
    """
    Validation error raised by PaginationLimitValidator when the user requests an unpaginated result (by specifiying
    limit=0 or None), but pagination is required (optional=False).
    """
    code = 'pagination_required'
