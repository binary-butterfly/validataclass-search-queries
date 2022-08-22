# 1. Defining search query dataclasses

This is a quick tutorial on how to use this library.

There are basically four parts to it:

1. Defining search query dataclasses (including filters, pagination and sorting).
2. Validating input search queries from GET parameters.
3. Using search queries to filter, sort and paginate SQL queries.
4. Generating API responses with the search results.

This chapter is only about the first part, as it is the most complex one. All other parts are covered in
[the next chapter](02-using-search-queries.md).


## Base definition

Search query dataclasses are an extended version of validataclasses. They can be defined and used like regular
validataclasses, but have some extra functionality.

Their purpose is to define parameters that are used to **filter** results (usually from an SQL database), to **sort**
the results in a specified way, and to **paginate** the results.

To define a search query dataclass, you need to use the special decorator `@search_query_dataclass` instead of the usual
`@validataclass` decorator. You also need to specify `BaseSearchQuery` as the base class of your dataclass. (Using the
`ValidataclassMixin` class is not necessary and not recommended.)

```python
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery

@search_query_dataclass
class ExampleSearchQuery(BaseSearchQuery):
    pass
```

In this dataclass you can now define search parameters for **filtering** results. These parameters are defined like
validataclass fields, but with a special option that marks them as search parameters. To use **pagination** and/or
**sorting**, there are special mixin classes that need to be included in your dataclass. (More about this in a moment.)


## Search filters

A search filter can be used to filter results from the database in the same way that you would do manually (e.g. using
`query.filter(FooModel.name == 'Foobar')` in SQLAlchemy), but in a more generic way and with user input.

These search parameters are defined using so called `SearchParam` objects. There are multiple types of filters, each of
which is a subclass of `SearchParam`. For example, there is an "equals" filter (`SearchParamEquals`), substring filters
(e.g. `SearchParamContains` and `SearchParamStartsWith`), greater/less filters, and a lot more. (See next page for a
[reference of all search filter types](03-search-param-reference.md).)


### Defining a search parameter

To define a search parameter in a search query dataclass, you need to specify a field with a `SearchParam` object and a
validator (as a tuple, similar to how you would define a field with a validator and a default in a validataclass):

```
example_field: Optional[str] = SearchParamEquals('example_column'), StringValidator()
```

This would define a search parameter with the name `example_field`, which is validated using a `StringValidator`, and
which will apply an "equals" filter on the database column `example_column` (i.e. "find all results where `example_column`
equals the value of the parameter `example_field`").

In most cases, the parameter name will be the same as the column name. In that case you can omit the column name, so
the following lines are equivalent:

```
name: Optional[str] = SearchParamEquals(), StringValidator()
name: Optional[str] = SearchParamEquals('name'), StringValidator()
```

You might have noticed something about this field definition: The field is defined as `Optional[str]`, but there is no
default specified. This is a small specialty of the `@search_query_dataclass` decorator: Unless a `Default` is specified
explicitly, every field with a `SearchParam` will automatically use `Default(None)` as the default.

This is just for practicality: In almost all cases search filters will be defined as optional. If a search parameter is
not set (i.e. `None`), the search filter will not be applied to the query. To avoid appending `Default(None)` to every
single line in your search query dataclass, this default value will be set automatically. If needed, you can override
this default value as usual, though.

(**Note:** This only applies to fields that are defined with a `SearchParam`. Regular validataclass fields will NOT
have any default value unless specified.)

(Internally, when defining a validataclass field with a `SearchParam` object, the `@search_query_dataclass` decorator
will just copy the `SearchParam` into the field's metadata (similarly how the validator and default values are saved in
other validataclasses). Apart from this extra bit of metadata (and the default `Default(None)`), the field will
practically be the same as a regular validataclass field.)


### Search parameter validation

One important thing to note about the validators is that, since search queries are validated from GET parameters, you
need to always use validators that accept strings as input.

