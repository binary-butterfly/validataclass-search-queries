"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

__all__ = [
    'PaginatedResult',
]

T_Result = TypeVar('T_Result')
T_MappedResult = TypeVar('T_MappedResult')


class PaginatedResult(list[T_Result]):
    """
    Custom list type for paginated database query results.

    This type behaves exactly like a regular list, but has the additional attribute "total_count" which should be set to
    the total amount of results before the query was paginated (i.e. before the `LIMIT` was applied to the SQL query).
    """

    # Total amount of results in the original query (before pagination)
    total_count: int

    def __init__(self, items: Iterable[T_Result], *, total_count: int):
        """
        Creates a PaginatedResult from any iterable.

        The keyword argument `total_count` should be set to the total amount of items *before* pagination.
        """
        list.__init__(self, items)
        self.total_count = total_count

    def map(self, map_func: Callable[[T_Result], T_MappedResult]) -> 'PaginatedResult[T_MappedResult]':
        """
        Maps every item of the paginated result using the specified mapper function, and returns a *new* PaginatedResult
        containing the mapped items (with the same `total_count` as the original one).

        The mapper function can be any callable that accepts the type of objects stored in the PaginatedResult.

        Examples:

        ```
        # Here, the paginated result contains objects of type Customer.
        paginated_result: PaginatedResult[Customer]

        # This method maps Customer objects to simple dictionaries
        def map_customers(customer: Customer) -> dict:
            return {
                'id': customer.id,
                'name': customer.name,
            }

        # This results in a PaginatedResult[dict] containing dictionaries as defined in map_customers above:
        mapped_customers = paginated_result.map(map_customers)

        # Assuming that the Customer class has a similar method `to_dict()` that takes no arguments, we can also do this:
        mapped_customers = paginated_result.map(Customers.to_dict)
        ```
        """
        # Previously, we used self.__class__() instead of PaginatedResult() here to properly support subclassing.
        # However, we don't know whether this potential subclass is a Generic too, so it might not even support
        # T_MappedResult. In other words, `self.__class__` can only be a subtype of `PaginatedResult[T_Result]`,
        # not of `PaginatedResult[T_MappedResult]`.
        return PaginatedResult(
            map(map_func, self),
            total_count=self.total_count,
        )

    def to_dict(self, *, recursive: bool = False) -> dict[str, Any]:
        """
        Returns a dictionary representing the PaginatedResult, consisting of the keys "items" (a list of the items) and
        "total_count" (the total count as an integer).

        If `recursive` is True (default: False), the method will try to convert all items to dictionaries by calling
        `to_dict()` on the item. If an object does not have a `to_dict` method, the list will contain the unmodified
        object as if `recursive` was not set.
        """
        if recursive:
            items = [item.to_dict() if hasattr(item, 'to_dict') else item for item in self]
        else:
            items = list(self)

        return {
            'items': items,
            'total_count': self.total_count,
        }
