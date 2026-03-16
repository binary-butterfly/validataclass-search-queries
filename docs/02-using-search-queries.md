# 2. Using search query dataclasses

This chapter covers the following parts of how to use this library:

- Validating input search queries from GET parameters.
- Using search queries to filter, sort and paginate SQL queries.
- Generating API responses with the search results.


## Validating input search queries

Now that we have defined a search query dataclass, we can use it to validate input parameters and apply our filters and
pagination on SQL queries.

Search query dataclasses can be used entirely on their own without any user input validation. For example, you can
simply instantiate the dataclass in your code, set the parameters you need, and use it to filter and fetch your data
from the database.

In most cases, though, search queries will be parsed from user input (e.g. GET parameters) and validated using the
validators specified in the dataclass. There is not much difference to validation of request bodies using regular
validataclasses: You only need to get the GET query parameters as a dictionary and use a regular `DataclassValidator`
with your search query dataclass to validate it.

Here is a basic example that would work with Flask:

```python
from flask import request
from validataclass.validators import DataclassValidator

# Get query arguments from Flask request
query_args = dict(request.args)

# Create a DataclassValidator for your search query
search_query_validator = DataclassValidator(ExampleSearchQuery)

# Validate query arguments and get an instance of your search query dataclass
search_query = search_query_validator.validate(query_args)
```

You might want to write a helper function/method with proper error handling, but basically, that's it.


## Using search queries in a repository

To use a search query on an SQL query for actual filtering and paginating, there are some helper methods defined in
`BaseSearchQuery` (for applying filters) and the pagination and sorting mixins. Take a look at these classes for more
details.

As a more convenient way to working with search queries in repository classes (that is, classes that use the repository
design pattern to fetch data from your database), there is the `SearchQueryRepositoryMixin` which you can include in
your repository classes. This mixin provides a few helper methods that do all the filtering, sorting and paginating for
you.

For this to work, it is important that your repository is dedicated to a single model class. You can of course query
and work with other models in the repository if you need to, but the methods of the repository mixin will only work
on one model class that needs to be specified per repository.


### Including the mixin in your repository

To include the `SearchQueryRepositoryMixin` in your repository class, first add it as a base class to your repository.

It is recommended to specify the model class as a type parameter, for example `SearchQueryRepositoryMixin[ExampleModel]`.
This is not strictly necessary, but improves type hinting.

Additionally you need to set the attribute `model_cls` in your repository class to your model class. This is used to
access the SQLAlchemy column objects of your model. For example, set: `model_cls = ExampleModel` in your repository.

**Example:**

```python
from validataclass_search_queries.repositories import SearchQueryRepositoryMixin

class ExampleRepository(SearchQueryRepositoryMixin[ExampleModel]):
    # Set model class
    model_cls = ExampleModel
```


### Using the mixin to work with SQL queries

The repository mixin provides multiple methods to work with SQLAlchemy queries and search queries.

Here, `query` is assumed to be an SQLAlchemy query for the model class (e.g. from `db_session.query(ExampleModel)`),
and `search_query` is the instance of your search query dataclass.

First, to apply the **search filters** to your SQL query, use the method `_filter_by_search_query()`:

```
query = self._filter_by_search_query(query, search_query)
```

This will internally use another method (`_apply_bound_search_filter`) for every filter in your dataclass that has a
value, which again will apply a `query.filter(...)` on your query. The method returns a new query including the filters.

Second, to apply the **sorting** to your SQL query, use the method `_order_by_search_query()`, which will apply
`query.order_by(...)` to your query and, again, return a new query:

```
query = self._order_by_search_query(query, search_query)
```

Third (and last), to apply the **pagination**, use the method `_paginate_result()`. This method is very different from
the other methods, because it does **not** return a new query. Instead, this method not only applies the pagination
to the query, but also **executes** the query for you and returns the results:

```
results = self._paginate_result(query, search_query)
```

However, instead of a regular list, this method returns a `PaginatedResult` object. This is a special type of list which
not only contains the results of the query, but also an additional attribute `total_count` with the total number of
results from this query **before** it was paginated.

For example, if the database contains 123 objects that match your query (i.e. your search filters), `total_count` will
always be 123, even though the `PaginatedResult` only contains 20 results because of the pagination limit.

Apart from this extra attribute and some useful helper methods, a `PaginatedResult` behaves exactly like a regular list.
In fact, the class is a subclass of `list` (as in: regular Python lists), so you can use a `PaginatedResult` in (almost)
every place where a `list` is expected (except for when a strict type check like `if type(foo) is list` is performed,
which you should generally avoid - use `isinstance` instead).

So, let's combine all of the above methods and apply filters, sorting and pagination all at once:

```
query = self._filter_by_search_query(query, search_query)
query = self._order_by_search_query(query, search_query)
results = self._paginate_result(query, search_query)
```

All of these methods can be used safely regardless of whether the search query actually supports all of these features.
For example, if you only want pagination and don't have any filters defined, `_filter_by_search_query()` will leave the
query unmodified, as will `_order_by_search_query()`. Likewise, if you don't use pagination, `_paginate_result()` will
work fine, too. It will still return a `PaginatedResult`, but it will contain all results at once (you have a single
page with unlimited results, so to speak). There might not even be a search query at all (meaning it is `None`), and
everything will still work fine.

