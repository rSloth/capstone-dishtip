# services/nlp_service.py
from __future__ import annotations
from typing import Iterable, Dict, List, Set, Any
import re
from transformers import pipeline  # type: ignore[import]

# ---- Config ----
MODEL_NAME = "Dizex/FoodBaseBERT-NER"
LABEL_WHITELIST: Set[str] = {"Food", "Dish"}
MIN_SCORE: float = 0.45

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# ---- Lazy singleton loader ----
_ner_pipe: Any | None = None

def get_ner() -> Any:
    """Load and cache the HuggingFace NER pipeline."""
    global _ner_pipe
    if _ner_pipe is None:
        _ner_pipe = pipeline(
            task="ner",
            model=MODEL_NAME,
            aggregation_strategy="simple",
            device=0  # set to -1 if no GPU
        )
    return _ner_pipe


# ---- Core function ----
def extract_dishes_from_texts(
    texts: Iterable[str],
    min_score: float = MIN_SCORE,
    label_whitelist: Set[str] = LABEL_WHITELIST
) -> Dict[str, Dict[str, Any]]:
    """
    Return a dictionary keyed by dish name.
    Example:
      {
        "spaghetti carbonara": {
            "count": 3,
            "mentions": ["...", "..."],
            "avg_conf": 0.73
        }
      }
    """
    ner = get_ner()
    assert ner is not None  # helps Pylance know it's not None
    dish_map: Dict[str, Dict[str, Any]] = {}

    for full_text in texts:
        sentences = SENT_SPLIT_RE.split(full_text.strip()) if full_text else []
        for sent in sentences:
            if not sent:
                continue
            entities: List[Dict[str, Any]] = ner(sent)
            for e in entities:
                group = e.get("entity_group") or e.get("entity")
                score = float(e.get("score", 0.0))
                word = (e.get("word") or "").strip()

                if not word or group not in label_whitelist or score < min_score:
                    continue

                dish = normalize_dish(word)
                entry = dish_map.setdefault(
                    dish, {"count": 0, "mentions": [], "avg_conf_sum": 0.0}
                )
                entry["count"] = int(entry["count"]) + 1
                if len(entry["mentions"]) < 10:
                    entry["mentions"].append(sent.strip())
                entry["avg_conf_sum"] = float(entry["avg_conf_sum"]) + score

    for dish, entry in dish_map.items():
        cnt = max(entry["count"], 1)
        entry["avg_conf"] = round(entry.pop("avg_conf_sum") / cnt, 3)

    return dish_map


# ---- Helpers ----
def normalize_dish(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[^\w\s\-’']", "", s)
    return s


def conv_to_food_string(text: str, entities: List[Dict[str, Any]]) -> List[str]:
    """
    Convert raw entity spans to clean dish strings.
    Example: conv_to_food_string(example, ner_entity_results)
    """
    ents: List[Dict[str, Any]] = []
    for ent in entities:
        e = {
            "start": ent["start"],
            "end": ent["end"],
            "label": ent.get("entity_group", ""),
        }
        if (
            ents
            and -1 <= ent["start"] - ents[-1]["end"] <= 1
            and ents[-1]["label"] == e["label"]
        ):
            ents[-1]["end"] = e["end"]
            continue
        ents.append(e)
    return [text[e["start"]:e["end"]] for e in ents]



from transformers import pipeline

ner = pipeline("ner", model=MODEL_NAME, aggregation_strategy="simple")
# NER = Named Entity Recognition

reviews = [
    "The spaghetti carbonara was amazing!",
    "The tiramisu was creamy and delicious.",
    "I didn’t like the lasagna; too salty.",
    "Their Margherita pizza is the best in town!",
    "Service sehr herzlich und locker, Essen sehr frisch und schmackhaft. Die Fisch Buns sowie das Spicy Shrimp Popcorn sind wirklich toll. Wir kommen wieder, wenn wir in Berlin sind."
    ]

for r in reviews:
    entities = ner(r)
    dishes = conv_to_food_string(r, entities)
    print(f"📝 {r}")
    print(f"🍽️ {dishes}\n")
