# Load Testing Guide

Comprehensive guide to performance testing Python Super Heroes with k6.

## Overview

The application includes k6-based load testing infrastructure to measure performance, identify bottlenecks, and validate optimization efforts.

## Architecture

``````
┌─────────────┐
│   k6        │
│  Container  │
└──────┬──────┘
       │
       │ HTTP Requests
       ▼
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│   Fights    │─────▶│   Heroes     │      │   Villains    │
│  Service    │      │   Service    │      │    Service    │
│             │      └──────────────┘      └───────────────┘
│             │      
│             │─────▶┌───────────────┐
│             │      │   Locations   │
└─────────────┘      └───────────────┘
``````

## Quick Start

### Run Basic Load Test

``````bash
# Access k6 container
docker compose exec k6 bash

# Run test at 10 RPS
k6 run -e RAMPING_RATE=10 /k6/load.js

# View results
cat /results/summary_10.json | jq
``````

### Run Full Test Suite

Execute all predefined scenarios:

``````bash
# Using usage_scenario.yml automation
# (Requires external orchestration tool)
``````

Or manually:

``````bash
k6 run -e RAMPING_RATE=1 --summary-export=/results/summary_1.json /k6/load.js
k6 run -e RAMPING_RATE=10 --summary-export=/results/summary_10.json /k6/load.js
k6 run -e RAMPING_RATE=50 --summary-export=/results/summary_50.json /k6/load.js
k6 run -e RAMPING_RATE=75 --summary-export=/results/summary_75.json /k6/load.js
k6 run -e RAMPING_RATE=100 --summary-export=/results/summary_100.json /k6/load.js
``````

## Test Scenarios

### Default Load Profile

Defined in `k6/load.js`:

``````javascript
scenarios: {
  ramp_high_load: {
    executor: 'ramping-arrival-rate',
    startRate: 10,
    timeUnit: '1s',
    preAllocatedVUs: 20,
    maxVUs: 400,
    stages: [
      { target: RAMPING_RATE, duration: '5s' },   // Ramp up
      { target: RAMPING_RATE, duration: '20s' },  // Sustain
      { target: 0, duration: '5s' },              // Ramp down
    ]
  }
}
``````

### Performance Thresholds

``````javascript
thresholds: {
  http_req_duration: ['p(95)<500'],    // 95% under 500ms
  http_req_failed: ['rate<0.001'],     // <0.1% errors
  dropped_iterations: ['count == 0'],  // No dropped requests
}
``````

## Test Scripts

### load.js

Primary load test script. Executes random fights.

**Features**:
- Configurable request rate via `RAMPING_RATE` env var
- Automated ramping stages
- Performance threshold validation
- JSON result export

**Usage**:
``````bash
k6 run -e RAMPING_RATE=50 /k6/load.js
``````

### randomFight.js

Helper module that executes a complete random fight.

**Implementation**:
``````javascript
export function randomFight() {
  const response = http.get(`${BASE_URL}/api/fights/execute_fight`);
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response has winner': (r) => JSON.parse(r.body).winner_name !== undefined,
  });
  return response;
}
``````

## Metrics

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `http_req_duration` | Request latency | p95 < 500ms |
| `http_req_failed` | Failed requests | < 0.1% |
| `http_reqs` | Requests per second | Varies by test |
| `dropped_iterations` | Requests dropped due to resource limits | 0 |
| `vus` | Virtual users active | Auto-scaled |
| `iterations` | Completed iterations | Matches arrival rate |

### Understanding Metrics

**http_req_duration percentiles**:
- `p(50)`: Median latency (typical user experience)
- `p(95)`: 95th percentile (worst case for most users)
- `p(99)`: 99th percentile (worst case outliers)

**http_req_failed**:
- Includes HTTP errors (4xx, 5xx)
- Network failures
- Timeout errors

**dropped_iterations**:
- Occurs when k6 can't generate enough VUs
- Indicates resource exhaustion
- Should always be 0 for valid tests

## Interpreting Results

### Successful Test

``````
✓ http_req_duration..............: avg=45ms  min=12ms med=38ms max=210ms p(95)=95ms  p(99)=150ms
✓ http_req_failed................: 0.00%
✓ dropped_iterations.............: 0
✓ http_reqs......................: 500/s
``````

**Analysis**: System handles load well. All thresholds passed.

### Failed Test (High Latency)

``````
✗ http_req_duration..............: avg=450ms min=200ms med=420ms max=2100ms p(95)=850ms p(99)=1500ms
✓ http_req_failed................: 0.00%
✗ dropped_iterations.............: 45
✗ http_reqs......................: 350/s (expected 500/s)
``````

**Analysis**: 
- p95 exceeds 500ms threshold
- Dropped iterations indicate VU exhaustion
- Lower actual RPS than target
- **Action**: Reduce load or optimize services

### Failed Test (Errors)

``````
✓ http_req_duration..............: avg=35ms  min=10ms med=30ms max=180ms p(95)=75ms p(99)=120ms
✗ http_req_failed................: 5.2%
✓ dropped_iterations.............: 0
``````

