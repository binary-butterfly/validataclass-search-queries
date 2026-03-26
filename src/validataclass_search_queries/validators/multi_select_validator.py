"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, TypeVar

from typing_extensions import override
from validataclass.validators import ListValidator, Validator

__all__ = [
    'MultiSelectValidator',
]

T_ListItem = TypeVar('T_ListItem')


# TODO: Base on StringToListValidator from upstream validataclass when implemented.
class MultiSelectValidator(ListValidator[T_ListItem]):
    """
    Validator for multi-select search parameters.

    Accepts a string as input, splits it to a list of strings using a delimiter (defaults to ",") and validates the
    resulting list using a specified item validator (based on the `ListValidator`).

    The validator assumes a minimum list length of 1. A maximum length can be optionally specified using `max_length`.

    The item validator can be any validator that accepts strings as input.

    Example:

    ```
    # Validates a comma separated list of integers
    MultiSelectValidator(IntegerValidator(min_value=0, allow_strings=True))

    # Same, but using a different delimiter
    MultiSelectValidator(IntegerValidator(min_value=0, allow_strings=True), delimiter=';')
    ```
    """

    # Delimiter to separate items in the input string
    delimiter: str

    def __init__(
        self,
        item_validator: Validator[T_ListItem],
        *,
        delimiter: str = ',',
        max_length: int | None = None,
    ):
        """
        Create a `MultiSelectValidator` with a given item validator.

        Parameters:
            `item_validator`: `Validator`, used to validate the items in the list (required)
            `delimiter`: `str`, specifies the string that separates the list items in the input string (default: ',')
            `max_length`: `int`, specifies maximum length of input list (default: `None`, no maximum length)
        """
        # Initialize base ListValidator
        super().__init__(
            item_validator,
            min_length=1,
            max_length=max_length,
        )
        self.delimiter = delimiter

    @override
    def validate(self, input_data: Any, **kwargs) -> list[T_ListItem]:
        """
        Validate input data as string. Returns a validated list.
        """
        self._ensure_type(input_data, str)

        if input_data == '':
            # Parse empty string to empty list
            value_list = []
        else:
            # Split string to list
            value_list = input_data.split(self.delimiter)

        # Validate list items
        return super().validate(value_list, **kwargs)