Because of this, it is recommended to define your fetch methods with an **optional** `search_query` parameter (like
`search_query: BaseSearchQuery | None = None`).

Last but not least, there is another repository method provided by the mixin: `_search_and_paginate()` is a shortcut
method that calls all of the other methods shown above, so it applies filters, sorting, pagination and returns a
`PaginatedResult`. In most cases, you can simply use this single "all-inclusive" method and be done.

Here is a full example for a repository class that makes use of search queries:

```python
from sqlalchemy.orm import Session
from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.repositories import SearchQueryRepositoryMixin
from validataclass_search_queries.search_queries import BaseSearchQuery

# (Imagine this is an SQLAlchemy model with actual columns like "id", "created_at", etc.)
class ExampleModel:
    pass

# Define repository with mixin
class ExampleRepository(SearchQueryRepositoryMixin[ExampleModel]):
    # Set model class
    model_cls = ExampleModel

    # This is a dependency-injected SQLAlchemy session
    session: Session

    def __init__(self, *, session: Session):
        self.session = session

    # Example for a fetch method that filters, sorts and paginates by search query
    def fetch_examples(self, *, search_query: BaseSearchQuery | None = None) -> PaginatedResult[ExampleModel]:
        # Create an SQLAlchemy query
        query = self.session.query(ExampleModel)

        # Apply search query, execute SQL query, return paginated results
        return self._search_and_paginate(query, search_query)


# Example usage
example_repository = ExampleRepository(session=...)
results = example_repository.fetch_examples(search_query=...)
print(results)
```


### Overriding the mixin methods for special cases

Sometimes you might have cases where the built-in methods of the repository mixin are not enough. For example, you might
have relationships between models and need a search filter that is not applied to the primary model class, but to a
related object (e.g. you have **customers**, which have one or more **addresses** in separate objects, and you want to
find all customers from a specific city, so you would `JOIN` the customers and addresses and filter `Address.city`
instead of `Customer.city`).

This kind of filter needs a bit of custom code, but the good thing is: The `SearchQueryRepositoryMixin` is designed
with these special cases in mind. You can override the methods provided by the mixin in your class (in this case,
you would need to override either `_filter_by_search_query` or `_apply_bound_search_filter`), extend these methods to
handle your special filter, and then continue using the methods like you would normally.

Here is an example how you could implement this:

```python
from sqlalchemy.orm import Session, Query
from validataclass.validators import StringValidator
from validataclass_search_queries.filters import SearchParamContains, BoundSearchFilter
from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.repositories import SearchQueryRepositoryMixin
from validataclass_search_queries.search_queries import search_query_dataclass, BaseSearchQuery

# Stubs for SQLAlchemy models (Customer needs a 1:n relationship "addresses" to Address)
class Customer: ...
class Address: ...

# Search query dataclass with filters
@search_query_dataclass
class CustomerSearchQuery(BaseSearchQuery):
    # Regular search filter on name (part of the customer)
    name: str | None = SearchParamContains(), StringValidator()

    # Search filter on the city (part of an address, not the customer)
    city: str | None = SearchParamContains(), StringValidator()


class CustomerRepository(SearchQueryRepositoryMixin[Customer]):
    # Set model class
    model_cls = Customer
    session: Session

    def __init__(self, *, session: Session):
        self.session = session

    def fetch_customers(self, *, search_query: BaseSearchQuery | None = None) -> PaginatedResult[Customer]:
        # Create a customer query, and join it with the addresses
        query = self.session.query(Customer).join(Customer.addresses)
        return self._search_and_paginate(query, search_query)

    def _apply_bound_search_filter(self, query: Query, bound_filter: BoundSearchFilter) -> Query:
        # Implement special handling for the "city" filter
        if bound_filter.column_name == 'city':
            return query.filter(bound_filter.get_sqlalchemy_filter(Address.city))

        # In all other cases, use the regular method
        return super()._apply_bound_search_filter(query, bound_filter)
```

For another slightly more complicated example, take a look at the in-code documentation of `SearchQueryRepositoryMixin`.
Also, you can take a look directly at the code of the mixin methods to understand how they work and how to override
them for other special features.


## Generating API responses

Now that we have filtered and paginated the results, there is only one thing left to do: Send the results back to the
user.

There is a convenient helper function called `paginated_api_response()` that takes a `PaginatedResult` (as returned by
the repository) and the original search query, and generates a dictionary suitable for an API response. Besides the
actual list of results, this dictionary contains some useful extra information: First, the field `total_count` with the
total number of unpaginated results for this query (which is why we're using a `PaginatedResult` instead of a regular
list). Second, if there is another page of results, the dictionary contains information on how to retrieve this next
page.

Before we go into detail about this function, let's first take a closer look at the `PaginatedResult` class.


### Working with PaginatedResults

As already explained above, `PaginatedResult` is a subclass of `list` that exactly behaves like a regular list, just
with an additional attribute `total_count`.

