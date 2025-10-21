# Retrieving Google Reviews using Place ID

import requests
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Function to get place ID from restaurant name
def get_place_id(restaurant_name: str):
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
    return place_id, place_name, place_address if data.get("candidates") else None

#Function to get reviews using place ID
def get_place_reviews(place_id: str):
    """
    Fetches reviews for a given restaurant using its Google Maps Place ID.
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
    return reviews