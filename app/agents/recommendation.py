import random
import json
from typing import Optional


class RecommendationWorker:
    def __init__(self, products_path=None):
        self.products_path = products_path or 'dummy_page/data/products.json'
        self._load_products()

    def _load_products(self):
        try:
            with open(self.products_path, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
        except Exception:
            self.products = []

    def recommend(self, prefs: Optional[dict] = None, context: Optional[dict] = None):
        """Return a small list of recommended product ids and details.
        This is a heuristic: if prefs has "favorite_tags" we prefer those.
        """
        if not self.products:
            return []

        # simple tag-based scoring
        scored = []
        fav_tags = (prefs or {}).get('favorite_tags', [])
        for p in self.products:
            score = 0
            tags = p.get('tags', [])
            for t in fav_tags:
                if t in tags:
                    score += 2
            # small randomness
            score += random.random()
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [p for s, p in scored[:3]]
        return top
