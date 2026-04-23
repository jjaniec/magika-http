"""
Tests for the /scan endpoint.
"""

from fastapi.testclient import TestClient


def _post_file(client: TestClient, file_tuple: tuple) -> dict:
    name, buf, mime = file_tuple
    response = client.post("/scan", files={"file": (name, buf, mime)})
    return response


class TestScanPython:
    def test_status_200(self, client: TestClient, python_file) -> None:
        assert _post_file(client, python_file).status_code == 200

    def test_ok_true(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert data["ok"] is True

    def test_label_is_python(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert data["label"] == "python"

    def test_mime_type_present(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert "python" in data["mime_type"]

    def test_score_between_0_and_1(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert 0.0 <= data["score"] <= 1.0

    def test_scan_duration_ms_positive(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert data["scan_duration_ms"] >= 0


class TestScanPng:
    def test_status_200(self, client: TestClient, png_file) -> None:
        assert _post_file(client, png_file).status_code == 200

    def test_ok_true(self, client: TestClient, png_file) -> None:
        data = _post_file(client, png_file).json()
        assert data["ok"] is True

    def test_label_is_png(self, client: TestClient, png_file) -> None:
        data = _post_file(client, png_file).json()
        assert data["label"] == "png"

    def test_mime_type_is_png(self, client: TestClient, png_file) -> None:
        data = _post_file(client, png_file).json()
        assert data["mime_type"] == "image/png"


class TestScanPdf:
    def test_status_200(self, client: TestClient, pdf_file) -> None:
        assert _post_file(client, pdf_file).status_code == 200

    def test_ok_true(self, client: TestClient, pdf_file) -> None:
        data = _post_file(client, pdf_file).json()
        assert data["ok"] is True

    def test_label_is_pdf(self, client: TestClient, pdf_file) -> None:
        data = _post_file(client, pdf_file).json()
        assert data["label"] == "pdf"


class TestScanResponseSchema:
    """Verify the response schema contains all required fields."""

    REQUIRED_FIELDS = {
        "ok",
        "label",
        "mime_type",
        "group",
        "description",
        "extensions",
        "is_text",
        "score",
        "scan_duration_ms",
    }

    def test_all_fields_present(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert self.REQUIRED_FIELDS.issubset(data.keys())

    def test_extensions_is_list(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert isinstance(data["extensions"], list)

    def test_is_text_is_bool(self, client: TestClient, python_file) -> None:
        data = _post_file(client, python_file).json()
        assert isinstance(data["is_text"], bool)


class TestScanEdgeCases:
    def test_missing_file_returns_422(self, client: TestClient) -> None:
        response = client.post("/scan")
        assert response.status_code == 422

    def test_empty_file_returns_200(self, client: TestClient, empty_file) -> None:
        # Magika handles empty files gracefully (returns a valid result)
        response = _post_file(client, empty_file)
        assert response.status_code == 200

    def test_empty_file_ok_true(self, client: TestClient, empty_file) -> None:
        data = _post_file(client, empty_file).json()
        assert data["ok"] is True
