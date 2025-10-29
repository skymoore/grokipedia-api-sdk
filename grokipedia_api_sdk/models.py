from typing import Any
from pydantic import BaseModel, Field, field_validator


class SearchResult(BaseModel):
    title_highlights: list[Any] = Field(alias="titleHighlights", default_factory=list)
    snippet_highlights: list[Any] = Field(alias="snippetHighlights", default_factory=list)
    slug: str
    title: str
    snippet: str
    relevance_score: float = Field(alias="relevanceScore")
    view_count: int = Field(alias="viewCount")


class SearchResponse(BaseModel):
    results: list[SearchResult]


class Citation(BaseModel):
    id: str
    title: str
    description: str
    url: str
    favicon: str = ""


class Page(BaseModel):
    slug: str
    title: str
    content: str = ""
    description: str = ""
    citations: list[Citation] = Field(default_factory=list)
    images: list[Any] = Field(default_factory=list)
    fixed_issues: list[Any] = Field(alias="fixedIssues", default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    stats: dict[str, Any] = Field(default_factory=dict)
    linked_pages: list[Any] = Field(alias="linkedPages", default_factory=list)
    
    @field_validator("citations", "images", "fixed_issues", "linked_pages", mode="before")
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
    
    @field_validator("metadata", "stats", mode="before")
    @classmethod
    def convert_none_to_dict(cls, v):
        return v if v is not None else {}


class PageResponse(BaseModel):
    page: Page
    found: bool


class ConstantsResponse(BaseModel):
    account_url: str = Field(alias="accountUrl")
    grok_com_url: str = Field(alias="grokComUrl")
    app_env: str = Field(alias="appEnv")


class StatsResponse(BaseModel):
    total_pages: str = Field(alias="totalPages")
    total_views: int = Field(alias="totalViews")
    avg_views_per_page: float = Field(alias="avgViewsPerPage")
    index_size_bytes: str = Field(alias="indexSizeBytes")
    stats_timestamp: str = Field(alias="statsTimestamp")
