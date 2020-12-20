from falcon import testing
import json
import pytest
from unittest.mock import patch

from dspace_statistics_api.app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_get_collection(client):
    """Test requesting a single collection."""

    response = client.simulate_get("/collection/8ea4b611-1f59-4d4e-b78d-a9921a72cfe7")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["downloads"], int)
    assert isinstance(response_doc["id"], str)
    assert isinstance(response_doc["views"], int)
    assert response.status_code == 200


def test_get_missing_collection(client):
    """Test requesting a single non-existing collection."""

    response = client.simulate_get("/collection/508abe0a-689f-402e-885d-2f6b02e7a39c")

    assert response.status_code == 404


def test_get_collections(client):
    """Test requesting 100 collections."""

    response = client.simulate_get("/collections", query_string="limit=100")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["currentPage"], int)
    assert isinstance(response_doc["totalPages"], int)
    assert isinstance(response_doc["statistics"], list)
    assert response.status_code == 200


def test_get_collections_invalid_limit(client):
    """Test requesting 100 collections with an invalid limit parameter."""

    response = client.simulate_get("/collections", query_string="limit=101")

    assert response.status_code == 400


def test_get_collections_invalid_page(client):
    """Test requesting 100 collections with an invalid page parameter."""

    response = client.simulate_get("/collections", query_string="page=-1")

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_collections_valid_dateFrom(client):
    """Test POSTing a request to /collections with a valid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00Z",
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_collections_valid_dateFrom_mocked(client):
    """Mock test POSTing a request to /collections with a valid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00Z",
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    get_views_return_value = {
        "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 21,
        "260548c8-fda4-4dc8-a979-03495753cdd5": 0,
    }
    get_downloads_return_value = {
        "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 575,
        "260548c8-fda4-4dc8-a979-03495753cdd5": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_collections_invalid_dateFrom(client):
    """Test POSTing a request to /collections with an invalid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00",
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_collections_valid_dateTo(client):
    """Test POSTing a request to /collections with a valid dateTo parameter in the request body."""

    request_body = {
        "dateTo": "2020-01-01T00:00:00Z",
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_collections_valid_dateTo_mocked(client):
    """Mock test POSTing a request to /collections with a valid dateTo parameter in the request body."""

    request_body = {
        "dateTo": "2020-01-01T00:00:00Z",
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    get_views_return_value = {
        "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 21,
        "260548c8-fda4-4dc8-a979-03495753cdd5": 0,
    }
    get_downloads_return_value = {
        "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 575,
        "260548c8-fda4-4dc8-a979-03495753cdd5": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_collections_invalid_dateTo(client):
    """Test POSTing a request to /collections with an invalid dateTo parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00",
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_collections_valid_limit(client):
    """Test POSTing a request to /collections with a valid limit parameter in the request body."""

    request_body = {
        "limit": 1,
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 1
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 1
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)


def test_post_collections_valid_limit_mocked(client):
    """Mock test POSTing a request to /collections with a valid limit parameter in the request body."""

    request_body = {
        "limit": 1,
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    get_views_return_value = {"8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 21}
    get_downloads_return_value = {"8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 575}

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 1
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 1
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)


def test_post_collections_invalid_limit(client):
    """Test POSTing a request to /collections with an invalid limit parameter in the request body."""

    request_body = {
        "limit": -1,
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_collections_valid_page(client):
    """Test POSTing a request to /collections with a valid page parameter in the request body."""

    request_body = {
        "page": 0,
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert response.json["totalPages"] == 0
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_collections_valid_page_mocked(client):
    """Mock test POSTing a request to /collections with a valid page parameter in the request body."""

    request_body = {
        "page": 0,
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    get_views_return_value = {
        "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 21,
        "260548c8-fda4-4dc8-a979-03495753cdd5": 0,
    }
    get_downloads_return_value = {
        "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7": 575,
        "260548c8-fda4-4dc8-a979-03495753cdd5": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_collections_invalid_page(client):
    """Test POSTing a request to /collections with an invalid page parameter in the request body."""

    request_body = {
        "page": -1,
        "collections": [
            "8ea4b611-1f59-4d4e-b78d-a9921a72cfe7",
            "260548c8-fda4-4dc8-a979-03495753cdd5",
        ],
    }

    response = client.simulate_post("/collections", json=request_body)

    assert response.status_code == 400
