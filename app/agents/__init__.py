"""Sub-agents package for the Cohesive Stylist demo.
Each module exposes a simple class implementing the worker behaviour.
This is intentionally lightweight so it works without external AI SDKs.
"""

from .master import MasterSalesAgent
from .recommendation import RecommendationWorker
from .inventory import InventoryWorker
from .payment import PaymentWorker
from .fulfillment import FulfillmentWorker

__all__ = [
    "MasterSalesAgent",
    "RecommendationWorker",
    "InventoryWorker",
    "PaymentWorker",
    "FulfillmentWorker",
]
