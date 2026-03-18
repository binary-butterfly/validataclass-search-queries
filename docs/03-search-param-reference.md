# 3. Reference of search filter types

This is a reference of all different search filter types, i.e. `SearchParam` classes.


## Base class

The base class of all search filters is `SearchParam`.

This class is abstract, so you cannot use it directly. However, in case you need a special search filter that is not
part of this library, you can build your own class by inheriting from `SearchParam` and implementing the abstract
method `sqlalchemy_filter()`.

Take a look at one of the many existing filter classes for how to do that, most of them are pretty simple.


## General filters

### SearchParamEquals

The `SearchParamEquals` filter is a simple "is equal to" filter for matching exact values of any type.

**Note:** For string fields, it may depend on your database collation whether the match is case-sensitive or not.

**Example:**

```
# This results in the filter `Model.column == param`
# (In SQL this would render as `column = {param}` or `column IS {param}` depending on the type)
param: Any = SearchParamEquals('column'), any_validator
```


## Substring filters

There are multiple filters for **substring matching**.

The `SearchParamContains` filter implements a partial string match, i.e. the column must be a string that contains the
parameter value. This is implemented using a `column LIKE "%{value}%"` SQL expression.

The `SearchParamStartsWith` filter implements a prefix search, i.e. the column must be a string that starts with the
parameter value. This is implemented using a `column LIKE "%{value}"` SQL expression.

The `SearchParamEndsWith` filter implements a suffix search, i.e. the column must be a string that ends with the
parameter value. This is implemented using a `column LIKE "{value}%"` SQL expression.

All of these filters work with an SQL `LIKE` expression. The values are automatically escaped, so that the characters
`%` and `_` are interpreted as the literal characters, not as wildcard characters.

**Examples:**

```
# (Assuming that the parameters are set to the string "example")

# Results in: `name LIKE "%example%"`
name_contains: str | None = SearchParamContains('name'), StringValidator()

# Results in: `name LIKE "%example"`
name_prefix: str | None = SearchParamStartsWith('name'), StringValidator()

# Results in: `name LIKE "example%"`
name_suffix: str | None = SearchParamEndsWith('name'), StringValidator()
```


## Boolean filters

The following filters are all used for **boolean** parameters, meaning that the user can set them to either `true` or
`false` (or omit them, in which case no filter will be applied at all).

You should use a `BooleanValidator(allow_strings=True)` for these filters. Other values than `True` and `False` can be
used as well, which will be interpreted as boolean using `bool(value)`, but it is recommended to stick to real booleans.


### SearchParamBoolean

The `SearchParamBoolean` filter is the most trivial one. It is equivalent to a `SearchParamEquals` that only allows
boolean values (or rather, that interprets all values as booleans).

- If the parameter is set to `true`, the resulting SQL expression will be `column IS TRUE`.
- If the parameter is set to `false`, the resulting SQL expression will be `column IS FALSE`.

**Example:**

```
# Results in: `completed IS TRUE` or `completed IS FALSE`, depending on the value
completed: bool | None = SearchParamBoolean(), BooleanValidator(allow_strings=True)
```


### SearchParamIsNone and SearchParamIsNotNone

The `SearchParamIsNone` and `SearchParamIsNotNone` filters both check if the column is `NULL` or anything else.
They are almost identical, except that one of them is inverted.

For `SearchParamIsNone`:

- If the parameter is set to `true`, the resulting SQL expression will be `column IS NULL`.
- If the parameter is set to `false`, the resulting SQL expression will be `column IS NOT NULL`.

For `SearchParamIsNotNone`:

- If the parameter is set to `true`, the resulting SQL expression will be `column IS NOT NULL`.
- If the parameter is set to `false`, the resulting SQL expression will be `column IS NULL`.

**Examples:**

```
# Results in: `price IS NULL` (if free=true) or `price IS NOT NULL` (if free=false)
free: bool | None = SearchParamIsNone('price'), BooleanValidator(allow_strings=True)

# Results in: `completed_at IS NOT NULL` (if completed=true) or `completed_at IS NULL` (if completed=false)
completed: bool | None = SearchParamIsNotNone('completed_at'), BooleanValidator(allow_strings=True)
```


### SearchParamTernary

The `SearchParamTernary` filter is comparable to the "ternary operator" found in many programming languages (e.g.
`value1 if condition else value2` in Python, or `condition ? value1 : value2` in other languages).

When defining the parameter, you need to specify two values. One value is used if the parameter is `True`, the other
is used if the parameter is `False`. The resulting filter will then be an "equals" filter using the column and that
value.

For `SearchParamTernary('value1', 'value2')`:

- If the parameter is set to `true`, the resulting SQL expression will be `column = "value1"`.
- If the parameter is set to `false`, the resulting SQL expression will be `column = "value2"`.

**Example:**

In this example, there is a database column called `visibility`, which has a string value that is either `"public"` or
`"hidden"`.

Instead of a string equals filter, we want a boolean parameter `is_public` though.

```
# Results in: `visibility = "public"` (if true) or `visibility = "hidden"` (if false)
# (Note that the column name needs to be specified as a keyword argument in this case.)
is_public: bool | None = SearchParamTernary('public', 'hidden', column_name='visibility'), \
    BooleanValidator(allow_strings=True)
```


## Comparison filters

Of course, there are also filters to compare values with "greater than", "less than", and so on.

- `SearchParamGreaterThan` for the expression `column > {value}`.
- `SearchParamGreaterOrEqual` for the expression `column >= {value}`.
- `SearchParamLessThan` for the expression `column < {value}`.
- `SearchParamLessOrEqual` for the expression `column <= {value}`.

