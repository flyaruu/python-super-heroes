# Performance Data Feedback Loop

This guide explains how to collect performance data and feed it back to AI agents for data-driven optimization decisions.

## Overview

The performance feedback loop enables you to:
1. **Collect** performance metrics from load tests and service instrumentation
2. **Analyze** the data to identify bottlenecks and optimization opportunities
3. **Feed** structured data to AI agents for informed optimization decisions
4. **Verify** improvements by comparing before/after results

## Architecture

### Components

1. **Service Instrumentation**
   - Prometheus metrics exposed at `/metrics` endpoint
   - Request duration tracking (per endpoint)
   - Database query timing
   - External service call timing
   - Error rate monitoring

2. **Load Testing**
   - k6 tests at various RPS levels (1, 10, 50, 75, 100)
   - JSON summary exports with detailed metrics
   - Threshold validation

3. **Data Collection Script**
   - `scripts/collect_performance_data.py`
   - Runs k6 tests and collects service metrics
   - Generates structured JSON data
   - Produces AI-readable reports

## Quick Start

### 1. Start the Services

```bash
docker compose up -d
```

Wait for all services to be healthy (check with `docker compose ps`).

### 2. Collect Baseline Performance Data

```bash
# Install required Python packages
pip install requests

# Collect baseline at 10 RPS
python scripts/collect_performance_data.py \
  --rps 10 \
  --output k6/results/baseline_10rps.json \
  --report k6/results/baseline_10rps_report.md
```

### 3. Make Optimization Changes

Make your code changes to improve performance.

### 4. Collect New Performance Data

```bash
# Rebuild services
docker compose up -d --build

# Collect new data and compare with baseline
python scripts/collect_performance_data.py \
  --rps 10 \
  --baseline k6/results/baseline_10rps.json \
  --output k6/results/optimized_10rps.json \
  --report k6/results/optimized_10rps_report.md
```

### 5. Review the Results

The report will show:
- Current performance metrics (latency percentiles, throughput, errors)
- Comparison with baseline (improvements and regressions)
- AI-readable optimization guidance
- Data-driven recommendations

## Using Data with AI Agents

### Providing Data to AI

When asking AI for optimization suggestions, include the performance report:

```markdown
Please help optimize this service. Here's the current performance data:

[paste contents of the *_report.md file]

Based on this data, what specific optimizations should I make?
```

### AI Workflow Integration

For the daily-perf-improver workflow, the script can be integrated into Phase 3:

1. **Before optimization:** Run the collection script to establish baseline
2. **After changes:** Run again to measure impact
3. **Include in PR:** Attach performance reports as evidence of improvement

## Available Metrics

### Request Metrics
- `http_requests_total`: Counter of all HTTP requests by method, endpoint, and status
- `http_request_duration_seconds`: Histogram of request duration by method and endpoint

### Database Metrics
- `db_query_duration_seconds`: Histogram of database query duration by query type

### External Service Metrics
- `external_request_duration_seconds`: Histogram of external HTTP call duration by service

### k6 Metrics
- HTTP request duration (avg, min, max, p50, p95, p99)
- Request rate (requests/second)
- Error rate and failed request count
- Threshold pass/fail status

## Advanced Usage

### Testing at Multiple Load Levels

```bash
# Test at various RPS levels
for rps in 10 50 100; do
  python scripts/collect_performance_data.py \
    --rps $rps \
    --output k6/results/perf_${rps}rps.json \
    --report k6/results/perf_${rps}rps_report.md
done
```

### Accessing Raw Prometheus Metrics

```bash
# Heroes service
curl http://localhost:8001/metrics

# Fights service
curl http://localhost:8004/metrics
```

### Custom Analysis

The JSON output files contain structured data that can be processed programmatically:

```python
import json

with open('k6/results/perf_10rps.json') as f:
    data = json.load(f)

# Access specific metrics
p95_latency = data['request_metrics']['duration']['p95']
error_rate = data['error_metrics']['failure_rate']
```

## Interpreting Results

### Good Performance Indicators
- ✓ P95 latency < 200ms
- ✓ Error rate < 0.1% (0.001)
- ✓ Small gap between avg and p95 (< 2.5x)

### Warning Signs
- ⚠️ P95 latency > 500ms: Slow requests need optimization
- ⚠️ High p95/avg ratio (> 3x): Inconsistent performance
- ⚠️ Error rate > 0.1%: Stability issues

### Common Optimization Targets

Based on data patterns:

1. **High P95 latency**: Database query optimization, connection pooling, caching
2. **High latency variance**: Reduce occasional slow requests, fix resource contention
3. **Elevated error rate**: Connection timeout tuning, retry logic, circuit breakers

## Integration with GitHub Workflows

### Phase 3 Enhancement

Modify the daily-perf-improver workflow to use this tool:

```yaml
- name: Collect baseline performance
  run: |
    python scripts/collect_performance_data.py \
      --rps 50 \
      --output k6/results/baseline.json \
      --report k6/results/baseline_report.md

# ... make changes ...

- name: Measure performance impact
  run: |
    python scripts/collect_performance_data.py \
      --rps 50 \
      --baseline k6/results/baseline.json \
      --output k6/results/optimized.json \
      --report k6/results/optimized_report.md
```

## Troubleshooting

### Services not responding
```bash
# Check service health
docker compose ps

# View service logs
docker compose logs heroes
docker compose logs fights
```

### k6 container not running
```bash
# Start k6 container
docker compose up -d k6

# Verify it's running
docker compose exec k6 k6 version
```

### Missing metrics endpoint
Ensure services have been rebuilt after adding instrumentation:
```bash
docker compose up -d --build
```

## Best Practices

1. **Always establish a baseline** before making changes
2. **Run tests multiple times** and take the median to reduce noise
3. **Test under realistic load** that matches your production traffic
4. **Compare like-for-like** (same RPS, same test duration)
5. **Include performance data** in all optimization PRs
6. **Document measurement methodology** for reproducibility
7. **Watch for regressions** in other metrics when optimizing one

## Example Workflow

Here's a complete example of the feedback loop:

```bash
# 1. Start services
docker compose up -d

# 2. Establish baseline
python scripts/collect_performance_data.py \
  --rps 50 \
  --output k6/results/baseline.json \
  --report k6/results/baseline.md

# 3. Review baseline report
cat k6/results/baseline.md

# 4. Make optimization (e.g., add caching)
# ... edit code ...

# 5. Rebuild
docker compose up -d --build

# 6. Measure impact
python scripts/collect_performance_data.py \
  --rps 50 \
  --baseline k6/results/baseline.json \
  --output k6/results/after_cache.json \
  --report k6/results/after_cache.md

# 7. Review improvements
cat k6/results/after_cache.md

# 8. If good, commit; if not, iterate
git add services/
git commit -m "Add caching - improved p95 by 40%"
```

## Future Enhancements

Potential improvements to this system:

1. **Continuous monitoring**: Prometheus + Grafana for real-time metrics
2. **Historical tracking**: Store metrics in time-series database
3. **Automated regression detection**: CI pipeline that fails on performance regressions
4. **Profile-guided optimization**: Integrate CPU/memory profiling
5. **Cost metrics**: Track energy consumption and resource usage
