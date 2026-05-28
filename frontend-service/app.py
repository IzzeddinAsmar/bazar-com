import requests
from flask import Flask, jsonify

# In-memory cache — stores book details to avoid repeated catalog calls
# Key: book id (int), Value: full book details (dict)
# Cache is cleared on frontend restart — it is not persistent
cache = {}

# List of available catalog replicas for load balancing
catalog_replicas = ['http://catalog-service-1:5000', 'http://catalog-service-2:5003']

# List of available order replicas for load balancing
order_replicas = ['http://order-service-1:5001', 'http://order-service-2:5004']

# Counters that track which replica gets the next request
# They cycle between 0 and 1 using modulo arithmetic
current_catalog = 0
current_order = 0


def get_next_catalog_replica():
    """
    Returns the next catalog replica URL using round-robin load balancing.
    Alternates between replica 1 and replica 2 on each call.
    """
    global current_catalog
    replica = catalog_replicas[current_catalog]
    # Modulo keeps the counter cycling: 0 → 1 → 0 → 1 ...
    current_catalog = (current_catalog + 1) % len(catalog_replicas)
    return replica


def get_next_order_replica():
    """
    Returns the next order replica URL using round-robin load balancing.
    Alternates between replica 1 and replica 2 on each call.
    """
    global current_order
    replica = order_replicas[current_order]
    current_order = (current_order + 1) % len(order_replicas)
    return replica


app = Flask(__name__)


@app.route('/search/<topic>')
def search(topic):
    """
    Forwards search requests to a catalog replica using round-robin.
    Search results are not cached because they reflect current stock
    levels which change frequently.
    """
    replica = get_next_catalog_replica()
    response = requests.get(f'{replica}/search/{topic}')
    return jsonify(response.json()), response.status_code


@app.route('/info/<int:id>')
def info(id):
    """
    Returns book details, serving from cache when available.
    Cache hit  — returns immediately without contacting catalog.
    Cache miss — fetches from a catalog replica, stores in cache,
                 returns to client.
    """
    # Check cache first — avoids unnecessary network call to catalog
    if id in cache:
        return jsonify(cache[id]), 200

    # Cache miss — fetch from catalog replica
    replica = get_next_catalog_replica()
    response = requests.get(f'{replica}/info/{id}')

    if response.status_code != 200:
        return jsonify({'error': 'Book not found'}), 404

    # Store result in cache for future requests
    cache[id] = response.json()
    return jsonify(cache[id]), 200


@app.route('/purchase/<int:id>', methods=['POST'])
def purchase(id):
    """
    Forwards purchase requests to an order replica using round-robin.
    Purchase results are not cached — purchases always go to the order service.
    """
    replica = get_next_order_replica()
    response = requests.post(f'{replica}/purchase/{id}')
    return jsonify(response.json()), response.status_code


@app.route('/invalidate/all', methods=['DELETE'])
def invalidate_all():
    """
    Clears the entire cache at once.
    Used for testing and performance measurements.
    """
    cache.clear()
    return jsonify({'message': 'Cache cleared'})


@app.route('/invalidate/<int:id>', methods=['DELETE'])
def invalidate(id):
    """
    Removes a book from the cache.
    Called by catalog replicas before writing to their database
    to ensure clients never read stale cached data after an update.
    """
    if id in cache:
        del cache[id]
    return jsonify({'message': 'Cache invalidated'})


if __name__ == '__main__':
    # host='0.0.0.0' makes Flask accessible from outside the Docker container
    app.run(host='0.0.0.0', port=5002)