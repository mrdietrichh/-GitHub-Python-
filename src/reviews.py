import json
import os
from typing import List, Dict, Any
from datetime import datetime

REVIEWS_FILE = "reviews.json"

def load_reviews() -> List[Dict[str, Any]]:
    if not os.path.exists(REVIEWS_FILE):
        return []
    with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_reviews(reviews: List[Dict[str, Any]]) -> None:
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def add_review(market_id: int, user_name: str, rating: int, text: str = "") -> None:
    reviews = load_reviews()
    review = {
        "market_id": market_id,
        "user_name": user_name,
        "rating": rating,
        "text": text,
        "timestamp": datetime.now().isoformat()
    }
    reviews.append(review)
    save_reviews(reviews)

def get_reviews_for_market(market_id: int) -> List[Dict[str, Any]]:
    all_reviews = load_reviews()
    return list(filter(lambda r: r["market_id"] == market_id, all_reviews))

def get_average_rating(market_id: int) -> float:
    reviews = get_reviews_for_market(market_id)
    if not reviews:
        return 0.0
    total = sum(r["rating"] for r in reviews)
    return total / len(reviews)
