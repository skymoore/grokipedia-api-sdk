# Grokipedia API SDK

A modern Python SDK for interacting with the Grokipedia API. Built with `httpx` and `pydantic` for type safety, performance, and ease of use.

## Features

- **🔄 Sync & Async Support** - Use synchronous `Client` or asynchronous `AsyncClient`
- **🔁 Automatic Retries** - Exponential backoff with jitter for transient failures
- **✅ Type Safety** - Full type hints and Pydantic models for validation
- **📝 Comprehensive Logging** - Debug and info logging throughout
- **⚡ Built on httpx** - Modern HTTP client with HTTP/2 support
- **🛡️ Exception Handling** - Granular exception types for different error scenarios

## Installation

```bash
pip install grokipedia-api-sdk
```

Or with uv:

```bash
uv add grokipedia-api-sdk
```

## Quick Start

### Synchronous Usage

```python
from grokipedia_api_sdk import Client

with Client() as client:
    results = client.search("python programming", limit=10)
    
    for result in results.results:
        print(f"{result.title} (relevance: {result.relevance_score})")
        print(f"  URL: https://grokipedia.com/page/{result.slug}")
        print(f"  Views: {result.view_count}")
        print()
    
    article = client.get_page("Python", include_content=True)
    print(f"Title: {article.page.title}")
    print(f"Content length: {len(article.page.content)} chars")
    print(f"Citations: {len(article.page.citations)}")
```

### Asynchronous Usage

```python
import asyncio
from grokipedia_api_sdk import AsyncClient

async def main():
    async with AsyncClient() as client:
        results = await client.search("python programming", limit=10)
        
        for result in results.results:
            print(f"{result.title} (relevance: {result.relevance_score})")
        
        article = await client.get_page("Python", include_content=True)
        print(f"Title: {article.page.title}")

asyncio.run(main())
```

## API Reference

### Client Configuration

Both `Client` and `AsyncClient` support the following initialization parameters:

```python
client = Client(
    base_url="https://grokipedia.com",
    user_agent="Custom User Agent",
    timeout=30.0,
    max_retries=3,
    retry_backoff_factor=0.5,
    retry_backoff_jitter=True,
)
```

**Parameters:**
- `base_url` (str, optional): Base URL for the API. Default: `"https://grokipedia.com"`
- `user_agent` (str, optional): User-Agent header value. Default: `"Mozilla/5.0 (Grokipedia Python SDK)"`
- `timeout` (float, optional): Request timeout in seconds. Default: `30.0`
- `max_retries` (int, optional): Maximum number of retry attempts. Default: `3`
- `retry_backoff_factor` (float, optional): Backoff multiplier for retries. Default: `0.5`
- `retry_backoff_jitter` (bool, optional): Add random jitter to backoff. Default: `True`

### Search API

Search for articles using full-text search:

```python
results = client.search(
    query="python programming",
    limit=12,
    offset=0
)
```

**Parameters:**
- `query` (str): Search query
- `limit` (int, optional): Maximum number of results. Default: `12`
- `offset` (int, optional): Pagination offset. Default: `0`

**Returns:** `SearchResponse`

**Response Model:**
```python
class SearchResponse:
    results: list[SearchResult]

class SearchResult:
    slug: str
    title: str
    snippet: str
    relevance_score: float
    view_count: str
    title_highlights: list
    snippet_highlights: list
```

### Page API

Retrieve full article content:

```python
page = client.get_page(
    slug="Python",
    include_content=True,
    validate_links=False
)
```

**Parameters:**
- `slug` (str): Article slug (URL-safe identifier)
- `include_content` (bool, optional): Include full article content. Default: `True`
- `validate_links` (bool, optional): Validate linked pages. Default: `False`

**Returns:** `PageResponse`

**Response Model:**
```python
class PageResponse:
    page: Page
    found: bool

class Page:
    slug: str
    title: str
    content: str
    description: str
    citations: list[Citation]
    images: list
    fixed_issues: list
    metadata: dict
    stats: dict
    linked_pages: list

class Citation:
    id: str
    title: str
    description: str
    url: str
    favicon: str
```