These filters are pretty self-explanatory. They work with anything that can be compared using these operators, including
numbers and datetimes.

There are also two more search filters which are supposed to be used with datetimes. However, these are really just
aliases for the filters above:

- `SearchParamSince` is an alias for `SearchParamGreaterOrEqual`, i.e. `column >= {value}`.
- `SearchParamUntil` is an alias for `SearchParamLessOrEqual`, i.e. `column <= {value}`.

**Examples:**

```
# Results in: `price > {price_above}`
price_above: Decimal | None = SearchParamGreaterThan('price'), DecimalValidator()

# Results in: `price < {price_below}`
price_below: Decimal | None = SearchParamLessThan('price'), DecimalValidator()

# Results in: `price >= {price_from}`
price_from: Decimal | None = SearchParamGreaterOrEqual('price'), DecimalValidator()

# Results in: `price <= {price_to}`
price_to: Decimal | None = SearchParamLessOrEqual('price'), DecimalValidator()

# Results in: `modified >= {modified_since}` (same as SearchParamGreaterOrEqual)
modified_since: datetime | None = SearchParamSince('modified'), DateTimeValidator()

# Results in: `modified <= {modified_until}` (same as SearchParamLessOrEqual)
modified_until: datetime | None = SearchParamUntil('modified'), DateTimeValidator()
```


## Multi-select filters

### SearchParamMultiSelect

The `SearchParamMultiSelect` filter implements a "multi-select filter". As the name suggests, with this filter a user
can select **one or multiple** values to search for instead of just a single value. The query will then return all
results where the column is equal to one of the given values.

This is implemented using a `column IN (values...)` SQL expression.

For this filter, the parameter should be set to a **list of values**. However, the filter is implemented in a way that
also allows scalar values (which will be interpreted as a list that only consists of this one value, effectively
resulting in an "equals" filter with this value).

Since HTTP GET parameters are always strings, you cannot use a regular `ListValidator`, though. The library provides a
special validator for this instead: The `MultiSelectValidator`.


### MultiSelectValidator

The `MultiSelectValidator` is an extended `ListValidator` that first parses an input string as a **comma-separated**
list of values to an actual list of strings, and then validates every list item with a specified item validator.

For example, `MultiSelectValidator(IntegerValidator(allow_strings=True))` would give you a validator that accepts an
input string like `"1,2,3"` and returns a list of integers like `[1, 2, 3]`.

By default, `,` is used as the delimiter. If you need to change this, you can set the option `delimiter` to a different
string. Also, you can optionally set a maximum list length with `max_length`.


#### Variations

As a shortcut, there are some more multi-select validators that might be commonly used:

The `MultiSelectIntegerValidator` is a `MultiSelectValidator` that uses an `IntegerValidator` (with `allow_strings=True`
already set) for item validation. You can optionally set the `min_value` and `max_value` options which get passed to
the `IntegerValidator`.

The `MultiSelectAnyOfValidator` uses an `AnyOfValidator` for item validation. This validator only allows values from a
predefined list (specified in the validator). For example, a `MultiSelectAnyOfValidator(['foo', 'bar', 'baz'])` would
validate an input string like `"foo,baz"` and return the list `['foo', 'baz']`, but raise an error for values not part
of the list.

The `MultiSelectEnumValidator` uses an `EnumValidator` for item validation. Similar to the previous validator, this one
only allows values from an enum class. It doesn't return a list of strings though, but converts the strings to the
corresponding enum members.

If you need a multi-select validator that uses an enum class for validation, but still returns lists of regular strings,
you can define your validator like this: `MultiSelectAnyOfValidator([i.value for i in ExampleEnum])`.


### Examples

Here are some examples for how to define multi-select filters using the aforementioned validators.

(Keep in mind to use type annotations for (optional) lists instead of scalar types.)

```
# Accepts a comma-separated list of positive integers like "2,4,6"
# Results in a filter like `customer_id IN (2, 4, 6)`
customer_id: list[int] | None = SearchParamMultiSelect(), MultiSelectIntegerValidator(min_value=1)

# Accepts a comma-separated list of strings (but only those defined in the validator), e.g. "active,pending"
# Results in a filter like `status IN ("active", "pending")`
status: list[str] | None = SearchParamMultiSelect(), MultiSelectAnyOfValidator(['active', 'inactive', 'pending'])
```


## Special filters

### SearchParamCustom

If you need a custom filter that is not covered by all these built-in filters, you basically have two options. The best
way is to implement your own filter by subclassing `SearchParam` and implementing the `sqlalchemy_filter` method to
return an appropriate SQLAlchemy filter expression.

However, in some cases this isn't possible or would be unnecessarily complicated, for example if the filter is very
specific to one model (so that a custom `SearchParam` class wouldn't be reusable anywhere else anyway) and/or applies
a complex filter on multiple fields of that model.

In those cases it's often a better option to implement your custom filter directly in the repository by overriding the
`_apply_bound_search_filter` or `_filter_by_search_query` methods from the repository mixin. This would essentially
bypass the `SearchParam.sqlalchemy_filter` implementation completely.

For those parameters, it is recommended to define it using the `SearchParamCustom` class. This filter simply raises a
`NotImplementedError` exception when its `sqlalchemy_filter` method is called, which ensures that the filter is never
used without your custom implementation in the repository.

**Example:**

```
# This search parameter only works if the repository handles it manually
param: Any = SearchParamCustom(), any_validator
```
