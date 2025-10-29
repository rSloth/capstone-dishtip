# 🍴 DishTip

**DishTip** is an AI-powered backend that helps users instantly discover a restaurant’s *best dishes* by analyzing real customer reviews.
It fetches live Google review data, extracts dish mentions using an NLP model, and ranks them by frequency and source validity.
It’s your AI food scout that tells you *what to order* before you even sit down. 😋

---
## 🧠 How to locally run the app

If you want to run both frontend and backend, from the project root:

```bash
# Terminal 1 (backend)
fastapi dev backend/main.py

# Terminal 2 (frontend)
npm --prefix frontend run dev
```

Frontend → http://localhost:5173
Backend → http://127.0.0.1:8000

---

## 🧠 Overview

The **DishTip Backend** is built with **FastAPI** and serves as the engine behind the DishTip web app.
It handles:

* 🌐 Fetching Google Place and review data
* 🧠 Extracting dish mentions with a fine-tuned **Flan-T5** model
* 📊 Ranking and returning the top dishes per restaurant
* ⚙️ Serving clean JSON responses to the frontend

---

## 🧩 System Architecture

```
User → React Frontend (Place Autocomplete Search)
              ↓
        FastAPI Backend
              ↓
       Google Places API
              ↓
  Flan-T5 Model (Dish Extraction)
              ↓
     Dish Ranking & Response
              ↓
          JSON Output
```

### Flow Summary

1. User searches for a restaurant (via Google Places Autocomplete).
2. Backend fetches Google Reviews using the Place ID.
3. NLP pipeline extracts dish names directly from review text.
4. Dishes are normalized, ranked, and returned to the frontend.

---

## 🧰 Tech Stack

| Layer          | Technology                | Purpose                                       |
| -------------- | ------------------------- | --------------------------------------------- |
| **Framework**  | FastAPI                   | Lightweight async REST API                    |
| **Model**      | `google/flan-t5-large`    | Extract dish names from reviews               |
| **APIs**       | Google Places API         | Retrieve reviews and metadata                 |
| **Data**       | Pandas, NumPy             | Clean and structure review data               |
| **Deployment** | Docker / Render / Railway | Cloud hosting for backend                     |
| **Frontend**   | React + Tailwind CSS      | UI built for smooth Google search integration |

---

## 📡 API Endpoints

| Method | Endpoint                      | Description                             |
| ------ | ----------------------------- | --------------------------------------- |
| `GET`  | `/recommendations/{place_id}` | Returns the top dishes for a restaurant |
| `GET`  | `/health`                     | Health check endpoint                   |

### Example Response

```json
{
  "restaurant": "Brasserie Torbar",
  "recommendations": [
    {
      "dish_name": "truffle risotto",
      "ranking": 1,
      "author": "Yusuf Hadi",
      "source": "google",
      "timestamp": 1759338734,
      "review_link": null
    },
    {
      "dish_name": "900g steak",
      "ranking": 2,
      "author": "Yusuf Hadi",
      "source": "google",
      "timestamp": 1759338734,
      "review_link": null
    }
  ]
}
```

---

## 🧱 Folder Structure

```
dishtip-backend/
│
├── src/
│   ├── main.py                 # FastAPI entry point
│   ├── api/
│   │   └── routes_recommend.py # main /recommendations endpoint
│   ├── services/
│   │   ├── google_service.py   # fetches Google Reviews
│   │   └── dish_extractor.py   # runs Flan-T5 dish extraction
│   ├── nlp/
│   │   └── model_loader.py     # lazy model loading
│   ├── normalisation/
│   │   └── schema.py           # defines DISH schema
│   └── utils/
│       └── text_utils.py       # cleaning and helpers
│
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/<yourusername>/dishtip-backend.git
cd dishtip-backend

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in your Google API key
```

Run the API:

```bash
uvicorn src.main:app --reload
```

---

## 🔐 Environment Variables

| Variable         | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `GOOGLE_API_KEY` | Google Maps / Places API key                              |
| `NLP_MODEL`      | Hugging Face model name (default: `google/flan-t5-large`) |
| `LOG_LEVEL`      | Logging verbosity (e.g., `info`, `debug`)                 |

---

## 🚀 Integration with Frontend

The React frontend (in `/frontend`) uses **Google Places Autocomplete** to fetch the restaurant’s `place_id` and calls:

```
GET http://localhost:8000/recommendations/{place_id}
```

to fetch the top dishes.

---

## 🧩 Future Enhancements

* Prettier design
* Multi-language review handling
* Blog + influencer data integration

---

## 🧑‍🍳 Credits

Built with ❤️ using **FastAPI**, **Transformers**, and **React**.
Part of the **DishTip** project — where **data meets delicious.**
