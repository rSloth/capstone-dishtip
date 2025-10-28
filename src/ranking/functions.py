def assign_rankings(reviews, verbose = False):
    """
    Assigns a default ranking of -1 to all dishes in reviews 
    where the source is 'google' and the dish ranking is None.
    """
    for review in reviews:
        if review.get("source") == "google" and review.get("dishes"):
            google_default_ranking = -1
            for dish in review["dishes"]:
                if dish.get("ranking") is None:
                    dish["ranking"] = google_default_ranking
                    if verbose:
                        print(f"Assigned ranking {google_default_ranking} to dish '{dish.get('name')}' in review #{review.get('id')}")  
        elif review.get("source") == "bing" and review.get("dishes"):
            pass  # Future logic for Bing reviews can be added here



    