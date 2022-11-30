"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from enum import Enum
from typing import Any, Optional, List, Type, Iterable

from validataclass.validators import Validator, ListValidator, IntegerValidator, AnyOfValidator, EnumValidator, \
    T_ListItem, T_Enum

__all__ = [
    'MultiSelectValidator',
    'MultiSelectIntegerValidator',
    'MultiSelectAnyOfValidator',
    'MultiSelectEnumValidator',
]


# TODO: Base on StringToListValidator from upstream validataclass when implemented.
class MultiSelectValidator(ListValidator[T_ListItem]):
    """
    Validator for multi-select search parameters.

    Accepts a string as input, splits it to a list of strings using a delimiter (defaults to ",") and validates the
    resulting list using a specified item validator (based on the `ListValidator`).

    The validator assumes a minimum list length of 1. A maximum list length can be optionally specified using `max_length`.

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
        item_validator: Validator,
        *,
        delimiter: str = ',',
        max_length: Optional[int] = None,
    ):
        """
        Create a MultiSelectValidator with a given item validator.

        Parameters:
            item_validator: Validator, used to validate the items in the list (required)
            delimiter: String, specifies the string that separates the list items in the input string (default: ',')
            max_length: Integer, specifies maximum length of input list (default: None, no maximum length)
        """
        # Initialize base ListValidator
        super().__init__(
            item_validator,
            min_length=1,
            max_length=max_length,
        )
        self.delimiter = delimiter

    def validate(self, input_data: Any, **kwargs) -> List[T_ListItem]:
        """
        Validate input data as string. Returns a validated list.
        """
        self._ensure_type(input_data, str)

        # Split string to list and validate items
        value_list = input_data.split(self.delimiter)
        return super().validate(value_list, **kwargs)


class MultiSelectIntegerValidator(MultiSelectValidator[int]):
    """
    Validator for multi-select search parameters that only allows integers.

    Shortcut for a `MultiSelectValidator` with an `IntegerValidator`.
    """

    def __init__(
        self,
        *,
        # Integer validator settings
        min_value: Optional[int] = IntegerValidator.DEFAULT_MIN_VALUE,
        max_value: Optional[int] = IntegerValidator.DEFAULT_MAX_VALUE,
        # List settings
        delimiter: str = ',',
        max_length: Optional[int] = None,
    ):
        """
        Create a MultiSelectValidator using a IntegerValidator to validate the items.
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


class MultiSelectAnyOfValidator(MultiSelectValidator):
    """
    Validator for multi-select search parameters that only allows a specified set of values.

    Shortcut for a `MultiSelectValidator` with an `AnyOfValidator`.
    """

    def __init__(
        self,
        # AnyOfValidator settings
        allowed_values: Iterable[Any],
        # TODO: case_insensitive is deprecated in validataclass and must be removed in a future version.
        case_sensitive: Optional[bool] = None,
        case_insensitive: Optional[bool] = None,
        *,
        # List settings
        delimiter: str = ',',
        max_length: Optional[int] = None,
    ):
        """
        Create a MultiSelectValidator using a AnyOfValidator to validate the items.
        """
        super().__init__(
            AnyOfValidator(allowed_values, case_sensitive=case_sensitive, case_insensitive=case_insensitive),
            delimiter=delimiter,
            max_length=max_length,
        )


class MultiSelectEnumValidator(MultiSelectValidator[T_Enum]):
    """
    Validator for multi-select search parameters that allows values from an Enum class.

    Shortcut for a `MultiSelectValidator` with an `EnumValidator`.
    """

    def __init__(
        self,
        # EnumValidator settings
        enum_cls: Type[Enum],
        *,
        allowed_values: Optional[Iterable[Any]] = None,
        # TODO: case_insensitive is deprecated in validataclass and must be removed in a future version.
        case_sensitive: Optional[bool] = None,
        case_insensitive: Optional[bool] = None,
        # List settings
        delimiter: str = ',',
        max_length: Optional[int] = None,
    ):
        """
        Create a MultiSelectValidator using a EnumValidator to validate the items.
        """
        super().__init__(
            EnumValidator(enum_cls, allowed_values=allowed_values, case_sensitive=case_sensitive, case_insensitive=case_insensitive),
            delimiter=delimiter,
            max_length=max_length,
        )
