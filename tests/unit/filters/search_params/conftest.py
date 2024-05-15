"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest
import sqlalchemy
from sqlalchemy.sql import ColumnElement


@pytest.fixture
def sqlalchemy_column() -> ColumnElement:
    return sqlalchemy.column('unit_test_column')
