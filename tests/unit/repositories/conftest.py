from unittest.mock import MagicMock

import pytest


@pytest.fixture
def database_connection() -> MagicMock:
    connection = MagicMock()
    connection.return_value = connection
    return connection
