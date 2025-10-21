REVIEW_SCHEMA = {
    "source": None,        # 'google', 'blog', 'yelp', etc.
    "restaurant": None,    # restaurant name
    "author": None,        # reviewer/blogger name
    "text": None,          # review text content
    "rating": None,        # numeric rating (1–5) or None
    "date": None,          # ISO date string
    "url": None,           # source URL if available
    "language": None,      # optional: helps later with translation
    "id": None,            # optional: unique id (e.g. hash of text+source)
}

REVIEW_MAPS = {
    "google": {
        "author_name": "author",
        "text": "text",
        "rating": "rating",
        "time": "date",
        "url": "url",
        "language": "language",
        "author_url": "url",

    },
    "blog": {
        "provider": "author",
        "description": "text",
        "datePublished": "date",
        "url": "url",
    },
}

# TIP_SCHEMA = {
#    "dish name": None,
#    "review_text": "from_schema",
#    "excerpt": None,
#    "author": "from_schema",
#    "source": "google reviews",
#    "review_link": "from_schema",
#    "pos_score": 0.9,
#    "ranking": 4
# }