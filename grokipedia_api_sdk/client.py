import logging
import random
import time
from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError

from .exceptions import (
    GrokipediaAPIError,
    GrokipediaBadRequestError,
    GrokipediaNetworkError,
    GrokipediaNotFoundError,
    GrokipediaRateLimitError,
    GrokipediaServerError,
    GrokipediaValidationError,
)
from .models import (
    ConstantsResponse,
    PageResponse,
    SearchResponse,
    StatsResponse,
)

logger = logging.getLogger(__name__)


class BaseClient:
    DEFAULT_BASE_URL = "https://grokipedia.com"
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Grokipedia Python SDK)"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        base_url: str | None = None,
        user_agent: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        retry_backoff_jitter: bool = True,
    ):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.retry_backoff_jitter = retry_backoff_jitter

        logger.info(
            f"Initializing Grokipedia client: base_url={self.base_url}, "
            f"timeout={self.timeout}s, max_retries={self.max_retries}"
        )

    def _get_headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent}

    def _build_url(self, endpoint: str) -> str:
        url = urljoin(self.base_url, endpoint)
        logger.debug(f"Built URL: {url}")
        return url

    def _calculate_backoff(self, attempt: int) -> float:
        backoff = self.retry_backoff_factor * (2**attempt)
        if self.retry_backoff_jitter:
            backoff += random.uniform(0, 0.1 * backoff)
        return backoff

    def _handle_http_error(self, response: httpx.Response) -> None:
        status_code = response.status_code
        try:
            error_body = response.text
        except Exception:
            error_body = None

        logger.error(f"HTTP error {status_code}: {error_body}")

        if status_code == 400:
            raise GrokipediaBadRequestError(
                f"Bad request: {error_body}", status_code=status_code, response_body=error_body
            )
        elif status_code == 404:
            raise GrokipediaNotFoundError(
                f"Resource not found: {error_body}", status_code=status_code, response_body=error_body
            )
        elif status_code == 429:
            raise GrokipediaRateLimitError(
                f"Rate limit exceeded: {error_body}", status_code=status_code, response_body=error_body
            )
        elif 500 <= status_code < 600:
            raise GrokipediaServerError(
                f"Server error: {error_body}", status_code=status_code, response_body=error_body
            )
        else:
            raise GrokipediaAPIError(
                f"HTTP error {status_code}: {error_body}",
                status_code=status_code,
                response_body=error_body,
            )

    def _parse_response(self, response: httpx.Response, model_class: type) -> Any:
        try:
            data = response.json()
            logger.debug(f"Parsing response into {model_class.__name__}")
            return model_class.model_validate(data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise GrokipediaValidationError(f"Failed to validate response: {e}") from e
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise GrokipediaValidationError(f"Failed to parse JSON response: {e}") from e


class Client(BaseClient):
    def __init__(
        self,
        base_url: str | None = None,
        user_agent: str | None = None,
        timeout: float = BaseClient.DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        retry_backoff_jitter: bool = True,
    ):
        super().__init__(
            base_url=base_url,
            user_agent=user_agent,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
            retry_backoff_jitter=retry_backoff_jitter,
        )
        self._client: httpx.Client | None = None

    def __enter__(self) -> "Client":
        self._client = httpx.Client(timeout=self.timeout, follow_redirects=True)
        logger.debug("Entered Client context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()
            logger.debug("Closed Client")
        self._client = None

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if not self._client:
            raise RuntimeError("Client must be used as a context manager")

        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        logger.debug(f"Making {method} request to {url}")

        for attempt in range(self.max_retries):
            try:
                response = self._client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                logger.info(f"Request successful: {method} {url} -> {response.status_code}")
                return response
            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    self._handle_http_error(e.response)
                if e.response.status_code in {429, 500, 502, 503, 504}:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(f"Retrying after {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(backoff)
                else:
                    self._handle_http_error(e.response)
            except (httpx.NetworkError, httpx.TimeoutException) as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Network error after {self.max_retries} attempts: {e}")
                    raise GrokipediaNetworkError(f"Network error: {e}") from e
                backoff = self._calculate_backoff(attempt)
                logger.warning(f"Network error, retrying after {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(backoff)

        raise GrokipediaNetworkError(f"Max retries ({self.max_retries}) exceeded")

    def search(self, query: str, limit: int = 12, offset: int = 0) -> SearchResponse:
        logger.info(f"Searching: query='{query}', limit={limit}, offset={offset}")
        url = self._build_url("/api/full-text-search")
        params = {"query": query, "limit": limit, "offset": offset}
        response = self._request("GET", url, params=params)
        return self._parse_response(response, SearchResponse)

    def get_page(self, slug: str, include_content: bool = True, validate_links: bool = False) -> PageResponse:
        logger.info(f"Getting page: slug='{slug}', include_content={include_content}")
        url = self._build_url("/api/page")
        params = {
            "slug": slug,
            "includeContent": str(include_content).lower(),
            "validateLinks": str(validate_links).lower(),
        }
        response = self._request("GET", url, params=params)
        return self._parse_response(response, PageResponse)

    def get_constants(self) -> ConstantsResponse:
        logger.info("Getting constants")
        url = self._build_url("/api/constants")
        response = self._request("GET", url)
        return self._parse_response(response, ConstantsResponse)

    def get_stats(self) -> StatsResponse:
        logger.info("Getting stats")
        url = self._build_url("/api/stats")
        response = self._request("GET", url)
        return self._parse_response(response, StatsResponse)


class AsyncClient(BaseClient):
    def __init__(
        self,
        base_url: str | None = None,
        user_agent: str | None = None,
        timeout: float = BaseClient.DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        retry_backoff_jitter: bool = True,
    ):
        super().__init__(
            base_url=base_url,
            user_agent=user_agent,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
            retry_backoff_jitter=retry_backoff_jitter,
        )
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "AsyncClient":
        self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        logger.debug("Entered AsyncClient context manager")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            logger.debug("Closed AsyncClient")
        self._client = None

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if not self._client:
            raise RuntimeError("AsyncClient must be used as an async context manager")

        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        logger.debug(f"Making async {method} request to {url}")

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                logger.info(f"Async request successful: {method} {url} -> {response.status_code}")
                return response
            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    self._handle_http_error(e.response)
                if e.response.status_code in {429, 500, 502, 503, 504}:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(f"Retrying after {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                    await self._async_sleep(backoff)
                else:
                    self._handle_http_error(e.response)
            except (httpx.NetworkError, httpx.TimeoutException) as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Network error after {self.max_retries} attempts: {e}")
                    raise GrokipediaNetworkError(f"Network error: {e}") from e
                backoff = self._calculate_backoff(attempt)
                logger.warning(f"Network error, retrying after {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                await self._async_sleep(backoff)

        raise GrokipediaNetworkError(f"Max retries ({self.max_retries}) exceeded")

    @staticmethod
    async def _async_sleep(seconds: float):
        import asyncio
        await asyncio.sleep(seconds)

    async def search(self, query: str, limit: int = 12, offset: int = 0) -> SearchResponse:
        logger.info(f"Async searching: query='{query}', limit={limit}, offset={offset}")
        url = self._build_url("/api/full-text-search")
        params = {"query": query, "limit": limit, "offset": offset}
        response = await self._request("GET", url, params=params)
        return self._parse_response(response, SearchResponse)

    async def get_page(self, slug: str, include_content: bool = True, validate_links: bool = False) -> PageResponse:
        logger.info(f"Async getting page: slug='{slug}', include_content={include_content}")
        url = self._build_url("/api/page")
        params = {
            "slug": slug,
            "includeContent": str(include_content).lower(),
            "validateLinks": str(validate_links).lower(),
        }
        response = await self._request("GET", url, params=params)
        return self._parse_response(response, PageResponse)

    async def get_constants(self) -> ConstantsResponse:
        logger.info("Async getting constants")
        url = self._build_url("/api/constants")
        response = await self._request("GET", url)
        return self._parse_response(response, ConstantsResponse)

    async def get_stats(self) -> StatsResponse:
        logger.info("Async getting stats")
        url = self._build_url("/api/stats")
        response = await self._request("GET", url)
        return self._parse_response(response, StatsResponse)
