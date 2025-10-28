from src.normalise.normaliser import normalise_review

all_reviews = []

def add_reviews_to_list(review: dict, source: str):
    """
    Add a dictionary of reviews to the list of all reviews. 

    Args:
        review (dict): normalised review dictionary to be added to the list. 
        source (str): source of the review, only "google" or "blog" possible.
    """
    all_reviews.append(normalise_review(review, source))