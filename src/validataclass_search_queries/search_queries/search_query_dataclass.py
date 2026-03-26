"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
from collections.abc import Callable
from inspect import get_annotations
from typing import Any, TypeVar, overload

from typing_extensions import dataclass_transform
from validataclass.dataclasses import validataclass, validataclass_field, BaseDefault, Default
from validataclass.exceptions import DataclassValidatorFieldException
from validataclass.validators import Validator

from validataclass_search_queries.filters import SearchParam

__all__ = [
    'search_query_dataclass',
]


@dataclasses.dataclass
class _ValidatorField:
    validator: Validator[Any] | None = None
    default: BaseDefault[Any] | None = None
    search_param: SearchParam | None = None


_T = TypeVar('_T')


# TODO: The special @search_query_dataclass decorator might become obsolete and replaced with the regular @validataclass
#  decorator when custom field options are implemented in validataclass.

@overload
def search_query_dataclass(cls: type[_T]) -> type[_T]:
    ...


@overload
def search_query_dataclass(cls: None = None, /, **kwargs: Any) -> Callable[[type[_T]], type[_T]]:
    ...


@dataclass_transform(
    kw_only_default=True,
    field_specifiers=(dataclasses.field, dataclasses.Field, validataclass_field),
)
def search_query_dataclass(
    cls: type[_T] | None = None,
    /,
    **kwargs: Any,
) -> type[_T] | Callable[[type[_T]], type[_T]]:
    """
    Custom dataclass decorator based on @validataclass, adding support for search parameter fields.

    This decorator generates a validataclass-compatible dataclass that has additional field metadata to define search
    parameters for GET queries (including pagination).

    Fields can be defined in the same way as regular validataclass fields (in tuple format). Additionally, you can use
    objects of the `SearchParam` class (and subclasses) to declare a field as a search parameter.

    If you don't specify a `SearchParam` object (and the field doesn't have one in the base class either), the field
    behaves the same as in a regular validataclass.

    For search parameter fields, an implicit `Default(None)` is assumed. You can overwrite this by setting a Default
    object yourself, but in most cases you'll want `Default(None)`, so that's the default. Keep in mind that you need
    to set the type hints correctly, though (always use `T | None` unless you specified a different default).
    """

    def decorator(_cls: type[_T]) -> type[_T]:
        # Transform class to be a valid validataclass
        _prepare_search_query_dataclass(_cls)

        # Use @validataclass decorator to transform class into a validataclass
        return validataclass(_cls, **kwargs)

    # Allow decorator to be called with and without parenthesis
    return decorator if cls is None else decorator(cls)


def _prepare_search_query_dataclass(cls) -> None:
    """
    Internal helper function used by @search_query_dataclass to prepare validataclass fields in a soon-to-be dataclass.
    """
    # In case of a subclassed dataclass, get the already existing fields
    existing_fields = _get_existing_validator_fields(cls)

    # Get annotations of this class (ignores base classes)
    cls_annotations = get_annotations(cls)

    # Prepare dataclass fields by checking for validators and setting metadata accordingly
    for name, field_type in cls_annotations.items():
        value = getattr(cls, name, None)

        # Skip field if it is already a dataclass Field object (created by field() or validataclass_field())
        if isinstance(value, dataclasses.Field):
            continue

        # Get current validator etc. if the field is already existing
        existing_field = existing_fields.get(name, _ValidatorField())

        # Parse field tuple
        try:
            parsed_field = _parse_validator_tuple(value)
        except Exception as e:
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": {e}')

        # Overwrite existing field arguments with validator etc. from tuple
        field = _ValidatorField(
            validator=parsed_field.validator or existing_field.validator,
            default=parsed_field.default or existing_field.default,
            search_param=parsed_field.search_param or existing_field.search_param,
        )

        # Ignore all fields without a SearchParam (they will be handled by @validataclass as usual validataclass fields)
        if field.search_param is None:
            continue

        # Ensure that a validator is set
        if not isinstance(field.validator, Validator):
            raise DataclassValidatorFieldException(f'Dataclass field "{name}" must specify a validator.')

        # For SearchParam fields, use Default(None) if no explicit default was set
        if field.default is None:
            field.default = Default(None)

        # Create validataclass field
        setattr(cls, name, validataclass_field(
            validator=field.validator,
            default=field.default,
            metadata={'search_param': field.search_param},
        ))


def _get_existing_validator_fields(cls) -> dict[str, _ValidatorField]:
    """
    Returns a dictionary containing all fields (as `_ValidatorField` objects) of an existing validataclass that have a
    validator set in their metadata, or an empty dictionary if the class is not a dataclass (yet).

    Existing dataclass fields are determined by looking at all direct parent classes that are dataclasses themselves.
    If two unrelated base classes define a field with the same name, the most-left class takes precedence (for example,
    in `class C(B, A)`, the definitions of B take precendence over A).

    (Internal helper function.)
    """
    existing_fields = {}

    for base_cls in reversed(cls.__bases__):
        if not dataclasses.is_dataclass(base_cls):
            continue

        for field in dataclasses.fields(base_cls):
            existing_fields[field.name] = _ValidatorField(
                validator=field.metadata.get('validator', None),
                default=field.metadata.get('validator_default', None),
                search_param=field.metadata.get('search_param', None),
            )

    return existing_fields


def _parse_validator_tuple(args: Any) -> _ValidatorField:
    """
    Parses field arguments (the value of a field in a dataclass that has not been parsed by `@dataclass` yet) to a
    `_ValidatorField` object.

    (Internal helper function.)
    """
    if args is None:
        return _ValidatorField()

    # Ensure args is a tuple
    if not isinstance(args, tuple):
        args = (args,)

    # Find validator, default object and search param in tuple and return them as a dictionary
    field = _ValidatorField()

    for arg in args:
        if isinstance(arg, Validator):
            if field.validator is not None:
                raise ValueError('Only one validator can be specified.')
            field.validator = arg
        elif isinstance(arg, BaseDefault):
            if field.default is not None:
                raise ValueError('Only one default can be specified.')
            field.default = arg
        elif isinstance(arg, SearchParam):
            if field.search_param is not None:
                raise ValueError('Only one SearchParam can be specified.')
            field.search_param = arg
        else:
            raise TypeError('Unexpected type of argument: ' + type(arg).__name__)

    return field
