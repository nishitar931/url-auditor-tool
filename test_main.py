from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
import requests

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. HAPPY PATH TEST
# ---------------------------------------------------------------------------
@patch("main.requests.get")
def test_audit_url_success(mock_get):
    """Tests auditing a valid HTML webpage with expected tags and content."""
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page Title</title>
        <meta name="description" content="This is a test meta description for auditing.">
    </head>
    <body>
        <h1>Primary Heading</h1>
        <img src="test1.jpg" alt="Valid Alt Text" />
        <img src="test2.jpg" />
        <p>This is a short sample body containing several words for word count validation.</p>
    </body>
    </html>
    """

    mock_get.return_value.status_code = 200
    mock_get.return_value.url = "https://digitalheroesco.com"
    mock_get.return_value.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_get.return_value.text = mock_html

    response = client.post(
        "/api/audit", json={"url": "https://digitalheroesco.com"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status_code"] == 200
    assert data["page_title"] == "Test Page Title"
    assert (
        data["meta_description"]
        == "This is a test meta description for auditing."
    )
    assert data["h1_count"] == 1
    assert data["total_images"] == 2
    assert data["images_missing_alt"] == 1
    assert data["word_count"] > 0


# ---------------------------------------------------------------------------
# 2. FAILURE CASE 1: Non-HTML Response (e.g., JSON or PDF)
# ---------------------------------------------------------------------------
@patch("main.requests.get")
def test_audit_url_non_html_response(mock_get):
    """Tests handling of URLs returning non-HTML content types (e.g., application/json)."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.headers = {"Content-Type": "application/json"}
    mock_get.return_value.text = '{"status": "ok"}'

    response = client.post("/api/audit", json={"url": "https://example.com/api"})

    assert response.status_code == 415
    data = response.json()
    assert (
        "Non-HTML response detected" in data["error"]
    )


# ---------------------------------------------------------------------------
# 3. FAILURE CASE 2: Network Timeout
# ---------------------------------------------------------------------------
@patch("main.requests.get")
def test_audit_url_timeout_failure(mock_get):
    """Tests handling when the target server times out during retrieval."""
    mock_get.side_effect = requests.exceptions.Timeout()

    response = client.post(
        "/api/audit", json={"url": "https://slow-server.example.com"}
    )

    assert response.status_code == 504
    data = response.json()
    assert "timed out" in data["error"]