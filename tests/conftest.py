import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="session", autouse=True)
def mock_instagram_login():
    mock_client_instance = MagicMock()
    mock_client_instance.login_by_sessionid.return_value = True
    with patch("services.instagram.Client", return_value=mock_client_instance):
        yield