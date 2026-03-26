"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

import pytest
import sqlalchemy
from sqlalchemy.sql import ColumnElement


@pytest.fixture
def sqlalchemy_column() -> ColumnElement[Any]:
    return sqlalchemy.column('unit_test_column')
