from flask import Flask, jsonify
import requests



app = Flask(__name__)

@app.route('/search/<topic>')
def search(topic):
    response = requests.get(f'http://localhost:5000/search/{topic}')
    return jsonify(response.json()), response.status_code

@app.route('/info/<int:id>')
def book(id):
    response = requests.get(f'http://localhost:5000/info/{id}')
    return jsonify(response.json()), response.status_code

@app.route('/purchase/<int:id>', methods=['POST'])
def purchase(id):
    response = requests.post(f'http://localhost:5001/purchase/{id}')
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(port=5002)