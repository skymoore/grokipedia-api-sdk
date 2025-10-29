import pytest


@pytest.fixture
def search_response_data():
    return {
        "results": [
            {
                "titleHighlights": [],
                "snippetHighlights": [],
                "slug": "Python",
                "title": "Python",
                "snippet": "Python is a high-level <em>programming</em> language",
                "relevanceScore": 3106.541015625,
                "viewCount": "90358",
            },
            {
                "titleHighlights": [],
                "snippetHighlights": [],
                "slug": "Indian_python",
                "title": "Indian python",
                "snippet": "The Indian <em>python</em> is a large snake species",
                "relevanceScore": 1907.3299560546875,
                "viewCount": "124804",
            },
        ]
    }


@pytest.fixture
def page_response_data():
    return {
        "page": {
            "slug": "Python",
            "title": "Python",
            "content": "# Python\n\nPython is a high-level programming language...",
            "description": "Python is a programming language",
            "citations": [
                {
                    "id": "1",
                    "title": "Python.org",
                    "description": "Official Python website",
                    "url": "https://www.python.org",
                    "favicon": "",
                }
            ],
            "images": [],
            "fixedIssues": [],
            "metadata": {},
            "stats": {},
            "linkedPages": [],
        },
        "found": True,
    }


@pytest.fixture
def constants_response_data():
    return {
        "accountUrl": "https://accounts.x.ai",
        "grokComUrl": "https://grok.com",
        "appEnv": "production",
    }


@pytest.fixture
def stats_response_data():
    return {
        "totalPages": "885279",
        "totalViews": 0,
        "avgViewsPerPage": 0,
        "indexSizeBytes": "46898447051",
        "statsTimestamp": "1761732694",
    }
