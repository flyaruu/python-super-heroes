# Microservices Performance Optimization

## Architecture Overview

This system has 4 services that communicate via HTTP:
- **Fights** (orchestrator) → calls Heroes, Villains, Locations
- **Heroes, Villains, Locations** (data services) → query databases

**Performance characteristic:** Network latency dominates (3 HTTP calls per fight)

## Critical Issue: Sequential Service Calls

**Current implementation in fights service:**
```python
# Each await blocks until response received
hero_response = await client.get("http://heroes:8000/api/heroes/random")
villain_response = await client.get("http://villains:8000/api/villains/random")  
location_response = await client.get("http://locations:8000/api/locations/random")
```

**Measured impact at 50 RPS:**
- Average internal latency per service: ~50ms
- Total fights latency: 150ms (3 × 50ms)
- **Waste: 100ms waiting for sequential I/O**

**Fix: Parallel execution with asyncio.gather:**
```python
hero_task = client.get("http://heroes:8000/api/heroes/random")
villain_task = client.get("http://villains:8000/api/villains/random")
location_task = client.get("http://locations:8000/api/locations/random")

hero_response, villain_response, location_response = await asyncio.gather(
    hero_task, villain_task, location_task
)
```

**Expected improvement:**
- New total latency: ~50ms (max of 3 parallel calls)
- **3x faster, no infrastructure changes needed**

## HTTP Client Configuration

**Current httpx setup:**
```python
client = httpx.AsyncClient()
```

**Optimized configuration:**
```python
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,        # Total connection pool
        max_keepalive_connections=20, # Keep-alive connections
    ),
    timeout=httpx.Timeout(
        connect=2.0,  # Fast fail on connection issues
        read=5.0,     # Allow time for query
        write=2.0,
        pool=2.0,
    ),
    http2=False,  # HTTP/1.1 is simpler for internal services
)
```

**Why this matters:**
- Connection reuse avoids TCP handshake (saves ~5-10ms per request)
- Timeouts prevent hanging requests from blocking pool
- Pool size should match expected concurrent outbound calls

## Service-to-Service Communication Patterns

**1. Request-Response (current):**
```
Fights → GET /random → Heroes → 200 OK
```
- Simple, easy to debug
- High latency if sequential
- Use asyncio.gather for parallel calls

**2. Caching upstream responses:**
```python
# Cache random heroes for 30 seconds
cache_ttl = 30
cached_heroes = []
last_fetch = 0

async def get_random_hero():
    if time.time() - last_fetch > cache_ttl or not cached_heroes:
        # Fetch batch of heroes
        response = await client.get("http://heroes:8000/api/heroes/list?limit=50")
        cached_heroes = response.json()
        last_fetch = time.time()
    return random.choice(cached_heroes)
```
- Reduces service calls 10-100x
- Trades freshness for performance
- Good for read-heavy, slowly changing data

## Error Handling and Resilience

**Add circuit breaker for failing services:**
```python
from collections import defaultdict
import time

circuit_state = defaultdict(lambda: {"failures": 0, "last_failure": 0})

async def call_with_circuit_breaker(service_name, url):
    state = circuit_state[service_name]
    
    # Circuit open if 5 failures in last 60s
    if state["failures"] >= 5 and time.time() - state["last_failure"] < 60:
        raise Exception(f"{service_name} circuit breaker open")
    
    try:
        response = await client.get(url)
        state["failures"] = 0  # Reset on success
        return response
    except Exception as e:
        state["failures"] += 1
        state["last_failure"] = time.time()
        raise
```

**Fallback for degraded service:**
```python
async def get_hero_with_fallback():
    try:
        return await get_hero()
    except:
        # Return cached/default value instead of failing
        return {"name": "Unknown Hero", "power": "mystery"}
```

## Service Health and Monitoring

**Add timing to service calls:**
```python
import time

async def timed_request(url):
    start = time.perf_counter()
    response = await client.get(url)
    duration = (time.perf_counter() - start) * 1000
    
    # Log slow upstream calls
    if duration > 100:
        logger.warning(f"Slow upstream call: {url} took {duration:.0f}ms")
    
    return response
```

**Expose metrics endpoint:**
```python
from collections import Counter

metrics = Counter()

@app.get("/metrics")
async def get_metrics():
    return {
        "requests": metrics["requests"],
        "upstream_calls": metrics["upstream_calls"],
        "upstream_errors": metrics["upstream_errors"],
    }
```

## Docker Compose Performance

**Resource limits in compose.yml:**
```yaml
services:
  fights:
    deploy:
      resources:
        limits:
          cpus: '0.5'    # Limit CPU to prevent starvation
          memory: 512M   # Prevent memory leaks from crashing host
```

**Service dependencies:**
```yaml
depends_on:
  heroes-db:
    condition: service_healthy  # Wait for DB before starting
```

## Quick Optimization Checklist

Before load testing microservices:
- [ ] Parallel calls with asyncio.gather (not sequential)
- [ ] HTTP client with connection pooling and timeouts
- [ ] Appropriate error handling (circuit breaker, fallbacks)
- [ ] Request timing logged for slow upstream calls
- [ ] Health check endpoints on all services
- [ ] Docker resource limits set to prevent contention
