from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

# backend/main.py
from src.fetch.google_reviews import fetch_google_reviews 
from src.fetch.google_place import Restaurant
from src.nlp.dish_extractor import extract_dishes
from src.ranking.functions import assign_rankings
from src.recommendation.recs import form_recommendations

app = FastAPI(title="DishTip Backend", version="1.0", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can later restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DishRequest(BaseModel):
    ingredients: list[str]

@app.get("/")
def root():
    return {"message": "Dishtip API is ready to serve hot tea and tips"}

@app.get("/recommendations/{place_id}")
def get_recommendations(place_id: str):
    try:
        reviews = fetch_google_reviews(place_id)
        reviews = extract_dishes(reviews, True)
        assign_rankings(reviews, True)
        recommendations = form_recommendations(reviews)
        return {"recommendations": recommendations}
    except Exception as e:
        traceback.print_exc()  # This prints the real error in your terminal
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/restaurant_info/{place_id}")
def get_rest_info(place_id: str):
    restaurant = Restaurant(place_id)

    return {"restaurant_info": restaurant}



