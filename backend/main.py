from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
import traceback
import time
import logging
import inspect

# ---- DishTip modules ----
from src.fetch.google_reviews import fetch_google_reviews
from src.fetch.google_place import Restaurant
from src.nlp.extractor_openai import extract_dishes_openai
from src.ranking.functions import assign_rankings
from src.recommendation.recs import form_recommendations

# ---- App setup ----
app = FastAPI(title="DishTip Backend", version="2.0", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger config
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---- Timing Decorator ----
def timed(func):
    """
    Measures execution time of sync or async functions and logs it.
    Works with FastAPI (async) and plain functions.
    """
    import functools
    import inspect
    import time

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            logger.info(f"⏳ Starting async: {func.__name__}")
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info(f"✅ Finished async: {func.__name__} in {duration:.2f}s")
            return result

        return async_wrapper

    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            logger.info(f"⏳ Starting: {func.__name__}")
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info(f"✅ Finished: {func.__name__} in {duration:.2f}s")
            return result

        return sync_wrapper


@app.get("/")
def root():
    return {"message": "DishTip API is ready to serve hot tea and tips ☕️"}


# ✅ Timed and non-blocking route
@app.get("/recommendations/{place_id}")
@timed
async def get_recommendations(place_id: str):
    try:
        reviews = await run_in_threadpool(fetch_google_reviews, place_id)
        logger.info(f"📄 Retrieved {len(reviews)} reviews")

        reviews = await run_in_threadpool(extract_dishes_openai, reviews, True)
        logger.info(f"🍽️ Dishes extracted for {len(reviews)} reviews")

        assign_rankings(reviews, True)
        recommendations = form_recommendations(reviews)

        return {"recommendations": recommendations}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurant_info/{place_id}")
@timed
async def get_rest_info(place_id: str):
    restaurant = await run_in_threadpool(Restaurant, place_id)
    return {"restaurant_info": restaurant}
