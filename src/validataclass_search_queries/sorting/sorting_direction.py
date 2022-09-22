"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from enum import Enum
from typing import Any, List, cast

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


class SortingDirectionValidator(EnumValidator):
    """
    Custom EnumValidator for the SortingDirection enum that allows the input to be case-insensitive.
    """

    def __init__(self, *, allowed_values: List[Any] = None):
        """
        The parameter "allowed_values" can be set to `[SortingDirection.ASC]` or `[SortingDirection.DESC]` to enforce a
        specific sorting direction.
        """
        super().__init__(SortingDirection, allowed_values=allowed_values)

    def validate(self, input_data: Any, **kwargs) -> SortingDirection:
        """
        Validates an input string to be a valid sorting direction ("ASC" or "DESC", case-insensitively) and returns
        a member of the SortingDirection enum.
        """
        self._ensure_type(input_data, str)

        # Allow case-insensitive values
        validated_data = super().validate(input_data.upper(), **kwargs)

        # Trick type checkers to believe that validated_data is really a SortingDirection. (Necessary because the base
        # EnumValidator just has Enum as return type: https://github.com/binary-butterfly/validataclass/issues/73)
        return cast(SortingDirection, validated_data)
