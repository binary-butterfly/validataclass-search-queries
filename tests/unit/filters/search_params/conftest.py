"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest
import sqlalchemy
from sqlalchemy.sql import ColumnElement


@pytest.fixture
def sqlalchemy_column() -> ColumnElement:
    return sqlalchemy.column('unit_test_column')
