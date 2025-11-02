"""
extractor_openai.py
-------------------
Extracts dish names mentioned in restaurant reviews using an OpenAI LLM
(e.g., GPT-5-Nano). Wraps model loading, prompting, inference, and
post-processing into a simple API, including in-memory caching and
controlled parallel requests for speed and safety.

Public function:
    - extract_dishes_openai_async(reviews)
"""

import os
import re
import time
import logging
import asyncio
from typing import Any, Dict, List
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI
from src.normalisation.schemas import DISH

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-5-nano"
MAX_WORKERS = 10  # concurrent requests allowed
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Semaphore to limit concurrent async calls
_sem = asyncio.Semaphore(MAX_WORKERS)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def chunk_text(text: str, max_words: int = 500) -> list[str]:
    """Splits long review text into smaller chunks (~max_words each)."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, current_chunk = [], []
    word_count = 0

    for sentence in sentences:
        words = sentence.split()
        if word_count + len(words) > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            word_count = 0
        current_chunk.extend(words)
        word_count += len(words)

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def make_prompt(review: str) -> str:
    """Builds the LLM extraction prompt."""
    return (
        "Extract only names of dishes mentioned exactly as written in the text below.\n"
        "Do not invent or infer dishes. If none are mentioned, reply 'none'.\n"
        "Output a comma-separated list.\n\n"
        f"Text: {review}\nOutput:"
    )


@lru_cache(maxsize=512)
def _cached_extract_single(prompt: str) -> str:
    """
    Calls the OpenAI API once for a given prompt (cached by prompt text).
    This remains synchronous but is called from async context safely.
    """
    start = time.perf_counter()
    response = client.responses.create(model=MODEL_NAME, input=prompt, store=True)
    text = response.output_text.strip()
    duration = time.perf_counter() - start
    logger.debug(f"🧠 Cached call took {duration:.2f}s | Output: {text[:80]}")
    return text


def _make_dish(name: str) -> Dict[str, Any]:
    """Returns a DISH dict with the given name."""
    dish = DISH.copy()
    dish["name"] = name
    return dish


# ----------------------------------------------------------------------
# Async single-call wrapper
# ----------------------------------------------------------------------
async def _extract_single_async(prompt: str) -> str:
    """
    Async wrapper that runs the cached synchronous extractor in a thread,
    using a semaphore to cap concurrency.
    """
    loop = asyncio.get_running_loop()
    async with _sem:
        return await loop.run_in_executor(None, _cached_extract_single, prompt)


# ----------------------------------------------------------------------
# Main async pipeline
# ----------------------------------------------------------------------
async def extract_dishes_openai(
    reviews: List[Dict[str, Any]],
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    """
    Extracts dish names from review texts using OpenAI model asynchronously.

    Args:
        reviews: List of review dicts, each containing a 'text' field.
        verbose: If True, logs each review and extracted dishes.

    Returns:
        List of reviews with an added 'dishes' key containing normalized dish dicts.
    """
    if not reviews:
        logger.warning("⚠️ No reviews passed to extractor.")
        return []

    start_total = time.perf_counter()

    # Prepare prompts and index mapping
    prompts = []
    review_index_map = []
    for i, r in enumerate(reviews):
        chunks = chunk_text(r.get("text", ""))
        for c in chunks:
            prompts.append(make_prompt(c))
            review_index_map.append(i)

    logger.info(f"🚀 Starting async extraction for {len(prompts)} chunks...")

    # --- Run all OpenAI calls concurrently ---
    tasks = [asyncio.create_task(_extract_single_async(p)) for p in prompts]
    outputs = await asyncio.gather(*tasks, return_exceptions=True)

    # --- Merge results correctly by review index ---
    dishes_by_review: dict[int, set[str]] = {}
    for idx, result in zip(review_index_map, outputs):
        if isinstance(result, Exception):
            logger.error(f"❌ Extraction failed for review {idx}: {result}")
            continue
        if not isinstance(result, str):
            logger.warning(f"⚠️ Unexpected non-string result for review {idx}: {type(result)}")
            continue

        output = result.strip()
        if not output or output.lower() == "none":
            continue

        dishes = {
            d.strip().lower()
            for d in output.split(",")
            if d.strip() and d.lower() != "none"
        }
        dishes_by_review.setdefault(idx, set()).update(dishes)

    # --- Attach results back to reviews ---
    for i, review in enumerate(reviews):
        dishes = dishes_by_review.get(i, set())
        review["dishes"] = [_make_dish(name) for name in dishes]
        if verbose:
            logger.info(f"🍽️ Extracted from Review #{i+1}: {', '.join(dishes) or 'none'}")

    duration = time.perf_counter() - start_total
    logger.info(f"✅ Completed dish extraction for {len(reviews)} reviews in {duration:.2f}s")

    return reviews