For example, a plain `IntegerValidator()` will reject the input because GET parameters are always strings, not integers,
so you need to use `IntegerValidator(allow_strings=True)`. Similarly, to validate **booleans**, use a
`BooleanValidator(allow_strings=True)`.

Special validators provided by this library (like the `MultiSelectIntegerValidator` or `PaginationLimitValidator`) will
already allow strings, though.


### Example

Here is a full example of a search query dataclass:

```python
from datetime import datetime
from typing import Optional, List

from validataclass.validators import DateTimeValidator, IntegerValidator, StringValidator
from validataclass_search_queries.filters import SearchParamContains, SearchParamEquals, SearchParamSince, \
    SearchParamUntil, SearchParamMultiSelect
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery
from validataclass_search_queries.validators import MultiSelectAnyOfValidator

@search_query_dataclass
class ExampleSearchQuery(BaseSearchQuery):
    # Filter for a substring search on the "name" column
    name: Optional[str] = SearchParamContains(), StringValidator()

    # Filter for all results where "customer_id" has the specified value
    # (Note: For validation of integers, remember to set allow_strings=True.)
    customer_id: Optional[int] = SearchParamEquals(), IntegerValidator(allow_strings=True)

    # Two filters on the same column "created_at" to filter for all results created between created_since
    # and created_until. (Both fields can be used alone, too.)
    created_since: Optional[datetime] = SearchParamSince('created_at'), DateTimeValidator()
    created_until: Optional[datetime] = SearchParamUntil('created_at'), DateTimeValidator()

    # Multi-select field: Parameter can be set to a comma-separated list of multiple values. The query will
    # fetch all results where the specified column has one of the given values. A special validator is required
    # here to parse the comma-separated list of values.
    status: Optional[List[str]] = SearchParamMultiSelect(), MultiSelectAnyOfValidator(['active', 'inactive', 'pending'])
```


## Pagination

To enable pagination, you need to include one of the **pagination mixins** in the base classes of your search query
dataclass.

Currently, there are two pagination mixins which implement different types of pagination: The `OffsetPaginationMixin`
and the `CursorPaginationMixin`. (They both implement the abstract base class `AbstractPaginationMixin`.)


### Offset pagination

The `OffsetPaginationMixin` implements so called **offset pagination**. The mixin adds two parameters to your dataclass:
`limit` and `offset`. The `limit` parameter specifies how many results are on a single page, while `offset` is the start
parameter that is used to query the individual pages.

Offset pagination works with any kind of SQL query (e.g. it can be sorted in any way you want). You simply need to
append a `LIMIT {limit} OFFSET {offset}` to the query and repeat the same query with an increasing offset.

As an example, we choose `limit=10`. You always start with an offset of 0, so you query the first page of results using
`LIMIT 10 OFFSET 0`. This will give you the first 10 results. For the second page, you repeat the query with `OFFSET 10`,
which will skip the first 10 results and fetch the next 10 results. For the third page, you skip the first 20 results
(`OFFSET 20`) and fetch the next 10, and so on.

The advantage of offset pagination is that it's pretty simple and works with any kind of SQL query. The disadvantage
is that offset pagination is "instable". This means that results can shift between pages when there are changes between
fetching the individual pages. For example, if an entry on page one is deleted, all following entries will shift one
place to the front. The first entry of each following page will become the last entry on the previous page. If you now
fetch the next page, you will miss one entry.


### Cursor pagination

The `CursorPaginationMixin` implements so called **cursor pagination**. Contrary to offset pagination, this type of
pagination is "stable".

The mixin adds two parameters to your dataclass: `limit` and `start`. The `limit` parameter has the same meaning as in
offset pagination. Instead of an offset, the `start` parameter specifies the first (i.e. lowest) ID of objects that you
want to fetch.

With cursor pagination, your SQL query first is ordered by ID. Then you apply a filter to only fetch results starting
with the ID specified in the `start` parameter (`WHERE id >= {start}`), and limit the query with `LIMIT {limit}`. To
fetch the next page of results, you need to take a look at the results of the first page: Take the ID of the last entry,
increment it by 1, and repeat your query with this value as your new `start` parameter.

