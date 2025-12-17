from .recommendation import RecommendationWorker
from .inventory import InventoryWorker
from .payment import PaymentWorker
from .fulfillment import FulfillmentWorker
from ..memory import PersistentMemory


class MasterSalesAgent:
    """A simple orchestrator that routes requests to worker agents."""

    def __init__(self, memory_path=None, products_path=None):
        self.memory = PersistentMemory(memory_path)
        self.recommender = RecommendationWorker(products_path)
        self.inventory = InventoryWorker(products_path)
        self.payment = PaymentWorker()
        self.fulfillment = FulfillmentWorker()

    def recommend(self, user_id=None, context=None):
        prefs = self.memory.get_user_prefs(user_id) if user_id else None
        return self.recommender.recommend(prefs=prefs, context=context)

    def check_inventory(self, product_id):
        return self.inventory.get_stock(product_id)

    def process_payment(self, order):
        result = self.payment.charge(order)
        if result.get('status') == 'success':
            # store minimal order history
            self.memory.append_order(order)
        return result

    def fulfill(self, order):
        shipment = self.fulfillment.create_shipment(order)
        if shipment.get('shipment_id'):
            self.memory.append_fulfillment(shipment)
        return shipment

    def save_user_prefs(self, user_id, prefs):
        self.memory.set_user_prefs(user_id, prefs)
