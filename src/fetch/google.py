# Retrieving Google Reviews using Place ID

import requests
from dotenv import load_dotenv
import os

# Importing the normalisation function
from src.normalise.normaliser import normalise_review

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Function to get place ID from restaurant name
def get_place_id(restaurant_name: str):
    """
    Input a restaurant name. Fetches and returns ID, Google name and address.
    """
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": restaurant_name,
        "inputtype": "textquery",
        "fields": "place_id,name,formatted_address",
        "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    place_id = data["candidates"][0]["place_id"]
    place_name = data["candidates"][0]["name"]
    place_address = data["candidates"][0]["formatted_address"]
    print(f"--- RESTAURANT DETAILS ---\n{place_name}\n{place_address}\n{place_id}\n--- END ---\n ")
    return place_id if data.get("candidates") else None

# Function to get place name and address using place ID
def get_rest_info(place_id: str) -> dict:
    """
    Retrieve a place's name and formatted address from Google Places Details API.
    Returns a dict like:
    {"name": "Place Name", "address": "123 Main St, City", "id": ID}
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,place_id",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        raise ValueError(f"API error: {data.get('status')} - {data.get('error_message')}")

    result = data.get("result", {})
    return {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "id": result.get("place_id")
    }



#Function to get reviews using place ID
def get_place_reviews(place_id: str):
    """
    Fetches reviews for a given restaurant using its Google Maps Place ID and returns it normalised according to the schema in a dictionary.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        print("❌ Error:", data)
        return []

    if "error_message" in data:
        print("⚠️ Google API error:", data["error_message"])
        return []

    result = data.get("result", {})
    reviews = result.get("reviews", [])
    print(f"✅ Google reviews retrieved, found {len(reviews)} reviews for {result.get('name', 'restaurant')}\n ")

    # normalising the reviews
    r_norm_rev = []

    for r in reviews:
        r_norm_rev.append(normalise_review(r, "google"))
    
    return r_norm_rev



def get_place_reviews_de(place_id: str, language: str = "de"):
    """
    Fetches reviews for a given restaurant using its Google Maps Place ID.
    If available, returns reviews in the specified language (e.g., 'de' for German).
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews,url",
        "language": language,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        print("❌ Google API error:", data.get("error_message"))
        return []

    result = data.get("result", {})
    reviews = result.get("reviews", [])

    # Keep only German reviews if they explicitly have 'language': 'de'
    german_reviews = [r for r in reviews if r.get("language") == "de"]

    return german_reviews or reviews  # fall back to all if no German ones