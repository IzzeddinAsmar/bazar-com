import sqlite3
import requests
from flask import Flask, jsonify, request
from database import init_db

# Points back to replica 1 for sync
OTHER_REPLICA_URL = 'http://order-service-1:5001'

app = Flask(__name__)


@app.route('/purchase/<int:id>', methods=['POST'])
def purchase(id):
    """
    Processes a purchase request for a book.
    Follows this order:
      1. Check the book exists and is in stock by querying the catalog
      2. Decrement stock by calling the catalog update endpoint
      3. Record the order in the local database
      4. Sync the order record to the other order replica
    Returns 404 if book doesn't exist, 400 if out of stock.
    """
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    # Step 1 — Ask catalog service if the book exists and check stock
    # The order service never accesses the catalog database directly
    response = requests.get(f'http://catalog-service-1:5000/info/{id}')

    # If catalog returns non-200, the book doesn't exist
    if response.status_code != 200:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    book = response.json()
    stock_count = book['stock_count']

    # Check if stock is available
    if stock_count <= 0:
        conn.close()
        return jsonify({'error': 'Book out of stock'}), 400

    # Step 2 — Decrement stock by 1 via catalog update endpoint
    # This also triggers cache invalidation and replica sync in the catalog
    requests.put(
        f'http://catalog-service-1:5000/update/{id}',
        json={'stock_count': stock_count - 1}
    )

    # Step 3 — Record the order in the local database
    cursor.execute("INSERT INTO orders (book_id) VALUES (?)", (id,))
    conn.commit()
    conn.close()

    # Step 4 — Sync the order record to the other order replica
    # Uses /sync instead of /purchase to avoid double stock decrement
    try:
        requests.post(f'{OTHER_REPLICA_URL}/sync/{id}')
    except:
        # Don't crash if the other replica is temporarily unreachable
        pass

    return jsonify({'message': 'Purchase successful'}), 201


@app.route('/sync/<int:id>', methods=['POST'])
def sync(id):
    """
    Internal endpoint called by the other order replica to sync an order.
    Only inserts the order record — no stock checks or catalog calls.
    This prevents double decrementing stock for the same purchase.
    """
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    # Simply record the order — all stock logic was handled by the primary replica
    cursor.execute("INSERT INTO orders (book_id) VALUES (?)", (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Order synced successfully'})


if __name__ == '__main__':
    init_db()
# Runs on port 5004 instead of 5001
app.run(host='0.0.0.0', port=5004)