import json


class InventoryWorker:
    def __init__(self, products_path=None):
        self.products_path = products_path or 'dummy_page/data/products.json'
        self._load_products()

    def _load_products(self):
        try:
            with open(self.products_path, 'r', encoding='utf-8') as f:
                self.products = {p['id']: p for p in json.load(f)}
        except Exception:
            self.products = {}

    def get_stock(self, product_id):
        # demo: assume field `stock` exists, otherwise return large number
        p = self.products.get(product_id)
        if not p:
            return {'product_id': product_id, 'stock': 0}
        return {'product_id': product_id, 'stock': p.get('stock', 100)}
