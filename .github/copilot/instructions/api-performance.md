# API Performance Optimization Guide

## Quick Performance Testing

**Fast iteration loop (< 2 minutes):**
```bash
# Start only the service you're testing
docker compose up -d heroes-db
cd services/heroes
source venv/bin/activate
uvicorn main:app --reload &
sleep 3

# Quick benchmark (single endpoint)
time for i in {1..100}; do curl -s http://localhost:8000/api/heroes/random > /dev/null; done

# Kill test server
pkill uvicorn
```

## Async Patterns for This Codebase

**Sequential vs Parallel HTTP Calls:**
The fights service currently makes 3 sequential calls. Here's the performance difference:

```python
# SLOW: Sequential (current implementation)
hero = await get_hero()      # 50ms
villain = await get_villain()  # 50ms
location = await get_location() # 50ms
# Total: 150ms

# FAST: Parallel with asyncio.gather
hero, villain, location = await asyncio.gather(
    get_hero(), get_villain(), get_location()
)
# Total: 50ms (3x faster)
```

**Connection pooling:** httpx.AsyncClient() reuses connections automatically. Create ONE client at startup:
```python
client = httpx.AsyncClient(limits=httpx.Limits(max_connections=100))
```

## Database Query Optimization

**Problem: ORDER BY RANDOM() is slow**
- Full table scan on every request
- Not index-friendly
- Scales poorly (100ms+ on 10k+ rows)

**Solution: Random ID selection**
```python
# Fast: Get random ID from sequence, then SELECT by PK
max_id = await conn.fetchval("SELECT MAX(id) FROM heroes")
random_id = random.randint(1, max_id)
hero = await conn.fetchrow("SELECT * FROM heroes WHERE id >= $1 LIMIT 1", random_id)
# 10x faster with index lookup
```

## Connection Pool Tuning

Current settings: `min_size=10, max_size=50` for asyncpg

**How to right-size:**
1. Measure concurrent requests under load: `docker compose logs fights | grep "concurrent"`
2. Pool should be >= peak concurrency (else requests queue)
3. Pool should be <= database max_connections (else connection errors)

**Rule of thumb:** For read-heavy workloads, `max_size = expected_RPS / 10`

## Caching Strategy

**Where to cache:**
- Random fighters/villains: 10-60s TTL (data rarely changes)
- Fight results: No cache (unique data)

**Simple in-memory cache:**
```python
from functools import lru_cache
import time

cache = {}
@app.get("/api/heroes/random")
async def get_random_hero():
    if "hero" in cache and cache["hero_time"] > time.time() - 30:
        return cache["hero"]
    hero = await fetch_random_hero()
    cache["hero"], cache["hero_time"] = hero, time.time()
    return hero
```

## Measuring Impact

**Before optimizing:** Establish baseline with k6
```bash
docker compose exec k6 k6 run /k6/10rps.js
# Note p95 latency
```

**After changes:** Re-run same test, compare p95/p99
- <20% improvement: Probably noise
- 20-50%: Meaningful improvement  
- >50%: Significant win

**Profile CPU hotspots:**
```bash
py-spy record -o profile.svg -- python main.py
# Open profile.svg to see flamegraph
```
