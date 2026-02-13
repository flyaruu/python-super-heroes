# Load Testing Guide

Comprehensive guide to performance testing the Python Super Heroes system using k6.

## Overview

The project includes a complete k6 load testing suite that simulates realistic user traffic patterns to validate performance requirements and identify bottlenecks.

## Load Testing Stack

- **k6**: Modern load testing tool written in Go
- **JavaScript**: Test scripts using k6's JavaScript DSL
- **Docker**: Custom k6 image with scripts included
- **Results Storage**: Mounted volume for test results persistence

## Performance Requirements

The system is designed to meet the following SLAs:

| Metric | Requirement |
|--------|-------------|
| **Throughput** | 500 requests/second (peak) |
| **Latency (p95)** | < 500ms |
| **Error Rate** | < 0.1% |
| **Dropped Iterations** | 0 (no request should be dropped) |

## Test Configuration

### Load Profile

The test uses a **ramping arrival rate** executor to simulate realistic traffic:

``````javascript
scenarios: {
  ramp_high_load: {
    executor: 'ramping-arrival-rate',
    startRate: 10,
    timeUnit: '1s',
    preAllocatedVUs: 20,
    maxVUs: 400,
    stages: [
      { target: 500, duration: '5s' },   // Ramp up to 500 req/s
      { target: 500, duration: '20s' },  // Maintain 500 req/s
      { target: 0, duration: '5s' }      // Ramp down
    ]
  }
}
``````

**Total Duration**: 30 seconds

**Stages**:
1. **Ramp-up (0-5s)**: Gradually increase from 10 to 500 req/s
2. **Sustained Load (5-25s)**: Maintain 500 req/s for 20 seconds
3. **Ramp-down (25-30s)**: Gracefully reduce to 0 req/s

### Virtual Users

- **Pre-allocated**: 20 VUs (started immediately)
- **Maximum**: 400 VUs (spawned as needed)
- **Arrival Rate**: 500 requests/second at peak

### Thresholds

``````javascript
thresholds: {
  http_req_duration: ['p(95)<500'],    // 95th percentile < 500ms
  http_req_failed: ['rate<0.001'],     // < 0.1% errors
  dropped_iterations: ['count == 0']   // No dropped requests
}
``````

## Test Scenarios

### Random Fight Scenario

The main test scenario (`randomFight.js`) simulates a complete user flow:

1. **Get Random Fighters**: `GET /api/fights/randomfighters`
   - Fetches random hero and villain
   - Validates response status (200)
   - Checks for fallback characters (failure condition)

2. **Get Random Location**: `GET /api/fights/randomlocation`
   - Fetches random fight location
   - Validates response status (200)
   - Checks for fallback location (failure condition)

3. **Execute Fight**: `POST /api/fights`
   - Sends fight request with hero, villain, location
   - Validates response status (200)
   - Returns fight result

### Request Flow

``````
VU → GET randomfighters → GET randomlocation → POST fight → Result
     ↓                     ↓                    ↓
     Check 200            Check 200             Check 200
     No fallback          No fallback
``````

## Running Load Tests

### Using Docker Compose

**Start the system**:
``````bash
docker-compose up -d heroes villains locations fights
``````

**Wait for services to be ready** (check health):
``````bash
docker-compose ps
``````

**Run load test**:
``````bash
docker-compose up k6
``````

**View results**:
``````bash
ls -lh k6/results/
cat k6/results/summary.txt
``````

### Using k6 CLI (Alternative)

If you have k6 installed locally:

``````bash
# Install k6 (macOS)
brew install k6

# Install k6 (Linux)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Run test
k6 run k6/load.js
``````

### Custom Load Levels

Override the default ramping rate:

``````bash
docker-compose run -e RAMPING_RATE=1000 k6
``````

Or with k6 CLI:

``````bash
K6_RAMPING_RATE=1000 k6 run k6/load.js
``````

### Custom Target Host

Test against different environments:

``````bash
# Test against staging
K6_HOST=https://staging.example.com k6 run k6/load.js

# Test against production (use with caution!)
K6_HOST=https://api.example.com k6 run k6/load.js
``````

## Interpreting Results

### Sample Output

``````
     ✓ random fighters status is 200
     ✓ hero is not fallback
     ✓ villain is not fallback
     ✓ location status is 200
     ✓ location is not fallback
     ✓ fight result is 200

     checks.........................: 100.00% ✓ 90000      ✗ 0
     data_received..................: 45 MB   1.5 MB/s
     data_sent......................: 15 MB   500 kB/s
     dropped_iterations.............: 0       0/s
     http_req_blocked...............: avg=12µs    min=1µs    med=8µs     max=2ms   p(95)=25µs
     http_req_connecting............: avg=5µs     min=0s     med=0s      max=1ms   p(95)=15µs
   ✓ http_req_duration..............: avg=125ms   min=10ms   med=95ms    max=480ms p(95)=285ms
     http_req_failed................: 0.00%   ✓ 0          ✗ 45000
     http_req_receiving.............: avg=85µs    min=15µs   med=65µs    max=5ms   p(95)=185µs
     http_req_sending...............: avg=45µs    min=8µs    med=35µs    max=2ms   p(95)=95µs
     http_req_tls_handshaking.......: avg=0s      min=0s     med=0s      max=0s    p(95)=0s
     http_req_waiting...............: avg=124ms   min=9ms    med=94ms    max=479ms p(95)=284ms
     http_reqs......................: 45000   1500/s
     iteration_duration.............: avg=385ms   min=35ms   med=295ms   max=1.4s  p(95)=825ms
     iterations.....................: 15000   500/s
     vus............................: 2       min=2        max=387
     vus_max........................: 400     min=400      max=400
