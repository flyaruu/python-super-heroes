# Testing Guide

Comprehensive guide for load testing, performance benchmarking, and test automation for Python Super Heroes.

## Overview

The project uses **K6** for load testing, providing scenarios from light (1 RPS) to stress testing (100 RPS). Tests simulate realistic fight execution patterns and measure system performance under load.

## K6 Architecture

### Test Structure

``````
k6/
├── load.js           # Main test configuration
├── randomFight.js    # Fight simulation logic
└── results/          # Test results output
    ├── summary_1.json
    ├── summary_10.json
    ├── summary_50.json
    ├── summary_75.json
    └── summary_100.json
``````

### Test Flow

1. Request random fighters (`/api/fights/randomfighters`)
2. Request random location (`/api/fights/randomlocation`)
3. Post fight request (`POST /api/fights`)
4. Validate response codes and data

## Running Tests

### Prerequisites

``````bash
# Ensure all services are running
docker-compose up -d

# Verify services are healthy
docker-compose ps
``````

### Quick Start

**Run single test:**
``````bash
docker-compose run k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

**Run with results export:**
``````bash
docker-compose run k6 k6 run \
  -e RAMPING_RATE=10 \
  --summary-export=/results/summary_10.json \
  /k6/load.js
``````

**View results:**
``````bash
cat k6/results/summary_10.json | jq
``````

### Test Scenarios

#### Baseline Test (1 RPS)
``````bash
docker-compose run k6 k6 run \
  -e RAMPING_RATE=1 \
  --summary-export=/results/summary_1.json \
  /k6/load.js
``````

**Purpose**: Establish baseline performance metrics.

**Expected Results**:
- p95 latency: <50ms
- Error rate: <0.1%
- No dropped iterations

#### Light Load (10 RPS)
``````bash
docker-compose run k6 k6 run \
  -e RAMPING_RATE=10 \
  --summary-export=/results/summary_10.json \
  /k6/load.js
``````

**Purpose**: Validate normal operation under typical load.

**Expected Results**:
- p95 latency: <100ms
- Error rate: <0.1%
- Stable memory usage

#### Medium Load (50 RPS)
``````bash
docker-compose run k6 k6 run \
  -e RAMPING_RATE=50 \
  --summary-export=/results/summary_50.json \
  /k6/load.js
``````

**Purpose**: Identify scaling limits and bottlenecks.

**Expected Results**:
- p95 latency: <200ms
- Error rate: <0.5%
- Connection pool pressure visible

#### Heavy Load (75 RPS)
``````bash
docker-compose run k6 k6 run \
  -e RAMPING_RATE=75 \
  --summary-export=/results/summary_75.json \
  /k6/load.js
``````

**Purpose**: Test system under sustained heavy load.

**Expected Results**:
- p95 latency: <350ms
- Error rate: <1%
- Database tuning may be required

#### Stress Test (100 RPS)
``````bash
docker-compose run k6 k6 run \
  -e RAMPING_RATE=100 \
  --summary-export=/results/summary_100.json \
  /k6/load.js
``````

**Purpose**: Find breaking point and failure modes.

**Expected Results**:
- p95 latency: <500ms (threshold)
- Error rate: <1%
- Possible dropped iterations

### Using usage_scenario.yml

The project includes automated scenario execution:

``````yaml
# usage_scenario.yml defines 5 scenarios:
flow:
  - name: K6 run 1 RPS
  - name: K6 run 10 RPS
  - name: K6 run 50 RPS
  - name: K6 run 75 RPS
  - name: K6 run 100 RPS
``````

This file is used for automated benchmarking workflows.

## Test Configuration

### Load Test Options (load.js)

``````javascript
export const options = {
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95th percentile < 500ms
    http_req_failed: ['rate<0.001'],    // Error rate < 0.1%
    dropped_iterations: ['count == 0'], // No dropped iterations
  },
  scenarios: {
    ramp_high_load: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 20,
      maxVUs: 400,
      stages: [
        { target: RAMPING_RATE, duration: '5s' },  // Ramp up
        { target: RAMPING_RATE, duration: '20s' }, // Sustain
        { target: 0, duration: '5s' },             // Ramp down
      ]
    },
  },
};
``````