### Constants API

Get application configuration:

```python
constants = client.get_constants()
print(f"Account URL: {constants.account_url}")
print(f"Grok URL: {constants.grok_com_url}")
print(f"Environment: {constants.app_env}")
```

**Returns:** `ConstantsResponse`

**Response Model:**
```python
class ConstantsResponse:
    account_url: str
    grok_com_url: str
    app_env: str
```

### Stats API

Get global statistics:

```python
stats = client.get_stats()
print(f"Total Pages: {stats.total_pages}")
print(f"Index Size: {stats.index_size_bytes} bytes")
print(f"Timestamp: {stats.stats_timestamp}")
```

**Returns:** `StatsResponse`

**Response Model:**
```python
class StatsResponse:
    total_pages: str
    total_views: int
    avg_views_per_page: float
    index_size_bytes: str
    stats_timestamp: str
```

## Error Handling

The SDK provides granular exception types for different error scenarios:

```python
from grokipedia_api_sdk import (
    Client,
    GrokipediaError,
    GrokipediaAPIError,
    GrokipediaBadRequestError,
    GrokipediaNotFoundError,
    GrokipediaRateLimitError,
    GrokipediaServerError,
    GrokipediaNetworkError,
    GrokipediaValidationError,
)

with Client() as client:
    try:
        results = client.search("python")
    except GrokipediaNotFoundError as e:
        print(f"Resource not found: {e}")
    except GrokipediaRateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        print(f"Status code: {e.status_code}")
    except GrokipediaNetworkError as e:
        print(f"Network error: {e}")
    except GrokipediaAPIError as e:
        print(f"API error: {e}")
        print(f"Status code: {e.status_code}")
        print(f"Response body: {e.response_body}")
    except GrokipediaError as e:
        print(f"General error: {e}")
```

**Exception Hierarchy:**
```
GrokipediaError (base)
├── GrokipediaAPIError
│   ├── GrokipediaBadRequestError (400)
│   ├── GrokipediaNotFoundError (404)
│   ├── GrokipediaRateLimitError (429)
│   └── GrokipediaServerError (5xx)
├── GrokipediaNetworkError
└── GrokipediaValidationError
```

## Logging

Enable logging to see debug information:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

with Client() as client:
    results = client.search("python")
```

**Log Levels:**
- `DEBUG`: Detailed request/response information, URL building, parsing
- `INFO`: High-level operations (search started, page fetched, etc.)
- `WARNING`: Retry attempts
- `ERROR`: HTTP errors, validation errors

## Advanced Usage

### Custom Retry Configuration

```python
client = Client(
    max_retries=5,
    retry_backoff_factor=1.0,
    retry_backoff_jitter=True,
)
```

The retry logic uses exponential backoff with the formula:
```
backoff = retry_backoff_factor * (2 ** attempt)
```

With jitter enabled, a small random delay is added to prevent thundering herd issues.

### Pagination

```python
with Client() as client:
    page = 0
    limit = 20
    all_results = []
    
    while True:
        response = client.search("python", limit=limit, offset=page * limit)
        all_results.extend(response.results)
        
        if len(response.results) < limit:
            break
        
        page += 1
    
    print(f"Total results: {len(all_results)}")
```

### Search and Retrieve Workflow

```python
with Client() as client:
    search_results = client.search("machine learning", limit=5)
    
    for result in search_results.results:
        article = client.get_page(result.slug, include_content=True)
        print(f"\n=== {article.page.title} ===")
        print(article.page.content[:500])
        print(f"\nCitations: {len(article.page.citations)}")
```

## Development

### Setup

```bash
git clone https://github.com/yourusername/grokipedia-api-sdk.git
cd grokipedia-api-sdk
uv sync
```

### Testing

```bash
uv run pytest
```

### Type Checking

```bash
uv run mypy grokipedia_api_sdk
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

Built on top of the undocumented Grokipedia internal API. API format may change without notice.
