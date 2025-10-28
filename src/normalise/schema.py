REVIEW_SCHEMA = {
    "id": None,            # optional: unique id (e.g. hash of text+source)
    "source": None,        # 'google', 'blog', 'yelp', etc.
    "author": None,        # reviewer/blogger name
    "text": None,          # review text content
    "dishes": None,        # list of positively mentioned dish names in the review
    "google_rating": None, # numeric rating (1–5) or None
    "date": None,          # ISO date string
    "url": None,           # source URL if available
    "language": None,      # optional: helps later with translation
}

DISH = {
    "name": None,
    "ranking": None
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