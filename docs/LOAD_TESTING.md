# Load Testing Guide

This guide explains how to perform load testing on the Python Super Heroes microservices using k6.

## Overview

The project includes k6, a modern load testing tool, for performance testing and benchmarking the microservices architecture.

## Prerequisites

- Docker and Docker Compose installed
- All services running (`docker-compose up -d`)

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

Wait for all services to become healthy (check with `docker-compose ps`).

### 2. Access k6 Container

```bash
docker-compose exec k6 bash
```

### 3. Run Load Tests

```bash
# Test random fight endpoint
k6 run /k6/randomFight.js

# Run general load test
k6 run /k6/load.js
```

## Load Test Scripts

### randomFight.js

Tests the complete fight execution flow including service orchestration.

**Endpoint**: `GET /api/fights/execute_fight`

**Test Stages**:
1. **Ramp-up**: 0 → 10 VUs over 30 seconds
2. **Sustained Load**: 10 VUs for 1 minute
3. **Ramp-down**: 10 → 0 VUs over 30 seconds

**What It Tests**:
- End-to-end fight execution
- Service-to-service communication
- Parallel HTTP requests (heroes + villains)
- Sequential HTTP requests (locations)
- Database query performance across all databases

**Key Metrics**:
- Request duration (p95, p99)
- Requests per second
- Error rate
- HTTP failure rate

### load.js

General load testing script for baseline performance metrics.

**Endpoint**: Configurable via `K6_HOST` environment variable

**What It Tests**:
- Basic HTTP request handling
- Service responsiveness
- Connection stability

## Understanding Results

### Metrics Explained

```
checks.........................: 100.00% ✓ 150       ✗ 0
data_received..................: 245 kB  4.1 kB/s
data_sent......................: 13 kB   217 B/s
http_req_blocked...............: avg=1.2ms    min=2µs     med=5µs     max=150ms   p(95)=8µs
http_req_connecting............: avg=1.1ms    min=0s      med=0s      max=145ms   p(95)=0s
http_req_duration..............: avg=45.3ms   min=12.5ms  med=38.2ms  max=250ms   p(95)=95.6ms
http_req_receiving.............: avg=125.4µs  min=23µs    med=89µs    max=890µs   p(95)=245µs
http_req_sending...............: avg=45.2µs   min=8µs     med=35µs    max=234µs   p(95)=98µs
http_req_waiting...............: avg=45.1ms   min=12.3ms  med=38ms    max=249ms   p(95)=95.4ms
http_reqs......................: 150     2.5/s
iteration_duration.............: avg=3.9s     min=3.8s    med=3.9s    max=4.2s    p(95)=4.05s
iterations.....................: 150     2.5/s
vus............................: 1       min=1       max=10
vus_max........................: 10      min=10      max=10
```

**Key Metrics to Monitor**:

- **http_req_duration**: Total request time
  - `avg`: Average latency
  - `p(95)`: 95th percentile (95% of requests faster than this)
  - `p(99)`: 99th percentile (important for SLA)

- **http_reqs**: Total requests made and rate (requests/second)

- **checks**: Success rate of assertions (should be 100%)

- **iteration_duration**: Time for complete test iteration

### Performance Baselines

**Expected Performance** (on typical developer machine):

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Avg Response Time | < 50ms | < 100ms | > 200ms |
| P95 Response Time | < 100ms | < 200ms | > 500ms |
| Throughput | > 50 req/s | > 20 req/s | < 10 req/s |
| Error Rate | 0% | < 1% | > 5% |

## Advanced Testing

### Custom Test Duration

```bash
# Run for 5 minutes
k6 run --duration 5m /k6/randomFight.js

# Run with 50 VUs
k6 run --vus 50 /k6/randomFight.js

# Combine options
k6 run --vus 100 --duration 10m /k6/randomFight.js
```

### Stress Testing

Test system limits by gradually increasing load:

```bash
k6 run --stages="5m:100,10m:200,5m:0" /k6/randomFight.js
```

### Spike Testing

Test behavior under sudden traffic spikes:

