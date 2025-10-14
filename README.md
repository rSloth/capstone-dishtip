🍴 DishTip — Backend

**DishTip** is an AI-powered backend that helps users instantly discover a restaurant’s *best dishes* — by analyzing real customer reviews and blog posts.

Simply select a restaurant, and DishTip uses live data from Google Reviews and curated food blogs to identify the most-loved dishes. It’s your personal AI food scout that finds what’s truly worth ordering. 😋

---

## Overview

The **DishTip Backend** handles:

* 🌐 Fetching and aggregating Google and blog review data
* 🧠 Applying NLP models for sentiment and keyword extraction
* 📊 Ranking dishes by sentiment, mention frequency, and popularity
* ⚙️ Serving recommendations via a clean REST API (FastAPI)

---

## 🧩 System Architecture

```
User → Frontend (Search Restaurant)
              ↓
        FastAPI Backend
              ↓
    Google Reviews & Blog APIs
              ↓
     NLP Model (Sentiment + NER)
              ↓
     Dish Ranking & Recommendation
              ↓
          JSON Response
```

**Flow Summary**

1. User searches a restaurant (via Google Maps API).
2. Backend fetches Google reviews + matching blog articles.
3. NLP models extract dish mentions and sentiment.
4. Dishes are ranked and returned as top 3–5 recommendations.

---

## 🧠 Tech Stack

| Layer                  | Technology                                       | Purpose                             |
| ---------------------- | ------------------------------------------------ | ----------------------------------- |
| **Framework**          | FastAPI                                          | Lightweight, async web API          |
| **NLP / Sentiment**    | Hugging Face Transformers (BERT, RoBERTa), VADER | Extract dish mentions and sentiment |
| **APIs**               | Google Places API, Bing Web Search API           | Fetch reviews & blog content        |
| **Data Handling**      | Pandas, NumPy                                    | Clean, aggregate, and rank data     |
| **Caching (optional, probably not implementing lets )** | Redis                                            | Avoid redundant API calls           |
| **Database** (also not sure about that)           | SQLite / PostgreSQL                              | Cache restaurant & dish results     |
| **Deployment**         | Docker + Render / Railway                        | Cloud hosting for backend           |

---

## 📡 API Endpoints (Example)

| Method | Endpoint                           | Description                                |
| ------ | ---------------------------------- | ------------------------------------------ |
| `GET`  | `/restaurant/search`               | Search for restaurants via Google Maps API |
| `GET`  | `/restaurant/{id}/reviews`         | Fetch and analyze Google reviews           |
| `GET`  | `/restaurant/{id}/recommendations` | Return top 3–5 recommended dishes          |
| `GET`  | `/health`                          | Health check endpoint                      |

**Example response:**

```json
{
  "restaurant": "Luigi's Trattoria",
  "top_dishes": [
    {
      "name": "Spaghetti Carbonara",
      "score": 9.4,
      "mentions": 52,
      "sentiment": 0.91,
      "review_snippet": "Best carbonara in town — creamy and rich!"
    },
    {
      "name": "Tiramisu",
      "score": 8.9,
      "mentions": 31,
      "sentiment": 0.88,
      "review_snippet": "So fluffy and perfectly balanced."
    },
    {
      "name": "Margherita Pizza",
      "score": 8.5,
      "mentions": 24,
      "sentiment": 0.83,
      "review_snippet": "Classic and flavorful, perfect crust."
    }
  ]
}
```

---

## 🧱 Folder Structure

```
dishtip-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_restaurant.py  # endpoints for /restaurant/*
│   │   └── routes_health.py      # health check
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py             # environment & settings
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── google_service.py     # fetch Google Reviews
│   │   ├── blog_service.py       # fetch blog articles (via Bing API or RSS)
│   │   ├── nlp_service.py        # sentiment + entity extraction
│   │   ├── ranking_service.py    # combine metrics and rank dishes
│   │   └── caching_service.py    # optional Redis caching
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_utils.py         # text cleaning, tokenization
│   │   ├── scoring_utils.py      # scoring helper functions
│   │   └── api_utils.py          # request/response helpers
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLAlchemy connection
│   │   └── crud.py               # cached query operations
│   │
│   └── tests/
│       ├── test_api.py
│       ├── test_nlp.py
│       └── test_ranking.py
│
├── .env.example
├── requirements.txt
├── Dockerfile
├── README.md
└── LICENSE
```

---

## 🧰 Installation

```bash
git clone https://github.com/<yourusername>/dishtip-backend.git
cd dishtip-backend

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in your Google/Bing API keys

uvicorn app.main:app --reload
```

---

## 🔐 Environment Variables

| Variable         | Description                                                                       |
| ---------------- | --------------------------------------------------------------------------------- |
| `GOOGLE_API_KEY` | Google Maps / Places API key                                                      |
| `BING_API_KEY`   | Bing Web Search API key                                                           |
| `DATABASE_URL`   | PostgreSQL or SQLite URL                                                          |
| `CACHE_URL`      | Redis URL (optional)                                                              |
| `NLP_MODEL`      | Name of Hugging Face model (default: `cardiffnlp/twitter-roberta-base-sentiment`) |

---

## 🧮 Scoring Formula (Simplified)

Each dish’s final score combines:

```
DishScore = (0.5 × SentimentScore) + (0.3 × MentionFrequency) + (0.2 × AvgRating)
```

This can be adjusted dynamically in config to emphasize sentiment, popularity, or consistency.

---

## 📈 Future Enhancements

* 🍳 Personalized recommendations (based on dietary preferences)
* 🏙️ Location-based suggestions (top dishes near you)
* 🧾 Multi-source review integration (TripAdvisor, Zomato, Yelp)
* 💬 AI chat layer (“What’s the best spicy dish here?”)

---

## 🧑‍🍳 Credits

Built with ❤️ using Python, FastAPI, and Hugging Face NLP.
Part of the **DishTip** project — where **data meets delicious.**

---

Would you like me to now generate:

* a **`requirements.txt`** (with the exact libraries you’ll need),
* and a sample **`.env.example`** file (so it’s plug-and-play for your repo)?
