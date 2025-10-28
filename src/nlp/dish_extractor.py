"""
dish_extractor.py
-----------------
Extracts dish names mentioned in restaurant reviews using a generative LLM
(Flan-T5).  Wraps model loading, prompting, inference, and post-processing into
a simple API.  Includes in-memory caching for repeated inputs.

Public functions:
    - extract_dishes_from_reviews(reviews)
"""

import re
from typing import Any, Dict, List
from functools import lru_cache
import logging
from transformers import pipeline
from src.normalisation.schema import DISH

logger = logging.getLogger(__name__)

# ---- Config ----
MODEL_NAME = "google/flan-t5-large"
MAX_TOKENS = 100       # Increased from 20 → safer for multi-dish outputs
BATCH_SIZE = 16
DEVICE = -1

_extractor = None  # Lazy singleton model

import torch
torch.set_num_threads(8)
logger.info(f"✅ Using 8 CPU threads for PyTorch")



def chunk_text(text: str, max_words: int = 500) -> list[str]:
    """
    Splits long review text into smaller chunks (~max_words each)
    while respecting sentence boundaries.
    """
    # Split by sentence-ending punctuation
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

    if chunks:
        logger.info(f"Text chunked into {len(chunks)+1} parts.")

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks



# ---- 1. Lazy model loader ----
def get_extractor():
    """
    Loads the Hugging Face pipeline only once.
    """
    global _extractor
    if _extractor is None:
        logger.info(f"Loading model: {MODEL_NAME} ...")
        _extractor = pipeline(
            "text2text-generation",
            model=MODEL_NAME,
            do_sample=False,
            temperature=0.0,
            truncation=True,
            batch_size=BATCH_SIZE,
            device=DEVICE,
        )
        logger.info("Model loaded successfully.")
    return _extractor


# ---- 2. Prompt builder ----
def make_prompt(review: str) -> str:
    """
    Creates a consistent instruction for dish extraction.
    Adjust wording if you prefer your original style.
    """
    return (
        "Extract only names of dishes mentioned exactly as written in the text below.\n"
        "Do not invent or infer dishes. If none are mentioned, reply 'none'.\n"
        "Output a comma-separated list.\n\n"
        f"Text: {review}\nOutput:"
    )


# ---- 3. Cached inference ----
@lru_cache(maxsize=512)
def _cached_extract_single(prompt: str) -> str:
    """
    Runs model inference for one prompt with LRU caching.
    Cached by exact prompt text (up to 512 unique reviews).
    """
    extractor = get_extractor()
    result = extractor(prompt, max_new_tokens=MAX_TOKENS)[0]
    return result.get("generated_text", "").strip()


# ---- 4. Core extraction ----
def extract_dishes(
    reviews: List[Dict[str, Any]], verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    Extracts dish names from review texts using the Flan-T5 model.
    Handles long texts by splitting them into smaller chunks.

    Args:
        reviews: A list of review dicts containing at least a 'text' field.
        verbose: If True, prints input/output for debugging.

    Returns:
        List of reviews with an added 'dishes' key containing normalized dish dicts.
    """
    if not reviews:
        logger.warning("No reviews passed to extractor.")
        return []

    # Prepare prompts (chunk-aware)
    prompts = []
    chunk_index_map = []  # track which review each chunk belongs to

    for i, r in enumerate(reviews):
        chunks = chunk_text(r.get("text", ""))
        for c in chunks:
            prompts.append(make_prompt(c))
            chunk_index_map.append(i)

    # Cached inference for each chunk
    results = [{"generated_text": _cached_extract_single(p)} for p in prompts]

    # Merge dish names by review
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

    # Attach merged, normalized dish lists
    for i, review in enumerate(reviews):
        dishes = dishes_by_review.get(i, set())
        review["dishes"] = [_make_dish(name) for name in dishes]

        if verbose:
            logger.info(f"📝 {review.get('text', '')[:500]}")
            logger.info(f"🍽️ {', '.join(dishes) or 'none'}\n")

    return reviews



# ---- 5. Helper ----
def _make_dish(name: str) -> Dict[str, Any]:
    """Returns a new DISH dict with the given name."""
    dish = DISH.copy()
    dish["name"] = name
    return dish