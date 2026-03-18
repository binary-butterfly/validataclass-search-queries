"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from validataclass.validators import IntegerValidator

from .multi_select_validator import MultiSelectValidator

__all__ = [
    'MultiSelectIntegerValidator',
]


class MultiSelectIntegerValidator(MultiSelectValidator[int]):
    """
    Validator for multi-select search parameters that only allows integers.

    Shortcut for a `MultiSelectValidator` with an `IntegerValidator`.
    """

    def __init__(
        self,
        *,
        # Integer validator settings
        min_value: int | None = IntegerValidator.DEFAULT_MIN_VALUE,
        max_value: int | None = IntegerValidator.DEFAULT_MAX_VALUE,
        # List settings
        delimiter: str = ',',
        max_length: int | None = None,
    ):
        """
        Create a `MultiSelectValidator` using an `IntegerValidator` to validate the items.
        """
        # Initialize base MultiSelectValidator and IntegerValidator
        super().__init__(
            IntegerValidator(
                min_value=min_value,
                max_value=max_value,
                allow_strings=True,
            ),
            delimiter=delimiter,
            max_length=max_length,
        )
