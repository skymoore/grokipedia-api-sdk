import pytest
from httpx import Response

from grokipedia_api_sdk import Client
from grokipedia_api_sdk.exceptions import (
    GrokipediaBadRequestError,
    GrokipediaNetworkError,
    GrokipediaNotFoundError,
    GrokipediaRateLimitError,
    GrokipediaServerError,
)


def test_client_initialization():
    with Client() as client:
        assert client.base_url == "https://grokipedia.com"
        assert client.timeout == 30.0
        assert client.max_retries == 3


def test_client_custom_config():
    with Client(
        base_url="https://custom.example.com",
        timeout=60.0,
        max_retries=5,
        retry_backoff_factor=1.0,
    ) as client:
        assert client.base_url == "https://custom.example.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_backoff_factor == 1.0


def test_client_context_manager_required():
    client = Client()
    with pytest.raises(RuntimeError, match="must be used as a context manager"):
        client.search("test")


def test_search_success(httpx_mock, search_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/full-text-search?query=python&limit=10&offset=0",
        json=search_response_data,
    )

    with Client() as client:
        response = client.search("python", limit=10, offset=0)

    assert len(response.results) == 2
    assert response.results[0].slug == "Python"
    assert response.results[0].relevance_score == 3106.541015625


def test_get_page_success(httpx_mock, page_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/page?slug=Python&includeContent=true&validateLinks=false",
        json=page_response_data,
    )

    with Client() as client:
        response = client.get_page("Python", include_content=True)

    assert response.found is True
    assert response.page.slug == "Python"
    assert response.page.title == "Python"
    assert len(response.page.citations) == 1


def test_get_page_without_content(httpx_mock):
    page_data = {
        "page": {
            "slug": "Python",
            "title": "Python",
            "content": "",
            "description": "Python programming language",
            "citations": [],
            "images": [],
            "fixedIssues": [],
            "metadata": {},
            "stats": {},
            "linkedPages": [],
        },
        "found": True,
    }
    httpx_mock.add_response(
        url="https://grokipedia.com/api/page?slug=Python&includeContent=false&validateLinks=false",
        json=page_data,
    )

    with Client() as client:
        response = client.get_page("Python", include_content=False)

    assert response.found is True
    assert response.page.content == ""


def test_get_constants_success(httpx_mock, constants_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/constants",
        json=constants_response_data,
    )

    with Client() as client:
        response = client.get_constants()

    assert response.account_url == "https://accounts.x.ai"
    assert response.grok_com_url == "https://grok.com"
    assert response.app_env == "production"


def test_get_stats_success(httpx_mock, stats_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/stats",
        json=stats_response_data,
    )

    with Client() as client:
        response = client.get_stats()

    assert response.total_pages == "885279"
    assert response.index_size_bytes == "46898447051"


def test_bad_request_error(httpx_mock):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/full-text-search?query=test&limit=12&offset=0",
        status_code=400,
        json={"error": "Invalid query"},
    )

    with Client() as client:
        with pytest.raises(GrokipediaBadRequestError) as exc_info:
            client.search("test")

    assert exc_info.value.status_code == 400


def test_not_found_error(httpx_mock):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/page?slug=NonExistent&includeContent=true&validateLinks=false",
        status_code=404,
    )

    with Client() as client:
        with pytest.raises(GrokipediaNotFoundError) as exc_info:
            client.get_page("NonExistent")

    assert exc_info.value.status_code == 404


def test_rate_limit_error(httpx_mock):
    httpx_mock.add_response(
        status_code=429,
        json={"error": "Rate limit exceeded"},
    )

    with Client(max_retries=1) as client:
        with pytest.raises(GrokipediaRateLimitError) as exc_info:
            client.search("test")

    assert exc_info.value.status_code == 429


def test_server_error(httpx_mock):
    httpx_mock.add_response(
        status_code=500,
        json={"error": "Internal server error"},
    )

    with Client(max_retries=1) as client:
        with pytest.raises(GrokipediaServerError) as exc_info:
            client.search("test")

    assert exc_info.value.status_code == 500


def test_retry_on_server_error(httpx_mock, search_response_data):
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(json=search_response_data)

    with Client(max_retries=3, retry_backoff_factor=0.01) as client:
        response = client.search("test")

    assert len(response.results) == 2


def test_retry_exhausted(httpx_mock):
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)

    with Client(max_retries=3, retry_backoff_factor=0.01) as client:
        with pytest.raises(GrokipediaServerError):
            client.search("test")


def test_user_agent_header(httpx_mock, search_response_data):
    httpx_mock.add_response(json=search_response_data)

    with Client(user_agent="Custom Agent") as client:
        client.search("test")

    request = httpx_mock.get_request()
    assert request.headers["User-Agent"] == "Custom Agent"


def test_build_url():
    with Client() as client:
        url = client._build_url("/api/search")
        assert url == "https://grokipedia.com/api/search"


def test_build_url_custom_base():
    with Client(base_url="https://custom.com") as client:
        url = client._build_url("/api/search")
        assert url == "https://custom.com/api/search"
