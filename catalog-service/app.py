import sqlite3
import requests
from flask import Flask, jsonify, request
from database import init_db

# Base URL of the frontend service — used to send cache invalidation requests
FRONTEND_URL = 'http://frontend-service:5002'

# Base URL of the other catalog replica — used to sync writes after a database update
OTHER_REPLICA_URL = 'http://catalog-service-2:5003'

app = Flask(__name__)

@app.route('/search/<topic>')
def search(topic):
    """
    Returns all books matching the given topic.
    Only returns id and title — full details are available via /info.
    """
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    # Query books by topic and return only id and title
    cursor.execute("SELECT id, title FROM books WHERE topic = ?", (topic,))
    rows = cursor.fetchall()
    conn.close()

    # Convert list of tuples to list of dictionaries for JSON serialization
    results = [{'id': row[0], 'title': row[1]} for row in rows]
    return jsonify(results)


@app.route('/info/<int:id>')
def info(id):
    """
    Returns full details of a single book by ID.
    Returns 404 if the book doesn't exist.
    """
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, topic, price, stock_count FROM books WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        result = {
            'id': row[0],
            'title': row[1],
            'topic': row[2],
            'price': row[3],
            'stock_count': row[4]
        }
        return jsonify(result)
    else:
        return jsonify({'error': 'Book not found'}), 404


@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    """
    Updates the price or stock_count of a book.
    Follows this order:
      1. Invalidate the frontend cache for this book
      2. Write the change to the local database
      3. Sync the change to the other catalog replica

    Accepts an optional is_sync flag in the request body.
    When is_sync=True, the replica sync step is skipped
    to prevent infinite replication loops.
    """
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    # Check the book exists before attempting any update
    cursor.execute("SELECT id FROM books WHERE id = ?", (id,))
    book = cursor.fetchone()

    if not book:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    data = request.get_json()
    new_price = data.get('price')
    new_stock = data.get('stock_count')

    # is_sync flag indicates this update came from the other replica
    # if True, we skip syncing back to prevent an infinite loop
    is_sync = data.get('is_sync', False)

    # Step 1 — Invalidate the frontend cache before writing
    # This ensures no client reads stale data after this update
    try:
        requests.delete(f'{FRONTEND_URL}/invalidate/{id}')
    except:
        # Don't crash if frontend is temporarily unreachable
        pass

    # Step 2 — Apply the update to the local database
    # Only update fields that were actually provided in the request
    # Use 'is not None' instead of 'if value' to correctly handle value=0
    if new_price is not None:
        cursor.execute("UPDATE books SET price = ? WHERE id = ?", (new_price, id))

    if new_stock is not None:
        cursor.execute("UPDATE books SET stock_count = ? WHERE id = ?", (new_stock, id))

    conn.commit()
    conn.close()

    # Step 3 — Sync the change to the other replica
    # Only if this is not already a sync call (prevents infinite loop)
    # is_sync=True is added so the other replica skips forwarding it further
    if not is_sync:
        try:
            requests.put(f'{OTHER_REPLICA_URL}/update/{id}', json={**data, 'is_sync': True})
        except:
            # Don't crash if the other replica is temporarily unreachable
            pass

    return jsonify({'message': 'Book updated successfully'})


if __name__ == '__main__':
    # Initialize the database on startup
    init_db()
    # host='0.0.0.0' makes Flask accessible from outside the Docker container
    app.run(host='0.0.0.0', port=5000)