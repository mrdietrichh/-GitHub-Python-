import json
import os
from typing import List, Dict, Any
from datetime import datetime

class ReviewManager:
    def __init__(self, reviews_file: str = "reviews.json"):
        self.reviews_file = reviews_file

    def load(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.reviews_file):
            return []
        with open(self.reviews_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, reviews: List[Dict[str, Any]]) -> None:
        with open(self.reviews_file, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)

    def add(self, market_id: int, user_name: str, rating: int, text: str = "") -> None:
        reviews = self.load()
        review = {
            "market_id": market_id,
            "user_name": user_name,
            "rating": rating,
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        reviews.append(review)
        self.save(reviews)

    def get_for_market(self, market_id: int) -> List[Dict[str, Any]]:
        all_reviews = self.load()
        return list(filter(lambda r: r["market_id"] == market_id, all_reviews))

    def average_rating(self, market_id: int) -> float:
        reviews = self.get_for_market(market_id)
        if not reviews:
            return 0.0
        total = sum(r["rating"] for r in reviews)
        return total / len(reviews)
