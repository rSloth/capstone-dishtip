"""
schema.py
----------
Defines canonical data schemas and source field mappings used for normalization.
"""

from typing import Dict, Any

# -------- Canonical Review Schema --------
REVIEW_SCHEMA: Dict[str, Any] = {
    "id": None,            # optional unique ID (e.g. hash of text+source)
    "source": None,        # "google", "blog", etc.
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

# -------- (Optional) Tip Schema --------
# TIP_SCHEMA defines the structure used when presenting ranked dish insights
# in the DishTip UI layer. You can keep it separate from raw review schema.
#
# TIP_SCHEMA = {
#     "dish_name": None,
#     "review_text": None,
#     "excerpt": None,
#     "author": None,
#     "source": None,
#     "review_link": None,
#     "pos_score": None,
#     "ranking": None,
# }