**Key Parameters:**
- `executor`: `ramping-arrival-rate` (maintains constant RPS)
- `startRate`: Initial requests per second
- `preAllocatedVUs`: Pre-spawned virtual users (20)
- `maxVUs`: Maximum virtual users (400)
- `stages`: Load profile (ramp-up → sustain → ramp-down)

### Thresholds

Tests fail if thresholds are exceeded:

| Threshold | Limit | Description |
|-----------|-------|-------------|
| `http_req_duration` | p95 < 500ms | 95% of requests complete in <500ms |
| `http_req_failed` | rate < 0.1% | Less than 0.1% errors |
| `dropped_iterations` | count = 0 | No requests dropped |

**Modify thresholds:**
``````javascript
// Stricter thresholds
thresholds: {
  http_req_duration: ['p(95)<200'],
  http_req_failed: ['rate<0.0001'],
}
``````

### Fight Validation (randomFight.js)

``````javascript
// Validates fighters aren't fallback values
check(location, {
  'hero is not fallback': (r) => !hero.name.toLowerCase().includes("fallback"),
  'villain is not fallback': (r) => !villain.name.toLowerCase().includes("fallback")
})

// Validates location response
check(location, {
  'location is not fallback': (r) => !location.name.toLowerCase().includes("fallback")
})

// Validates fight execution
check(fight_response, {
  'fight result is 200': (r) => r.status === 200
})
``````

## Analyzing Results

### Terminal Output

K6 displays real-time metrics during test execution:

``````
running (30.0s), 000/400 VUs, 500 complete and 0 interrupted iterations
ramp_high_load ✓ [======================================] 000/400 VUs  30s

     ✓ random fighters status is 200
     ✓ hero is not fallback
     ✓ villain is not fallback
     ✓ location status is 200
     ✓ location is not fallback
     ✓ fight result is 200

     checks.........................: 100.00% ✓ 3000      ✗ 0
     data_received..................: 15 MB   500 kB/s
     data_sent......................: 750 kB  25 kB/s
     dropped_iterations.............: 0       0/s
     http_req_duration..............: avg=45ms min=12ms med=38ms max=385ms p(95)=120ms
     http_reqs......................: 1500    50/s
     iteration_duration.............: avg=135ms min=45ms med=125ms max=620ms p(95)=245ms
``````

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `checks` | Validation pass rate | 100% |
| `http_req_duration` | Request latency | p95 < 500ms |
| `http_req_failed` | Error rate | < 0.1% |
| `dropped_iterations` | Requests not executed | 0 |
| `http_reqs` | Total requests | Varies |
| `iteration_duration` | Full test cycle time | Varies |

### JSON Results

Results are exported to `/results/summary_*.json`:

``````bash
# View results with jq
cat k6/results/summary_10.json | jq '.metrics'

# Extract specific metric
cat k6/results/summary_10.json | jq '.metrics.http_req_duration.values."p(95)"'
``````

**Example output:**
``````json
{
  "metrics": {
    "http_req_duration": {
      "values": {
        "avg": 45.2,
        "min": 12.5,
        "max": 385.1,
        "p(50)": 38.4,
        "p(95)": 120.3,
        "p(99)": 285.7
      }
    },
    "http_req_failed": {
      "values": {
        "rate": 0.0002
      }
    }
  }
}
``````

### Comparing Results

``````bash
# Compare p95 latencies across scenarios
for file in k6/results/summary_*.json; do
  echo "$file:"
  jq '.metrics.http_req_duration.values."p(95)"' $file
done
``````

## Performance Tuning

### Interpreting Results

**Good Performance:**
- p95 latency < 100ms
- p99 latency < 200ms
- Error rate < 0.01%
- Zero dropped iterations

**Degraded Performance:**
- p95 latency 100-300ms
- Error rate 0.01-0.5%
- Occasional dropped iterations

**System Overload:**
- p95 latency > 500ms
- Error rate > 1%
- Consistent dropped iterations

### Optimization Strategies

#### 1. Database Connection Pool

**Problem**: High latency, connection errors

**Solution**: Increase pool size
``````python
# services/heroes/main.py
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=20,  # Increase from 10
    max_size=100  # Increase from 50
)
``````

#### 2. Service Scaling

**Problem**: CPU saturation, high response times

