import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def form_recommendations(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Combines all extracted dishes from review data into a flat, sorted list.

    Each dish entry includes metadata (ranking, author, source, timestamp, etc.).
    Ensures consistent structure for downstream use in ranking or display.

    Args:
        reviews: List of normalized review dictionaries, each possibly containing a "dishes" list.

    Returns:
        A list of dish recommendation dictionaries, sorted by ranking (ascending).
    """

    recommendations: List[Dict[str, Any]] = []

    for review in reviews:
        source = review.get("source", "google")
        author = review.get("author")
        url = review.get("url")
        timestamp = review.get("timestamp")

        dishes = review.get("dishes", [])
        if not dishes:
            continue

        for dish in dishes:
            recommendations.append({
                "dish_name": dish.get("name"),
                "ranking": dish.get("ranking"),
                "author": author,
                "source": source,
                "timestamp": timestamp,
                "review_link": url,
            })

    # Sort: dishes with None rankings go last
    recommendations.sort(
        key=lambda rec: (rec["ranking"] is None, -(rec["ranking"] or 0))
    )

    logger.info(f"🍽️ Generated {len(recommendations)} recommendations from {len(reviews)} reviews.")
    logger.info(f"🍽️ Sorted dish scores are {[rec.get('ranking','') for rec in recommendations]}.")
    
    return recommendations
