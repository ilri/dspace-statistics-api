from falcon import testing
import json
import pytest
from unittest.mock import patch

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

    response = client.simulate_get("/item/c3910974-c3a5-4053-9dce-104aa7bb1621")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["downloads"], int)
    assert isinstance(response_doc["id"], str)
    assert isinstance(response_doc["views"], int)
    assert response.status_code == 200


def test_get_missing_item(client):
    """Test requesting a single non-existing item."""

    response = client.simulate_get("/item/c3910974-c3a5-4053-9dce-104aa7bb1620")

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


@pytest.mark.xfail
def test_post_items_valid_dateFrom(client):
    """Test POSTing a request with a valid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00Z",
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_items_valid_dateFrom_mocked(client):
    """Mock test POSTing a request with a valid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00Z",
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    get_views_return_value = {
        "c3910974-c3a5-4053-9dce-104aa7bb1620": 21,
        "887cc5f8-b5e7-4a2f-9053-49c91ab81313": 0,
    }
    get_downloads_return_value = {
        "c3910974-c3a5-4053-9dce-104aa7bb1620": 575,
        "887cc5f8-b5e7-4a2f-9053-49c91ab81313": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_items_invalid_dateFrom(client):
    """Test POSTing a request with an invalid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00",
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_items_valid_dateTo(client):
    """Test POSTing a request with a valid dateTo parameter in the request body."""

    request_body = {
        "dateTo": "2020-01-01T00:00:00Z",
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_items_valid_dateTo_mocked(client):
    """Mock test POSTing a request with a valid dateTo parameter in the request body."""

    request_body = {
        "dateTo": "2020-01-01T00:00:00Z",
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    get_views_return_value = {
        "c3910974-c3a5-4053-9dce-104aa7bb1620": 21,
        "887cc5f8-b5e7-4a2f-9053-49c91ab81313": 0,
    }
    get_downloads_return_value = {
        "c3910974-c3a5-4053-9dce-104aa7bb1620": 575,
        "887cc5f8-b5e7-4a2f-9053-49c91ab81313": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_items_invalid_dateTo(client):
    """Test POSTing a request with an invalid dateTo parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00",
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_items_valid_limit(client):
    """Test POSTing a request with a valid limit parameter in the request body."""

    request_body = {
        "limit": 1,
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 1
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 1
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)


def test_post_items_valid_limit_mocked(client):
    """Mock test POSTing a request with a valid limit parameter in the request body."""

    request_body = {
        "limit": 1,
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    get_views_return_value = {"c3910974-c3a5-4053-9dce-104aa7bb1620": 21}
    get_downloads_return_value = {"c3910974-c3a5-4053-9dce-104aa7bb1620": 575}

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 1
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 1
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)


def test_post_items_invalid_limit(client):
    """Test POSTing a request with an invalid limit parameter in the request body."""

    request_body = {
        "limit": -1,
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_items_valid_page(client):
    """Test POSTing a request with a valid page parameter in the request body."""

    request_body = {
        "page": 0,
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert response.json["totalPages"] == 0
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_items_valid_page_mocked(client):
    """Mock test POSTing a request with a valid page parameter in the request body."""

    request_body = {
        "page": 0,
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    get_views_return_value = {
        "c3910974-c3a5-4053-9dce-104aa7bb1620": 21,
        "887cc5f8-b5e7-4a2f-9053-49c91ab81313": 0,
    }
    get_downloads_return_value = {
        "c3910974-c3a5-4053-9dce-104aa7bb1620": 575,
        "887cc5f8-b5e7-4a2f-9053-49c91ab81313": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_items_invalid_page(client):
    """Test POSTing a request with an invalid page parameter in the request body."""

    request_body = {
        "page": -1,
        "items": [
            "c3910974-c3a5-4053-9dce-104aa7bb1620",
            "887cc5f8-b5e7-4a2f-9053-49c91ab81313",
        ],
    }

    response = client.simulate_post("/items", json=request_body)

    assert response.status_code == 400
