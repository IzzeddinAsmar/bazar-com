import requests
import time

FRONTEND = 'http://localhost:5002'

def measure(url, method='GET', runs=10):
    """Send multiple requests and return average response time in milliseconds."""
    times = []
    for _ in range(runs):
        start = time.time()
        if method == 'GET':
            requests.get(url)
        elif method == 'POST':
            requests.post(url)
        end = time.time()
        times.append((end - start) * 1000)  # convert to milliseconds
    return round(sum(times) / len(times), 2)

print("=" * 55)
print("        Bazar.com Performance Measurements")
print("=" * 55)

# ── Test 1: Info without cache (cold) ──
requests.delete(f'{FRONTEND}/invalidate/all')  # clear cache first
cold_info = measure(f'{FRONTEND}/info/1')
print(f"\n[INFO] Cold (no cache):  {cold_info} ms")

# ── Test 2: Info with cache (warm) ──
requests.get(f'{FRONTEND}/info/1')  # warm the cache
warm_info = measure(f'{FRONTEND}/info/1')
print(f"[INFO] Warm (cached):    {warm_info} ms")

improvement = round(((cold_info - warm_info) / cold_info) * 100, 1)
print(f"[INFO] Cache speedup:    {improvement}% faster")

# ── Test 3: Search without cache ──
requests.delete(f'{FRONTEND}/invalidate/all')
cold_search = measure(f'{FRONTEND}/search/distributed%20systems')
print(f"\n[SEARCH] Cold (no cache): {cold_search} ms")

# ── Test 4: Search with cache ──
requests.get(f'{FRONTEND}/search/distributed%20systems')
warm_search = measure(f'{FRONTEND}/search/distributed%20systems')
print(f"[SEARCH] Warm (cached):   {warm_search} ms")

# ── Test 5: Purchase (never cached) ──
purchase_time = measure(f'{FRONTEND}/purchase/3', method='POST', runs=5)
print(f"\n[PURCHASE] Average:       {purchase_time} ms")

# ── Test 6: Cache consistency ──
print("\n── Cache Consistency Test ──")
requests.delete(f'{FRONTEND}/invalidate/all')
requests.get(f'{FRONTEND}/info/3')  # cache book 3

before = requests.get(f'{FRONTEND}/info/3').json()['stock_count']
print(f"Stock before purchase:   {before}")

requests.post(f'{FRONTEND}/purchase/3')  # triggers invalidation

after = requests.get(f'{FRONTEND}/info/3').json()['stock_count']
print(f"Stock after purchase:    {after}")

if after == before - 1:
    print("Cache consistency:       PASS - cache was invalidated correctly")
else:
    print("Cache consistency:       FAIL")

# ── Summary Table ──
print("\n" + "=" * 55)
print(f"{'Operation':<25} {'Cold (ms)':>12} {'Warm (ms)':>12}")
print("-" * 55)
print(f"{'Info':<25} {cold_info:>12} {warm_info:>12}")
print(f"{'Search':<25} {cold_search:>12} {warm_search:>12}")
print(f"{'Purchase (no cache)':<25} {purchase_time:>12} {'N/A':>12}")
print("=" * 55)