```bash
k6 run --stages="1m:10,30s:100,1m:10,30s:0" /k6/randomFight.js
```

### Soak Testing

Test stability over extended periods:

```bash
k6 run --vus 20 --duration 2h /k6/randomFight.js
```

## Saving Results

### JSON Output

```bash
k6 run --out json=/results/test-results.json /k6/randomFight.js
```

### CSV Output

```bash
k6 run --out csv=/results/test-results.csv /k6/randomFight.js
```

### Summary Report

```bash
k6 run --summary-export=/results/summary.json /k6/randomFight.js
```

## Monitoring During Tests

### Watch Service Logs

```bash
# In another terminal
docker-compose logs -f fights heroes villains locations
```

### Check Database Connections

```bash
# PostgreSQL connections (Heroes)
docker-compose exec heroes-db psql -U superman -d heroes_database \
  -c "SELECT count(*) FROM pg_stat_activity;"

# PostgreSQL connections (Villains)
docker-compose exec villains-db psql -U superman -d villains_database \
  -c "SELECT count(*) FROM pg_stat_activity;"

# MariaDB connections (Locations)
docker-compose exec locations-db mysql -ulocations -plocations \
  -e "SHOW STATUS WHERE Variable_name='Threads_connected';"
```

## Troubleshooting

### High Error Rates

**Symptoms**: Many failed requests, timeouts

**Possible Causes**:
1. Services not fully started
2. Database connection pool exhausted
3. Container resource limits

**Solutions**:
```bash
# Check service health
docker-compose ps

# Check logs for errors
docker-compose logs fights

# Restart services
docker-compose restart

# Increase connection pool sizes (edit service code)
```

### Slow Response Times

**Symptoms**: High p95/p99 latencies

**Possible Causes**:
1. Database query performance
2. Network latency between containers
3. Insufficient CPU/memory

**Solutions**:
```bash
# Check container resource usage
docker stats

# Add database indexes (if missing)
# Profile slow queries

# Increase Docker resource limits
# (Docker Desktop > Settings > Resources)
```

### Connection Refused

**Symptoms**: `ECONNREFUSED` errors

**Possible Causes**:
1. Services not accessible from k6 container
2. Wrong hostname in k6 scripts

**Solutions**:
```bash
# Verify network connectivity
docker-compose exec k6 curl http://fights:8000/api/fights/execute_fight

# Check k6 environment variables
docker-compose exec k6 env | grep K6_HOST
```

## Best Practices

1. **Warm-up Period**: Always include ramp-up stage to avoid cold start effects
2. **Baseline First**: Run baseline tests before making changes
3. **Isolate Variables**: Test one change at a time
4. **Monitor Resources**: Watch CPU, memory, and database connections
5. **Document Results**: Save test configurations and results for comparison
6. **Test Incrementally**: Start with low load, gradually increase

## Integration with CI/CD

The project includes GitHub Actions workflows for automated performance testing. See `.github/workflows/` for examples.

### Example CI Integration

```yaml
- name: Run Load Tests
  run: |
    docker-compose up -d
    docker-compose exec -T k6 k6 run --out json=/results/ci-results.json /k6/randomFight.js
    
- name: Check Performance Thresholds
  run: |
    # Parse results and fail if thresholds exceeded
    python scripts/check_performance.py k6/results/ci-results.json
```

## Custom Test Scripts

### Creating New Tests

Create new test files in the `k6/` directory:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 10 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://fights:8000/api/fights/randomfighters');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has hero': (r) => JSON.parse(r.body).hero !== undefined,
    'has villain': (r) => JSON.parse(r.body).villain !== undefined,
  });
  
  sleep(1);
}
```

### Running Custom Tests

```bash
docker-compose exec k6 k6 run /k6/your-custom-test.js
```

## Resources

- [k6 Documentation](https://k6.io/docs/)
- [k6 Test Types](https://k6.io/docs/test-types/)
- [k6 Metrics Reference](https://k6.io/docs/using-k6/metrics/)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/performance-testing-best-practices/)
