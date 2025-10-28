# services/nlp_service.py
from typing import Iterable, Dict, List, Set, Any
from transformers import pipeline  # type: ignore[import]
from src.normalise.schema import DISH

# --- 1 Load your model once ---
extractor = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",
    do_sample=False,
    temperature=0.0,
    truncation=True
)

# --- 2 Build prompt function ---
def make_prompt(review: str) -> str:
    return (
        "Extract ONLY names of dishes on the restaurant's menu mentioned word-for-word in the text below.\n"
        "Do not add or guess any dishes. If no dishes are mentioned, reply 'none'.\n"
        "Output a comma-separated list.\n\n"
        f"Text: {review}\nOutput:"
    )

def extract_dishes(reviews, verbose = False):
    """
    Extract positively mentioned dish names from reviews using Flan-T5.

    Args:
        reviews (str): Reviews in the specific schema format.
        verbose (bool): Set to False by default. If True, prints all reviews and matched dishes.
    
    Returns:
        list[str]: List of dish names (or ['none'] if none found).
    """    
    # --- 3 Prepare input data ---
    review_texts = [r["text"] for r in reviews]       # collect just the review text
    prompts = [make_prompt(text) for text in review_texts]

    # --- 4 Run batched extraction ---
    results = extractor(prompts, max_new_tokens=20, batch_size=4)

    # --- 5 Clean and structure outputs ---
    dish_lists = []
    for i, res in enumerate(results):
        output_text = res["generated_text"].strip()
        if output_text.lower() == "none":
            dishes = ["none"]
        else:
            dishes = [d.strip().lower() for d in output_text.split(",") if d.strip()]
        dish_lists.append({
            "id": i,
            "dishes": dishes})
        
        if verbose == True:
            print(f"📝 {review_texts[i]}")
            print(f"🍽️ {dishes}\n")   

    # --- 6 Add normalised dish list to each review ---
    
        normalised_list = []

    for entry in dish_lists:
        normalised_list = []

        for d in set(entry.get("dishes")):
            new_dish = DISH.copy()
            new_dish["name"] = d
            normalised_list.append(new_dish)
        reviews[entry.get("id")]["dishes"] = normalised_list

    # --- 7 Add a serialised ID to each review ---
    for i, review in enumerate(reviews):
        review["id"] = i