``````

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `checks` | Percentage of validation checks passed | 100% |
| `http_req_duration (p95)` | 95th percentile request latency | < 500ms |
| `http_req_failed` | Percentage of failed HTTP requests | < 0.1% |
| `dropped_iterations` | Number of iterations k6 couldn't start | 0 |
| `http_reqs` | Total HTTP requests made | ~45,000 (3 per iteration) |
| `iterations` | Complete test iterations | ~15,000 |

### Success Criteria

✅ **PASS** if:
- All checks are 100% (✓)
- `http_req_duration` p95 < 500ms
- `http_req_failed` rate < 0.001 (0.1%)
- `dropped_iterations` count == 0

❌ **FAIL** if:
- Any check fails
- Latency exceeds threshold
- Error rate exceeds threshold
- Iterations are dropped

## Troubleshooting

### High Latency

**Symptoms**: `http_req_duration` p95 > 500ms

**Possible Causes**:
- Database connection pool exhaustion
- Slow database queries
- Insufficient resources (CPU/memory)
- Network latency

**Solutions**:
``````bash
# Increase database connection pool size
# Edit service code:
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=20,    # Increase from 10
    max_size=100    # Increase from 50
)

# Scale services horizontally
docker-compose up -d --scale heroes=3 --scale villains=3
``````

### High Error Rate

**Symptoms**: `http_req_failed` > 0.1%

**Possible Causes**:
- Service crashes
- Database connection failures
- Timeout issues

**Solutions**:
``````bash
# Check service logs
docker-compose logs fights
docker-compose logs heroes

# Verify database health
docker-compose ps

# Restart failed services
docker-compose restart fights
``````

### Dropped Iterations

**Symptoms**: `dropped_iterations` > 0

**Possible Causes**:
- k6 can't spawn VUs fast enough
- System resource constraints

**Solutions**:
``````bash
# Reduce load
docker-compose run -e RAMPING_RATE=250 k6

# Increase pre-allocated VUs
# Edit k6/load.js:
preAllocatedVUs: 50,  // Increase from 20
``````

### Fallback Characters

**Symptoms**: Check failures for "hero/villain/location is not fallback"

**Possible Causes**:
- Database service is down
- No data in database
- Service returning default/fallback values

**Solutions**:
``````bash
# Verify database connectivity
docker-compose exec heroes-db psql -U superman -d heroes_database -c "SELECT COUNT(*) FROM hero;"

# Check service logs
docker-compose logs heroes
``````

## Advanced Usage

### Custom Scripts

Create custom test scenarios:

``````javascript
// custom-test.js
import { randomFight } from './randomFight.js';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function() {
  randomFight();
}
``````

Run:
``````bash
k6 run k6/custom-test.js
``````

### Distributed Load Testing

For large-scale tests, use k6 Cloud or distributed execution:

``````bash
# k6 Cloud
k6 cloud k6/load.js

# Distributed with multiple machines
k6 run --out json=results.json k6/load.js
``````

### Continuous Integration

Integrate with CI/CD pipelines:

``````yaml
# .github/workflows/load-test.yml
- name: Run Load Tests
  run: |
    docker-compose up -d
    sleep 30  # Wait for services
    docker-compose run k6
    if [ $? -ne 0 ]; then
      echo "Load tests failed!"
      exit 1
    fi
``````

### Metrics Export

Export results to monitoring systems:

``````bash
# InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 k6/load.js

# Prometheus
k6 run --out experimental-prometheus-rw k6/load.js

# DataDog
k6 run --out datadog k6/load.js
``````

## Performance Baselines

### Expected Performance (Development)

| Metric | Value |
|--------|-------|
| Throughput | 500 req/s |
| p50 Latency | ~95ms |
| p95 Latency | ~285ms |
| p99 Latency | ~400ms |
| Error Rate | 0% |

### Scaling Recommendations

| Load (req/s) | Recommended Setup |
|--------------|-------------------|
| 0-500 | Single instance per service |
| 500-1000 | 2 instances per service |
| 1000-2000 | 3-4 instances + load balancer |
| 2000+ | Auto-scaling group + CDN |

## Best Practices

1. **Gradual Ramp-up**: Always ramp up gradually to avoid overwhelming services
2. **Realistic Scenarios**: Model actual user behavior patterns
3. **Consistent Environment**: Test in environment similar to production
4. **Baseline First**: Establish baseline before making changes
5. **Monitor Resources**: Watch CPU, memory, network during tests
6. **Repeat Tests**: Run multiple times to account for variance
7. **Production Safety**: Never test production without approval

## Resources

- [k6 Documentation](https://k6.io/docs/)
- [k6 Best Practices](https://k6.io/docs/testing-guides/test-types/)
- [k6 Executors](https://k6.io/docs/using-k6/scenarios/executors/)
- [k6 Thresholds](https://k6.io/docs/using-k6/thresholds/)

## Next Steps

After establishing baseline performance:

1. Optimize slow database queries
2. Implement caching (Redis)
3. Add API rate limiting
4. Configure horizontal autoscaling
5. Set up continuous performance monitoring
