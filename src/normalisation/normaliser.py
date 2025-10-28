"""
Normalisation utilities:
- Map heterogeneous review dicts from various sources into a single REVIEW_SCHEMA.
- Optional coercions, defaults, and strict validation.
"""

from src.normalisation.schema import REVIEW_SCHEMA, REVIEW_MAPS

# ---- Logging ----
import logging
logger = logging.getLogger(__name__)

def normalise_review(raw: dict, source: str) -> dict:
    """
    Normalise a single review dictionary to match the standard REVIEW_SCHEMA.
    Unrecognized keys are ignored. Missing keys get default values.

    Args:
        raw (dict): Raw review data from source.
        source (str): Must be "google", "blog".
    """
    
    # Start with defaults
    review = REVIEW_SCHEMA.copy()

    # Get the appropriate field mapping for this source
    mapping = REVIEW_MAPS.get(source, {})

    # Always record where it came from
    review["source"] = source  # type: ignore
    

    # Translate raw keys → schema keys
    for raw_key, value in raw.items():
        # Find which schema field this raw key maps to
        schema_key = mapping.get(raw_key)
        if not mapping:
            logger.warning(f"[WARN] No field mapping found for source '{source}'")

        if schema_key and schema_key in review:
            review[schema_key] = value

    return review