**Solution**: Scale service replicas
``````bash
docker-compose up --scale fights=3 --scale heroes=2
``````

#### 3. Database Tuning

**PostgreSQL optimization:**
``````sql
-- Increase shared buffers
ALTER SYSTEM SET shared_buffers = '256MB';

-- Increase connection limit
ALTER SYSTEM SET max_connections = '200';

-- Reload configuration
SELECT pg_reload_conf();
``````

**MariaDB optimization:**
``````sql
-- my.cnf
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 256M
``````

#### 4. Caching Layer

Add Redis for frequently accessed data:

``````yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
``````

``````python
# Cache random heroes
cached = await redis.get('random_hero')
if cached:
    return JSONResponse(json.loads(cached))
``````

## Advanced Testing

### Custom Test Scenarios

Create custom K6 scripts:

``````javascript
// k6/custom-test.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
};

export default function() {
  const response = http.get('http://fights:8000/api/fights/execute_fight');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
``````

Run custom test:
``````bash
docker-compose run k6 k6 run /k6/custom-test.js
``````

### Distributed Testing

For higher load, use K6 Cloud or distributed execution:

``````bash
# Run K6 Cloud test
k6 cloud k6/load.js

# Or run multiple local instances
docker-compose up --scale k6=5
``````

### Monitoring During Tests

**Monitor service logs:**
``````bash
# Terminal 1: Run test
docker-compose run k6 k6 run -e RAMPING_RATE=50 /k6/load.js

# Terminal 2: Monitor logs
docker-compose logs -f fights heroes villains locations
``````

**Monitor resource usage:**
``````bash
# Watch Docker stats
docker stats
``````

**Monitor database:**
``````bash
# PostgreSQL active connections
docker-compose exec heroes-db psql -U superman -d heroes_database \
  -c "SELECT count(*) FROM pg_stat_activity;"

# MariaDB processlist
docker-compose exec locations-db mysql -u locations -plocations \
  -e "SHOW PROCESSLIST;"
``````

## Continuous Integration

### GitHub Actions Example

``````yaml
# .github/workflows/load-test.yml
name: Load Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: sleep 30
      
      - name: Run K6 test
        run: |
          docker-compose run k6 k6 run \
            -e RAMPING_RATE=10 \
            --summary-export=/results/summary.json \
            /k6/load.js
      
      - name: Check thresholds
        run: |
          docker-compose run k6 k6 run \
            -e RAMPING_RATE=10 \
            --no-usage-report \
            /k6/load.js || exit 1
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: k6/results/
``````

## Troubleshooting

### Test Failures

**Dropped iterations:**
- Increase `maxVUs` in test configuration
- Reduce `RAMPING_RATE`
- Scale up services

**High error rates:**
- Check service logs for errors
- Verify database connections
- Check network connectivity

**Timeout errors:**
- Increase test timeout in K6
- Optimize slow endpoints
- Check database query performance

### Common Issues

**K6 container exits immediately:**
``````bash
# Check command syntax
docker-compose run k6 k6 run /k6/load.js
``````

**Cannot connect to services:**
``````bash
# Verify network
docker-compose exec k6 ping fights

# Check K6_HOST environment variable
docker-compose run k6 env | grep K6_HOST
``````

**Results not saved:**
``````bash
# Ensure results directory exists
mkdir -p k6/results

# Check volume mount in docker-compose.yml
volumes:
  - ./k6/results:/results
``````

## Best Practices

1. **Baseline First**: Always run baseline (1 RPS) before heavy tests
2. **Incremental Load**: Gradually increase load to identify limits
3. **Monitor Resources**: Watch CPU, memory, and connections during tests
4. **Isolate Tests**: Run one test at a time for accurate results
5. **Document Results**: Keep historical data for comparison
6. **Realistic Scenarios**: Match test patterns to production usage
7. **Automate**: Integrate tests into CI/CD pipeline

## Resources

- [K6 Documentation](https://k6.io/docs/)
- [K6 Test Types](https://k6.io/docs/test-types/)
- [Ramping Arrival Rate](https://k6.io/docs/using-k6/scenarios/executors/ramping-arrival-rate/)
- [K6 Thresholds](https://k6.io/docs/using-k6/thresholds/)
