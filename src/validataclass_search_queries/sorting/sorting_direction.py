"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from collections.abc import Iterable
from enum import Enum
from typing import Any

from validataclass.validators import EnumValidator

__all__ = [
    'SortingDirection',
    'SortingDirectionValidator',
]


class SortingDirection(Enum):
    """
    Enum for the sorting direction in a search query.
    """
    ASC = 'ASC'
    DESC = 'DESC'


class SortingDirectionValidator(EnumValidator[SortingDirection]):
    """
    Shortcut for an EnumValidator for the SortingDirection enum. Allows case-insensitive input strings.
    """

    def __init__(self, *, allowed_values: Iterable[Any] | None = None):
        """
        The parameter "allowed_values" can be set to `[SortingDirection.ASC]` or `[SortingDirection.DESC]` to enforce a
        specific sorting direction.
        """
        super().__init__(SortingDirection, allowed_values=allowed_values)
