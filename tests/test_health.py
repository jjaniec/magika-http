"""
Tests for the /healthz endpoint.
"""

from fastapi.testclient import TestClient


def test_healthz_returns_200(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200


def test_healthz_status_ok(client: TestClient) -> None:
    data = client.get("/healthz").json()
    assert data["status"] == "ok"


def test_healthz_model_ready(client: TestClient) -> None:
    data = client.get("/healthz").json()
    assert data["model_ready"] is True


def test_healthz_has_model_version(client: TestClient) -> None:
    data = client.get("/healthz").json()
    assert isinstance(data["model_version"], str)
    assert len(data["model_version"]) > 0


def test_healthz_has_magika_version(client: TestClient) -> None:
    data = client.get("/healthz").json()
    assert isinstance(data["magika_version"], str)
    assert len(data["magika_version"]) > 0
