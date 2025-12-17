import uuid
import time


class FulfillmentWorker:
    def __init__(self):
        pass

    def create_shipment(self, order):
        # Simulate a shipment creation
        shipment_id = 'SHIP-' + str(uuid.uuid4())
        time.sleep(0.01)
        return {
            'shipment_id': shipment_id,
            'order': order,
            'carrier': 'DemoCarrier',
            'status': 'created'
        }
