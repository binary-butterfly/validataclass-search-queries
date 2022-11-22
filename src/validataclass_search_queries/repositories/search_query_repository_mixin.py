"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Optional, Generic, Type, TypeVar

from sqlalchemy.orm import Query

from ..filters import BoundSearchFilter
from ..pagination import AbstractPaginationMixin, PaginatedResult
from ..search_queries import BaseSearchQuery
from ..sorting import AbstractSortingMixin

__all__ = [
    'SearchQueryRepositoryMixin',
    'T_Model',
]

T_Model = TypeVar('T_Model')


class SearchQueryRepositoryMixin(Generic[T_Model], ABC):
    """
    Mixin class with helper methods for repositories to work with search queries (including pagination and sorting).

    The class is defined as a generic with the model class as type parameter (e.g. `RepositoryMixin[User]` where `User`
    is your model class). This isn't strictly necessary, but helps with type hinting. However, you DO need to set the
    `model_cls` property to your model class (can be set as a regular attribute too, see example below).

    The mixin defines the following helper methods (which should only be used internally by your repository class, hence
    the leading underscores). With one minor exception, they all take a database query (`sqlalchemy.orm.Query`) and a
    search query (defined with `@search_query_dataclass`) as arguments and return either a new database query or a
    `PaginatedResult`.

    - Search filters (`SearchParam`) can be applied using `_filter_by_search_query()`. It iterates over all fields that
      are set in the search query, calls `_apply_bound_search_filter()` for every set filter to apply them to the
      database query, and returns the modified query.
    - Sorting the results (`SortingMixin`) can be done using `_order_by_search_query()`. It gets the order column from
      the search query, applies an `order_by()` to your query, and returns the modified query.
    - Pagination (`CursorPaginationMixin` or `OffsetPaginationMixin`) is handled by `_paginate_result()`. It applies
      the filters, limits and/or offsets to your query. Instead of returning a new query, however, it then *executes*
      your query and returns a `PaginatedResult`.

    But wait, there's more: As a shortcut for applying all of the methods above, there is the "all-inclusive" helper
    method `_search_and_paginate()`. It applies your search filters, sorting and pagination, executes your query and
    returns a `PaginatedResult`.

    All of these methods can be used regardless of whether your search query dataclass implements the according feature,
    so for example, if your dataclass does not include the `SortingMixin`, `_order_by_search_query()` will return your
    database query unmodified. If your search query does not implement any pagination, `_paginate_result()` (and by
    extension `_search_and_paginate()`) will still return a `PaginatedResult` object, but it will contain ALL results
    of your query (as if the pagination limit was set to infinity).

    In most cases, you probably can just use `return self._search_and_paginate(query, search_query)` at the end of your
    fetch method and ignore everything else.

    Basic example:

    ```
    # Here, "Example" would be an SQLAlchemy model class.
    class ExampleRepository(SearchQueryRepositoryMixin[Example]):
        # This abstract property needs to be set to the model class in every repository that uses this mixin
        model_cls = Example

        # This would be an SQLAlchemy database session that gets dependency-injected
        session: Session

        def __init__(self, *, session: Session):
            self.session = session

        # Example for a fetch method that filters, sorts and paginates by search query
        def fetch_examples(self, *, search_query: Optional[BaseSearchQuery] = None) -> PaginatedResult[Example]:
            query = self.session.query(Example)
            return self._search_and_paginate(query, search_query)
    ```

    In more complex scenarios, you might need to implement special handling for your search queries. The methods of this
    mixin are designed to be overridden and extended, to make implementation of such special cases as easy as possible.

    The most useful method to override probably is `_apply_bound_search_filter()`, which is the internal method used
    by `_filter_by_search_query()` for every set search parameter.

    The default implementation of `_apply_bound_search_filter()` first gets the column of the model class with the name
    specified in the SearchParam (`getattr(self.model_cls, bound_filter.column_name)` and applies the search filter to
    this column (`query.filter(bound_filter.get_sqlalchemy_filter(col))`). For example, with a `SearchParamSince('created')`
    and the `Example` model, the "since" filter (i.e. `>=`) would be applied to the column `Example.created`.

    If you need to, you can override this method, choose a different column (maybe even from a different model, or using
    some SQL functions) and apply the search filter to this column.

    For example, imagine your model has child objects and you want a "last modified since" filter that not only looks at
    the modification date of the parent object, but also at the modification dates of its child objects, so that your
    filter includes all objects where either the parent or one of its children was modified since the specified date.
    In SQL terms, this could be written as `WHERE GREATEST(Parent.modified, Child.modified) >= value`. In SQLAlchemy,
    there is the corresponding `func.greatest()` function.

    The following example implements this special behavior for the "modified" column (independently from the actual
    filter that is used, e.g. SearchParamSince or SearchParamUntil) using the methods of this mixin class:

    ```
    # Here, we have to models: Customer and Address. Both have a "modified" column. Customer has a relation
    # "shipping_address" to exactly one Address.
    class CustomerRepository(SearchQueryRepositoryMixin[Customer]):
        model_cls = Customer

        # (__init__(): see other example above)

        def fetch_customers(self, *, search_query: Optional[BaseSearchQuery] = None) -> PaginatedResult[Customer]:
            # We need to JOIN the Customer query with the Address model via the shipping_address relation
            query = self.session.query(Customer).join(Customer.shipping_address)
            return self._search_and_paginate(query, search_query)

        # Override the default method for applying search filters
        def _apply_bound_search_filter(self, query: Query, bound_filter: BoundSearchFilter) -> Query:
            # Only implement a special case for the "modified" column
            if bound_filter.column_name == 'modified':
                # Get column objects for both models
                customer_col = getattr(Customer, 'modified')
                address_col = getattr(Address, 'modified')

                # Use GREATEST function to get the highest value of both columns
                greatest_col = func.greatest(costumer_col, address_col)

                # Apply the filter
                return query.filter(bound_filter.get_sqlalchemy_filter(greatest_col)

            # Call default implementation for all other filters
            return super()._apply_bound_search_filter(query, bound_filter)
    ```

    In a similar way, you can also override the other methods, but most special cases should be implementable by
    overriding just `_apply_bound_search_filter()`.
    """

    @property
    @abstractmethod
    def model_cls(self) -> Type[T_Model]:
        """
        The model class used by this repository.

        Abstract property that needs to be defined by any repository using this mixin.
        """
        raise NotImplementedError

    def _search_and_paginate(self, query: Query, search_query: Optional[BaseSearchQuery]) -> PaginatedResult[T_Model]:
        """
        Filters a query based on search parameters (usually parsed from HTTP query parameters) and paginates the result.

        Shortcut method for calling `_filter_by_search_query()`, `_order_by_search_query()` and `_paginate_result()`.
        """
        query = self._filter_by_search_query(query, search_query)
        query = self._order_by_search_query(query, search_query)
        return self._paginate_result(query, search_query)

    def _filter_by_search_query(self, query: Query, search_query: Optional[BaseSearchQuery]) -> Query:
        """
        Filters a query based on search parameters (usually parsed from HTTP query parameters), *excluding* pagination.

        If no search query is given (or no search parameter is set), the database query is returned unmodified.
        """
        if search_query is None:
            return query

        # Apply all search filters one-by-one
        for _param_name, bound_filter in search_query.get_search_filters():
            query = self._apply_bound_search_filter(query, bound_filter)

        return query

    def _apply_bound_search_filter(self, query: Query, bound_filter: BoundSearchFilter) -> Query:
        """
        Filters a query based on a BoundSearchFilter. Called by _filter_by_search_query() for every set search filter.

        Override this method to implement custom handling for (all or specific) search filters.
        """
        # Get column object and apply filter
        col = getattr(self.model_cls, bound_filter.column_name)
        return query.filter(bound_filter.get_sqlalchemy_filter(col))

    def _order_by_search_query(self, query: Query, search_query: Optional[BaseSearchQuery]) -> Query:
        """
        Applies sorting (order_by) to a query based on sorting parameters from a search query.

        If the search query does not implement sorting (i.e. it does not inherit from `AbstractSortingMixin`), the
        database query is returned unmodified.
        """
        if search_query and isinstance(search_query, AbstractSortingMixin):
            query = search_query.apply_sorting_to_query(query, self.model_cls)

        return query

    def _paginate_result(self, query: Query, search_query: Optional[BaseSearchQuery]) -> PaginatedResult[T_Model]:
        """
        Applies pagination to a query based on search parameters, executes the query and returns a paginated result list.

        To define pagination parameters in your search query dataclass, use a pagination mixin like OffsetPaginationMixin
        or StablePaginationMixin.

        If the search query does not implement pagination (i.e. it does not inherit from `AbstractPaginationMixin`),
        a PaginatedResult with ALL results is returned (as if the pagination limit was set to infinity).
        """
        # Get total count of search results BEFORE pagination is applied
        total_count = query.count()

        if search_query and isinstance(search_query, AbstractPaginationMixin):
            query = search_query.apply_pagination_to_query(query, self.model_cls)

        return PaginatedResult(query.all(), total_count=total_count)
