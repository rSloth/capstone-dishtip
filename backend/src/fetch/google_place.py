"""
google_api.py
-------------
Utilities for fetching restaurant information via the Google Maps Places API.

Includes:
- Place ID lookup from name
- Restaurant metadata (name, address)
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



class Restaurant():
    def __init__(self, place_id):
        self.id = place_id
        
        #fetching restaurant info
        info = fetch_restaurant_info(place_id)
        self.name = info.get("name")
        self.address = info.get("address")
        self.id_check = info.get("id")
        
        #check if fetch worked
        if str(place_id).strip() != str(self.id_check).strip():
            raise ValueError(f"Restaurant ID mismatch: {place_id} vs {self.id_check}")
        
        #putting in placeholders for important later info
        self.google_url = ""
        self.homepage_url = ""
        self.menu_url = ""


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


# ---- Helper Functions (place ID is normally provided in the API call) ----
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