**Analysis**:
- Good latency but high error rate
- Likely service errors (database connections, timeouts)
- **Action**: Check service logs, database health

## Advanced Usage

### Custom Test Scenarios

Create custom test file:

``````javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    constant_load: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 50,
      maxVUs: 200,
    },
  },
};

export default function() {
  const res = http.get('http://fights:8000/api/fights/execute_fight');
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(0.1);
}
``````

**Run**:
``````bash
docker compose exec k6 k6 run /k6/custom_test.js
``````

### Smoke Testing

Quick validation test (low load):

``````bash
k6 run -e RAMPING_RATE=1 --duration 30s /k6/load.js
``````

### Stress Testing

Push system to limits:

``````bash
k6 run -e RAMPING_RATE=500 --summary-export=/results/stress.json /k6/load.js
``````

### Soak Testing

Long-duration stability test:

``````bash
k6 run -e RAMPING_RATE=50 --duration 30m /k6/load.js
``````

## Analyzing Results

### View Summary

``````bash
cat /results/summary_10.json | jq '.metrics | keys'
``````

### Extract Specific Metric

``````bash
cat /results/summary_10.json | jq '.metrics.http_req_duration'
``````

### Compare Results

``````bash
# Compare p95 latency across tests
jq '.metrics.http_req_duration.values."p(95)"' /results/summary_*.json
``````

### Export to CSV

``````bash
k6 run --out csv=/results/results.csv /k6/load.js
``````

## Performance Baselines

Expected performance on standard hardware (4 CPU, 8GB RAM):

| Rate | p95 Latency | Error Rate | Notes |
|------|-------------|------------|-------|
| 1 RPS | < 50ms | 0% | Baseline |
| 10 RPS | < 75ms | 0% | Light load |
| 50 RPS | < 150ms | 0% | Moderate load |
| 75 RPS | < 300ms | 0% | Heavy load |
| 100 RPS | < 500ms | < 0.1% | Stress test |
| 200+ RPS | Varies | Varies | Over capacity |

## Troubleshooting

### Dropped Iterations

**Symptom**: `dropped_iterations > 0`

**Causes**:
- Insufficient VUs allocated
- System resource exhaustion
- k6 container resource limits

**Solutions**:
``````javascript
// Increase maxVUs
maxVUs: 400  // Increase to 800

// Increase preAllocated VUs
preAllocatedVUs: 20  // Increase to 50
``````

### High Error Rates

**Symptom**: `http_req_failed > 1%`

**Causes**:
- Service crashes
- Database connection exhaustion
- Timeout errors

**Solutions**:
``````bash
# Check service logs
docker compose logs fights

# Check database health
docker compose ps

# Increase database connection pool
# Edit services/*/main.py
max_size=50  # Increase to 100
``````

### Inconsistent Results

**Symptom**: Wide variance between test runs

**Causes**:
- Background processes
- Insufficient warm-up
- Database cold starts

**Solutions**:
``````javascript
// Add warm-up stage
stages: [
  { target: 10, duration: '10s' },    // Warm up
  { target: TARGET, duration: '5s' }, // Ramp
  { target: TARGET, duration: '20s' },// Sustain
  { target: 0, duration: '5s' },      // Ramp down
]
``````

## Best Practices

### 1. Establish Baseline

Always run low-load baseline test first:
``````bash
k6 run -e RAMPING_RATE=1 /k6/load.js
``````

### 2. Incremental Load Increase

Test at increasing rates to find breaking point:
``````bash
for rate in 10 25 50 75 100; do
  k6 run -e RAMPING_RATE=$rate --summary-export=/results/summary_$rate.json /k6/load.js
done
``````

### 3. Monitor Resources

Watch container resource usage during tests:
``````bash
# In separate terminal
watch 'docker stats --no-stream'
``````

### 4. Clean State Between Tests

Restart services to ensure clean state:
``````bash
docker compose restart heroes villains locations fights
sleep 10  # Wait for startup
``````

### 5. Document Results

Save results with context:
``````bash
k6 run -e RAMPING_RATE=50 /k6/load.js | tee results_$(date +%Y%m%d_%H%M%S).txt
``````

## Integration with CI/CD

### GitHub Actions Example

``````yaml
- name: Run Load Tests
  run: |
    docker compose up -d
    sleep 30
    docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
    
- name: Check Performance Thresholds
  run: |
    # Extract p95 latency
    P95=$(cat k6/results/summary_10.json | jq '.metrics.http_req_duration.values."p(95)"')
    if (( $(echo "$P95 > 500" | bc -l) )); then
      echo "Performance regression: p95 = ${P95}ms"
      exit 1
    fi
``````

## Additional Resources

- **k6 Documentation**: https://k6.io/docs/
- **k6 Examples**: https://k6.io/docs/examples/
- **Performance Testing Guide**: https://k6.io/docs/testing-guides/
