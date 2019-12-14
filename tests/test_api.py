from falcon import testing
import json
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


def test_get_item(client):
    """Test requesting a single item."""

    response = client.simulate_get("/item/17")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["downloads"], int)
    assert isinstance(response_doc["id"], int)
    assert isinstance(response_doc["views"], int)
    assert response.status_code == 200


def test_get_missing_item(client):
    """Test requesting a single non-existing item."""

    response = client.simulate_get("/item/1")

    assert response.status_code == 404


def test_get_items(client):
    """Test requesting 100 items."""

    response = client.simulate_get("/items", query_string="limit=100")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["currentPage"], int)
    assert isinstance(response_doc["totalPages"], int)
    assert isinstance(response_doc["statistics"], list)
    assert response.status_code == 200


def test_get_items_invalid_limit(client):
    """Test requesting 100 items with an invalid limit parameter."""

    response = client.simulate_get("/items", query_string="limit=101")

    assert response.status_code == 400


def test_get_items_invalid_page(client):
    """Test requesting 100 items with an invalid page parameter."""

    response = client.simulate_get("/items", query_string="page=-1")

    assert response.status_code == 400
