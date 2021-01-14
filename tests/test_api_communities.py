import json
from unittest.mock import patch

import pytest
from falcon import testing

from dspace_statistics_api.app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_get_community(client):
    """Test requesting a single community."""

    response = client.simulate_get("/community/bde7139c-d321-46bb-aef6-ae70799e5edb")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["downloads"], int)
    assert isinstance(response_doc["id"], str)
    assert isinstance(response_doc["views"], int)
    assert response.status_code == 200


def test_get_missing_community(client):
    """Test requesting a single non-existing community."""

    response = client.simulate_get("/item/dec6bfc6-efeb-4f74-8436-79fa80bb5c21")

    assert response.status_code == 404


def test_get_communities(client):
    """Test requesting 100 communities."""

    response = client.simulate_get("/communities", query_string="limit=100")
    response_doc = json.loads(response.text)

    assert isinstance(response_doc["currentPage"], int)
    assert isinstance(response_doc["totalPages"], int)
    assert isinstance(response_doc["statistics"], list)
    assert response.status_code == 200


def test_get_communities_invalid_limit(client):
    """Test requesting 100 communities with an invalid limit parameter."""

    response = client.simulate_get("/communities", query_string="limit=101")

    assert response.status_code == 400


def test_get_communities_invalid_page(client):
    """Test requesting 100 communities with an invalid page parameter."""

    response = client.simulate_get("/communities", query_string="page=-1")

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_communities_valid_dateFrom(client):
    """Test POSTing a request to /communities with a valid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00Z",
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_communities_valid_dateFrom_mocked(client):
    """Mock test POSTing a request to /communities with a valid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00Z",
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    get_views_return_value = {
        "bde7139c-d321-46bb-aef6-ae70799e5edb": 309,
        "2a920a61-b08a-4642-8e5d-2639c6702b1f": 0,
    }
    get_downloads_return_value = {
        "bde7139c-d321-46bb-aef6-ae70799e5edb": 400,
        "2a920a61-b08a-4642-8e5d-2639c6702b1f": 290,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_communities_invalid_dateFrom(client):
    """Test POSTing a request to /communities with an invalid dateFrom parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00",
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_communities_valid_dateTo(client):
    """Test POSTing a request to /communities with a valid dateTo parameter in the request body."""

    request_body = {
        "dateTo": "2020-01-01T00:00:00Z",
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_communities_valid_dateTo_mocked(client):
    """Mock test POSTing a request to /communities with a valid dateTo parameter in the request body."""

    request_body = {
        "dateTo": "2020-01-01T00:00:00Z",
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    get_views_return_value = {
        "bde7139c-d321-46bb-aef6-ae70799e5edb": 21,
        "2a920a61-b08a-4642-8e5d-2639c6702b1f": 0,
    }
    get_downloads_return_value = {
        "bde7139c-d321-46bb-aef6-ae70799e5edb": 575,
        "2a920a61-b08a-4642-8e5d-2639c6702b1f": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_communities_invalid_dateTo(client):
    """Test POSTing a request to /communities with an invalid dateTo parameter in the request body."""

    request_body = {
        "dateFrom": "2020-01-01T00:00:00",
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_communities_valid_limit(client):
    """Test POSTing a request to /communities with a valid limit parameter in the request body."""

    request_body = {
        "limit": 1,
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 1
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 1
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)


def test_post_communities_valid_limit_mocked(client):
    """Mock test POSTing a request to /communities with a valid limit parameter in the request body."""

    request_body = {
        "limit": 1,
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    get_views_return_value = {"bde7139c-d321-46bb-aef6-ae70799e5edb": 200}
    get_downloads_return_value = {"bde7139c-d321-46bb-aef6-ae70799e5edb": 309}

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 1
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 1
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)


def test_post_communities_invalid_limit(client):
    """Test POSTing a request to /communities with an invalid limit parameter in the request body."""

    request_body = {
        "limit": -1,
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 400


@pytest.mark.xfail
def test_post_communities_valid_page(client):
    """Test POSTing a request to /communities with a valid page parameter in the request body."""

    request_body = {
        "page": 0,
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert response.json["totalPages"] == 0
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_communities_valid_page_mocked(client):
    """Mock test POSTing a request to communities with a valid page parameter in the request body."""

    request_body = {
        "page": 0,
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    get_views_return_value = {
        "bde7139c-d321-46bb-aef6-ae70799e5edb": 21,
        "2a920a61-b08a-4642-8e5d-2639c6702b1f": 0,
    }
    get_downloads_return_value = {
        "bde7139c-d321-46bb-aef6-ae70799e5edb": 575,
        "2a920a61-b08a-4642-8e5d-2639c6702b1f": 899,
    }

    with patch(
        "dspace_statistics_api.app.get_views", return_value=get_views_return_value
    ):
        with patch(
            "dspace_statistics_api.app.get_downloads",
            return_value=get_downloads_return_value,
        ):
            response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 200
    assert response.json["limit"] == 100
    assert response.json["currentPage"] == 0
    assert isinstance(response.json["totalPages"], int)
    assert len(response.json["statistics"]) == 2
    assert isinstance(response.json["statistics"][0]["views"], int)
    assert isinstance(response.json["statistics"][0]["downloads"], int)
    assert isinstance(response.json["statistics"][1]["views"], int)
    assert isinstance(response.json["statistics"][1]["downloads"], int)


def test_post_communities_invalid_page(client):
    """Test POSTing a request to /communities with an invalid page parameter in the request body."""

    request_body = {
        "page": -1,
        "communities": [
            "bde7139c-d321-46bb-aef6-ae70799e5edb",
            "2a920a61-b08a-4642-8e5d-2639c6702b1f",
        ],
    }

    response = client.simulate_post("/communities", json=request_body)

    assert response.status_code == 400


# vim: set sw=4 ts=4 expandtab:
