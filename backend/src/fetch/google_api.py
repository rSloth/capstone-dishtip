"""
google_api.py
-------------
Fetches a restaurant's info and reviews from Google Places API,
and normalises them into simple dicts ready for downstream processing.

Returns:
    restaurant: Dict[str, Any]
    reviews: List[Dict[str, Any]]
"""

import os
import requests
import logging
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv
from src.normalisation.schema import Restaurant, Review

logger = logging.getLogger(__name__)

# ---- Config ----
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL_GOOGLEPLACES = "https://places.googleapis.com/v1/places/"
URL_FINDPLACE = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"


def fetch_google_places_data(place_id: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Fetch restaurant metadata + reviews for a given Google Place ID.
    Returns validated + flattened dicts, not Pydantic objects.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "id,"
            "displayName.text,"
            "formattedAddress,"
            "websiteUri,"
            "googleMapsUri,"
            "rating,"
            "reviews.rating,"
            "reviews.text.text,"
            "reviews.authorAttribution.displayName,"
            "reviews.publishTime,"
            "reviews.googleMapsUri,"
            "reviews.originalText.languageCode"
        ),
    }

    resp = requests.get(BASE_URL_GOOGLEPLACES + place_id, headers=headers)
    data = resp.json()

    if resp.status_code != 200:
        logger.error(f"HTTP error {resp.status_code}: {data}")
        return {}, []

    if "error_message" in data:
        logger.error(f"Google API error: {data['error_message']}")
        return {}, []

    display_name = (data.get("displayName") or {}).get("text", "Unknown")
    address = data.get("formattedAddress", "No address available")
    logger.info(f"\nFound restaurant: {display_name}\n{address}\n")

    # --- Normalize and validate ---
    restaurant = Restaurant(**data)
    restaurant_dict = restaurant.model_dump()

    reviews_data = data.get("reviews") or []
    logger.info(f"Retrieved {len(reviews_data)} reviews for {restaurant.name} ✅")

    if not reviews_data:
        logger.info(f"No reviews found for {restaurant.name}")
        return restaurant_dict, []

    reviews_models = [Review(**r) for r in reviews_data]
    reviews_dicts = [r.model_dump() for r in reviews_models]

    for r in reviews_dicts:
        r["source_type"] = "google"
        r["source"] = "Google Reviews"

    return restaurant_dict, reviews_dicts


# ---- Helper: find Place ID by restaurant name ----
def fetch_place_id(restaurant_name: str) -> Optional[str]:
    """Fetch the Google Place ID for a given restaurant name."""
    params = {
        "input": restaurant_name,
        "inputtype": "textquery",
        "fields": "place_id,name,formatted_address",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(URL_FINDPLACE, params=params)
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        logger.warning(f"No candidates found for '{restaurant_name}'")
        return None

    candidate = candidates[0]
    logger.info(
        f"\nFound restaurant: {candidate.get('name')}\n"
        f"{candidate.get('formatted_address')}\n"
        f"ID = {candidate.get('place_id')}\n"
    )
    return candidate.get("place_id")