As an example, we again choose `limit=10`. Since IDs should never be negative, you can start with `start=0` and fetch
the first 10 results. The IDs of these results are counting up, but there might be gaps (because entries could have
been deleted). For example, the last result of the first page might have the ID 15. To get the second page of results,
you repeat the query, now with `start=16`, and get the next 10 results, and so on.

Since cursor pagination requires the results to be ordered by ID, you cannot combine cursor pagination with custom
sorting.

(**Note:** It is possible to use a different column than "id" as your cursor column, as long as this column is strictly
monotonically increasing. In case you need this, take a look at the in-code documentation of `CursorPaginationMixin`.)


### Usage

To use one of the pagination mixins, include it in the base classes of your dataclass:

```python
from validataclass_search_queries.pagination import CursorPaginationMixin
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery

@search_query_dataclass
class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
    # (Optionally define search filters here...)
    pass
```

The pagination parameters are already defined in the mixin, so you don't need to define them yourself.

The default value for `limit` (if the user doesn't specify the limit explicitly) is 20. The maximum value for `limit`
is set to 100.

To change these values, you can override the validator and/or default of the field in your class. The validator used
for `limit` is a `PaginationLimitValidator`, which is a specialized version of an `IntegerValidator`.

**Examples:**

```python
from typing import Optional

from validataclass.dataclasses import Default
from validataclass_search_queries.pagination import CursorPaginationMixin, PaginationLimitValidator
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery

@search_query_dataclass
class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
    # To change both the maximum limit (default: 100) and default limit (20), override both validator and default.
    # (You can also omit `max_value` to allow any positive value for limit.)
    limit: Optional[int] = PaginationLimitValidator(max_value=1000), Default(100)

    # Alternatively, you can also just override the default and leave the validator unchanged:
    limit: Optional[int] = Default(100)
```


### Optional pagination

By default, using one of the pagination mixins makes pagination **mandatory**. The user can specify the page limit, but
the value can only be a positive number and if omitted, the default limit is used, so results will always be paginated.

In some cases you might want pagination to be enabled, but optional, so the user chooses if the results should be
paginated. This can be achieved by allowing the `limit` parameter to be set to `None`.

For this, the `PaginationLimitValidator` has an option: If you set `optional=True`, the validator will allow `0` as an
input value, and return `None` in that case. The user can now set `limit=0` as a query parameter to disable pagination,
and thus get a full list of all results. (This would be considered "opt-out pagination").

You can also set the default limit to `None`, so that pagination is disabled by default and can be enabled by the user
using the `limit` parameter ("opt-in pagination").

**Examples:**

```python
from typing import Optional

from validataclass.dataclasses import Default
from validataclass_search_queries.pagination import CursorPaginationMixin, PaginationLimitValidator
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery

@search_query_dataclass
class ExampleSearchQuery(CursorPaginationMixin, BaseSearchQuery):
    # Opt-out pagination: Allow limit=0 to disable pagination, but by default, paginate with a limit of 20.
    limit: Optional[int] = PaginationLimitValidator(optional=True), Default(20)

    # Opt-in pagination: Don't paginate by default, but allow limit to be set (e.g. limit=20) to enable pagination.
    limit: Optional[int] = PaginationLimitValidator(optional=True), Default(None)
```


## Sorting

To enable sorting (i.e. let the user select which column the results should be ordered by), you need to include the
`SortingMixin` in the base classes of your search query dataclass.

This mixin adds two parameters to your dataclass: `sorted_by` and `sorting_direction`.

The `sorted_by` parameter determines the column which the results should be ordered by. It is validated using an
`AnyOfValidator` which by default only allows the value `id` (to sort the results by the "id" column).

The `sorting_direction` parameter determines whether the results should be ordered in ascending (`ASC`) or descending
(`DESC`) order. It is validated using the `SortingDirectionValidator`, which is basically just a case-insensitive
`EnumValidator` for the `SortingDirection`. By default, results will be sorted in ascending order.

You can change the list of allowed sorting keys, the default sorting key and the default sorting direction by overriding
the validator and/or defaults of these fields.

**Examples:**

```python
from validataclass.dataclasses import Default
from validataclass.validators import AnyOfValidator
from validataclass_search_queries.sorting import SortingMixin, SortingDirection
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery

@search_query_dataclass
class ExampleSearchQuery(SortingMixin, BaseSearchQuery):
    # Set allowed sorting keys and default sorting key
    sorted_by: str = AnyOfValidator(['id', 'created_at', 'name', 'total_value']), Default('name')

    # Set default sorting direction to descending (doesn't seem very useful in this example, though)
    sorting_direction: SortingDirection = Default(SortingDirection.DESC)
```


## Full example of a search query dataclass

You can of course combine search filters, pagination and sorting in a search query dataclass. The only exception here
is that sorting cannot be combined with cursor pagination (using `SortingMixin` and `CursorPaginationMixin` as base
classes will raise an exception at definition time).

There is nothing new here, just combine the classes from above. For completeness sake, here is a full example (using
offset pagination, so it can be combined with sorting) nevertheless:

```python
from typing import Optional

from validataclass.dataclasses import Default
from validataclass.validators import AnyOfValidator, IntegerValidator, StringValidator
from validataclass_search_queries.filters import SearchParamContains, SearchParamEquals
from validataclass_search_queries.pagination import OffsetPaginationMixin, PaginationLimitValidator
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery
from validataclass_search_queries.sorting import SortingMixin


@search_query_dataclass
class ExampleSearchQuery(SortingMixin, OffsetPaginationMixin, BaseSearchQuery):
    # Opt-in pagination
    limit: Optional[int] = PaginationLimitValidator(optional=True), Default(None)

    # Set allowed sorting keys and default sorting key
    sorted_by: str = AnyOfValidator(['id', 'created_at', 'name', 'total_value']), Default('name')

    # Search filters
    name: Optional[str] = SearchParamContains(), StringValidator()
    customer_id: Optional[int] = SearchParamEquals(), IntegerValidator(allow_strings=True)
    # (Other filters omitted)
```

If you have a lot of search query dataclasses in your application, it is recommended to define custom base classes and
mixins to avoid repetition.

For example, if all your search queries use sorting and offset pagination, you could define a custom base class like
this:

```python
from typing import Optional

from validataclass.dataclasses import Default
from validataclass_search_queries.pagination import OffsetPaginationMixin, PaginationLimitValidator
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery
from validataclass_search_queries.sorting import SortingMixin


@search_query_dataclass
class AppBaseSearchQuery(SortingMixin, OffsetPaginationMixin, BaseSearchQuery):
    # Set default pagination limits
    limit: Optional[int] = PaginationLimitValidator(max_value=1000), Default(50)


# Now define your actual search query dataclasses like this:
@search_query_dataclass
class ExampleSearchQuery(AppBaseSearchQuery):
    # Define your filters
    pass
```

In a similar way, you can define a custom mixin class for filters that you need in multiple places:

```python
from datetime import datetime
from typing import Optional

from validataclass.validators import DateTimeValidator
from validataclass_search_queries.filters import SearchParamSince, SearchParamUntil
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery


@search_query_dataclass
class CreatedModifiedMixin(BaseSearchQuery):
    # Define reusable filters
    created_since: Optional[datetime] = SearchParamSince('created_at'), DateTimeValidator()
    created_until: Optional[datetime] = SearchParamUntil('created_at'), DateTimeValidator()
```


---

We now have learned how to define a search query dataclass with filters, pagination and sorting.

Go to [the next chapter](02-using-search-queries.md) to learn how to validate an input search query using these
dataclasses, how to work with a search query, and how to generate API responses with the results.
