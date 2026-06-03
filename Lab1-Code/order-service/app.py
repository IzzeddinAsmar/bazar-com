from flask import Flask, jsonify
import sqlite3
from flask import request
import requests
from database import init_db

app = Flask(__name__)
@app.route("/purchase/<int:id>", methods=['POST'])
def purchase(id):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    response = requests.get(f'http://localhost:5000/info/{id}')
    if response.status_code != 200:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404
    book = response.json()
    stock_count = book['stock_count']
    if stock_count <= 0:
        conn.close()
        return jsonify({'error': 'Book out of stock'}), 400
    else:
        requests.put(f'http://localhost:5000/update/{id}', json={'stock_count': stock_count - 1})
        cursor.execute("INSERT INTO orders (book_id) VALUES (?)", (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Purchase successful'}), 201
    
if __name__ == '__main__':
    init_db()
    app.run(port=5001)