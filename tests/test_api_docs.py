# SPDX-License-Identifier: GPL-3.0-only

import pytest
from falcon import testing

from dspace_statistics_api.app import app


@pytest.fixture
def client():
    return testing.TestClient(app)


def test_get_docs(client):
    """Test requesting the documentation at the root."""

    response = client.simulate_get("/")

    assert isinstance(response.content, bytes)
    assert response.status_code == 200


def test_get_openapi_json(client):
    """Test requesting the OpenAPI JSON schema."""

    response = client.simulate_get("/docs/openapi.json")

    assert isinstance(response.content, bytes)
    assert response.status_code == 200


def test_get_swagger_ui(client):
    """Test requesting the Swagger UI."""

    response = client.simulate_get("/swagger")

    assert isinstance(response.content, bytes)
    assert response.status_code == 200


def test_get_status(client):
    """Test requesting the status page."""

    response = client.simulate_get("/status")

    assert isinstance(response.content, bytes)
    assert response.status_code == 200


# vim: set sw=4 ts=4 expandtab:
