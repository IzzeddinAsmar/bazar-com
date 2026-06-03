from flask import Flask, jsonify
import sqlite3
from flask import request
from database import init_db

app = Flask(__name__)

@app.route('/search/<topic>')
def search(topic):

    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, title FROM books WHERE topic = ?", (topic,))
    rows = cursor.fetchall()

    conn.close()

    results = [{'id': row[0], 'title': row[1]} for row in rows]
    return jsonify(results)

@app.route('/info/<int:id>')
def book(id):

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
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM books WHERE id = ?", (id,))
    book = cursor.fetchone()

    if not book:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.get_json()
    new_price = data.get('price')
    new_stock = data.get('stock_count')

    if new_price is not None:
        cursor.execute("UPDATE books SET price = ? WHERE id = ?", (new_price, id))

    if new_stock is not None:
        cursor.execute("UPDATE books SET stock_count = ? WHERE id = ?", (new_stock, id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book updated successfully'})

if __name__ == '__main__':
    init_db()
    app.run(port=5000)