"""
scoring.py
----------
Provides logic for assigning numerical scores to dishes. Scores are based on several 
heuristics, including the source type (Google vs. blog), author name quality, and 
length of dish name.
"""

# import
import logging
logger = logging.getLogger(__name__)
from typing import Dict, List, Any

# helper function
def count_words(string:str) -> int:
    """
    Counts words in a given string.
    """
    word_count = len(string.split())
    return word_count


# main function
def assign_dish_scores(reviews: List[Dict[str, Any]]) -> None:
    """
    Assigns scores to dishes based on review source, author name, and dish name length.

    Google reviews get a small author bonus; blog reviews start with higher base points.
    Longer dish names earn extra points up to a cap. Logs all scoring steps.

    Args:
        reviews: List of review dicts with 'source_type', 'author', and 'dishes'.
    """
    
    # constants
    google_default_points = 0
    blog_default_points = 1000
    
    logger.info("=" * 16 + " SCORING " +"=" * 15 )

    if any(
        dish.get("ranking") is not None
        for review in reviews
        if review.get("dishes")
        for dish in review["dishes"]
    ):
        logger.warning("This review set already contains ranked dishes. Skipping scoring.")
    else:
        for i, review in enumerate(reviews):
                # variables
                final_score: int = 0
                author_p: int = 0
                source_p: int = 0
                dish_name_p: int = 0

                # scoring source type
                if review.get("source_type") == "google" and review.get("dishes"):
                    source_p = google_default_points
                    if count_words(review.get("author","")) > 1 and len(review.get("author","")) > 5:
                        author_p = 10 # rewards real min. two word names for google reviewrs

                elif review.get("source_type") == "blog" and review.get("dishes"): 
                    source_p = blog_default_points

                # scoring dish based on number of words         
                for dish in review["dishes"]:
                    dish_name_p = 0
                    if dish.get("ranking") is None:
                        dish_name = dish.get("name")
                        word_count = len(dish_name.split())
                        dish_name_p = min(word_count**3, 50) # reward more words exponentially with a cap on 4
                    
                        final_score = author_p + source_p + dish_name_p
                        dish["ranking"] = final_score
                        logger.info(f"SCORE: Review #{i+1} -- {final_score}p -- {dish.get('name')} -- ({source_p} +{author_p} +{dish_name_p})")  
                logger.info("=" * 40)