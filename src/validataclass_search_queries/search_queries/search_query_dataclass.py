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

from ..filters import SearchParam

__all__ = [
    'search_query_dataclass',
]

_T = TypeVar('_T')


# TODO: The special @search_query_dataclass decorator might become obsolete and replaced with the regular @validataclass
#  decorator when custom field options are implemented in validataclass.

@overload
def search_query_dataclass(cls: type[_T]) -> type[_T]:
    ...


@overload
def search_query_dataclass(cls: None = None, /, **kwargs) -> Callable[[type[_T]], type[_T]]:
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
        _prepare_search_query_dataclass(_cls)
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
        field_args = existing_fields.get(name, {})

        # Overwrite existing field arguments with validator etc. from tuple
        try:
            field_args.update(_parse_validator_tuple(value))
        except Exception as e:
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": {e}')

        # Ignore all fields without a SearchParam (they will be handled by @validataclass as usual validataclass fields)
        if 'search_param' not in field_args.keys():
            continue

        # Ensure that a validator is set
        if not isinstance(field_args.get('validator', None), Validator):
            raise DataclassValidatorFieldException(f'Dataclass field "{name}" must specify a validator.')

        # For SearchParam fields, use Default(None) if no explicit default was set
        if field_args.get('default', None) is None:
            field_args['default'] = Default(None)

        # Create validataclass field
        setattr(cls, name, validataclass_field(
            validator=field_args.get('validator'),
            default=field_args.get('default'),
            metadata={'search_param': field_args.get('search_param')},
        ))


def _get_existing_validator_fields(cls) -> dict[str, dict[str, Any]]:
    """
    Internal helper function used by @search_query_dataclass to get all pre-existing validataclass fields from the base classes.
    """
    existing_fields = {}

    for base_cls in reversed(cls.__bases__):
        if not dataclasses.is_dataclass(base_cls):
            continue

        for field in dataclasses.fields(base_cls):
            existing_fields[field.name] = {
                'validator': field.metadata.get('validator', None),
                'default': field.metadata.get('validator_default', None),
                'search_param': field.metadata.get('search_param', None),
            }

    return existing_fields


def _parse_validator_tuple(args: Any) -> dict:
    """
    Internal helper function used by @search_query_dataclass to parse validataclass-style field tuples to dictionaries.
    """
    if args is None:
        return {}

    # Ensure args is a tuple
    if not isinstance(args, tuple):
        args = (args,)

    # Find validator, default object and search param in tuple and return them as a dictionary
    arg_dict = {}

    for arg in args:
        if isinstance(arg, Validator):
            if 'validator' in arg_dict:
                raise ValueError('Only one validator can be specified.')
            arg_dict['validator'] = arg
        elif isinstance(arg, BaseDefault):
            if 'default' in arg_dict:
                raise ValueError('Only one default can be specified.')
            arg_dict['default'] = arg
        elif isinstance(arg, SearchParam):
            if 'search_param' in arg_dict:
                raise ValueError('Only one SearchParam can be specified.')
            arg_dict['search_param'] = arg
        else:
            raise TypeError('Unexpected type of argument: ' + type(arg).__name__)

    return arg_dict
