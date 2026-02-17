# Example: Performance Data Feedback Loop

This example demonstrates how to use the performance feedback loop to make data-driven optimization decisions.

## Scenario

You want to optimize the fights service but aren't sure where to focus. Instead of guessing, you'll collect performance data to identify the real bottleneck.

## Step-by-Step Example

### Step 1: Start the Services

```bash
cd /home/runner/work/python-super-heroes/python-super-heroes
docker compose up -d
```

Wait for all services to become healthy:

```bash
docker compose ps
```

All services should show "healthy" status.

### Step 2: Collect Baseline Performance

```bash
python scripts/collect_performance_data.py \
  --rps 50 \
  --output k6/results/baseline.json \
  --report k6/results/baseline_report.md
```

This runs a k6 load test at 50 RPS and collects metrics from the services.

### Step 3: Review the Report

```bash
cat k6/results/baseline_report.md
```

Example output:

```markdown
# Performance Test Results

**Timestamp:** 2026-02-17T08:00:00.000Z

## Request Performance Metrics
- **Average latency:** 185.50ms
- **P50 (median):** 165.00ms
- **P95:** 450.00ms
- **P99:** 520.00ms
- **Min:** 85.00ms
- **Max:** 650.00ms

- **Total requests:** 1500
- **Requests per second:** 50.00

## Error Metrics
- **Failure rate:** 0.0000 (0.00%)
- **Failed requests:** 0

## AI Optimization Guidance
⚠️ **High latency variance**: Some requests are significantly slower than average

## Data-Driven Optimization Recommendations
1. **Reduce latency variance**
   - Investigate occasional slow requests
   - Check for database connection pool exhaustion
   - Look for cache misses or cold starts
```

### Step 4: Analyze the Data

From the report, we see:
- P95 latency is 450ms (acceptable, but could be better)
- High variance: P95/avg = 2.4x (some requests are much slower)
- No errors (good!)

**Conclusion:** Focus on reducing latency variance by optimizing the slow requests.

### Step 5: Identify the Bottleneck

Check service-specific metrics:

```bash
# View fights service metrics
curl http://localhost:8004/metrics | grep external_request_duration
```

You might see that external service calls take 100-300ms. Since the fights service calls three services (heroes, villains, locations), optimizing these calls could help.

**Hypothesis:** The fights service might be calling services sequentially instead of in parallel.

### Step 6: Make the Optimization

Check the code in `services/fights/main.py`:

```python
@fights_router.get("/fights/execute_fight")
async def execute_random_fight():
    """Execute random fight by fetching all data in parallel."""
    location, hero, villain = await asyncio.gather(
        get_location(),
        get_hero(),
        get_villain()
    )
    # ... rest of the code
```

Good news! The code already uses `asyncio.gather()` for parallel calls. This is already optimized.

Let's check another area - maybe the database queries can be optimized.

### Step 7: Alternative Optimization

Looking at the heroes service, we notice the random selection query. Let's say we want to test if adding a database index improves performance.

**Change:** Add an index to the heroes table (this is hypothetical - the actual schema might already have it).

```sql
CREATE INDEX idx_hero_id ON Hero(id);
```

### Step 8: Rebuild and Test

```bash
# Rebuild services
docker compose up -d --build

# Collect new performance data with comparison
python scripts/collect_performance_data.py \
  --rps 50 \
  --baseline k6/results/baseline.json \
  --output k6/results/optimized.json \
  --report k6/results/optimized_report.md
```

### Step 9: Review the Results

```bash
cat k6/results/optimized_report.md
```

Example output with improvement:

```markdown
# Performance Test Results

**Timestamp:** 2026-02-17T08:15:00.000Z

## Request Performance Metrics
- **Average latency:** 145.20ms
- **P50 (median):** 135.00ms
- **P95:** 320.00ms
- **P99:** 380.00ms

## Comparison with Baseline
**Net change:** improved

### Improvements ✓
- **http_req_duration_avg:** 185.50 → 145.20 (-21.73%)
- **http_req_duration_p95:** 450.00 → 320.00 (-28.89%)
- **http_req_duration_p99:** 520.00 → 380.00 (-26.92%)
```

**Result:** The optimization improved P95 latency by ~29% and reduced variance!

### Step 10: Document and Commit

Create a PR with the changes and include the performance data:

```markdown
## Performance Improvement: Database Query Optimization

### Problem
Baseline testing at 50 RPS showed high latency variance (P95: 450ms, avg: 185ms).

### Solution
Added database index on Hero.id to speed up random selection queries.

### Results
- P95 latency: 450ms → 320ms (-28.89%)
- Average latency: 185ms → 145ms (-21.73%)
- P99 latency: 520ms → 380ms (-26.92%)
- Error rate: 0% (no change)

### Methodology
Tests run at 50 RPS using `scripts/collect_performance_data.py`
Full reports: k6/results/baseline_report.md, k6/results/optimized_report.md
```

## Key Takeaways

1. **Always measure first**: We collected baseline data before making any changes
2. **Use data to decide**: The report told us to focus on latency variance
3. **Verify improvements**: We compared before/after with the same test
4. **Document methodology**: We explained how we measured and what we found

## Using with AI

You can paste the performance report to an AI agent:

```
Please help me optimize this service. Here's the current performance data:

[paste baseline_report.md contents]

Based on this data, what specific areas should I focus on?
```

The AI can now provide **data-driven** recommendations instead of guessing!

## Next Steps

- Try different optimizations and measure their impact
- Test at various load levels (10, 50, 100 RPS)
- Look at service-specific metrics for deeper insights
- Use the daily-perf-improver workflow for automated optimization
