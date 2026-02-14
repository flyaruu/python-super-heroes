# Profiling Python Services

## Quick Start: Finding CPU Bottlenecks

**Install py-spy:**
```bash
pip install py-spy
```

**Profile a running service:**
```bash
# Start service
cd services/fights
source venv/bin/activate
uvicorn main:app &
PID=$!

# Generate some load
for i in {1..1000}; do curl -s http://localhost:8000/api/fights/random > /dev/null; done &

# Profile while under load
py-spy record -o profile.svg --pid $PID --duration 30
# Creates flamegraph showing where CPU time is spent

kill $PID
```

**Read the flamegraph:**
- **Width = time spent** (wider = slower)
- **Height = call stack** (bottom = low-level, top = your code)
- **Look for:** Wide bars in your code (not stdlib/framework)

## Memory Profiling

**Install memory_profiler:**
```bash
pip install memory-profiler
```

**Profile a specific function:**
```python
from memory_profiler import profile

@profile
@app.get("/api/fights/random")
async def fight_endpoint():
    # Your code
    pass
```

**Run with profiling:**
```bash
python -m memory_profiler main.py
# Shows memory usage line-by-line
```

**Find memory leaks:**
```python
import tracemalloc
tracemalloc.start()

# ... run your code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

## Profiling in Docker

**py-spy with Docker:**
```bash
# Add py-spy to requirements.txt
docker compose up -d fights

# Profile inside container
docker compose exec fights py-spy record -o /tmp/profile.svg -- python -m uvicorn main:app
```

**Copy results out:**
```bash
docker compose cp fights:/tmp/profile.svg ./profile.svg
```

## Async-Specific Profiling

**Profile async/await overhead:**
```python
import asyncio
import time

async def timed(coro):
    start = time.perf_counter()
    result = await coro
    print(f"Took {(time.perf_counter() - start)*1000:.2f}ms")
    return result

# Use in code
hero = await timed(get_hero())
```

**Find slow async operations:**
```bash
# Enable asyncio debug mode
PYTHONASYNCIODEBUG=1 python main.py
# Logs slow coroutines (>100ms by default)
```

## Common Performance Issues to Look For

**1. Sequential async calls (most common in this codebase):**
```python
# BAD: Serial execution
hero = await get_hero()
villain = await get_villain()

# GOOD: Parallel execution  
hero, villain = await asyncio.gather(get_hero(), get_villain())
```

**2. Blocking I/O in async code:**
```python
# BAD: Blocks event loop
with open('file.txt') as f:
    data = f.read()

# GOOD: Use async file I/O or run_in_executor
import aiofiles
async with aiofiles.open('file.txt') as f:
    data = await f.read()
```

**3. CPU-bound work in async code:**
```python
# BAD: Blocks event loop
result = expensive_computation(data)

# GOOD: Run in thread pool
result = await asyncio.to_thread(expensive_computation, data)
```

## Quick Performance Checks

**Benchmark a specific function:**
```python
import timeit

# Test current implementation
time_old = timeit.timeit(lambda: old_function(), number=1000)

# Test new implementation
time_new = timeit.timeit(lambda: new_function(), number=1000)

print(f"Speedup: {time_old/time_new:.2f}x")
```

**Profile database queries:**
```python
import time

async def query_with_timing(conn, query):
    start = time.perf_counter()
    result = await conn.fetch(query)
    duration = time.perf_counter() - start
    if duration > 0.1:  # Log slow queries
        logger.warning(f"Slow query ({duration*1000:.0f}ms): {query}")
    return result
```

## Tools Quick Reference

| Tool | Use Case | Installation |
|------|----------|--------------|
| py-spy | CPU profiling (production-safe) | `pip install py-spy` |
| cProfile | CPU profiling (detailed, overhead) | Built-in |
| memory_profiler | Memory usage line-by-line | `pip install memory-profiler` |
| tracemalloc | Memory leak detection | Built-in |
| asyncio debug | Find slow coroutines | Set `PYTHONASYNCIODEBUG=1` |

## When to Profile

✅ **Profile when:**
- p95 latency is above target
- High CPU usage under load
- Memory usage growing over time
- After major code changes

❌ **Don't profile when:**
- System is already fast enough
- Before establishing baseline metrics
- Without load (cold cache, no contention)
