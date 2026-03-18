"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from collections.abc import Iterable
from enum import Enum
from typing import Any, TypeVar

from validataclass.validators import EnumValidator

from .multi_select_validator import MultiSelectValidator

__all__ = [
    'MultiSelectEnumValidator',
]

T_Enum = TypeVar('T_Enum', bound=Enum)


class MultiSelectEnumValidator(MultiSelectValidator[T_Enum]):
    """
    Validator for multi-select search parameters that allows values from an Enum class.

    Shortcut for a `MultiSelectValidator` with an `EnumValidator`.
    """

    def __init__(
        self,
        # EnumValidator settings
        enum_cls: type[Enum],
        *,
        allowed_values: Iterable[Any] | None = None,
        # TODO: case_insensitive is deprecated in validataclass and must be removed in a future version.
        case_sensitive: bool | None = None,
        case_insensitive: bool | None = None,
        # List settings
        delimiter: str = ',',
        max_length: int | None = None,
    ):
        """
        Create a `MultiSelectValidator` using an `EnumValidator` to validate the items.
        """
        super().__init__(
            EnumValidator(
                enum_cls,
                allowed_values=allowed_values,
                case_sensitive=case_sensitive,
                case_insensitive=case_insensitive,
            ),
            delimiter=delimiter,
            max_length=max_length,
        )
