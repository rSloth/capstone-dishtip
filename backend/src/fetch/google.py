"""
google_api.py
-------------
Utilities for fetching restaurant information and Google Reviews
via the Google Maps Places API.

Includes:
- Place ID lookup from name
- Restaurant metadata (name, address)
- Review fetching (optionally language-filtered)
"""

from __future__ import annotations
import os
import requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from src.normalisation.normaliser import normalise_review

# ---- Logging ----
import logging
logger = logging.getLogger(__name__)

# ---- Config ----
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_URL_FINDPLACE = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
BASE_URL_DETAILS = "https://maps.googleapis.com/maps/api/place/details/json"

# ---- Core Functions ----
def fetch_place_id(restaurant_name: str) -> Optional[str]:
    """
    Fetch the Google Place ID for a given restaurant name.
    Returns the place_id if found, otherwise None.
    """
    params = {
        "input": restaurant_name,
        "inputtype": "textquery",
        "fields": "place_id,name,formatted_address",
        "key": GOOGLE_API_KEY,
    }
    response = requests.get(BASE_URL_FINDPLACE, params=params)
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        logger.warning(f"No candidates found for '{restaurant_name}'")
        return None

    candidate = candidates[0]
    logger.info(
        f"\n Found restaurant: {candidate.get('name')}\n"
        f"{candidate.get('formatted_address')}\n"
        f"ID = {candidate.get('place_id')}\n"
    )
    return candidate.get("place_id")


def fetch_restaurant_info(place_id: str) -> Dict[str, Optional[str]]:
    """
    Retrieve basic metadata for a restaurant by Place ID.
    Returns: {"name": ..., "address": ..., "id": ...}
    """
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,place_id",
        "key": GOOGLE_API_KEY,
    }

    resp = requests.get(BASE_URL_DETAILS, params=params)
    data = resp.json()

    if data.get("status") != "OK":
        raise ValueError(f"Google API error: {data.get('status')} - {data.get('error_message')}")

    result = data.get("result", {})
    return {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "id": result.get("place_id"),
    }


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