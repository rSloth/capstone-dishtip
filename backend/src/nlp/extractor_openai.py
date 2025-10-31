"""
extractor_openai.py
-------------------
Extracts dish names mentioned in restaurant reviews using an OpenAI LLM
(e.g., GPT-5-Nano). Wraps model loading, prompting, inference, and
post-processing into a simple API, including in-memory caching and
parallel requests for speed.

Public functions:
    - extract_dishes_openai(reviews)
"""

import os
import re
import time
import logging
from typing import Any, Dict, List
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI
from src.normalisation.schema import DISH


# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-5-nano"
MAX_WORKERS = 10  # Number of concurrent API calls
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def chunk_text(text: str, max_words: int = 500) -> list[str]:
    """
    Splits long review text into smaller chunks (~max_words each)
    while respecting sentence boundaries.
    """
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

    if len(chunks) > 1:
        logger.info(f"🧩 Text chunked into {len(chunks)} parts.")
    return chunks


def make_prompt(review: str) -> str:
    """
    Builds the extraction prompt for the LLM.
    """
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
    """
    start = time.perf_counter()
    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        store=True,
    )
    duration = time.perf_counter() - start
    text = response.output_text.strip()
    logger.debug(f"🧠 OpenAI call took {duration:.2f}s | Output: {text[:80]}")
    return text


def _make_dish(name: str) -> Dict[str, Any]:
    """Returns a DISH dict with the given name."""
    dish = DISH.copy()
    dish["name"] = name
    return dish


# ----------------------------------------------------------------------
# Main extraction pipeline
# ----------------------------------------------------------------------
def extract_dishes_openai(reviews: List[Dict[str, Any]], verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Extracts dish names from review texts using the OpenAI model.

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

    # Prepare prompts
    prompts = []
    chunk_index_map = []  # track which review each chunk belongs to

    for i, r in enumerate(reviews):
        chunks = chunk_text(r.get("text", ""))
        for c in chunks:
            prompts.append(make_prompt(c))
            chunk_index_map.append(i)

    logger.info(f"🚀 Starting extraction for {len(prompts)} text chunks...")

    # --- Parallel OpenAI calls ---
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_cached_extract_single, p): p for p in prompts}

        for future in as_completed(futures):
            prompt = futures[future]
            try:
                output_text = future.result()
            except Exception as e:
                logger.error(f"❌ OpenAI request failed for prompt: {prompt[:100]}... ({e})")
                output_text = "none"
            results.append({"generated_text": output_text})

    # --- Merge dish names by review ---
    dishes_by_review: dict[int, set[str]] = {}
    for idx, res in zip(chunk_index_map, results):
        output = res.get("generated_text", "").strip()
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
            logger.info(f"📝 {review.get('text', '')[:250]}...")
            logger.info(f"🍽️ Extracted: {', '.join(dishes) or 'none'}")

    duration = time.perf_counter() - start_total
    logger.info(f"✅ Completed dish extraction for {len(reviews)} reviews in {duration:.2f}s")

    return reviews