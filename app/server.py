from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

from .agents.master import MasterSalesAgent

APP_ROOT = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(APP_ROOT, 'dummy_page')

app = Flask(__name__, static_folder=STATIC_ROOT, static_url_path='')
CORS(app)

# create master agent with paths pointing to the repo's dummy data
master = MasterSalesAgent(memory_path=os.path.join(os.path.dirname(__file__), 'memory.json'),
                          products_path=os.path.join(STATIC_ROOT, 'data', 'products.json'))


@app.route('/')
def web_root():
    return send_from_directory(STATIC_ROOT, 'index.html')


@app.route('/api/recommendations')
def recommendations():
    user_id = request.args.get('userId')
    recs = master.recommend(user_id)
    return jsonify({'results': recs})


@app.route('/api/inventory')
def inventory():
    product_id = request.args.get('productId')
    if not product_id:
        return jsonify({'error': 'productId required'}), 400
    res = master.check_inventory(product_id)
    return jsonify(res)


@app.route('/api/payment', methods=['POST'])
def payment():
    order = request.get_json() or {}
    res = master.process_payment(order)
    return jsonify(res)


@app.route('/api/fulfill', methods=['POST'])
def fulfill():
    order = request.get_json() or {}
    res = master.fulfill(order)
    return jsonify(res)


@app.route('/api/user/prefs', methods=['GET', 'POST'])
def user_prefs():
    if request.method == 'GET':
        uid = request.args.get('userId')
        if not uid:
            return jsonify({'error': 'userId required'}), 400
        prefs = master.memory.get_user_prefs(uid)
        return jsonify({'userId': uid, 'prefs': prefs})
    else:
        body = request.get_json() or {}
        uid = body.get('userId')
        prefs = body.get('prefs')
        if not uid or prefs is None:
            return jsonify({'error': 'userId and prefs required'}), 400
        master.save_user_prefs(uid, prefs)
        return jsonify({'status': 'ok'})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple rule-based chat endpoint that routes to agent capabilities.

    Expected JSON: {"userId": "u1", "message": "recommend some shoes"}
    """
    body = request.get_json() or {}
    user_id = body.get('userId')
    message = (body.get('message') or '').strip().lower()

    if not message:
        return jsonify({'reply': "Please send a message."}), 400

    # simple intent rules
    if any(w in message for w in ('recommend', 'suggest', 'what should i', 'show me')):
        recs = master.recommend(user_id)
        return jsonify({'reply': f'I found {len(recs)} recommendations.', 'recommendations': recs})

    # buy command: expects 'buy <product_id>' or 'purchase <product_id>'
    tokens = message.split()
    if tokens and tokens[0] in ('buy', 'purchase') and len(tokens) >= 2:
        product_id = tokens[1]
        # create a simple order object
        order = {'order_id': f'order-{user_id or "anon"}-{product_id}', 'items': [{'id': product_id, 'qty': 1}]}
        # try to find product price
        # master.recommender has product details
        prod = None
        try:
            for p in master.recommender.products:
                if p.get('id') == product_id:
                    prod = p
                    break
        except Exception:
            prod = None
        order['amount'] = prod.get('price') if prod else 0
        pay = master.process_payment(order)
        if pay.get('status') == 'success':
            ship = master.fulfill(order)
            return jsonify({'reply': 'Payment successful, order placed.', 'payment': pay, 'shipment': ship})
        return jsonify({'reply': 'Payment failed', 'payment': pay}), 500

    # checkout command: process cart from client if provided
    if 'checkout' in message:
        cart = body.get('cart') or []
        total = sum((item.get('price', 0) * item.get('qty', 1)) for item in cart)
        order = {'order_id': f'order-{user_id or "anon"}-cart', 'items': cart, 'amount': total}
        pay = master.process_payment(order)
        if pay.get('status') == 'success':
            ship = master.fulfill(order)
            return jsonify({'reply': 'Checkout complete — payment & fulfillment created.', 'payment': pay, 'shipment': ship})
        return jsonify({'reply': 'Checkout failed during payment', 'payment': pay}), 500

    # fallback: echo
    return jsonify({'reply': "I can 'recommend' products or you can 'buy <productId>' or 'checkout'."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
