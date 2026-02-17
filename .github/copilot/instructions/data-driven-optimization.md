# Data-Driven Performance Optimization

## Overview

This guide explains how to use performance data to make informed optimization decisions instead of guessing. Always measure before and after changes to validate improvements.

## The Performance Feedback Loop

### 1. Establish Baseline

**Before making any changes**, collect baseline performance data:

```bash
# Start services
docker compose up -d

# Collect baseline
python scripts/collect_performance_data.py \
  --rps 50 \
  --output k6/results/baseline.json \
  --report k6/results/baseline_report.md

# Review the report
cat k6/results/baseline_report.md
```

### 2. Identify Bottlenecks from Data

Read the performance report and look for:

- **High P95 latency (>500ms)**: Indicates slow requests that need optimization
- **High latency variance (p95/avg > 2.5)**: Some requests are much slower than others
- **Elevated error rate (>0.1%)**: Connection or service issues
- **Service-specific metrics**: Check database query times, external call times

### 3. Make Targeted Changes

Based on the data, choose the right optimization:

**If P95 latency is high:**
- Check database query metrics - optimize slow queries
- Review external service call times - add parallelization or caching
- Look at code profiling data

**If latency variance is high:**
- Check for connection pool exhaustion
- Look for occasional slow database queries (missing indexes)
- Investigate cache miss scenarios

**If error rate is elevated:**
- Check timeout configuration
- Review connection pool settings
- Add retry logic or circuit breakers

### 4. Measure Impact

After making changes:

```bash
# Rebuild services
docker compose up -d --build

# Measure new performance with comparison
python scripts/collect_performance_data.py \
  --rps 50 \
  --baseline k6/results/baseline.json \
  --output k6/results/optimized.json \
  --report k6/results/optimized_report.md

# Review improvements
cat k6/results/optimized_report.md
```

### 5. Validate and Document

- **If improved:** Include the comparison in your PR description
- **If no improvement:** Investigate why and iterate or revert
- **If regressed:** Revert the change immediately

## Key Metrics Reference

### Request Duration Metrics
- **avg**: Average response time across all requests
- **p50 (median)**: 50% of requests complete in this time or less
- **p95**: 95% of requests complete in this time or less (focus here!)
- **p99**: 99% of requests complete in this time or less
- **min/max**: Fastest and slowest requests

**Why P95 matters:** It represents the experience of most users while excluding outliers. A good P95 means most users get fast responses.

### Error Metrics
- **failure_rate**: Percentage of failed requests (HTTP 5xx or timeouts)
- **failed_requests**: Total number of failures

**Target:** < 0.1% error rate (< 0.001)

### Service-Specific Metrics

Available at `/metrics` endpoints:

- `http_request_duration_seconds`: Request time by endpoint
- `db_query_duration_seconds`: Database query time by query type
- `external_request_duration_seconds`: External service call time

## Common Optimization Patterns

### Pattern 1: Slow Database Queries

**Symptoms:**
- High p95 latency
- `db_query_duration_seconds` shows high values

**Solutions:**
1. Add indexes to frequently queried columns
2. Replace `ORDER BY RANDOM()` with efficient random selection
3. Use connection pooling (already configured)
4. Cache frequently accessed data

**Example:** The heroes service already uses efficient random selection instead of `ORDER BY RANDOM()`.

### Pattern 2: Connection Pool Exhaustion

**Symptoms:**
- High latency variance (p95/avg ratio > 3)
- Occasional very slow requests
- Error rate spikes under load

**Solutions:**
1. Increase connection pool size
2. Reduce connection timeout
3. Use connection pooling for HTTP clients (already configured in fights service)

### Pattern 3: Inefficient External Calls

**Symptoms:**
- `external_request_duration_seconds` shows high values
- Sequential external calls in code

**Solutions:**
1. Use `asyncio.gather()` for parallel calls
2. Add caching for frequently accessed data
3. Implement request coalescing

**Example:** The fights service uses `asyncio.gather()` to fetch hero, villain, and location in parallel.

### Pattern 4: Excessive Logging

**Symptoms:**
- High CPU usage
- Increased latency under load
- Log volume is very high

