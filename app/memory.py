import json
import os
from threading import Lock


class PersistentMemory:
    """A very small file-backed persistent memory.

    Methods are minimal: get/set user prefs, append orders/fulfillments.
    """

    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), 'memory.json')
        self._lock = Lock()
        if not os.path.exists(self.path):
            self._write({'users': {}, 'orders': [], 'fulfillments': []})

    def _read(self):
        with self._lock:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {'users': {}, 'orders': [], 'fulfillments': []}

    def _write(self, data):
        with self._lock:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

    def get_user_prefs(self, user_id):
        data = self._read()
        return data.get('users', {}).get(str(user_id))

    def set_user_prefs(self, user_id, prefs):
        data = self._read()
        data.setdefault('users', {})[str(user_id)] = prefs
        self._write(data)

    def append_order(self, order):
        data = self._read()
        data.setdefault('orders', []).append(order)
        self._write(data)

    def append_fulfillment(self, shipment):
        data = self._read()
        data.setdefault('fulfillments', []).append(shipment)
        self._write(data)
