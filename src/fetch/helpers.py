# Printing 5 reviews of a restaurant

def print_google_reviews(reviews: list):
    print(" ")
    print("- GOOGLE REVIEWS -")
    for r in reviews:
        print(f"{r['rating']}⭐: {r['text']}\n")
        print("-"*3)
    print("- END OF GOOGLE REVIEWS-")