**Solutions:**
1. Set log level to WARNING or ERROR in production
2. Use structured logging with sampling
3. Avoid logging in hot paths

**Example:** Services are configured with `logging.WARNING` level.

## Instrumentation Usage

### Adding New Metrics

When adding new endpoints or features, instrument them:

```python
from prometheus_client import Histogram
import time

# Define metric
MY_OPERATION_DURATION = Histogram(
    'my_operation_duration_seconds',
    'Time spent in my operation',
    ['operation_type']
)

# Use metric
@app.get("/my-endpoint")
async def my_endpoint():
    start_time = time.time()
    try:
        # Your code here
        result = await do_something()
        return result
    finally:
        MY_OPERATION_DURATION.labels(operation_type='something').observe(
            time.time() - start_time
        )
```

### Accessing Metrics

```bash
# Heroes service metrics
curl http://localhost:8001/metrics

# Fights service metrics  
curl http://localhost:8004/metrics

# Parse specific metric
curl http://localhost:8001/metrics | grep http_request_duration
```

## Performance Testing Best Practices

### Always Compare Before/After

Never claim performance improvements without data:

❌ **BAD:** "Added caching to improve performance"
✅ **GOOD:** "Added caching - reduced P95 latency from 450ms to 180ms (-60%)"

### Test at Realistic Load

Choose RPS based on expected traffic:

- **10 RPS**: Light load, good for baseline
- **50 RPS**: Moderate load, typical production
- **100 RPS**: High load, stress testing

### Run Multiple Tests

Performance can vary due to noise. Best practice:

```bash
# Run test 3 times and compare
for i in 1 2 3; do
  python scripts/collect_performance_data.py \
    --rps 50 \
    --output k6/results/run_${i}.json
done

# Look at the median p95 across runs
```

### Watch for Regressions

Even if you improve one metric, check that others didn't regress:

- Did error rate increase?
- Did other endpoints get slower?
- Did resource usage (CPU/memory) increase significantly?

## Integration with Daily Perf Improver

When working with the daily-perf-improver workflow:

1. **Phase 3: Before optimization**
   - Run collection script to establish baseline
   - Review data to identify the highest-impact optimization target

2. **Phase 3: During optimization**
   - Make targeted changes based on data
   - Measure frequently to ensure you're moving in the right direction

3. **Phase 3: After optimization**
   - Run final comparison with baseline
   - Include performance report in PR description
   - Document methodology for reproducibility

## Example PR Description Format

```markdown
## Performance Improvement: Database Query Optimization

### Baseline Performance (50 RPS)
- P95 latency: 520ms
- Error rate: 0%
- Bottleneck: `get_random` query using inefficient random selection

### Changes Made
- Replaced `ORDER BY RANDOM()` with max ID + random offset approach
- Maintains uniform distribution while reducing query cost

### Results (50 RPS)
- P95 latency: 185ms (-64%)
- P99 latency: 220ms (-68%)
- Error rate: 0% (no change)

### Methodology
Baseline: `python scripts/collect_performance_data.py --rps 50 --output baseline.json`
After: `python scripts/collect_performance_data.py --rps 50 --baseline baseline.json --output optimized.json`

Full reports attached: baseline_report.md, optimized_report.md
```

## Anti-Patterns to Avoid

1. ❌ **Optimizing without measuring first**: Always establish baseline
2. ❌ **Micro-optimizations without profiling**: Focus on actual bottlenecks
3. ❌ **Ignoring error rates**: Fast but wrong is not an improvement
4. ❌ **Claiming improvement without data**: Use the collection script
5. ❌ **Testing only happy path**: Test under realistic load and error conditions

## Quick Reference Commands

```bash
# Collect baseline
python scripts/collect_performance_data.py --rps 50 --output baseline.json --report baseline.md

# After changes, measure improvement
docker compose up -d --build
python scripts/collect_performance_data.py --rps 50 --baseline baseline.json --output optimized.json --report optimized.md

# View service metrics
curl http://localhost:8001/metrics  # heroes
curl http://localhost:8004/metrics  # fights

# Check service health
docker compose ps
docker compose logs heroes

# Manual quick test
time curl http://localhost:8004/api/fights/randomfighters
```
