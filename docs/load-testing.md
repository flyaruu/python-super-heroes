# Load Testing Guide

Comprehensive guide to load testing Python Super Heroes with k6.

## Overview

The project includes a k6-based load testing suite to measure system performance under various load conditions.

## k6 Setup

### Architecture

The k6 service is included in `compose.yml`:

``````yaml
k6:
  build: k6-image
  environment:
    K6_HOST: http://fights:8000
  command: ["bash", "-c", "while true; do sleep 3600; done"]
  volumes:
    - ./k6:/k6:ro
    - ./k6/results:/results
``````

### Test Scripts

Load test scripts are located in the `k6/` directory.

## Running Load Tests

### Start the System

``````bash
docker compose up -d
``````

Wait for all services to be healthy.

### Execute Tests

#### Single Test Run

``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

#### Multiple Test Rates

Run tests at different request rates to identify performance thresholds:

``````bash
# 1 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=1 \
  --summary-export=/results/summary_1.json /k6/load.js

# 10 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=10 \
  --summary-export=/results/summary_10.json /k6/load.js

# 50 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=50 \
  --summary-export=/results/summary_50.json /k6/load.js

# 100 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=100 \
  --summary-export=/results/summary_100.json /k6/load.js
``````

### Automated Test Suite

Use the `usage_scenario.yml` to run all tests sequentially:

``````bash
# Requires scenario runner tool
# Runs tests at 1, 10, 50, 75, and 100 RPS
``````

## Test Scenarios

### Load Test Configuration

The test script uses ramping stages:

``````javascript
export let options = {
  stages: [
    { duration: '30s', target: RAMPING_RATE },  // Ramp up
    { duration: '1m', target: RAMPING_RATE },   // Stay at rate
    { duration: '30s', target: 0 },             // Ramp down
  ],
};
``````

### Tested Endpoints

The load test exercises the Fights service:

- `GET /api/fights/execute_fight` - Complete fight execution
- `GET /api/fights/randomfighters` - Random hero/villain selection
- `GET /api/fights/randomlocation` - Random location selection

## Analyzing Results

### Console Output

k6 provides real-time metrics:

``````
scenarios: (100.00%) 1 scenario, 10 max VUs, 2m30s max duration
default: 10 looping VUs

     data_received..................: 2.3 MB  38 kB/s
     data_sent......................: 123 kB  2.1 kB/s
     http_req_blocked...............: avg=1.23ms   min=2µs
     http_req_connecting............: avg=423µs    min=0s
     http_req_duration..............: avg=145.67ms min=23.45ms
     http_req_failed................: 0.00%
     http_req_receiving.............: avg=234µs    min=45µs
     http_req_sending...............: avg=87µs     min=12µs
     http_req_waiting...............: avg=145.35ms min=23.21ms
     http_reqs......................: 600     10/s
     iteration_duration.............: avg=1.14s    min=1.02s
     iterations.....................: 600     10/s
``````

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `http_req_duration` | Response time | < 500ms (p95) |
| `http_req_failed` | Error rate | < 1% |
| `http_reqs` | Throughput | Matches RAMPING_RATE |
| `iterations` | Completed scenarios | High as possible |

### JSON Export

Results are saved to `/results/summary_*.json`:

``````json
{
  "metrics": {
    "http_req_duration": {
      "avg": 145.67,
      "min": 23.45,
      "max": 567.89,
      "p(90)": 234.56,
      "p(95)": 345.67
    },
    "http_req_failed": {
      "rate": 0.0,
      "passes": 600,
      "fails": 0
    }
  }
}
``````

Access results:

``````bash
docker compose exec k6 cat /results/summary_10.json
``````

## Performance Baselines

### Expected Performance

Based on typical microservices architecture:

| RPS | Expected p95 Latency | Expected Error Rate |
|-----|---------------------|---------------------|
| 1   | < 100ms            | 0%                  |
| 10  | < 200ms            | 0%                  |
| 50  | < 500ms            | < 1%                |
| 100 | < 1000ms           | < 5%                |

### Bottleneck Identification

Monitor these components:

1. **Database Connection Pools**
   - Check pool exhaustion in logs
   - Increase pool size if needed

2. **Service Response Times**
   - Use logs to identify slow endpoints
   - Check database query performance

3. **Network Latency**
   - Internal Docker network overhead
   - Service-to-service communication

## Advanced Testing

### Custom Scenarios

Create custom k6 scripts:

``````javascript
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  // Test specific endpoint
  let res = http.get('http://fights:8000/api/fights/execute_fight');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response has winner': (r) => JSON.parse(r.body).winner_name !== undefined,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
``````

### Threshold-Based Tests

Define pass/fail criteria:

``````javascript
export let options = {
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // 95% of requests < 500ms
    'http_req_failed': ['rate<0.01'],    // Error rate < 1%
  },
};
``````

### Smoke Testing

Quick validation test:

``````bash
docker compose exec k6 k6 run \
  --vus 1 \
  --duration 10s \
  /k6/load.js
``````

### Stress Testing

Find breaking point:

``````bash
docker compose exec k6 k6 run \
  --vus 100 \
  --duration 5m \
  /k6/load.js
``````

### Soak Testing

Long-duration stability test:

``````bash
docker compose exec k6 k6 run \
  --vus 10 \
  --duration 1h \
  /k6/load.js
``````

## Monitoring During Tests

### View Service Logs

``````bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f fights
``````

### Database Monitoring

``````bash
# PostgreSQL connections
docker compose exec heroes-db psql -U superman -d heroes_database \
  -c "SELECT count(*) FROM pg_stat_activity;"

# MariaDB connections
docker compose exec locations-db mysql -u locations -plocations \
  -e "SHOW PROCESSLIST;"
``````

### Resource Usage

``````bash
docker stats
``````

## Troubleshooting

### High Error Rates

- Check service logs for errors
- Verify database connections
- Increase connection pool sizes
- Add retry logic

### Slow Response Times

- Enable query logging
- Check database indexes
- Optimize connection pooling
- Review service-to-service communication

### Connection Timeouts

- Increase retry timeouts
- Check network configuration
- Verify service dependencies

## Best Practices

1. **Baseline Testing**: Establish performance baselines before changes
2. **Incremental Load**: Test at increasing rates to find limits
3. **Realistic Scenarios**: Mirror production usage patterns
4. **Consistent Environment**: Use same configuration for comparable results
5. **Monitor Everything**: Track logs, metrics, and resource usage

## CI/CD Integration

Add performance tests to CI pipeline:

``````yaml
# .github/workflows/performance.yml
- name: Run Performance Tests
  run: |
    docker compose up -d
    docker compose exec k6 k6 run \
      --summary-export=/results/summary.json \
      /k6/load.js
    # Parse results and fail if thresholds exceeded
``````

## Further Reading

- [k6 Documentation](https://k6.io/docs/)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/test-types/)
- [k6 Metrics Reference](https://k6.io/docs/using-k6/metrics/)
