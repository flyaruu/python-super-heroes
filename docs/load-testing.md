# Load Testing

The Python Super Heroes project includes comprehensive load testing capabilities using [k6](https://k6.io/), a modern load testing tool.

## Overview

Load testing is performed against the Fights Service, which exercises the entire application stack by making calls to all microservices (Heroes, Villains, Locations).

## k6 Configuration

### Custom k6 Image

The project uses a custom k6 Docker image located in `k6-image/`:
- Based on the official k6 image
- Includes custom entrypoint for containerized execution
- Pre-configured for the application environment

### Environment Variables

- `K6_HOST`: Base URL for the Fights Service
  - Default: `http://fights:8000`

## Load Test Scripts

### load.js

Main load test script with configurable ramping scenarios.

**Features**:
- Ramping arrival rate executor
- Configurable target RPS via `RAMPING_RATE` environment variable
- Performance thresholds
- Three-stage load profile

**Stages**:
1. **Ramp Up** (5 seconds): Scale from 10 to target RPS
2. **Sustained Load** (20 seconds): Maintain target RPS
3. **Ramp Down** (5 seconds): Scale back to 0 RPS

**Performance Thresholds**:
``````javascript
{
  http_req_duration: ['p(95)<500'],    // 95% of requests under 500ms
  http_req_failed: ['rate<0.001'],      // Error rate under 0.1%
  dropped_iterations: ['count == 0']    // No dropped iterations
}
``````

**VU Configuration**:
- Pre-allocated VUs: 20
- Max VUs: 400

### randomFight.js

Reusable module for executing random fight requests.

## Running Load Tests

### Using Docker Compose

Execute a test with specific RPS:
``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

### Using the Usage Scenario

The project includes a `usage_scenario.yml` that defines multiple load test stages:

``````bash
# 1 RPS
k6 run -e RAMPING_RATE=1 --summary-export=/results/summary_1.json /k6/load.js

# 10 RPS
k6 run -e RAMPING_RATE=10 --summary-export=/results/summary_10.json /k6/load.js

# 50 RPS
k6 run -e RAMPING_RATE=50 --summary-export=/results/summary_50.json /k6/load.js

# 75 RPS
k6 run -e RAMPING_RATE=75 --summary-export=/results/summary_75.json /k6/load.js

# 100 RPS
k6 run -e RAMPING_RATE=100 --summary-export=/results/summary_100.json /k6/load.js
``````

## Results

Test results are exported to `/results/` directory:
- `summary_1.json` - 1 RPS test results
- `summary_10.json` - 10 RPS test results
- `summary_50.json` - 50 RPS test results
- `summary_75.json` - 75 RPS test results
- `summary_100.json` - 100 RPS test results

Results are in **machine-readable format** for automated processing.

## Interpreting Results

### Key Metrics

- **http_req_duration**: Response time percentiles
  - p(95): 95th percentile (most important)
  - p(99): 99th percentile
  - avg: Average response time

- **http_req_failed**: Percentage of failed requests
  - Should be near 0% for healthy systems

- **http_reqs**: Total number of requests executed

- **iterations**: Complete test iterations

- **vus**: Virtual users (concurrent connections)

### Threshold Violations

If thresholds are violated, k6 exits with non-zero status:
- Response times exceed 500ms (p95)
- Error rate exceeds 0.1%
- Iterations were dropped (system overload)

## Customizing Load Tests

### Modify Target RPS

Change the `RAMPING_RATE` environment variable:
``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=200 /k6/load.js
``````

### Adjust Thresholds

Edit `k6/load.js` and modify the `options.thresholds` object:
``````javascript
thresholds: {
  http_req_duration: ['p(95)<1000'],  // Relax to 1 second
  http_req_failed: ['rate<0.01'],      // Allow 1% errors
}
``````

### Change Test Duration

Modify the `stages` in `k6/load.js`:
``````javascript
stages: [
  { target: 100, duration: '30s' },  // Longer ramp up
  { target: 100, duration: '60s' },  // Longer sustained load
  { target: 0, duration: '10s' },    // Longer ramp down
]
``````

## Best Practices

1. **Start Small**: Begin with low RPS (1-10) to establish baseline
2. **Incremental Scaling**: Gradually increase load to find breaking points
3. **Monitor Services**: Watch container logs during tests
4. **Resource Monitoring**: Track CPU, memory, and database connections
5. **Repeat Tests**: Run multiple times to ensure consistency

## Troubleshooting

### Dropped Iterations

If you see dropped iterations:
- System is overloaded
- Reduce target RPS
- Increase `maxVUs` setting
- Scale application resources

### High Error Rates

If error rates are high:
- Check service logs: `docker compose logs fights`
- Verify all services are running: `docker compose ps`
- Check database connections
- Reduce load to find sustainable RPS

### Slow Response Times

If response times exceed thresholds:
- Check database query performance
- Review service logs for bottlenecks
- Monitor network latency between services
- Consider connection pooling settings

## Advanced Scenarios

### Custom Test Scripts

Create custom k6 scripts in the `k6/` directory:
``````javascript
import http from 'k6/http';
import { check } from 'k6';

export default function() {
  const res = http.get(`${__ENV.K6_HOST}/api/fights/execute_fight`);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has winner': (r) => r.json('winner_name') !== undefined,
  });
}
``````

### Distributed Testing

For very high load, run multiple k6 instances:
``````bash
docker compose up --scale k6=3
``````

## Integration with CI/CD

Load tests can be integrated into CI/CD pipelines:
``````bash
# Run test and fail if thresholds violated
docker compose exec k6 k6 run --summary-export=/results/ci-summary.json /k6/load.js

# Check exit code
if [ $? -eq 0 ]; then
  echo "Load test passed"
else
  echo "Load test failed - thresholds violated"
  exit 1
fi
``````
