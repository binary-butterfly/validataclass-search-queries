"""
validataclass-search-queries
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
from dataclasses import FrozenInstanceError

import pytest
from validataclass.dataclasses import Default, DefaultUnset, NoDefault, validataclass_field
from validataclass.exceptions import DataclassValidatorFieldException
from validataclass.helpers import UnsetValue, UnsetValueType
from validataclass.validators import BooleanValidator, IntegerValidator, RejectValidator, StringValidator

from tests.unit.search_queries._helpers import assert_field_default, assert_field_no_default, get_dataclass_fields
from validataclass_search_queries.filters import (
    SearchParamEquals,
    SearchParamGreaterThan,
    SearchParamLessThan,
    SearchParamTernary,
    SearchParamMultiSelect,
)
from validataclass_search_queries.search_queries import search_query_dataclass
from validataclass_search_queries.validators import MultiSelectIntegerValidator


def test_search_query_dataclass_with_empty_class():
    """ Create an empty search query dataclass. """

    @search_query_dataclass
    class EmptySearchQuery:
        pass

    assert len(get_dataclass_fields(EmptySearchQuery)) == 0


def test_search_query_dataclass_without_kwargs():
    """ Create a search query dataclass without additional arguments and check that fields are created correctly. """

    @search_query_dataclass
    class UnitTestSearchQuery:
        # Regular validataclass field (no default expected)
        regular_required: str = StringValidator()

        # Regular validataclass field with default
        regular_optional: str | None = StringValidator(), Default(None)

        # Field created explicitly via validataclass_field()
        explicit_field: str = validataclass_field(StringValidator(), default=Default('meow'))

        # Search parameter without explicit default (default None expected)
        filter1: int | None = SearchParamEquals('field'), IntegerValidator(allow_strings=True)

        # Search parameter with explicit default
        filter2: int = SearchParamGreaterThan(), IntegerValidator(allow_strings=True), Default(42)

        # Search parameter that explicitly has no default
        filter3: int = SearchParamLessThan(), IntegerValidator(allow_strings=True), NoDefault

        # Special search parameters
        filter4: list[int] | None = SearchParamMultiSelect(), MultiSelectIntegerValidator(min_value=0, max_value=10)
        filter5: bool | None = SearchParamTernary('visible', 'hidden'), BooleanValidator(allow_strings=True)

    # Check that @search_query_dataclass actually created a dataclass (i.e. @dataclass was used on the class)
    assert dataclasses.is_dataclass(UnitTestSearchQuery)

    # Get fields from dataclass
    fields = get_dataclass_fields(UnitTestSearchQuery)

    # Check names and types of all fields
    assert list(fields.keys()) == [
        'regular_required',
        'regular_optional',
        'explicit_field',
        'filter1',
        'filter2',
        'filter3',
        'filter4',
        'filter5',
    ]
    assert fields['regular_required'].type == str
    assert fields['regular_optional'].type == str | None
    assert fields['explicit_field'].type == str
    assert fields['filter1'].type == int | None
    assert fields['filter2'].type == int
    assert fields['filter3'].type == int
    assert fields['filter4'].type == list[int] | None
    assert fields['filter5'].type == bool | None

    # Check field defaults
    assert_field_no_default(fields['regular_required'])
    assert_field_default(fields['regular_optional'], default_value=None)
    assert_field_default(fields['explicit_field'], default_value='meow')
    assert_field_default(fields['filter1'], default_value=None)
    assert_field_default(fields['filter2'], default_value=42)
    assert_field_no_default(fields['filter3'])
    assert_field_default(fields['filter4'], default_value=None)
    assert_field_default(fields['filter5'], default_value=None)

    # Check that fields have correct validators
    assert type(fields['regular_required'].metadata.get('validator')) is StringValidator
    assert type(fields['regular_optional'].metadata.get('validator')) is StringValidator
    assert type(fields['explicit_field'].metadata.get('validator')) is StringValidator
    assert type(fields['filter1'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter2'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter3'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter4'].metadata.get('validator')) is MultiSelectIntegerValidator
    assert type(fields['filter5'].metadata.get('validator')) is BooleanValidator

    # Check that fields have correct SearchParams
    assert fields['regular_required'].metadata.get('search_param') is None
    assert fields['regular_optional'].metadata.get('search_param') is None
    assert fields['explicit_field'].metadata.get('search_param') is None
    assert type(fields['filter1'].metadata.get('search_param')) is SearchParamEquals
    assert type(fields['filter2'].metadata.get('search_param')) is SearchParamGreaterThan
    assert type(fields['filter3'].metadata.get('search_param')) is SearchParamLessThan
    assert type(fields['filter4'].metadata.get('search_param')) is SearchParamMultiSelect
    filter5_search_param = fields['filter5'].metadata.get('search_param')
    assert type(filter5_search_param) is SearchParamTernary
    assert filter5_search_param.value_true == 'visible'
    assert filter5_search_param.value_false == 'hidden'


def test_search_query_dataclass_with_kwargs():
    """ Create a search query dataclass with additional arguments and check that they are passed to @dataclass. """

    # As an example, create two dataclasses, one without any arguments and one with frozen=True.
    # Writing to an object of the frozen dataclass should raise an exception.

    @search_query_dataclass()
    class NormalSearchQuery:
        foo: int | None = SearchParamEquals(), IntegerValidator()

    @search_query_dataclass(frozen=True)
    class FrozenSearchQuery:
        foo: int | None = SearchParamEquals(), IntegerValidator()

    # NormalSearchQuery is not frozen, writing is allowed
    normal = NormalSearchQuery(foo=42)
    assert normal.foo == 42
    normal.foo = 13
    assert normal.foo == 13

    # FrozenSearchQuery is frozen, writing should raise an exception!
    frozen = FrozenSearchQuery(foo=42)
    assert frozen.foo == 42
    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'foo'"):
        frozen.foo = 13  # type: ignore[misc]


def test_search_query_dataclass_create_objects_valid():
    """ Create a search query dataclass and instantiate objects from it. """

    @search_query_dataclass
    class UnitTestSearchQuery:
        # Regular required/optional validataclass fields
        regular_required: str = StringValidator()
        regular_optional: str | None = StringValidator(), Default(None)

        # Search filters with/without explicit default
        filter1: int | None = SearchParamEquals('field'), IntegerValidator(allow_strings=True)
        filter2: int = SearchParamGreaterThan(), IntegerValidator(allow_strings=True), Default(42)

    # Create an instance where all fields are specified explicitly
    instance1 = UnitTestSearchQuery(
        regular_required='banana',
        regular_optional='apple',
        filter1=42,
        filter2=1312,
    )
    assert instance1.regular_required == 'banana'
    assert instance1.regular_optional == 'apple'
    assert instance1.filter1 == 42
    assert instance1.filter2 == 1312

    # Create an instance with default values
    instance2 = UnitTestSearchQuery(
        regular_required='banana',
    )
    assert instance2.regular_required == 'banana'
    assert instance2.regular_optional is None
    assert instance2.filter1 is None
    assert instance2.filter2 == 42


def test_search_query_dataclass_create_objects_invalid():
    """ Create a search query dataclass and try to instantiate objects from it, but missing a required values. """

    @search_query_dataclass
    class UnitTestSearchQuery:
        # Regular required/optional validataclass fields
        regular_required: str = StringValidator()
        regular_optional: str | None = StringValidator(), Default(None)

        # Search filters with/without explicit default
        filter1: int | None = SearchParamEquals('field'), IntegerValidator(allow_strings=True)
        filter2: int = SearchParamGreaterThan(), IntegerValidator(allow_strings=True), Default(42)

    # Try to instantiate without the required field
    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'regular_required'"):
        UnitTestSearchQuery()

    # Try to instantiate with some fields, but missing the required field
    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'regular_required'"):
        UnitTestSearchQuery(
            regular_optional='apple',
            filter1=42,
            filter2=1312,
        )


# Subclassing / inheritance

def test_search_query_dataclass_subclassing():
    """ Create a subclass of a search query dataclass and check that fields are inherited and overridden correctly. """

    @search_query_dataclass
    class BaseClass:
        # Regular fields
        regular_required1: str = StringValidator()
        regular_required2: str = StringValidator()
        regular_optional1: str = StringValidator(), Default('')
        regular_optional2: str = StringValidator(), Default('')
        regular_to_filter: str = StringValidator()

        # Search parameters
        filter1: int | None = SearchParamEquals(), IntegerValidator(allow_strings=True)
        filter2: int = SearchParamEquals(), IntegerValidator(allow_strings=True), Default(42)
        filter3: int | None = SearchParamEquals(), IntegerValidator(allow_strings=True)
        filter4: int | None = SearchParamEquals(), IntegerValidator(allow_strings=True), Default(None)
        filter5: int = SearchParamEquals(), IntegerValidator(allow_strings=True), NoDefault

    @search_query_dataclass
    class SubClass(BaseClass):
        # Skipped fields must be still present and unchanged in subclass
        # regular_required1: Unchanged
        # regular_optional1: Unchanged
        # filter1: Unchanged
        # filter2: Unchanged

        # Changing defaults or validators in regular fields
        regular_required2: UnsetValueType = RejectValidator(), DefaultUnset
        regular_optional2: str = NoDefault

        # Changing a regular field to a search parameter
        regular_to_filter: str | None = SearchParamEquals()

        # Changing defaults or validators in search parameter fields
        filter3: int = NoDefault
        filter4: int = Default(42)
        filter5: None = RejectValidator(), Default(None)

    # Check that @search_query_dataclass actually created a dataclass (i.e. @dataclass was used on the class)
    assert dataclasses.is_dataclass(SubClass)

    # Get fields from dataclass
    fields = get_dataclass_fields(SubClass)

    # Check names and types of all fields
    assert list(fields.keys()) == [
        'regular_required1',
        'regular_required2',
        'regular_optional1',
        'regular_optional2',
        'regular_to_filter',
        'filter1',
        'filter2',
        'filter3',
        'filter4',
        'filter5',
    ]
    assert fields['regular_required1'].type == str
    assert fields['regular_required2'].type == UnsetValueType
    assert fields['regular_optional1'].type == str
    assert fields['regular_optional2'].type == str
    assert fields['regular_to_filter'].type == str | None
    assert fields['filter1'].type == int | None
    assert fields['filter2'].type == int
    assert fields['filter3'].type == int
    assert fields['filter4'].type == int
    assert fields['filter5'].type is None

    # Check field defaults
    assert_field_no_default(fields['regular_required1'])
    assert_field_default(fields['regular_required2'], default_value=UnsetValue)
    assert_field_default(fields['regular_optional1'], default_value='')
    assert_field_no_default(fields['regular_optional2'])
    assert_field_default(fields['regular_to_filter'], default_value=None)
    assert_field_default(fields['filter1'], default_value=None)
    assert_field_default(fields['filter2'], default_value=42)
    assert_field_no_default(fields['filter3'])
    assert_field_default(fields['filter4'], default_value=42)
    assert_field_default(fields['filter5'], default_value=None)

    # Check that fields have correct validators
    assert type(fields['regular_required1'].metadata.get('validator')) is StringValidator
    assert type(fields['regular_required2'].metadata.get('validator')) is RejectValidator
    assert type(fields['regular_optional1'].metadata.get('validator')) is StringValidator
    assert type(fields['regular_optional2'].metadata.get('validator')) is StringValidator
    assert type(fields['regular_to_filter'].metadata.get('validator')) is StringValidator
    assert type(fields['filter1'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter2'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter3'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter4'].metadata.get('validator')) is IntegerValidator
    assert type(fields['filter5'].metadata.get('validator')) is RejectValidator

    # Check that fields have correct SearchParams
    assert fields['regular_required1'].metadata.get('search_param') is None
    assert fields['regular_required2'].metadata.get('search_param') is None
    assert fields['regular_optional1'].metadata.get('search_param') is None
    assert fields['regular_optional2'].metadata.get('search_param') is None
    assert type(fields['regular_to_filter'].metadata.get('search_param')) is SearchParamEquals
    assert type(fields['filter1'].metadata.get('search_param')) is SearchParamEquals
    assert type(fields['filter2'].metadata.get('search_param')) is SearchParamEquals
    assert type(fields['filter3'].metadata.get('search_param')) is SearchParamEquals
    assert type(fields['filter4'].metadata.get('search_param')) is SearchParamEquals
    assert type(fields['filter5'].metadata.get('search_param')) is SearchParamEquals


# Error cases

def test_search_query_dataclass_with_invalid_values():
    """
    Test that @search_query_dataclass raises exceptions if a field is not already defined (e.g. with field()) and has
    no Validator.
    """

    with pytest.raises(DataclassValidatorFieldException) as exception_info:
        @search_query_dataclass
        class InvalidSearchQueryDataclass:
            foo: int  # type: ignore[validataclass]

    assert str(exception_info.value) == 'Dataclass field "foo" must specify a validator.'


@pytest.mark.parametrize(
    'field_tuple, expected_exception_msg',
    [
        # Missing validator
        (None, 'Dataclass field "foo" must specify a validator.'),
        ((Default(3)), 'Dataclass field "foo" must specify a validator.'),
        ((SearchParamEquals(), Default(0)), 'Dataclass field "foo" must specify a validator.'),

        # Too many validators
        (
            (IntegerValidator(), StringValidator()),
            'Dataclass field "foo": Only one validator can be specified.',
        ),
        (
            (SearchParamEquals(), IntegerValidator(), IntegerValidator()),
            'Dataclass field "foo": Only one validator can be specified.',
        ),

        # Too many defaults
        (
            (Default(1), IntegerValidator(), Default(2)),
            'Dataclass field "foo": Only one default can be specified.',
        ),
        (
            (Default(1), SearchParamEquals(), IntegerValidator(), Default(2)),
            'Dataclass field "foo": Only one default can be specified.',
        ),

        # Too many SearchParams
        (
            (SearchParamEquals(), IntegerValidator(), SearchParamLessThan()),
            'Dataclass field "foo": Only one SearchParam can be specified.',
        ),

        # Unexpected type in tuple
        ((IntegerValidator(), 42), 'Dataclass field "foo": Unexpected type of argument: int'),
        ((SearchParamEquals(), IntegerValidator(), 42), 'Dataclass field "foo": Unexpected type of argument: int'),
    ],
)
def test_search_query_dataclass_with_invalid_field_tuples(field_tuple, expected_exception_msg):
    """ Test that @search_query_dataclass raises exceptions for various invalid tuples. """
    with pytest.raises(DataclassValidatorFieldException) as exception_info:
        @search_query_dataclass
        class InvalidSearchQueryDataclass:
            foo: int = field_tuple  # type: ignore[validataclass]

    assert str(exception_info.value) == expected_exception_msg
