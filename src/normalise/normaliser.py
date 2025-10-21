from schema import REVIEW_SCHEMA, REVIEW_MAPS

def normalise_review(raw: dict, source: str) -> dict:
    """
    Normalize a single review dictionary to match the standard REVIEW_SCHEMA.
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
            print(f"[WARN] No field mapping found for source '{source}'")

        if schema_key and schema_key in review:
            review[schema_key] = value

    return review