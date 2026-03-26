"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from collections.abc import Iterable
from typing import Any

from validataclass.validators import AnyOfValidator

from .multi_select_validator import MultiSelectValidator

__all__ = [
    'MultiSelectAnyOfValidator',
]


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
        case_sensitive: bool | None = None,
        case_insensitive: bool | None = None,
        *,
        # List settings
        delimiter: str = ',',
        max_length: int | None = None,
    ):
        """
        Create a `MultiSelectValidator` using an `AnyOfValidator` to validate the items.
        """
        super().__init__(
            AnyOfValidator(
                allowed_values,
                case_sensitive=case_sensitive,
                case_insensitive=case_insensitive,
            ),
            delimiter=delimiter,
            max_length=max_length,
        )