To encode your paginated result as JSON, you would first need to convert the items (which are objects of your database
model) to dictionaries. Since `PaginatedResult` basically is a list, you could simply iterate over it and construct
dictionaries from the items (for example using a `to_dict()` method that is defined in your model).

To help with that, `PaginatedResult` has a method called `map()` which takes a callable as argument, applies this
callable on every item, and returns a **new** `PaginatedResult` consisting of the return values of this callable.
In other words, `paginated_result.map(map_func)` is the equivalent of `[map_func(item) for item in paginated_result]`,
with the main difference that you get another `PaginatedResult` (with the same `total_count` as the original one)
instead of a regular list.

The `map()` method works with any callable that takes your model class as argument. This also includes methods of your
model class, so if your model has a `to_dict()` method, you can simply write `paginated_result.map(YourModel.to_dict)`.

There is also another helper method: `PaginatedResult.to_dict()` returns a dictionary with two keys: `items` which is a
regular list with the results, and `total_count` (which is self-explanatory). Additionally, this method has an option
`recursive`. If `recursive=True`, the method will automatically try to convert the items to dictionaries by calling the
`to_dict()` method on every item. If this method does not exist (or the item already is a dictionary), the item stays
unmodified. With this option, you don't need to use `map()` beforehand.


### Generating responses with paginated_api_response()

Of course you can already use the existing tools to build any kind of API response with the results.

However, unless you're implementing a specific API with a different response format, there is the convenient helper
function `paginated_api_response()` (which generates an API response in the format used by our internal services in our
company).

The function has two required and a few optional keyword parameters: It requires a `PaginatedResult` and the original
search query that contains the search parameters specified by the user. The search query is used to get information on
which kind of pagination is used. However, you *can* omit the search query by passing `None` (in that case, there will
be no extra information regarding pagination).

The function will use `PaginatedResult.to_dict(recursive=True)` as the base for the output dictionary (keys `item` and
`total_count` as described above). Since the recursive option is set, the results will automatically be converted to
dictionaries using the `.to_dict()` method of the objects, as long as this method is defined. If your model class does
not have this method or you need a custom mapping from objects to dictionaries, you should use `PaginatedResult.map()`
beforehand to convert them manually.

If you explicitly need to disable the recursive option, call `paginated_api_response()` with `recursive_to_dict=False`.
Though in most cases, this won't be necessary. For example, if the results are already dictionaries, nothing bad will
happen if the recursive option stays on.

If the search query has pagination enabled and the function detects that there could be another page (by checking the
amount of results on the page, the pagination parameters and the total count of results), another field will be added
to the output dictionary, containing the **next start parameter** (e.g. the next value for `offset` or `start`). The key
of this field depends on the type of pagination: `next_offset` for offset pagination, `next_id` for cursor pagination.

Additionally, you can set the optional keyword arguments `request_path` and `original_params`. If there is another page
and these arguments are set, another field with the key `next_path` will be added to the output dictionary. This field
will contain a full path including query parameters to access the next page of data. `request_path` will be used as the
base of this path (your API path, e.g. `/api/customers`). `original_params` should be a dictionary containing the
original (unvalidated) query parameters, which will be part of the `next_path` (except for the pagination parameters,
which will be set to the parameters needed to query the next page). If `original_params` is omitted, the path will only
contain the pagination parameters.

**Examples (using Flask):**

```python
from flask import request, jsonify

from validataclass_search_queries.pagination import PaginatedResult, paginated_api_response
from validataclass_search_queries.search_queries import BaseSearchQuery

# Validate the search query from query parameters
search_query: BaseSearchQuery = ...

# Fetch the results from a repository
paginated_result: PaginatedResult = ...

# Optional: Use a mapper function to map the objects to dictionaries
# (If possible, it's recommended to just define a to_dict() method on your model)
paginated_result = paginated_result.map(lambda customer: {
    'id': customer.id,
    'name': customer.name,
    # ...
})

# Generate a dictionary for an API response
response_dict = paginated_api_response(
    paginated_result,
    search_query,
    request_path=request.path,
    original_params=dict(request.args)
)

# Encode the response dictionary as JSON and return it
response = jsonify(response_dict)
```

In this example, the resulting response dictionaries will look something like this:

```
# These examples use offset pagination.

# Response when there is another page:
{
    "items": [
        {
            'id': 3,
            'name': 'Foo',
        },
        # [... more items ...]
    ],
    "total_count": 123,
    "next_offset": 10,
    "next_path": '/api/customers?offset=10&limit=10&other_parameters=from_original_query',
}

# Response when it's the last page:
{
    "items": [
        # [... items ...]
    ],
    "total_count": 123,
}
```

As with the validation of the search queries, it is recommended to write some base classes or helper methods to simplify
the code of your API endpoints. For example, you could write a method that calls `paginated_api_response()`, but
automatically sets `request_path` and `original_params`, and maybe already encodes the dictionary as JSON.


---

And this concludes the tutorial!

On the following page, there will be a [reference of all search filter types](03-search-param-reference.md).

For more information, please take a look at the in-code documentation of the library. All classes and helper functions
have detailed information on how to use them.
