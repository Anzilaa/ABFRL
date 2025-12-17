import uuid
import time


class PaymentWorker:
    def __init__(self):
        pass

    def charge(self, order):
        # very simple simulated payment flow
        tx_id = str(uuid.uuid4())
        time.sleep(0.01)
        return {
            'status': 'success',
            'transaction_id': tx_id,
            'amount': order.get('amount') or 0,
        }
