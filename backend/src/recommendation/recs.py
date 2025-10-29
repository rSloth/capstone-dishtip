def form_recommendations(reviews):
    """
    Extracts all dishes from a list of reviews and returns
    them as a flat, sorted list of dicts with metadata.
    """
    recommendations = []

    for review in reviews:
        source = review.get("source")
        author = review.get("author")
        url = review.get("url")
        date = review.get("date")

        for dish in review.get("dishes", []):
            recommendations.append({
                "dish_name": dish.get("name"),
                "ranking": dish.get("ranking"),
                "author": author,
                "source": source,
                "timestamp": date,
                "review_link": url,
            })

    # Sort by ranking (None values last)
    recommendations.sort(key=lambda d: (d["ranking"] is None, d["ranking"]))
    return recommendations
