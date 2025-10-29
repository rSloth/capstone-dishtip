"""
google_review.py
-------------
Utilities for Google Reviews via the Google Maps Places API.

Includes:
- Review fetching (optionally language-filtered)
"""

from __future__ import annotations
import os
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv
from src.normalisation.normaliser import normalise_review

# ---- Logging ----
import logging
logger = logging.getLogger(__name__)

# ---- Config ----
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL_DETAILS = "https://maps.googleapis.com/maps/api/place/details/json"


def fetch_google_reviews(place_id: str, language: str = "en") -> List[Dict[str, Any]]:
    """
    Fetch and normalise Google reviews for a restaurant by its Place ID.
    Optionally specify a language (e.g., 'de' for German).
    Returns a list of normalised review dicts.
    """
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews",
        "language": language,
        "key": GOOGLE_API_KEY,
    }

    resp = requests.get(BASE_URL_DETAILS, params=params)
    data = resp.json()

    if resp.status_code != 200:
        logger.error(f"HTTP error {resp.status_code}: {data}")
        return []

    if "error_message" in data:
        logger.error(f"Google API error: {data['error_message']}")
        return []

    result = data.get("result", {})
    reviews = result.get("reviews", [])

    if not reviews:
        logger.info(f"No reviews found for {result.get('name', 'unknown place')}")
        return []

    logger.info(
        f"✅ Retrieved {len(reviews)} reviews for {result.get('name', 'restaurant')} "
        f"({language.upper()})"
    )

    # Normalise all reviews
    normalised_reviews = [normalise_review(r, "google") for r in reviews]

    # Optionally filter strictly by language field if needed
    filtered_reviews = [
        r for r in normalised_reviews if r.get("language") == language
    ] or normalised_reviews

    return filtered_reviews


# --- Helper functions ---
# Printing 5 reviews of a restaurant

def print_google_reviews(reviews: list):
    print(" ")
    print("- GOOGLE REVIEWS -")
    for r in reviews:
        print(f"{r['rating']}⭐: {r['text']}\n")
        print("-"*3)
    print("- END OF GOOGLE REVIEWS-")