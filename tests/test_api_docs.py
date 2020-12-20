from falcon import testing
import pytest

from dspace_statistics_api.app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_get_docs(client):
    """Test requesting the documentation at the root."""

    response = client.simulate_get("/")

    assert isinstance(response.content, bytes)
    assert response.status_code == 200
