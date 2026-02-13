# Load Testing Best Practices

## k6 Setup in This Repository

**Available load scenarios:**
- `1rps.js` - Baseline health check
- `10rps.js` - Normal load
- `50rps.js` - High traffic
- `75rps.js` - Stress test  
- `100rps.js` - Peak capacity

**Current thresholds:**
- p95 latency < 500ms
- Error rate < 0.1%

## Running Load Tests

**From within k6 container:**
```bash
docker compose up -d
docker compose exec k6 k6 run /k6/10rps.js
```

**One-off test:**
```bash
docker compose run --rm k6 k6 run /k6/50rps.js
```

**Save results:**
```bash
docker compose exec k6 k6 run /k6/10rps.js --out json=/results/baseline.json
# Results saved to k6/results/baseline.json on host
```

## Interpreting Results

**Key metrics to watch:**
```
http_req_duration..........: avg=123ms min=45ms med=98ms max=1.2s p(95)=245ms
http_req_failed............: 0.05%
http_reqs..................: 600 (10/s)
```

**What matters:**
- **p95 < 500ms:** Most users have good experience
- **p99 < 1s:** Even slowest requests are acceptable
- **Error rate < 0.1%:** System is stable
- **avg vs p95 gap:** Large gap means inconsistent performance

**Failure patterns:**
- **High p95/p99, low avg:** Occasional slow requests (database lock, GC pause)
- **High error rate:** Connection pool exhaustion, database overload
- **Increasing latency over time:** Memory leak, connection leak, cache thrashing

## Setting Realistic Thresholds

**Current threshold (p95 < 500ms) is reasonable for:**
- Internal microservices
- Non-critical APIs
- Read-heavy workloads

**Tighten to p95 < 200ms if:**
- User-facing API
- Real-time features
- SLA requirements

**Relax to p95 < 1s if:**
- Complex queries
- Heavy computation
- Batch processing

## Comparing Before/After

**Establish baseline:**
```bash
docker compose exec k6 k6 run /k6/50rps.js | tee baseline.txt
```

**After optimization:**
```bash
docker compose exec k6 k6 run /k6/50rps.js | tee optimized.txt
```

**Compare:**
```bash
grep "http_req_duration" baseline.txt optimized.txt
# Look for p95 improvement >20%
```

## Local Quick Tests (No k6)

**Single request latency:**
```bash
time curl -s http://localhost:8004/api/fights/random > /dev/null
```

**Parallel requests (concurrency test):**
```bash
seq 100 | xargs -P 10 -I {} curl -s http://localhost:8004/api/fights/random > /dev/null
# -P 10 = 10 concurrent requests
```

**Sustained load with wrk (alternative to k6):**
```bash
wrk -t4 -c100 -d30s http://localhost:8004/api/fights/random
# 4 threads, 100 connections, 30 seconds
```

## Common Mistakes

❌ **Testing with empty database:** Load test after seeding data
❌ **Testing localhost only:** Network latency matters in production
❌ **Single test run:** Run 3x, take median to reduce noise
❌ **Ignoring warm-up:** First few requests are slower (cold caches)
❌ **Testing one endpoint:** Load all services to find bottlenecks

## Quick Wins Checklist

Before running expensive load tests, verify:
- [ ] Services are using connection pooling
- [ ] HTTP clients reuse connections (keep-alive)
- [ ] No `ORDER BY RANDOM()` queries
- [ ] Appropriate logging level (not DEBUG in production)
- [ ] Docker resource limits set appropriately
