"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Optional, Any

from .abstract_pagination_mixin import AbstractPaginationMixin
from .paginated_result import PaginatedResult
from ..search_queries import BaseSearchQuery

__all__ = [
    'paginated_api_response',
]


def paginated_api_response(
    paginated_result: PaginatedResult[Any],
    search_query: BaseSearchQuery,
    *,
    request_path: Optional[str] = None,
    original_params: Optional[dict] = None,
) -> dict:
    """
    Constructs a REST API response (as a dictionary) for paginated results.

    Requires a PaginatedResult (might contain dictionaries or objects) and the search query that was used to query the
    results. Optionally a request base path and a dictionary with the original query parameters can be given.

    The format of this dictionary varies depending on the parameters given and the type of pagination.

    Example for a dictionary (here, offset pagination is used and all optional parameters are given):

    ```
    {
        "items": [
            { first item... },
            { second item... },
        ],
        "total_count": 123,
        "next_id": 7,
        "next_path": '/base/path?start=7&limit=10&other_parameters=from_original_query',
    }
    ```

    The keys "items" and "total_count" will always be set.

    "items" contains a list with the results (which will be automatically converted to dictionaries if they implement
    `to_dict()`).

    "total_count" is the total number of results before pagination (i.e. if there are 123 results and the page limit is
    10, there will be 10 items, but "total_count" will be 123).

    If there might be a next page (which is determined e.g. by the number of results and the given pagination parameters),
    there will be another field that contains the start value for the next page. In case of offset pagination, this
    field will be called "next_offset", in case of cursor pagination, it will be called "next_id".

    Additionally, if the optional parameter `request_path` is set, another field called "next_path" will be added to the
    response, containing the URL path with query parameters that can be used to retrieve the next page. This string
    will use `request_path` as the prefix, followed by a "?", followed by the query parameters separated by "&" (for
    example: "/base/path?start=7&limit=10").

    You can further set `original_params` to the dictionary with the original query parameters of the request, which
    will be merged with the next page parameters and appended to the "next_path" (see example dictionary above).

    If `request_path` is not set, the parameter `original_params` will be ignored.
    """
    # Construct base for response dictionary (with keys "items" and "total_count")
    response_data = paginated_result.to_dict(recursive=True)

    # If the result is empty, there certainly will be no next page
    if len(paginated_result) == 0:
        return response_data

    # If pagination is enabled: Add information on how to get the next page
    if isinstance(search_query, AbstractPaginationMixin):
        # Get the start parameter for the next page
        next_start_value = search_query.get_next_start_value(paginated_result)

        # Don't add next page fields if this is the last page
        if next_start_value is None:
            return response_data

        # Write next start parameter to response. For legacy reasons, cursor pagination uses "next_id" instead of "next_start".
        # TODO: This might be changed in the future, but we need to keep compatibility somehow...
        start_param = search_query.get_start_parameter_name()
        response_data['next_id' if start_param == 'start' else f'next_{start_param}'] = next_start_value

        # Only set next_path if a request base path is given
        if request_path is not None:
            # Construct parameters for next page from original request parameters (if given). Ensure limit parameter is set.
            next_path_params = dict(original_params) if original_params is not None else {}
            next_path_params.update({
                start_param: next_start_value,
                'limit': search_query.limit,
            })

            # Construct path with query parameters and write to response
            query_str = '&'.join([f'{key}={value}' for key, value in next_path_params.items() if value is not None])
            response_data['next_path'] = f'{request_path}?{query_str}'

    return response_data
