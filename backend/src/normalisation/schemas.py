"""
basemodel.py
----------
Defines canonical data schemas and source field mappings used for normalization. They are not really used but might be useful later?
"""

from typing import List, Optional, Dict, Any

# -------- Canonical Review Schema --------
REVIEW_SCHEMA: Dict[str, Any] = {
    "id": None,            # optional unique ID (e.g. hash of text+source)
    "source_type": None,   # "google", "blog", etc.
    "source": None,        # source name displayed in rec box
    "author": None,        # reviewer/blogger name
    "text": None,          # review content
    "dishes": [],          # list of mentioned dish names
    "rating": None,        # numeric rating (1–5) or None
    "date": None,          # ISO 8601 date string
    "url": None,           # link to original review
    "author_url": None,    # reviewer profile link if available
    "language": None,      # ISO language code (e.g., "en", "de")
}

# -------- Dish Schema --------
DISH: Dict[str, Any] = {
    "name": None,          # dish name (normalized lowercase)
    "ranking": None,       # optional numeric rank (based on score)
}

# -------- Field Mapping per Source --------
REVIEW_MAPS: Dict[str, Dict[str, str]] = {
    "google": {
        "author_name": "author",
        "author_url": "author_url",
        "text": "text",
        "rating": "rating",
        "time": "date",
        "url": "url",
        "language": "language",
    },
    "blog": {
        "provider": "author",
        "description": "text",
        "datePublished": "date",
        "url": "url",
        # "ratingValue": "rating",   # include if your blogs have explicit ratings
        # "inLanguage": "language",
    },
}


# -------- Recommendation Schema --------
# Recommendation format returned by FastAPI

REC_SCHEMA = {
    "dish_name": None,
    "author": None,
    "source": None,
    "timestamp": None,
    "review_link": None,
    "ranking": None,
}
