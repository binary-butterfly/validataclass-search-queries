"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass_search_queries.filters import SearchParamCustom


def test_search_param_custom(sqlalchemy_column):
    """ Test the SearchParamBoolean search parameter. """
    search_param = SearchParamCustom()
    with pytest.raises(NotImplementedError) as error:
        search_param.sqlalchemy_filter(sqlalchemy_column, 'any value')
    assert str(error.value) == 'Custom search parameter needs to be handled in the repository!'
