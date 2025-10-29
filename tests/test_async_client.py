import pytest

from grokipedia_api_sdk import AsyncClient
from grokipedia_api_sdk.exceptions import (
    GrokipediaBadRequestError,
    GrokipediaNotFoundError,
    GrokipediaRateLimitError,
    GrokipediaServerError,
)


@pytest.mark.asyncio
async def test_async_client_initialization():
    async with AsyncClient() as client:
        assert client.base_url == "https://grokipedia.com"
        assert client.timeout == 30.0
        assert client.max_retries == 3


@pytest.mark.asyncio
async def test_async_client_custom_config():
    async with AsyncClient(
        base_url="https://custom.example.com",
        timeout=60.0,
        max_retries=5,
        retry_backoff_factor=1.0,
    ) as client:
        assert client.base_url == "https://custom.example.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_backoff_factor == 1.0


@pytest.mark.asyncio
async def test_async_client_context_manager_required():
    client = AsyncClient()
    with pytest.raises(RuntimeError, match="must be used as an async context manager"):
        await client.search("test")


@pytest.mark.asyncio
async def test_async_search_success(httpx_mock, search_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/full-text-search?query=python&limit=10&offset=0",
        json=search_response_data,
    )

    async with AsyncClient() as client:
        response = await client.search("python", limit=10, offset=0)

    assert len(response.results) == 2
    assert response.results[0].slug == "Python"
    assert response.results[0].relevance_score == 3106.541015625


@pytest.mark.asyncio
async def test_async_get_page_success(httpx_mock, page_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/page?slug=Python&includeContent=true&validateLinks=false",
        json=page_response_data,
    )

    async with AsyncClient() as client:
        response = await client.get_page("Python", include_content=True)

    assert response.found is True
    assert response.page.slug == "Python"
    assert response.page.title == "Python"
    assert len(response.page.citations) == 1


@pytest.mark.asyncio
async def test_async_get_constants_success(httpx_mock, constants_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/constants",
        json=constants_response_data,
    )

    async with AsyncClient() as client:
        response = await client.get_constants()

    assert response.account_url == "https://accounts.x.ai"
    assert response.grok_com_url == "https://grok.com"
    assert response.app_env == "production"


@pytest.mark.asyncio
async def test_async_get_stats_success(httpx_mock, stats_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/stats",
        json=stats_response_data,
    )

    async with AsyncClient() as client:
        response = await client.get_stats()

    assert response.total_pages == "885279"
    assert response.index_size_bytes == "46898447051"


@pytest.mark.asyncio
async def test_async_bad_request_error(httpx_mock):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/full-text-search?query=test&limit=12&offset=0",
        status_code=400,
        json={"error": "Invalid query"},
    )

    async with AsyncClient() as client:
        with pytest.raises(GrokipediaBadRequestError) as exc_info:
            await client.search("test")

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_async_not_found_error(httpx_mock):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/page?slug=NonExistent&includeContent=true&validateLinks=false",
        status_code=404,
    )

    async with AsyncClient() as client:
        with pytest.raises(GrokipediaNotFoundError) as exc_info:
            await client.get_page("NonExistent")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_async_rate_limit_error(httpx_mock):
    httpx_mock.add_response(
        status_code=429,
        json={"error": "Rate limit exceeded"},
    )

    async with AsyncClient(max_retries=1) as client:
        with pytest.raises(GrokipediaRateLimitError) as exc_info:
            await client.search("test")

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_async_server_error(httpx_mock):
    httpx_mock.add_response(
        status_code=500,
        json={"error": "Internal server error"},
    )

    async with AsyncClient(max_retries=1) as client:
        with pytest.raises(GrokipediaServerError) as exc_info:
            await client.search("test")

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_async_retry_on_server_error(httpx_mock, search_response_data):
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(json=search_response_data)

    async with AsyncClient(max_retries=3, retry_backoff_factor=0.01) as client:
        response = await client.search("test")

    assert len(response.results) == 2


@pytest.mark.asyncio
async def test_async_retry_exhausted(httpx_mock):
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)

    async with AsyncClient(max_retries=3, retry_backoff_factor=0.01) as client:
        with pytest.raises(GrokipediaServerError):
            await client.search("test")


@pytest.mark.asyncio
async def test_async_user_agent_header(httpx_mock, search_response_data):
    httpx_mock.add_response(json=search_response_data)

    async with AsyncClient(user_agent="Custom Async Agent") as client:
        await client.search("test")

    request = httpx_mock.get_request()
    assert request.headers["User-Agent"] == "Custom Async Agent"


@pytest.mark.asyncio
async def test_async_multiple_requests(httpx_mock, search_response_data, page_response_data):
    httpx_mock.add_response(
        url="https://grokipedia.com/api/full-text-search?query=python&limit=12&offset=0",
        json=search_response_data,
    )
    httpx_mock.add_response(
        url="https://grokipedia.com/api/page?slug=Python&includeContent=true&validateLinks=false",
        json=page_response_data,
    )

    async with AsyncClient() as client:
        search_response = await client.search("python")
        page_response = await client.get_page("Python")

    assert len(search_response.results) == 2
    assert page_response.found is True
