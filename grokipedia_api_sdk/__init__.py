import logging

from .client import AsyncClient, Client
from .exceptions import (
    GrokipediaAPIError,
    GrokipediaBadRequestError,
    GrokipediaError,
    GrokipediaNetworkError,
    GrokipediaNotFoundError,
    GrokipediaRateLimitError,
    GrokipediaServerError,
    GrokipediaValidationError,
)
from .models import (
    Citation,
    ConstantsResponse,
    Page,
    PageResponse,
    SearchResponse,
    SearchResult,
    StatsResponse,
)

__version__ = "0.1.0"

__all__ = [
    "Client",
    "AsyncClient",
    "GrokipediaError",
    "GrokipediaAPIError",
    "GrokipediaBadRequestError",
    "GrokipediaNotFoundError",
    "GrokipediaRateLimitError",
    "GrokipediaServerError",
    "GrokipediaNetworkError",
    "GrokipediaValidationError",
    "SearchResponse",
    "SearchResult",
    "PageResponse",
    "Page",
    "Citation",
    "ConstantsResponse",
    "StatsResponse",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
