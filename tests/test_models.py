import pytest
from pydantic import ValidationError

from grokipedia_api_sdk.models import (
    Citation,
    ConstantsResponse,
    Page,
    PageResponse,
    SearchResponse,
    SearchResult,
    StatsResponse,
)


def test_search_result_model():
    data = {
        "titleHighlights": [],
        "snippetHighlights": [],
        "slug": "Python",
        "title": "Python",
        "snippet": "Python is a programming language",
        "relevanceScore": 100.5,
        "viewCount": "12345",
    }
    result = SearchResult.model_validate(data)
    assert result.slug == "Python"
    assert result.title == "Python"
    assert result.relevance_score == 100.5
    assert result.view_count == "12345"


def test_search_response_model(search_response_data):
    response = SearchResponse.model_validate(search_response_data)
    assert len(response.results) == 2
    assert response.results[0].slug == "Python"
    assert response.results[1].slug == "Indian_python"


def test_search_result_missing_required_field():
    data = {
        "slug": "Python",
        "title": "Python",
    }
    with pytest.raises(ValidationError):
        SearchResult.model_validate(data)


def test_citation_model():
    data = {
        "id": "1",
        "title": "Test Citation",
        "description": "A test citation",
        "url": "https://example.com",
        "favicon": "favicon.ico",
    }
    citation = Citation.model_validate(data)
    assert citation.id == "1"
    assert citation.title == "Test Citation"
    assert citation.url == "https://example.com"


def test_page_model(page_response_data):
    page = Page.model_validate(page_response_data["page"])
    assert page.slug == "Python"
    assert page.title == "Python"
    assert page.content.startswith("# Python")
    assert len(page.citations) == 1
    assert page.citations[0].url == "https://www.python.org"


def test_page_response_model(page_response_data):
    response = PageResponse.model_validate(page_response_data)
    assert response.found is True
    assert response.page.slug == "Python"


def test_page_model_with_defaults():
    data = {
        "slug": "Test",
        "title": "Test Page",
    }
    page = Page.model_validate(data)
    assert page.slug == "Test"
    assert page.title == "Test Page"
    assert page.content == ""
    assert page.description == ""
    assert page.citations == []
    assert page.images == []
    assert page.metadata == {}


def test_constants_response_model(constants_response_data):
    response = ConstantsResponse.model_validate(constants_response_data)
    assert response.account_url == "https://accounts.x.ai"
    assert response.grok_com_url == "https://grok.com"
    assert response.app_env == "production"


def test_stats_response_model(stats_response_data):
    response = StatsResponse.model_validate(stats_response_data)
    assert response.total_pages == "885279"
    assert response.total_views == 0
    assert response.avg_views_per_page == 0
    assert response.index_size_bytes == "46898447051"
    assert response.stats_timestamp == "1761732694"


def test_stats_response_validation_error():
    data = {
        "totalPages": "885279",
    }
    with pytest.raises(ValidationError):
        StatsResponse.model_validate(data)
